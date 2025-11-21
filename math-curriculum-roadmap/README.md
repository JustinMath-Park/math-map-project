# Math Curriculum Roadmap

SAT, AP Calculus, IGCSE, A-Level 등의 공식 커리큘럼을 정리하고 Firebase에 저장하여 학년/시험별 로드맵과 학습 플로우를 제공하는 웹 애플리케이션.

## 🎯 프로젝트 목표

- 표준화된 수학 커리큘럼 데이터 관리
- 시험별/학년별 학습 경로 시각화
- 인터랙티브한 강의 플로우 제공

## 📁 프로젝트 구조

```
math-curriculum-roadmap/
├── frontend/              # 정적 웹 애플리케이션
│   ├── index.html        # 메인 커리큘럼 로드맵
│   ├── lecture.html      # 강의 상세 페이지
│   ├── app.js            # 메인 로직
│   ├── lecture.js        # 강의 페이지 로직
│   ├── js/
│   │   ├── config.js     # 환경 설정
│   │   └── modules/
│   │       └── katex-helper.js  # 수식 렌더링
│   ├── data/             # JSON 데이터 파일
│   ├── assets/           # 이미지, SVG 등
│   └── *.css            # 스타일시트
├── scripts/              # 데이터 관리 스크립트
│   ├── seed_curriculums.py  # Firestore 커리큘럼 업로드
│   └── seed_lectures.py     # Firestore 강의 업로드
├── docs/                 # 문서
├── firebase.json         # Firebase 호스팅 설정
├── .firebaserc          # Firebase 프로젝트 설정
└── requirements.txt     # Python 의존성

```

## 🚀 Quick Start

### 로컬 개발

1. **프로젝트 클론**
```bash
cd math-curriculum-roadmap
```

2. **로컬 서버 실행**
```bash
cd frontend
python3 -m http.server 8000
# 또는
npx serve .
```

3. **브라우저에서 확인**
```
http://localhost:8000
```

### Firebase Hosting 배포

상세 배포 가이드는 [DEPLOYMENT.md](DEPLOYMENT.md)를 참고하세요.

```bash
# Firebase 로그인
firebase login

# 로컬 미리보기
firebase serve --only hosting

# 배포
firebase deploy --only hosting
```

## 📊 데이터 관리

### Firestore에 데이터 업로드

```bash
# 가상환경 활성화
source venv/bin/activate

# 커리큘럼 데이터 업로드
python scripts/seed_curriculums.py

# 강의 데이터 업로드
python scripts/seed_lectures.py
```

## 🛠 기술 스택

- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **수식 렌더링**: KaTeX
- **데이터베이스**: Firebase Firestore
- **호스팅**: Firebase Hosting
- **백엔드 스크립트**: Python 3.14

## ✅ 최근 개선사항 (2024-11-21)

- ✅ katex-helper.js 모듈 추가
- ✅ 환경 설정 시스템 구축 (config.js)
- ✅ .gitignore 추가 (보안 강화)
- ✅ Firebase Hosting 설정 완료
- ✅ API endpoint 환경별 자동 감지

## 📝 진행 로그

- 2024-11-19: 초기 구조 생성
- 2024-11-21: 프로덕션 배포 준비 완료
