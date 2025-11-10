/**
 * 메인 애플리케이션
 */
const App = {
    /**
     * 앱 초기화
     */
    init() {
        console.log('AI Math Test 애플리케이션 시작');
        
        // UI 초기화
        UI.init();
        
        // 이벤트 리스너 등록
        this.attachEventListeners();
        
        console.log('초기화 완료');
    },
    
    /**
     * 이벤트 리스너 등록
     */
    attachEventListeners() {
        UI.elements.startBtn.addEventListener('click', () => this.handleStartTest());
        UI.elements.submitBtn.addEventListener('click', () => this.handleSubmit());
    },
    
    /**
     * 테스트 시작 핸들러
     */
    async handleStartTest() {
        UI.showMessage(CONFIG.LOADING_MESSAGES.LOADING_PROBLEMS, 'blue');
        UI.setButtonState('start', true);
        
        try {
            // API로부터 문제 로드
            const problems = await API.loadProblems();
            
            // 상태에 저장
            AppState.setProblems(problems);
            
            // UI에 표시
            UI.displayProblems(problems);
            UI.showSection('problem');
            UI.hideMessage();

            // ⭐ 문제 섹션 시작 부분으로 스크롤
            window.scrollTo({ top: 0, behavior: 'smooth' });
            
            console.log(`${problems.length}개 문제 로드 완료`);
            
            
        } catch (error) {
            UI.showMessage(`오류: ${error.message}`, 'red');
            UI.setButtonState('start', false);
            console.error('문제 로드 실패:', error);
        }
    },
    
    /**
     * 답안 제출 핸들러
     */
    async handleSubmit() {
        UI.showMessage(CONFIG.LOADING_MESSAGES.SUBMITTING, 'blue');
        UI.setButtonState('submit', true);
        
        try {
            // 답안 수집
            const answers = this.collectAnswers();
            
            if (answers.length === 0) {
                throw new Error(CONFIG.ERROR_MESSAGES.NO_ANSWERS);
            }
            
            // 상태에 저장
            AppState.setUserAnswers(answers);
            
            // API로 제출
            const data = await API.submitAnswers(answers);
            
            // 상태에 결과 저장
            AppState.setResults(data.test_results, data.ai_analysis_report);
            
            // UI에 결과 표시
            UI.displayResults(data);
            UI.showSection('result');
            UI.hideMessage();

            // ⭐ 결과 페이지 맨 위로 스크롤
            window.scrollTo({ top: 0, behavior: 'smooth' });
            
            console.log('답안 제출 및 분석 완료');
            
        } catch (error) {
            UI.showMessage(`오류: ${error.message}`, 'red');
            UI.setButtonState('submit', false);
            console.error('답안 제출 실패:', error);
        }
    },
    
    /**
     * 답안 수집
     */
    collectAnswers() {
        const problems = AppState.getProblems();
        const answers = [];
        
        problems.forEach(problem => {
            const problemId = problem.problem_id;
            
            // Radio 또는 Text Input 찾기
            const checkedRadio = document.querySelector(
                `input[name="problem-${problemId}"]:checked`
            );
            const textInput = document.querySelector(
                `input[type="text"][name="problem-${problemId}"]`
            );
            
            const inputEl = checkedRadio || textInput;
            
            if (inputEl && inputEl.value) {
                answers.push({
                    problem_id: problemId,
                    user_answer: inputEl.value
                });
            }
        });
        
        console.log(`${answers.length}개 답안 수집됨`);
        return answers;
    }
};

// DOM 로드 완료 후 앱 시작
document.addEventListener('DOMContentLoaded', () => {
    App.init();
});