@echo off
REM Windows 설치 및 실행 스크립트
echo ========================================
echo  Automated Course Content Generator
echo  Windows 설치 및 실행 스크립트
echo ========================================

REM Python 설치 확인
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python이 설치되지 않았습니다.
    echo Python 3.12 이상을 설치해주세요: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [INFO] Python 버전 확인 중...
python --version

REM 가상환경 생성 및 활성화
echo [INFO] 가상환경 생성 중...
if not exist "venv" (
    python -m venv venv
    echo [SUCCESS] 가상환경이 성공적으로 생성되었습니다.
) else (
    echo [INFO] 가상환경이 이미 존재합니다.
)

echo [INFO] 가상환경 활성화 중...
call venv\Scripts\activate.bat

REM 의존성 설치
echo [INFO] 의존성 패키지 설치 중...
pip install --upgrade pip
pip install -r requirements.txt

REM .env 파일 확인
if not exist ".env" (
    if exist ".env.example" (
        echo [WARNING] .env 파일이 없습니다. .env.example을 참고하여 .env 파일을 생성해주세요.
    ) else (
        echo [WARNING] .env 파일이 없습니다. OpenAI API 키 등 환경 변수를 설정해주세요.
    )
    echo [INFO] .env 파일 생성 후 다시 실행해주세요.
    pause
    exit /b 1
)

REM Streamlit 애플리케이션 실행
echo [INFO] Streamlit 애플리케이션을 시작합니다...
echo [INFO] 브라우저에서 http://localhost:8501 로 접속하세요.
echo [INFO] 종료하려면 Ctrl+C를 누르세요.
echo ========================================

streamlit run app.py

pause 