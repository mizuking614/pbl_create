import json
import os
import re
import shutil
import sys
from pathlib import Path
from dataclasses import dataclass, field, asdict

SUPPORTED_EXTENSIONS = {
    ".pdf", ".docx", ".doc", ".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".gif",
    ".txt", ".md", ".py", ".csv", ".json"
}

@dataclass
class AttendanceRecord:
    date: str
    class_round: int
    status: str
    memo: str = ""

@dataclass
class LinkRecord:
    title: str
    url: str
    memo: str = ""

@dataclass
class Course:
    name: str
    teacher: str
    keywords: list[str] = field(default_factory=list)
    folder: str = ""
    learned_terms: list[str] = field(default_factory=list)
    attendance: list[AttendanceRecord] = field(default_factory=list)
    links: list[LinkRecord] = field(default_factory=list)

@dataclass
class MaterialRecord:
    path: str
    course: str | None = None
    learned_terms: list[str] = field(default_factory=list)
    score: float = 0.0
    class_round: int | None = None

@dataclass
class SummaryRecord:
    path: str
    summary: str
    key_points: list[str] = field(default_factory=list)
    important_terms: list[str] = field(default_factory=list)
    review_checklist: list[str] = field(default_factory=list)
    learning_priority: int = 3
    priority_category: str = "補足資料"
    priority_reason: str = ""

@dataclass
class QuestionRecord:
    title: str
    question: str
    answer: str
    source_paths: list[str] = field(default_factory=list)
    course: str | None = None

def root_path() -> Path:
    return Path(os.environ.get("PBL_ROOT", ".")).resolve()

def app_dir(root: Path) -> Path:
    d = root / ".class_materials"
    d.mkdir(parents=True, exist_ok=True)
    return d

def config_path(root: Path) -> Path:
    return app_dir(root) / "courses.json"

def summaries_path(root: Path) -> Path:
    return app_dir(root) / "summaries.json"

def questions_path(root: Path) -> Path:
    return app_dir(root) / "questions.json"

def global_links_path(root: Path) -> Path:
    return app_dir(root) / "global_links.json"

def search_index_path(root: Path) -> Path:
    d = app_dir(root) / "index"
    d.mkdir(parents=True, exist_ok=True)
    return d / "search_index.json"

def normalize_record_path(p: str | Path) -> str:
    return str(Path(p).as_posix())

def material_path(root: Path, rel: str) -> Path:
    return root / rel

def href_between(base_dir: Path, target_path: Path) -> str:
    try:
        rel = os.path.relpath(target_path, base_dir)
        return Path(rel).as_posix()
    except Exception:
        return Path(target_path).as_posix()

def relative_to_root(root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(root).as_posix())
    except Exception:
        return str(path.name)

def safe_folder_name(name: str) -> str:
    cleaned = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", name).strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned or "untitled_course"

def split_keywords(raw: str) -> list[str]:
    return [item.strip() for item in re.split(r"[,、\n]", raw) if item.strip()]

def unique_destination(path: Path) -> Path:
    if not path.exists():
        return path
    stem = path.stem
    suffix = path.suffix
    for index in range(1, 1000):
        candidate = path.with_name(f"{stem}_{index}{suffix}")
        if not candidate.exists():
            return candidate
    raise RuntimeError(f"Cannot decide destination: {path}")

def migrate_existing_files(root: Path, courses: list[Course], records: list[MaterialRecord]) -> bool:
    modified = False
    for record in records:
        path = material_path(root, record.path)
        if not path.exists() or not path.is_file():
            continue
        suffix = path.suffix.lower().lstrip(".") or "file"
        parent_name = path.parent.name.lower()
        if parent_name == suffix:
            continue
        dest_dir = path.parent / suffix
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_path = unique_destination(dest_dir / path.name)
        try:
            shutil.move(str(path), str(dest_path))
            record.path = normalize_record_path(relative_to_root(root, dest_path))
            modified = True
        except Exception as e:
            print(f"Failed to migrate {path.name}: {e}", file=sys.stderr)

    target_dirs = [root / "その他"] + [root / c.folder for c in courses if c.folder]
    for target_dir in target_dirs:
        if not target_dir.exists():
            continue
        try:
            for path in list(target_dir.iterdir()):
                if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS:
                    suffix = path.suffix.lower().lstrip(".") or "file"
                    dest_dir = target_dir / suffix
                    dest_dir.mkdir(parents=True, exist_ok=True)
                    dest_path = unique_destination(dest_dir / path.name)
                    try:
                        shutil.move(str(path), str(dest_path))
                        modified = True
                    except Exception as e:
                        print(f"Failed to migrate physical file {path.name}: {e}", file=sys.stderr)
        except Exception as e:
            print(f"Failed to read target dir {target_dir.name}: {e}", file=sys.stderr)
    return modified

def load_courses(root: Path) -> list[Course]:
    courses, _records = load_state(root)
    return courses

def save_courses(root: Path, courses: list[Course]) -> None:
    _, records = load_state(root)
    save_state(root, courses, records)

