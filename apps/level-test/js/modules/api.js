/**
 * API 통신 모듈
 */
const API = {
    /**
     * 테스트 문제 로드
     * @returns {Promise<Array>} 문제 리스트
     */
    async loadProblems() {
        try {
            const response = await fetch(`${CONFIG.API_URL}/get_test_problems`);
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `서버 오류: ${response.status}`);
            }
            
            const problems = await response.json();
            
            if (!problems || problems.length === 0) {
                throw new Error(CONFIG.ERROR_MESSAGES.NO_PROBLEMS);
            }
            
            return problems;
            
        } catch (error) {
            console.error('문제 로드 실패:', error);
            throw error;
        }
    },
    
    /**
     * 답안 제출 및 AI 분석 요청
     * @param {Array} answers - 답안 리스트
     * @param {Object} timeInfo - 시간 정보 (optional)
     * @returns {Promise<Object>} 분석 결과
     */
    async submitAnswers(answers, timeInfo = null) {
        try {
            const payload = { answers };

            // 시간 정보가 있으면 추가
            if (timeInfo) {
                payload.total_time_spent = timeInfo.total_time_spent;
                payload.time_limit = timeInfo.time_limit;
                payload.is_overtime = timeInfo.is_overtime;
            }

            const response = await fetch(`${CONFIG.API_URL}/submit_and_analyze`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `서버 오류: ${response.status}`);
            }

            const data = await response.json();
            return data;

        } catch (error) {
            console.error('답안 제출 실패:', error);
            throw error;
        }
    }
};