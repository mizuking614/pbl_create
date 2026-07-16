// UI要素の取得
const apiKeyInput = document.getElementById('apiKeyInput');
const saveKeyBtn = document.getElementById('saveKeyBtn');
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const fileStatus = document.getElementById('fileStatus');
const statusFileName = document.getElementById('statusFileName');
const statusFileSize = document.getElementById('statusFileSize');
const clearFileBtn = document.getElementById('clearFileBtn');
const textPreview = document.getElementById('textPreview');
const extractTopicsBtn = document.getElementById('extractTopicsBtn');
const topicsContainer = document.getElementById('topicsContainer');
const topicsList = document.getElementById('topicsList');
const difficultySelect = document.getElementById('difficultySelect');
const formatSelect = document.getElementById('formatSelect');
const generateQuestionBtn = document.getElementById('generateQuestionBtn');
const questionOutputArea = document.getElementById('questionOutputArea');
const outputPlaceholder = document.getElementById('outputPlaceholder');
const outputLoader = document.getElementById('outputLoader');
const loaderMessage = document.getElementById('loaderMessage');
const questionContainer = document.getElementById('questionContainer');
const qDifficulty = document.getElementById('qDifficulty');
const qFormat = document.getElementById('qFormat');
const qText = document.getElementById('qText');
const optionsArea = document.getElementById('optionsArea');
const textInputArea = document.getElementById('textInputArea');
const userAnswerText = document.getElementById('userAnswerText');
const submitTextAnswerBtn = document.getElementById('submitTextAnswerBtn');
const freeInputArea = document.getElementById('freeInputArea');
const userAnswerFree = document.getElementById('userAnswerFree');
const submitFreeAnswerBtn = document.getElementById('submitFreeAnswerBtn');
const feedbackArea = document.getElementById('feedbackArea');
const feedbackResult = document.getElementById('feedbackResult');
const correctAnswerText = document.getElementById('correctAnswerText');
const explanationText = document.getElementById('explanationText');
const nextQuestionBtn = document.getElementById('nextQuestionBtn');
const toast = document.getElementById('toast');
const displayFormat = document.getElementById('displayFormat');
const apiProviderBadge = document.getElementById('apiProviderBadge');
const cleUrlInput = document.getElementById('cleUrlInput');
const saveCleUrlBtn = document.getElementById('saveCleUrlBtn');
const cleUrlStatus = document.getElementById('cleUrlStatus');

// アプリケーション状態
let appState = {
    apiKey: '',
    uploadedText: '',
    extractedTopics: [],
    selectedTopics: [],
    currentQuestion: null,
    selectedOption: null,
    cachedImageDataUrl: null,
    cleUrl: localStorage.getItem('cle_ical_url') || ''
};

// 1. 初期化処理
document.addEventListener('DOMContentLoaded', () => {
    // APIキーの読み込み
    const savedKey = localStorage.getItem('gemini_api_key');
    if (savedKey) {
        apiKeyInput.value = savedKey;
        appState.apiKey = savedKey;
        updateProviderBadge(savedKey);
        showToast('保存されているAPIキーをロードしました。', 'success');
    }

    // CLE URLの読み込み
    if (appState.cleUrl) {
        cleUrlInput.value = appState.cleUrl;
    }
    updateCleUrlStatus();

    setupEventListeners();
});

