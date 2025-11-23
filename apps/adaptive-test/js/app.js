import { initializeApp } from 'https://www.gstatic.com/firebasejs/10.8.0/firebase-app.js';
import { getAuth, onAuthStateChanged } from 'https://www.gstatic.com/firebasejs/10.8.0/firebase-auth.js';
import { updateLanguage } from './i18n.js';

// --- State Management ---
const state = {
    sessionId: null,
    currentQuestion: null,
    questionCount: 0,
    totalQuestions: 25,
    language: 'en', // Default language
    userContext: {
        system: 'US',
        grade: 'G9'
    }
};

// --- DOM Elements ---
const els = {
    app: document.getElementById('app'),
    onboardingSection: document.getElementById('onboarding-section'),
    onboardingForm: document.getElementById('onboarding-form'),
    gradeSelect: document.getElementById('grade-select'),

    questionSection: document.getElementById('question-section'),
    questionTopic: document.getElementById('question-topic'),
    questionDifficulty: document.getElementById('question-difficulty'),
    questionText: document.getElementById('question-text'),
    choicesContainer: document.getElementById('choices-container'),
    submitBtn: document.getElementById('submit-answer-btn'),

    loadingSection: document.getElementById('loading-section'),
    loadingTitle: document.getElementById('loading-title'),

    resultSection: document.getElementById('result-section'),
    recommendationText: document.getElementById('recommendation-text'),
    recCourse: document.getElementById('rec-course'),
    recModule: document.getElementById('rec-module'),
    goToCurriculumBtn: document.getElementById('go-to-curriculum-btn'),

    progressContainer: document.getElementById('progress-container'),
    progressBar: document.getElementById('progress-bar'),
    progressText: document.getElementById('progress-text'),

    langEnBtn: document.getElementById('lang-en'),
    langKrBtn: document.getElementById('lang-kr')
};

// --- Initialization ---
function init() {
    document.getElementById('app-version').textContent = CONFIG.VERSION;
    populateGrades();
    setupEventListeners();
    setLanguage('en'); // Initial render
}

function populateGrades() {
    const grades = [
        { value: 'G7', label: 'Grade 7 / Year 8' },
        { value: 'G8', label: 'Grade 8 / Year 9' },
        { value: 'G9', label: 'Grade 9 / Year 10' },
        { value: 'G10', label: 'Grade 10 / Year 11' },
        { value: 'G11', label: 'Grade 11 / Year 12' },
        { value: 'G12', label: 'Grade 12 / Year 13' }
    ];

    els.gradeSelect.innerHTML = grades.map(g =>
        `<option value="${g.value}">${g.label}</option>`
    ).join('');
}

function setupEventListeners() {
    els.onboardingForm.addEventListener('submit', handleStartTest);
    els.submitBtn.addEventListener('click', handleSubmitAnswer);
    els.goToCurriculumBtn.addEventListener('click', () => {
        window.location.href = 'https://mathiter-curriculum.web.app'; // TODO: Add query params
    });

    els.langEnBtn.addEventListener('click', () => setLanguage('en'));
    els.langKrBtn.addEventListener('click', () => setLanguage('kr'));
}

function setLanguage(lang) {
    state.language = lang;
    updateLanguage(lang);

    // Update Toggle UI
    if (lang === 'en') {
        els.langEnBtn.className = "px-3 py-1 rounded-full text-xs font-bold bg-white shadow-sm text-blue-600 transition";
        els.langKrBtn.className = "px-3 py-1 rounded-full text-xs font-bold text-gray-500 hover:text-gray-700 transition";
    } else {
        els.langEnBtn.className = "px-3 py-1 rounded-full text-xs font-bold text-gray-500 hover:text-gray-700 transition";
        els.langKrBtn.className = "px-3 py-1 rounded-full text-xs font-bold bg-white shadow-sm text-blue-600 transition";
    }
}

// --- Event Handlers ---

