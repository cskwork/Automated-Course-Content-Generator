@echo off
echo 가상환경을 재생성합니다...
echo.

REM 기존 가상환경 삭제
if exist venv (
    echo 기존 가상환경을 삭제합니다...
    rmdir /s /q venv
)

echo.
echo 새 가상환경을 생성합니다...
python -m venv venv

echo.
echo 가상환경을 활성화합니다...
call venv\Scripts\activate.bat

echo.
echo pip를 업그레이드합니다...
python -m pip install --upgrade pip

echo.
echo requirements.txt에서 패키지를 설치합니다...
pip install -r requirements.txt

echo.
echo 설치 완료! 다음 명령으로 앱을 실행하세요:
echo streamlit run app.py
echo.
pause 