// 2. イベントリスナーの設定
function setupEventListeners() {
    // APIキーの保存
    saveKeyBtn.addEventListener('click', () => {
        const key = apiKeyInput.value.trim();
        if (key) {
            localStorage.setItem('gemini_api_key', key);
            appState.apiKey = key;
            updateProviderBadge(key);
            showToast('APIキーを保存しました。', 'success');
        } else {
            localStorage.removeItem('gemini_api_key');
            appState.apiKey = '';
            updateProviderBadge('');
            showToast('APIキーをクリアしました。', 'success');
        }
    });

    apiKeyInput.addEventListener('input', (e) => {
        updateProviderBadge(e.target.value);
    });

    // CLE URL保存
    saveCleUrlBtn.addEventListener('click', () => {
        const url = cleUrlInput.value.trim();
        if (!url) {
            localStorage.removeItem('cle_ical_url');
            appState.cleUrl = '';
            updateCleUrlStatus();
            showToast('CLE共有URLをクリアしました。', 'success');
            return;
        }

        if (!url.startsWith('http://') && !url.startsWith('https://')) {
            showToast('有効なURLを入力してください。', 'error');
            return;
        }

        localStorage.setItem('cle_ical_url', url);
        appState.cleUrl = url;
        updateCleUrlStatus();
        showToast('CLE共有URLを保存しました。', 'success');
    });

    cleUrlInput.addEventListener('input', () => {
        if (!cleUrlInput.value.trim() && appState.cleUrl) {
            cleUrlInput.value = appState.cleUrl;
        }
    });

    // ファイル選択ダイアログのトリガー
    dropZone.addEventListener('click', () => {
        fileInput.click();
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFile(e.target.files[0]);
        }
    });

    // ドラッグ＆ドロップイベント
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('dragover');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        if (e.dataTransfer.files.length > 0) {
            handleFile(e.dataTransfer.files[0]);
        }
    });

    // ファイル解除
    clearFileBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        clearFile();
    });

    // プレビュー変更監視
    textPreview.addEventListener('input', (e) => {
        appState.uploadedText = e.target.value;
        checkExtractButtonState();
    });

    // トピック抽出実行
    extractTopicsBtn.addEventListener('click', extractTopics);

    // 類題生成実行
    generateQuestionBtn.addEventListener('click', generateQuestion);

    // 次の問題ボタン
    nextQuestionBtn.addEventListener('click', generateQuestion);

    // 記述式解答送信
    submitTextAnswerBtn.addEventListener('click', () => {
        const answer = userAnswerText.value.trim();
        if (!answer) {
            showToast('解答を入力してください。', 'error');
            return;
        }
        checkAnswer(answer);
    });

    // 思考記述式解答送信
    submitFreeAnswerBtn.addEventListener('click', () => {
        const answer = userAnswerFree.value.trim();
        if (!answer) {
            showToast('考えやコードを記入してください。', 'error');
            return;
        }
        evaluateFreeAnswer(answer);
    });

    // 表示形式の切り替え
    displayFormat.addEventListener('change', () => {
        if (appState.currentQuestion) {
            renderQuestion(difficultySelect.value, formatSelect.value, appState.currentQuestion);
        }
    });
}

// 3. ファイル読み込み処理
async function handleFile(file) {
    // 読込制限
    const MAX_SIZE = 5 * 1024 * 1024; // 5MB
    if (file.size > MAX_SIZE) {
        showToast('ファイルサイズが大きすぎます。5MB以下のファイルを選択してください。', 'error');
        return;
    }

    // 読み込み中UI
    statusFileName.textContent = '読み込み中...';
    statusFileSize.textContent = '';
    dropZone.classList.add('hidden');
    fileStatus.classList.remove('hidden');

    const isPdf = file.name.toLowerCase().endsWith('.pdf') || file.type === 'application/pdf';

    try {
        let text = '';
        if (isPdf) {
            // PDFの場合はサーバーのテキスト抽出APIを使用する
            const response = await fetch('/api/extract-text', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/octet-stream',
                    'X-File-Name': encodeURIComponent(file.name),
                    'X-File-Type': file.type || 'application/pdf',
                },
                body: await file.arrayBuffer(),
            });

            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.error || 'PDFの解析に失敗しました。');
            }
            text = data.text;
        } else {
            // テキストファイルの場合は FileReader を使用
            text = await new Promise((resolve, reject) => {
                const reader = new FileReader();
                reader.onload = (e) => resolve(e.target.result);
                reader.onerror = () => reject(new Error('ファイルの読み込み中にエラーが発生しました。'));
                reader.readAsText(file, 'UTF-8');
            });

            // 簡易バイナリチェック（NULLバイトが含まれる場合はテキストではないとみなす）
            if (text.includes('\u0000')) {
                throw new Error('バイナリファイルはサポートされていません。テキスト形式のファイルまたはPDFを選択してください。');
            }
        }

        appState.uploadedText = text;
        textPreview.value = text;
        
        statusFileName.textContent = file.name;
        statusFileSize.textContent = formatBytes(file.size);
        
        showToast('ファイルを正常に読み込みました。', 'success');
        checkExtractButtonState();
    } catch (error) {
        showToast(error.message, 'error');
        clearFile();
    }
}

