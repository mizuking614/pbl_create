
# Class Materials Compiler

授業資料や手書きメモ、課題ファイルを授業ごとに整理し、AI分析や練習問題生成まで行うPythonツールです。

## できること

- 授業名、教員名、キーワードを登録し、授業名のフォルダを作成
- テキスト、Markdown、CSV、PDF、画像ファイルを読み取り
- 画像は Tesseract OCR を使って文字認識
- 手書き・スキャンPDFは、文字抽出できないページを画像化してOCR
- `pypdfium2` により、PopplerなしでPDFを画像化してOCR
- Word文書（`.docx`）の読み取り
- 登録キーワードと、過去に分類した資料から学習した語句を使って分類
- 分類先が弱い資料は `_未分類` に保存
- 誤分類された資料をあとから別授業へ移動し、資料由来の学習語句も移動
- 集めた資料をブラウザで見やすいHTMLページとして出力
- 資料をAIで分析し、要約、要点、重要語句、復習チェックを生成
- 授業資料をもとに練習問題と解答・解説を生成
- CLEカレンダーから課題を取得し、締切が5か月以上前のものを除外
- 締切から7日以上経過した課題は一覧に残すが、「今日やること」には入れない
- 「課題」「提出」「レポート」「宿題」「homework」「assignment」を含む予定を課題として判定
- 出席履歴と資料を授業回ごとのタイムラインで確認
- OCR本文、要約、授業名、キーワードを横断検索
- Streamlit GUIで主要操作を画面から実行

## セットアップ

Python 3.10 以降を推奨します。

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

画像OCRを使う場合は、別途 Tesseract OCR 本体と日本語データが必要です。
Windows では Tesseract をインストールし、`jpn.traineddata` と `eng.traineddata` が使える状態にしてください。

手書き・スキャンPDFのOCRにはTesseract OCRが必要です。PDFの画像化には `pypdfium2` を使用するため、Popplerの `pdftoppm` は不要です。
通常の文字入りPDFはそのまま読み取り、文字を抽出できないページだけOCRします。要約を実行すると、資料ごとの要約PDFも生成されます。

OpenAI APIで要約・問題生成を行う場合は、環境変数 `OPENAI_API_KEY` を設定してください。
Geminiを利用する場合は `GEMINI_API_KEY` を設定してください。
APIキーがない場合でも、`--local-only` を使うと抽出型の簡易生成で動作確認できます。

## 使い方

授業を登録します。

```powershell
python class_materials_compiler.py add-course "情報理論" --teacher "山田先生" --keywords "エントロピー,符号化,通信路"
python class_materials_compiler.py add-course "心理学概論" --teacher "佐藤先生" --keywords "認知,記憶,学習,発達"
```

登録内容を確認します。

```powershell
python class_materials_compiler.py list-courses
```

資料を分類します。

```powershell
python class_materials_compiler.py sort "C:\path\to\materials" --recursive
```

元ファイルを残したい場合はコピーします。

```powershell
python class_materials_compiler.py sort "C:\path\to\materials" --recursive --copy
```

分類が厳しすぎる、または緩すぎる場合は `--threshold` を調整してください。

```powershell
python class_materials_compiler.py sort ".\incoming" --threshold 0.05
```

誤って分類された資料は、あとから正しい授業へ移動できます。
このとき、その資料から学習した語句も元の授業から移動先の授業へ付け替えます。

```powershell
python class_materials_compiler.py reassign ".\心理学概論\entropy_note.md" --to "情報理論"
```

資料を分析して、要約・要点・重要語句・復習チェックを生成します。

```powershell
python class_materials_compiler.py analyze
```

特定の授業だけ分析する場合:

```powershell
python class_materials_compiler.py analyze --course "情報理論"
```

OpenAI APIを使わず、ローカルの抽出型要約だけを生成する場合:

```powershell
python class_materials_compiler.py analyze --local-only
```

授業資料から練習問題を生成します。

```powershell
python class_materials_compiler.py generate-practice --course "情報理論" --count 8
```

集めた資料をWebページ形式にまとめます。

```powershell
python class_materials_compiler.py build-site
```

生成された `_site\index.html` をブラウザで開くと、授業別の資料一覧、検索欄、キーワード、画像資料のサムネイルを確認できます。
出力先を変える場合は `--output` を指定します。

```powershell
python class_materials_compiler.py build-site --output ".\library_site"
```

GUIで操作する場合:

```powershell
streamlit run streamlit_app.py
```

Windowsでは、プロジェクト直下の `launch_compiler.bat` を実行すると、ブラウザ用APIサーバーとStreamlitをまとめて起動できます。

`server.py` は個人利用向けのローカルAPIです。`http://127.0.0.1:8000` で起動し、授業・資料の一覧取得と登録、PDFやテキストの文字抽出、OpenAI API中継を提供します。ログインやユーザー認証は実装していません。

