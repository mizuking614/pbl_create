import sys

def create_questions(
    course,
    context: str,
    source_paths: list[str],
    count: int,
    model: str,
    local_only: bool,
    api_provider: str = "openai",
) -> list[dict]:
    """
    Custom question generator plugin.
    Can return a list of QuestionRecord objects or list of dicts.
    """
    print(f"[Plugin Log] Custom question creator invoked for course: {course.name}", file=sys.stderr)
    
    # Return mock questions as a demonstration
    mock_questions = []
    for i in range(1, count + 1):
        mock_questions.append({
            "course": course.name,
            "title": f"{course.name} プラグイン問題 {i}",
            "question_type": "multiple_choice",
            "question": f"これはカスタムプラグインで生成された {course.name} に関する質問 {i} です。",
            "answer": "解答",
            "explanation": "この問題と解説は外部プラグイン (plugins/question_creator.py) から生成されました。",
            "source_paths": source_paths,
            "source": "custom_question_creator_plugin"
        })
    return mock_questions
