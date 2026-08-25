import os
import sys
import json
import re
from pathlib import Path
from collections import Counter

from src.core.models import (
    Course, MaterialRecord, SummaryRecord, QuestionRecord,
    normalize_record_path
)
from src.data.extractor import tokenize, split_sentences

def trim_text(text: str, limit: int = 6000) -> str:
    if len(text) <= limit:
        return text
    return text[:limit] + "... [テキストが長いため一部省略されました]"

def string_list(val) -> list[str]:
    if not val:
        return []
    if isinstance(val, list):
        return [str(v) for v in val if v]
    if isinstance(val, str):
        return [v.strip() for v in val.split(",") if v.strip()]
    return []

def relative_to_root(root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(root).as_posix())
    except Exception:
        return str(path.name)

def find_custom_plugin(name: str):
    if os.environ.get("PBL_USE_CUSTOM_PLUGINS") != "1":
        return None

    import importlib.util
    plugins_dir = Path.cwd() / "plugins"
    candidates = [
        plugins_dir / f"{name}.py",
        Path.cwd() / f"{name}.py"
    ]
    for candidate in candidates:
        if candidate.exists() and candidate.is_file():
            try:
                module_name = f"custom_plugin_{name}"
                spec = importlib.util.spec_from_file_location(module_name, str(candidate))
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[module_name] = module
                    spec.loader.exec_module(module)
                    return module
            except Exception as e:
                print(f"Failed to load plugin from {candidate}: {e}", file=sys.stderr)
    return None

def call_openai_json(model: str, instructions: str, user_text: str) -> dict:
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError("openai パッケージがインストールされていません。") from exc

    client = OpenAI()
    response = client.responses.create(
        model=model,
        instructions=instructions,
        input=user_text,
        text={"format": {"type": "json_object"}},
    )
    output_text = getattr(response, "output_text", "")
    if not output_text:
        raise RuntimeError("AI応答からテキストを取得できませんでした。")
    return json.loads(output_text)

def call_gemini_json(model: str, instructions: str, user_text: str) -> dict:
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        import subprocess
        print("Installing google-genai...", file=sys.stderr)
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "google-genai"], check=True, stdout=subprocess.DEVNULL)
            from google import genai
            from google.genai import types
        except Exception as e:
            raise RuntimeError(f"google-genai パッケージのインストールに失敗しました: {e}")

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("環境変数 GEMINI_API_KEY が設定されていません。")

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=model,
        contents=user_text,
        config=types.GenerateContentConfig(
            system_instruction=instructions,
            response_mime_type="application/json",
        ),
    )
    if not response.text:
        raise RuntimeError("Geminiからの応答が空でした。")
    
    text = response.text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines[-1].startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()
        
    return json.loads(text)

