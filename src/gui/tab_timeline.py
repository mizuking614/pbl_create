import streamlit as st
from collections import defaultdict
import src.core.models as models
from src.gui.common import root_path, refresh_state

def render_tab_timeline():
    st.subheader("📅 授業タイムライン")
    
    courses, records = refresh_state()
    if not courses:
        st.info("登録されている授業がありません。授業管理タブから授業を追加してください。")
        return
        
    selected_course_name = st.selectbox("授業を選択", [c.name for c in courses], key="timeline_course_name")
    course = next(c for c in courses if c.name == selected_course_name)
    
    # 1. Timeline Display
    st.write("### 🕰️ 講義タイムライン")
    
    from src.report.timeline import course_materials, find_material_record, associate_material_to_round, find_summary
    mats = course_materials(root_path(), course, records)
    round_materials = defaultdict(list)
    
    for mat in mats:
        record_obj = find_material_record(records, root_path(), mat)
        c_round = getattr(record_obj, "class_round", None) if record_obj else None
        if c_round is None:
            c_round = associate_material_to_round(mat, course.attendance)
        if c_round is not None:
            round_materials[c_round].append(mat)
        else:
            round_materials[-1].append(mat)
            
    rounds_set = set(att.class_round for att in course.attendance)
    rounds_set.update(round_materials.keys())
    rounds_set.discard(-1)
    sorted_rounds = sorted(list(rounds_set))
    
    summaries = models.load_summaries(root_path())
    questions = models.load_questions(root_path())
    
    if not sorted_rounds and not round_materials[-1]:
        st.info("この授業にはタイムライン情報（出席履歴や資料）がありません。")
    else:
        for r in sorted_rounds:
            att = next((a for a in course.attendance if a.class_round == r), None)
            date_str = att.date if att else "日付未設定"
            status = att.status if att else "出席状況未登録"
            memo = att.memo if att else ""
            
            with st.expander(f"📌 第 {r} 回 — {date_str} 【{status}】"):
                if memo:
                    st.markdown(f"*授業メモ*: {memo}")
                
                st.write("**📁 関連資料**")
                if round_materials[r]:
                    for mat in round_materials[r]:
                        summary_obj = find_summary(summaries, root_path(), mat)
                        importance_str = ""
                        if summary_obj:
                            lvl = getattr(summary_obj, "learning_priority", 3)
                            cat = getattr(summary_obj, "priority_category", "補足資料")
                            stars = "★" * lvl + "☆" * (5 - lvl)
                            importance_str = f" (学習優先度: {stars} | {cat})"
                        
                        st.write(f"- 📄 {mat.name}{importance_str}")
                else:
                    st.write("*(この回の資料はありません)*")
                    
                st.write("**📝 関連する練習問題**")
                related_questions = []
                for q in questions:
                    if q.course == course.name:
                        for mat in round_materials[r]:
                            rel_mat_path = models.normalize_record_path(mat.relative_to(root_path()))
                            if any(models.normalize_record_path(sp) == rel_mat_path for sp in q.source_paths):
                                related_questions.append(q)
                                break
                if related_questions:
                    for q in related_questions:
                        st.write(f"- **{q.title}**: {q.question}")
                else:
                    st.write("*(関連する問題はありません)*")
                    
        if round_materials[-1]:
            with st.expander("❓ 未割り当ての資料"):
                for mat in round_materials[-1]:
                    st.write(f"- {mat.name}")
                    
    st.write("---")
    st.write("### ✏️ 資料の授業回割り当て（手動編集）")
    st.write("授業資料を特定の授業回（回数）に関連付けることができます。")
    
    if not mats:
        st.info("この授業には分類済みの資料がありません。")
        return
        
    with st.form("manual_round_assignment_form"):
        updates = {}
        for mat in mats:
            record_obj = find_material_record(records, root_path(), mat)
            current_round = getattr(record_obj, "class_round", None) if record_obj else None
            
            options = ["未割り当て"] + [f"第 {att.class_round} 回" for att in course.attendance]
            default_idx = 0
            if current_round is not None:
                try:
                    default_idx = [att.class_round for att in course.attendance].index(current_round) + 1
                except ValueError:
                    default_idx = 0
                    
            sel_opt = st.selectbox(
                f"📄 {mat.name}",
                options,
                index=default_idx,
                key=f"assign_{str(mat.resolve())}"
            )
            
            if sel_opt == "未割り当て":
                updates[str(mat.resolve())] = None
            else:
                r_num = int(sel_opt.split()[1])
                updates[str(mat.resolve())] = r_num
                
        save_assignment = st.form_submit_button("割り当てを保存")
        
    if save_assignment:
        for mat in mats:
            record_obj = find_material_record(records, root_path(), mat)
            if record_obj:
                record_obj.class_round = updates[str(mat.resolve())]
                
        models.save_state(root_path(), courses, records)
        try:
            from src.core.indexing import update_search_index
            from src.report.builder import build_site
            update_search_index(root_path())
            build_site(root_path(), root_path() / "_site")
        except Exception:
            pass
        st.success("授業回の割り当てを保存し、インデックスとポータルサイトを更新しました。")
        st.rerun()