GUIには、授業管理、資料整理、AI分析、出席管理、リンク管理に加えて、授業回ごとのタイムライン、資料の全文検索、授業資料に基づくAIチャットを搭載しています。データは既存の `.class_materials` 配下へ保存され、従来のCLIと同じ保存ルートを共有します。

GUIの主なタブ:

1. **授業管理**: 授業、教員名、分類キーワードを登録・更新
2. **資料整理**: 資料のアップロード、分類、再配置、削除
3. **AI分析**: 要約、重要語句、復習チェック、練習問題の生成
4. **Webページ**: 資料ライブラリをHTMLポータルとして出力
5. **出席管理**: 出席状況、授業回、授業メモ、出席率を管理
6. **リンク管理**: 授業に関する参考URLを管理
7. **タイムライン**: 出席履歴と資料を授業回ごとに表示
8. **全文検索**: OCR本文、要約、授業名、キーワードを横断検索
9. **授業AIチャット**: 資料を根拠にした質問応答

## 対応ファイル

- `.txt`
- `.md`
- `.csv`
- `.pdf`
- `.png`
- `.jpg`
- `.jpeg`
- `.bmp`
- `.tif`
- `.tiff`
- `.docx`

## 保存されるもの

- `.class_materials/courses.json`: 授業情報、資料ごとの分類履歴、分類から学習した語句
- `.class_materials/summaries.json`: 資料ごとの要約、要点、重要語句
- `.class_materials/questions.json`: 授業ごとの練習問題、解答、解説
- `<授業名>/`: 授業資料の保存フォルダ
- `<資料名>.summary.md`: 資料ごとの要約Markdown
- `<資料名>.summary.pdf`: 印刷用の要約PDF
- `<授業名>/practice_questions.md`: 授業ごとの練習問題Markdown
- `_未分類/`: どの授業にも十分一致しなかった資料

## Flutter版

Flutter版はCLEカレンダー連携を中心としたAIタスク管理アプリです。ポータルから次の機能を利用できます。

- **学習優先順位AI**: CLEのICS URLから課題と予定を取得し、重要度・締切・空き時間をもとに優先順位を計算
- **今日やること**: 睡眠・食事・授業を除いた空き時間へ、7日以内の期限超過または未来の未完了課題を自動配置
- **手入力タスク**: CLEにない個人タスクを追加・編集・削除し、締切・所要時間・重要度を設定して同じ優先順位計算に追加
- **課題検索**: 課題名または授業名で課題一覧を絞り込み
- **カテゴリ絞り込み**: 授業名カテゴリで課題一覧を絞り込み、検索と併用できる
- **学修計画・類題生成**: 学習目標と期間から計画を作成し、CLE課題がある場合は締切順に計画へ反映。入力テーマと課題名から確認問題を生成
- **授業・資料管理**: 授業名と資料名を端末へ保存し、ローカルAPIが起動していればSQLiteとも同期

課題の完了状態と生活リズム、授業・資料のローカル情報は `SharedPreferences` に保存されます。FlutterとPythonのデータを完全に同じ形式で自動共有する機能は、今後の拡張対象です。

### Flutter版の保存項目

- `cle_ics_url`: CLEカレンダー共有用ICS URL
- `assignment_completions`: 課題ごとの完了状態
- `user_routine`: 睡眠時間と食事時間
- `member_b_courses`: 登録した授業名
- `member_b_materials`: 登録した資料名

## Flutter版の進捗

Flutter版には、CLEカレンダーから課題と予定を取得し、重要度・締切・空き時間をもとに学習優先順位を表示する機能があります。課題の完了状態と睡眠時間はSharedPreferencesへ保存され、再起動後も復元されます。カテゴリ絞り込み、手入力タスクの編集・削除、資料連携付きの学修計画・類題生成、資料アップロード連携も利用できます。

ポータルからは、学修計画・類題生成と授業・資料管理の画面へ移動できます。メンバーA画面では目標と期間、授業/資料コンテキストを使った学習計画・確認問題を作成でき、メンバーB画面では授業名と資料名を端末またはローカルAPIへ保存し、資料ファイルの本文抽出にも対応しています。生成AIによる自然言語の計画・問題生成とPython版との自動連携は今後の拡張対象ですが、現在の個人向けタスク管理アプリとしては利用可能な状態です。

### 最終状態

以下の機能は実装・検証済みです。

- 課題一覧の追加・編集・削除
- 課題検索と授業カテゴリでの絞り込み
- 今日やるべきことの優先度自動計算
- 手入力タスクとCLE課題の統合
- 学修計画の作成と、授業/資料コンテキストへの連携
- 授業・資料管理のローカル保存とローカルAPI同期
- 資料アップロード時の本文抽出連携
- CLE URL不正時の明確なエラーメッセージ表示
- 回帰テストの整備

現在のアプリは、個人向けAIタスク管理を主目的としたローカル利用型の運用を前提にしています。ログイン機能や多人数共有は設計上不要であり、今後は実際のAIモデル連携やPyhon/Flutter間のデータ統合を深める方向で拡張できます。