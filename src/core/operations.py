import sys
from pathlib import Path

from src.core.models import (
    load_state, save_state, load_summaries, save_summaries, load_questions, save_questions,
    normalize_record_path, MaterialRecord, SummaryRecord, QuestionRecord
)
from src.core.indexing import update_search_index
from src.data.extractor import extract_text, tokenize
from src.ai.agent import create_summary, create_questions, local_summary, local_questions
from src.report.builder import build_site
from src.report.timeline import find_summary, find_material_record, write_summary_pdf

def sort_materials_op(root: Path, provider: str = "gemini", copy: bool = True, threshold: float = 0.3, ocr_language: str = "jpn+eng") -> int:
    courses, records = load_state(root)
    unsorted_dir = root / "unsorted"
    if not unsorted_dir.exists():
        unsorted_dir.mkdir(parents=True, exist_ok=True)
        print("unsorted directory created. Please put materials there.")
        return 0

    files = [p for p in unsorted_dir.rglob("*") if p.is_file()]
    if not files:
        print("No files to sort in unsorted/.")
        return 0

    print(f"Found {len(files)} files to sort.")
    
    for f in files:
        # Check if already sorted
        rel_path = normalize_record_path(f.relative_to(root))
        if any(normalize_record_path(r.path) == rel_path for r in records):
            continue

        print(f"Processing {f.name}...")
        text = extract_text(f)
        tokens = tokenize(text)
        
        assigned_course = None
        max_score = 0.0
        
        for c in courses:
            if not c.keywords:
                continue
            # Basic keyword score matching
            score = sum(1 for kw in c.keywords if kw.lower() in text.lower())
            score_ratio = score / len(c.keywords) if c.keywords else 0.0
            
            if score_ratio >= threshold and score_ratio > max_score:
                max_score = score_ratio
                assigned_course = c.name

        # If matched a course, we can copy or move it
        target_path = f
        if assigned_course:
            course_dir = root / assigned_course / f.parent.name
            if f.parent.name == "unsorted":
                course_dir = root / assigned_course / f.suffix.lstrip(".").lower()
            course_dir.mkdir(parents=True, exist_ok=True)
            
            dest = course_dir / f.name
            if copy:
                import shutil
                shutil.copy2(f, dest)
                target_path = dest
            else:
                shutil.move(f, dest)
                target_path = dest

        new_rel = normalize_record_path(target_path.relative_to(root))
        records.append(MaterialRecord(
            path=new_rel,
            course=assigned_course
        ))

    save_state(root, courses, records)
    update_search_index(root)
    build_site(root, root / "_site")
    print("Sorting completed.")
    return 0

def reassign_material_op(root: Path, file_path: Path, target_course: str | None) -> int:
    courses, records = load_state(root)
    # Target can be "None" string or actual course name
    course_val = target_course if target_course != "None" else None
    
    # Resolve relative path
    try:
        rel = normalize_record_path(file_path.relative_to(root))
    except Exception:
        rel = normalize_record_path(file_path)

    found = False
    for r in records:
        if normalize_record_path(r.path) == rel:
            r.course = course_val
            found = True
            break
            
    if not found:
        # Register new record
        records.append(MaterialRecord(path=rel, course=course_val))

    # Optional: Move physical file
    if course_val:
        p = root / rel
        if p.exists() and p.is_file():
            dest_dir = root / course_val / p.parent.name
            if p.parent.name == root.name or p.parent.name == "unsorted" or p.parent.name in [c.name for c in courses]:
                dest_dir = root / course_val / p.suffix.lstrip(".").lower()
            dest_dir.mkdir(parents=True, exist_ok=True)
            
            dest = dest_dir / p.name
            try:
                import shutil
                shutil.move(str(p), str(dest))
                # Update path in record
                for r in records:
                    if normalize_record_path(r.path) == rel:
                        r.path = normalize_record_path(dest.relative_to(root))
                        break
            except Exception as e:
                print(f"Could not physically move file: {e}", file=sys.stderr)

    save_state(root, courses, records)
    update_search_index(root)
    build_site(root, root / "_site")
    print(f"Reassigned {file_path.name} to {course_val}.")
    return 0

