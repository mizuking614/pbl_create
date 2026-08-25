import streamlit as st
import src.core.models as models
from src.gui.common import root_path, refresh_state

def render_tab_courses():
    st.subheader("授業を登録")
    courses, records = refresh_state()
    
    with st.form("add_course", clear_on_submit=True):
        name = st.text_input("授業名")
        teacher = st.text_input("教員名")
        keywords = st.text_input("キーワード", placeholder="認知,記憶,学習")
        submitted = st.form_submit_button("授業を追加")
        
    if submitted:
        if not name:
            st.error("授業名を入力してください。")
        elif any(c.name == name for c in courses):
            st.error(f"授業「{name}」はすでに存在します。")
        else:
            kw_list = [k.strip() for k in keywords.split(",") if k.strip()]
            new_course = models.Course(name=name, teacher=teacher, keywords=kw_list)
            courses.append(new_course)
            models.save_courses(root_path(), courses)
            st.success(f"授業「{name}」を追加しました。")
            st.rerun()
            
    st.write("---")
    st.subheader("登録済みの授業一覧")
    
    if not courses:
        st.info("登録されている授業はありません。")
        return
        
    for c in list(courses):
        with st.expander(f"📚 {c.name} (担当: {c.teacher or '未登録'})"):
            with st.form(f"edit_course_{c.name}"):
                edit_teacher = st.text_input("教員名", value=c.teacher)
                edit_keywords = st.text_input("キーワード (カンマ区切り)", value=",".join(c.keywords))
                
                col1, col2 = st.columns(2)
                with col1:
                    save_submitted = st.form_submit_button("更新")
                with col2:
                    delete_submitted = st.form_submit_button("授業を削除")
                    
            if save_submitted:
                c.teacher = edit_teacher
                c.keywords = [k.strip() for k in edit_keywords.split(",") if k.strip()]
                models.save_courses(root_path(), courses)
                st.success("授業設定を更新しました。")
                st.rerun()
                
            if delete_submitted:
                courses.remove(c)
                # Cleanup associated material records
                for r in list(records):
                    if r.course == c.name:
                        r.course = None
                models.save_state(root_path(), courses, records)
                st.success("授業を削除しました。")
                st.rerun()
