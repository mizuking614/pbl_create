import html
import os
import shutil
import sys
import json
from pathlib import Path
from PIL import Image
import pypdfium2

from src.core.models import (
    Course, MaterialRecord, SummaryRecord, QuestionRecord, LinkRecord,
    load_state, load_summaries, load_questions, load_global_links,
    normalize_record_path, search_index_path, relative_to_root, href_between
)
from src.report.templates import HTML_TEMPLATE
from src.report.timeline import (
    render_timeline_html, write_summary_pdf, find_summary,
    course_materials, unknown_materials
)

def html_id(name: str) -> str:
    return name.replace("/", "-").replace(" ", "-")

def escape(s: str) -> str:
    return html.escape(str(s))

def escape_attr(s: str) -> str:
    return html.escape(str(s), quote=True)

def ensure_pdf_thumbnail(root: Path, material: Path) -> Path | None:
    thumb_dir = root / ".class_materials" / "thumbnails"
    thumb_dir.mkdir(parents=True, exist_ok=True)
    thumb_name = material.name + ".thumb.png"
    thumb_path = thumb_dir / thumb_name
    
    if thumb_path.exists() and thumb_path.stat().st_mtime > material.stat().st_mtime:
        return thumb_path
        
    try:
        pdf = pypdfium2.PdfDocument(str(material))
        if len(pdf) > 0:
            page = pdf[0]
            bitmap = page.render(scale=0.5)
            pil_img = bitmap.to_pil()
            pil_img.save(thumb_path)
            return thumb_path
    except Exception as e:
        print(f"Thumbnail error: {material.name}: {e}", file=sys.stderr)
    return None

def render_chips(terms: list[str]) -> str:
    return f'<div class="chips">{"".join(f"<span class=chip>{escape(t)}</span>" for t in terms)}</div>' if terms else ""

def render_text_list(title: str, items: list[str]) -> str:
    return f"<h4>{escape(title)}</h4><ul>{''.join(f'<li>{escape(i)}</li>' for i in items)}</ul>" if items else ""

def render_course_insights(course: Course, summaries: list[SummaryRecord], questions: list[QuestionRecord]) -> str:
    num_questions = sum(1 for q in questions if q.course == course.name)
    return f"""<div class="insight-section"><h3>📈 学習インサイト</h3><div class="insight-grid"><div class="insight-card"><strong>登録練習問題数:</strong> {num_questions} 問</div><div class="insight-card"><strong>参考リンク数:</strong> {len(course.links)} 件</div></div></div>"""

def render_preview(root: Path, output_dir: Path, material: Path, suffix: str) -> str:
    if suffix in {"png", "jpg", "jpeg", "bmp", "tif", "tiff"}:
        src = href_between(output_dir, material)
        return f'<div class="preview"><img src="{escape_attr(src)}" alt=""></div>'
    
    if suffix == "pdf":
        thumb_cache = ensure_pdf_thumbnail(root, material)
        if thumb_cache and thumb_cache.exists():
            thumb_dest_dir = output_dir / "_thumbnails"
            thumb_dest_dir.mkdir(parents=True, exist_ok=True)
            thumb_dest = thumb_dest_dir / thumb_cache.name
            if not thumb_dest.exists() or thumb_dest.stat().st_mtime < thumb_cache.stat().st_mtime:
                shutil.copy2(thumb_cache, thumb_dest)
            src = href_between(output_dir, thumb_dest)
            return f'<div class="preview"><img src="{escape_attr(src)}" alt=""></div>'
            
    return f'<div class="preview">{escape(suffix.upper())}</div>'

