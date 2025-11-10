/**
 * 애플리케이션 상태 관리
 */
const AppState = {
    // 현재 로드된 문제들
    problems: [],

    // 사용자 답안
    userAnswers: {},

    // 테스트 결과
    testResults: null,

    // AI 분석 리포트
    analysisReport: null,

    // 타이머 상태
    timer: {
        isRunning: false,
        timeRemaining: CONFIG.TIMER.DURATION,
        intervalId: null,
        startTime: null,
        isOvertime: false
    },
    
    /**
     * 문제 설정
     */
    setProblems(problems) {
        this.problems = problems;
    },
    
    /**
     * 문제 가져오기
     */
    getProblems() {
        return this.problems;
    },
    
    /**
     * 답안 설정
     */
    setUserAnswers(answers) {
        this.userAnswers = answers;
    },
    
    /**
     * 답안 가져오기
     */
    getUserAnswers() {
        return this.userAnswers;
    },
    
    /**
     * 결과 설정
     */
    setResults(results, report) {
        this.testResults = results;
        this.analysisReport = report;
    },
    
    /**
     * 결과 가져오기
     */
    getResults() {
        return {
            results: this.testResults,
            report: this.analysisReport
        };
    },
    
    /**
     * 타이머 시작
     */
    startTimer() {
        this.timer.isRunning = true;
        this.timer.startTime = Date.now();
        this.timer.timeRemaining = CONFIG.TIMER.DURATION;
        this.timer.isOvertime = false;
    },

    /**
     * 타이머 정지
     */
    stopTimer() {
        this.timer.isRunning = false;
        if (this.timer.intervalId) {
            clearInterval(this.timer.intervalId);
            this.timer.intervalId = null;
        }
    },

    /**
     * 타이머 업데이트
     */
    decrementTimer() {
        if (this.timer.timeRemaining > 0) {
            this.timer.timeRemaining--;
        } else {
            this.timer.isOvertime = true;
        }
    },

    /**
     * 실제 소요 시간 계산 (초)
     */
    getTotalTimeSpent() {
        if (!this.timer.startTime) return 0;
        return Math.floor((Date.now() - this.timer.startTime) / 1000);
    },

    /**
     * 초과 시간 확인
     */
    isTimerOvertime() {
        return this.timer.isOvertime;
    },

    /**
     * 상태 초기화
     */
    reset() {
        this.problems = [];
        this.userAnswers = {};
        this.testResults = null;
        this.analysisReport = null;
        this.stopTimer();
        this.timer.timeRemaining = CONFIG.TIMER.DURATION;
        this.timer.startTime = null;
        this.timer.isOvertime = false;
    }
};