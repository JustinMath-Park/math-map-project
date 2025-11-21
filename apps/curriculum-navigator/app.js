// Use Config from config.js
const APP_VERSION = window.Config?.APP_VERSION || 'v0.3.2';
const API_ENDPOINT = window.Config?.CURRICULUMS_ENDPOINT || './data/curriculums.json';
const LOCAL_DATA_URL = window.Config?.LOCAL_CURRICULUMS || './data/curriculums.json';
const EXAM_ORDER = [
  'igcse-mathematics',
  'igcse-additional-mathematics-(0606)',
  'sat-mathematics',
  'alevel-mathematics',
  'ap-calculus-ab/bc'
];

const slugify = (value) =>
  (value || '')
    .toString()
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '');

const examListEl = document.getElementById('examList');
const domainRoadmapEl = document.getElementById('domainRoadmap');
const lessonTitleEl = document.getElementById('lessonTitle');
const lessonSummaryEl = document.getElementById('lessonSummary');
const lessonObjectivesEl = document.getElementById('lessonObjectives');
const lessonExampleEl = document.getElementById('lessonExample');
const lessonActionBtn = document.getElementById('lessonActionBtn');
const examLabelEl = document.getElementById('roadmapExamLabel');
const examTitleEl = document.getElementById('roadmapExamTitle');
const examDescEl = document.getElementById('roadmapExamDesc');

let curriculumData = {};
let selectedExamId = null;
let selectedTopic = null;
let expandedDomainId = null;
let currentLectureId = null;

const versionEl = document.getElementById('appVersion');
if (versionEl) versionEl.textContent = APP_VERSION;

async function loadData() {
  try {
    curriculumData = await fetchFromApi();
  } catch (error) {
    console.warn('API 호출 실패, 로컬 데이터 사용', error);
    try {
      curriculumData = await fetchLocalJson();
    } catch (err) {
      console.warn('로컬 파일 로딩 실패, 샘플 데이터 사용', err);
      curriculumData = window.FALLBACK_DATA;
    }
  } finally {
    const firstExam = Object.keys(curriculumData)[0];
    selectedExamId = firstExam;
    renderExamList();
    renderRoadmap();
  }
}

async function fetchFromApi() {
  const resp = await fetch(API_ENDPOINT);
  if (!resp.ok) throw new Error(`API (${API_ENDPOINT}) 응답 오류`);
  const data = await resp.json();
  return normalizeData(data);
}

async function fetchLocalJson() {
  const resp = await fetch(LOCAL_DATA_URL);
  if (!resp.ok) throw new Error('로컬 JSON 로딩 실패');
  const data = await resp.json();
  return normalizeData(data);
}

function canonicalSubject(examType, subject) {
  const normalized = (subject || '').trim().toLowerCase();
  if (!normalized) return 'general';
  if (['math', 'mathematics'].includes(normalized)) return 'mathematics';
  return normalized;
}

function normalizeData(data) {
  if (!data) return {};
  if (!Array.isArray(data)) return data;
  const map = {};

  const topicCount = (curr) =>
    (curr?.domains || []).reduce((sum, domain) => sum + ((domain?.topics || []).length), 0);

  data.forEach((item) => {
    if (!item || !Array.isArray(item.domains) || item.domains.length === 0) return;

    const examNormalized = slugify(item.exam_type || 'exam');
    const subjectNormalized = slugify(canonicalSubject(item.exam_type, item.subject));
    const examKey = `${examNormalized}-${subjectNormalized}`;
    const fallbackKey = item.curriculum_id || `curriculum-${Object.keys(map).length}`;
    const key = examKey || fallbackKey;

    const shouldReplace = !map[key] || topicCount(item) > topicCount(map[key]);
    if (shouldReplace) {
      map[key] = {
        ...item,
        curriculum_id: item.curriculum_id || fallbackKey
      };
    }
  });

  return map;
}

function renderExamList() {
  const orderedEntries = Object.entries(curriculumData).sort(([keyA], [keyB]) => {
    const idxA = EXAM_ORDER.indexOf(keyA);
    const idxB = EXAM_ORDER.indexOf(keyB);
    if (idxA === -1 && idxB === -1) return keyA.localeCompare(keyB);
    if (idxA === -1) return 1;
    if (idxB === -1) return -1;
    return idxA - idxB;
  });

  examListEl.innerHTML = orderedEntries
    .map(([id, exam]) => {
      return `<article class="exam-card ${id === selectedExamId ? 'active' : ''}" data-id="${id}">
        <h3>${exam.exam_type} · ${exam.subject}</h3>
        <p>${exam.description ?? ''}</p>
      </article>`;
    })
    .join('');

  examListEl.querySelectorAll('.exam-card').forEach((card) => {
    card.addEventListener('click', () => {
      selectedExamId = card.dataset.id;
      selectedTopic = null;
      expandedDomainId = null;
      renderExamList();
      renderRoadmap();
    });
  });
}

