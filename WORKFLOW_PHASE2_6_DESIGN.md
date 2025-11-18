# Workflow 자동화 Phase 2~6 설계 문서

## 전체 개요

Mathiter 워크플로우 자동화 시스템의 나머지 단계(Phase 2~6) 구현 계획입니다.

### 완료된 작업 (Phase 1)
- ✅ Jira API 클라이언트 구현 (`lib/jira_client.py`)
- ✅ 테스트 완료 (KAN-5 이슈 생성)
- ✅ Stable Diffusion WebUI 설치 (로컬 이미지 생성)
- ✅ 네트워크 재시도 로직 추가

### 프로젝트 구조
```
/Users/justinminim4/projects/
├── backend/                    # Mathiter 백엔드
├── lib/                        # 워크플로우 라이브러리
│   ├── jira_client.py         # ✅ Jira API 클라이언트
│   ├── confluence_client.py   # ⏳ Phase 3
│   ├── blog_client.py         # ⏳ Phase 5
│   └── image_generator.py     # ⏳ Phase 4
├── config/
│   └── workflow_config.json   # API 키, 설정
├── wix/                        # Wix 코드
├── test_jira.py               # Jira 테스트 스크립트
└── workflow.py                # ⏳ Phase 6 - 메인 워크플로우
```

---

## Phase 2: AI 기반 작업 분류 시스템

### 목표
사용자 요청을 분석하여 자동으로 작업 타입을 분류하고 Jira 이슈를 생성합니다.

### 요구사항

1. **5가지 작업 타입 지원**
   - `SYSTEM_DEVELOPMENT`: 시스템 개발
   - `RESEARCH`: 자료 조사
   - `BLOG_WRITING`: 블로그 글 작성
   - `YOUTUBE_VIDEO`: 유튜브 영상 제작
   - `OTHER`: 기타

2. **작업 분류 기준**
   - Gemini AI를 사용하여 사용자 요청 분석
   - 자동/수동 작업 분리
   - 우선순위 자동 설정

3. **자동/수동 태스크 분리**
   - **자동 태스크**: Claude Code가 수행 가능한 작업
     - 코드 작성, 버그 수정, API 통합, 테스트 작성 등
   - **수동 태스크**: 사용자가 직접 수행해야 하는 작업
     - 블로그 초안 작성, 영상 촬영, 디자인 리뷰 등

### 구현 파일

#### `lib/task_analyzer.py`
```python
"""
AI 기반 작업 분석 및 분류
"""
from google import genai
from config import Config
from utils.logger import setup_logger

class TaskAnalyzer:
    def __init__(self, ai_client):
        self.ai_client = ai_client

    def analyze_task(self, user_request: str) -> dict:
        """
        사용자 요청을 분석하여 작업 정보 반환

        Returns:
            {
                'task_type': 'SYSTEM_DEVELOPMENT',
                'summary': '이슈 제목',
                'description': '상세 설명',
                'priority': 'High',
                'estimated_hours': 4,
                'subtasks': [
                    {
                        'summary': '서브태스크 제목',
                        'is_automated': True,  # 자동 가능
                        'description': '상세 내용'
                    },
                    ...
                ]
            }
        """
        pass

    def classify_task_type(self, request: str) -> str:
        """작업 타입 분류"""
        pass

    def split_automated_manual(self, subtasks: list) -> tuple:
        """자동/수동 태스크 분리"""
        pass
```

#### `lib/workflow_orchestrator.py`
```python
"""
워크플로우 오케스트레이터
Jira, AI, 사용자 승인을 조율
"""
class WorkflowOrchestrator:
    def __init__(self, jira_client, task_analyzer):
        self.jira = jira_client
        self.analyzer = task_analyzer

    def create_workflow(self, user_request: str) -> str:
        """
        전체 워크플로우 생성
        1. 요청 분석
        2. Jira 이슈 생성
        3. 서브태스크 생성 (자동/수동 라벨링)
        4. 승인 대기

        Returns:
            issue_key (예: KAN-10)
        """
        pass

    def execute_automated_tasks(self, issue_key: str):
        """자동 태스크 실행"""
        pass
```

### AI 프롬프트 설계

