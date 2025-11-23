export const translations = {
    en: {
        appTitle: "Mathiter Level Test",
        progress: "Progress",

        // Onboarding
        startTitle: "Start Your Assessment",
        startDesc: "We'll adapt to your level to find the perfect curriculum for you.",
        labelSystem: "Curriculum System",
        labelGrade: "Current Grade / Year",
        usSystem: "US System",
        usDesc: "(Common Core, AP)",
        ukSystem: "UK System",
        ukDesc: "(IGCSE, A-Level)",
        btnStart: "Start Test",

        // Question
        topic: "Topic",
        difficulty: "Difficulty",
        btnSubmit: "Submit Answer",

        // Loading
        analyzingTitle: "Analyzing your answer...",
        analyzingDesc: "Our AI is adjusting the difficulty for you.",

        // Result
        resultTitle: "Assessment Complete!",
        resultDesc: "We have analyzed your math skills and found the perfect starting point.",
        recTitle: "Recommendation",
        recLabel: "Recommended",
        btnGoToCurriculum: "View My Curriculum Map"
    },
    kr: {
        appTitle: "Mathiter 레벨 테스트",
        progress: "진행률",

        // Onboarding
        startTitle: "진단 평가 시작하기",
        startDesc: "학생의 실력을 분석하여 최적의 커리큘럼을 찾아드립니다.",
        labelSystem: "커리큘럼 시스템",
        labelGrade: "현재 학년",
        usSystem: "미국식 (US)",
        usDesc: "(Common Core, AP)",
        ukSystem: "영국식 (UK)",
        ukDesc: "(IGCSE, A-Level)",
        btnStart: "테스트 시작",

        // Question
        topic: "토픽",
        difficulty: "난이도",
        btnSubmit: "정답 제출",

        // Loading
        analyzingTitle: "답안 분석 중...",
        analyzingDesc: "AI가 난이도를 조절하고 있습니다.",

        // Result
        resultTitle: "진단 완료!",
        resultDesc: "수학 실력 분석이 완료되었습니다. 맞춤형 시작점을 확인하세요.",
        recTitle: "추천 커리큘럼",
        recLabel: "추천",
        btnGoToCurriculum: "내 커리큘럼 맵 보기"
    }
};

export function updateLanguage(lang) {
    const t = translations[lang];
    if (!t) return;

    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (t[key]) {
            el.textContent = t[key];
        }
    });

    // Update specific placeholders if needed
    // document.getElementById('some-input').placeholder = t.somePlaceholder;
}
