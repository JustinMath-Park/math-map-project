# 수학 개념 설명 영상 자동 생성 시스템 설계

**작성일**: 2025-01-18
**목적**: Brilliant.org보다 더 상세하고 한국 학생에게 최적화된 수학 개념 설명 영상 자동 생성
**예상 구현 시간**: 12-16시간 (3-4 세션)
**예상 토큰 사용량**: ~150K tokens

---

## 📋 목차

1. [비용 분석](#1-비용-분석)
2. [시스템 아키텍처](#2-시스템-아키텍처)
3. [기술 스택](#3-기술-스택)
4. [구현 단계](#4-구현-단계)
5. [스타일 학습 시스템](#5-스타일-학습-시스템)
6. [코드 예시](#6-코드-예시)
7. [타임라인](#7-타임라인)

---

## 1. 비용 분석

### 1.1 ElevenLabs TTS API 비용 (음성 생성)

**한국어 지원**: ✅ 완전 지원 (Multilingual v2, Flash v2.5, Turbo v2.5 모델)

#### 요금제 구조

| 플랜 | 월 비용 | 포함 크레딧 | 추가 비용 | 특징 |
|------|---------|-------------|-----------|------|
| **Free** | $0 | 10,000 characters/월 | - | API 사용 가능, 프로토타입용 |
| **Starter** | $5 | 30,000 characters/월 | $0.20/1K chars | 개인 사용자 |
| **Creator** | $22 | 100,000 characters/월 | $0.15/1K chars | 프로젝트 제작자 |
| **Pro** | $99 | 500,000 characters/월 | $0.12/1K chars | 전문가용 |
| **Scale** | $330 | 2,000,000 characters/월 | $0.10/1K chars | 기업용 |
| **Business** | $1,320 | 11,000,000 characters/월 | $0.09/1K chars | 대규모 |

#### 모델별 크레딧 소비량

- **Multilingual v2** (고품질): 1 크레딧/문자
- **Flash v2.5** (빠름): 0.5 크레딧/문자
- **Turbo v2.5** (저비용): 0.3 크레딧/문자

#### 실사용 예상 비용

**5분 영상 기준 (약 1,200자 스크립트)**:
- Multilingual v2: 1,200 크레딧 = $0.24
- Flash v2.5: 600 크레딧 = $0.12
- Turbo v2.5: 360 크레딧 = $0.072

**월 20개 영상 제작 시**:
- Multilingual v2: 24,000 크레딧 = **$4.80** (Starter 플랜으로 가능)
- Flash v2.5: 12,000 크레딧 = **$2.40** (Free 플랜으로도 가능!)
- Turbo v2.5: 7,200 크레딧 = **$1.44** (Free 플랜으로 충분)

**✅ 권장**: **Free 플랜** (10K chars/월) + **Flash v2.5 모델**로 시작
- 프로토타입 단계에는 충분함
- 월 10개 이상 영상 제작 가능

---

### 1.2 서버 비용 (영상 렌더링)

#### 옵션 1: 로컬 렌더링 (M4 Mac) - **$0**

**장점**:
- ✅ 무료
- ✅ 이미 M4 Mac 보유
- ✅ Manim은 CPU 기반으로 충분히 빠름
- ✅ 5분 영상 렌더링 시간: ~2-5분

**단점**:
- ❌ 렌더링 중 Mac 사용 제한
- ❌ 대량 생성 시 시간 소요

**예상 렌더링 시간 (M4 Mac)**:
- 1분 애니메이션: ~30초
- 5분 애니메이션: ~2-3분
- 10분 애니메이션: ~5-7분

**✅ 권장**: 프로토타입 및 초기 단계에서는 **로컬 렌더링**이 최적

---

#### 옵션 2: Google Cloud Run (클라우드 렌더링)

**비용 구조** (us-central1 기준):

| 리소스 | 무료 티어 | 유료 비용 | 비고 |
|--------|-----------|-----------|------|
| CPU | 180,000 vCPU-초/월 | $0.00002400/vCPU-초 | 50시간/월 무료 |
| 메모리 | 360,000 GiB-초/월 | $0.00000250/GiB-초 | 100시간/월 무료 |
| 요청 수 | 2,000,000 요청/월 | $0.40/백만 요청 | - |
| GPU (L4) | - | $0.67/시간 | 영상 처리 가속화 |

**실제 사용 예시** (유럽 기준):
- 1 vCPU, 512 MiB 메모리
- 월 전체 가동 시: **$11.61**
- 영상 처리 전용: **$5-10/월** (일반 사용량)

**GPU 사용 시**:
- NVIDIA L4 GPU: $0.67/시간
- 5분 영상 렌더링 시간: ~1분
- 영상 1개당 비용: $0.011
- 월 100개 영상: **$1.10**

**실제 사례**:
- 영상 처리 서비스: 월 **£20 (~$25)** (Google Cloud 공식 사례)

**✅ 권장**: 대량 생산 단계에서만 Cloud Run 사용
- 월 100개 이상 영상 제작 시 고려
- 예상 비용: **$20-30/월**

---

#### 옵션 3: YouTube 무료 저장소

**비용**: **$0**
- YouTube는 무제한 동영상 업로드 제공
- 저장소 비용 걱정 없음
- CDN 제공 (전 세계 빠른 스트리밍)

---

### 1.3 AI API 비용

#### Gemini API (스크립트 생성, 스타일 학습)

**무료 티어**:
- Gemini 1.5 Flash: **15 RPM (requests per minute)**
- Gemini 1.5 Pro: **2 RPM**
- **무료 쿼터 내에서 충분히 사용 가능**

**유료 티어** (Google AI Studio Pay-as-you-go):
- Gemini 1.5 Flash: $0.000075/1K chars (입력), $0.0003/1K chars (출력)
- Gemini 1.5 Pro: $0.00125/1K chars (입력), $0.005/1K chars (출력)

**예상 사용량** (영상 1개당):
- 스크립트 생성: ~2,000 입력 + 1,500 출력 = **$0.0006** (Flash 기준)
- 스타일 최적화: ~1,000 입력 + 500 출력 = **$0.0003**
- **합계: $0.001/영상**

**월 100개 영상**: **$0.10**

**✅ 권장**: **무료 티어**로 충분 (프로토타입 단계)

---

#### Claude API (Manim 코드 생성)

**Anthropic API 요금**:
- Claude 3.5 Sonnet: $3/1M 입력 토큰, $15/1M 출력 토큰
- Claude 3 Haiku: $0.25/1M 입력 토큰, $1.25/1M 출력 토큰

**예상 사용량** (영상 1개당):
- Manim 코드 생성: ~3,000 입력 + 2,000 출력 = **$0.039** (Sonnet)
- Haiku 사용 시: **$0.003**

**월 100개 영상**:
- Sonnet: **$3.90**
- Haiku: **$0.30**

**✅ 권장**: **Haiku** 사용 (비용 효율적, 코드 생성에 충분한 성능)

---

### 1.4 Stable Diffusion (썸네일/삽화 생성)

**비용**: **$0** (로컬 실행)
- 이미 M4 Mac에 설치됨
- 모델 4개 보유 (12GB)
- 썸네일 생성: ~10-30초/이미지

---

### 1.5 총 비용 요약

#### 프로토타입 단계 (월 10-20개 영상)

| 항목 | 비용 | 비고 |
|------|------|------|
| ElevenLabs TTS | **$0** | Free 플랜 (10K chars) |
| 렌더링 (M4 Mac) | **$0** | 로컬 렌더링 |
| Gemini API | **$0** | 무료 쿼터 |
| Claude API (Haiku) | **$0.06** | 20개 영상 기준 |
| Stable Diffusion | **$0** | 로컬 실행 |
| **총계** | **~$0-1/월** | 거의 무료! |

---

#### 본격 운영 단계 (월 100개 영상)

| 항목 | 비용 | 비고 |
|------|------|------|
| ElevenLabs TTS | **$5** | Starter 플랜 |
| 렌더링 (로컬 or Cloud) | **$0-20** | 로컬 추천 |
| Gemini API | **$0.10** | 무료 쿼터 초과 시 |
| Claude API (Haiku) | **$0.30** | 100개 영상 기준 |
| Stable Diffusion | **$0** | 로컬 실행 |
| **총계** | **$5-25/월** | 매우 저렴! |

---

#### 대규모 운영 (월 500개 영상, YouTube 채널)

| 항목 | 비용 | 비고 |
|------|------|------|
| ElevenLabs TTS | **$22** | Creator 플랜 |
| Cloud Run (GPU) | **$30** | 대량 렌더링 |
| Gemini API | **$0.50** | 대량 스크립트 생성 |
| Claude API (Haiku) | **$1.50** | 500개 영상 |
| YouTube 저장소 | **$0** | 무료 |
| **총계** | **$54/월** | 매우 합리적! |

---

**✅ 결론**:
- **프로토타입 단계: 거의 무료 (~$0-1/월)**
- **본격 운영: $5-25/월**
- **대규모: $50-100/월**

**초기 투자 없이 바로 시작 가능!**

---

## 2. 시스템 아키텍처

### 2.1 전체 흐름도

```
┌─────────────────────────────────────────────────────────────────┐
│                        1. 주제 선정 & 분석                         │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │ Brilliant.org│ -> │ 수학 개념     │ -> │  AI 분석     │      │
│  │  컨텐츠 분석  │    │  리스트      │    │ (Gemini Pro) │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
└─────────────────────────────────────────────────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────────┐
│                        2. 스크립트 생성                           │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │ 개념 설명     │ -> │  예시 문제   │ -> │  AI 스크립트 │      │
│  │ 텍스트 생성   │    │  생성       │    │  (Gemini)    │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│                                                                  │
│  - 도입부 (Why this matters?)                                    │
│  - 개념 설명 (단계별 논리 전개)                                    │
│  - 예시 & 시각화                                                 │
│  - 연습 문제                                                     │
│  - 요약 & 다음 학습                                              │
└─────────────────────────────────────────────────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────────┐
│                   3. Manim 애니메이션 코드 생성                    │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │ 스크립트     │ -> │ Claude API   │ -> │  Manim 코드  │      │
│  │ (한글 + 수식)│    │ (Haiku)      │    │  (Python)    │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│                                                                  │
│  - MathTex, Tex 객체 생성                                        │
│  - 그래프, 도형 애니메이션                                         │
│  - Transform, Write 효과                                         │
│  - 색상, 타이밍 최적화                                            │
└─────────────────────────────────────────────────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────────┐
│                     4. 영상 렌더링 & 음성 합성                     │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │ Manim 렌더링 │ -> │ ElevenLabs   │ -> │  FFmpeg      │      │
│  │ (M4 Mac/GPU) │    │ TTS (한국어) │    │  병합        │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│                                                                  │
│  - MP4 영상 (1080p/60fps)                                       │
│  - MP3 음성 (고품질 한국어)                                       │
│  - 자막 SRT 생성                                                 │
└─────────────────────────────────────────────────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────────┐
│                    5. 스타일 학습 & 최적화                         │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │ 사용자 피드백 │ -> │ AI 스타일    │ -> │ 프롬프트     │      │
│  │ (1-5점 평가) │    │ 학습         │    │ 자동 개선    │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│                                                                  │
│  - 설명 속도 조절                                                │
│  - 예시 난이도 조정                                              │
│  - 시각화 스타일 변경                                            │
│  - 음성 톤 최적화                                                │
└─────────────────────────────────────────────────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────────┐
│                       6. YouTube 자동 업로드                      │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │ 썸네일 생성  │ -> │ 메타데이터   │ -> │  YouTube API │      │
│  │ (SD Model)   │    │ 자동 작성    │    │  업로드      │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
└─────────────────────────────────────────────────────────────────┘
```

---

### 2.2 데이터 흐름

```python
# 1. 입력
concept = "미분의 기하학적 의미"
target_level = "고등학교 2학년"
style_preferences = {
    "explanation_speed": "느림",
    "example_difficulty": "중간",
    "visual_style": "3Blue1Brown"
}

# 2. 스크립트 생성
script = generate_script(concept, target_level, style_preferences)
# {
#     "title": "미분의 기하학적 의미 - 접선의 기울기로 이해하기",
#     "sections": [
#         {"type": "intro", "content": "왜 미분을 배울까요?", "duration": 30},
#         {"type": "concept", "content": "접선의 기울기...", "duration": 120},
#         {"type": "example", "content": "y=x^2 그래프에서...", "duration": 90},
#         ...
#     ],
#     "voice_over": "안녕하세요! 오늘은 미분의 기하학적 의미를...",
#     "math_expressions": ["\\frac{dy}{dx}", "\\lim_{h \\to 0}"]
# }

# 3. Manim 코드 생성
manim_code = generate_manim_code(script)
# class Derivative(Scene):
#     def construct(self):
#         title = Text("미분의 기하학적 의미")
#         self.play(Write(title))
#         ...

# 4. 렌더링 & 음성
video = render_video(manim_code)  # MP4
audio = generate_audio(script["voice_over"])  # MP3
final_video = merge_video_audio(video, audio)  # 최종 MP4

# 5. 피드백 학습
user_rating = 4.5
feedback = "설명이 좋은데 예시가 더 쉬웠으면 좋겠어요"
update_style_model(script, user_rating, feedback)

# 6. YouTube 업로드
upload_to_youtube(final_video, title, description, tags)
```

---

## 3. 기술 스택

### 3.1 핵심 기술

| 영역 | 기술 | 목적 | 비용 |
|------|------|------|------|
| **애니메이션** | Manim Community | 수학 애니메이션 생성 | 무료 |
| **AI 스크립트** | Gemini 1.5 Flash | 강의 스크립트 생성 | 무료 |
| **AI 코드** | Claude 3 Haiku | Manim 코드 생성 | $0.30/100개 |
| **음성 합성** | ElevenLabs TTS | 한국어 음성 생성 | $0-5/월 |
| **영상 편집** | FFmpeg | 영상+음성 병합 | 무료 |
| **썸네일** | Stable Diffusion | 썸네일 이미지 생성 | 무료 |
| **업로드** | YouTube Data API v3 | 자동 업로드 | 무료 |
| **렌더링** | M4 Mac (로컬) | 영상 렌더링 | 무료 |

---

### 3.2 개발 환경

```bash
# Python 환경
Python 3.11+
pip install manim
pip install google-generativeai
pip install anthropic
pip install elevenlabs
pip install ffmpeg-python
pip install google-api-python-client
pip install opencv-python
pip install pillow

# FFmpeg 설치 (Mac)
brew install ffmpeg

# LaTeX 설치 (Manim 의존성)
brew install --cask mactex-no-gui
```

---

### 3.3 디렉토리 구조

```
video-generation/
├── config/
│   ├── api_keys.py          # API 키 관리
│   ├── style_config.py      # 스타일 설정
│   └── prompts.py           # AI 프롬프트 템플릿
├── scripts/
│   ├── script_generator.py  # 스크립트 생성
│   ├── manim_generator.py   # Manim 코드 생성
│   └── style_learner.py     # 스타일 학습
├── animations/
│   ├── templates/           # Manim 템플릿
│   └── generated/           # 생성된 Manim 코드
├── renders/
│   ├── videos/              # 렌더링된 영상
│   ├── audio/               # 생성된 음성
│   └── final/               # 최종 영상 (영상+음성)
├── data/
│   ├── concepts.json        # 수학 개념 리스트
│   ├── feedback.db          # 사용자 피드백 DB
│   └── style_history.json   # 스타일 학습 히스토리
├── utils/
│   ├── renderer.py          # 렌더링 유틸
│   ├── audio.py             # 음성 합성
│   └── youtube.py           # YouTube 업로드
└── main.py                  # 메인 파이프라인
```

---

## 4. 구현 단계

### Phase 0: 환경 설정 (1-2시간)

**목표**: 필요한 도구 설치 및 API 연동

**작업**:
1. Manim Community 설치
2. FFmpeg, LaTeX 설치
3. API 키 설정 (Gemini, Claude, ElevenLabs, YouTube)
4. 디렉토리 구조 생성
5. 테스트 애니메이션 렌더링

**검증**:
```bash
# Manim 테스트
manim -pql test.py TestScene

# FFmpeg 테스트
ffmpeg -version

# API 테스트
python test_apis.py
```

---

### Phase 1: 스크립트 생성 시스템 (3-4시간)

**목표**: AI로 강의 스크립트 자동 생성

**1.1 개념 리스트 크롤링**

```python
# scripts/concept_crawler.py
import requests
from bs4 import BeautifulSoup

def crawl_brilliant_concepts():
    """
    Brilliant.org 수학 개념 리스트 크롤링

    Returns:
        [
            {
                "topic": "Calculus",
                "concept": "Derivatives",
                "difficulty": "High School",
                "url": "https://brilliant.org/courses/..."
            },
            ...
        ]
    """
    # 실제 크롤링 대신 수동으로 개념 리스트 작성 추천
    concepts = [
        # 미적분
        {"topic": "미적분", "concept": "극한의 개념", "level": "고1"},
        {"topic": "미적분", "concept": "미분의 정의", "level": "고2"},
        {"topic": "미적분", "concept": "미분의 기하학적 의미", "level": "고2"},
        {"topic": "미적분", "concept": "적분의 정의", "level": "고2"},

        # 대수학
        {"topic": "대수학", "concept": "이차방정식의 근의 공식", "level": "중3"},
        {"topic": "대수학", "concept": "인수분해", "level": "중3"},

        # 기하학
        {"topic": "기하학", "concept": "피타고라스 정리", "level": "중2"},
        {"topic": "기하학", "concept": "삼각비", "level": "중3"},

        # 확률/통계
        {"topic": "확률", "concept": "순열과 조합", "level": "고1"},
        {"topic": "통계", "concept": "평균과 분산", "level": "고1"},
    ]
    return concepts
```

**1.2 AI 스크립트 생성**

```python
# scripts/script_generator.py
import google.generativeai as genai
from config.prompts import SCRIPT_GENERATION_PROMPT

class ScriptGenerator:
    def __init__(self):
        genai.configure(api_key=API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def generate_script(self, concept, level, style_preferences=None):
        """
        수학 개념에 대한 강의 스크립트 생성

        Args:
            concept: "미분의 기하학적 의미"
            level: "고등학교 2학년"
            style_preferences: {
                "explanation_speed": "느림",
                "example_difficulty": "쉬움",
                "visual_emphasis": True
            }

        Returns:
            {
                "title": "...",
                "duration_seconds": 300,
                "sections": [
                    {
                        "type": "intro",
                        "content": "...",
                        "duration": 30,
                        "visual_cues": ["그래프 등장", "제목 애니메이션"]
                    },
                    ...
                ],
                "voice_over": "전체 내레이션 텍스트...",
                "math_expressions": ["\\frac{dy}{dx}", ...],
                "timing": [
                    {"timestamp": 0, "action": "제목 표시"},
                    {"timestamp": 5, "action": "그래프 등장"},
                    ...
                ]
            }
        """
        prompt = self._build_prompt(concept, level, style_preferences)
        response = self.model.generate_content(prompt)
        script = self._parse_response(response.text)
        return script

    def _build_prompt(self, concept, level, style_prefs):
        base_prompt = f"""
당신은 수학 교육 전문가입니다. 다음 개념에 대한 5분짜리 강의 스크립트를 작성하세요.

**개념**: {concept}
**대상**: {level}

**구조**:
1. **도입부 (30초)**: 이 개념이 왜 중요한지, 실생활에서 어떻게 쓰이는지
2. **개념 설명 (120초)**: 단계별로 논리적으로 설명 (Why 중심)
3. **시각적 예시 (90초)**: 그래프/도형으로 시각화
4. **연습 문제 (60초)**: 간단한 예시 문제 풀이
5. **요약 & 다음 학습 (20초)**

**스타일**:
- 3Blue1Brown 스타일 (시각적, 직관적)
- 한국어로 작성
- 수식은 LaTeX 문법 사용
- 친근하고 대화하듯이

**출력 형식** (JSON):
{{
    "title": "...",
    "sections": [
        {{
            "type": "intro",
            "content": "안녕하세요! 오늘은...",
            "duration": 30,
            "visual_cues": ["제목 애니메이션", "실생활 예시 이미지"]
        }},
        ...
    ],
    "voice_over": "전체 내레이션...",
    "math_expressions": ["\\frac{{dy}}{{dx}}", "\\lim_{{h \\to 0}}"],
    "timing": [
        {{"timestamp": 0, "action": "제목 표시"}},
        {{"timestamp": 5, "action": "그래프 등장"}},
        ...
    ]
}}
"""

        if style_prefs:
            base_prompt += f"\n\n**추가 스타일 요청**:\n"
            if style_prefs.get("explanation_speed") == "느림":
                base_prompt += "- 설명을 천천히, 각 단계를 충분히 설명하세요\n"
            if style_prefs.get("example_difficulty") == "쉬움":
                base_prompt += "- 예시 문제는 최대한 쉽게 만드세요\n"

        return base_prompt

    def _parse_response(self, text):
        """JSON 파싱 및 검증"""
        import json
        import re

        # JSON 추출
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if not json_match:
            raise ValueError("JSON 형식이 아님")

        script = json.loads(json_match.group())

        # 검증
        required_fields = ["title", "sections", "voice_over", "timing"]
        for field in required_fields:
            if field not in script:
                raise ValueError(f"{field} 필드가 없음")

        return script
```

**1.3 테스트**

```python
# test_script_generation.py
from scripts.script_generator import ScriptGenerator

generator = ScriptGenerator()

# 테스트 1: 기본 생성
script = generator.generate_script(
    concept="미분의 기하학적 의미",
    level="고등학교 2학년"
)

print(f"제목: {script['title']}")
print(f"섹션 수: {len(script['sections'])}")
print(f"총 길이: {script.get('duration_seconds', 0)}초")
print(f"\n내레이션 (앞 200자):\n{script['voice_over'][:200]}...")

# 테스트 2: 스타일 적용
script2 = generator.generate_script(
    concept="피타고라스 정리",
    level="중학교 2학년",
    style_preferences={
        "explanation_speed": "느림",
        "example_difficulty": "쉬움"
    }
)
```

---

### Phase 2: Manim 코드 생성 시스템 (3-4시간)

**목표**: 스크립트를 Manim 애니메이션 코드로 변환

**2.1 Manim 템플릿 작성**

```python
# animations/templates/base_template.py
from manim import *

class MathConceptScene(Scene):
    """수학 개념 설명 기본 템플릿"""

    def construct(self):
        # 1. 제목
        self.show_title()

        # 2. 개념 설명
        self.explain_concept()

        # 3. 시각적 예시
        self.show_visual_example()

        # 4. 요약
        self.show_summary()

    def show_title(self):
        """제목 애니메이션"""
        title = Text("개념 제목", font_size=48)
        title.to_edge(UP)
        self.play(Write(title))
        self.wait(1)
        self.play(title.animate.scale(0.7).to_corner(UL))

    def explain_concept(self):
        """개념 설명 (텍스트 + 수식)"""
        explanation = Text("개념 설명 텍스트", font_size=32)
        self.play(Write(explanation))
        self.wait(2)

        formula = MathTex(r"\frac{dy}{dx} = \lim_{h \to 0} \frac{f(x+h) - f(x)}{h}")
        formula.next_to(explanation, DOWN, buff=0.5)
        self.play(Write(formula))
        self.wait(2)

    def show_visual_example(self):
        """시각적 예시 (그래프, 도형 등)"""
        axes = Axes(
            x_range=[-3, 3, 1],
            y_range=[-1, 9, 1],
            axis_config={"color": BLUE}
        )

        graph = axes.plot(lambda x: x**2, color=YELLOW)
        graph_label = axes.get_graph_label(graph, label='y=x^2')

        self.play(Create(axes), Create(graph), Write(graph_label))
        self.wait(2)

    def show_summary(self):
        """요약"""
        summary = Text("요약: 미분은 접선의 기울기!", font_size=36, color=GREEN)
        self.play(Write(summary))
        self.wait(2)
```

**2.2 Claude API로 Manim 코드 생성**

```python
# scripts/manim_generator.py
import anthropic
from config.prompts import MANIM_CODE_PROMPT

class ManimCodeGenerator:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)

    def generate_manim_code(self, script):
        """
        스크립트를 Manim 코드로 변환

        Args:
            script: ScriptGenerator가 생성한 스크립트

        Returns:
            Python 코드 (str)
        """
        prompt = self._build_prompt(script)

        message = self.client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=4000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        code = self._extract_code(message.content[0].text)
        return code

    def _build_prompt(self, script):
        sections_text = "\n\n".join([
            f"**{i+1}. {section['type']}** ({section['duration']}초)\n{section['content']}"
            for i, section in enumerate(script['sections'])
        ])

        math_exprs = ", ".join(script.get('math_expressions', []))

        prompt = f"""
당신은 Manim 전문가입니다. 아래 강의 스크립트를 Manim Community 코드로 변환하세요.

**제목**: {script['title']}
**총 길이**: {script.get('duration_seconds', 300)}초

**스크립트**:
{sections_text}

**사용할 수식**: {math_exprs}

**타이밍 정보**:
{script.get('timing', [])}

**요구사항**:
1. Manim Community (최신 버전) 문법 사용
2. 클래스명: `{script['title'].replace(' ', '')}`
3. 한글 텍스트는 `Text()` 사용, 수식은 `MathTex()` 사용
4. 애니메이션 타이밍을 스크립트와 정확히 맞추기
5. 3Blue1Brown 스타일 (색상: BLUE, YELLOW, GREEN 활용)
6. 주석으로 각 섹션 표시
7. `self.wait()` 로 적절한 대기 시간 추가

**출력 형식**:
```python
from manim import *

class ConceptScene(Scene):
    def construct(self):
        # 1. 제목 (0-5초)
        ...

        # 2. 개념 설명 (5-125초)
        ...

        # 3. 시각적 예시 (125-215초)
        ...

        # 4. 요약 (215-235초)
        ...
```

지금 바로 코드만 작성하세요 (설명 불필요):
"""
        return prompt

    def _extract_code(self, response):
        """응답에서 Python 코드만 추출"""
        import re

        # ```python ... ``` 블록 추출
        match = re.search(r'```python\n(.*?)\n```', response, re.DOTALL)
        if match:
            return match.group(1)

        # 코드 블록이 없으면 전체 반환
        return response
```

**2.3 코드 검증 및 실행**

```python
# utils/renderer.py
import subprocess
import os

class ManimRenderer:
    def __init__(self, output_dir="renders/videos"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def render(self, code, scene_name, quality="high"):
        """
        Manim 코드 렌더링

        Args:
            code: Python 코드 (str)
            scene_name: 클래스명
            quality: "low" (480p, 빠름), "medium" (720p), "high" (1080p)

        Returns:
            렌더링된 영상 파일 경로
        """
        # 임시 파일에 코드 저장
        temp_file = f"animations/generated/{scene_name}.py"
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(code)

        # Manim 렌더링 명령
        quality_flags = {
            "low": "-ql",      # 480p, 15fps
            "medium": "-qm",   # 720p, 30fps
            "high": "-qh"      # 1080p, 60fps
        }

        flag = quality_flags.get(quality, "-qh")

        cmd = [
            "manim",
            flag,
            temp_file,
            scene_name,
            "-o", f"{scene_name}.mp4"
        ]

        # 실행
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10분 타임아웃
            )

            if result.returncode != 0:
                raise Exception(f"렌더링 실패:\n{result.stderr}")

            # 렌더링된 파일 경로
            video_path = f"media/videos/{scene_name}/1080p60/{scene_name}.mp4"
            return video_path

        except subprocess.TimeoutExpired:
            raise Exception("렌더링 타임아웃 (10분 초과)")
        except Exception as e:
            raise Exception(f"렌더링 에러: {e}")
```

**2.4 테스트**

```python
# test_manim_generation.py
from scripts.script_generator import ScriptGenerator
from scripts.manim_generator import ManimCodeGenerator
from utils.renderer import ManimRenderer

# 1. 스크립트 생성
script_gen = ScriptGenerator()
script = script_gen.generate_script("피타고라스 정리", "중학교 2학년")

# 2. Manim 코드 생성
manim_gen = ManimCodeGenerator()
code = manim_gen.generate_manim_code(script)

print("=== 생성된 Manim 코드 ===")
print(code[:500])  # 앞 500자만 출력

# 3. 렌더링
renderer = ManimRenderer()
video_path = renderer.render(code, "PythagoreanTheorem", quality="low")

print(f"\n✅ 렌더링 완료: {video_path}")
```

---

### Phase 3: 음성 합성 & 영상 병합 (2-3시간)

**목표**: ElevenLabs로 음성 생성 후 영상과 병합

**3.1 음성 생성**

```python
# utils/audio.py
from elevenlabs import generate, Voice, VoiceSettings

class AudioGenerator:
    def __init__(self, api_key):
        self.api_key = api_key

    def generate_audio(self, text, output_path, voice_name="Bella"):
        """
        텍스트를 음성으로 변환

        Args:
            text: 내레이션 텍스트 (한국어)
            output_path: 출력 MP3 파일 경로
            voice_name: ElevenLabs 음성 이름

        Returns:
            오디오 파일 경로
        """
        audio = generate(
            text=text,
            voice=Voice(
                voice_id=self._get_korean_voice_id(),
                settings=VoiceSettings(
                    stability=0.5,
                    similarity_boost=0.75,
                    style=0.0,
                    use_speaker_boost=True
                )
            ),
            model="eleven_multilingual_v2"  # 한국어 지원
        )

        # 파일 저장
        with open(output_path, 'wb') as f:
            f.write(audio)

        return output_path

    def _get_korean_voice_id(self):
        """한국어 음성 ID 반환 (ElevenLabs 음성 라이브러리에서 선택)"""
        # 실제로는 ElevenLabs API에서 한국어 음성 목록 조회
        # 여기서는 예시로 기본 음성 ID 사용
        return "21m00Tcm4TlvDq8ikWAM"  # Rachel (영어 기본 음성)
        # TODO: 한국어 음성으로 변경 필요
```

**3.2 영상 + 음성 병합**

```python
# utils/video_merge.py
import ffmpeg
import os

class VideoMerger:
    def merge_video_audio(self, video_path, audio_path, output_path):
        """
        영상과 음성 병합

        Args:
            video_path: Manim 렌더링 영상 (MP4)
            audio_path: ElevenLabs 음성 (MP3)
            output_path: 최종 출력 경로

        Returns:
            최종 영상 파일 경로
        """
        try:
            # FFmpeg로 병합
            video = ffmpeg.input(video_path)
            audio = ffmpeg.input(audio_path)

            ffmpeg.output(
                video,
                audio,
                output_path,
                vcodec='copy',
                acodec='aac',
                strict='experimental'
            ).overwrite_output().run()

            return output_path

        except ffmpeg.Error as e:
            raise Exception(f"FFmpeg 에러: {e.stderr.decode()}")

    def add_subtitles(self, video_path, srt_path, output_path):
        """
        자막 추가 (선택 사항)

        Args:
            video_path: 영상 파일
            srt_path: SRT 자막 파일
            output_path: 출력 경로
        """
        ffmpeg.input(video_path).output(
            output_path,
            vf=f"subtitles={srt_path}"
        ).run()
```

**3.3 전체 파이프라인 통합**

```python
# main.py
from scripts.script_generator import ScriptGenerator
from scripts.manim_generator import ManimCodeGenerator
from utils.renderer import ManimRenderer
from utils.audio import AudioGenerator
from utils.video_merge import VideoMerger
import os

class VideoPipeline:
    def __init__(self):
        self.script_gen = ScriptGenerator()
        self.manim_gen = ManimCodeGenerator()
        self.renderer = ManimRenderer()
        self.audio_gen = AudioGenerator(api_key=ELEVENLABS_API_KEY)
        self.merger = VideoMerger()

    def generate_video(self, concept, level, style_prefs=None):
        """
        전체 파이프라인 실행

        Args:
            concept: 수학 개념
            level: 학년
            style_prefs: 스타일 설정

        Returns:
            최종 영상 파일 경로
        """
        print(f"🎬 영상 생성 시작: {concept}")

        # 1. 스크립트 생성
        print("📝 1/5 - 스크립트 생성 중...")
        script = self.script_gen.generate_script(concept, level, style_prefs)
        print(f"✅ 제목: {script['title']}")

        # 2. Manim 코드 생성
        print("🎨 2/5 - 애니메이션 코드 생성 중...")
        manim_code = self.manim_gen.generate_manim_code(script)
        scene_name = script['title'].replace(' ', '').replace('-', '')

        # 3. 영상 렌더링
        print("🎥 3/5 - 영상 렌더링 중 (2-5분 소요)...")
        video_path = self.renderer.render(manim_code, scene_name, quality="high")
        print(f"✅ 영상: {video_path}")

        # 4. 음성 생성
        print("🎤 4/5 - 음성 합성 중...")
        audio_path = f"renders/audio/{scene_name}.mp3"
        os.makedirs("renders/audio", exist_ok=True)
        self.audio_gen.generate_audio(script['voice_over'], audio_path)
        print(f"✅ 음성: {audio_path}")

        # 5. 병합
        print("🎬 5/5 - 영상 + 음성 병합 중...")
        final_path = f"renders/final/{scene_name}_final.mp4"
        os.makedirs("renders/final", exist_ok=True)
        self.merger.merge_video_audio(video_path, audio_path, final_path)

        print(f"✅ 완료! {final_path}")
        return final_path

# 실행
if __name__ == "__main__":
    pipeline = VideoPipeline()

    video = pipeline.generate_video(
        concept="미분의 기하학적 의미",
        level="고등학교 2학년"
    )

    print(f"\n🎉 영상 생성 완료: {video}")
```

---

### Phase 4: 스타일 학습 시스템 (3-4시간)

**목표**: 사용자 피드백을 학습하여 AI 프롬프트 자동 개선

**4.1 피드백 수집**

```python
# data/feedback.db (SQLite)
# CREATE TABLE feedback (
#     id INTEGER PRIMARY KEY,
#     concept TEXT,
#     video_path TEXT,
#     rating INTEGER,  -- 1-5점
#     comments TEXT,
#     style_preferences TEXT,  -- JSON
#     created_at TIMESTAMP
# );

# utils/feedback.py
import sqlite3
import json
from datetime import datetime

class FeedbackManager:
    def __init__(self, db_path="data/feedback.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                concept TEXT,
                video_path TEXT,
                rating INTEGER,
                comments TEXT,
                style_preferences TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    def save_feedback(self, concept, video_path, rating, comments="", style_prefs=None):
        """피드백 저장"""
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            "INSERT INTO feedback (concept, video_path, rating, comments, style_preferences) VALUES (?, ?, ?, ?, ?)",
            (concept, video_path, rating, comments, json.dumps(style_prefs or {}))
        )
        conn.commit()
        conn.close()

    def get_all_feedback(self):
        """모든 피드백 조회"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("SELECT * FROM feedback ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()
        return rows
```

**4.2 스타일 학습 알고리즘**

```python
# scripts/style_learner.py
import google.generativeai as genai
import json

class StyleLearner:
    """
    사용자 피드백을 분석하여 AI 프롬프트 자동 최적화
    """

    def __init__(self, feedback_manager):
        self.feedback_mgr = feedback_manager
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def learn_from_feedback(self):
        """
        모든 피드백을 분석하여 스타일 패턴 학습

        Returns:
            {
                "preferred_explanation_speed": "느림",
                "preferred_example_difficulty": "중간",
                "preferred_visual_style": "3Blue1Brown",
                "common_complaints": ["너무 빠름", "예시가 어려움"],
                "high_rated_features": ["시각화가 좋음", "단계별 설명"],
                "prompt_improvements": "스크립트 프롬프트에 '각 단계를 천천히...' 추가"
            }
        """
        feedbacks = self.feedback_mgr.get_all_feedback()

        if not feedbacks:
            return None

        # 피드백 요약
        summary = self._summarize_feedback(feedbacks)

        # AI로 패턴 분석
        insights = self._analyze_patterns(summary)

        # 프롬프트 개선안 생성
        improvements = self._generate_prompt_improvements(insights)

        return improvements

    def _summarize_feedback(self, feedbacks):
        """피드백 요약"""
        high_rated = []  # 4-5점
        low_rated = []   # 1-2점

        for fb in feedbacks:
            rating = fb[3]
            comments = fb[4]

            if rating >= 4:
                high_rated.append(comments)
            elif rating <= 2:
                low_rated.append(comments)

        return {
            "total_count": len(feedbacks),
            "avg_rating": sum([fb[3] for fb in feedbacks]) / len(feedbacks),
            "high_rated_comments": high_rated,
            "low_rated_comments": low_rated
        }

    def _analyze_patterns(self, summary):
        """AI로 패턴 분석"""
        prompt = f"""
아래는 수학 강의 영상에 대한 사용자 피드백 요약입니다. 패턴을 분석하세요.

**평균 평점**: {summary['avg_rating']:.1f}/5.0
**총 피드백 수**: {summary['total_count']}

**높은 평점 (4-5점) 댓글**:
{chr(10).join(['- ' + c for c in summary['high_rated_comments'][:10]])}

**낮은 평점 (1-2점) 댓글**:
{chr(10).join(['- ' + c for c in summary['low_rated_comments'][:10]])}

**분석 요청**:
1. 사용자들이 좋아하는 요소는?
2. 사용자들이 싫어하는 요소는?
3. 개선해야 할 점은?
4. 스타일 선호도는? (설명 속도, 예시 난이도, 시각화 스타일 등)

**출력 형식** (JSON):
{{
    "liked_features": ["시각화", "단계별 설명", ...],
    "disliked_features": ["너무 빠름", "예시 어려움", ...],
    "style_preferences": {{
        "explanation_speed": "느림",
        "example_difficulty": "쉬움",
        "visual_emphasis": true
    }},
    "improvement_suggestions": ["...", "..."]
}}
"""

        response = self.model.generate_content(prompt)
        insights = json.loads(response.text)
        return insights

    def _generate_prompt_improvements(self, insights):
        """프롬프트 개선안 생성"""
        prompt = f"""
아래 사용자 선호도를 반영하여 스크립트 생성 프롬프트를 개선하세요.

**사용자 선호도**:
{json.dumps(insights, ensure_ascii=False, indent=2)}

**현재 프롬프트** (일부):
"당신은 수학 교육 전문가입니다. 다음 개념에 대한 5분짜리 강의 스크립트를 작성하세요."

**요청**:
위 선호도를 반영하여 프롬프트에 추가할 문구를 작성하세요.

**출력 형식**:
{{
    "additional_instructions": "- 각 단계를 천천히 설명하세요\\n- 예시는 최대한 쉽게...",
    "style_guidelines": "- 3Blue1Brown 스타일 강조\\n- 시각화를 많이 사용..."
}}
"""

        response = self.model.generate_content(prompt)
        improvements = json.loads(response.text)

        # 개선안 저장
        with open("config/prompt_improvements.json", "w", encoding="utf-8") as f:
            json.dump(improvements, f, ensure_ascii=False, indent=2)

        return improvements
```

**4.3 자동 프롬프트 업데이트**

```python
# scripts/script_generator.py (수정)
class ScriptGenerator:
    def __init__(self, use_learned_style=True):
        # ...
        self.use_learned_style = use_learned_style
        self.learned_improvements = self._load_improvements()

    def _load_improvements(self):
        """학습된 프롬프트 개선안 로드"""
        try:
            with open("config/prompt_improvements.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return None

    def _build_prompt(self, concept, level, style_prefs):
        base_prompt = f"""
당신은 수학 교육 전문가입니다. 다음 개념에 대한 5분짜리 강의 스크립트를 작성하세요.

**개념**: {concept}
**대상**: {level}
"""

        # ⭐ 학습된 개선안 추가
        if self.use_learned_style and self.learned_improvements:
            base_prompt += f"\n\n**사용자 선호도 반영** (피드백 기반):\n"
            base_prompt += self.learned_improvements.get("additional_instructions", "")
            base_prompt += "\n\n"
            base_prompt += self.learned_improvements.get("style_guidelines", "")

        # 나머지 프롬프트...
        return base_prompt
```

---

### Phase 5: YouTube 자동 업로드 (2시간)

**목표**: 완성된 영상을 YouTube에 자동 업로드

```python
# utils/youtube.py
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

class YouTubeUploader:
    def __init__(self, credentials_path="config/youtube_credentials.json"):
        self.credentials = Credentials.from_authorized_user_file(credentials_path)
        self.youtube = build('youtube', 'v3', credentials=self.credentials)

    def upload_video(self, video_path, title, description, tags, thumbnail_path=None):
        """
        YouTube에 영상 업로드

        Args:
            video_path: 영상 파일 경로
            title: 영상 제목
            description: 설명
            tags: 태그 리스트 ["수학", "미적분", ...]
            thumbnail_path: 썸네일 이미지 경로 (선택)

        Returns:
            YouTube 영상 ID
        """
        body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': tags,
                'categoryId': '27'  # Education 카테고리
            },
            'status': {
                'privacyStatus': 'public'  # 'private', 'unlisted', 'public'
            }
        }

        media = MediaFileUpload(video_path, chunksize=-1, resumable=True)

        request = self.youtube.videos().insert(
            part='snippet,status',
            body=body,
            media_body=media
        )

        response = request.execute()
        video_id = response['id']

        # 썸네일 업로드 (선택)
        if thumbnail_path:
            self.upload_thumbnail(video_id, thumbnail_path)

        return video_id

    def upload_thumbnail(self, video_id, thumbnail_path):
        """썸네일 업로드"""
        request = self.youtube.thumbnails().set(
            videoId=video_id,
            media_body=MediaFileUpload(thumbnail_path)
        )
        request.execute()
```

---

## 5. 스타일 학습 시스템

### 5.1 학습 프로세스

```
사용자 피드백 입력
        ↓
피드백 DB 저장 (SQLite)
        ↓
AI 패턴 분석 (Gemini)
        ↓
프롬프트 개선안 생성
        ↓
다음 영상 생성 시 자동 반영
        ↓
반복 (Meta-Learning)
```

### 5.2 피드백 항목

사용자가 각 영상을 보고 평가:

1. **전체 평점**: 1-5점
2. **구체적 피드백**:
   - 설명 속도: 너무 빠름 / 적당 / 너무 느림
   - 예시 난이도: 너무 쉬움 / 적당 / 너무 어려움
   - 시각화 품질: 1-5점
   - 음성 품질: 1-5점
3. **자유 코멘트**: 텍스트 입력

### 5.3 학습 예시

**초기 프롬프트**:
```
"당신은 수학 교육 전문가입니다. 5분짜리 강의 스크립트를 작성하세요."
```

**10개 영상 후 피드백 분석**:
- 평균 평점: 3.2/5.0
- 공통 불만: "너무 빠름", "예시가 어려움"
- 높은 평가: "시각화가 좋음"

**자동 개선된 프롬프트**:
```
"당신은 수학 교육 전문가입니다. 5분짜리 강의 스크립트를 작성하세요.

**사용자 선호도 반영**:
- 각 단계를 천천히, 충분히 설명하세요
- 예시 문제는 최대한 쉽게 만드세요 (중학생도 이해 가능하도록)
- 시각화를 적극 활용하세요 (그래프, 도형, 애니메이션)
- 3Blue1Brown 스타일을 유지하세요
"
```

**50개 영상 후**:
- 평균 평점: 4.5/5.0
- AI가 사용자의 선호 스타일을 완전히 학습

---

## 6. 코드 예시

### 6.1 전체 실행 예시

```python
# main.py
from scripts.script_generator import ScriptGenerator
from scripts.manim_generator import ManimCodeGenerator
from scripts.style_learner import StyleLearner
from utils.renderer import ManimRenderer
from utils.audio import AudioGenerator
from utils.video_merge import VideoMerger
from utils.youtube import YouTubeUploader
from utils.feedback import FeedbackManager
import os

class VideoProductionPipeline:
    """전체 영상 제작 파이프라인"""

    def __init__(self):
        # 컴포넌트 초기화
        self.script_gen = ScriptGenerator(use_learned_style=True)
        self.manim_gen = ManimCodeGenerator()
        self.renderer = ManimRenderer()
        self.audio_gen = AudioGenerator(api_key=os.getenv("ELEVENLABS_API_KEY"))
        self.merger = VideoMerger()
        self.uploader = YouTubeUploader()
        self.feedback_mgr = FeedbackManager()
        self.style_learner = StyleLearner(self.feedback_mgr)

    def produce_video(self, concept, level, upload_to_youtube=False):
        """
        완전 자동화된 영상 제작

        Args:
            concept: 수학 개념
            level: 학년
            upload_to_youtube: YouTube 업로드 여부

        Returns:
            {
                "video_path": "...",
                "youtube_id": "..." (업로드 시)
            }
        """
        print(f"\n{'='*60}")
        print(f"🎬 영상 제작 시작: {concept}")
        print(f"{'='*60}\n")

        # 1. 스크립트 생성
        print("📝 [1/6] 스크립트 생성 중...")
        script = self.script_gen.generate_script(concept, level)
        print(f"   ✅ 제목: {script['title']}")
        print(f"   ✅ 길이: {script.get('duration_seconds', 0)}초")

        # 2. Manim 코드 생성
        print("\n🎨 [2/6] 애니메이션 코드 생성 중...")
        manim_code = self.manim_gen.generate_manim_code(script)
        scene_name = script['title'].replace(' ', '').replace('-', '')[:50]
        print(f"   ✅ 씬 이름: {scene_name}")

        # 3. 영상 렌더링
        print("\n🎥 [3/6] 영상 렌더링 중 (M4 Mac, 2-5분 소요)...")
        video_path = self.renderer.render(manim_code, scene_name, quality="high")
        print(f"   ✅ 영상: {video_path}")

        # 4. 음성 생성
        print("\n🎤 [4/6] 음성 합성 중 (ElevenLabs)...")
        audio_path = f"renders/audio/{scene_name}.mp3"
        os.makedirs("renders/audio", exist_ok=True)
        self.audio_gen.generate_audio(script['voice_over'], audio_path)
        print(f"   ✅ 음성: {audio_path}")

        # 5. 병합
        print("\n🎬 [5/6] 영상 + 음성 병합 중...")
        final_path = f"renders/final/{scene_name}_final.mp4"
        os.makedirs("renders/final", exist_ok=True)
        self.merger.merge_video_audio(video_path, audio_path, final_path)
        print(f"   ✅ 최종 영상: {final_path}")

        result = {"video_path": final_path}

        # 6. YouTube 업로드 (선택)
        if upload_to_youtube:
            print("\n📤 [6/6] YouTube 업로드 중...")
            video_id = self.uploader.upload_video(
                video_path=final_path,
                title=script['title'],
                description=f"수학 개념 설명: {concept}\n\n{script['voice_over'][:500]}...",
                tags=["수학", "Math", concept, level, "교육"]
            )
            result["youtube_id"] = video_id
            result["youtube_url"] = f"https://youtube.com/watch?v={video_id}"
            print(f"   ✅ YouTube: {result['youtube_url']}")

        print(f"\n{'='*60}")
        print(f"✅ 영상 제작 완료!")
        print(f"{'='*60}\n")

        return result

    def batch_produce(self, concepts, upload=False):
        """
        대량 영상 제작

        Args:
            concepts: [
                {"concept": "미분", "level": "고2"},
                {"concept": "적분", "level": "고2"},
                ...
            ]
        """
        results = []

        for i, item in enumerate(concepts, 1):
            print(f"\n{'#'*60}")
            print(f"# 진행: {i}/{len(concepts)}")
            print(f"{'#'*60}")

            result = self.produce_video(
                concept=item['concept'],
                level=item['level'],
                upload_to_youtube=upload
            )
            results.append(result)

        return results

    def update_learning(self):
        """스타일 학습 업데이트 (주기적으로 실행)"""
        print("🧠 스타일 학습 업데이트 중...")
        improvements = self.style_learner.learn_from_feedback()

        if improvements:
            print(f"   ✅ 프롬프트 개선안 적용됨")
            print(f"   - 좋아하는 요소: {improvements.get('liked_features', [])}")
            print(f"   - 개선할 요소: {improvements.get('disliked_features', [])}")
        else:
            print("   ℹ️  피드백 데이터 부족")

# === 실행 예시 ===

if __name__ == "__main__":
    pipeline = VideoProductionPipeline()

    # 예시 1: 단일 영상 제작
    result = pipeline.produce_video(
        concept="미분의 기하학적 의미",
        level="고등학교 2학년",
        upload_to_youtube=False
    )
    print(f"\n결과: {result}")

    # 예시 2: 대량 제작 (10개 개념)
    concepts = [
        {"concept": "미분의 정의", "level": "고2"},
        {"concept": "적분의 정의", "level": "고2"},
        {"concept": "피타고라스 정리", "level": "중2"},
        {"concept": "이차방정식의 근의 공식", "level": "중3"},
        {"concept": "삼각비", "level": "중3"},
        # ... 더 추가
    ]

    # results = pipeline.batch_produce(concepts, upload=True)

    # 예시 3: 스타일 학습 업데이트
    # pipeline.update_learning()
```

---

### 6.2 피드백 수집 웹 UI (선택 사항)

```python
# web_ui/app.py (Flask)
from flask import Flask, render_template, request, jsonify
from utils.feedback import FeedbackManager

app = Flask(__name__)
feedback_mgr = FeedbackManager()

@app.route('/')
def index():
    return render_template('feedback_form.html')

@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    data = request.json

    feedback_mgr.save_feedback(
        concept=data['concept'],
        video_path=data['video_path'],
        rating=data['rating'],
        comments=data['comments'],
        style_prefs=data.get('style_preferences')
    )

    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

```html
<!-- web_ui/templates/feedback_form.html -->
<!DOCTYPE html>
<html>
<head>
    <title>영상 피드백</title>
    <style>
        body { font-family: Arial; max-width: 600px; margin: 50px auto; }
        .rating { font-size: 24px; }
        .rating span { cursor: pointer; }
        textarea { width: 100%; height: 100px; }
        button { padding: 10px 20px; font-size: 16px; }
    </style>
</head>
<body>
    <h1>영상 피드백</h1>
    <form id="feedbackForm">
        <p><strong>개념:</strong> <span id="concept">미분의 기하학적 의미</span></p>

        <p><strong>평점:</strong></p>
        <div class="rating">
            <span onclick="setRating(1)">⭐</span>
            <span onclick="setRating(2)">⭐</span>
            <span onclick="setRating(3)">⭐</span>
            <span onclick="setRating(4)">⭐</span>
            <span onclick="setRating(5)">⭐</span>
        </div>

        <p><strong>코멘트:</strong></p>
        <textarea id="comments" placeholder="개선할 점이나 좋았던 점을 알려주세요"></textarea>

        <p><strong>설명 속도:</strong></p>
        <select id="speed">
            <option value="빠름">너무 빠름</option>
            <option value="적당" selected>적당</option>
            <option value="느림">너무 느림</option>
        </select>

        <p><strong>예시 난이도:</strong></p>
        <select id="difficulty">
            <option value="쉬움">너무 쉬움</option>
            <option value="적당" selected>적당</option>
            <option value="어려움">너무 어려움</option>
        </select>

        <p></p>
        <button type="submit">제출</button>
    </form>

    <script>
        let rating = 0;

        function setRating(r) {
            rating = r;
            document.querySelector('.rating').innerHTML = '⭐'.repeat(r) + '☆'.repeat(5-r);
        }

        document.getElementById('feedbackForm').onsubmit = async (e) => {
            e.preventDefault();

            const data = {
                concept: document.getElementById('concept').innerText,
                video_path: "temp",
                rating: rating,
                comments: document.getElementById('comments').value,
                style_preferences: {
                    speed: document.getElementById('speed').value,
                    difficulty: document.getElementById('difficulty').value
                }
            };

            await fetch('/submit_feedback', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });

            alert('피드백이 저장되었습니다!');
        };
    </script>
</body>
</html>
```

---

## 7. 타임라인

### 세션 1: 환경 설정 & 스크립트 생성 (4시간)

**작업**:
- [ ] Manim Community 설치
- [ ] FFmpeg, LaTeX 설치
- [ ] API 키 설정 (Gemini, Claude, ElevenLabs)
- [ ] 디렉토리 구조 생성
- [ ] 스크립트 생성 시스템 구현
- [ ] 테스트 (3개 개념으로 스크립트 생성)

**검증**:
```bash
python test_script_generation.py
```

**예상 토큰**: ~40K

---

### 세션 2: Manim 코드 생성 & 렌더링 (4시간)

**작업**:
- [ ] Manim 템플릿 작성
- [ ] Claude API 연동
- [ ] Manim 코드 생성 시스템 구현
- [ ] 렌더링 시스템 구현
- [ ] 테스트 (3개 개념으로 영상 렌더링)

**검증**:
```bash
python test_manim_generation.py
```

**예상 토큰**: ~50K

---

### 세션 3: 음성 합성 & 전체 파이프라인 (4시간)

**작업**:
- [ ] ElevenLabs TTS 연동
- [ ] FFmpeg 병합 시스템 구현
- [ ] 전체 파이프라인 통합
- [ ] 테스트 (3개 완전한 영상 제작)

**검증**:
```bash
python main.py
```

**예상 토큰**: ~30K

---

### 세션 4: 스타일 학습 & YouTube 업로드 (4시간)

**작업**:
- [ ] 피드백 DB 구축
- [ ] 스타일 학습 시스템 구현
- [ ] YouTube API 연동
- [ ] 썸네일 생성 (Stable Diffusion)
- [ ] 자동 업로드 시스템
- [ ] 대량 제작 테스트 (10개 영상)

**검증**:
```bash
python batch_production.py
```

**예상 토큰**: ~40K

---

**총 예상 시간**: 16시간 (4세션)
**총 예상 토큰**: ~160K tokens

---

## 8. 다음 단계

### 프로토타입 완료 후

1. **사용자 테스트** (10-20명)
   - 영상 10개 제작
   - 피드백 수집
   - 스타일 학습 검증

2. **YouTube 채널 런칭**
   - 채널 개설
   - 브랜딩 (로고, 배너)
   - 초기 영상 20개 업로드

3. **마케팅**
   - 수학 커뮤니티 홍보
   - 학생/교사 타겟 광고
   - Brilliant.org와 비교 영상

4. **수익화**
   - YouTube 파트너 프로그램
   - Patreon 후원
   - 온라인 강좌 판매

---

## 9. 예상 결과

### 3개월 후 (영상 100개)

- YouTube 구독자: 1,000-5,000명
- 총 조회수: 50,000-200,000
- 평균 평점: 4.5/5.0
- AI 스타일 학습 완료 (사용자 선호도 완전 반영)

### 1년 후 (영상 500개)

- YouTube 구독자: 10,000-50,000명
- 총 조회수: 500,000-2,000,000
- 수익화 시작 (YouTube 광고)
- 유료 강좌 론칭

---

## 10. 비용 vs 가치

### 비용

- **프로토타입**: ~$0-1/월 (거의 무료!)
- **본격 운영**: $5-25/월 (매우 저렴)
- **대규모**: $50-100/월 (합리적)

### 가치

- **시간 절약**: 영상 1개당 수동 제작 시 10-20시간 → 자동 5-10분
- **일관성**: AI가 항상 동일한 품질 유지
- **확장성**: 하루 10개 이상 영상 제작 가능
- **학습 능력**: 시간이 지날수록 품질 향상

**ROI**: 매우 높음! 🚀

---

## 11. 시작하기

**다음 세션에서 바로 시작하려면**:

1. 이 문서를 새 세션에 첨부
2. "Phase 0: 환경 설정부터 시작해줘" 요청
3. 단계별로 진행

**준비물**:
- M4 Mac (✅ 보유)
- Stable Diffusion (✅ 설치됨)
- API 키 발급:
  - Google AI Studio (Gemini) - 무료
  - Anthropic (Claude) - $5 충전
  - ElevenLabs - 무료 계정
  - YouTube Data API - 무료

**예상 첫 영상 완성 시간**: 세션 1-2 완료 후 (8시간 내)

---

**✅ 이 문서를 저장하고, 준비되면 새 세션에서 시작하세요!**