**작업 분류 프롬프트:**
```
사용자 요청: "{user_request}"

위 요청을 분석하여 다음 형식으로 반환하세요:

{
  "task_type": "SYSTEM_DEVELOPMENT | RESEARCH | BLOG_WRITING | YOUTUBE_VIDEO | OTHER",
  "summary": "이슈 제목 (50자 이내)",
  "description": "상세 설명",
  "priority": "High | Medium | Low",
  "estimated_hours": 예상 작업 시간(숫자),
  "subtasks": [
    {
      "summary": "서브태스크 제목",
      "is_automated": true/false,
      "description": "상세 설명",
      "labels": ["automation" 또는 "manual"]
    }
  ]
}

**분류 기준:**
- SYSTEM_DEVELOPMENT: 코드 작성, 버그 수정, 기능 추가
- RESEARCH: 자료 조사, 기술 검토
- BLOG_WRITING: 블로그 글 작성, 콘텐츠 제작
- YOUTUBE_VIDEO: 영상 기획, 촬영, 편집
- OTHER: 위에 해당하지 않는 작업

**자동/수동 판단:**
- is_automated: true → Claude Code가 수행 가능
- is_automated: false → 사용자가 직접 수행
```

### 테스트 시나리오

**테스트 1: 시스템 개발**
```python
# test_task_analyzer.py
user_request = "Mathiter에 타이머 일시정지 기능 추가해줘"

expected_output = {
    "task_type": "SYSTEM_DEVELOPMENT",
    "summary": "타이머 일시정지 기능 추가",
    "subtasks": [
        {"summary": "프론트엔드 UI 버튼 추가", "is_automated": True},
        {"summary": "타이머 상태 관리 로직 구현", "is_automated": True},
        {"summary": "UI/UX 디자인 검토", "is_automated": False}
    ]
}
```

**테스트 2: 블로그 글 작성**
```python
user_request = "중학생을 위한 이차방정식 개념 블로그 글 작성"

expected_output = {
    "task_type": "BLOG_WRITING",
    "summary": "이차방정식 개념 블로그 글 작성",
    "subtasks": [
        {"summary": "블로그 초안 작성 (네이버)", "is_automated": False},
        {"summary": "이미지 생성 (Stable Diffusion)", "is_automated": True},
        {"summary": "Wix 블로그 자동 등록", "is_automated": True}
    ]
}
```

---

## Phase 3: Confluence 문서 자동화

### 목표
Jira 이슈와 연결된 Confluence 문서를 자동으로 생성하고 관리합니다.

### 요구사항

1. **문서 자동 생성**
   - Jira 이슈 생성 시 Confluence 문서도 함께 생성
   - 이슈 키와 연결 (예: KAN-10 → Confluence 페이지)

2. **문서 내용**
   - 작업 상세 내역
   - 코드 변경 사항 (diff)
   - 테스트 결과
   - 이미지/스크린샷

3. **템플릿**
   - 작업 타입별 다른 템플릿 적용

### 구현 파일

#### `lib/confluence_client.py`
```python
"""
Confluence API 클라이언트
"""
class ConfluenceClient:
    def __init__(self, config: dict):
        self.base_url = config['base_url']
        self.email = config['email']
        self.api_token = config['api_token']
        self.space_key = config['space_key']
        self.auth = (self.email, self.api_token)

    def create_page(self, title: str, content: str, parent_id=None) -> dict:
        """
        Confluence 페이지 생성

        Returns:
            {
                'id': '페이지 ID',
                'url': 'https://...',
                'success': True
            }
        """
        pass

    def update_page(self, page_id: str, content: str, version: int):
        """페이지 업데이트"""
        pass

    def add_attachment(self, page_id: str, file_path: str):
        """파일 첨부"""
        pass

    def link_to_jira(self, page_id: str, issue_key: str):
        """Jira 이슈와 연결"""
        pass
```

### Confluence 템플릿

**시스템 개발 템플릿:**
```html
<h1>{issue_key}: {summary}</h1>

<h2>📋 작업 개요</h2>
<p>{description}</p>

<h2>✅ 완료된 작업</h2>
<ul>
  <li>서브태스크 1</li>
  <li>서브태스크 2</li>
</ul>

<h2>💻 코드 변경사항</h2>
<ac:structured-macro ac:name="code">
  <ac:parameter ac:name="language">python</ac:parameter>
  <ac:plain-text-body><![CDATA[
# 코드 diff
  ]]></ac:plain-text-body>
</ac:structured-macro>

<h2>🧪 테스트 결과</h2>
<p>테스트 통과 여부...</p>

<h2>🔗 관련 링크</h2>
<ul>
  <li>Jira: {jira_url}</li>
  <li>GitHub PR: {pr_url}</li>
</ul>
```

**블로그 글 템플릿:**
```html
<h1>{issue_key}: {blog_title}</h1>

<h2>📝 블로그 초안</h2>
<p>{draft_content}</p>

<h2>🖼️ 생성된 이미지</h2>
<ac:image>
  <ri:attachment ri:filename="image1.png" />
</ac:image>

<h2>🌐 발행 정보</h2>
<ul>
  <li>네이버 블로그: {naver_url}</li>
  <li>Wix 블로그: {wix_url}</li>
</ul>
```

