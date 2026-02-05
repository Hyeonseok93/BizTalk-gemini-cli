# BizTone Converter - 프로젝트 컨텍스트

## 프로젝트 개요
**BizTone Converter**는 비즈니스 커뮤니케이션을 다듬기 위해 설계된 AI 기반 웹 솔루션입니다. 일상적인 말투나 초안 상태의 텍스트를 수신자에 맞춰 전문적인 비즈니스 언어로 변환합니다.
- **상사 (Upward):** 격식 있는 보고 형식, 결론부터 제시(두괄식).
- **동료 (Lateral):** 정중하고 협력적인 태도, 명확한 요청 사항.
- **고객 (External):** 극존칭 사용, 서비스 마인드 강조, 고객 중심적 표현.

## 기술 스택
- **프론트엔드:** HTML5, Tailwind CSS (CDN 방식), JavaScript (Vanilla JS).
- **백엔드:** Python (3.11+), Flask, Flask-CORS.
- **AI 통합:** Groq API (모델: `moonshotai/kimi-k2-instruct-0905`).
- **환경 관리:** `python-dotenv`.

## 아키텍처
본 프로젝트는 Flask 백엔드가 정적 프론트엔드 자산과 REST API를 모두 제공하는 구조를 따릅니다.

```
Root
├── backend/            # Flask 서버 및 API 로직
│   ├── app.py          # 메인 엔트리 포인트, API 라우트, Groq 연동
│   └── requirements.txt
├── frontend/           # 정적 자산
│   ├── index.html      # 메인 UI (Tailwind CSS 적용)
│   ├── css/            # 커스텀 스타일 및 애니메이션
│   └── js/             # 클라이언트 측 로직
└── .env                # 환경 변수 (GROQ_API_KEY)
```

## 설정 및 실행 방법
1.  **사전 요구 사항:** Python 3.11 이상, Groq API 키.
2.  **의존성 설치:**
    ```bash
    pip install -r backend/requirements.txt
    ```
3.  **환경 설정:**
    - 루트 디렉토리에 `.env` 파일을 생성하고 `GROQ_API_KEY=your_key`를 추가합니다.
4.  **서버 실행:**
    ```bash
    python backend/app.py
    ```
    - `http://localhost:5000` 접속을 통해 애플리케이션을 확인할 수 있습니다.

## 주요 기능 및 로직
- **말투 변환:** 각 대상(상사, 동료, 고객)별로 최적화된 시스템 프롬프트를 사용하여 상황에 적절한 결과를 보장합니다.
- **UI/UX:** Tailwind CSS를 활용한 현대적인 글래스모피즘(Glassmorphism) 디자인. 실시간 글자 수 계산, 원클릭 복사, 피드백 수집 기능을 포함합니다.
- **에러 처리:** 견고한 백엔드 로깅 및 사용자 친화적인 프론트엔드 에러 메시지를 제공합니다.

## 개발 컨벤션
- **스타일링:** 주로 Tailwind CSS 유틸리티 클래스를 사용합니다. 커스텀 애니메이션은 `frontend/css/style.css`에 정의되어 있습니다.
- **API:**
    - 엔드포인트: `POST /api/convert`
    - 페이로드: `{ "text": "...", "target": "upward|lateral|external" }`
    - 응답: `{ "converted_text": "...", "original_text": "...", "target": "..." }`
- **Git:** 표준 `main` 브랜치 워크플로우를 따릅니다. 커밋 메시지는 변경 사항을 명확히 설명해야 합니다.

## 관련 문서
- `PRD.md`: 상세 제품 요구사항 및 사용자 스토리.
- `프로그램개요서.md`: 상위 레벨 프로젝트 요약 및 아키텍처 다이어그램.