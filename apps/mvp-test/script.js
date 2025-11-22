// Python 백엔드 서버의 주소
const API_URL = 'https://my-mvp-backend-1093137562151.us-central1.run.app';

// 타이머 설정
const TIMER_CONFIG = {
    DURATION: 1800,      // 30분 = 1800초
    WARNING_TIME: 300,   // 5분 = 300초 (주황색 경고)
    DANGER_TIME: 60      // 1분 = 60초 (빨간색 경고)
};

// 전역 변수
let loadedProblems = [];
let timerState = {
    timeRemaining: TIMER_CONFIG.DURATION,
    startTime: null,
    intervalId: null,
    isOvertime: false
};

// DOM 요소
const startBtn = document.getElementById('start-test-btn');
const startSection = document.getElementById('start-section');
const problemSection = document.getElementById('problem-section');
const problemContainer = document.getElementById('problem-container');
const submitBtn = document.getElementById('submit-btn');
const resultSection = document.getElementById('result-section');
const analysisReportDiv = document.getElementById('ai-analysis-report');
const resultDetailsDiv = document.getElementById('result-details');
const messageDiv = document.getElementById('message-container');
const timerContainer = document.getElementById('timer-container');
const timerDisplay = document.getElementById('timer-display');
const timeoutModal = document.getElementById('timeout-modal');
const submitTimeoutBtn = document.getElementById('submit-timeout-btn');
const continueBtn = document.getElementById('continue-btn');
const loadingModal = document.getElementById('loading-modal');

// 이벤트 리스너
startBtn.addEventListener('click', loadProblems);
submitBtn.addEventListener('click', submitAnswers);
submitTimeoutBtn.addEventListener('click', submitAnswers);
continueBtn.addEventListener('click', hideTimeoutModal);

// M2.1: Python 백엔드에서 문제 로드 (FIXED)
async function loadProblems() {
    showMessage("문제를 불러오는 중입니다...", "blue");
    startBtn.disabled = true;

    try {
        const response = await fetch(`${API_URL}/get_test_problems`);
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `서버 오류: ${response.status}`);
        }

        loadedProblems = await response.json(); // 전역 변수에 저장
        
        if (!loadedProblems || loadedProblems.length === 0) {
            throw new Error("DB에서 문제를 불러오지 못했습니다. (데이터가 비어있을 수 있습니다)");
        }

        displayProblems(); // 문제 표시 함수 호출

        startSection.classList.add('hidden'); // 시작 버튼 숨기기
        problemSection.classList.remove('hidden'); // 문제 섹션 표시
        messageDiv.innerHTML = ''; // 로딩 메시지 제거

        // 타이머 시작
        startTimer();
        showTimer();

        // 문제 섹션으로 스크롤
        problemSection.scrollIntoView({ behavior: 'smooth', block: 'start' });

    } catch (error) {
        console.error('Error loading problems:', error);
        showMessage(`오류: 문제 로딩 실패: ${error.message} (Python 서버 실행 및 DB 연결, Phase 1 데이터 확인)`, "red");
        startBtn.disabled = false;
    }
}

// 타이머 시작
function startTimer() {
    timerState.startTime = Date.now();
    timerState.intervalId = setInterval(() => {
        timerState.timeRemaining--;
        updateTimer();

        // 시간 종료 시 모달 표시
        if (timerState.timeRemaining === 0 && !timerState.isOvertime) {
            showTimeoutModal();
        }

        // 초과 시간
        if (timerState.timeRemaining < 0) {
            timerState.isOvertime = true;
        }
    }, 1000);
}

// 타이머 정지
function stopTimer() {
    if (timerState.intervalId) {
        clearInterval(timerState.intervalId);
        timerState.intervalId = null;
    }
}

// 타이머 표시/숨김
function showTimer() {
    timerContainer.classList.remove('hidden');
}

function hideTimer() {
    timerContainer.classList.add('hidden');
}

// 타이머 업데이트
function updateTimer() {
    const seconds = timerState.timeRemaining;
    const minutes = Math.floor(Math.abs(seconds) / 60);
    const secs = Math.abs(seconds) % 60;
    const sign = seconds < 0 ? '-' : '';

    timerDisplay.textContent = `${sign}${minutes}:${secs.toString().padStart(2, '0')}`;

    // 색상 변경
    timerDisplay.className = 'text-xl font-bold';
    if (seconds < 0) {
        timerDisplay.classList.add('timer-danger');
    } else if (seconds <= TIMER_CONFIG.DANGER_TIME) {
        timerDisplay.classList.add('timer-danger');
    } else if (seconds <= TIMER_CONFIG.WARNING_TIME) {
        timerDisplay.classList.add('timer-warning');
    } else {
        timerDisplay.classList.add('timer-normal');
    }
}