---

## Phase 4: 이미지 생성 자동화

### 목표
Stable Diffusion을 이용한 블로그/영상용 이미지 자동 생성

### 요구사항

1. **로컬 Stable Diffusion 연동**
   - AUTOMATIC1111 WebUI API 사용
   - M4 Mac 최적화 (MPS)

2. **프롬프트 자동 생성**
   - Gemini AI로 이미지 프롬프트 생성
   - 컨텍스트 기반 (블로그 주제, 영상 내용)

3. **이미지 후처리**
   - 자동 크롭/리사이즈
   - 썸네일 생성

### 구현 파일

#### `lib/image_generator.py`
```python
"""
Stable Diffusion 이미지 생성
"""
import requests
import base64
from PIL import Image
import io

class ImageGenerator:
    def __init__(self, sd_url='http://127.0.0.1:7860'):
        self.sd_url = sd_url
        self.api_url = f"{sd_url}/sdapi/v1"

    def generate_prompt(self, context: str, image_type: str) -> str:
        """
        AI로 이미지 프롬프트 생성

        Args:
            context: 블로그 내용 또는 영상 설명
            image_type: 'thumbnail', 'illustration', 'diagram'

        Returns:
            Stable Diffusion 프롬프트
        """
        pass

    def generate_image(
        self,
        prompt: str,
        negative_prompt: str = "",
        model: str = "dreamshaper_8.safetensors",
        width: int = 512,
        height: int = 512
    ) -> bytes:
        """
        이미지 생성

        Returns:
            이미지 바이트 데이터
        """
        payload = {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "width": width,
            "height": height,
            "steps": 20,
            "cfg_scale": 7,
            "sampler_name": "DPM++ 2M"
        }

        response = requests.post(
            f"{self.api_url}/txt2img",
            json=payload
        )

        if response.ok:
            r = response.json()
            image_data = base64.b64decode(r['images'][0])
            return image_data
        else:
            raise Exception(f"이미지 생성 실패: {response.status_code}")

    def save_image(self, image_data: bytes, file_path: str):
        """이미지 저장"""
        with open(file_path, 'wb') as f:
            f.write(image_data)

    def create_thumbnail(self, image_data: bytes, size=(512, 512)) -> bytes:
        """썸네일 생성"""
        img = Image.open(io.BytesIO(image_data))
        img.thumbnail(size)

        output = io.BytesIO()
        img.save(output, format='PNG')
        return output.getvalue()
```

### 프롬프트 생성 예시

**Gemini AI 프롬프트:**
```
블로그 주제: "중학생을 위한 이차방정식 개념 설명"

위 주제에 적합한 Stable Diffusion 이미지 프롬프트를 생성하세요.

요구사항:
- 스타일: 교육용, 친근한 일러스트
- 모델: DreamShaper 8
- 포함 요소: 수식, 그래프, 학생 캐릭터
- 색상: 밝고 화사한 색상

출력 형식:
{
  "positive_prompt": "영문 프롬프트 (구체적으로)",
  "negative_prompt": "피해야 할 요소",
  "suggested_model": "dreamshaper_8",
  "width": 768,
  "height": 512
}
```

**예상 출력:**
```json
{
  "positive_prompt": "educational illustration, friendly student character studying quadratic equation, colorful math graph, mathematical formula on blackboard, bright and cheerful atmosphere, clean design, digital art, high quality",
  "negative_prompt": "dark, scary, complex, text, watermark, signature, blurry",
  "suggested_model": "dreamshaper_8",
  "width": 768,
  "height": 512
}
```

---

## Phase 5: 블로그 자동 발행

### 목표
네이버 블로그 초안을 Wix 블로그에 자동으로 발행

### 요구사항

1. **Wix 블로그 API 연동**
   - 글 작성 API
   - 이미지 업로드
   - 카테고리 설정

2. **네이버 블로그 참조**
   - 사용자가 작성한 네이버 블로그 URL 입력
   - 내용 파싱 (선택적, 또는 사용자가 직접 제공)

3. **자동 변환**
   - 마크다운 → HTML
   - 이미지 자동 삽입

### 구현 파일