def create_summary(
    root: Path,
    material: Path,
    course: Course | None,
    text: str,
    model: str = "gemini-2.5-flash",
    local_only: bool = False,
    api_provider: str = "gemini",
) -> SummaryRecord:
    custom_analyzer = find_custom_plugin("summary_analyzer")
    if custom_analyzer:
        try:
            print(f"Using custom summary analyzer plugin: {custom_analyzer.__file__}")
            summary = custom_analyzer.create_summary(
                root, material, course, text, model, local_only, api_provider
            )
            if isinstance(summary, SummaryRecord):
                return summary
            elif isinstance(summary, dict):
                return SummaryRecord(
                    path=summary.get("path", normalize_record_path(relative_to_root(root, material))),
                    summary=summary.get("summary", ""),
                    key_points=string_list(summary.get("key_points")),
                    important_terms=string_list(summary.get("important_terms")),
                    review_checklist=string_list(summary.get("review_checklist")),
                    learning_priority=summary.get("learning_priority", 3),
                    priority_reason=summary.get("priority_reason", ""),
                    priority_category=summary.get("priority_category", "補足資料"),
                )
        except Exception as e:
            print(f"Error executing custom summary analyzer plugin: {e}", file=sys.stderr)

    if not local_only:
        instructions = (
            "あなたは大学生の授業資料を分かりやすく整理・解説する優秀な学習支援AIアシスタントです。\n"
            "入力された授業資料を日本語で論理的に分析し、JSON形式でのみ回答を返してください。マークダウンのコードブロックなどで囲まず、純粋なJSON文字列だけを出力してください。\n"
            "JSONの構造は以下のキーを必ず持たせてください：\n"
            "1. `title`: 授業資料の内容を的確に表す、簡潔で分かりやすいタイトル（20文字程度）。\n"
            "2. `summary`: この授業回の「核心テーマ（何のための授業か、何を解決するのか）」から書き始め、授業全体の論理の流れが専門用語を知らない人にも直感的に伝わるように、300〜500文字程度で分かりやすく説明した文章。\n"
            "3. `key_points`: 授業の重要なポイントをまとめた文字列の配列。各要素は単一の文章として独立して意味が通り、具体的な内容を含むもの（例：「〜の定義とメリット」「〜における3つの主要課題」など）にしてください。\n"
            "4. `important_terms`: 学習上、絶対に外せない最重要キーワードとその簡単な解説を組み合わせた文字列の配列（例：「キーワード: ○○について解説した説明文」形式）。\n"
            "5. `review_checklist`: 授業内容が定着したかを自己確認（セルフテスト）するためのチェックリスト。単に「○○について」ではなく、「○○の仕組みを説明できるか？」「○○と○○の違いを3つ挙げられるか？」といった、具体的な疑問文形式の文字列の配列にしてください。\n"
            "6. `learning_priority`: 資料の学習優先度を1から5の整数（1：非常に低い、2：低い、3：中程度、4：高い、5：非常に高い）で表したもの。授業全体における中心的内容か、後続授業の理解に必要か、重要概念が多いかなどを総合的に資料内容のみから判断してください。※「試験頻出」「試験に出る」などの推測は絶対に行わないこと。\n"
            "7. `priority_reason`: その学習優先度を判定した具体的な理由（100文字程度）。資料内に書かれている内容のみに基づいて判断してください。\n"
            "8. `priority_category`: 資料のカテゴリ。以下のいずれかの文字列から1つ選択してください：'基礎概念', '重要概念', '応用内容', '演習', '補足資料', '参考資料'。\n"
        )
        user_text = (
            f"授業名: {course.name if course else 'その他'}\n"
            f"教員名: {course.teacher if course else ''}\n"
            f"資料名: {material.name}\n\n"
            f"資料本文:\n{trim_text(text)}"
        )
        if api_provider == "gemini" and os.environ.get("GEMINI_API_KEY"):
            try:
                payload = call_gemini_json(model, instructions, user_text)
                try:
                    priority = int(payload.get("learning_priority", 3))
                    priority = max(1, min(5, priority))
                except Exception:
                    priority = 3
                return SummaryRecord(
                    path=normalize_record_path(relative_to_root(root, material)),
                    summary=str(payload.get("summary") or ""),
                    key_points=string_list(payload.get("key_points")),
                    important_terms=string_list(payload.get("important_terms")),
                    review_checklist=string_list(payload.get("review_checklist")),
                    learning_priority=priority,
                    priority_reason=str(payload.get("priority_reason") or ""),
                    priority_category=str(payload.get("priority_category") or "補足資料"),
                )
            except Exception as exc:
                print(f"Gemini分析に失敗したためローカル要約に切り替えます: {exc}", file=sys.stderr)
        elif api_provider == "openai" and os.environ.get("OPENAI_API_KEY"):
            try:
                payload = call_openai_json(model, instructions, user_text)
                try:
                    priority = int(payload.get("learning_priority", 3))
                    priority = max(1, min(5, priority))
                except Exception:
                    priority = 3
                return SummaryRecord(
                    path=normalize_record_path(relative_to_root(root, material)),
                    summary=str(payload.get("summary") or ""),
                    key_points=string_list(payload.get("key_points")),
                    important_terms=string_list(payload.get("important_terms")),
                    review_checklist=string_list(payload.get("review_checklist")),
                    learning_priority=priority,
                    priority_reason=str(payload.get("priority_reason") or ""),
                    priority_category=str(payload.get("priority_category") or "補足資料"),
                )
            except Exception as exc:
                print(f"OpenAI分析に失敗したためローカル要約に切り替えます: {exc}", file=sys.stderr)

    return local_summary(root, material, course, text)