function clearFile() {
    fileInput.value = '';
    appState.uploadedText = '';
    textPreview.value = '';
    dropZone.classList.remove('hidden');
    fileStatus.classList.add('hidden');
    checkExtractButtonState();
}

function checkExtractButtonState() {
    if (appState.uploadedText.trim().length > 10) {
        extractTopicsBtn.removeAttribute('disabled');
    } else {
        extractTopicsBtn.setAttribute('disabled', 'true');
    }
}

// 4. APIキー判定 & プロバイダーバッジ制御
function detectProvider(key) {
    if (!key) return null;
    const cleanKey = key.trim();
    if (cleanKey.startsWith('sk-')) return 'openai';
    if (cleanKey.startsWith('AIzaSy')) return 'gemini';
    return null;
}

function updateProviderBadge(key) {
    const provider = detectProvider(key);
    if (provider === 'openai') {
        apiProviderBadge.textContent = 'OpenAI';
        apiProviderBadge.className = 'provider-badge openai';
        apiProviderBadge.classList.remove('hidden');
    } else if (provider === 'gemini') {
        apiProviderBadge.textContent = 'Gemini';
        apiProviderBadge.className = 'provider-badge gemini';
        apiProviderBadge.classList.remove('hidden');
    } else {
        apiProviderBadge.classList.add('hidden');
    }
}

function updateCleUrlStatus() {
    if (appState.cleUrl) {
        cleUrlStatus.textContent = '保存済みのCLE共有URLがあります。';
    } else {
        cleUrlStatus.textContent = '共有されたCLEのiCal URLを貼り付けて保存してください。';
    }
}

// AI API 呼び出し共通関数 (Gemini / OpenAI 自動切替)
async function callAI(prompt, systemInstruction = '', responseSchema = null) {
    if (!appState.apiKey) {
        throw new Error('APIキーが設定されていません。ヘッダーから入力して保存してください。');
    }

    const provider = detectProvider(appState.apiKey);
    if (!provider) {
        throw new Error('APIキーの形式が正しくありません。(OpenAIキーは sk-...、Geminiキーは AIzaSy... で始まる必要があります)');
    }

    if (provider === 'gemini') {
        return callGeminiAPI(prompt, systemInstruction, responseSchema);
    } else {
        return callOpenAIAPI(prompt, systemInstruction, responseSchema);
    }
}

