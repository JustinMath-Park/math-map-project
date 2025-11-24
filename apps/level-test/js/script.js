const API_BASE_URL = 'https://my-mvp-backend-1093137562151.asia-northeast3.run.app';
let curriculumData = null;

// DOM Elements
const elements = {
    loading: document.getElementById('loading'),
    error: document.getElementById('error'),
    curriculumList: document.getElementById('curriculum-list'),
    curriculumGrid: document.getElementById('curriculum-grid'),
    curriculumDetail: document.getElementById('curriculum-detail')
};

// Initialize App
document.addEventListener('DOMContentLoaded', loadCurriculums);

/**
 * Fetch and display the list of curriculums
 */
async function loadCurriculums() {
    try {
        const response = await fetch(`${API_BASE_URL}/curriculums`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();

        elements.loading.style.display = 'none';
        elements.curriculumList.style.display = 'block';

        displayCurriculumList(data);
    } catch (error) {
        console.error('Failed to load curriculums:', error);
        elements.loading.style.display = 'none';
        elements.error.textContent = '커리큘럼 데이터를 불러오는데 실패했습니다: ' + error.message;
        elements.error.style.display = 'block';
    }
}

/**
 * Render the curriculum cards
 */
function displayCurriculumList(curriculums) {
    elements.curriculumGrid.innerHTML = '';

    curriculums.forEach(curriculum => {
        const card = document.createElement('div');
        card.className = 'curriculum-card';
        card.onclick = () => loadCurriculumDetail(curriculum.curriculum_id);

        card.innerHTML = `
            <h3>${curriculum.exam_type}</h3>
            <div class="subject">${curriculum.subject}</div>
            <div class="version">${curriculum.version}</div>
            <div class="description">${curriculum.description}</div>
        `;

        elements.curriculumGrid.appendChild(card);
    });
}

/**
 * Fetch and display details for a specific curriculum
 */
async function loadCurriculumDetail(curriculumId) {
    try {
        elements.loading.style.display = 'flex'; // Changed to flex for centering
        elements.curriculumList.style.display = 'none';
        elements.curriculumDetail.classList.remove('active');

        const response = await fetch(`${API_BASE_URL}/curriculums/${curriculumId}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        curriculumData = await response.json();

        elements.loading.style.display = 'none';
        displayCurriculumDetail(curriculumData);
    } catch (error) {
        console.error('Failed to load curriculum details:', error);
        elements.loading.style.display = 'none';
        elements.error.textContent = '커리큘럼 상세 정보를 불러오는데 실패했습니다: ' + error.message;
        elements.error.style.display = 'block';
        
        // Show list again if detail fails
        elements.curriculumList.style.display = 'block';
    }
}

/**
 * Render the curriculum detail view
 */
function displayCurriculumDetail(curriculum) {
    elements.curriculumDetail.classList.add('active');

    let html = `
        <button class="back-button" onclick="goBack()">
            <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"/>
            </svg>
            목록으로 돌아가기
        </button>
        <div class="detail-header">
            <h2>${curriculum.exam_type} - ${curriculum.subject}</h2>
            <div class="meta">
                <strong>버전:</strong> ${curriculum.version}<br>
                <strong>설명:</strong> ${curriculum.description}
            </div>
    `;

    // Test Format Info
    if (curriculum.test_format) {
        html += `
            <div style="margin-top: 15px;">
                <span class="badge">총 문항: ${curriculum.test_format.total_questions}개</span>
                <span class="badge">시험 시간: ${curriculum.test_format.time_limit_minutes}분</span>
                ${curriculum.test_format.calculator_allowed ? `<span class="badge">계산기: ${curriculum.test_format.calculator_allowed}</span>` : ''}
            </div>
        `;
    }

    html += `</div>`;

    // Domains and Topics
    if (curriculum.domains) {
        curriculum.domains.forEach(domain => {
            html += `
                <div class="domain">
                    <h3>${domain.name}</h3>
                    <div class="domain-meta">
                        ${domain.description}<br>
                        ${domain.weight ? `<strong>비중:</strong> ${domain.weight}` : ''}
                    </div>
            `;

            if (domain.topics) {
                domain.topics.forEach(topic => {
                    html += `
                        <div class="topic">
                            <h4>${topic.name}</h4>
                    `;

                    // Level Info (IGCSE)
                    if (topic.core_level !== undefined) {
                        html += `<div style="margin-bottom: 10px; color: #666;">`;
                        if (topic.core_level) html += `<span class="badge">Core</span>`;
                        if (topic.extended_level) html += `<span class="badge">Extended</span>`;
                        html += `</div>`;
                    }

                    // Subtopics
                    if (topic.subtopics && topic.subtopics.length > 0) {
                        html += `<ul class="subtopics">`;
                        topic.subtopics.forEach(subtopic => {
                            html += `<li>${subtopic}</li>`;
                        });
                        html += `</ul>`;
                    }

                    html += `</div>`;
                });
            }

            html += `</div>`;
        });
    }

    elements.curriculumDetail.innerHTML = html;
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

/**
 * Return to the list view
 */
function goBack() {
    elements.curriculumDetail.classList.remove('active');
    elements.curriculumList.style.display = 'block';
    
    // Clear error if any
    elements.error.style.display = 'none';
}

// Expose goBack to global scope for the button onclick
window.goBack = goBack;
