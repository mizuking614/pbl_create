import streamlit as st
import src.core.models as models
from src.gui.common import root_path, args

def render_tab_links():
    st.subheader("共通参考URLリンク集の管理")
    
    global_links = models.load_global_links(root_path())
    
    st.write("### 🔗 共通の参考リンク一覧")
    
    if global_links:
        for idx, lk in list(enumerate(global_links)):
            col_link, col_del = st.columns([8, 2])
            with col_link:
                st.markdown(f"[{lk.title}]({lk.url}) — *{lk.memo}*" if lk.memo else f"[{lk.title}]({lk.url})")
            with col_del:
                if st.button("削除", key=f"del_global_link_{idx}"):
                    global_links.pop(idx)
                    models.save_global_links(root_path(), global_links)
                    try:
                        from src.report.builder import build_site
                        build_site(root_path(), root_path() / "_site")
                    except Exception:
                        pass
                    st.success("リンクを削除しました。")
                    st.rerun()
    else:
        st.info("登録されているリンクはありません。以下のフォームから追加してください。")
        
    st.write("---")
    st.write("#### ➕ 新規リンクを追加")
    with st.form("add_global_link_form", clear_on_submit=True):
        lk_title = st.text_input("サイト名 / タイトル")
        lk_url = st.text_input("URL", placeholder="https://example.com")
        lk_memo = st.text_input("メモ (任意)", placeholder="参考になる公式サイトなど")
        submitted_link = st.form_submit_button("リンクを追加")
        
    if submitted_link:
        if not lk_title or not lk_url:
            st.error("サイト名とURLを入力してください。")
        else:
            new_link = models.LinkRecord(title=lk_title, url=lk_url, memo=lk_memo)
            global_links.append(new_link)
            models.save_global_links(root_path(), global_links)
            try:
                from src.report.builder import build_site
                build_site(root_path(), root_path() / "_site")
            except Exception:
                pass
            st.success("リンクを追加しました。")
            st.rerun()