def delete_material_op(root: Path, file_path: Path) -> int:
    courses, records = load_state(root)
    try:
        rel = normalize_record_path(file_path.relative_to(root))
    except Exception:
        rel = normalize_record_path(file_path)

    # Delete physical file
    p = root / rel
    if p.exists() and p.is_file():
        try:
            p.unlink()
        except Exception as e:
            print(f"Failed to delete file {p}: {e}", file=sys.stderr)

    # Remove record
    records = [r for r in records if normalize_record_path(r.path) != rel]
    
    # Remove summary
    summaries = load_summaries(root)
    summaries = [s for s in summaries if normalize_record_path(s.path) != rel]
    save_summaries(root, summaries)

    save_state(root, courses, records)
    update_search_index(root)
    build_site(root, root / "_site")
    print(f"Deleted material: {file_path.name}.")
    return 0

def analyze_material_op(root: Path, file_path: Path, provider: str = "gemini", mode: str = "ai") -> int:
    courses, records = load_state(root)
    summaries = load_summaries(root)
    
    try:
        rel = normalize_record_path(file_path.relative_to(root))
    except Exception:
        rel = normalize_record_path(file_path)

    p = root / rel
    if not p.exists() or not p.is_file():
        print(f"File not found: {p}", file=sys.stderr)
        return 1

    print(f"Analyzing {p.name}...")
    text = extract_text(p)

    course_name = next((r.course for r in records if normalize_record_path(r.path) == rel), None)
    course = next((c for c in courses if c.name == course_name), None)
    summary_rec = create_summary(
        root,
        p,
        course,
        text,
        local_only=mode == "local",
        api_provider=provider,
    )
        
    summary_rec.path = rel
    
    # Overwrite if exists
    summaries = [s for s in summaries if normalize_record_path(s.path) != rel]
    summaries.append(summary_rec)
    save_summaries(root, summaries)

    # Write summary PDF
    pdf_path = p.with_suffix(p.suffix + ".summary.pdf")
    write_summary_pdf(pdf_path, p.name, summary_rec)

    update_search_index(root)
    build_site(root, root / "_site")
    print(f"Analysis completed for {p.name}.")
    return 0

def generate_practice_op(root: Path, course_name: str, provider: str = "gemini") -> int:
    courses, records = load_state(root)
    questions = load_questions(root)
    
    course = next((c for c in courses if c.name == course_name), None)
    if not course:
        print(f"Course not found: {course_name}", file=sys.stderr)
        return 1

    mats = []
    for r in records:
        if r.course == course_name:
            p = root / r.path
            if p.exists() and p.is_file():
                mats.append(p)
                
    if not mats:
        print(f"No materials registered for course {course_name}.", file=sys.stderr)
        return 1

    print(f"Generating practice questions for {course_name} using {len(mats)} materials...")
    
    try:
        # Combine texts
        all_text = ""
        for m in mats:
            all_text += f"\n--- {m.name} ---\n" + extract_text(m)
            if len(all_text) > 8000:
                break

        q_list = create_questions(
            course,
            all_text,
            [normalize_record_path(m.relative_to(root)) for m in mats],
            model="gemini-2.5-flash",
            local_only=provider == "local",
            api_provider=provider,
        )

        for q in q_list:
            q.course = course_name
            # associate with all materials of this course
            q.source_paths = [normalize_record_path(m.relative_to(root)) for m in mats]

        # Append and save
        questions.extend(q_list)
        save_questions(root, questions)
        build_site(root, root / "_site")
        print(f"Successfully generated {len(q_list)} practice questions.")
        return 0
    except Exception as e:
        print(f"Practice generator failed: {e}", file=sys.stderr)
        return 1
