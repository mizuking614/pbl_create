import sys
from pathlib import Path
from collections import defaultdict
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from src.core.models import (
    Course, MaterialRecord, SummaryRecord, QuestionRecord, AttendanceRecord,
    normalize_record_path, relative_to_root, href_between
)

def escape(s: str) -> str:
    import html
    return html.escape(str(s))

def escape_attr(s: str) -> str:
    import html
    return html.escape(str(s), quote=True)

def find_summary(summaries: list[SummaryRecord], root: Path, material: Path) -> SummaryRecord | None:
    rel = normalize_record_path(relative_to_root(root, material))
    for s in summaries:
        if normalize_record_path(s.path) == rel:
            return s
    return None

def find_material_record(records: list[MaterialRecord], root: Path, material: Path) -> MaterialRecord | None:
    rel = normalize_record_path(relative_to_root(root, material))
    for r in records:
        if normalize_record_path(r.path) == rel:
            return r
    return None

def course_materials(root: Path, course: Course, records: list[MaterialRecord]) -> list[Path]:
    out = []
    for r in records:
        if r.course == course.name:
            p = root / r.path
            if p.exists() and p.is_file():
                out.append(p)
    return sorted(out, key=lambda x: x.name)

def unknown_materials(root: Path, records: list[MaterialRecord]) -> list[Path]:
    out = []
    for r in records:
        if not r.course:
            p = root / r.path
            if p.exists() and p.is_file():
                out.append(p)
    return sorted(out, key=lambda x: x.name)

def associate_material_to_round(material_path: Path, attendance_records: list[AttendanceRecord]) -> int | None:
    import re
    filename = material_path.name
    match = re.search(r'(?:第|round|l|L)\s*(\d+)', filename, re.IGNORECASE)
    if not match:
        match = re.search(r'\b(\d+)\b', filename)
    if match:
        try:
            return int(match.group(1))
        except ValueError:
            pass

    if not attendance_records:
        return None

    try:
        from datetime import datetime
        file_mtime = material_path.stat().st_mtime
        file_date = datetime.fromtimestamp(file_mtime).date()
    except Exception:
        return None

    closest_round = None
    min_diff = None
    for att in attendance_records:
        if not att.date:
            continue
        try:
            att_date = datetime.strptime(att.date, "%Y-%m-%d").date()
            diff = abs((file_date - att_date).days)
            if min_diff is None or diff < min_diff:
                min_diff = diff
                closest_round = att.class_round
        except Exception:
            continue
            
    if min_diff is not None and min_diff <= 7:
        return closest_round
    return None

