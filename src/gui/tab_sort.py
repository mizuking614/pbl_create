import streamlit as st
from pathlib import Path
import src.core.models as models
import src.core.operations as ops
from src.gui.common import root_path, refresh_state

def render_tab_sort():
    st.subheader("未分類の資料を自動整理")
    st.write("`unsorted/` フォルダ内の資料について、授業キーワードとの類似度を測定して自動的に各授業フォルダへコピー・移動します。")
    
    with st.form("auto_sort_form"):
        copy_files = st.checkbox("ファイルを授業フォルダにコピーする (オフの場合は移動)", value=True)
        threshold = st.slider("マッチングしきい値 (キーワード合致割合)", 0.0, 1.0, 0.3)
        sort_submitted = st.form_submit_button("自動分類を実行")
        
    if sort_submitted:
        with st.spinner("分類処理中..."):
            code = ops.sort_materials_op(
                root_path(),
                copy=copy_files,
                threshold=threshold,
                ocr_language="jpn+eng",
            )
            if code == 0:
                st.success("分類を完了しました！")
                st.rerun()
            else:
                st.error("分類できませんでした。")

    courses, records = refresh_state()
    summaries = models.load_summaries(root_path())
    
    st.subheader("分類済み資料")
    for course in courses:
        # Get sorted list
        from src.report.timeline import course_materials
        materials = course_materials(root_path(), course, records)
        with st.expander(f"📚 {course.name} ({len(materials)}件)"):
            for material in materials:
                st.checkbox(material.name, key=f"select_{str(material.resolve())}")
                rel_path = models.normalize_record_path(material.relative_to(root_path()))
                summary_obj = next((s for s in summaries if models.normalize_record_path(s.path) == rel_path), None)
                if summary_obj:
                    priority = getattr(summary_obj, "learning_priority", 3)
                    category = getattr(summary_obj, "priority_category", "補足資料")
                    reason = getattr(summary_obj, "priority_reason", "")
                    stars = "★" * priority + "☆" * (5 - priority)
                    st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;**学習優先度**: {stars} &nbsp;|&nbsp; **カテゴリ**: `{category}`")
                    if reason:
                        st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;*理由*: {reason}")
    
    from src.report.timeline import unknown_materials
    unknown_mats = unknown_materials(root_path(), records)
    with st.expander(f"📂 その他 / 未分類 ({len(unknown_mats)}件)"):
        for material in unknown_mats:
            st.checkbox(material.name, key=f"select_{str(material.resolve())}")

    st.subheader("資料の移動・削除 (一括選択)")
    
    selected_paths = []
    for key, val in list(st.session_state.items()):
        if key.startswith("select_") and val:
            path_str = key[len("select_"):]
            selected_paths.append(Path(path_str))
            
    if not selected_paths:
        st.info("上の資料一覧からチェックを入れて選択してください。")
        return

    st.write(f"選択中: {len(selected_paths)} 件の資料")
    
    with st.form("bulk_action_form"):
        target_course = st.selectbox("移動先授業", ["未分類に戻す"] + [c.name for c in courses])
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            move_btn = st.form_submit_button("選択した資料を移動")
        with col_btn2:
            delete_btn = st.form_submit_button("選択した資料を物理削除")
            
    if move_btn:
        c_val = None if target_course == "未分類に戻す" else target_course
        for path in selected_paths:
            ops.reassign_material_op(root_path(), path, c_val)
            # clear checkbox state
            st.session_state[f"select_{str(path.resolve())}"] = False
        st.success("資料を再配置しました。")
        st.rerun()
        
    if delete_btn:
        for path in selected_paths:
            ops.delete_material_op(root_path(), path)
            st.session_state[f"select_{str(path.resolve())}"] = False
        st.success("資料を削除しました。")
        st.rerun()
