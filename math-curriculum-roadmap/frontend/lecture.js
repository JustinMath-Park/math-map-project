const params = new URLSearchParams(window.location.search);
const lectureId = params.get('lectureId');
const API_BASE = window.Config?.API_BASE || '';

const FALLBACK_LECTURES = {
  default: {
    title: '강의 콘텐츠 준비 중',
    video_url: '',
    objectives: ['선택한 주제의 강의가 준비되는 대로 이곳에서 볼 수 있습니다.'],
    outline: [
      { label: 'Preview', description: '해당 주제의 핵심 개념과 풀이 전략을 곧 공개할 예정입니다.' },
      { label: 'Practice', description: '실전 적용 문제와 해설이 추가될 예정입니다.' }
    ],
    notes: ['문의 사항이 있다면 대시보드에서 알려주세요.']
  }
};

const titleEl = document.getElementById('lectureTitle');
const videoEl = document.getElementById('lectureVideo');
const objectivesEl = document.getElementById('objectiveList');
const outlineEl = document.getElementById('outlineList');
const noteEl = document.getElementById('noteList');
const backBtn = document.getElementById('backBtn');

async function fetchLecture(id) {
  const resp = await fetch(`${API_BASE}/lectures/${id}`);
  if (!resp.ok) throw new Error('강의를 불러올 수 없습니다.');
  return resp.json();
}

function renderLecture(data) {
  titleEl.textContent = data.title || 'Lecture';
  document.title = `${data.title || 'Lecture'} - Mathiter`;
  if (data.video_url) {
    videoEl.src = data.video_url;
    videoEl.style.display = 'block';
  } else {
    videoEl.style.display = 'none';
  }

  objectivesEl.innerHTML = (data.objectives || [])
    .map((obj) => `<li>${obj}</li>`)
    .join('') || '<li>학습 목표가 곧 추가될 예정입니다.</li>';

  outlineEl.innerHTML = (data.outline || [])
    .map(
      (step) => `<div class="outline-card">
        <span>${step.label}</span>
        <p class="math-text">${step.description}</p>
      </div>`
    )
    .join('');

  noteEl.innerHTML = (data.notes || ['곧 강의 필기가 올라옵니다.'])
    .map((note) => `<p class="math-text">${note}</p>`)
    .join('');

  if (typeof KatexRenderer !== 'undefined') {
    const mathNodes = document.querySelectorAll('.math-text');
    KatexRenderer.renderInElements(mathNodes);
  }
}

async function init() {
  if (!lectureId) {
    titleEl.textContent = '강의 ID가 전달되지 않았습니다.';
    return;
  }
  try {
    const data = await fetchLecture(lectureId);
    renderLecture(data);
  } catch (error) {
    console.error(error);
    renderLecture(FALLBACK_LECTURES.default);
  }
}

if (backBtn) {
  backBtn.addEventListener('click', () => {
    if (document.referrer) {
      window.history.back();
    } else {
      window.location.href = 'index.html';
    }
  });
}

init();