// Gemini API 呼び出し
async function callGeminiAPI(prompt, systemInstruction = '', responseSchema = null) {
    const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${appState.apiKey}`;
    
    const requestBody = {
        contents: [
            {
                parts: [{ text: prompt }]
            }
        ]
    };

    if (systemInstruction) {
        requestBody.systemInstruction = {
            parts: [{ text: systemInstruction }]
        };
    }

    if (responseSchema) {
        requestBody.generationConfig = {
            responseMimeType: "application/json",
            responseSchema: responseSchema
        };
    }

    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestBody)
    });

    if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        const errMsg = errData.error?.message || `HTTPエラー: ${response.status}`;
        throw new Error(errMsg);
    }

    const data = await response.json();
    const responseText = data.candidates?.[0]?.content?.parts?.[0]?.text;
    
    if (!responseText) {
        throw new Error('Geminiからのレスポンスが空です。プロンプトを見直すか、時間を置いて再度試してください。');
    }

    return responseText;
}

// OpenAI API 呼び出し
async function callOpenAIAPI(prompt, systemInstruction = '', responseSchema = null) {
    const url = 'https://api.openai.com/v1/chat/completions';
    
    const messages = [];
    if (systemInstruction) {
        messages.push({ role: 'system', content: systemInstruction });
    }
    messages.push({ role: 'user', content: prompt });

    const requestBody = {
        model: 'gpt-4o-mini',
        messages: messages,
        temperature: 0.7
    };

    let wasArray = false;
    if (responseSchema) {
        let finalSchema = responseSchema;
        // OpenAIの制約（ルートは必ずobjectでなければならない）を回避するため、array型の場合は一時的にオブジェクトでラップする
        if (responseSchema.type === 'ARRAY' || responseSchema.type === 'array') {
            wasArray = true;
            finalSchema = {
                type: 'OBJECT',
                properties: {
                    items: responseSchema
                },
                required: ['items']
            };
        }

        requestBody.response_format = {
            type: "json_schema",
            json_schema: {
                name: "api_response",
                strict: true,
                schema: convertGeminiSchemaToOpenAISchema(finalSchema)
            }
        };
    }

    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${appState.apiKey}`
        },
        body: JSON.stringify(requestBody)
    });

    if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        const errMsg = errData.error?.message || `HTTPエラー: ${response.status}`;
        throw new Error(errMsg);
    }

    const data = await response.json();
    let responseText = data.choices?.[0]?.message?.content;
    
    if (!responseText) {
        throw new Error('OpenAIからのレスポンスが空です。プロンプトを見直すか、時間を置いて再度試してください。');
    }

    // オブジェクトでラップしていた場合は、配列部分を取り出して元の形状に戻す
    if (wasArray) {
        try {
            const parsed = JSON.parse(responseText.trim());
            if (parsed && parsed.items) {
                responseText = JSON.stringify(parsed.items);
            }
        } catch (e) {
            console.error('JSONアンラップエラー:', e);
        }
    }

    return responseText;
}

// GeminiのSchema形式をOpenAI (Standard JSON Schema / strict: true) の形式に変換する
function convertGeminiSchemaToOpenAISchema(geminiSchema) {
    if (!geminiSchema) return null;

    function convert(schema) {
        if (!schema || typeof schema !== 'object') return schema;

        const newSchema = {};
        
        if (schema.type) {
            newSchema.type = schema.type.toLowerCase();
        }

        if (schema.description) {
            newSchema.description = schema.description;
        }

        if (newSchema.type === 'array' && schema.items) {
            newSchema.items = convert(schema.items);
        }

        if (newSchema.type === 'object') {
            if (schema.properties) {
                newSchema.properties = {};
                for (const key in schema.properties) {
                    newSchema.properties[key] = convert(schema.properties[key]);
                }
            }
            
            // strict: true の制約上、すべてのプロパティを required に含める必要がある
            if (newSchema.properties) {
                newSchema.required = Object.keys(newSchema.properties);
            }
            
            newSchema.additionalProperties = false;
        }

        return newSchema;
    }

    return convert(geminiSchema);
}