#### `lib/blog_client.py`
```python
"""
Wix 블로그 API 클라이언트
"""
class WixBlogClient:
    def __init__(self, config: dict):
        self.api_key = config['api_key']
        self.site_id = config['site_id']
        self.base_url = 'https://www.wixapis.com/v3'

    def create_post(
        self,
        title: str,
        content: str,  # HTML
        category_id: str = None,
        tags: list = None,
        featured_image_url: str = None
    ) -> dict:
        """
        블로그 포스트 생성

        Returns:
            {
                'post_id': '...',
                'url': 'https://...',
                'success': True
            }
        """
        pass

    def upload_image(self, image_path: str) -> str:
        """
        이미지 업로드

        Returns:
            이미지 URL
        """
        pass

    def publish_post(self, post_id: str):
        """포스트 발행 (초안 → 공개)"""
        pass
```

### 워크플로우

```
1. 사용자: 네이버 블로그 초안 작성 완료
2. 사용자: Jira에서 "승인" 댓글 작성
3. 시스템: 승인 감지
4. 시스템: 이미지 생성 (Phase 4)
5. 시스템: 이미지 Wix 업로드
6. 시스템: 블로그 글 작성 (HTML 변환)
7. 시스템: Wix 발행
8. 시스템: Confluence에 결과 기록
9. 시스템: Jira 이슈 완료 처리
```

---

## Phase 6: 전체 워크플로우 통합

### 목표
모든 단계를 통합하여 완전 자동화된 워크플로우 구축

### 메인 스크립트

#### `workflow.py` (개선)
```python
"""
Mathiter 워크플로우 자동화 메인 스크립트
"""
import sys
from lib.jira_client import JiraClient
from lib.confluence_client import ConfluenceClient
from lib.task_analyzer import TaskAnalyzer
from lib.workflow_orchestrator import WorkflowOrchestrator
from lib.image_generator import ImageGenerator
from lib.blog_client import WixBlogClient
from utils.ai_client import initialize_ai_client
import json
from pathlib import Path

def load_config():
    """설정 로드"""
    config_path = Path(__file__).parent / "config" / "workflow_config.json"
    with open(config_path, 'r') as f:
        return json.load(f)

def main():
    """메인 워크플로우"""
    print("🚀 Mathiter 워크플로우 자동화 시작\n")

    # 1. 설정 로드
    config = load_config()

    # 2. 클라이언트 초기화
    jira = JiraClient(config['jira'])
    confluence = ConfluenceClient(config['confluence'])
    ai_client = initialize_ai_client()
    task_analyzer = TaskAnalyzer(ai_client)
    image_gen = ImageGenerator()
    blog_client = WixBlogClient(config['wix'])

    # 3. 오케스트레이터 초기화
    orchestrator = WorkflowOrchestrator(
        jira=jira,
        confluence=confluence,
        task_analyzer=task_analyzer,
        image_gen=image_gen,
        blog_client=blog_client
    )

    # 4. 사용자 요청 입력
    print("작업을 설명해주세요:")
    user_request = input("> ")

    # 5. 워크플로우 실행
    try:
        issue_key = orchestrator.create_workflow(user_request)
        print(f"\n✅ Jira 이슈 생성: {issue_key}")
        print(f"   URL: {jira.base_url}/browse/{issue_key}")

        # 승인 대기
        print(f"\n⏳ Jira에서 승인을 기다리는 중...")
        approved = jira.wait_for_approval(issue_key)

        if approved:
            print("\n✅ 승인됨! 자동 작업 실행 중...")
            orchestrator.execute_automated_tasks(issue_key)
            print("\n🎉 모든 작업 완료!")
        else:
            print("\n⏱️ 타임아웃 또는 승인되지 않음")

    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

### CLI 인터페이스 (선택적)

```bash
# 대화형 모드
python workflow.py

# 커맨드 라인 모드
python workflow.py --request "타이머 일시정지 기능 추가"

# 이슈 직접 지정
python workflow.py --issue KAN-10

# 테스트 모드 (Jira 생성 없이 로컬 테스트)
python workflow.py --test --request "블로그 글 작성"
```

---

## Phase 2.5: 멀티 AI 코드 리뷰 (추가)

### 목표
작성된 코드를 여러 AI로 리뷰하여 품질 보장

### 워크플로우

```
1. Claude Code: 코드 작성
2. Gemini: 1차 리뷰 (구조, 성능)
3. GPT-4: 2차 리뷰 (보안, 베스트 프랙티스)
4. Claude: 리뷰 결과 반영 및 최종 검증
5. Jira/Confluence에 리뷰 결과 기록
```

### 구현 파일

#### `lib/code_reviewer.py`
```python
"""
멀티 AI 코드 리뷰어
"""
class CodeReviewer:
    def __init__(self, gemini_client, openai_client, claude_client):
        self.gemini = gemini_client
        self.openai = openai_client
        self.claude = claude_client

    def review_with_gemini(self, code: str) -> dict:
        """Gemini로 코드 리뷰"""
        pass

    def review_with_gpt4(self, code: str) -> dict:
        """GPT-4로 코드 리뷰"""
        pass

    def review_with_claude(self, code: str) -> dict:
        """Claude로 최종 검증"""
        pass

    def merge_reviews(self, reviews: list) -> str:
        """리뷰 결과 통합"""
        pass
