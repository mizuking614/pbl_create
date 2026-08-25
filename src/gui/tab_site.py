import streamlit as st
import src.report.builder as builder
from src.gui.common import root_path

def render_tab_site():
    st.subheader("🌐 Webポータルサイト生成")
    st.write("登録されている授業、資料、出席記録、参考リンクから、ブラウザで閲覧可能なスタディポータル（HTML）を生成します。")
    
    col1, col2 = st.columns(2)
    with col1:
        build_submitted = st.button("Webページをビルドする")
    with col2:
        open_site = st.write(f"保存先: `_site/index.html` (フォルダ: `{root_path() / '_site'}`)")
        
    if build_submitted:
        with st.spinner("ビルド中..."):
            try:
                # Triggers differential indexing and builds HTML portal
                from src.core.indexing import update_search_index
                update_search_index(root_path())
                builder.build_site(root_path(), root_path() / "_site")
                st.success("Webサイトをビルドしました！ `_site/index.html` をダブルクリックして開いてください。")
            except Exception as e:
                st.error(f"ビルド中にエラーが発生しました: {e}")