// 시간 종료 모달 표시/숨김
function showTimeoutModal() {
    timeoutModal.classList.remove('hidden');
}

function hideTimeoutModal() {
    timeoutModal.classList.add('hidden');
}

// 로딩 모달 표시/숨김
function showLoadingModal() {
    loadingModal.classList.remove('hidden');
}

function hideLoadingModal() {
    loadingModal.classList.add('hidden');
}

// 실제 소요 시간 계산
function getTotalTimeSpent() {
    if (!timerState.startTime) return 0;
    return Math.floor((Date.now() - timerState.startTime) / 1000);
}

// 로드된 문제를 HTML로 표시 (FIXED for Fix 1 & 2)
function displayProblems() {
    problemContainer.innerHTML = '';
    loadedProblems.forEach((problem, index) => {
        const problemEl = document.createElement('div');
        problemEl.className = 'border p-5 rounded-lg';
        problemEl.dataset.problemId = problem.problem_id; // id 저장

        // 문제 텍스트 (Fix 1: innerHTML, Fix 2: text-gray-900)
        const textEl = document.createElement('div');
        textEl.className = 'problem-text mb-4 text-gray-900'; // 2. 기본 검정색
        
        // 1. innerHTML로 텍스트를 먼저 설정 (띄어쓰기 보존)
        textEl.innerHTML = `<b>Q ${index + 1}.</b> ${problem.text_latex}`;

        // 선택지 (Radio Buttons)
        const choicesEl = document.createElement('div');
        choicesEl.className = 'choices space-y-2';
        
        // choices가 배열인지 확인
        if (Array.isArray(problem.choices)) {
            problem.choices.forEach(choice => {
                // "A) 4", "B) 9" 에서 "A", "4" 또는 "B", "9" 분리
                const choiceMatch = choice.match(/^([A-D])\)\s*(.*)$/);
                let choiceValue = choice;
                let choiceLabel = choice;

                if (choiceMatch) {
                    choiceValue = choiceMatch[1]; // "A"
                    choiceLabel = choice; // "A) 4"
                }

                choicesEl.innerHTML += `
                    <label class="block flex items-center p-3 rounded-md border hover:bg-gray-50 cursor-pointer">
                        <input type="radio" name="problem-${problem.problem_id}" value="${choiceValue}" class="mr-3">
                        <span class="choice-text">${choiceLabel}</span>
                    </label>
                `;
            });
        } else if (problem.choices === '주관식') {
                choicesEl.innerHTML = `
                <label class="block">
                    <span class="text-gray-700">주관식 답:</span>
                    <input type="text" name="problem-${problem.problem_id}" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500">
                </label>
            `;
        }

        problemEl.appendChild(textEl);
        problemEl.appendChild(choicesEl);
        problemContainer.appendChild(problemEl);

        // 2. KaTeX 렌더링: '$' 기호가 포함된 경우에만 실행 (기존 헬퍼 함수 사용)
        renderKatexInElements([textEl]); // 문제 텍스트 렌더링
    });

    // 선택지 내부의 LaTeX도 렌더링
    renderKatexInElements(problemContainer.querySelectorAll('.choice-text'));
}

// M3 & M4: 답안 제출 및 AI 분석 요청
async function submitAnswers() {
    // 로딩 모달 표시
    showLoadingModal();
    submitBtn.disabled = true;
    submitTimeoutBtn.disabled = true;

    // 타이머 정지
    stopTimer();
    hideTimer();
    hideTimeoutModal();

    // 사용자 인증 확인 (게스트 모드 지원)
    const userId = window.currentUser ? window.currentUser.uid : `guest_${Date.now()}`;
    const isGuest = !window.currentUser;

    // 1. 학생 답안 수집
    const userAnswers = [];
    loadedProblems.forEach(problem => {
        const problemId = problem.problem_id;
        // Radio 또는 Text Input 찾기
        const inputEl = document.querySelector(`input[name="problem-${problemId}"]:checked, input[type="text"][name="problem-${problemId}"]`);
        userAnswers.push({
            problem_id: problemId,
            user_answer: inputEl ? inputEl.value : null // 선택 안하면 null
        });
    });

    // 시간 정보 수집
    const totalTimeSpent = getTotalTimeSpent();
    const isOvertime = totalTimeSpent > TIMER_CONFIG.DURATION;

    // 2. Python 백엔드로 전송
    try {
        const response = await fetch(`${API_URL}/submit_and_analyze`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: userId,  // 로그인 사용자 또는 게스트 ID
                is_guest: isGuest,  // 게스트 여부
                answers: userAnswers,
                test_type: 'level_test',
                grade: null,  // TODO: 사용자 프로필에서 가져오기
                curriculum_category: null,
                target_difficulty: 'Medium',
                total_time_spent: totalTimeSpent,
                time_limit: TIMER_CONFIG.DURATION,
                is_overtime: isOvertime
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `서버 오류: ${response.status}`);
        }

        const data = await response.json();

        // 로딩 모달 숨김
        hideLoadingModal();

        // 3. 결과 표시
        displayResults(data);
        problemSection.classList.add('hidden');
        resultSection.classList.remove('hidden');
        messageDiv.innerHTML = ''; // 성공

    } catch (error) {
        console.error('Error submitting answers:', error);
        hideLoadingModal();
        showMessage(`오류: ${error.message} (Python 서버 로직 확인)`, "red");
        submitBtn.disabled = false;
    }
}

