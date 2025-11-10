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
     * 상태 초기화
     */
    reset() {
        this.problems = [];
        this.userAnswers = {};
        this.testResults = null;
        this.analysisReport = null;
    }
};