// 5. 学習トピック抽出処理
async function extractTopics() {
    const btnLoader = extractTopicsBtn.querySelector('.btn-loader');
    const btnText = extractTopicsBtn.querySelector('span:first-child');
    
    // UIをロード状態にする
    extractTopicsBtn.setAttribute('disabled', 'true');
    btnLoader.classList.remove('hidden');
    btnText.textContent = 'トピック抽出中...';
    topicsContainer.innerHTML = '<div class="spinner" style="width: 24px; height: 24px;"></div>';

    const prompt = `以下のテキスト（学習資料）を分析し、ユーザーが学ぶべき重要な概念、技術用語、またはトピックを最大10個抽出してください。
出力は、必ずユーザーの選択肢（タグ名）としてふさわしい、具体的で簡潔な日本語のキーワードにしてください。`;

    const systemInstruction = 'あなたは学習資料を分析し、主要なトピックを抽出してJSON配列で出力する専門のAIアシスタントです。';
    
    // JSON Schemaによる構造化出力定義
    const responseSchema = {
        type: 'ARRAY',
        description: '主要なトピックキーワードのリスト',
        items: {
            type: 'STRING'
        }
    };

    try {
        const responseText = await callAI(
            `${prompt}\n\n【テキスト】\n${appState.uploadedText}`,
            systemInstruction,
            responseSchema
        );

        // JSONパース
        const topics = JSON.parse(responseText.trim());
        appState.extractedTopics = topics;
        appState.selectedTopics = []; // リセット

        renderTopics();
        showToast('トピックの抽出が完了しました！', 'success');
    } catch (error) {
        showToast(`トピック抽出に失敗しました: ${error.message}`, 'error');
        topicsContainer.innerHTML = `<p class="placeholder-text" style="color: var(--color-error)">トピック抽出に失敗しました: ${error.message}</p>`;
    } finally {
        extractTopicsBtn.removeAttribute('disabled');
        btnLoader.classList.add('hidden');
        btnText.textContent = '学習トピックを抽出する';
        updateGenerateButtonState();
    }
}

// トピックタグの描画
function renderTopics() {
    topicsContainer.innerHTML = '';
    
    if (appState.extractedTopics.length === 0) {
        topicsContainer.innerHTML = '<p class="placeholder-text">トピックが見つかりませんでした。</p>';
        return;
    }

    const listDiv = document.createElement('div');
    listDiv.className = 'topics-list';

    appState.extractedTopics.forEach(topic => {
        const chip = document.createElement('div');
        chip.className = 'topic-chip';
        chip.textContent = topic;
        
        chip.addEventListener('click', () => {
            if (chip.classList.contains('selected')) {
                chip.classList.remove('selected');
                appState.selectedTopics = appState.selectedTopics.filter(t => t !== topic);
            } else {
                chip.classList.add('selected');
                appState.selectedTopics.push(topic);
            }
            updateGenerateButtonState();
        });

        listDiv.appendChild(chip);
    });

    topicsContainer.appendChild(listDiv);
}

function updateGenerateButtonState() {
    if (appState.selectedTopics.length > 0) {
        generateQuestionBtn.removeAttribute('disabled');
    } else {
        generateQuestionBtn.setAttribute('disabled', 'true');
    }
}

// 6. 類題生成処理
async function generateQuestion() {
    const difficulty = difficultySelect.value;
    const format = formatSelect.value;
    appState.cachedImageDataUrl = null;
    
    // UI表示の切り替え
    outputPlaceholder.classList.add('hidden');
    questionContainer.classList.add('hidden');
    feedbackArea.classList.add('hidden');
    outputLoader.classList.remove('hidden');
    
    const btnLoader = generateQuestionBtn.querySelector('.btn-loader');
    generateQuestionBtn.setAttribute('disabled', 'true');
    btnLoader.classList.remove('hidden');

    const prompt = `以下の【学習資料】をもとに、指定された【選択トピック】に関連する類題（練習問題）を1問作成してください。

【学習資料】
${appState.uploadedText}

【選択トピック】
${appState.selectedTopics.join(', ')}

【問題の難易度】
${difficulty}

【問題の形式】
${format === '選択式' ? '4択の多肢選択式' : format === '記述式' ? '記述式（穴埋め、または短い言葉で答える問題）' : '思考記述式（考えを自由に説明させる問題）'}

【出力内容の要件】
- 多肢選択式の場合: options配列に4つの選択肢を入れてください。answerは正解の選択肢の文字列（例："A: ..."）を記述してください。
- 記述式の場合: optionsはnullまたは空配列にしてください。answerは想定される正解のキーワードや短い文を入れてください。
- 思考記述式の場合: optionsはnullまたは空配列にしてください。answerは模範解答を記述してください。`;

    const systemInstruction = 'あなたは優秀な教育AIです。提供された学習資料とトピックに基づき、指定されたJSONフォーマットに従って精度の高い問題を作成してください。';
    
    // JSON Schema定義
    const responseSchema = {
        type: 'OBJECT',
        properties: {
            question: { type: 'STRING', description: '問題文。マークダウン形式でも可。' },
            options: { 
                type: 'ARRAY', 
                description: '多肢選択式の場合の4つの選択肢。それ以外はnullまたは空配列。',
                items: { type: 'STRING' } 
            },
            answer: { type: 'STRING', description: '正解または模範解答。選択式の場合はoptions内のいずれかの文字列。' },
            explanation: { type: 'STRING', description: '問題の解き方や背景知識に関する詳細な解説。' }
        },
        required: ['question', 'answer', 'explanation']
    };

    try {
        const responseText = await callAI(prompt, systemInstruction, responseSchema);
        const questionData = JSON.parse(responseText.trim());
        
        appState.currentQuestion = questionData;
        
        // UIに反映
        renderQuestion(difficulty, format, questionData);
    } catch (error) {
        showToast(`問題の生成に失敗しました: ${error.message}`, 'error');
        outputPlaceholder.classList.remove('hidden');
        outputLoader.classList.add('hidden');
    } finally {
        generateQuestionBtn.removeAttribute('disabled');
        btnLoader.classList.add('hidden');
    }
}