def render_timeline_html(
    root: Path,
    output_dir: Path,
    course: Course,
    records: list[MaterialRecord],
    summaries: list[SummaryRecord],
    questions: list[QuestionRecord],
) -> str:
    mats = course_materials(root, course, records)
    round_materials = defaultdict(list)
    
    for mat in mats:
        record_obj = find_material_record(records, root, mat)
        c_round = getattr(record_obj, "class_round", None) if record_obj else None
        if c_round is None:
            c_round = associate_material_to_round(mat, course.attendance)
        if c_round is not None:
            round_materials[c_round].append(mat)
        else:
            round_materials[-1].append(mat)
            
    rounds = set(att.class_round for att in course.attendance)
    rounds.update(round_materials.keys())
    rounds.discard(-1)
    sorted_rounds = sorted(list(rounds))
    
    if not sorted_rounds and not round_materials[-1]:
        return ""
        
    timeline_items = []
    for r in sorted_rounds:
        att = next((a for a in course.attendance if a.class_round == r), None)
        date_str = att.date if att else "日付未設定"
        status = att.status if att else "出席状況未登録"
        memo = att.memo if att else ""
        
        mat_links = []
        for mat in round_materials[r]:
            href = href_between(output_dir, mat)
            summary_obj = find_summary(summaries, root, mat)
            importance_html = ""
            if summary_obj:
                lvl = getattr(summary_obj, "learning_priority", 3)
                cat = getattr(summary_obj, "priority_category", "補足資料")
                stars = "★" * lvl + "☆" * (5 - lvl)
                importance_html = f' <span class="stars" style="color:#d97706; font-size:0.8rem;" title="{escape_attr(summary_obj.priority_reason)}">({stars} | {escape(cat)})</span>'
            mat_links.append(f'<li><a href="{escape_attr(href)}" target="_blank" style="color:var(--accent); font-weight:500;">{escape(mat.name)}</a>{importance_html}</li>')
            
        materials_html = f"<ul style='margin:0; padding-left:20px; font-size:0.9rem;'>{''.join(mat_links)}</ul>" if mat_links else "<p style='margin:0; color:var(--muted); font-size:0.9rem;'>資料なし</p>"
        
        related_questions = []
        for q in questions:
            if q.course == course.name:
                for mat in round_materials[r]:
                    rel_mat_path = normalize_record_path(relative_to_root(root, mat))
                    if any(normalize_record_path(sp) == rel_mat_path for sp in q.source_paths):
                        related_questions.append(q)
                        break
                        
        questions_html = ""
        if related_questions:
            q_list = []
            for q in related_questions:
                q_list.append(f"<li style='margin-bottom:6px;'><strong>{escape(q.title)}</strong><br><span style='color:#4b5563; font-size:0.85rem;'>問: {escape(q.question)}</span></li>")
            questions_html = f"<ul style='margin:0; padding-left:20px; font-size:0.9rem;'>{''.join(q_list)}</ul>"
        else:
            questions_html = "<p style='margin:0; color:var(--muted); font-size:0.9rem;'>課題/練習問題なし</p>"
            
        status_color = "#0f766e" if status == "出席" else ("#d97706" if status == "遅刻" else "#dc2626")
        
        timeline_items.append(f"""
        <div class="timeline-item" style="border-left: 2px solid var(--line); padding-left: 20px; margin-bottom: 24px; position: relative;">
            <div class="timeline-badge" style="width: 12px; height: 12px; border-radius: 50%; background: {status_color}; position: absolute; left: -7px; top: 6px; border: 2px solid #fff; box-shadow: 0 0 0 2px {status_color};"></div>
            <h4 style="margin: 0 0 6px 0; color: var(--ink); font-size: 1.05rem;">第 {r} 回 - {escape(date_str)} ({escape(status)})</h4>
            {f'<p style="margin: 0 0 10px 0; font-size:0.9rem; color: var(--muted); font-style:italic;">メモ: {escape(memo)}</p>' if memo else ''}
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-top: 8px;">
                <div>
                    <strong style="font-size:0.85rem; color:var(--muted); text-transform:uppercase;">📁 授業資料</strong>
                    <div style="margin-top:4px;">{materials_html}</div>
                </div>
                <div>
                    <strong style="font-size:0.85rem; color:var(--muted); text-transform:uppercase;">📝 課題・練習問題</strong>
                    <div style="margin-top:4px;">{questions_html}</div>
                </div>
            </div>
        </div>
        """)
        
    if round_materials[-1]:
        mat_links = []
        for mat in round_materials[-1]:
            href = href_between(output_dir, mat)
            mat_links.append(f'<li><a href="{escape_attr(href)}" target="_blank" style="color:var(--accent);">{escape(mat.name)}</a></li>')
        unassociated_html = f"""
        <div class="timeline-item" style="border-left: 2px dashed var(--line); padding-left: 20px; margin-bottom: 24px; position: relative;">
            <div class="timeline-badge" style="width: 12px; height: 12px; border-radius: 50%; background: var(--muted); position: absolute; left: -7px; top: 6px; border: 2px solid #fff;"></div>
            <h4 style="margin: 0 0 6px 0; color: var(--muted); font-size: 1rem;">授業回未割り当ての資料</h4>
            <div style="margin-top:4px;">
                <ul style='margin:0; padding-left:20px; font-size:0.9rem;'>{''.join(mat_links)}</ul>
            </div>
        </div>
        """
        timeline_items.append(unassociated_html)
        
    return f"""
    <div class="timeline-section" style="margin-top: 30px; border-top: 1px solid var(--line); padding-top: 20px;">
        <h3 style="margin: 0 0 15px 0; font-size: 1.1rem; color: var(--accent);">📅 授業タイムライン</h3>
        <div style="margin-top: 10px;">
            {"".join(timeline_items)}
        </div>
    </div>
    """

def write_summary_pdf(output_path: Path, title: str, summary: SummaryRecord) -> None:
    font_registered = False
    for font_name, font_file in [
        ("MS-Gothic", "C:\\Windows\\Fonts\\msgothic.ttc"),
        ("IPAexGothic", "/usr/share/fonts/opentype/ipaexfont-gothic/ipaexg.ttf"),
        ("HeiseiKakuGo-W5", "HeiseiKakuGo-W5")
    ]:
        if Path(font_file).exists() or font_name == "HeiseiKakuGo-W5":
            try:
                if font_name != "HeiseiKakuGo-W5":
                    pdfmetrics.registerFont(TTFont(font_name, font_file))
                font_registered = True
                f_name = font_name
                break
            except Exception:
                pass
                
    if not font_registered:
        f_name = "Helvetica"
        
    doc = SimpleDocTemplate(str(output_path), pagesize=letter)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'JPTitle', parent=styles['Heading1'], fontName=f_name, fontSize=18, leading=22, spaceAfter=15
    )
    h2_style = ParagraphStyle(
        'JPH2', parent=styles['Heading2'], fontName=f_name, fontSize=14, leading=18, spaceBefore=12, spaceAfter=6
    )
    body_style = ParagraphStyle(
        'JPBody', parent=styles['BodyText'], fontName=f_name, fontSize=10, leading=14, spaceAfter=10
    )
    
    story = [
        Paragraph(f"{title} - AI要約レポート", title_style),
        Spacer(1, 10),
        Paragraph("■ 資料要約", h2_style),
        Paragraph(summary.summary, body_style),
        Spacer(1, 10),
        Paragraph("■ 重要ポイント", h2_style)
    ]
    
    for kp in summary.key_points:
        story.append(Paragraph(f"• {kp}", body_style))
        
    story.append(Spacer(1, 10))
    story.append(Paragraph("■ 重要キーワード", h2_style))
    story.append(Paragraph(", ".join(summary.important_terms), body_style))
    
    story.append(Spacer(1, 10))
    story.append(Paragraph("■ 理解度チェックリスト", h2_style))
    for check in summary.review_checklist:
        story.append(Paragraph(f"[ ] {check}", body_style))
        
    try:
        doc.build(story)
    except Exception as e:
        print(f"Failed to generate summary PDF: {output_path.name}: {e}", file=sys.stderr)