// 결과 페이지 표시
function displayResults(data) {
    // M4: AI 종합 분석
    analysisReportDiv.innerHTML = `
        <h3 class="text-xl font-semibold text-blue-900 mb-2">종합 진단</h3>
        <p class="text-base">${data.ai_analysis_report || "AI 분석 리포트가 없습니다."}</p>
    `;

    // M3: 문항별 해설
    resultDetailsDiv.innerHTML = '<h3 class="text-xl font-semibold text-gray-800 mb-4 border-b pb-2">문항별 상세 해설</h3>';
    data.test_results.forEach((result, index) => {
        const isCorrect = result.is_correct;
        const resultEl = document.createElement('div');
        resultEl.className = `p-5 rounded-lg border-l-4 ${isCorrect ? 'border-green-500 bg-green-50' : 'border-red-500 bg-red-50'}`;
        
        let html = '';
        
        // 문제 텍스트 (렌더링 필요 없음 - 헬퍼 함수가 처리)
        const problemTextHtml = `<b>Q ${index + 1}.</b> ${result.text_latex}`;
        
        if (isCorrect) {
            html = `
                <h4 class="text-lg font-semibold text-green-800">문제 ${index + 1}: 정답 <span class="font-bold">✓</span></h4>
                <div class="problem-text-result mt-2">${problemTextHtml}</div>
                <p class="mt-2 text-green-700"><b>정답:</b> ${result.correct_answer}</p>
            `;
        } else {
            // M3: AI 해설
            html = `
                <h4 class="text-lg font-semibold text-red-800">문제 ${index + 1}: 오답 <span class="font-bold">✗</span></h4>
                <div class="problem-text-result mt-2">${problemTextHtml}</div>
                <p class="mt-2 text-red-700"><b>내 답안:</b> ${result.user_answer || '미제출'} | <b>정답:</b> ${result.correct_answer}</p>
                <div class="mt-4 pt-4 border-t border-red-200">
                    <h5 class="font-semibold text-red-900 mb-2">AI 튜터의 해설</h5>
                    <!--
                        [최종 버그 수정]
                        서버가 보내는 키는 'ai_solution'입니다.
                        'ai_explanation'을 'ai_solution'으로 변경합니다.
                    -->
                    <div class="ai-explanation text-gray-700">${result.ai_solution || "해설 생성 중 오류가 발생했습니다."}</div>
                </div>
            `;
        }
        resultEl.innerHTML = html;
        resultDetailsDiv.appendChild(resultEl);
    });
    
    // 결과 페이지의 모든 문제 텍스트와 AI 해설에 KaTeX 렌더링
    renderKatexInElements(resultDetailsDiv.querySelectorAll('.problem-text-result'));
    renderKatexInElements(resultDetailsDiv.querySelectorAll('.ai-explanation'));
}

// 메시지 표시 유틸리티
function showMessage(message, color) {
    messageDiv.innerHTML = `<p class="text-${color}-600 font-semibold">${message}</p>`;
}

// 여러 요소에 KaTeX를 한 번에 적용하는 헬퍼
function renderKatexInElements(elements) {
    elements.forEach(el => {
        try {
            // KaTeX는 $$...$$ (display) 와 $...$ (inline)을 지원하지 않음.
            // replaceAll을 사용하여 수동으로 렌더링 트리거
            let text = el.innerHTML;
            
            // Display mode ($$)
            text = text.replace(/\$\$([\s\S]*?)\$\$/g, (match, latex) => {
                return katex.renderToString(latex, { displayMode: true, throwOnError: false });
            });
            
            // Inline mode ($)
            text = text.replace(/\$([\s\S]*?)\$/g, (match, latex) => {
                return katex.renderToString(latex, { displayMode: false, throwOnError: false });
            });

            el.innerHTML = text;
        } catch (e) {
            console.warn("Katex rendering error", e);
        }
    });
}
