import streamlit as st
import json
import re
import src.core.models as models
from src.gui.common import root_path

def render_tab_search():
    st.subheader("🔍 全文検索")
    st.write("授業資料のOCR本文、AI要約、授業名、キーワードなどから高速に全文検索します。")
    
    query = st.text_input("検索キーワード", placeholder="検索したい言葉を入力 (スペース区切りでAND検索)", key="streamlit_gui_search_query")
    if not query:
        return
        
    index_path = models.search_index_path(root_path())
    if not index_path.exists():
        st.warning("検索インデックスが見つかりません。先に「資料整理」または「AI分析」を実行してインデックスを生成してください。")
        return
        
    try:
        data = json.loads(index_path.read_text(encoding="utf-8"))
        index_items = data.get("index", [])
        
        query_terms = [t.lower() for t in query.split()]
        results = []
        
        for item in index_items:
            fields = [
                ("授業名", item.get("course", "")),
                ("教員名", item.get("teacher", "")),
                ("資料名", item.get("material_name", "")),
                ("キーワード", ", ".join(item.get("keywords", []))),
                ("AI要約", item.get("summary", "")),
                ("要点", " ".join(item.get("key_points", []))),
                ("重要語句", " ".join(item.get("important_terms", []))),
                ("復習リスト", " ".join(item.get("review_checklist", []))),
                ("OCR本文", item.get("ocr_text", ""))
            ]
            
            matched_field = None
            matched_val = None
            for name_f, val_f in fields:
                if not val_f:
                    continue
                val_f_lower = val_f.lower()
                if all(term in val_f_lower for term in query_terms):
                    matched_field = name_f
                    matched_val = val_f
                    break
                    
            if matched_field:
                first_term = query_terms[0]
                idx = matched_val.lower().find(first_term)
                start = max(0, idx - 50)
                end = min(len(matched_val), idx + len(first_term) + 50)
                snippet = matched_val[start:end]
                if start > 0:
                    snippet = "..." + snippet
                if end < len(matched_val):
                    snippet = snippet + "..."
                    
                for term in query_terms:
                    pattern = re.compile(re.escape(term), re.IGNORECASE)
                    snippet = pattern.sub(lambda m: f"<mark style='background-color: #fef08a;'>{m.group(0)}</mark>", snippet)
                    
                results.append({
                    "item": item,
                    "reason": matched_field,
                    "snippet": snippet
                })
                
        if results:
            st.success(f"{len(results)} 件の資料が見つかりました。")
            for res in results:
                item = res["item"]
                st.markdown(f"📄 **{item['material_name']}** (授業: {item['course']} | 担当: {item['teacher'] or '未登録'})")
                st.markdown(f"**一致項目**: {res['reason']}")
                st.write(f"**一致箇所**: {res['snippet']}", unsafe_allow_html=True)
                st.caption(f"ファイルパス: {item['path']}")
                st.write("---")
        else:
            st.info("キーワードに一致する資料が見つかりませんでした。")
    except Exception as e:
        st.error(f"検索エラーが発生しました: {e}")
