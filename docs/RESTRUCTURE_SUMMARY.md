# 프로젝트 구조 재정리 요약

## 변경된 디렉토리 구조

### 새로운 선호 구조에 따른 변경사항:

- `src/config` → `src/Config`
- `src/models` → `src/Entity`
- `src/services` → `src/Service`
- `src/ui` → `src/UI`
- `src/utils` → `src/Utils`
- `prompts/` → `src/Prompts`
- `src/templates` → `src/UI` (병합됨)

### 새로 생성된 디렉토리:

- `src/Controller` - API 엔드포인트용
- `src/IService` - 서비스 인터페이스용
- `docs/` - 프로젝트 문서용
- `backup/` - 백업 파일용

## 백업된 파일들

### backup/duplicate_files/

- `requirements_windows.txt` (requirements.txt와 중복)
- `install_and_run.bat` (run.bat로 대체됨)
- `install_and_run.sh` (run.sh로 대체됨)
- `run_app.bat` (기능 중복)

### backup/unused_files/

- `debug_selectbox.py` (디버그 스크립트)
- `recreate_venv.bat` (유틸리티 스크립트)
- `check_gpu.py` (유틸리티 스크립트)
- `constraints.txt` (사용되지 않는 제약 파일)

### backup/dev_docs/

- `README_REFACTORING.md` (개발 문서)
- `CLAUDE.md` (개발 노트)

## 업데이트된 import 문

모든 Python 파일의 import 문이 새로운 디렉토리 구조에 맞게 업데이트되었습니다:

```python
# 이전
from src.config.settings import settings
from src.models.content_types import CourseConfig
from src.services.ai_service import ai_service
from src.ui.sidebar import SidebarUI
from src.utils.logger import content_logger

# 변경 후
from src.Config.settings import settings
from src.Entity.content_types import CourseConfig
from src.Service.ai_service import ai_service
from src.UI.sidebar import SidebarUI
from src.Utils.logger import content_logger
```

## 최종 프로젝트 구조

```
Automated-Course-Content-Generator/
├── app.py                    # 메인 애플리케이션
├── run.bat                   # Windows 실행 스크립트
├── run.sh                    # Linux/Mac 실행 스크립트
├── requirements.txt          # Python 의존성
├── .env.example             # 환경 설정 예시
├── .gitignore               # Git 무시 파일
├── README.md                # 개발자 가이드
├── LICENSE                  # 라이선스
├── docs/                    # 프로젝트 문서
├── logs/                    # 로그 디렉토리
├── output/                  # 생성 결과물
├── backup/                  # 백업 파일들
└── src/
    ├── Config/              # 설정 파일
    ├── Controller/          # API 엔드포인트
    ├── Entity/              # DTO, 엔티티
    ├── IService/            # 서비스 인터페이스
    ├── Service/             # 서비스 로직 구현
    ├── UI/                  # 뷰, 프론트엔드
    ├── Utils/               # 공통 유틸리티
    └── Prompts/             # AI 프롬프트
```

이제 프로젝트가 선호하는 코드 구조에 맞게 재정리되었습니다.
