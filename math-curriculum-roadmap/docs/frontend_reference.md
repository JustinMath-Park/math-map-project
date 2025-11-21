# Brilliant.org Reference Notes

## Observed Patterns
- 페이지 전환 없이 모듈 단위로 콘텐츠가 이어지는 SPA(Single Page Application) 패턴.
- 섹션 단위 스크롤 애니메이션과 reactive progress bar.
- MathJax/KaTeX 기반 수식 렌더링.
- SVG/Canvas 애니메이션으로 인터랙티브 그래프 제공.

## Stack 추정 및 검증 방법
1. **DevTools → Elements/Network**: `webpack`, `next`, `react` 키워드 검색으로 React/Next.js 여부 확인.
2. **Sources → `__NEXT_DATA__`**: 존재한다면 Next.js.
3. **Network → JS bundle**: `/_next/static` 요청 확인.
4. **Fonts/CSS**: custom webfont + tailwind 유사 유틸 클래스를 통해 스타일 시스템 파악.

현재 네트워크 접근 제약으로 실제 html 소스를 직접 가져오지는 못했지만, 이전 공개 정보와 DevTools 패턴을 근거로 React/Next.js 기반일 가능성이 높습니다. 향후 집/회사 환경에서 DevTools로 위 항목을 확인해주시면, 해당 정보를 토대로 컴포넌트 아키텍처를 더 구체화할 수 있습니다.

## 구현 포인트
- **Section-based Flow**: 각 커리큘럼 도메인을 stepper 형태로 구성.
- **Sticky Sidebar**: 학습 진행률과 관련 문제목록을 고정된 패널에 배치.
- **Transition Animations**: Framer Motion 또는 GSAP으로 smooth transition.
- **Problem Blocks**: Q&A 카드 형태 + 즉시 채점.
