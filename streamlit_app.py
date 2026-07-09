from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import datetime

import streamlit as st

import class_materials_compiler as cmc
import importlib
importlib.reload(cmc)


st.set_page_config(page_title="授業資料コンパイラ", layout="wide")


def args(**kwargs: object) -> argparse.Namespace:
    return argparse.Namespace(**kwargs)


def root_path() -> Path:
    return Path(st.session_state.get("root", Path.cwd())).expanduser().resolve()


def refresh_state() -> tuple[list[cmc.Course], list[cmc.MaterialRecord]]:
    courses, records = cmc.load_state(root_path())
    cleaned = False
    for course in courses:
        old_terms = list(course.learned_terms)
        cmc.recalculate_course_learned_terms(course, records)
        if course.learned_terms != old_terms:
            cleaned = True
    if cleaned:
        cmc.save_state(root_path(), courses, records)
    return courses, records


st.title("授業資料コンパイラ")

with st.sidebar:
    st.text_input("保存ルート", value=str(Path.cwd()), key="root")
    st.caption("授業フォルダ、設定、HTML出力を保存する場所です。")
    
    st.write("---")
    st.subheader("APIキー設定")
    gemini_key = st.text_input("Gemini API Key", type="password", key="gemini_key_input")
    openai_key = st.text_input("OpenAI API Key", type="password", key="openai_key_input")
    
    import os
    if gemini_key:
        os.environ["GEMINI_API_KEY"] = gemini_key
    if openai_key:
        os.environ["OPENAI_API_KEY"] = openai_key

tab_courses, tab_sort, tab_ai, tab_site, tab_attendance, tab_links = st.tabs(
    ["授業管理", "資料整理", "AI分析", "Webページ", "出席管理", "リンク管理"]
)

with tab_courses:
    st.subheader("授業を登録")
    with st.form("add_course", clear_on_submit=True):
        name = st.text_input("授業名")
        teacher = st.text_input("教員名")
        keywords = st.text_input("キーワード", placeholder="認知,記憶,学習")
        submitted = st.form_submit_button("登録")
    if submitted and name:
        code = cmc.add_course(
            args(root=str(root_path()), name=name, teacher=teacher, keywords=keywords)
        )
        st.success("登録しました。" if code == 0 else "登録できませんでした。")

    courses, _records = refresh_state()
    st.subheader("登録済み授業")
    if courses:
        for course in courses:
            with st.expander(f"📚 **{course.name}** / {course.teacher or '教員名未登録'}"):
                with st.form(f"edit_course_{course.name}"):
                    new_teacher = st.text_input("教員名", value=course.teacher, key=f"teacher_{course.name}")
                    new_keywords = st.text_input("キーワード (カンマ区切り)", value=", ".join(course.keywords), key=f"keywords_{course.name}")
                    submitted_edit = st.form_submit_button("更新")
                if submitted_edit:
                    code = cmc.update_course(
                        args(
                            root=str(root_path()),
                            name=course.name,
                            teacher=new_teacher,
                            keywords=new_keywords,
                        )
                    )
                    if code == 0:
                        st.success(f"{course.name} を更新しました。")
                        st.rerun()
                    else:
                        st.error(f"{course.name} を更新できませんでした。")
                st.caption("自動学習済み語句: " + ", ".join(course.learned_terms[:8]) if course.learned_terms else "自動学習済み語句: なし")

    else:
        st.info("授業はまだ登録されていません。")


