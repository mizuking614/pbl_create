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
const customTopicInput = document.getElementById('customTopicInput');
const addCustomTopicBtn = document.getElementById('addCustomTopicBtn');
const generationModeSelect = document.getElementById('generationModeSelect');
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
const showAnswerBtn = document.getElementById('showAnswerBtn');
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
const questionCountInput = document.getElementById('questionCountInput');
const prevQuestionBtn = document.getElementById('prevQuestionBtn');
const nextNavQuestionBtn = document.getElementById('nextNavQuestionBtn');
const questionProgress = document.getElementById('questionProgress');
const resultScreen = document.getElementById('resultScreen');
const resultScore = document.getElementById('resultScore');
const resultTotal = document.getElementById('resultTotal');
const resultDetails = document.getElementById('resultDetails');
const restartExerciseBtn = document.getElementById('restartExerciseBtn');
const createNewQuestionsBtn = document.getElementById('createNewQuestionsBtn');

// --- タブ切り替えUI ---
const tabBtnExercise = document.getElementById('tabBtnExercise');
const tabBtnPlanner = document.getElementById('tabBtnPlanner');
const exerciseView = document.getElementById('exerciseView');
const plannerView = document.getElementById('plannerView');

// --- 学習計画プランナーUI ---
const plannerGoalInput = document.getElementById('plannerGoalInput');
const plannerTargetInput = document.getElementById('plannerTargetInput');
const plannerDeadlineInput = document.getElementById('plannerDeadlineInput');
const plannerAssignmentCount = document.getElementById('plannerAssignmentCount');
const plannerAssignmentDeadline = document.getElementById('plannerAssignmentDeadline');
const plannerAssignmentFilterDate = document.getElementById('plannerAssignmentFilterDate');
const manualAssignTitle = document.getElementById('manualAssignTitle');
const manualAssignDate = document.getElementById('manualAssignDate');
const manualAssignDuration = document.getElementById('manualAssignDuration');
const addManualAssignBtn = document.getElementById('addManualAssignBtn');
const manualAssignmentsList = document.getElementById('manualAssignmentsList');
const plannerTopicDuration = document.getElementById('plannerTopicDuration');
const importModeIcalBtn = document.getElementById('importModeIcalBtn');
const importModeManualBtn = document.getElementById('importModeManualBtn');
const icalInputArea = document.getElementById('icalInputArea');
const manualInputArea = document.getElementById('manualInputArea');
const plannerIcalUrl = document.getElementById('plannerIcalUrl');
const syncIcalBtn = document.getElementById('syncIcalBtn');
const icalStatusMessage = document.getElementById('icalStatusMessage');
const syncedAssignmentsList = document.getElementById('syncedAssignmentsList');
const addPlannerTopicBtn = document.getElementById('addPlannerTopicBtn');
const plannerTopicInput = document.getElementById('plannerTopicInput');
const plannerTopicsList = document.getElementById('plannerTopicsList');
const createPlanBtn = document.getElementById('createPlanBtn');
const rescheduleBtn = document.getElementById('rescheduleBtn');
const plannerOutputArea = document.getElementById('plannerOutputArea');
const plannerPlaceholder = document.getElementById('plannerPlaceholder');
const plannerLoader = document.getElementById('plannerLoader');
const plannerLoaderMessage = document.getElementById('plannerLoaderMessage');
const planDashboard = document.getElementById('planDashboard');
const todayTasksList = document.getElementById('todayTasksList');
const roadmapTimeline = document.getElementById('roadmapTimeline');
const weeklyScheduleGrid = document.getElementById('weeklyScheduleGrid');

// 週間学習リソース（各曜日）
const resourceMon = document.getElementById('resourceMon');
const resourceTue = document.getElementById('resourceTue');
const resourceWed = document.getElementById('resourceWed');
const resourceThu = document.getElementById('resourceThu');
const resourceFri = document.getElementById('resourceFri');
const resourceSat = document.getElementById('resourceSat');
const resourceSun = document.getElementById('resourceSun');

// アプリケーション状態
let appState = {
    apiKey: '',
    uploadedText: '',
    extractedTopics: [],
    selectedTopics: [],
    questionsList: [],
    userAnswers: [],
    currentQuestionIndex: 0,
    currentQuestion: null,
    selectedOption: null,
    cachedImageDataUrl: null,
    // 学習計画プランナーの状態
    plannerTopics: [], // [{ name: "完全形", duration: 60 }] 形式で保存されます
    plannerPlan: JSON.parse(localStorage.getItem('planner_plan')) || null,
    icalUrl: localStorage.getItem('planner_ical_url') || '',
    icalAssignments: JSON.parse(localStorage.getItem('planner_ical_assignments')) || [],
    manualAssignments: JSON.parse(localStorage.getItem('planner_manual_assignments')) || [],
    assignmentFilterDate: localStorage.getItem('planner_assignment_filter_date') || '',
    importMode: localStorage.getItem('planner_import_mode') || 'ical'
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
    
    // デフォルト期限日（1週間後）を期限カレンダーに設定
    const todayStr = new Date();
    const oneWeekLater = new Date(todayStr.getTime() + 7 * 24 * 60 * 60 * 1000);
    plannerDeadlineInput.value = oneWeekLater.toISOString().split('T')[0];
    if (plannerAssignmentDeadline) {
        plannerAssignmentDeadline.value = oneWeekLater.toISOString().split('T')[0];
    }
    plannerAssignmentFilterDate.value = oneWeekLater.toISOString().split('T')[0];
    manualAssignDate.value = oneWeekLater.toISOString().split('T')[0];

    // 既存のiCalデータ・表示モードの復元
    if (appState.icalUrl && plannerIcalUrl) {
        plannerIcalUrl.value = appState.icalUrl;
    }
    if (appState.assignmentFilterDate && plannerAssignmentFilterDate) {
        plannerAssignmentFilterDate.value = appState.assignmentFilterDate;
    }
    toggleImportMode(appState.importMode);
    renderSyncedAssignments();
    renderManualAssignments();

    // ローカルストレージに既存の計画があれば復元
    if (appState.plannerPlan) {
        renderPlannerDashboard();
    }

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

    // カスタムトピック追加
    addCustomTopicBtn.addEventListener('click', () => {
        const topic = customTopicInput.value.trim();
        if (topic) {
            if (!appState.extractedTopics.includes(topic)) {
                appState.extractedTopics.push(topic);
            }
            if (!appState.selectedTopics.includes(topic)) {
                appState.selectedTopics.push(topic);
            }
            customTopicInput.value = '';
            renderTopics();
            updateGenerateButtonState();
        }
    });
    customTopicInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            addCustomTopicBtn.click();
        }
    });

    // 類題生成実行
    generateQuestionBtn.addEventListener('click', generateQuestion);

    // 次の問題ボタン
    nextQuestionBtn.addEventListener('click', handleNextQuestion);

    // ナビゲーションボタン
    prevQuestionBtn.addEventListener('click', () => {
        if (appState.currentQuestionIndex > 0) {
            showQuestion(appState.currentQuestionIndex - 1);
        }
    });

    nextNavQuestionBtn.addEventListener('click', handleNextQuestion);

    // リザルト画面アクション
    restartExerciseBtn.addEventListener('click', () => {
        appState.userAnswers = new Array(appState.questionsList.length).fill(null);
        showQuestion(0);
    });

    createNewQuestionsBtn.addEventListener('click', () => {
        resultScreen.classList.add('hidden');
        appState.questionsList = [];
        appState.userAnswers = [];
        appState.currentQuestionIndex = 0;
        outputPlaceholder.classList.remove('hidden');
    });

    // 記述式解答の自己開示
    if (showAnswerBtn) {
        showAnswerBtn.addEventListener('click', () => {
            revealDescriptiveAnswer();
        });
    }

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

    // === タブ切り替え制御 ===
    tabBtnExercise.addEventListener('click', () => {
        tabBtnExercise.classList.add('active');
        tabBtnPlanner.classList.remove('active');
        exerciseView.classList.remove('hidden');
        plannerView.classList.add('hidden');
    });

    tabBtnPlanner.addEventListener('click', () => {
        tabBtnPlanner.classList.add('active');
        tabBtnExercise.classList.remove('active');
        plannerView.classList.remove('hidden');
        exerciseView.classList.add('hidden');
    });

    // === プランナートピック管理 ===
    addPlannerTopicBtn.addEventListener('click', () => {
        const topicName = plannerTopicInput.value.trim();
        const duration = parseInt(plannerTopicDuration.value) || 60;
        if (topicName) {
            const exists = appState.plannerTopics.some(t => t.name === topicName);
            if (!exists) {
                appState.plannerTopics.push({ name: topicName, duration: duration });
            }
            plannerTopicInput.value = '';
            renderPlannerTopics();
        }
    });

    plannerTopicInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            addPlannerTopicBtn.click();
        }
    });

    // === 手動課題の追加・管理 ===
    addManualAssignBtn.addEventListener('click', () => {
        const title = manualAssignTitle.value.trim();
        const date = manualAssignDate.value;
        const duration = parseInt(manualAssignDuration.value) || 90;
        
        if (!title) {
            showToast('課題名を入力してください。', 'error');
            return;
        }
        if (!date) {
            showToast('締め切り期限を設定してください。', 'error');
            return;
        }

        const newAssign = {
            id: 'manual_' + Date.now(),
            summary: title,
            dueDate: date,
            duration: duration
        };

        appState.manualAssignments.push(newAssign);
        localStorage.setItem('planner_manual_assignments', JSON.stringify(appState.manualAssignments));
        
        manualAssignTitle.value = '';
        renderManualAssignments();
        showToast('手動課題を追加しました。', 'success');
    });

    plannerAssignmentFilterDate.addEventListener('change', () => {
        appState.assignmentFilterDate = plannerAssignmentFilterDate.value;
        localStorage.setItem('planner_assignment_filter_date', appState.assignmentFilterDate);
        renderSyncedAssignments();
        renderManualAssignments();
    });

    // === 課題インポートモード切り替え ===
    importModeIcalBtn.addEventListener('click', () => toggleImportMode('ical'));
    importModeManualBtn.addEventListener('click', () => toggleImportMode('manual'));

    // === カレンダー同期 ===
    syncIcalBtn.addEventListener('click', syncIcalCalendar);

    // === プランナー生成およびリスケジュール ===
    createPlanBtn.addEventListener('click', generateStudyPlan);
    rescheduleBtn.addEventListener('click', rescheduleStudyPlan);
}

