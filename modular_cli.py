import argparse
import sys
import os
from pathlib import Path

import src.core.models as models
import src.core.operations as ops
from src.core.indexing import update_search_index
from src.report.builder import build_site

def get_root(args) -> Path:
    r = getattr(args, "root", None)
    return Path(r or os.environ.get("PBL_ROOT", ".")).expanduser().resolve()

def add_course_cmd(args) -> int:
    root = get_root(args)
    courses, records = models.load_state(root)
    if any(c.name == args.name for c in courses):
        print(f"Error: Course '{args.name}' already exists.", file=sys.stderr)
        return 1
    
    kws = [k.strip() for k in args.keywords.split(",") if k.strip()]
    c = models.Course(name=args.name, teacher=args.teacher, keywords=kws)
    courses.append(c)
    models.save_courses(root, courses)
    print(f"Added course: {args.name}")
    return 0

def update_course_cmd(args) -> int:
    root = get_root(args)
    courses, records = models.load_state(root)
    c = next((co for co in courses if co.name == args.name), None)
    if not c:
        print(f"Error: Course '{args.name}' not found.", file=sys.stderr)
        return 1
    if args.teacher is not None:
        c.teacher = args.teacher
    if args.keywords is not None:
        c.keywords = [k.strip() for k in args.keywords.split(",") if k.strip()]
    models.save_courses(root, courses)
    print(f"Updated course: {args.name}")
    return 0

def list_courses_cmd(args) -> int:
    root = get_root(args)
    courses = models.load_courses(root)
    if not courses:
        print("No courses registered.")
        return 0
    for c in courses:
        print(f"- {c.name} (Teacher: {c.teacher or 'None'}, Keywords: {', '.join(c.keywords)})")
    return 0

def sort_cmd(args) -> int:
    return ops.sort_materials_op(
        get_root(args),
        provider=args.provider,
        copy=not args.no_copy,
        threshold=args.threshold
    )

def reassign_cmd(args) -> int:
    target_course = args.course if args.course != "None" else None
    return ops.reassign_material_op(
        get_root(args),
        Path(args.file),
        target_course
    )

def delete_material_cmd(args) -> int:
    return ops.delete_material_op(get_root(args), Path(args.file))

def analyze_cmd(args) -> int:
    mode = "local" if args.local else "ai"
    return ops.analyze_material_op(
        get_root(args),
        Path(args.file),
        provider=args.provider,
        mode=mode
    )

def generate_practice_cmd(args) -> int:
    return ops.generate_practice_op(
        get_root(args),
        args.course,
        provider=args.provider
    )

def build_site_cmd(args) -> int:
    root = get_root(args)
    dest = root / args.output
    update_search_index(root)
    build_site(root, dest)
    print(f"Built site at: {dest}")
    return 0

def clear_analysis_cmd(args) -> int:
    root = get_root(args)
    courses, records = models.load_state(root)
    
    target_course_name = getattr(args, "course", None)
    target_material_path_str = getattr(args, "material", None)
    
    summaries = models.load_summaries(root)
    remaining_summaries = []
    cleared_sum = 0
    
    for s in summaries:
        should_clear = False
        if target_course_name and s.course == target_course_name:
            should_clear = True
        elif target_material_path_str:
            mat_path = Path(target_material_path_str).expanduser().resolve()
            rec_path = (root / s.path).resolve()
            if mat_path == rec_path:
                should_clear = True
        elif not target_course_name and not target_material_path_str:
            should_clear = True
            
        if should_clear:
            path = root / s.path
            pdf_path = path.with_suffix(path.suffix + ".summary.pdf")
            if pdf_path.exists():
                try:
                    pdf_path.unlink()
                except Exception:
                    pass
            cleared_sum += 1
        else:
            remaining_summaries.append(s)
            
    models.save_summaries(root, remaining_summaries)
    print(f"要約を {cleared_sum} 件削除しました。")
    
    questions = models.load_questions(root)
    remaining_qs = []
    cleared_q = 0
    
    for q in questions:
        should_clear = False
        if target_course_name and q.course == target_course_name:
            should_clear = True
        elif not target_course_name and not target_material_path_str:
            should_clear = True
            
        if should_clear:
            cleared_q += 1
        else:
            remaining_qs.append(q)
            
    models.save_questions(root, remaining_qs)
    print(f"練習問題を {cleared_q} 問削除しました。")
    
    build_site(root, root / "_site")
    return 0

