import math
import re
from pathlib import Path
from src.ai.agent import call_openai_json, call_gemini_json

def clean_tokens(text: str) -> list[str]:
    # Normalize, remove punctuation, split
    cleaned = re.sub(r'[^\w\s\u3040-\u309f\u30a0-\u30ff\u4e00-\u9faf]', ' ', text.lower())
    return [w for w in cleaned.split() if len(w) > 1]

def score_documents(query: str, items: list[dict], course_name: str | None = None) -> list[tuple[dict, float]]:
    query_terms = clean_tokens(query)
    if not query_terms:
        return []
        
    filtered_items = items
    if course_name:
        filtered_items = [it for it in items if it.get("course") == course_name]
        
    if not filtered_items:
        return []
        
    # Build Document Frequency (DF) map
    df_map = {}
    doc_tokens_list = []
    
    for it in filtered_items:
        # Combine indexed content fields
        fields = [
            it.get("course", ""),
            it.get("material_name", ""),
            " ".join(it.get("keywords", [])),
            it.get("summary", ""),
            " ".join(it.get("key_points", [])),
            " ".join(it.get("important_terms", [])),
            it.get("ocr_text", "")
        ]
        doc_text = " ".join(fields)
        tokens = clean_tokens(doc_text)
        doc_tokens_list.append(tokens)
        
        seen = set(tokens)
        for t in seen:
            df_map[t] = df_map.get(t, 0) + 1
            
    num_docs = len(filtered_items)
    avg_len = sum(len(tokens) for tokens in doc_tokens_list) / num_docs if num_docs > 0 else 1
    
    scored_items = []
    for idx, it in enumerate(filtered_items):
        tokens = doc_tokens_list[idx]
        if not tokens:
            continue
            
        doc_len = len(tokens)
        score = 0.0
        
        # Calculate TF for query terms and sum their BM25 score
        for term in query_terms:
            tf = tokens.count(term)
            if tf == 0:
                continue
            df = df_map.get(term, 1)
            idf = math.log((num_docs - df + 0.5) / (df + 0.5) + 1.0)
            # BM25 formula parameters: k1 = 1.2, b = 0.75
            k1 = 1.2
            b = 0.75
            tf_scored = (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * (doc_len / avg_len)))
            score += idf * tf_scored
            
        if score > 0:
            scored_items.append((it, score))
            
    scored_items.sort(key=lambda x: x[1], reverse=True)
    return scored_items

def query_rag(query: str, course_name: str | None, search_index_data: dict, provider: str = "gemini") -> tuple[str, list[dict]]:
    items = search_index_data.get("index", [])
    ranked = score_documents(query, items, course_name)
    
    if not ranked:
        return "関連する講義資料が見つかりませんでした。質問やキーワードを変えてみてください。", []
        
    # Take top 3 documents
    top_matches = ranked[:3]
    context_blocks = []
    source_infos = []
    
    for item, score in top_matches:
        source_infos.append(item)
        
        # Crop OCR text around search query to keep context size manageable
        ocr = item.get("ocr_text", "")
        # Find first term index
        query_terms = clean_tokens(query)
        cropped_ocr = ocr[:3000] # default to first 3000 chars
        if query_terms:
            first_term = query_terms[0]
            term_idx = ocr.lower().find(first_term)
            if term_idx != -1:
                start = max(0, term_idx - 1000)
                end = min(len(ocr), term_idx + 2000)
                cropped_ocr = ocr[start:end]
                if start > 0:
                    cropped_ocr = "..." + cropped_ocr
                if end < len(ocr):
                    cropped_ocr = cropped_ocr + "..."
                    
        block = f"""---
授業名: {item.get('course')}
資料名: {item.get('material_name')}
教員: {item.get('teacher')}
概要: {item.get('summary')}
内容スニペット:
{cropped_ocr}"""
        context_blocks.append(block)
        
    context_str = "\n\n".join(context_blocks)
    
    prompt = f"""
あなたは講義資料に基づき回答する優秀な学習支援AIアシスタントです。
提供された以下の「講義資料の抜粋コンテキスト」のみに基づいて、学習者の「質問」に日本語で丁寧かつ具体的に回答してください。

回答におけるルール：
1. 必ず提供されたコンテキストの内容のみに基づいて回答してください。コンテキストに記載がない内容は「提供された資料内には記載が見つかりませんでした」と回答し、外部知識に基づく独自の推測や記述は絶対に行わないでください。
2. 関連する具体的な資料名（例：〜.pdf）や該当箇所を回答の中で明示してください。
3. 学習者が理解しやすいよう、必要に応じて箇条書きなどを用いて構造化して回答してください。
4. 返答フォーマットは、回答文を含むJSONとします。

【出力JSONフォーマット】
{{
  "answer": "回答テキスト（Markdown形式での太字や箇条書きを適宜使用）"
}}

[講義資料の抜粋コンテキスト]
{context_str}

[質問]
{query}
"""
    try:
        if provider.lower() == "openai":
            res = call_openai_json(prompt)
        else:
            res = call_gemini_json(prompt)
        return res.get("answer", "回答を生成できませんでした。"), source_infos
    except Exception as e:
        return f"RAGエラーが発生しました: {e}", source_infos
