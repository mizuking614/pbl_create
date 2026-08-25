import streamlit as st
import os
from src.gui.common import root_path

# Import each modular tab renderer
from src.gui.tab_courses import render_tab_courses
from src.gui.tab_sort import render_tab_sort
from src.gui.tab_timeline import render_tab_timeline
from src.gui.tab_chat import render_tab_chat
from src.gui.tab_search import render_tab_search
from src.gui.tab_ai import render_tab_ai
from src.gui.tab_site import render_tab_site
from src.gui.tab_attendance import render_tab_attendance
from src.gui.tab_links import render_tab_links

st.set_page_config(page_title="授業資料コンパイラ", layout="wide")
st.title("📚 授業資料コンパイラ")

with st.sidebar:
    st.header("⚙️ 設定")
    root_input = st.text_input("ルートフォルダ", value=str(root_path()), key="root_path_input")
    if root_input:
        os.environ["PBL_ROOT"] = root_input
        
    st.write("---")
    st.subheader("APIキー設定")
    gemini_key = st.text_input("Gemini API Key", type="password", key="gemini_key_input")
    openai_key = st.text_input("OpenAI API Key", type="password", key="openai_key_input")
    
    if gemini_key:
        os.environ["GEMINI_API_KEY"] = gemini_key
    if openai_key:
        os.environ["OPENAI_API_KEY"] = openai_key

# Set up Streamlit layout tabs
(
    tab_courses, tab_sort, tab_timeline, tab_chat, tab_search,
    tab_ai, tab_site, tab_attendance, tab_links
) = st.tabs([
    "授業管理", "資料整理", "タイムライン", "授業AIチャット", "全文検索",
    "AI分析", "Webページ", "出席管理", "リンク管理"
])

with tab_courses:
    render_tab_courses()
    
with tab_sort:
    render_tab_sort()
    
with tab_timeline:
    render_tab_timeline()
    
with tab_chat:
    render_tab_chat()
    
with tab_search:
    render_tab_search()
    
with tab_ai:
    render_tab_ai()
    
with tab_site:
    render_tab_site()
    
with tab_attendance:
    render_tab_attendance()
    
with tab_links:
    render_tab_links()