function renderRoadmap() {
  const exam = curriculumData[selectedExamId];
  if (!exam) return;
  const curriculumDocId = exam.curriculum_id || selectedExamId;

  const getDomainId = (domain, fallback) =>
    domain.id || domain.domain_id || domain.name || `domain-${fallback}`;
  const firstDomainId = exam.domains?.[0] ? slugify(getDomainId(exam.domains[0], 0)) : null;
  if (
    !expandedDomainId ||
    !exam.domains?.some((d, index) => slugify(getDomainId(d, index)) === expandedDomainId)
  ) {
    expandedDomainId = firstDomainId || null;
  }

  examLabelEl.textContent = exam.exam_type;
  examTitleEl.textContent = `${exam.subject} ${exam.version}`;
  examDescEl.textContent = exam.description || '';

  domainRoadmapEl.innerHTML = exam.domains
    .map((domain, idx) => {
      const domainId = slugify(getDomainId(domain, idx));
      const topics = domain.topics || [];
      const nodes = topics
        .map((topic, tIdx) => {
          const topicId = slugify(topic.id || topic.topic_id || tIdx);
          const nodeId = `${domainId}-${topicId}`;
          const active = selectedTopic === nodeId;
          const title = topic.title || topic.name || `토픽 ${tIdx + 1}`;
          const summary = topic.summary || topic.description || '';
          const objectives = topic.objectives || topic.subtopics || [];
          const examples = topic.examples || [];
          const lectureId = `${curriculumDocId}-${domainId}-${topicId}`;
          return `<button class="node-btn ${active ? 'active' : ''}" data-node="${nodeId}" data-domain="${domainId}" data-title="${title}" data-summary="${summary}" data-objectives='${JSON.stringify(objectives)}' data-examples='${JSON.stringify(examples)}' data-lecture="${lectureId}">
              <span class="badge">STEP ${tIdx + 1}</span>
              <strong>${title}</strong>
            </button>`;
        })
        .join('');

      const expanded = domainId === expandedDomainId;
      return `<div class="domain-block ${expanded ? 'expanded' : ''}">
        <button class="domain-header" data-domain="${domainId}">
          <div>
            <p class="eyebrow">LEVEL ${idx + 1}</p>
            <h4>${domain.name}</h4>
            <p class="domain-summary">${domain.summary || domain.description || ''}</p>
          </div>
          <span class="chevron">${expanded ? '−' : '+'}</span>
        </button>
        <div class="domain-content ${expanded ? 'open' : ''}">
          <div class="node-track">${nodes || '<em>토픽이 준비 중입니다.</em>'}</div>
        </div>
      </div>`;
    })
    .join('');

  domainRoadmapEl.querySelectorAll('.domain-header').forEach((header) => {
    header.addEventListener('click', () => {
      expandedDomainId = header.dataset.domain;
      renderRoadmap();
    });
  });

  domainRoadmapEl.querySelectorAll('.node-btn').forEach((btn) => {
    btn.addEventListener('click', () => {
      selectedTopic = btn.dataset.node;
      updateLessonPreview({
        title: btn.dataset.title,
        summary: btn.dataset.summary,
        objectives: JSON.parse(btn.dataset.objectives || '[]'),
        examples: JSON.parse(btn.dataset.examples || '[]'),
        lectureId: btn.dataset.lecture
      });
      renderRoadmap();
    });
  });

  if (!selectedTopic) {
    lessonTitleEl.textContent = '도메인을 선택해 시작해 보세요';
    lessonSummaryEl.textContent = '각 노드는 독립된 강의 입구입니다. 클릭하면 연계 강의/문제 페이지로 이동하게 됩니다.';
    lessonObjectivesEl.textContent = '';
    lessonExampleEl.textContent = '';
    lessonActionBtn.disabled = true;
  }
}

function updateLessonPreview({ title, summary, objectives, examples, lectureId }) {
  lessonTitleEl.textContent = title || '노드 상세';
  lessonSummaryEl.textContent = summary || 'AI 튜터와 함께 학습을 시작할 수 있습니다.';
  lessonObjectivesEl.textContent = objectives.length
    ? `학습 목표: ${objectives.join(', ')}`
    : '';
  lessonExampleEl.textContent = examples.length
    ? `예시 문제: ${examples[0]}`
    : '';
  currentLectureId = lectureId;
  lessonActionBtn.disabled = false;
  lessonActionBtn.onclick = () => {
    const targetId = lectureId || `placeholder-${Date.now()}`;
    window.location.href = `lecture.html?lectureId=${encodeURIComponent(targetId)}`;
  };
}

// fallback dataset for local file usage
window.FALLBACK_DATA = {
  sample_exam: {
    exam_type: 'Sample',
    subject: 'Math',
    version: 'Prototype',
    description: '데이터 파일을 불러오지 못했을 때 표시되는 예시입니다.',
    domains: [
      {
        id: 'intro',
        name: 'Intro Domain',
        summary: '커리큘럼 데이터 로딩 실패 시 표시되는 템플릿.',
        topics: [
          {
            id: 'topic-a',
            title: '예시 토픽',
            summary: '샘플 토픽입니다.',
            objectives: ['Understand placeholder'],
            examples: ['x + 2 = 5'],
          },
        ],
      },
    ],
  },
};

loadData();