def create_questions(
    course: Course,
    context: str,
    source_paths: list[str],
    count: int = 3,
    model: str = "gemini-2.5-flash",
    local_only: bool = False,
    api_provider: str = "gemini",
) -> list[QuestionRecord]:
    custom_creator = find_custom_plugin("question_creator")
    if custom_creator:
        try:
            print(f"Using custom question creator plugin: {custom_creator.__file__}")
            questions = custom_creator.create_questions(
                course, context, source_paths, count, model, local_only, api_provider
            )
            validated_questions = []
            for item in questions:
                if isinstance(item, QuestionRecord):
                    validated_questions.append(item)
                elif isinstance(item, dict):
                    validated_questions.append(
                        QuestionRecord(
                            course=item.get("course", course.name),
                            title=item.get("title", "練習問題"),
                            question=item.get("question", ""),
                            answer=item.get("answer", ""),
                            source_paths=item.get("source_paths", source_paths),
                        )
                    )
            return validated_questions
        except Exception as e:
            print(f"Error executing custom question creator plugin: {e}", file=sys.stderr)

    if not local_only:
        instructions = (
            "あなたは授業内容の定着度を測る問題作成AIです。"
            "入力された授業資料だけを根拠に、日本語で練習問題を作ってください。"
            "JSONだけを返してください。キーは questions です。"
            "questions は配列で、各要素は title, question, answer を持ちます。"
        )
        user_text = (
            f"授業名: {course.name}\n"
            f"教員名: {course.teacher}\n"
            f"問題数: {count}\n\n"
            f"資料・要約:\n{trim_text(context)}"
        )
        if api_provider == "gemini" and os.environ.get("GEMINI_API_KEY"):
            try:
                payload = call_gemini_json(model, instructions, user_text)
                raw_questions = payload.get("questions", [])
                results = []
                for item in raw_questions[:count]:
                    if not isinstance(item, dict):
                        continue
                    results.append(
                        QuestionRecord(
                            course=course.name,
                            title=str(item.get("title") or "練習問題"),
                            question=str(item.get("question") or ""),
                            answer=str(item.get("answer") or ""),
                            source_paths=source_paths,
                        )
                    )
                if results:
                    return results
            except Exception as exc:
                print(f"Gemini問題生成に失敗したためローカル生成に切り替えます: {exc}", file=sys.stderr)
        elif api_provider == "openai" and os.environ.get("OPENAI_API_KEY"):
            try:
                payload = call_openai_json(model, instructions, user_text)
                raw_questions = payload.get("questions", [])
                results = []
                for item in raw_questions[:count]:
                    if not isinstance(item, dict):
                        continue
                    results.append(
                        QuestionRecord(
                            course=course.name,
                            title=str(item.get("title") or "練習問題"),
                            question=str(item.get("question") or ""),
                            answer=str(item.get("answer") or ""),
                            source_paths=source_paths,
                        )
                    )
                if results:
                    return results
            except Exception as exc:
                print(f"OpenAI問題生成に失敗したためローカル生成に切り替えます: {exc}", file=sys.stderr)

    return local_questions(course, context, source_paths, count)

def local_summary(
    root: Path, material: Path, course: Course | None, text: str
) -> SummaryRecord:
    sentences = split_sentences(text)
    terms = [term for term, _count in Counter(tokenize(text)).most_common(10)]
    key_points = sentences[:5] if sentences else terms[:5]
    summary = " ".join(sentences[:3]) if sentences else " ".join(terms[:8])
    checklist = [f"{term} を説明できる" for term in terms[:5]]
    return SummaryRecord(
        path=normalize_record_path(relative_to_root(root, material)),
        summary=summary or "本文から十分な要約を作成できませんでした。",
        key_points=key_points,
        important_terms=terms,
        review_checklist=checklist,
        learning_priority=3,
        priority_reason="ローカル要約のため、デフォルトの学習優先度が設定されています。",
        priority_category="補足資料",
    )

def local_questions(
    course: Course, context: str, source_paths: list[str], count: int
) -> list[QuestionRecord]:
    terms = [term for term, _count in Counter(tokenize(context)).most_common(max(count, 1) * 2)]
    sentences = split_sentences(context)
    questions = []
    for index in range(count):
        term = terms[index % len(terms)] if terms else course.name
        sentence = sentences[index % len(sentences)] if sentences else context[:120]
        questions.append(
            QuestionRecord(
                course=course.name,
                title=f"{course.name} 確認問題 {index + 1}",
                question=f"「{term}」について、授業資料の内容に基づいて説明してください。",
                answer=term,
                source_paths=source_paths,
            )
        )
    return questions