```

---

## 구현 순서 및 예상 시간

| Phase | 작업 내용 | 예상 시간 | 토큰 예상 |
|-------|----------|----------|----------|
| Phase 2 | AI 작업 분류 시스템 | 2-3시간 | 50K |
| Phase 2.5 | 멀티 AI 코드 리뷰 | 1-2시간 | 30K |
| Phase 3 | Confluence 자동화 | 1-2시간 | 30K |
| Phase 4 | 이미지 생성 자동화 | 1-2시간 | 25K |
| Phase 5 | 블로그 자동 발행 | 1-2시간 | 30K |
| Phase 6 | 전체 통합 및 테스트 | 2-3시간 | 35K |
| **합계** | | **8-14시간** | **200K** |

**토큰 관리 전략:**
- 각 Phase를 별도 세션에서 진행
- Phase 2와 2.5를 한 세션에서 처리 가능
- Phase 3~5는 각각 독립적으로 진행
- Phase 6은 별도 세션 (통합 테스트)

---

## 설정 파일 구조

### `config/workflow_config.json`
```json
{
  "jira": {
    "base_url": "https://sspark222.atlassian.net",
    "project_key": "KAN",
    "email": "sspark222@gmail.com",
    "api_token": "ATATT3x..."
  },
  "confluence": {
    "base_url": "https://sspark222.atlassian.net/wiki",
    "space_key": "MATHITER",
    "email": "sspark222@gmail.com",
    "api_token": "ATATT3x..."
  },
  "wix": {
    "api_key": "발급 필요",
    "site_id": "발급 필요"
  },
  "stable_diffusion": {
    "url": "http://127.0.0.1:7860",
    "default_model": "dreamshaper_8.safetensors"
  },
  "ai": {
    "gemini_project_id": "my-mvp-backend",
    "openai_api_key": "발급 필요 (선택)"
  }
}
```

---

## 테스트 계획

### Phase 2 테스트
```python
# test_phase2.py
def test_system_development_workflow():
    """시스템 개발 워크플로우 테스트"""
    user_request = "Mathiter에 다크모드 추가해줘"

    # 1. 작업 분석
    result = analyzer.analyze_task(user_request)
    assert result['task_type'] == 'SYSTEM_DEVELOPMENT'
    assert len(result['subtasks']) > 0

    # 2. Jira 이슈 생성
    issue_key = orchestrator.create_workflow(user_request)
    assert issue_key.startswith('KAN-')

    # 3. 서브태스크 확인
    issue = jira.get_issue(issue_key)
    assert 'automation' in issue['fields']['labels']

def test_blog_writing_workflow():
    """블로그 워크플로우 테스트"""
    user_request = "피타고라스 정리 블로그 글 작성"

    result = analyzer.analyze_task(user_request)
    assert result['task_type'] == 'BLOG_WRITING'
```

---

## 다음 세션에서 사용할 프롬프트

```markdown
Phase 1이 완료된 Mathiter 워크플로우 자동화 프로젝트를 이어서 진행합니다.

## 프로젝트 경로
- 작업 디렉토리: /Users/justinminim4/projects
- 설계 문서: WORKFLOW_PHASE2_6_DESIGN.md (이 파일을 먼저 읽어주세요)

## 완료된 작업
✅ Phase 1: Jira API 클라이언트, SD 설치, 네트워크 재시도

## 현재 작업
Phase 2: AI 기반 작업 분류 시스템 구현

설계 문서를 참고하여 Phase 2부터 구현해주세요.
파일 위치: /Users/justinminim4/projects/WORKFLOW_PHASE2_6_DESIGN.md
```

---

## 참고 자료

- Jira REST API: https://developer.atlassian.com/cloud/jira/platform/rest/v3/
- Confluence REST API: https://developer.atlassian.com/cloud/confluence/rest/v1/
- Stable Diffusion API: https://github.com/AUTOMATIC1111/stable-diffusion-webui/wiki/API
- Wix Blog API: https://dev.wix.com/api/rest/wix-blog/blog
- Google Gemini API: https://ai.google.dev/docs

---

**작성일:** 2025-11-18
**버전:** 1.0
**작성자:** Claude Code + 사용자
