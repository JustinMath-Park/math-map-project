/**
 * UI 관리 모듈
 */
const UI = {
    // DOM 요소 캐시
    elements: {
        startSection: null,
        problemSection: null,
        resultSection: null,
        problemContainer: null,
        resultDetailsDiv: null,
        analysisReportDiv: null,
        messageDiv: null,
        startBtn: null,
        submitBtn: null,
        timerContainer: null,
        timerDisplay: null,
        modalOverlay: null,
        modalMessage: null,
        timeoutModal: null,
        continueBtn: null,
        submitNowBtn: null
    },
    
    /**
     * DOM 요소 초기화
     */
    init() {
        this.elements = {
            startSection: document.getElementById('start-section'),
            problemSection: document.getElementById('problem-section'),
            resultSection: document.getElementById('result-section'),
            problemContainer: document.getElementById('problem-container'),
            resultDetailsDiv: document.getElementById('result-details'),
            analysisReportDiv: document.getElementById('ai-analysis-report'),
            messageDiv: document.getElementById('message-container'),
            startBtn: document.getElementById('start-test-btn'),
            submitBtn: document.getElementById('submit-btn'),
            timerContainer: document.getElementById('timer-container'),
            timerDisplay: document.getElementById('timer-display'),
            modalOverlay: document.getElementById('modal-overlay'),
            modalMessage: document.getElementById('modal-message'),
            timeoutModal: document.getElementById('timeout-modal'),
            continueBtn: document.getElementById('continue-btn'),
            submitNowBtn: document.getElementById('submit-now-btn')
        };
    },
    
    /**
     * 메시지 표시
     */
    showMessage(message, type = 'blue') {
        this.elements.messageDiv.innerHTML = 
            `<p class="text-${type}-600 font-semibold">${message}</p>`;
    },
    
    /**
     * 메시지 숨김
     */
    hideMessage() {
        this.elements.messageDiv.innerHTML = '';
    },
    
    /**
     * 섹션 전환
     */
    showSection(section) {
        this.elements.startSection.classList.add('hidden');
        this.elements.problemSection.classList.add('hidden');
        this.elements.resultSection.classList.add('hidden');

        // 모든 섹션에서 fade-in 제거
        this.elements.startSection.classList.remove('fade-in');
        this.elements.problemSection.classList.remove('fade-in');
        this.elements.resultSection.classList.remove('fade-in');

        if (section === 'problem') {
            this.elements.problemSection.classList.remove('hidden');
            this.elements.problemSection.classList.add('fade-in');
        } else if (section === 'result') {
            this.elements.resultSection.classList.remove('hidden');
            this.elements.resultSection.classList.add('fade-in');
        } else if (section === 'start') {
            this.elements.startSection.classList.remove('hidden');
            this.elements.startSection.classList.add('fade-in');
        }
    },
    
    /**
     * 버튼 상태 변경
     */
    setButtonState(button, disabled) {
        if (button === 'start') {
            this.elements.startBtn.disabled = disabled;
        } else if (button === 'submit') {
            this.elements.submitBtn.disabled = disabled;
        }
    },
    
    /**
     * 문제 표시
     */
    displayProblems(problems) {
        this.elements.problemContainer.innerHTML = '';
        
        problems.forEach((problem, index) => {
            const problemEl = this.createProblemElement(problem, index);
            this.elements.problemContainer.appendChild(problemEl);
        });
        
        // LaTeX 렌더링
        const textElements = this.elements.problemContainer.querySelectorAll('.problem-text');
        const choiceElements = this.elements.problemContainer.querySelectorAll('.choice-text');
        
        KatexRenderer.renderInElements(textElements);
        KatexRenderer.renderInElements(choiceElements);
    },
    
    /**
     * 문제 요소 생성
     */
    createProblemElement(problem, index) {
        const problemEl = document.createElement('div');
        problemEl.className = 'border p-3 sm:p-4 md:p-5 rounded-lg bg-gray-50';
        problemEl.dataset.problemId = problem.problem_id;

        // 문제 텍스트
        const textEl = document.createElement('div');
        textEl.className = 'problem-text mb-3 sm:mb-4 text-gray-900 text-sm sm:text-base';
        textEl.innerHTML = `<b class="text-base sm:text-lg">Q ${index + 1}.</b> ${problem.text_latex}`;

        // 선택지
        const choicesEl = this.createChoicesElement(problem);

        problemEl.appendChild(textEl);
        problemEl.appendChild(choicesEl);

        return problemEl;
    },
    
    /**
     * 선택지 요소 생성
     */
    createChoicesElement(problem) {
        const choicesEl = document.createElement('div');
        choicesEl.className = 'choices space-y-2 sm:space-y-3';

        if (Array.isArray(problem.choices)) {
            problem.choices.forEach(choice => {
                const choiceMatch = choice.match(/^([A-D])\)\s*(.*)$/);
                const choiceValue = choiceMatch ? choiceMatch[1] : choice;
                const choiceLabel = choice;

                choicesEl.innerHTML += `
                    <label class="block flex items-center p-3 sm:p-3.5 rounded-md border border-gray-300 bg-white hover:bg-blue-50 hover:border-blue-300 cursor-pointer transition-colors min-h-[48px]">
                        <input type="radio" name="problem-${problem.problem_id}" value="${choiceValue}" class="mr-3 w-4 h-4 sm:w-5 sm:h-5 flex-shrink-0">
                        <span class="choice-text text-sm sm:text-base">${choiceLabel}</span>
                    </label>
                `;
            });
        } else if (problem.choices === '주관식') {
            choicesEl.innerHTML = `
                <label class="block">
                    <span class="text-gray-700 text-sm sm:text-base font-medium">주관식 답:</span>
                    <input type="text" name="problem-${problem.problem_id}"
                           class="mt-2 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 p-3 text-sm sm:text-base">
                </label>
            `;
        }

        return choicesEl;
    },
    
     /**
     * 텍스트를 HTML로 안전하게 변환 (줄바꿈, 마크다운 처리)
     */
    
     formatText(text) {
        if (!text) return '';
        
        // 1. 줄바꿈을 <br>로 변환
        let formatted = text.replace(/\n/g, '<br>');
        
        // 2. 마크다운 볼드 처리 (**텍스트** → <strong>텍스트</strong>)
        formatted = formatted.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
        
        return formatted;
    },

    /**
     * 결과 표시
     */
    displayResults(data) {
        // AI 종합 분석
        const formattedReport = this.formatText(data.ai_analysis_report || "AI 분석 리포트가 없습니다.");
        this.elements.analysisReportDiv.innerHTML = `
            <h3 class="text-xl font-semibold text-blue-900 mb-2">종합 진단</h3>
            <div class="text-base">${formattedReport}</div>
        `;

        // 문항별 해설
        this.elements.resultDetailsDiv.innerHTML =
            '<h3 class="text-xl font-semibold text-gray-800 mb-4 border-b pb-2">문항별 상세 해설</h3>';

        data.test_results.forEach((result, index) => {
            const resultEl = this.createResultElement(result, index);
            this.elements.resultDetailsDiv.appendChild(resultEl);

            // 오답 문제에만 해설 토글 버튼 추가
            if (!result.is_correct) {
                this.addExplanationToggle(resultEl, index);
            }
        });

        // LaTeX 렌더링
        const problemTexts = this.elements.resultDetailsDiv.querySelectorAll('.problem-text-result');
        const explanations = this.elements.resultDetailsDiv.querySelectorAll('.ai-explanation');
        const reports = this.elements.analysisReportDiv.querySelectorAll('.text-base');

        KatexRenderer.renderInElements(problemTexts);
        KatexRenderer.renderInElements(explanations);
        KatexRenderer.renderInElements(reports);
    },
    
    /**
     * 결과 요소 생성
     */
    createResultElement(result, index) {
        const isCorrect = result.is_correct;
        const resultEl = document.createElement('div');
        resultEl.className = `p-3 sm:p-4 md:p-5 rounded-lg border-l-4 mb-3 sm:mb-4 ${
            isCorrect ? 'border-green-500 bg-green-50' : 'border-red-500 bg-red-50'
        }`;

        const problemTextHtml = `<b class="text-sm sm:text-base">Q ${index + 1}.</b> ${result.text_latex || '문제 텍스트 없음'}`;

        if (isCorrect) {
            resultEl.innerHTML = `
                <h4 class="text-base sm:text-lg font-semibold text-green-800">
                    문제 ${index + 1}: 정답 <span class="font-bold">✓</span>
                </h4>
                <div class="problem-text-result mt-2 text-sm sm:text-base">${problemTextHtml}</div>
                <p class="mt-2 text-green-700 text-sm sm:text-base"><b>정답:</b> ${result.correct_answer}</p>
            `;
        } else {
            // ⭐ AI 해설을 formatText로 처리
            const formattedSolution = this.formatText(result.ai_solution || "해설 생성 중 오류가 발생했습니다.");

            resultEl.innerHTML = `
                <h4 class="text-base sm:text-lg font-semibold text-red-800">
                    문제 ${index + 1}: 오답 <span class="font-bold">✗</span>
                </h4>
                <div class="problem-text-result mt-2 text-sm sm:text-base">${problemTextHtml}</div>
                <p class="mt-2 text-red-700 text-sm sm:text-base">
                    <b>내 답안:</b> ${result.user_answer || '미제출'} |
                    <b>정답:</b> ${result.correct_answer}
                </p>
                <div class="mt-3 sm:mt-4 pt-3 sm:pt-4 border-t border-red-200">
                    <h5 class="font-semibold text-red-900 mb-2 text-sm sm:text-base">AI 튜터의 해설</h5>
                    <div class="ai-explanation text-gray-700 whitespace-pre-wrap break-words max-w-full overflow-wrap-anywhere text-sm sm:text-base">
                        ${formattedSolution}
                    </div>
                </div>
            `;
        }

        return resultEl;
    },

    /**
     * 타이머 표시
     */
    showTimer() {
        this.elements.timerContainer.classList.remove('hidden');
    },

    /**
     * 타이머 숨김
     */
    hideTimer() {
        this.elements.timerContainer.classList.add('hidden');
    },

    /**
     * 타이머 업데이트
     */
    updateTimer(seconds) {
        const minutes = Math.floor(Math.abs(seconds) / 60);
        const secs = Math.abs(seconds) % 60;
        const sign = seconds < 0 ? '-' : '';
        this.elements.timerDisplay.textContent =
            `${sign}${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;

        // 색상 변경
        this.elements.timerContainer.classList.remove('timer-normal', 'timer-warning', 'timer-danger');
        if (seconds <= 0) {
            this.elements.timerContainer.classList.add('timer-danger');
        } else if (seconds <= CONFIG.TIMER.DANGER_TIME) {
            this.elements.timerContainer.classList.add('timer-danger');
        } else if (seconds <= CONFIG.TIMER.WARNING_TIME) {
            this.elements.timerContainer.classList.add('timer-warning');
        } else {
            this.elements.timerContainer.classList.add('timer-normal');
        }
    },

    /**
     * 모달 표시
     */
    showModal() {
        this.elements.modalOverlay.classList.remove('hidden');
    },

    /**
     * 모달 숨김
     */
    hideModal() {
        this.elements.modalOverlay.classList.add('hidden');
    },

    /**
     * 시간 종료 모달 표시
     */
    showTimeoutModal() {
        this.elements.timeoutModal.classList.remove('hidden');
    },

    /**
     * 시간 종료 모달 숨김
     */
    hideTimeoutModal() {
        this.elements.timeoutModal.classList.add('hidden');
    },

    /**
     * 해설 토글 버튼 추가 (오답 문제에만)
     */
    addExplanationToggle(resultEl, index) {
        const explanationDiv = resultEl.querySelector('.ai-explanation');
        if (!explanationDiv) return;

        // 기본적으로 해설 숨김
        explanationDiv.style.display = 'none';

        // 버튼 생성
        const toggleBtn = document.createElement('button');
        toggleBtn.className = 'mt-2 sm:mt-3 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 active:bg-blue-800 transition text-sm sm:text-base font-medium w-full sm:w-auto';
        toggleBtn.textContent = '해설보기';
        toggleBtn.dataset.visible = 'false';

        // 토글 이벤트
        toggleBtn.addEventListener('click', () => {
            const isVisible = toggleBtn.dataset.visible === 'true';
            if (isVisible) {
                explanationDiv.style.display = 'none';
                toggleBtn.textContent = '해설보기';
                toggleBtn.dataset.visible = 'false';
            } else {
                explanationDiv.style.display = 'block';
                toggleBtn.textContent = '해설 닫기';
                toggleBtn.dataset.visible = 'true';
            }
        });

        // 버튼을 해설 앞에 삽입
        explanationDiv.parentElement.insertBefore(toggleBtn, explanationDiv);
    }
};