def render_material_card(
    root: Path, output_dir: Path, material: Path, summaries: list[SummaryRecord]
) -> str:
    suffix = material.suffix.lower().lstrip(".") or "file"
    href = href_between(output_dir, material)
    preview = render_preview(root, output_dir, material, suffix)
    search_text = " ".join([material.name, suffix, str(material.parent.name)]).lower()
    rel_path = normalize_record_path(relative_to_root(root, material))

    summary = find_summary(summaries, root, material)
    summary_html = ""
    if summary:
        priority = getattr(summary, "learning_priority", 3)
        category = getattr(summary, "priority_category", "補足資料")
        reason = getattr(summary, "priority_reason", "")
        stars = "★" * priority + "☆" * (5 - priority)
        
        priority_html = f"""
        <div class="priority-box" style="margin-bottom: 12px; padding: 10px; background: #fffbeb; border-left: 4px solid #f59e0b; border-radius: 4px; font-size: 0.9rem;">
            <div style="font-weight: bold; color: #b45309; margin-bottom: 4px;">
                学習優先度: <span style="font-size: 1.1rem; letter-spacing: 2px;">{stars}</span> 
                <span style="display: inline-block; margin-left: 8px; padding: 2px 6px; background: #fef3c7; border-radius: 3px; font-size: 0.8rem; font-weight: bold; color: #d97706; border: 1px solid #fcd34d;">{escape(category)}</span>
            </div>
            {f'<div style="color: #4b5563; line-height: 1.4;">理由: {escape(reason)}</div>' if reason else ''}
        </div>
        """

        summary_text = f"""<details class="summary-details">
  <summary><span class="btn">要約を表示</span></summary>
  <div class="summary-content">
    {priority_html}
    <h4>要約</h4>
    <p>{escape(summary.summary)}</p>
    {render_text_list("要点", summary.key_points)}
    {render_text_list("重要語句", summary.important_terms)}
  </div>
</details>"""
        pdf_path = material.with_suffix(material.suffix + ".summary.pdf")
        pdf_link = ""
        if pdf_path.exists():
            pdf_href = href_between(output_dir, pdf_path)
            pdf_link = f'<a class="btn" href="{escape_attr(pdf_href)}" target="_blank">要約PDFを開く</a>'
        summary_html = f"{pdf_link}{summary_text}"

    return f"""<div class="material" data-search="{escape_attr(search_text)}" data-path="{escape_attr(rel_path)}">
  <div style="display: flex; gap: 10px; width: 100%; align-items: start;">
    {preview}
    <div style="flex: 1; min-width: 0;">
      <div class="name">{escape(material.name)}</div>
      <div class="terms">{escape(relative_to_root(root, material))}</div>
    </div>
  </div>
  <div style="display: flex; flex-wrap: wrap; gap: 8px; width: 100%; margin-top: auto; padding-top: 8px;">
    <a class="btn" href="{escape_attr(href)}" target="_blank">資料を開く</a>
    {summary_html}
  </div>
</div>"""

def render_course_section(
    root: Path,
    output_dir: Path,
    course: Course,
    records: list[MaterialRecord],
    summaries: list[SummaryRecord],
    questions: list[QuestionRecord],
) -> str:
    materials = course_materials(root, course, records)
    cards = "\n".join(render_material_card(root, output_dir, item, summaries) for item in materials)
    if not cards:
        cards = '<div class="empty">資料はまだありません。</div>'
    terms = course.keywords + course.learned_terms
    chips = render_chips(terms[:16])
    insights = render_course_insights(course, summaries, questions)
    
    attendance_html = ""
    if hasattr(course, "attendance") and course.attendance:
        total = len(course.attendance)
        presents = sum(1 for att in course.attendance if att.status == "出席")
        lates = sum(1 for att in course.attendance if att.status == "遅刻")
        absents = sum(1 for att in course.attendance if att.status == "欠席")
        excuseds = sum(1 for att in course.attendance if att.status == "公欠")
        rate = (presents + lates) / total * 100 if total > 0 else 0.0
        
        rows = []
        for att in course.attendance:
            status_class = "present"
            if att.status == "欠席":
                status_class = "absent"
            elif att.status == "遅刻":
                status_class = "late"
            elif att.status == "公欠":
                status_class = "excused"
            
            rows.append(f"""
            <tr>
              <td style="padding: 8px 12px; border-bottom: 1px solid var(--line);">第 {att.class_round} 回</td>
              <td style="padding: 8px 12px; border-bottom: 1px solid var(--line);">{escape(att.date)}</td>
              <td style="padding: 8px 12px; border-bottom: 1px solid var(--line);"><span class="status-badge {status_class}">{escape(att.status)}</span></td>
              <td style="padding: 8px 12px; border-bottom: 1px solid var(--line);">{escape(att.memo) if att.memo else '<span style="color:var(--muted)">-</span>'}</td>
            </tr>
            """)
        rows_html = "\n".join(rows)
        
        attendance_html = f"""
        <div class="attendance-section" style="margin-top: 15px; margin-bottom: 20px; background: var(--soft); border: 1px solid var(--line); border-radius: 6px; padding: 15px;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; flex-wrap: wrap; gap: 10px;">
            <h3 style="margin: 0; font-size: 1.1rem; color: var(--accent);">📊 出席状況</h3>
            <div style="display: flex; gap: 12px; font-size: 0.9rem; color: var(--muted); flex-wrap: wrap;">
              <span>総回数: <strong>{total}</strong></span>
              <span>出席: <strong style="color:#0f766e">{presents}</strong></span>
              <span>遅刻: <strong style="color:#b25e00">{lates}</strong></span>
              <span>欠席: <strong style="color:#b91c1c">{absents}</strong></span>
              <span>公欠: <strong style="color:#1d4ed8">{excuseds}</strong></span>
              <span style="margin-left: 10px;">出席率: <strong style="color:var(--ink)">{rate:.1f}%</strong></span>
            </div>
          </div>
          <div style="width: 100%; height: 6px; background: #e2e8f0; border-radius: 3px; overflow: hidden; margin-bottom: 15px;">
            <div style="width: {rate}%; height: 100%; background: var(--accent); transition: width 0.3s ease;"></div>
          </div>
          <table class="attendance-table" style="width: 100%; border-collapse: collapse; font-size: 0.9rem; text-align: left; background: #fff; border-radius: 4px; overflow: hidden;">
            <thead>
              <tr style="border-bottom: 2px solid var(--line); background: var(--soft); color: var(--muted);">
                <th style="padding: 8px 12px; width: 80px;">回数</th>
                <th style="padding: 8px 12px; width: 120px;">日付</th>
                <th style="padding: 8px 12px; width: 80px;">状況</th>
                <th style="padding: 8px 12px;">授業メモ・課題など</th>
              </tr>
            </thead>
            <tbody>
              {rows_html}
            </tbody>
          </table>
        </div>
        """
        
    timeline_html = render_timeline_html(root, output_dir, course, records, summaries, questions)
    search_text = " ".join([course.name, course.teacher, *terms]).lower()
    return f"""<section id="{html_id(course.name)}" data-search="{escape_attr(search_text)}">
  <div class="course-head">
    <div>
      <h2>{escape(course.name)}</h2>
      <div class="teacher">{escape(course.teacher) if course.teacher else "教員名未登録"}</div>
      {chips}
    </div>
    <div class="meta">{len(materials)} 資料</div>
  </div>
  {attendance_html}
  {insights}
  <h3 style="margin-top: 25px; font-size: 1.15rem; color: var(--ink);">📚 授業資料</h3>
  <div class="grid">{cards}</div>
  {timeline_html}
</section>"""