def load_state(root: Path) -> tuple[list[Course], list[MaterialRecord]]:
    path = config_path(root)
    if not path.exists():
        return [], []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        courses = []
        for item in data.get("courses", []):
            attendance = []
            for att in item.get("attendance", []):
                attendance.append(AttendanceRecord(
                    date=att.get("date", ""),
                    class_round=att.get("class_round", 1),
                    status=att.get("status", "出席"),
                    memo=att.get("memo", "")
                ))
            links = []
            for lk in item.get("links", []):
                links.append(LinkRecord(
                    title=lk.get("title", ""),
                    url=lk.get("url", ""),
                    memo=lk.get("memo", "")
                ))
            courses.append(Course(
                name=item["name"],
                teacher=item.get("teacher", ""),
                keywords=item.get("keywords", []),
                folder=item.get("folder", ""),
                learned_terms=item.get("learned_terms", []),
                attendance=attendance,
                links=links
            ))
        records = []
        for r in data.get("materials", []):
            records.append(MaterialRecord(
                path=normalize_record_path(r["path"]),
                course=r.get("course"),
                learned_terms=r.get("learned_terms", []),
                score=r.get("score", 0.0),
                class_round=r.get("class_round")
            ))
        
        if migrate_existing_files(root, courses, records):
            save_state(root, courses, records)
            
        return courses, records
    except Exception as e:
        print(f"Load state error: {e}", file=sys.stderr)
        return [], []

def save_state(root: Path, courses: list[Course], records: list[MaterialRecord]) -> None:
    app_dir(root).mkdir(parents=True, exist_ok=True)
    courses_payload = []
    for c in courses:
        courses_payload.append({
            "name": c.name,
            "teacher": c.teacher,
            "keywords": c.keywords,
            "folder": c.folder,
            "learned_terms": c.learned_terms,
            "attendance": [asdict(a) for a in c.attendance],
            "links": [asdict(l) for l in c.links]
        })
    records_payload = []
    for r in records:
        records_payload.append({
            "path": normalize_record_path(r.path),
            "course": r.course,
            "learned_terms": r.learned_terms,
            "score": r.score,
            "class_round": r.class_round
        })
    config_path(root).write_text(json.dumps({
        "courses": courses_payload,
        "materials": records_payload
    }, indent=2, ensure_ascii=False), encoding="utf-8")

def load_summaries(root: Path) -> list[SummaryRecord]:
    path = summaries_path(root)
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        summaries = []
        for s in data.get("summaries", []):
            summaries.append(SummaryRecord(
                path=normalize_record_path(s["path"]),
                summary=s["summary"],
                key_points=s.get("key_points", []),
                important_terms=s.get("important_terms", []),
                review_checklist=s.get("review_checklist", []),
                learning_priority=s.get("learning_priority", 3),
                priority_category=s.get("priority_category", "補足資料"),
                priority_reason=s.get("priority_reason", "")
            ))
        return summaries
    except Exception:
        return []

def save_summaries(root: Path, summaries: list[SummaryRecord]) -> None:
    path = summaries_path(root)
    out = []
    for s in summaries:
        out.append({
            "path": normalize_record_path(s.path),
            "summary": s.summary,
            "key_points": s.key_points,
            "important_terms": s.important_terms,
            "review_checklist": s.review_checklist,
            "learning_priority": s.learning_priority,
            "priority_category": s.priority_category,
            "priority_reason": s.priority_reason
        })
    path.write_text(json.dumps({"summaries": out}, indent=2, ensure_ascii=False), encoding="utf-8")

def load_questions(root: Path) -> list[QuestionRecord]:
    path = questions_path(root)
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        questions = []
        for q in data.get("questions", []):
            questions.append(QuestionRecord(
                title=q["title"],
                question=q["question"],
                answer=q["answer"],
                source_paths=[normalize_record_path(sp) for sp in q.get("source_paths", [])],
                course=q.get("course")
            ))
        return questions
    except Exception:
        return []

def save_questions(root: Path, questions: list[QuestionRecord]) -> None:
    path = questions_path(root)
    out = []
    for q in questions:
        out.append({
            "title": q.title,
            "question": q.question,
            "answer": q.answer,
            "source_paths": [normalize_record_path(sp) for sp in q.source_paths],
            "course": q.course
        })
    path.write_text(json.dumps({"questions": out}, indent=2, ensure_ascii=False), encoding="utf-8")

def load_global_links(root: Path) -> list[LinkRecord]:
    path = global_links_path(root)
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        links = []
        for lk in data.get("links", []):
            links.append(LinkRecord(
                title=lk.get("title", ""),
                url=lk.get("url", ""),
                memo=lk.get("memo", "")
            ))
        return links
    except Exception:
        return []

def save_global_links(root: Path, links: list[LinkRecord]) -> None:
    path = global_links_path(root)
    out = [asdict(l) for l in links]
    path.write_text(json.dumps({"links": out}, indent=2, ensure_ascii=False), encoding="utf-8")