async function handleStartTest(e) {
    e.preventDefault();

    const formData = new FormData(els.onboardingForm);
    state.userContext.system = formData.get('system');
    state.userContext.grade = els.gradeSelect.value;

    showLoading("Initializing Test...");

    // Generate a random user ID for guest session if not exists
    if (!state.userContext.userId) {
        state.userContext.userId = 'guest_' + Math.random().toString(36).substr(2, 9);
    }

    // Map system to curriculum_category
    const categoryMap = {
        'US': 'Common Core',
        'UK': 'IGCSE'
    };
    const curriculumCategory = categoryMap[state.userContext.system] || 'General';

    try {
        const response = await fetch(`${CONFIG.API_BASE_URL}/api/adaptive-test/start`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: state.userContext.userId,
                grade: state.userContext.grade,
                curriculum_category: curriculumCategory,
                test_type: 'adaptive_test'
            })
        });

        if (!response.ok) throw new Error('Failed to start test');

        const data = await response.json();
        state.sessionId = data.session_id;
        state.totalQuestions = data.total_questions;

        loadNextQuestion(data.first_question);

    } catch (error) {
        console.error(error);
        alert('Error starting test. Please try again.');
        showSection('onboarding-section');
    }
}

async function handleSubmitAnswer() {
    const selectedChoice = document.querySelector('input[name="choice"]:checked');
    if (!selectedChoice) return;

    const answer = selectedChoice.value;

    showLoading("Analyzing answer...");

    try {
        const response = await fetch(`${CONFIG.API_BASE_URL}/api/adaptive-test/submit`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: state.userContext.userId,
                session_id: state.sessionId,
                question_id: state.currentQuestion.id,
                answer: answer
            })
        });

        if (!response.ok) throw new Error('Failed to submit answer');

        const data = await response.json();

        if (data.is_finished) {
            showResults(data.results);
        } else {
            loadNextQuestion(data.next_question);
        }

    } catch (error) {
        console.error(error);
        alert('Error submitting answer.');
        showSection('question-section');
    }
}

// --- UI Functions ---

function loadNextQuestion(question) {
    state.currentQuestion = question;
    state.questionCount++;

    updateProgress();

    // Update UI
    els.questionTopic.textContent = question.topic;
    els.questionDifficulty.textContent = question.difficulty;
    els.questionText.innerHTML = question.text_latex; // Will be rendered by KaTeX

    // Render Choices
    els.choicesContainer.innerHTML = question.choices.map((choice, idx) => `
        <label class="choice-label block p-4 border rounded-lg cursor-pointer transition border-gray-200">
            <div class="flex items-center">
                <input type="radio" name="choice" value="${choice.id}" class="choice-input sr-only">
                <div class="w-6 h-6 rounded-full border border-gray-300 flex items-center justify-center mr-3 text-sm font-bold text-gray-500 peer-checked:border-blue-600 peer-checked:text-blue-600">
                    ${String.fromCharCode(65 + idx)}
                </div>
                <span class="choice-text">${choice.text}</span>
            </div>
        </label>
    `).join('');

    // Enable/Disable submit button based on selection
    els.submitBtn.disabled = true;
    const inputs = els.choicesContainer.querySelectorAll('input');
    inputs.forEach(input => {
        input.addEventListener('change', () => {
            els.submitBtn.disabled = false;

            // Visual feedback for selection
            document.querySelectorAll('.choice-label').forEach(label => {
                label.classList.remove('border-blue-600', 'bg-blue-50', 'ring-2', 'ring-blue-200');
                label.classList.add('border-gray-200');
            });

            const selectedLabel = input.closest('.choice-label');
            selectedLabel.classList.remove('border-gray-200');
            selectedLabel.classList.add('border-blue-600', 'bg-blue-50', 'ring-2', 'ring-blue-200');
        });
    });

    // Render KaTeX
    renderMathInElement(els.questionText, {
        delimiters: [
            { left: '$$', right: '$$', display: true },
            { left: '$', right: '$', display: false }
        ]
    });

    document.querySelectorAll('.choice-text').forEach(el => {
        renderMathInElement(el, {
            delimiters: [{ left: '$', right: '$', display: false }]
        });
    });

    showSection('question-section');
}

