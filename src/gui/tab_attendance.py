import streamlit as st
import datetime
import src.core.models as models
from src.gui.common import root_path, refresh_state, args

def render_tab_attendance():
    st.subheader("📊 出席・講義メモ管理")
    courses, records = refresh_state()
    
    if not courses:
        st.info("授業が登録されていません。授業管理タブから授業を追加してください。")
        return
        
    selected_course_name = st.selectbox("授業を選択", [c.name for c in courses], key="attendance_course_name")
    course = next(c for c in courses if c.name == selected_course_name)
    
    col_left, col_right = st.columns([4, 6])
    
    with col_left:
        st.write("#### ➕ 新規出席を登録")
        with st.form("add_attendance_form", clear_on_submit=True):
            class_round = st.number_input("授業回数 (回目)", min_value=1, max_value=30, value=1)
            att_date = st.date_input("授業実施日", value=datetime.date.today())
            att_status = st.selectbox("出席状況", ["出席", "遅刻", "欠席", "公欠"])
            att_memo = st.text_area("メモ (授業内容・課題など)")
            submitted = st.form_submit_button("登録")
            
        if submitted:
            if any(att.class_round == class_round for att in course.attendance):
                st.error(f"第 {class_round} 回のデータはすでに存在します。右側のリストから編集・削除してください。")
            else:
                new_att = models.AttendanceRecord(
                    date=str(att_date),
                    class_round=int(class_round),
                    status=att_status,
                    memo=att_memo
                )
                course.attendance.append(new_att)
                course.attendance.sort(key=lambda x: x.class_round)
                models.save_courses(root_path(), courses)
                
                # Update portal site and index
                try:
                    from src.core.indexing import update_search_index
                    from src.report.builder import build_site
                    update_search_index(root_path())
                    build_site(root_path(), root_path() / "_site")
                except Exception:
                    pass
                st.success(f"第 {class_round} 回の出席状況を登録しました。")
                st.rerun()
                
    with col_right:
        st.write("#### 📋 登録済みの出席履歴")
        if not course.attendance:
            st.info("登録済みの出席データはありません。")
        else:
            for att in list(course.attendance):
                with st.expander(f"📌 第 {att.class_round} 回 ({att.date}) - 【{att.status}】"):
                    with st.form(f"edit_attendance_form_{att.class_round}"):
                        try:
                            default_date = datetime.date.fromisoformat(att.date)
                        except Exception:
                            default_date = datetime.date.today()
                            
                        edit_date = st.date_input("日付", value=default_date, key=f"edit_date_{att.class_round}")
                        edit_status = st.selectbox(
                            "出席状況",
                            ["出席", "遅刻", "欠席", "公欠"],
                            index=["出席", "遅刻", "欠席", "公欠"].index(att.status) if att.status in ["出席", "遅刻", "欠席", "公欠"] else 0,
                            key=f"edit_status_{att.class_round}"
                        )
                        edit_memo = st.text_area("メモ", value=att.memo, key=f"edit_memo_{att.class_round}")
                        
                        col_btn1, col_btn2 = st.columns(2)
                        with col_btn1:
                            save_submitted = st.form_submit_button("更新")
                        with col_btn2:
                            delete_submitted = st.form_submit_button("削除")
                            
                    if save_submitted:
                        att.date = str(edit_date)
                        att.status = edit_status
                        att.memo = edit_memo
                        models.save_courses(root_path(), courses)
                        try:
                            from src.report.builder import build_site
                            build_site(root_path(), root_path() / "_site")
                        except Exception:
                            pass
                        st.success(f"第 {att.class_round} 回を更新しました。")
                        st.rerun()
                        
                    if delete_submitted:
                        course.attendance.remove(att)
                        models.save_courses(root_path(), courses)
                        try:
                            from src.report.builder import build_site
                            build_site(root_path(), root_path() / "_site")
                        except Exception:
                            pass
                        st.success(f"第 {att.class_round} 回を削除しました。")
                        st.rerun()
