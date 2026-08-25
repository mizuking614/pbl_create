import streamlit as st
from pathlib import Path
import src.core.models as models
import src.core.operations as ops
from src.gui.common import root_path, refresh_state

def render_tab_ai():
    st.subheader("🤖 AI要約・重要語句抽出")
    st.write("授業資料の内容を解析して要約、重要語句、復習チェックリストを作成し、PDF要約レポートも自動生成します。")
    
    courses, records = refresh_state()
    
    # 1. AI Analysis
    all_materials = []
    for record in records:
        p = root_path() / record.path
        if p.exists() and p.is_file():
            all_materials.append(p)
            
    if not all_materials:
        st.info("分析可能な資料がありません。先に資料をソート・登録してください。")
    else:
        with st.form("ai_analysis_form"):
            selected_file_name = st.selectbox("分析する資料を選択", [m.name for m in all_materials])
            provider = st.selectbox("使用AIモデル", ["Gemini", "OpenAI"], key="ai_analysis_provider")
            mode = st.selectbox("分析モード", ["AI", "local"], key="ai_analysis_mode")
            analyze_submitted = st.form_submit_button("資料分析を実行")
            
        if analyze_submitted:
            target_file = next(m for m in all_materials if m.name == selected_file_name)
            with st.spinner("資料分析・要約生成中..."):
                code = ops.analyze_material_op(root_path(), target_file, provider=provider.lower(), mode=mode)
                if code == 0:
                    st.success(f"「{selected_file_name}」の分析が完了しました！")
                    st.rerun()
                else:
                    st.error("分析中にエラーが発生しました。")

    st.write("---")
    st.subheader("📝 練習問題自動生成")
    st.write("選択した授業に属するすべての資料をコンテキストとして、AIが記述式の練習問題を自動で作成します。")
    
    if not courses:
        st.info("授業が登録されていません。")
        return
        
    with st.form("generate_practice_form"):
        selected_course = st.selectbox("対象の授業", [c.name for c in courses])
        provider_q = st.selectbox("使用AIモデル", ["Gemini", "OpenAI"], key="generate_practice_provider")
        practice_submitted = st.form_submit_button("練習問題を作成")
        
    if practice_submitted:
        with st.spinner("問題生成中..."):
            code = ops.generate_practice_op(root_path(), selected_course, provider=provider_q.lower())
            if code == 0:
                st.success("練習問題を追加しました！「タイムライン」またはWebポータルで確認できます。")
                st.rerun()
            else:
                st.error("問題生成に失敗しました。この授業に資料が登録されているか確認してください。")