def render_unknown_section(
    root: Path, output_dir: Path, records: list[MaterialRecord], summaries: list[SummaryRecord]
) -> str:
    materials = unknown_materials(root, records)
    if not materials:
        return ""
    cards = "\n".join(render_material_card(root, output_dir, item, summaries) for item in materials)
    return f"""<section id="unknown" class="unknown" data-search="その他">
  <div class="course-head">
    <div>
      <h2>その他</h2>
      <div class="teacher">確認が必要な資料</div>
      {render_chips(["要確認"])}
    </div>
    <div class="meta">{len(materials)} 資料</div>
  </div>
  <div class="grid">{cards}</div>
</section>"""

def build_site(root: Path, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    courses, records = load_state(root)
    summaries = load_summaries(root)
    questions = load_questions(root)
    global_links = load_global_links(root)
    
    nav_links = "".join(f'<a href="#{html_id(c.name)}">{escape(c.name)}</a>' for c in courses)
    
    content = ""
    for c in courses:
        content += render_course_section(root, output_dir, c, records, summaries, questions)
    content += render_unknown_section(root, output_dir, records, summaries)
    
    global_links_html = ""
    if global_links:
        cards = []
        for lk in global_links:
            memo_str = f"<div>{escape(lk.memo)}</div>" if lk.memo else ""
            cards.append(f"""
            <div class="global-link-card">
              <a href="{escape_attr(lk.url)}" target="_blank">{escape(lk.title)}</a>
              {memo_str}
            </div>
            """)
        global_links_html = f'<div class="global-links-grid">{"".join(cards)}</div>'
    else:
        global_links_html = '<div class="empty">登録されている参考リンクはありません。</div>'
        
    html_out = HTML_TEMPLATE.format(
        nav_links=nav_links,
        content=content,
        global_links_html=global_links_html
    )
    
    (output_dir / "index.html").write_text(html_out, encoding="utf-8")
    
    idx_src = search_index_path(root)
    idx_dest = output_dir / "search_index.json"
    if idx_src.exists():
        try:
            data = json.loads(idx_src.read_text(encoding="utf-8"))
            for item in data.get("index", []):
                item.pop("mtime", None)
                item.pop("size", None)
            idx_dest.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        except Exception as e:
            print(f"Failed to export cleaned search index: {e}", file=sys.stderr)
