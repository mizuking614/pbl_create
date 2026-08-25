import json
import sys
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor

from src.core.models import (
    load_state, load_summaries, load_questions, search_index_path,
    normalize_record_path
)
from src.report.timeline import find_summary, relative_to_root
from src.data.extractor import extract_text

def extract_single_file_worker(args: tuple[str, str]) -> tuple[str, str]:
    # Returns (normalized_rel_path, extracted_text)
    root_str, rel_path_str = args
    root = Path(root_str)
    full_path = root / rel_path_str
    
    if not full_path.exists() or not full_path.is_file():
        return rel_path_str, ""
        
    try:
        text = extract_text(full_path)
        return rel_path_str, text
    except Exception as e:
        print(f"Error extracting {full_path.name} in parallel: {e}", file=sys.stderr)
        return rel_path_str, ""

def update_search_index(root: Path) -> None:
    courses, records = load_state(root)
    summaries = load_summaries(root)
    questions = load_questions(root)
    
    idx_path = search_index_path(root)
    
    # Load existing search index
    existing_index = {}
    if idx_path.exists():
        try:
            data = json.loads(idx_path.read_text(encoding="utf-8"))
            for item in data.get("index", []):
                existing_index[item["path"]] = item
        except Exception:
            pass
            
    updated_items = []
    files_to_process = []
    
    # Find files that need extraction
    for record in records:
        rel_path = normalize_record_path(record.path)
        full_path = root / rel_path
        if not full_path.exists() or not full_path.is_file():
            continue
            
        mtime = full_path.stat().st_mtime
        size = full_path.stat().st_size
        
        # Check cache
        cache = existing_index.get(rel_path)
        if cache and cache.get("mtime") == mtime and cache.get("size") == size:
            # Re-read OCR text from cache, but update metadata just in case course/teacher changed
            updated_items.append({
                "path": rel_path,
                "course": record.course or "",
                "teacher": next((c.teacher for c in courses if c.name == record.course), ""),
                "material_name": full_path.name,
                "ocr_text": cache.get("ocr_text", ""),
                "summary": cache.get("summary", ""),
                "key_points": cache.get("key_points", []),
                "important_terms": cache.get("important_terms", []),
                "review_checklist": cache.get("review_checklist", []),
                "keywords": cache.get("keywords", []),
                "mtime": mtime,
                "size": size
            })
        else:
            files_to_process.append((str(root), rel_path))
            
    # Process modified/new files in parallel using ProcessPoolExecutor
    extracted_texts = {}
    if files_to_process:
        print(f"Parallel extracting {len(files_to_process)} modified/new files...")
        try:
            # Set max_workers to speed up but keep machine responsive
            with ProcessPoolExecutor() as executor:
                results = executor.map(extract_single_file_worker, files_to_process)
                for rel_path, text in results:
                    extracted_texts[rel_path] = text
        except Exception as e:
            # Fallback to serial extraction if multiprocessing fails
            print(f"Parallel extraction failed, falling back to serial: {e}", file=sys.stderr)
            for root_str, rel_path in files_to_process:
                extracted_texts[rel_path] = extract_text(Path(root_str) / rel_path)
                
    # Reassemble search index records
    for root_str, rel_path in files_to_process:
        full_path = Path(root_str) / rel_path
        mtime = full_path.stat().st_mtime
        size = full_path.stat().st_size
        
        record = next(r for r in records if normalize_record_path(r.path) == rel_path)
        summary_rec = find_summary(summaries, Path(root_str), full_path)
        
        course_keywords = []
        c_obj = next((c for c in courses if c.name == record.course), None)
        if c_obj:
            course_keywords = c_obj.keywords + c_obj.learned_terms
            
        updated_items.append({
            "path": rel_path,
            "course": record.course or "",
            "teacher": c_obj.teacher if c_obj else "",
            "material_name": full_path.name,
            "ocr_text": extracted_texts.get(rel_path, ""),
            "summary": summary_rec.summary if summary_rec else "",
            "key_points": summary_rec.key_points if summary_rec else [],
            "important_terms": summary_rec.important_terms if summary_rec else [],
            "review_checklist": summary_rec.review_checklist if summary_rec else [],
            "keywords": course_keywords,
            "mtime": mtime,
            "size": size
        })
        
    # Write search index file
    try:
        idx_path.write_text(json.dumps({"index": updated_items}, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception as e:
        print(f"Failed to write search index: {e}", file=sys.stderr)