// 問題の描画
function renderQuestion(difficulty, format, data) {
    outputLoader.classList.add('hidden');
    questionContainer.classList.remove('hidden');

    qDifficulty.textContent = `難易度: ${difficulty}`;
    qFormat.textContent = `形式: ${format}`;

    // UIをすべて非表示にする
    optionsArea.classList.add('hidden');
    textInputArea.classList.add('hidden');
    freeInputArea.classList.add('hidden');
    feedbackArea.classList.add('hidden');
    
    // 解答インプットのリセット
    userAnswerText.value = '';
    userAnswerFree.value = '';
    appState.selectedOption = null;

    // 表示形式の判定
    if (displayFormat.value === 'image') {
        renderAsImage(data);
    } else {
        qText.innerHTML = '';
        qText.textContent = data.question;
        if (window.MathJax?.typesetPromise) {
            window.MathJax.typesetPromise([qText]).catch(() => {});
        }
    }

    if (format === '選択式' && data.options && data.options.length > 0) {
        optionsArea.innerHTML = '';
        optionsArea.classList.remove('hidden');
        
        data.options.forEach(opt => {
            const btn = document.createElement('button');
            btn.className = 'option-btn';
            btn.textContent = opt;
            btn.addEventListener('click', () => selectOption(btn, opt));
            optionsArea.appendChild(btn);
        });
    } else if (format === '記述式') {
        textInputArea.classList.remove('hidden');
    } else {
        // 思考記述式
        freeInputArea.classList.remove('hidden');
    }
}

