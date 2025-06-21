# 초등 디지털 교과서 컨텐츠 생성기 - 리팩토링 문서

## 프로젝트 구조 개선

### 이전 구조

- `app.py` - 모든 코드가 하나의 파일에 627줄로 구성

### 새로운 구조

```
Automated-Course-Content-Generator/
├── app.py                    # 메인 엔트리 포인트 (간소화됨)
├── src/                      # 소스 코드 패키지
│   ├── __init__.py
│   ├── config/              # 설정 관리
│   │   ├── __init__.py
│   │   └── settings.py      # 모든 설정값 중앙 관리
│   ├── services/            # 비즈니스 로직
│   │   ├── __init__.py
│   │   ├── ai_service.py    # AI 클라이언트 및 컨텐츠 생성
│   │   ├── image_service.py # Unsplash API 통합
│   │   └── export_service.py # PDF/HTML 내보내기
│   ├── ui/                  # UI 컴포넌트
│   │   ├── __init__.py
│   │   ├── sidebar.py       # 사이드바 설정 UI
│   │   └── content_display.py # 컨텐츠 표시 UI
│   ├── utils/               # 유틸리티
│   │   ├── __init__.py
│   │   ├── session_manager.py # 세션 상태 관리
│   │   └── validators.py    # 입력값 검증
│   └── models/              # 데이터 모델
│       ├── __init__.py
│       └── content_types.py # 데이터 클래스 정의
└── prompts/                 # 기존 프롬프트 (변경 없음)
```

## 주요 개선사항

### 1. 단일 책임 원칙 (Single Responsibility Principle)

각 모듈이 하나의 명확한 책임만 가지도록 분리:

- `ai_service.py`: AI 클라이언트 관리 및 컨텐츠 생성
- `image_service.py`: 이미지 검색 및 처리
- `export_service.py`: 파일 내보내기 기능
- `session_manager.py`: 세션 상태 관리
- `validators.py`: 입력값 검증

### 2. 설정 중앙화

- `settings.py`에서 모든 설정값을 중앙 관리
- 환경 변수, UI 옵션, API 설정 등을 한 곳에서 관리

### 3. 데이터 모델 사용

- `dataclass`를 사용한 타입 안전한 데이터 구조
- `CourseConfig`, `ImageInfo`, `GeneratedContent` 등 명확한 데이터 모델

### 4. UI 컴포넌트 분리

- 사이드바와 메인 컨텐츠 영역을 별도 모듈로 분리
- 재사용 가능한 UI 컴포넌트 구조

### 5. 에러 처리 개선

- 각 서비스에서 적절한 에러 처리
- 사용자 친화적인 에러 메시지

## 사용 방법

기존과 동일하게 애플리케이션 실행:

```bash
streamlit run app.py
```

## 환경 설정

`.env` 파일에 필요한 API 키 설정:

```
OPENAI_API_KEY=your_key_here
OPENROUTER_API_KEY=your_key_here
UNSPLASH_API_KEY=your_key_here
```

## 향후 개선 가능 사항

1. **테스트 추가**: 각 모듈에 대한 유닛 테스트
2. **로깅 시스템**: 구조화된 로깅 추가
3. **비동기 처리**: AI 요청 및 이미지 검색의 비동기 처리
4. **캐싱**: 생성된 컨텐츠 및 이미지 캐싱
5. **데이터베이스**: 파일 기반 저장소 대신 적절한 데이터베이스 사용
