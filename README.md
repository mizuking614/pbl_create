# Class Materials Compiler

授業資料や手書きメモを、授業ごとのフォルダへ自動分類する Python CLI ツールです。

## できること

- 授業名、教員名、キーワードを登録し、授業名のフォルダを作成
- テキスト、Markdown、CSV、PDF、画像ファイルを読み取り
- 画像は Tesseract OCR を使って文字認識
- 手書き・スキャンPDFは、文字抽出できないページを画像化してOCR
- 登録キーワードと、過去に分類した資料から学習した語句を使って分類
- 分類先が弱い資料は `_未分類` に保存
- 誤分類された資料をあとから別授業へ移動し、資料由来の学習語句も移動
- 集めた資料をブラウザで見やすいHTMLページとして出力
- 資料をAIで分析し、要約、要点、重要語句、復習チェックを生成
- 授業資料をもとに練習問題と解答・解説を生成
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

手書き・スキャンPDFのOCRには、Tesseract OCR に加えて Poppler の `pdftoppm` コマンドが必要です。
通常の文字入りPDFはそのまま読み取り、文字を抽出できないページだけOCRします。

OpenAI APIで要約・問題生成を行う場合は、環境変数 `OPENAI_API_KEY` を設定してください。
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

## 保存されるもの

- `.class_materials/courses.json`: 授業情報、資料ごとの分類履歴、分類から学習した語句
- `.class_materials/summaries.json`: 資料ごとの要約、要点、重要語句
- `.class_materials/questions.json`: 授業ごとの練習問題、解答、解説
- `<授業名>/`: 授業資料の保存フォルダ
- `<資料名>.summary.md`: 資料ごとの要約Markdown
- `<授業名>/practice_questions.md`: 授業ごとの練習問題Markdown
- `_未分類/`: どの授業にも十分一致しなかった資料
