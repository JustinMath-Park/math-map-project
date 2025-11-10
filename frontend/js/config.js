const CONFIG = {
    // Cloud Run 백엔드 URL로 변경
    API_URL: 'https://my-mvp-backend-1093137562151.asia-northeast3.run.app',

    KATEX_VERSION: '0.16.9',
    KATEX_OPTIONS: {
        throwOnError: false,
        displayMode: false
    },

    TIMER: {
        DURATION: 1800,      // 30분 = 1800초
        WARNING_TIME: 300,   // 5분 = 300초 (주황색 경고)
        DANGER_TIME: 60      // 1분 = 60초 (빨간색 경고)
    },

    LOADING_MESSAGES: {
        LOADING_PROBLEMS: '문제를 불러오는 중입니다...',
        SUBMITTING: '답안 제출 중... AI가 분석하고 있습니다...'
    },

    ERROR_MESSAGES: {
        NO_PROBLEMS: 'DB에서 문제를 불러오지 못했습니다.',
        NO_ANSWERS: '제출된 답안이 없습니다.',
        SERVER_ERROR: '서버 오류가 발생했습니다.'
    }
};