// 問題文を画像化して描画する処理
async function renderAsImage(data) {
    if (appState.cachedImageDataUrl) {
        qText.innerHTML = '';
        const img = document.createElement('img');
        img.src = appState.cachedImageDataUrl;
        img.className = 'generated-question-image';
        img.alt = '生成された類題（クリックでコピー）';
        img.title = 'クリックでクリップボードにコピー';
        img.style.cursor = 'pointer';
        img.addEventListener('click', () => copyImageToClipboard(appState.cachedImageDataUrl));
        qText.appendChild(img);
        return;
    }

    // ローディングを表示
    qText.innerHTML = `
        <div class="image-loading-placeholder">
            <div class="image-loading-spinner"></div>
            <span>画像を作成中...</span>
        </div>
    `;

    // 隠しコンテナを作成してレンダリング
    const tempDiv = document.createElement('div');
    tempDiv.className = 'question-text';
    const targetWidth = qText.clientWidth || 500;
    tempDiv.style.width = `${targetWidth}px`;
    tempDiv.style.position = 'absolute';
    tempDiv.style.left = '-9999px';
    tempDiv.style.top = '0';
    tempDiv.style.background = '#ffffff'; // 紙のような白背景
    tempDiv.style.color = '#111827'; // ダークグレーのテキスト
    tempDiv.style.padding = '24px';
    tempDiv.style.borderRadius = '12px';
    tempDiv.style.boxSizing = 'border-box';
    tempDiv.style.fontFamily = "'Outfit', 'Noto Sans JP', sans-serif";
    tempDiv.style.fontSize = '1.1rem';
    tempDiv.style.lineHeight = '1.6';
    tempDiv.style.whiteSpace = 'pre-wrap';
    tempDiv.style.fontWeight = '600';
    
    tempDiv.textContent = data.question;
    document.body.appendChild(tempDiv);

    try {
        // MathJax の適用
        if (window.MathJax?.typesetPromise) {
            await window.MathJax.typesetPromise([tempDiv]);
        }

        // レイアウト反映待ち
        await new Promise(resolve => requestAnimationFrame(() => setTimeout(resolve, 150)));

        // キャプチャ
        const canvas = await html2canvas(tempDiv, {
            scale: 2,
            useCORS: true,
            backgroundColor: '#ffffff',
            logging: false,
            width: targetWidth
        });

        const dataUrl = canvas.toDataURL('image/png');
        appState.cachedImageDataUrl = dataUrl;

        qText.innerHTML = '';
        const img = document.createElement('img');
        img.src = dataUrl;
        img.className = 'generated-question-image';
        img.alt = '生成された類題（クリックでコピー）';
        img.title = 'クリックでクリップボードにコピー';
        img.style.cursor = 'pointer';
        img.addEventListener('click', () => copyImageToClipboard(dataUrl));
        qText.appendChild(img);
    } catch (err) {
        console.error('画像化エラー:', err);
        // エラー時はテキスト表示にフォールバック
        qText.innerHTML = '';
        qText.textContent = data.question;
        if (window.MathJax?.typesetPromise) {
            window.MathJax.typesetPromise([qText]).catch(() => {});
        }
    } finally {
        if (document.body.contains(tempDiv)) {
            document.body.removeChild(tempDiv);
        }
    }
}

// 画像のクリップボードへのコピー処理
async function copyImageToClipboard(dataUrl) {
    try {
        const response = await fetch(dataUrl);
        const blob = await response.blob();
        await navigator.clipboard.write([
            new ClipboardItem({ [blob.type]: blob })
        ]);
        showToast('問題を画像としてクリップボードにコピーしました！', 'success');
    } catch (err) {
        console.error('画像コピー失敗', err);
        showToast('画像のコピーに失敗しました。右クリックから保存してください。', 'error');
    }
}

// 選択肢クリック時の処理
function selectOption(selectedBtn, optionText) {
    if (appState.selectedOption !== null) return; // 回答済みなら何もしない

    appState.selectedOption = optionText;
    const buttons = optionsArea.querySelectorAll('.option-btn');
    
    const isCorrect = optionText === appState.currentQuestion.answer;
    
    buttons.forEach(btn => {
        btn.setAttribute('disabled', 'true');
        if (btn.textContent === appState.currentQuestion.answer) {
            btn.classList.add('correct');
        } else if (btn === selectedBtn && !isCorrect) {
            btn.classList.add('incorrect');
        }
    });

    showFeedback(isCorrect, appState.currentQuestion.answer, appState.currentQuestion.explanation);
}

// 記述式解答のチェック
function checkAnswer(userAnswer) {
    // 記述式は多少の表記揺れがあるため、AIではなく簡易チェックと、解説で確認させるスタイルにする
    // または、APIキーがあるのでAIに部分一致判定を投げてもよいですが、ここでは迅速さのために部分一致判定＋AI解説とします
    const correctAnswer = appState.currentQuestion.answer;
    
    // 簡易正規化（大文字小文字、スペース無視など）
    const normalize = str => str.toLowerCase().replace(/\s+/g, '');
    const isCorrect = normalize(userAnswer) === normalize(correctAnswer) || 
                      correctAnswer.toLowerCase().includes(userAnswer.toLowerCase());

    showFeedback(isCorrect, correctAnswer, appState.currentQuestion.explanation);
}