function showResults(results) {
    els.recommendationText.textContent = results.recommendation_text;
    els.recCourse.textContent = results.recommended_course;
    els.recModule.textContent = results.recommended_module;

    showSection('result-section');

    // Render Topic Analysis
    const topicContainer = document.getElementById('topic-analysis-container');
    if (results.topic_analysis && topicContainer) {
        topicContainer.innerHTML = results.topic_analysis.map(topic => `
            <div class="flex items-center justify-between bg-gray-50 p-3 rounded-lg">
                <span class="font-medium text-gray-700">${topic.topic}</span>
                <div class="flex items-center">
                    <div class="w-24 h-2 bg-gray-200 rounded-full mr-3">
                        <div class="h-2 bg-blue-500 rounded-full" style="width: ${topic.accuracy}%"></div>
                    </div>
                    <span class="text-sm font-bold text-gray-600">${topic.accuracy}%</span>
                </div>
            </div>
        `).join('');
    }

    // Render Answer History
    const historyContainer = document.getElementById('answer-history-container');
    if (results.answer_history && historyContainer) {
        historyContainer.innerHTML = results.answer_history.map((ans, idx) => `
            <div class="flex items-center justify-between p-3 border rounded-lg ${ans.is_correct ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50 cursor-pointer hover:bg-red-100 transition-colors'}" 
                 ${!ans.is_correct ? `onclick="showSolution('${idx}')"` : ''}>
                <div class="flex items-center">
                    <span class="w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold mr-3 ${ans.is_correct ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}">
                        ${idx + 1}
                    </span>
                    <div>
                        <div class="text-sm font-medium text-gray-900">${ans.topic}</div>
                        <div class="text-xs text-gray-500">${ans.difficulty}</div>
                    </div>
                </div>
                <div class="flex items-center">
                    <span class="text-sm font-bold ${ans.is_correct ? 'text-green-600' : 'text-red-600'} mr-2">
                        ${ans.is_correct ? 'Correct' : 'Incorrect'}
                    </span>
                    ${!ans.is_correct ? '<span class="text-xs text-blue-600 underline">View Solution</span>' : ''}
                </div>
            </div>
        `).join('');

        // Store history for modal access
        window.currentHistory = results.answer_history;
    }
}

// Modal Functions
window.showSolution = function (index) {
    const item = window.currentHistory[index];
    if (!item) return;

    const modal = document.getElementById('solution-modal');
    const qText = document.getElementById('modal-question-text');
    const expText = document.getElementById('modal-explanation-text');

    // Render LaTeX in modal
    qText.innerHTML = item.text_latex; // Assuming KaTeX will auto-render or we need to call it
    expText.innerHTML = item.explanation || "No explanation available.";

    modal.classList.remove('hidden');

    // Re-render KaTeX in modal
    renderMathInElement(modal, {
        delimiters: [
            { left: "$$", right: "$$", display: true },
            { left: "$", right: "$", display: false }
        ]
    });
};

// Modal Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('solution-modal');
    const closeBtn = document.getElementById('close-modal-btn');
    const okBtn = document.getElementById('modal-ok-btn');

    const closeModal = () => modal.classList.add('hidden');

    if (closeBtn) closeBtn.addEventListener('click', closeModal);
    if (okBtn) okBtn.addEventListener('click', closeModal);

    // Close on outside click
    if (modal) {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) closeModal();
        });
    }
});

function updateProgress() {
    els.progressContainer.classList.remove('hidden');
    const percent = (state.questionCount / state.totalQuestions) * 100;
    els.progressBar.style.width = `${percent}%`;
    els.progressText.textContent = `${state.questionCount}/${state.totalQuestions}`;
}

function showSection(sectionId) {
    ['onboarding-section', 'question-section', 'loading-section', 'result-section'].forEach(id => {
        document.getElementById(id).classList.add('hidden');
    });
    document.getElementById(sectionId).classList.remove('hidden');
}

function showLoading(message) {
    els.loadingTitle.textContent = message;
    showSection('loading-section');
}

// Start
init();