def load_command_plugins(subparsers) -> None:
    import importlib.util
    plugins_dir = Path.cwd() / "plugins"
    if not plugins_dir.exists() or not plugins_dir.is_dir():
        return
    for candidate in plugins_dir.glob("cmd_*.py"):
        if candidate.is_file():
            try:
                module_name = f"custom_cmd_{candidate.stem}"
                spec = importlib.util.spec_from_file_location(module_name, str(candidate))
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[module_name] = module
                    spec.loader.exec_module(module)
                    if hasattr(module, "register_subcommand"):
                        module.register_subcommand(subparsers)
            except Exception as e:
                print(f"Failed to load command plugin from {candidate}: {e}", file=sys.stderr)

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="授業資料コンパイラ CLI")
    parser.add_argument("--root", help="授業フォルダと設定を保存するルート")
    
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    add = subparsers.add_parser("add-course", help="授業を登録して保存フォルダを作成")
    add.add_argument("name", help="授業名")
    add.add_argument("--teacher", default="", help="教員名")
    add.add_argument("--keywords", default="", help="カンマ区切りのキーワード")
    add.set_defaults(func=add_course_cmd)
    
    update = subparsers.add_parser("update-course", help="授業の教員名・キーワードを更新")
    update.add_argument("name", help="授業名")
    update.add_argument("--teacher", help="教員名")
    update.add_argument("--keywords", help="キーワード")
    update.set_defaults(func=update_course_cmd)
    
    list_c = subparsers.add_parser("list-courses", help="登録済みの授業一覧を表示")
    list_c.set_defaults(func=list_courses_cmd)
    
    sort = subparsers.add_parser("sort", help="未分類資料を自動分類")
    sort.add_argument("--provider", default="gemini", help="AIモデルプロバイダー")
    sort.add_argument("--no-copy", action="store_true", help="コピーの代わりに移動する")
    sort.add_argument("--threshold", type=float, default=0.3, help="類似度しきい値")
    sort.set_defaults(func=sort_cmd)
    
    reassign = subparsers.add_parser("reassign", help="資料を特定の授業へ再割当て")
    reassign.add_argument("file", help="資料ファイルのパス")
    reassign.add_argument("course", help="授業名またはNone")
    reassign.set_defaults(func=reassign_cmd)
    
    delete = subparsers.add_parser("delete-material", help="資料を削除")
    delete.add_argument("file", help="資料ファイルのパス")
    delete.set_defaults(func=delete_material_cmd)
    
    analyze = subparsers.add_parser("analyze", help="資料をAI要約分析")
    analyze.add_argument("file", help="資料ファイルのパス")
    analyze.add_argument("--provider", default="gemini", help="AIプロバイダー")
    analyze.add_argument("--local", action="store_true", help="ローカル分析（AI未使用）")
    analyze.set_defaults(func=analyze_cmd)
    
    gen = subparsers.add_parser("generate-practice", help="練習問題を作成")
    gen.add_argument("course", help="授業名")
    gen.add_argument("--provider", default="gemini", help="AIプロバイダー")
    gen.set_defaults(func=generate_practice_cmd)
    
    site = subparsers.add_parser("build-site", help="Webポータルサイトをビルド")
    site.add_argument("--output", default="_site", help="出力先フォルダ")
    site.set_defaults(func=build_site_cmd)
    
    clear = subparsers.add_parser("clear-analysis", help="作成した要約や練習問題を消去")
    clear.add_argument("--course", help="対象授業")
    clear.add_argument("--material", help="対象資料")
    clear.set_defaults(func=clear_analysis_cmd)
    
    load_command_plugins(subparsers)
    return parser

def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if hasattr(args, "func"):
        return args.func(args)
    parser.print_help()
    return 1

if __name__ == "__main__":
    import multiprocessing
    # Safeguard for multiprocessing on Windows
    multiprocessing.freeze_support()
    raise SystemExit(main())