with tab_sort:
    st.subheader("資料を分類")
    
    input_mode = st.radio("入力方法を選択", ["ファイルアップロード (参照・ドロップ)", "ローカルパス指定"], horizontal=True)
    
    if input_mode == "ファイルアップロード (参照・ドロップ)":
        uploaded_files = st.file_uploader("分類する資料ファイルをドラッグ＆ドロップまたは選択してください", accept_multiple_files=True)
        copy_files = st.checkbox("コピーする (元のアップロードデータを一時フォルダに残す場合)")
        threshold = st.slider("分類しきい値", 0.0, 0.5, 0.08, 0.01, key="threshold_upload")
        if st.button("アップロードして分類を実行") and uploaded_files:
            temp_dir = root_path() / "_upload_temp"
            temp_dir.mkdir(parents=True, exist_ok=True)
            
            temp_filepaths = []
            for uploaded_file in uploaded_files:
                target_path = temp_dir / uploaded_file.name
                target_path.write_bytes(uploaded_file.read())
                temp_filepaths.append(str(target_path))
                
            code = cmc.sort_materials(
                args(
                    root=str(root_path()),
                    inputs=temp_filepaths,
                    recursive=False,
                    copy=copy_files,
                    threshold=threshold,
                    ocr_language="jpn+eng",
                )
            )
            
            shutil.rmtree(temp_dir, ignore_errors=True)
            
            if code == 0:
                st.success("アップロードされたファイルを分類しました！")
                st.rerun()
            else:
                st.error("分類中にエラーが発生しました。")
    else:
        input_path = st.text_input("資料ファイルまたはフォルダの絶対パス")
        recursive = st.checkbox("フォルダを再帰的に処理", value=True)
        copy_files = st.checkbox("移動せずコピーする")
        threshold = st.slider("分類しきい値", 0.0, 0.5, 0.08, 0.01, key="threshold_path")
        if st.button("分類を実行") and input_path:
            code = cmc.sort_materials(
                args(
                    root=str(root_path()),
                    inputs=[input_path],
                    recursive=recursive,
                    copy=copy_files,
                    threshold=threshold,
                    ocr_language="jpn+eng",
                )
            )
            if code == 0:
                st.success("分類しました！")
                st.rerun()
            else:
                st.error("分類できませんでした。")

    courses, records = refresh_state()
    st.subheader("分類済み資料")
    for course in courses:
        materials = cmc.course_materials(root_path(), course, records)
        with st.expander(f"📚 {course.name} ({len(materials)}件)"):
            for material in materials:
                st.checkbox(material.name, key=f"select_{str(material.resolve())}")
    
    unknown_mats = cmc.unknown_materials(root_path(), records)
    with st.expander(f"📂 その他 / 未分類 ({len(unknown_mats)}件)"):
        for material in unknown_mats:
            st.checkbox(material.name, key=f"select_{str(material.resolve())}")

    st.subheader("資料の移動・削除 (一括選択)")
    
    selected_paths = []
    for key, val in list(st.session_state.items()):
        if key.startswith("select_") and val:
            path_str = key[len("select_"):]
            selected_paths.append(Path(path_str))
            
    if selected_paths:
        st.write(f"👉 **選択中: {len(selected_paths)} 件の資料**")
        for p in selected_paths:
            st.caption(f"- {p.name}")
            
        action = st.radio("一括アクションを選択", ["選択した資料を他の授業へ移動", "選択した資料を削除"], horizontal=True, key="batch_action_choice")
        if action == "選択した資料を他の授業へ移動":
            dest_options = [c.name for c in courses] + ["その他"]
            dest_course = st.selectbox("移動先の授業", dest_options, key="batch_select_dest_course")
            if st.button("一括移動を実行", key="btn_batch_execute_reassign"):
                success_count = 0
                for path in selected_paths:
                    code = cmc.reassign_material(
                        args(
                            root=str(root_path()),
                            material=str(path),
                            to=dest_course,
                            ocr_language="jpn+eng",
                        )
                    )
                    if code == 0:
                        success_count += 1
                
                if success_count > 0:
                    st.success(f"{success_count}件の資料を {dest_course} へ移動しました。")
                    st.rerun()
                else:
                    st.error("移動できませんでした。")
        else:
            if st.button("一括削除を実行", type="primary", key="btn_batch_execute_delete"):
                success_count = 0
                for path in selected_paths:
                    code = cmc.delete_material(
                        args(
                            root=str(root_path()),
                            material=str(path),
                            ocr_language="jpn+eng",
                        )
                    )
                    if code == 0:
                        success_count += 1
                
                if success_count > 0:
                    st.success(f"{success_count}件の資料を削除しました。")
                    st.rerun()
                else:
                    st.error("削除できませんでした。")
    else:
        st.info("上の「分類済み資料」リストから、移動・削除したい資料のチェックボックスにチェックを入れてください。")