// 3. ファイル読み込み処理
async function handleFile(file) {
    // 読込制限
    const MAX_SIZE = 20 * 1024 * 1024; // 20MB
    if (file.size > MAX_SIZE) {
        showToast('ファイルサイズが大きすぎます。20MB以下のファイルを選択してください。', 'error');
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
            // クライアント側でPDFからテキストを抽出 (pdf.js使用)
            const arrayBuffer = await file.arrayBuffer();
            let pdf;
            try {
                pdf = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;
                let fullText = '';
                for (let i = 1; i <= pdf.numPages; i++) {
                    const page = await pdf.getPage(i);
                    const textContent = await page.getTextContent();
                    const pageText = textContent.items.map(item => item.str).join(' ');
                    if (pageText.trim()) {
                        fullText += `--- page ${i} ---\n${pageText}\n\n`;
                    }
                }
                text = fullText;
                if (!text.trim()) {
                    console.warn('PDFからテキストを抽出できませんでした。スキャン画像化されたPDFとみなしてGeminiに処理を委ねます。');
                }
            } catch (err) {
                throw new Error('PDFの解析に失敗しました: ' + err.message);
            }

            // Geminiマルチモーダル受信用にBase64版も保持
            const blob = new Blob([arrayBuffer], { type: 'application/pdf' });
            const dataUrl = await new Promise((resolve) => {
                const reader = new FileReader();
                reader.onload = (e) => resolve(e.target.result);
                reader.readAsDataURL(blob);
            });

            // PDFの各ページをJPEG画像（データURL）にレンダリングして保存
            const pageImages = await renderPdfPagesToImages(pdf);

            appState.uploadedFile = {
                data: dataUrl,
                mimeType: 'application/pdf',
                type: 'pdf',
                name: file.name,
                pages: pageImages
            };
        } else if (file.type.startsWith('image/')) {
            const dataUrl = await new Promise((resolve) => {
                const reader = new FileReader();
                reader.onload = (e) => resolve(e.target.result);
                reader.readAsDataURL(file);
            });
            appState.uploadedFile = {
                data: dataUrl,
                mimeType: file.type,
                type: 'image',
                name: file.name
            };
            text = '画像ファイルがアップロードされました。画像から直接問題を生成します。';
            
            const imagePreview = document.getElementById('imagePreview');
            const imagePreviewContainer = document.getElementById('imagePreviewContainer');
            if (imagePreview && imagePreviewContainer) {
                imagePreview.src = dataUrl;
                imagePreviewContainer.classList.remove('hidden');
            }
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
    if (appState.uploadedText.trim().length > 10 || (appState.uploadedFile && (appState.uploadedFile.type === 'image' || appState.uploadedFile.type === 'pdf'))) {
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

    if (appState.uploadedFile) {
        if (appState.uploadedFile.type === 'pdf' && appState.uploadedFile.pages) {
            appState.uploadedFile.pages.forEach(dataUrl => {
                const base64Data = dataUrl.split(',')[1];
                requestBody.contents[0].parts.push({
                    inlineData: {
                        mimeType: 'image/jpeg',
                        data: base64Data
                    }
                });
            });
        } else if (appState.uploadedFile.data) {
            const base64Data = appState.uploadedFile.data.split(',')[1];
            requestBody.contents[0].parts.push({
                inlineData: {
                    mimeType: appState.uploadedFile.mimeType,
                    data: base64Data
                }
            });
        }
    }

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
    
    // ユーザーメッセージをマルチモーダル（画像＋テキスト）構成にする
    const userContent = [{ type: 'text', text: prompt }];
    
    if (appState.uploadedFile) {
        if (appState.uploadedFile.type === 'image' && appState.uploadedFile.data) {
            userContent.push({
                type: 'image_url',
                image_url: {
                    url: appState.uploadedFile.data
                }
            });
        } else if (appState.uploadedFile.type === 'pdf' && appState.uploadedFile.pages) {
            appState.uploadedFile.pages.forEach(dataUrl => {
                userContent.push({
                    type: 'image_url',
                    image_url: {
                        url: dataUrl
                    }
                });
            });
        }
    }
    
    messages.push({ role: 'user', content: userContent });

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

    const prompt = `提供された学習資料（テキストまたは画像）を詳細に分析し、この資料の主要なテーマ（授業の単元名、主要な公式、解法手法など）を優先的かつ大局的な視点から最大10個抽出してください。
抽出時の注意点：
- 資料の大部分を占める大きな主題・テーマ（例：「微分方程式」「特性方程式」「定数係数線形常微分方程式」「行列の積」など）を最優先で、漏れなく抽出してください。
- 「多項式 P(x)」のような細部の要素や一時的な数式、部分的な概念も抽出して構いませんが、それらが大元の大きな主題を差し置いて優先されたり、主要トピックが埋もれてしまったりしないように、バランス良く重み付けして抽出してください。
- 画像がある場合は、スライドのタイトルや大きく目立つ文字、中心となる数式から大元の主要テーマを推測してください。
- 出力は、タグ名としてふさわしい具体的で簡潔な日本語のキーワード（15文字以内）の配列にしてください。`;

    const systemInstruction = 'あなたは講義資料を分析し、学習者が演習すべき主要なトピック（単元名・公式・解法名などの大局的な主題を優先）を抽出する専門の教育AIアシスタントです。細部の数式やサブ概念も許容しますが、常に資料の大元の大きな主題が中心となるようにバランス良く抽出してください。';
    
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
        if (appState.selectedTopics.includes(topic)) {
            chip.classList.add('selected');
        }
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
    const mode = generationModeSelect ? generationModeSelect.value : 'similar';
    const count = parseInt(questionCountInput.value, 10) || 3;
    appState.cachedImageDataUrl = null;
    
    // UI表示の切り替え
    outputPlaceholder.classList.add('hidden');
    questionContainer.classList.add('hidden');
    feedbackArea.classList.add('hidden');
    resultScreen.classList.add('hidden');
    outputLoader.classList.remove('hidden');
    
    const btnLoader = generateQuestionBtn.querySelector('.btn-loader');
    generateQuestionBtn.setAttribute('disabled', 'true');
    btnLoader.classList.remove('hidden');

    let contentPrompt = appState.uploadedText ? `\n【学習資料のテキスト】\n${appState.uploadedText}` : '';
    if (appState.uploadedFile && (appState.uploadedFile.type === 'image' || appState.uploadedFile.type === 'pdf')) {
        contentPrompt += `\n(※添付された画像/PDFファイルも参照してください)`;
    }

    let instructionText = '';
    if (mode === 'exact') {
        instructionText = `以下の【学習資料】の中にある問題や重要な内容をそのまま抽出して、${count}問 の問題として出力してください。\n数値を変更したり、新しい設定を作ったり類題にしたりしないでください。資料の通りの問題を抽出・作成してください。\n画像の中に数式が含まれている場合は、それらを正確にLaTeX記法で書き起こしてください。`;
    } else if (mode === 'create_from_materials') {
        instructionText = `以下の【学習資料】（公式、解説、用語など）を詳細に分析し、ユーザーがその内容を理解できているかを確認するための基礎的な練習問題を ${count}問 作成してください。\n資料に元の問題が含まれていなくても、記載されている公式や概念を使った問題を独自に作成してください。`;
    } else {
        instructionText = `以下の【学習資料】にある問題をもとに、指定された【選択トピック】に関連する類題（練習問題）を ${count}問 作成してください。数値を変更したり応用を効かせた問題を含めてください。`;
    }

    const prompt = `${instructionText}

${contentPrompt}

【選択トピック】
${appState.selectedTopics.length > 0 ? appState.selectedTopics.join(', ') : '資料全体から重要なトピック'}

【問題の難易度】
${difficulty}

【問題の形式】
${format === '選択式' ? '4択の多肢選択式' : format === '記述式' ? '記述式（計算結果や穴埋め、短い言葉で答える問題）' : '思考記述式（考えや計算プロセスを自由に説明させる問題）'}

【出力内容の要件】
- 多肢選択式（選択式）の場合:
  - options配列に必ず4つの選択肢を入れてください（例: ["選択肢Aのテキスト", "選択肢Bの...", ...]）。
  - 問題文（question）の中には、絶対に選択肢（A:, B: などの選択肢の文字列）を含めないでください。選択肢はoptions配列の中だけで管理・出力します。
  - answerは正解の選択肢の文字列（options配列内の正解の文字列と完全に同一のもの）を記述してください。
- 記述式の場合: optionsは必ず空配列（[]）にしてください。answerは想定される正解（計算の答えやキーワード）を入れてください。
- 思考記述式の場合: optionsは必ず空配列（[]）にしてください。answerは模範解答や導出プロセスを記述してください。
- 行列、積分、その他数式が必要な場合は LaTeX 記法（\`$$ ... $$\` または \`$ ... $\`）を使用してください。
- 物理の図（力学、回路、光学など）や数学のグラフ・図形が必要な場合は、問題文(question)の中に必ず XMLブロック (\`\`\`xml または \`\`\`svg) を用いて SVG (\`<svg viewBox="..." xmlns="http://www.w3.org/2000/svg">...\`) を出力してください。線は見やすいように暗黙の黒ではなく、適切な色かスタイルを指定して綺麗に描画してください。

【解説（explanation）の要件】
- 問題の解き方や背景知識に関する詳細な解説を記述してください。
- 途中式、変数変換（例: ベルヌイ型微分方程式における $u = y^{1-n}$ の置換ステップなど）、計算プロセス、使用した公式を一切省略せずに、段階を追って詳しく記述してください。
- 物理の回路図や数学のグラフがある場合は、図のどの要素に注目して式を立てるかについても丁寧に説明してください。文字数を十分に使い、学習者が自習できるレベルで詳しく解説してください。

【資料参照の厳密ルール】
- 選択されたトピックが手動で追加されたキーワードであっても、必ず【学習資料】（スライド画像やテキスト）に書かれている解法の流儀や公式、難易度、出題範囲をベースに問題を作成してください。資料と関係のない一般的な問題や、資料で扱っていない高度な解法が必要な問題は絶対に避けてください。`;

    const systemInstruction = `あなたは優秀な物理・数学の教育AIアシスタントです。提供された学習資料とトピックに基づき、指定されたJSONフォーマットに従って精度の高い問題を作成してください。
特に物理（力学の斜面や滑車、電気回路、光学、波動のグラフ等）や幾何学などで視覚的な図が必要な場合は、問題文(question)の中に必ず美しいSVG画像を XMLコードブロック (\`\`\`xml ... \`\`\`) として埋め込んでください。

【SVG図面生成のガイドライン】
- viewBoxを適切に設定し、レスポンシブで崩れないようにしてください。
- 線の色は暗黙の黒ではなく、コントラストがはっきりした色（基本線: #1f2937、補助線・矢印: #ef4444 や #3b82f6 など）を明示的に指定してください。
- オブジェクト（台、物体、ばね、抵抗など）には美しい塗りと境界線を施してください。背景は白（#ffffff）のカードに合うようにしてください。
- 物理量（力 F、重力 mg、角度 θ など）の文字も SVG内の <text> タグを使い、適切な位置に配置してください。
- 矢印を描く際はマーカー（marker）を定義するか、polygon等で矢印の先端を綺麗に描写してください。

【力学の斜面の記述例】:
\`\`\`xml
<svg viewBox="0 0 300 200" xmlns="http://www.w3.org/2000/svg" style="background:#ffffff; border-radius:8px;">
  <!-- 矢印マーカーの定義 -->
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#ef4444" />
    </marker>
  </defs>
  <!-- 斜面台 -->
  <polygon points="40,160 260,160 260,60" fill="#f3f4f6" stroke="#1f2937" stroke-width="2"/>
  <!-- 斜面上の物体 -->
  <rect x="120" y="95" width="45" height="30" transform="rotate(-21.8 142.5 110)" fill="#3b82f6" stroke="#1f2937" stroke-width="2"/>
  <!-- 重力矢印 -->
  <line x1="142" y1="110" x2="142" y2="155" stroke="#ef4444" stroke-width="2.5" marker-end="url(#arrow)"/>
  <text x="150" y="145" fill="#ef4444" font-size="12" font-weight="bold">mg</text>
  <!-- 斜面角度θ -->
  <path d="M 60 160 A 20 20 0 0 1 58 152" fill="none" stroke="#1f2937" stroke-width="1.5"/>
  <text x="65" y="155" fill="#1f2937" font-size="12">θ</text>
</svg>
\`\`\`
上記の例を参考に、出題トピック（力学、電気回路、波動、グラフ等）に応じた適切な図面を自前で設計し、XMLコードブロックで出力してください。`;
    
    // JSON Schema定義 (配列対応)
    const responseSchema = {
        type: 'ARRAY',
        description: '生成された問題のリスト',
        items: {
            type: 'OBJECT',
            properties: {
                question: { type: 'STRING', description: '問題文。マークダウン形式でも可。問題文のみを書き、選択肢は含めないでください。' },
                options: { 
                    type: 'ARRAY', 
                    description: '多肢選択式の場合の4つの選択肢。それ以外は空配列。',
                    items: { type: 'STRING' } 
                },
                answer: { type: 'STRING', description: '正解または模範解答。選択式の場合はoptions内のいずれかの文字列。' },
                explanation: { type: 'STRING', description: '問題の解き方や背景知識に関する詳細な解説。' }
            },
            required: ['question', 'options', 'answer', 'explanation']
        }
    };

    try {
        const responseText = await callAI(prompt, systemInstruction, responseSchema);
        let questionsData = JSON.parse(responseText.trim());
        // 配列でない場合は配列にする
        if (!Array.isArray(questionsData)) {
            if (questionsData.items) questionsData = questionsData.items;
            else questionsData = [questionsData];
        }

        // --- 二段階校閲（検算・セルフチェック）フェーズの追加 ---
        try {
            loaderMessage.textContent = 'AIが問題を検算・校正しています... 🔍';
            
            const verifyPrompt = `あなたは厳格な数学・物理の校閲専門家です。
AIが作成した以下の問題リストを詳細に検算し、問題文、解答、解説に数学的・物理学的な計算ミスや矛盾（プラス・マイナスの符号ミス、定数の計算ミス、解説と答えの不一致など）がないか厳密に確認・修正してください。

【検証対象の問題リスト】
${JSON.stringify(questionsData, null, 2)}

【校閲・検算の指示】
- 各問題の数式を実際にステップごとに解き、解答と解説が数学的に100%正しいか検証してください。
- 符号の誤りや定数の計算ミス、解説と解答の不一致があれば、解説または解答（必要なら問題文）を数学的に正しい内容に修正してください。
- 問題文中の XMLブロック (\`\`\`xml や \`\`\`svg) のSVGコードは、タグの閉じ忘れ等のエラーを修復し、より美しく見やすい図面になるように調整・清書してください。図自体を消去しないでください。
- 出力は必ず指定のJSON形式で、検証・修正済みの問題リストのみを返却してください。`;

            const verifySystemInstruction = 'あなたは数学・物理の計算の正確性を極限まで高める校閲・検算AIアシスタントです。問題文中のSVG図面コードの構文エラーも修復し、修正後のJSONのみを返却してください。';

            const verifiedResponseText = await callAI(verifyPrompt, verifySystemInstruction, responseSchema);
            let verifiedQuestionsData = JSON.parse(verifiedResponseText.trim());

            if (!Array.isArray(verifiedQuestionsData)) {
                if (verifiedQuestionsData.items) verifiedQuestionsData = verifiedQuestionsData.items;
                else verifiedQuestionsData = [verifiedQuestionsData];
            }
            // 検算・修正済みのデータを採用
            questionsData = verifiedQuestionsData;
        } catch (verifyError) {
            console.warn('検算・校正処理でエラーが発生したため、一次生成データを採用します:', verifyError);
        }

        appState.questionsList = questionsData;
        appState.userAnswers = new Array(questionsData.length).fill(null);
        appState.currentQuestionIndex = 0;
        
        showQuestion(0);
    } catch (error) {
        showToast(`問題の生成に失敗しました: ${error.message}`, 'error');
        outputPlaceholder.classList.remove('hidden');
        outputLoader.classList.add('hidden');
    } finally {
        generateQuestionBtn.removeAttribute('disabled');
        btnLoader.classList.add('hidden');
    }
}

// 質問ナビゲーション表示
function showQuestion(index) {
    if (index < 0 || index >= appState.questionsList.length) return;
    
    appState.currentQuestionIndex = index;
    appState.currentQuestion = appState.questionsList[index];
    appState.cachedImageDataUrl = null;
    
    questionProgress.textContent = `問題 ${index + 1} / ${appState.questionsList.length}`;
    
    // ボタンの有効無効
    prevQuestionBtn.disabled = index === 0;
    
    const difficulty = difficultySelect.value;
    const format = formatSelect.value;
    
    // 既存の解答があればフィードバックを表示状態にするかリセット
    renderQuestion(difficulty, format, appState.currentQuestion);
    
    const previousAnswer = appState.userAnswers[index];
    if (previousAnswer) {
        // すでに回答済みの場合
        if (showAnswerBtn) showAnswerBtn.disabled = true;
        showFeedback(previousAnswer.isCorrect, appState.currentQuestion.answer, appState.currentQuestion.explanation, previousAnswer);
        updateNextQuestionBtnLabel();
    } else {
        if (showAnswerBtn) showAnswerBtn.disabled = false;
        feedbackArea.classList.add('hidden');
        updateNextQuestionBtnLabel();
    }
}

function updateNextQuestionBtnLabel() {
    const isLast = appState.currentQuestionIndex === appState.questionsList.length - 1;
    nextQuestionBtn.textContent = isLast ? '結果を見る' : '次の問題へ';
    nextNavQuestionBtn.textContent = isLast ? '結果を見る' : '次へ →';
    nextNavQuestionBtn.disabled = false;
}

function handleNextQuestion() {
    if (appState.currentQuestionIndex < appState.questionsList.length - 1) {
        showQuestion(appState.currentQuestionIndex + 1);
    } else {
        showResultScreen();
    }
}

function showResultScreen() {
    questionContainer.classList.add('hidden');
    feedbackArea.classList.add('hidden');
    resultScreen.classList.remove('hidden');
    
    const total = appState.questionsList.length;
    const correctCount = appState.userAnswers.filter(ans => ans && ans.isCorrect).length;
    
    resultScore.textContent = correctCount;
    resultTotal.textContent = total;
    
    resultDetails.innerHTML = appState.questionsList.map((q, idx) => {
        const ans = appState.userAnswers[idx];
        const isCorrect = ans ? ans.isCorrect : false;
        const statusBadge = isCorrect ? '<span class="result-item-badge correct">正解</span>' : '<span class="result-item-badge incorrect">不正解</span>';
        
        const qTextShort = q.question.length > 50 ? q.question.substring(0, 50) + '...' : q.question;
        return `
            <div class="result-item" style="cursor: pointer;" onclick="viewQuestionFromSummary(${idx})">
                <span class="result-item-q" title="クリックでこの問題へ移動">問 ${idx + 1}: ${qTextShort}</span>
                ${statusBadge}
            </div>
        `;
    }).join('');
}

window.viewQuestionFromSummary = function(index) {
    resultScreen.classList.add('hidden');
    questionContainer.classList.remove('hidden');
    showQuestion(index);
};

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
    if (showAnswerBtn) showAnswerBtn.disabled = false;
    userAnswerFree.value = '';
    appState.selectedOption = null;

    // 表示形式の判定
    if (displayFormat.value === 'image') {
        renderAsImage(data);
    } else {
        qText.innerHTML = '';
        renderParsedContent(data.question, qText);
    }

    if (format === '選択式' && data.options && data.options.length > 0) {
        optionsArea.innerHTML = '';
        optionsArea.classList.remove('hidden');
        
        data.options.forEach(opt => {
            const btn = document.createElement('button');
            btn.className = 'option-btn';
            
            // 数式やテキストをパース描画
            renderParsedContent(opt, btn);
            
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
    
    // 先にDOMに追加することで、MathJaxのレンダリング時にフォントサイズやレイアウトが正しく計算されるようにする
    document.body.appendChild(tempDiv);

    // コンテンツのパースとレンダリング
    await renderParsedContent(data.question, tempDiv);

    // 選択式の場合、選択肢も画像に含める
    const format = formatSelect.value;
    if (format === '選択式' && data.options && data.options.length > 0) {
        const optContainer = document.createElement('div');
        optContainer.className = 'options-image-container';
        optContainer.style.marginTop = '20px';
        optContainer.style.display = 'flex';
        optContainer.style.flexDirection = 'column';
        optContainer.style.gap = '10px';
        
        for (const opt of data.options) {
            const optDiv = document.createElement('div');
            optDiv.className = 'option-image-item';
            optDiv.style.border = '1px solid #e5e7eb';
            optDiv.style.borderRadius = '8px';
            optDiv.style.padding = '12px 16px';
            optDiv.style.background = '#f9fafb';
            optDiv.style.color = '#1f2937';
            optDiv.style.fontWeight = '500';
            optDiv.style.textAlign = 'left';
            
            // 数式パース処理を適用
            await renderParsedContent(opt, optDiv);
            optContainer.appendChild(optDiv);
        }
        tempDiv.appendChild(optContainer);
    }

    try {
        // レイアウト反映待ち
        await new Promise(resolve => requestAnimationFrame(() => setTimeout(resolve, 150)));

        // スクリーンリーダー用の非表示数式テキスト（mjx-assistive-mml）がhtml2canvasで二重描画されるのを防ぐため削除する
        tempDiv.querySelectorAll('mjx-assistive-mml').forEach(el => el.remove());

        // SVGを画像（img）タグに置換して、html2canvasがviewBoxや相対単位を誤解するバグを完全に回避する
        tempDiv.querySelectorAll('svg').forEach(svg => {
            const rect = svg.getBoundingClientRect();
            let width = rect.width;
            let height = rect.height;
            
            // フォールバック: オフスクリーンなどでサイズが0の場合、属性値から計算する
            if (width === 0 || height === 0) {
                const attrWidth = svg.getAttribute('width');
                const attrHeight = svg.getAttribute('height');
                const fontSize = parseFloat(window.getComputedStyle(svg).fontSize) || 16;
                const exPx = fontSize * 0.45; // 1ex ≈ 0.45 * fontSize の近似値
                
                if (attrWidth && (attrWidth.endsWith('ex') || attrWidth.endsWith('em'))) {
                    const unit = attrWidth.endsWith('ex') ? exPx : fontSize;
                    width = parseFloat(attrWidth) * unit;
                } else if (attrWidth) {
                    width = parseFloat(attrWidth);
                }
                
                if (attrHeight && (attrHeight.endsWith('ex') || attrHeight.endsWith('em'))) {
                    const unit = attrHeight.endsWith('ex') ? exPx : fontSize;
                    height = parseFloat(attrHeight) * unit;
                } else if (attrHeight) {
                    height = parseFloat(attrHeight);
                }
                
                // それでも0なら viewBox から推測する
                if (width === 0 || height === 0) {
                    const viewBox = svg.getAttribute('viewBox');
                    if (viewBox) {
                        const vbParts = viewBox.trim().split(/\s+/);
                        if (vbParts.length === 4) {
                            const vbWidth = parseFloat(vbParts[2]);
                            const vbHeight = parseFloat(vbParts[3]);
                            if (vbWidth && vbHeight) {
                                // アスペクト比を保ちつつデフォルト幅にする
                                width = 120;
                                height = (vbHeight / vbWidth) * 120;
                            }
                        }
                    }
                }
                
                // 最終フォールバック
                if (width === 0 || height === 0) {
                    width = 100;
                    height = 30;
                }
            }

            if (width && height) {
                // 1. インラインスタイルのwidth/heightを削除し、直値属性に強制する
                svg.style.removeProperty('width');
                svg.style.removeProperty('height');
                svg.setAttribute('width', width);
                svg.setAttribute('height', height);
                
                try {
                    const serializer = new XMLSerializer();
                    const svgString = serializer.serializeToString(svg);
                    // URLエンコード方式に変更（btoaのマルチバイトエラーを防ぎ、よりシンプル・安全に）
                    const encodedSvg = encodeURIComponent(svgString);
                    
                    const img = document.createElement('img');
                    img.src = 'data:image/svg+xml;charset=utf-8,' + encodedSvg;
                    img.style.width = width + 'px';
                    img.style.height = height + 'px';
                    img.style.display = 'inline-block';
                    img.style.verticalAlign = 'middle';
                    img.style.margin = svg.style.margin;
                    img.className = svg.className;
                    
                    svg.parentNode.replaceChild(img, svg);
                } catch (e) {
                    console.warn('SVGのimg置換に失敗しました:', e);
                }
            }
        });

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
    if (appState.userAnswers[appState.currentQuestionIndex]) return; // 回答済みなら何もしない

    appState.selectedOption = optionText;
    const buttons = optionsArea.querySelectorAll('.option-btn');
    
    const isCorrect = optionText === appState.currentQuestion.answer;
    
    appState.userAnswers[appState.currentQuestionIndex] = {
        isCorrect: isCorrect,
        userAnswer: optionText,
        resultText: isCorrect ? '正解！' : '不正解',
        feedbackComment: null
    };
    
    buttons.forEach(btn => {
        btn.setAttribute('disabled', 'true');
        if (btn.textContent === appState.currentQuestion.answer) {
            btn.classList.add('correct');
        } else if (btn === selectedBtn && !isCorrect) {
            btn.classList.add('incorrect');
        }
    });

    showFeedback(isCorrect, appState.currentQuestion.answer, appState.currentQuestion.explanation);
    updateNextQuestionBtnLabel();
}

// 記述式解答のチェック
function checkAnswer(userAnswer) {
    const correctAnswer = appState.currentQuestion.answer;
    
    // 簡易正規化
    const normalize = str => str.toLowerCase().replace(/\s+/g, '');
    const isCorrect = normalize(userAnswer) === normalize(correctAnswer) || 
                      correctAnswer.toLowerCase().includes(userAnswer.toLowerCase());

    appState.userAnswers[appState.currentQuestionIndex] = {
        isCorrect: isCorrect,
        userAnswer: userAnswer,
        resultText: isCorrect ? '正解！' : '不正解',
        feedbackComment: null
    };

    userAnswerText.disabled = true;
    submitTextAnswerBtn.disabled = true;

    showFeedback(isCorrect, correctAnswer, appState.currentQuestion.explanation);
    updateNextQuestionBtnLabel();
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
        
        appState.userAnswers[appState.currentQuestionIndex] = {
            isCorrect: evalData.isCorrect,
            userAnswer: userAnswer,
            resultText: evalData.isCorrect ? '合格' : '要学習',
            feedbackComment: evalData.feedbackComment,
            score: evalData.score
        };

        feedbackResult.className = `feedback-result ${evalData.isCorrect ? 'correct-style' : 'incorrect-style'}`;
        feedbackResult.querySelector('.result-icon').textContent = evalData.isCorrect ? '✅' : '❌';
        feedbackResult.querySelector('.result-text').textContent = `${evalData.isCorrect ? '合格' : '要学習'} (スコア: ${evalData.score}/100)`;
        
        explanationText.innerHTML = `<strong>AI採点フィードバック:</strong>\n${evalData.feedbackComment}\n\n<strong>元の問題の解説:</strong>\n${appState.currentQuestion.explanation}`;
        updateNextQuestionBtnLabel();
    } catch (error) {
        showToast(`自己採点に失敗しました: ${error.message}`, 'error');
        feedbackResult.querySelector('.result-text').textContent = '採点エラー';
        explanationText.textContent = `エラーが発生したため自己採点できませんでした。模範解答を確認して自己採点してください。\n\nエラー内容: ${error.message}`;
    }
}

// フィードバック表示
function showFeedback(isCorrect, answer, explanation, previousAnswer = null) {
    feedbackArea.classList.remove('hidden');
    
    if (previousAnswer && previousAnswer.feedbackComment) {
        feedbackResult.className = `feedback-result ${previousAnswer.isCorrect ? 'correct-style' : 'incorrect-style'}`;
        feedbackResult.querySelector('.result-icon').textContent = previousAnswer.isCorrect ? '✅' : '❌';
        feedbackResult.querySelector('.result-text').textContent = `${previousAnswer.isCorrect ? '合格' : '要学習'} (スコア: ${previousAnswer.score}/100)`;
        
        renderParsedContent(`<strong>AI採点フィードバック:</strong>\n${previousAnswer.feedbackComment}\n\n<strong>元の問題の解説:</strong>\n${explanation}`, explanationText);
    } else {
        feedbackResult.className = `feedback-result ${isCorrect ? 'correct-style' : 'incorrect-style'}`;
        feedbackResult.querySelector('.result-icon').textContent = isCorrect ? '✅' : '❌';
        feedbackResult.querySelector('.result-text').textContent = isCorrect ? '正解！' : '不正解';
        
        renderParsedContent(explanation, explanationText);
    }
    
    renderParsedContent(answer, correctAnswerText);
    
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

// --- コンテンツパース・レンダリング (Mermaid & SVG 統合) ---
function renderParsedContent(rawText, container) {
    container.innerHTML = '';
    
    // ```mermaid, ```svg, ```xml を抽出する
    const regex = /```(mermaid|svg|xml)\n([\s\S]*?)```/gi;
    let lastIndex = 0;
    let match;
    
    while ((match = regex.exec(rawText)) !== null) {
        const textBefore = rawText.substring(lastIndex, match.index);
        if (textBefore) {
            const span = document.createElement('span');
            span.textContent = textBefore;
            container.appendChild(span);
        }
        
        const type = match[1].toLowerCase();
        const content = match[2].trim();
        
        if (type === 'mermaid') {
            const div = document.createElement('div');
            div.className = 'mermaid-diagram';
            div.textContent = content;
            container.appendChild(div);
        } else if (type === 'svg' || (type === 'xml' && content.includes('<svg'))) {
            const wrapper = document.createElement('div');
            wrapper.className = 'svg-diagram-container';
            wrapper.innerHTML = content;
            container.appendChild(wrapper);
        } else {
            const pre = document.createElement('pre');
            const code = document.createElement('code');
            code.textContent = match[0];
            pre.appendChild(code);
            container.appendChild(pre);
        }
        
        lastIndex = regex.lastIndex;
    }
    
    const textRemaining = rawText.substring(lastIndex);
    if (textRemaining) {
        const span = document.createElement('span');
        span.textContent = textRemaining;
        container.appendChild(span);
    }

    const promises = [];
    if (window.mermaid) {
        const mermaidNodes = container.querySelectorAll('.mermaid-diagram');
        if (mermaidNodes.length > 0) {
            promises.push(window.mermaid.run({ nodes: mermaidNodes }).catch(e => console.warn(e)));
        }
    }
    if (window.MathJax?.typesetPromise) {
        promises.push(window.MathJax.typesetPromise([container]).catch(() => {}));
    }
    return Promise.all(promises);
}

// 記述式の解答を開示する
function revealDescriptiveAnswer() {
    const correctAnswer = appState.currentQuestion.answer;
    
    appState.userAnswers[appState.currentQuestionIndex] = {
        isCorrect: true, // 確認済みを正解扱いにする
        userAnswer: "自己確認",
        resultText: "確認済み",
        feedbackComment: null
    };

    if (showAnswerBtn) showAnswerBtn.disabled = true;

    // フィードバック領域を表示・構成する
    feedbackArea.classList.remove('hidden');
    feedbackResult.className = 'feedback-result correct-style';
    feedbackResult.querySelector('.result-icon').textContent = '📝';
    feedbackResult.querySelector('.result-text').textContent = '解答を確認しました';
    
    correctAnswerText.textContent = correctAnswer;
    explanationText.textContent = appState.currentQuestion.explanation;

    // MathJaxで数式をレンダリング
    if (window.MathJax?.typesetPromise) {
        window.MathJax.typesetPromise([feedbackArea]).catch(() => {});
    }

    feedbackArea.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    updateNextQuestionBtnLabel();
}

// PDFの各ページをJPEG画像（データURL）に変換する
async function renderPdfPagesToImages(pdf) {
    const images = [];
    const numPages = Math.min(pdf.numPages, 10); // 最大10ページに制限して転送量を抑える
    for (let i = 1; i <= numPages; i++) {
        try {
            const page = await pdf.getPage(i);
            const canvas = document.createElement('canvas');
            const context = canvas.getContext('2d');
            
            // 鮮明さとデータサイズのバランスが良い1.2倍スケールで描画
            const viewport = page.getViewport({ scale: 1.2 });
            canvas.width = viewport.width;
            canvas.height = viewport.height;
            
            await page.render({
                canvasContext: context,
                viewport: viewport
            }).promise;
            
            // JPEG形式で圧縮してBase64で格納（平均80KB〜150KB）
            images.push(canvas.toDataURL('image/jpeg', 0.7));
        } catch (e) {
            console.error(`PDFページ ${i} の画像レンダリングに失敗しました:`, e);
        }
    }
    return images;
}

// === プランナートピックのレンダリング ===
function renderPlannerTopics() {
    plannerTopicsList.innerHTML = '';
    appState.plannerTopics.forEach(topic => {
        const chip = document.createElement('div');
        chip.className = 'topic-chip selected';
        chip.textContent = `${topic.name} (${topic.duration}分)`;
        
        const removeBtn = document.createElement('span');
        removeBtn.className = 'remove-btn';
        removeBtn.innerHTML = ' &times;';
        removeBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            appState.plannerTopics = appState.plannerTopics.filter(t => t.name !== topic.name);
            renderPlannerTopics();
        });
        
        chip.appendChild(removeBtn);
        plannerTopicsList.appendChild(chip);
    });
}

// === 新しい計画をAIで生成する ===
async function generateStudyPlan() {
    if (!appState.apiKey) {
        showToast('APIキーを入力・保存してください。', 'error');
        return;
    }

    const goal = plannerGoalInput.value.trim();
    const target = plannerTargetInput.value.trim() || 'なし';
    const deadline = plannerDeadlineInput.value;

    const filterDateStr = plannerAssignmentFilterDate.value;
    const filterDate = filterDateStr ? new Date(filterDateStr) : null;
    if (filterDate) filterDate.setHours(23, 59, 59, 999);

    // インポートモードに基づいて課題を収集・フィルタリング
    let activeAssignments = [];
    if (appState.importMode === 'ical') {
        activeAssignments = appState.icalAssignments.filter(a => {
            if (!filterDate) return true;
            const due = new Date(a.dueDate);
            return due <= filterDate;
        });
    } else {
        activeAssignments = appState.manualAssignments.filter(a => {
            if (!filterDate) return true;
            const due = new Date(a.dueDate);
            return due <= filterDate;
        });
    }

    const assignmentCount = activeAssignments.length;
    const assignmentDeadline = activeAssignments.length > 0
        ? activeAssignments.reduce((latest, a) => a.dueDate > latest ? a.dueDate : latest, activeAssignments[0].dueDate)
        : 'なし';

    if (!goal) {
        showToast('学習目標を入力してください。', 'error');
        return;
    }
    if (!deadline) {
        showToast('期限日を設定してください。', 'error');
        return;
    }

    const deadlineDate = new Date(deadline);
    const today = new Date();
    const todayStrJP = today.toLocaleDateString('ja-JP', { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' });
    const todayISO = today.toISOString().split('T')[0];
    today.setHours(0, 0, 0, 0);
    deadlineDate.setHours(0, 0, 0, 0);

    const diffTime = deadlineDate - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    if (diffDays <= 0) {
        showToast('期限日は明日以降の日付を設定してください。', 'error');
        return;
    }

    // 曜日のリソース時間をパース
    const weeklyHours = {
        Mon: parseFloat(resourceMon.value) || 0,
        Tue: parseFloat(resourceTue.value) || 0,
        Wed: parseFloat(resourceWed.value) || 0,
        Thu: parseFloat(resourceThu.value) || 0,
        Fri: parseFloat(resourceFri.value) || 0,
        Sat: parseFloat(resourceSat.value) || 0,
        Sun: parseFloat(resourceSun.value) || 0
    };

    const totalHoursPerWeek = Object.values(weeklyHours).reduce((sum, h) => sum + h, 0);
    if (totalHoursPerWeek <= 0) {
        showToast('少なくとも1つの曜日の学習時間を0より大きく設定してください。', 'error');
        return;
    }

    // UIをローディングに切り替える
    plannerPlaceholder.classList.add('hidden');
    planDashboard.classList.add('hidden');
    plannerLoader.classList.remove('hidden');
    rescheduleBtn.classList.add('hidden');
    createPlanBtn.disabled = true;
    createPlanBtn.querySelector('.btn-loader').classList.remove('hidden');



    const topics = appState.plannerTopics;

    // 大学課題セクションのプロンプト構築 (個別の所要時間を伝える)
    let assignmentSection = '';
    if (activeAssignments.length > 0) {
        assignmentSection = `【大学の未提出課題】
` + activeAssignments.map(a => `- 課題名: ${a.summary} (提出期限: ${a.dueDate}, 目標作業所要時間: ${a.duration || 90}分)`).join('\n') + `
※重要: 各課題の締め切り期限（提出期限）に絶対に遅れないように、締め切り期限前日の日程までに、その課題の「目標作業所要時間」に相当する合計時間の課題レポート作成タスク（例: 180分であれば、90分のタスクを2回に分ける等。isAssignment: true）を必ず最優先で割り振ってください。`;
    } else {
        assignmentSection = `【大学の未提出課題】
- なし`;
    }

    // 学習トピックセクションのプロンプト構築 (個別の希望勉強時間を伝える)
    let topicSection = '';
    if (topics.length > 0) {
        topicSection = `【学習対象のテスト勉強トピックおよび希望学習時間】
` + topics.map(t => `- トピック名: ${t.name} (希望合計学習時間: ${t.duration}分)`).join('\n') + `
※重要: 指定された各テスト勉強トピックについて、全体の計画期間（${diffDays}日間）を通じて合計が希望学習時間（分）に達するように、タスク（isAssignment: false）を適切に散らしてスケジューリングしてください。`;
    } else {
        topicSection = `【学習対象の主要トピック】
- 目標に適したテスト勉強トピックをAIが自動抽出して割り振ってください。`;
    }

    // AIプロンプトの作成
    const prompt = `以下の要件に基づいて、大学の課題と、テスト勉強（トピック）の両方をバランスよく配分した完璧な学習計画を日次タスクレベルで作成してください。

【基準となる本日（Day 1）の日付と曜日】
- 本日の日付: ${todayStrJP} (西暦では ${todayISO} とします)
※重要: この本日の日付（${todayISO}）を計画の1日目（Day 1）とし、カレンダーの日付（date）を割り当ててください。

【学習目標】
- 目標名: ${goal}
- 達成スコア等: ${target}
- 期限日: ${deadline} (今日から数えて ${diffDays} 日間)

${assignmentSection}

${topicSection}

【学習可能な時間（曜日ごと）】
- 月曜: ${weeklyHours.Mon}時間, 火曜: ${weeklyHours.Tue}時間, 水曜: ${weeklyHours.Wed}時間, 木曜: ${weeklyHours.Thu}時間, 金曜: ${weeklyHours.Fri}時間, 土曜: ${weeklyHours.Sat}時間, 日曜: ${weeklyHours.Sun}時間

【計画作成の指示】
1. 今日から期限日までの全日程（${diffDays} 日間）について、各曜日の学習可能時間を超えないように日次タスクを割り振ってください。学習時間が0時間の曜日にはタスクを割り振らないでください。
2. 各タスクの「date」フィールド（YYYY-MM-DD形式）は、本日の日付（${todayISO}）をDay 1として、経過日数に応じて正しいカレンダーの日付を割り当ててください。また、各日付の曜日名（例: 月, 火, 水, 木, 金, 土, 日）を「dayName」に設定してください。
3. タスク（taskName）は「[課題] 経済レポートの作成」「[トピック] 完全微分方程式の解法」などの具体的で実行可能な最小単位にしてください。各タスクの所要時間（duration）は分単位（例: 45, 60など）で指定してください。
4. 大学の課題レポート作成タスク（isAssignment: true）と、通常のテスト勉強トピックのタスク（isAssignment: false）の両方を同じ一日のスケジュール内で共存させてください。
5. 全体ロードマップ（roadmap）として、週ごとの大まかなフェーズ（テーマと解説）を作成してください。最大で週数の数だけ作成してください（例えば、計画が4週間の場合は4つ）。
6. 出力は、指定されたJSON構造のみを正確に返却してください。`;

    const systemInstruction = 'あなたはプロフェッショナルなAI学習コンサルタントです。ユーザーの期限、学習時間、課題の有無を徹底的に分析し、指定されたJSONフォーマットに従って日次レベルで実行可能かつ完璧に最適化された学習プランを作成してください。';

    const responseSchema = {
        type: 'OBJECT',
        properties: {
            roadmap: {
                type: 'ARRAY',
                description: '週ごとのロードマップ',
                items: {
                    type: 'OBJECT',
                    properties: {
                        weekNum: { type: 'INTEGER', description: '第何週目か (1から開始)' },
                        theme: { type: 'STRING', description: 'その週の主要なテーマ' },
                        description: { type: 'STRING', description: '具体的な学習方針やアクション' }
                    },
                    required: ['weekNum', 'theme', 'description']
                }
            },
            tasks: {
                type: 'ARRAY',
                description: '日次の学習タスクリスト',
                items: {
                    type: 'OBJECT',
                    properties: {
                        id: { type: 'STRING', description: 'タスク固有の一意のID (例: task_1)' },
                        dayNum: { type: 'INTEGER', description: '計画開始からの経過日数 (1からN)' },
                        dayName: { type: 'STRING', description: '曜日名 (例: 月, 火, 水, 木, 金, 土, 日)' },
                        date: { type: 'STRING', description: 'タスクの実行日 (YYYY-MM-DD形式)' },
                        isAssignment: { type: 'BOOLEAN', description: '大学課題のタスクかどうか' },
                        topic: { type: 'STRING', description: '関連する学習トピック' },
                        taskName: { type: 'STRING', description: '具体的なタスク内容' },
                        duration: { type: 'INTEGER', description: '目標所要時間（分）' },
                        status: { type: 'STRING', description: '初期値は "pending" で固定。完了時は "completed"' },
                        difficulty: { type: 'STRING', description: '初期値は null で固定' }
                    },
                    required: ['id', 'dayNum', 'dayName', 'date', 'isAssignment', 'topic', 'taskName', 'duration', 'status']
                }
            }
        },
        required: ['roadmap', 'tasks']
    };

    try {
        const responseText = await callAI(prompt, systemInstruction, responseSchema);
        const planData = JSON.parse(responseText.trim());
        
        planData.createdAt = new Date().toISOString().split('T')[0];
        planData.goal = goal;
        planData.target = target;
        planData.deadline = deadline;
        planData.weeklyHours = weeklyHours;
        planData.topics = topics;
        
        appState.plannerPlan = planData;
        savePlan();
        
        renderPlannerDashboard();
        showToast('AIが新しい学習計画を作成しました！ 📅', 'success');
    } catch (e) {
        console.error(e);
        showToast(`計画の作成に失敗しました: ${e.message}`, 'error');
        plannerPlaceholder.classList.remove('hidden');
        planDashboard.classList.add('hidden');
    } finally {
        plannerLoader.classList.add('hidden');
        createPlanBtn.disabled = false;
        createPlanBtn.querySelector('.btn-loader').classList.add('hidden');
    }
}

// === AI学習計画の再調整（自動リスケジュール） ===
async function rescheduleStudyPlan() {
    if (!appState.apiKey || !appState.plannerPlan) return;

    const plan = appState.plannerPlan;
    const deadlineDate = new Date(plan.deadline);
    const today = new Date();
    const todayStrJP = today.toLocaleDateString('ja-JP', { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' });
    const todayISO = today.toISOString().split('T')[0];
    today.setHours(0, 0, 0, 0);
    deadlineDate.setHours(0, 0, 0, 0);
    
    const diffTime = deadlineDate - today;
    const remainingDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    if (remainingDays <= 0) {
        showToast('期限日を過ぎているか、最終日です。新しく計画を作成してください。', 'warning');
        return;
    }

    const completedTasks = plan.tasks.filter(t => t.status === 'completed');
    const pendingTasks = plan.tasks.filter(t => t.status !== 'completed');

    if (pendingTasks.length === 0) {
        showToast('すべてのタスクが完了しています！再調整の必要はありません。', 'success');
        return;
    }

    const difficultTopics = Array.from(new Set(
        plan.tasks
            .filter(t => t.status === 'completed' && t.difficulty === 'hard')
            .map(t => t.topic)
    ));

    rescheduleBtn.disabled = true;
    rescheduleBtn.querySelector('.btn-loader').classList.remove('hidden');
    plannerLoaderMessage.textContent = 'AIが進行状況に合わせて学習計画を再調整しています... 🔍';
    plannerLoader.classList.remove('hidden');
    planDashboard.classList.add('hidden');

    const filterDateStr = plannerAssignmentFilterDate.value;
    const filterDate = filterDateStr ? new Date(filterDateStr) : null;
    if (filterDate) filterDate.setHours(23, 59, 59, 999);

    // インポートモードに基づいて課題を収集・フィルタリング
    let activeAssignments = [];
    if (appState.importMode === 'ical') {
        activeAssignments = appState.icalAssignments.filter(a => {
            if (!filterDate) return true;
            const due = new Date(a.dueDate);
            return due <= filterDate;
        });
    } else {
        activeAssignments = appState.manualAssignments.filter(a => {
            if (!filterDate) return true;
            const due = new Date(a.dueDate);
            return due <= filterDate;
        });
    }

    let assignmentStatus = '';
    if (activeAssignments.length > 0) {
        assignmentStatus = `【大学の未提出課題と所要時間】
` + activeAssignments.map(a => `- 課題名: ${a.summary} (提出期限: ${a.dueDate}, 目標作業所要時間: ${a.duration || 90}分)`).join('\n') + `
※重要: 未完了の課題がある場合、または締め切り期限が迫っている場合は、その期日前に終わるよう、指定された「目標作業所要時間」に相当する課題レポートタスク（isAssignment: true）を最優先でスケジュール内に残し、適正な日程へ再配分してください。`;
    } else {
        assignmentStatus = `【大学の未提出課題】
- なし`;
    }

    let topicStatus = '';
    const topics = plan.topics || [];
    if (topics.length > 0) {
        topicStatus = `【学習対象のテスト勉強トピックと希望合計学習時間】
` + topics.map(t => `- ${t.name || t}: ${t.duration || 60}分`).join('\n');
    }

    const prompt = `進行状況とフィードバックに基づいて、残り期限までに実行可能なように学習計画を動的に再構成（リスケジュール）してください。

【基準となる今日の再調整日付と曜日】
- 本日の日付: ${todayStrJP} (西暦では ${todayISO} とします)
※重要: この本日の日付（${todayISO}）を基準にして、未完了タスクのカレンダー日付（date）を割り当ててください。

【学習目標】
- 目標名: ${plan.goal}
- 残り日数: 今日を含めて残り ${remainingDays} 日間 (期限日: ${plan.deadline})

【現在までの進捗】
- 完了したタスク数: ${completedTasks.length} 件 / 全体 ${plan.tasks.length} 件
${assignmentStatus}
${topicStatus}
- 苦手（難しかった）と感じているトピック: ${difficultTopics.length > 0 ? difficultTopics.join(', ') : '特になし'}

【学習可能な時間（曜日ごと）】
- 月曜: ${plan.weeklyHours.Mon}時間, 火曜: ${plan.weeklyHours.Tue}時間, 水曜: ${plan.weeklyHours.Wed}時間, 木曜: ${plan.weeklyHours.Thu}時間, 金曜: ${plan.weeklyHours.Fri}時間, 土曜: ${plan.weeklyHours.Sat}時間, 日曜: ${plan.weeklyHours.Sun}時間

【リスケジュール（再調整）の指示】
1. すでに「完了（completed）」したタスク（全 ${completedTasks.length} 件）は、変更せず「date」「dayName」「status: "completed"」の履歴を含めたままで新しいタスクリストにそのまま含めてください。
2. 未完了のタスクは、本日の日付（${todayISO}）以降の正しいカレンダー日付（date: YYYY-MM-DD形式）および曜日（dayName）を割り振ってください。各曜日ごとの学習可能時間内に収まるように再配分してください。
3. 苦手なトピック（${difficultTopics.join(', ')}）については、理解を深めるための「復習タスク（例: 復習や見直し）」を新たに追加してください。
4. 残り時間に対してタスクが多すぎて収まりきらないと判断した場合は、重要度の低いトピックのタスクを自動で削減し、最も重要なタスクや大学課題の提出タスク（isAssignment: true）を優先して残してください。
5. 出力は、修正・検証完了後のロードマップと全タスク（完了済み＋再配分された未完了タスク）を含む指定のJSON形式のみを返却してください。`;

    const systemInstruction = 'あなたは優秀なAI学習計画コーチです。ユーザーの進捗と苦手トピックに合わせて、残された日数と時間リソースを数学的に最適化し、現実的で挫折しない学習計画を再構築してください。';

    const responseSchema = {
        type: 'OBJECT',
        properties: {
            roadmap: {
                type: 'ARRAY',
                description: '週ごとのロードマップ',
                items: {
                    type: 'OBJECT',
                    properties: {
                        weekNum: { type: 'INTEGER' },
                        theme: { type: 'STRING' },
                        description: { type: 'STRING' }
                    },
                    required: ['weekNum', 'theme', 'description']
                }
            },
            tasks: {
                type: 'ARRAY',
                description: '日次の学習タスクリスト',
                items: {
                    type: 'OBJECT',
                    properties: {
                        id: { type: 'STRING' },
                        dayNum: { type: 'INTEGER' },
                        dayName: { type: 'STRING' },
                        date: { type: 'STRING', description: 'タスクの実行日 (YYYY-MM-DD形式)' },
                        isAssignment: { type: 'BOOLEAN' },
                        topic: { type: 'STRING' },
                        taskName: { type: 'STRING' },
                        duration: { type: 'INTEGER' },
                        status: { type: 'STRING' },
                        difficulty: { type: 'STRING' }
                    },
                    required: ['id', 'dayNum', 'dayName', 'date', 'isAssignment', 'topic', 'taskName', 'duration', 'status']
                }
            }
        },
        required: ['roadmap', 'tasks']
    };

    try {
        const responseText = await callAI(prompt, systemInstruction, responseSchema);
        const planData = JSON.parse(responseText.trim());
        
        planData.createdAt = plan.createdAt;
        planData.goal = plan.goal;
        planData.target = plan.target;
        planData.deadline = plan.deadline;
        planData.weeklyHours = plan.weeklyHours;
        planData.topics = plan.topics;
        
        completedTasks.forEach(comp => {
            const match = planData.tasks.find(t => t.id === comp.id);
            if (match) {
                match.status = 'completed';
                match.difficulty = comp.difficulty;
            }
        });

        appState.plannerPlan = planData;
        savePlan();
        
        renderPlannerDashboard();
        showToast('AIが学習計画を進行状況に合わせて再調整しました！ 🔄', 'success');
    } catch (e) {
        console.error(e);
        showToast(`計画の再調整に失敗しました: ${e.message}`, 'error');
        renderPlannerDashboard();
    } finally {
        plannerLoader.classList.add('hidden');
        rescheduleBtn.disabled = false;
        rescheduleBtn.querySelector('.btn-loader').classList.add('hidden');
    }
}

// === ダッシュボード表示のレンダリング ===
function renderPlannerDashboard() {
    const plan = appState.plannerPlan;
    if (!plan) return;

    // UIの切り替え
    plannerPlaceholder.classList.add('hidden');
    plannerLoader.classList.add('hidden');
    planDashboard.classList.remove('hidden');
    rescheduleBtn.classList.remove('hidden');

    // 左側の入力値の同期
    plannerGoalInput.value = plan.goal;
    plannerTargetInput.value = plan.target;
    plannerDeadlineInput.value = plan.deadline;
    appState.plannerTopics = (plan.topics || []).map(t => {
        if (typeof t === 'string') {
            return { name: t, duration: 60 };
        }
        return t;
    });
    renderPlannerTopics();

    // 曜日時間の同期
    if (plan.weeklyHours) {
        resourceMon.value = plan.weeklyHours.Mon;
        resourceTue.value = plan.weeklyHours.Tue;
        resourceWed.value = plan.weeklyHours.Wed;
        resourceThu.value = plan.weeklyHours.Thu;
        resourceFri.value = plan.weeklyHours.Fri;
        resourceSat.value = plan.weeklyHours.Sat;
        resourceSun.value = plan.weeklyHours.Sun;
    }

    // 既存の計画データを読み込み、後方互換性のために date 属性を補完
    const createdAtDate = new Date(plan.createdAt);
    const todayDate = new Date();
    createdAtDate.setHours(0, 0, 0, 0);
    todayDate.setHours(0, 0, 0, 0);
    
    plan.tasks.forEach(t => {
        if (!t.date) {
            const taskDate = new Date(createdAtDate);
            taskDate.setDate(taskDate.getDate() + (t.dayNum - 1));
            t.date = taskDate.toISOString().split('T')[0];
        }
    });

    const elapsedDays = Math.floor((todayDate - createdAtDate) / (1000 * 60 * 60 * 24)) + 1;
    const todayStrISO = todayDate.toISOString().split('T')[0];

    // 1. 今日のタスク一覧の表示
    todayTasksList.innerHTML = '';
    const todayTasks = plan.tasks.filter(t => t.date === todayStrISO);

    if (todayTasks.length === 0) {
        todayTasksList.innerHTML = `
            <div class="planner-task-card" style="justify-content: center; opacity: 0.7;">
                <div class="task-info-left" style="align-items: center; text-align: center;">
                    <span class="task-title">🎉 今日の学習タスクはありません</span>
                    <span class="task-meta">本日はゆっくり休むか、カレンダーから先の予習をしましょう。</span>
                </div>
            </div>`;
    } else {
        todayTasks.forEach(task => {
            const card = document.createElement('div');
            card.className = `planner-task-card ${task.status === 'completed' ? 'completed' : ''} ${task.isAssignment ? 'assignment' : ''}`;
            
            const isCompleted = task.status === 'completed';
            const actionBtn = isCompleted 
                ? `<span style="color:#10b981; font-weight:bold; display:flex; align-items:center; gap:4px;">
                     ✅ 完了 (${task.difficulty === 'easy' ? '簡単' : task.difficulty === 'hard' ? '復習要' : '普通'})
                   </span>`
                : `<button class="btn btn-primary" onclick="window.completePlannerTask('${task.id}')">完了する</button>`;

            const assignmentBadge = task.isAssignment 
                ? `<span class="tag tag-assignment">課題提出</span>` 
                : '';

            card.innerHTML = `
                <div class="task-info-left">
                    <div class="task-header-tags">
                        <span class="tag tag-difficulty">トピック: ${task.topic || '共通'}</span>
                        ${assignmentBadge}
                    </div>
                    <span class="task-title">${task.taskName}</span>
                    <span class="task-meta">🕒 目標時間: ${task.duration} 分</span>
                </div>
                <div class="task-info-right">
                    ${actionBtn}
                </div>
            `;
            todayTasksList.appendChild(card);
        });
    }

    // 2. ロードマップの表示
    roadmapTimeline.innerHTML = '';
    const currentWeekNum = Math.max(1, Math.ceil(elapsedDays / 7));
    plan.roadmap.forEach(rm => {
        const item = document.createElement('div');
        item.className = `roadmap-item ${rm.weekNum === currentWeekNum ? 'active' : ''}`;
        item.innerHTML = `
            <div class="roadmap-item-bubble"></div>
            <div class="roadmap-item-content">
                <div class="roadmap-week">第 ${rm.weekNum} 週目 ${rm.weekNum === currentWeekNum ? '(現在地)' : ''}</div>
                <div class="roadmap-theme">${rm.theme}</div>
                <div class="roadmap-desc">${rm.description}</div>
            </div>
        `;
        roadmapTimeline.appendChild(item);
    });

    // 3. 週間スケジュールの表示 (現在の週の月曜日〜日曜日を表示)
    weeklyScheduleGrid.innerHTML = '';
    
    // 現在の週の月曜日を特定
    const todayObj = new Date();
    todayObj.setHours(0, 0, 0, 0);
    const currentDayOfWeek = todayObj.getDay(); // 0: 日曜日, 1: 月曜日...
    
    // 月曜日を週の始まり(idx 0)にするための差分
    const diffToMonday = todayObj.getDate() - currentDayOfWeek + (currentDayOfWeek === 0 ? -6 : 1);
    const monday = new Date(todayObj);
    monday.setDate(diffToMonday);

    const dayNamesJP = ["月", "火", "水", "木", "金", "土", "日"];
    const dayNamesEN = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

    dayNamesEN.forEach((dayEN, idx) => {
        const col = document.createElement('div');
        col.className = 'schedule-day-column';
        
        // 各曜日の日付
        const colDate = new Date(monday);
        colDate.setDate(monday.getDate() + idx);
        const colDateStr = colDate.toISOString().split('T')[0];
        
        const isTodayColumn = colDateStr === todayStrISO;
        
        const header = document.createElement('div');
        header.className = `schedule-day-header ${isTodayColumn ? 'today' : ''}`;
        header.innerHTML = `${dayNamesJP[idx]}曜日<br><span style="font-size:0.72rem; font-weight:normal; opacity:0.8;">${colDate.getMonth()+1}/${colDate.getDate()}</span>`;
        col.appendChild(header);

        // この曜日のタスク
        const dayTasks = plan.tasks.filter(t => t.date === colDateStr);
        if (dayTasks.length === 0) {
            const emptyItem = document.createElement('div');
            emptyItem.className = 'schedule-task-item';
            emptyItem.style.opacity = '0.5';
            emptyItem.style.textAlign = 'center';
            emptyItem.textContent = '-';
            col.appendChild(emptyItem);
        } else {
            dayTasks.forEach(task => {
                const item = document.createElement('div');
                item.className = `schedule-task-item ${task.status === 'completed' ? 'completed' : ''} ${task.isAssignment ? 'assignment' : ''}`;
                item.innerHTML = `
                    <div style="font-weight:bold; margin-bottom:2px;">${task.isAssignment ? '🚨 ' : ''}${task.taskName}</div>
                    <div style="font-size:0.7rem; opacity:0.8;">🕒 ${task.duration}分 | ${task.topic}</div>
                `;
                col.appendChild(item);
            });
        }

        weeklyScheduleGrid.appendChild(col);
    });
}

// === タスク完了アクション ===
window.completePlannerTask = function(taskId) {
    const plan = appState.plannerPlan;
    if (!plan) return;

    const task = plan.tasks.find(t => t.id === taskId);
    if (!task) return;

    // 振り返り評価ダイアログのポップアップを生成
    openEvaluationDialog(task);
};

// === 振り返り用ダイアログ表示 ===
function openEvaluationDialog(task) {
    const overlay = document.createElement('div');
    overlay.className = 'evaluation-dialog-overlay';

    overlay.innerHTML = `
        <div class="evaluation-dialog">
            <h3>学習の振り返り</h3>
            <p>「${task.taskName}」お疲れ様でした！このタスクの理解度・難易度はどうでしたか？</p>
            <div class="evaluation-options">
                <button class="evaluation-btn" data-val="easy">
                    <span class="emoji">🟢</span>
                    <div>
                        <div style="font-weight:bold;">簡単だった / 順調</div>
                        <div style="font-size:0.75rem; color:var(--text-secondary);">予定より早くできた。復習は少なめでOK</div>
                    </div>
                </button>
                <button class="evaluation-btn" data-val="normal">
                    <span class="emoji">🟡</span>
                    <div>
                        <div style="font-weight:bold;">ちょうど良い / 普通</div>
                        <div style="font-size:0.75rem; color:var(--text-secondary);">予定通り理解できた。順調です</div>
                    </div>
                </button>
                <button class="evaluation-btn" data-val="hard">
                    <span class="emoji">🔴</span>
                    <div>
                        <div style="font-weight:bold;">難しかった / 復習要</div>
                        <div style="font-size:0.75rem; color:var(--text-secondary);">時間超過、または理解不足。後日復習が必要</div>
                    </div>
                </button>
                <button class="evaluation-btn" data-val="skipped" style="margin-top: 10px; border-color: rgba(239,68,68,0.3);">
                    <span class="emoji">❌</span>
                    <div>
                        <div style="font-weight:bold; color:#f87171;">できなかった / スキップ</div>
                        <div style="font-size:0.75rem; color:var(--text-secondary);">別日にリスケジュールを希望する</div>
                    </div>
                </button>
            </div>
        </div>
    `;

    document.body.appendChild(overlay);

    overlay.querySelectorAll('.evaluation-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const difficulty = btn.getAttribute('data-val');
            
            // 状態の更新
            if (difficulty === 'skipped') {
                task.status = 'pending'; // skippedは未完了状態でリスケ待ちにする
                task.difficulty = 'skipped';
                showToast('タスクをスキップしました。「再調整」すると別日に自動割り当てされます。', 'info');
            } else {
                task.status = 'completed';
                task.difficulty = difficulty;
                showToast('タスク完了！よく頑張りました。🎉', 'success');
            }

            savePlan();
            renderPlannerDashboard();
            document.body.removeChild(overlay);
        });
    });

    // 背景クリックでキャンセル可能にする
    overlay.addEventListener('click', (e) => {
        if (e.target === overlay) {
            document.body.removeChild(overlay);
        }
    });
}

// === 計画のローカル保存 ===
function savePlan() {
    if (appState.plannerPlan) {
        localStorage.setItem('planner_plan', JSON.stringify(appState.plannerPlan));
    }
}

// === 課題インポートモードの切り替え ===
function toggleImportMode(mode) {
    appState.importMode = mode;
    localStorage.setItem('planner_import_mode', mode);

    if (mode === 'ical') {
        importModeIcalBtn.classList.add('active');
        importModeManualBtn.classList.remove('active');
        icalInputArea.classList.remove('hidden');
        manualInputArea.classList.add('hidden');
    } else {
        importModeManualBtn.classList.add('active');
        importModeIcalBtn.classList.remove('active');
        manualInputArea.classList.remove('hidden');
        icalInputArea.classList.add('hidden');
    }
}

// === iCalカレンダーの同期処理 ===
async function syncIcalCalendar() {
    const icalUrl = plannerIcalUrl.value.trim();
    if (!icalUrl) {
        showToast('iCal URLを入力してください。', 'error');
        return;
    }

    if (!icalUrl.startsWith('http://') && !icalUrl.startsWith('https://')) {
        showToast('有効なURLを入力してください (http:// または https://)。', 'error');
        return;
    }

    syncIcalBtn.disabled = true;
    syncIcalBtn.querySelector('.btn-loader').classList.remove('hidden');
    icalStatusMessage.textContent = 'カレンダーを取得中... 🌐';
    icalStatusMessage.style.color = 'var(--text-secondary)';
    syncedAssignmentsList.innerHTML = '';

    try {
        // CORS制限回避プロキシ (二重化フォールバック)
    let icsText = '';
    let fetchedSuccess = false;
    let lastErrorMsg = '';

    // 試行1: allorigins.win
    try {
        const proxyUrl1 = `https://api.allorigins.win/raw?url=${encodeURIComponent(icalUrl)}`;
        const response = await fetch(proxyUrl1);
        if (response.ok) {
            icsText = await response.text();
            fetchedSuccess = true;
        } else {
            lastErrorMsg = `HTTP status ${response.status}`;
        }
    } catch (e1) {
        console.warn("Proxy 1 (allorigins) failed:", e1);
        lastErrorMsg = e1.message;
    }

    // 試行2: corsproxy.io (フォールバック)
    if (!fetchedSuccess) {
        try {
            icalStatusMessage.textContent = '代替サーバー経由で再接続中... 🌐';
            const proxyUrl2 = `https://corsproxy.io/?${encodeURIComponent(icalUrl)}`;
            const response = await fetch(proxyUrl2);
            if (response.ok) {
                icsText = await response.text();
                fetchedSuccess = true;
            } else {
                lastErrorMsg = `HTTP status ${response.status}`;
            }
        } catch (e2) {
            console.error("Proxy 2 (corsproxy) failed:", e2);
            lastErrorMsg = e2.message;
        }
    }

    if (!fetchedSuccess) {
        throw new Error(`接続失敗 (${lastErrorMsg})`);
    }
        const events = parseICS(icsText);
        
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        
        // 今日以降の締切/開始イベントのみ抽出
        const futureEvents = events.filter(e => {
            const date = e.dtend || e.dtstart;
            return date && date >= today;
        });

        // 日付順にソート
        futureEvents.sort((a, b) => (a.dtend || a.dtstart) - (b.dtend || b.dtstart));

        appState.icalUrl = icalUrl;
        appState.icalAssignments = futureEvents.map(e => ({
            summary: e.summary,
            dueDate: (e.dtend || e.dtstart).toISOString().split('T')[0]
        }));

        localStorage.setItem('planner_ical_url', icalUrl);
        localStorage.setItem('planner_ical_assignments', JSON.stringify(appState.icalAssignments));

        renderSyncedAssignments();
        showToast('カレンダーの同期に成功しました！ 🎉', 'success');
        icalStatusMessage.textContent = `同期完了: ${appState.icalAssignments.length} 件の予定が読み込まれました`;
        icalStatusMessage.style.color = '#10b981';
    } catch (e) {
        console.error(e);
        icalStatusMessage.textContent = `同期失敗: ${e.message}。URLが正しいか、または時間をおいて再度お試しください。`;
        icalStatusMessage.style.color = '#f87171';
        showToast('カレンダーの同期に失敗しました。', 'error');
    } finally {
        syncIcalBtn.disabled = false;
        syncIcalBtn.querySelector('.btn-loader').classList.add('hidden');
    }
}

// === 簡易ICSファイルパーサー ===
function parseICS(text) {
    const events = [];
    const lines = text.split(/\r?\n/);
    let currentEvent = null;
    
    for (let i = 0; i < lines.length; i++) {
        let line = lines[i];
        if (!line) continue;

        // 行折りたたみの結合処理
        while (i + 1 < lines.length && (lines[i+1].startsWith(' ') || lines[i+1].startsWith('\t'))) {
            line += lines[i+1].substring(1);
            i++;
        }

        line = line.trim();
        if (line === 'BEGIN:VEVENT') {
            currentEvent = {};
        } else if (line === 'END:VEVENT') {
            if (currentEvent && currentEvent.summary) {
                events.push(currentEvent);
            }
            currentEvent = null;
        } else if (currentEvent) {
            const colonIdx = line.indexOf(':');
            if (colonIdx !== -1) {
                const keyPart = line.substring(0, colonIdx);
                const key = keyPart.split(';')[0];
                const value = line.substring(colonIdx + 1);
                
                if (key === 'SUMMARY') {
                    currentEvent.summary = value.replace(/\\,/g, ',').replace(/\\;/g, ';');
                } else if (key === 'DTEND' || key === 'DTSTART') {
                    currentEvent[key.toLowerCase()] = parseICSDate(value);
                } else if (key === 'DESCRIPTION') {
                    currentEvent.description = value.replace(/\\n/g, '\n').replace(/\\,/g, ',').replace(/\\;/g, ';');
                }
            }
        }
    }
    return events;
}

// === ICS日付文字列パース（Dateオブジェクト化） ===
function parseICSDate(value) {
    if (!value) return null;
    const year = parseInt(value.substring(0, 4), 10);
    const month = parseInt(value.substring(4, 6), 10) - 1;
    const day = parseInt(value.substring(6, 8), 10);
    
    if (value.includes('T')) {
        const hour = parseInt(value.substring(9, 11), 10);
        const min = parseInt(value.substring(11, 13), 10);
        const sec = parseInt(value.substring(13, 15), 10);
        if (value.endsWith('Z')) {
            return new Date(Date.UTC(year, month, day, hour, min, sec));
        } else {
            return new Date(year, month, day, hour, min, sec);
        }
    } else {
        return new Date(year, month, day);
    }
}

// === 同期済み課題プレビューリストのレンダリング ===
function renderSyncedAssignments() {
    syncedAssignmentsList.innerHTML = '';
    
    if (appState.icalAssignments.length === 0) {
        return;
    }

    const filterDateStr = plannerAssignmentFilterDate.value;
    const filterDate = filterDateStr ? new Date(filterDateStr) : null;
    if (filterDate) filterDate.setHours(23, 59, 59, 999);

    const activeAssignments = appState.icalAssignments.filter(assign => {
        if (!filterDate) return true;
        const due = new Date(assign.dueDate);
        return due <= filterDate;
    });

    if (activeAssignments.length === 0) {
        syncedAssignmentsList.innerHTML = '<div class="placeholder-text" style="font-size: 0.8rem; padding: 10px; text-align: left;">指定した期限内の課題はありません</div>';
        return;
    }

    activeAssignments.forEach(assign => {
        const item = document.createElement('div');
        item.className = 'synced-assignment-item';
        
        const dateObj = new Date(assign.dueDate);
        const dateStr = `${dateObj.getMonth() + 1}/${dateObj.getDate()}`;
        const currentDuration = assign.duration || 90;

        item.innerHTML = `
            <span class="synced-assignment-title" title="${assign.summary}">${assign.summary}</span>
            <div style="display: flex; align-items: center; gap: 12px; margin-left: auto;">
                <span class="synced-assignment-date">締切: ${dateStr}</span>
                <div class="synced-assignment-duration">
                    <input type="number" min="15" step="15" value="${currentDuration}" class="assign-dur-input" />
                    <span>分</span>
                </div>
            </div>
        `;

        const durInput = item.querySelector('.assign-dur-input');
        durInput.addEventListener('change', () => {
            const val = parseInt(durInput.value) || 90;
            assign.duration = val;
            const original = appState.icalAssignments.find(a => a.summary === assign.summary && a.dueDate === assign.dueDate);
            if (original) original.duration = val;
            localStorage.setItem('planner_ical_assignments', JSON.stringify(appState.icalAssignments));
        });

        syncedAssignmentsList.appendChild(item);
    });
}

// === 手動登録済み課題プレビューリストのレンダリング ===
function renderManualAssignments() {
    manualAssignmentsList.innerHTML = '';
    
    if (appState.manualAssignments.length === 0) {
        return;
    }

    const filterDateStr = plannerAssignmentFilterDate.value;
    const filterDate = filterDateStr ? new Date(filterDateStr) : null;
    if (filterDate) filterDate.setHours(23, 59, 59, 999);

    const activeManual = appState.manualAssignments.filter(assign => {
        if (!filterDate) return true;
        const due = new Date(assign.dueDate);
        return due <= filterDate;
    });

    if (activeManual.length === 0) {
        manualAssignmentsList.innerHTML = '<div class="placeholder-text" style="font-size: 0.8rem; padding: 10px; text-align: left;">指定した期限内の手動課題はありません</div>';
        return;
    }

    activeManual.forEach(assign => {
        const item = document.createElement('div');
        item.className = 'synced-assignment-item';
        
        const dateObj = new Date(assign.dueDate);
        const dateStr = `${dateObj.getMonth() + 1}/${dateObj.getDate()}`;
        const currentDuration = assign.duration || 90;

        item.innerHTML = `
            <span class="synced-assignment-title" title="${assign.summary}">${assign.summary}</span>
            <div style="display: flex; align-items: center; gap: 12px; margin-left: auto;">
                <span class="synced-assignment-date">締切: ${dateStr}</span>
                <div class="synced-assignment-duration">
                    <input type="number" min="15" step="15" value="${currentDuration}" class="manual-dur-input" />
                    <span>分</span>
                </div>
                <span class="remove-btn" style="cursor: pointer; font-size: 1.1rem; color: #ef4444; margin-left: 4px;">&times;</span>
            </div>
        `;

        const durInput = item.querySelector('.manual-dur-input');
        durInput.addEventListener('change', () => {
            const val = parseInt(durInput.value) || 90;
            assign.duration = val;
            const original = appState.manualAssignments.find(a => a.id === assign.id);
            if (original) original.duration = val;
            localStorage.setItem('planner_manual_assignments', JSON.stringify(appState.manualAssignments));
        });

        const removeBtn = item.querySelector('.remove-btn');
        removeBtn.addEventListener('click', () => {
            appState.manualAssignments = appState.manualAssignments.filter(a => a.id !== assign.id);
            localStorage.setItem('planner_manual_assignments', JSON.stringify(appState.manualAssignments));
            renderManualAssignments();
            showToast('課題を削除しました。', 'info');
        });

        manualAssignmentsList.appendChild(item);
    });
}

