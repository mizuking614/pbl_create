import streamlit as st
import json
import src.core.models as models
import src.ai.rag as rag
from src.gui.common import root_path, refresh_state

def render_tab_chat():
    st.subheader("🤖 授業AI学習アシスタント (RAG)")
    st.write("講義資料の内容のみに基づいて質問に答えるAI家庭教師です。")
    
    courses, records = refresh_state()
    if not courses:
        st.info("登録されている授業がありません。授業管理タブから授業を追加してください。")
        return
        
    index_path = models.search_index_path(root_path())
    if not index_path.exists():
        st.warning("検索インデックスが見つかりません。先に「資料整理」または「AI分析」を実行してインデックスを生成してください。")
        return

    # Configuration panel
    col_course, col_provider = st.columns(2)
    with col_course:
        course_options = ["すべての授業"] + [c.name for c in courses]
        selected_course = st.selectbox("対象の授業", course_options)
    with col_provider:
        provider = st.selectbox("使用AIモデル", ["Gemini", "OpenAI"])
        
    # Maintain chat history per course
    history_key = f"chat_history_{selected_course}"
    if history_key not in st.session_state:
        st.session_state[history_key] = []
        
    # Render chat history
    for msg in st.session_state[history_key]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("sources"):
                st.caption(f"📁 参照資料: {', '.join(msg['sources'])}")

    # Handle user query
    user_query = st.chat_input("資料について質問してください（例：ラグランジェ方程式の解き方は？）")
    
    if user_query:
        # Display user input
        with st.chat_message("user"):
            st.markdown(user_query)
        st.session_state[history_key].append({"role": "user", "content": user_query})
        
        # Query index and invoke LLM
        with st.spinner("資料を調べて回答を生成中..."):
            try:
                # Load index data
                index_data = json.loads(index_path.read_text(encoding="utf-8"))
                course_filter = None if selected_course == "すべての授業" else selected_course
                
                # Perform RAG query
                answer, sources = rag.query_rag(
                    user_query,
                    course_filter,
                    index_data,
                    provider=provider.lower()
                )
                
                # Display response
                with st.chat_message("assistant"):
                    st.markdown(answer)
                    source_names = []
                    if sources:
                        source_names = list(set(s.get("material_name") for s in sources if s.get("material_name")))
                        st.caption(f"📁 参照資料: {', '.join(source_names)}")
                
                st.session_state[history_key].append({
                    "role": "assistant",
                    "content": answer,
                    "sources": source_names
                })
                st.rerun()
            except Exception as e:
                st.error(f"回答の生成中にエラーが発生しました: {e}")