with tab_ai:
    courses, _records = refresh_state()
    course_names = ["全授業"] + [course.name for course in courses]
    selected = st.selectbox("対象授業", course_names)
    course_arg = None if selected == "全授業" else selected
    api_provider = st.radio("APIプロバイダー", ["OpenAI", "Gemini", "ローカル（APIを使わない）"], horizontal=True)
    
    import os
    has_gemini = bool(os.environ.get("GEMINI_API_KEY"))
    has_openai = bool(os.environ.get("OPENAI_API_KEY"))
    
    if api_provider == "OpenAI":
        default_model = "gpt-4o-mini"
        local_only = False
        api_provider_arg = "openai"
        if not has_openai:
            st.warning("⚠️ OpenAI APIキーが設定されていません。サイドバーに入力するか、環境変数を設定してください。実行するとローカル要約にフォールバックします。")
    elif api_provider == "Gemini":
        default_model = "gemini-2.5-flash"
        local_only = False
        api_provider_arg = "gemini"
        if not has_gemini:
            st.warning("⚠️ Gemini APIキーが設定されていません。サイドバーに入力するか、環境変数を設定してください。実行するとローカル要約にフォールバックします。")
    else:
        default_model = "local"
        local_only = True
        api_provider_arg = "openai"
        
    model = st.text_input("モデル", value=default_model)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("要約と要点を生成"):
            code = cmc.analyze_materials(
                args(
                    root=str(root_path()),
                    course=course_arg,
                    model=model,
                    local_only=local_only,
                    api_provider=api_provider_arg,
                    force=True,
                    ocr_language="jpn+eng",
                )
            )
            st.success("分析しました。" if code == 0 else "分析できませんでした。")
    with col2:
        count = st.number_input("問題数", min_value=1, max_value=20, value=5)
        if st.button("練習問題を生成"):
            code = cmc.generate_practice(
                args(
                    root=str(root_path()),
                    course=course_arg,
                    count=int(count),
                    model=model,
                    local_only=local_only,
                    api_provider=api_provider_arg,
                    force=True,
                )
            )
            st.success("問題を生成しました。" if code == 0 else "生成できませんでした。")

    summaries = cmc.load_summaries(root_path())
    questions = cmc.load_questions(root_path())
    st.subheader("生成済み")
    st.write(f"要約: {len(summaries)} 件 / 問題: {len(questions)} 問")

    st.write("---")
    st.subheader("管理")
    if st.button("選択した授業の要約と練習問題をクリア", type="primary", key="btn_clear_analysis"):
        code = cmc.clear_analysis(
            args(
                root=str(root_path()),
                course=course_arg,
            )
        )
        if code == 0:
            st.success(f"「{selected}」の要約と練習問題をクリアしました！")
            st.rerun()
        else:
            st.error("クリアに失敗しました。")

with tab_site:
    output = st.text_input("出力フォルダ", value="_site")
    index_path = root_path() / output / "index.html"
    
    if st.button("Webページを生成"):
        code = cmc.build_site(args(root=str(root_path()), output=output))
        if code == 0:
            st.success(f"生成しました: {index_path}")
        else:
            st.error("Webページを生成できませんでした。")
            
    if index_path.exists():
        st.write("---")
        st.info("Webページを表示する準備ができています。")
        output_url_path = output.strip("/").replace("\\", "/")
        site_url = f"/{output_url_path}/index.html"
        st.markdown(f"### 🔗 [こちらをクリックしてWebページを開く (別タブ)]({site_url})")
        st.caption("※現在のStreamlitサーバー経由で表示します。Webページ生成後、開いているページを更新してください。")
        
        if st.button("ブラウザで直接開く", key="btn_open_site"):
            import os
            os.system(f"start {site_url}")