// 思考記述式解答をAIが自己採点する
async function evaluateFreeAnswer(userAnswer) {
    // フィードバックエリアを表示し、ローディングに切り替える
    feedbackArea.classList.remove('hidden');
    feedbackResult.className = 'feedback-result';
    feedbackResult.querySelector('.result-icon').textContent = '🤖';
    feedbackResult.querySelector('.result-text').textContent = 'AIが自己採点中...';
    correctAnswerText.textContent = appState.currentQuestion.answer;
    explanationText.textContent = '評価中...';
    
    const prompt = `ユーザーの解答が模範解答に対して正しいか、または十分な理解を示しているかを評価してください。

【問題文】
${appState.currentQuestion.question}

【模範解答】
${appState.currentQuestion.answer}

【ユーザーの解答】
${userAnswer}

【評価ルール】
正誤（isCorrect）、得点率（score: 0〜100）、およびアドバイスや採点基準を含めたフィードバックコメント（feedbackComment）をJSON形式で返却してください。`;

    const systemInstruction = 'あなたは丁寧で公平な採点官AIです。ユーザーの解答を冷静に分析し、採点結果をJSONで出力してください。';
    
    const responseSchema = {
        type: 'OBJECT',
        properties: {
            isCorrect: { type: 'BOOLEAN', description: '合格点（おおむね60%以上理解している）かどうか。' },
            score: { type: 'INTEGER', description: '採点スコア（0から100点）' },
            feedbackComment: { type: 'STRING', description: '良かった点、改善できる点、模範解答との対比。' }
        },
        required: ['isCorrect', 'score', 'feedbackComment']
    };

    try {
        const responseText = await callAI(prompt, systemInstruction, responseSchema);
        const evalData = JSON.parse(responseText.trim());
        
        feedbackResult.className = `feedback-result ${evalData.isCorrect ? 'correct-style' : 'incorrect-style'}`;
        feedbackResult.querySelector('.result-icon').textContent = evalData.isCorrect ? '✅' : '❌';
        feedbackResult.querySelector('.result-text').textContent = `${evalData.isCorrect ? '合格' : '要学習'} (スコア: ${evalData.score}/100)`;
        
        explanationText.innerHTML = `<strong>AI採点フィードバック:</strong>\n${evalData.feedbackComment}\n\n<strong>元の問題の解説:</strong>\n${appState.currentQuestion.explanation}`;
    } catch (error) {
        showToast(`自己採点に失敗しました: ${error.message}`, 'error');
        feedbackResult.querySelector('.result-text').textContent = '採点エラー';
        explanationText.textContent = `エラーが発生したため自己採点できませんでした。模範解答を確認して自己採点してください。\n\nエラー内容: ${error.message}`;
    }
}

// フィードバック表示
function showFeedback(isCorrect, answer, explanation) {
    feedbackArea.classList.remove('hidden');
    
    feedbackResult.className = `feedback-result ${isCorrect ? 'correct-style' : 'incorrect-style'}`;
    feedbackResult.querySelector('.result-icon').textContent = isCorrect ? '✅' : '❌';
    feedbackResult.querySelector('.result-text').textContent = isCorrect ? '正解！' : '不正解';
    
    correctAnswerText.textContent = answer;
    explanationText.textContent = explanation;
    
    // スムーズスクロール
    feedbackArea.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// 7. ユーティリティ関数
function formatBytes(bytes, decimals = 2) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

function showToast(message, type = 'success') {
    toast.textContent = message;
    toast.className = `toast ${type}`;
    toast.classList.remove('hidden');

    setTimeout(() => {
        toast.classList.add('hidden');
    }, 4000);
}