with tab_attendance:
    st.subheader("出席状況の管理")
    courses, _records = refresh_state()
    if not courses:
        st.info("先に「授業管理」タブから授業を登録してください。")
    else:
        course_names = [course.name for course in courses]
        selected_course_name = st.selectbox("授業を選択", course_names, key="attendance_course_select")
        
        # 選択されたコースの取得
        course = next(c for c in courses if c.name == selected_course_name)
        
        # 出席統計の計算
        total_classes = len(course.attendance)
        presents = sum(1 for att in course.attendance if att.status == "出席")
        lates = sum(1 for att in course.attendance if att.status == "遅刻")
        absents = sum(1 for att in course.attendance if att.status == "欠席")
        excuseds = sum(1 for att in course.attendance if att.status == "公欠")
        
        attendance_rate = 0.0
        if total_classes > 0:
            attendance_rate = (presents + lates) / total_classes * 100
            
        st.write("### 📊 出席統計")
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("総授業回数", f"{total_classes} 回")
        col2.metric("出席", f"{presents} 回")
        col3.metric("遅刻", f"{lates} 回")
        col4.metric("欠席", f"{absents} 回")
        col5.metric("出席率", f"{attendance_rate:.1f} %")
        
        st.write("---")
        
        col_left, col_right = st.columns([1, 2])
        
        with col_left:
            st.write("#### ➕ 出席の登録")
            with st.form("add_attendance_form", clear_on_submit=True):
                next_round = total_classes + 1
                if course.attendance:
                    next_round = max(att.class_round for att in course.attendance) + 1
                
                class_round = st.number_input("授業回", min_value=1, value=next_round)
                att_date = st.date_input("授業日", value=datetime.date.today())
                att_status = st.selectbox("出席状況", ["出席", "遅刻", "欠席", "公欠"])
                att_memo = st.text_area("メモ (授業内容・課題など)")
                submitted = st.form_submit_button("登録")
                
            if submitted:
                if any(att.class_round == class_round for att in course.attendance):
                    st.error(f"第 {class_round} 回のデータはすでに存在します。右側のリストから編集・削除してください。")
                else:
                    new_att = cmc.AttendanceRecord(
                        date=str(att_date),
                        class_round=int(class_round),
                        status=att_status,
                        memo=att_memo
                    )
                    course.attendance.append(new_att)
                    course.attendance.sort(key=lambda x: x.class_round)
                    cmc.save_courses(root_path(), courses)
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
                            edit_status = st.selectbox("出席状況", ["出席", "遅刻", "欠席", "公欠"], index=["出席", "遅刻", "欠席", "公欠"].index(att.status) if att.status in ["出席", "遅刻", "欠席", "公欠"] else 0, key=f"edit_status_{att.class_round}")
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
                            cmc.save_courses(root_path(), courses)
                            st.success(f"第 {att.class_round} 回を更新しました。")
                            st.rerun()
                            
                        if delete_submitted:
                            course.attendance.remove(att)
                            cmc.save_courses(root_path(), courses)
                            st.success(f"第 {att.class_round} 回を削除しました。")
                            st.rerun()

with tab_links:
    st.subheader("共通参考URLリンク集の管理")
    
    global_links = cmc.load_global_links(root_path())
    
    st.write("### 🔗 共通の参考リンク一覧")
    
    if global_links:
        for idx, lk in list(enumerate(global_links)):
            col_link, col_del = st.columns([8, 2])
            with col_link:
                st.markdown(f"[{lk.title}]({lk.url}) — *{lk.memo}*" if lk.memo else f"[{lk.title}]({lk.url})")
            with col_del:
                if st.button("削除", key=f"del_global_link_{idx}"):
                    global_links.pop(idx)
                    cmc.save_global_links(root_path(), global_links)
                    try:
                        cmc.build_site(args(root=str(root_path()), output="_site"))
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
            new_link = cmc.LinkRecord(title=lk_title, url=lk_url, memo=lk_memo)
            global_links.append(new_link)
            cmc.save_global_links(root_path(), global_links)
            try:
                cmc.build_site(args(root=str(root_path()), output="_site"))
            except Exception:
                pass
            st.success("リンクを追加しました。")
            st.rerun()
