#!/bin/bash

# macOS/Linux 설치 및 실행 스크립트
echo "========================================"
echo " Automated Course Content Generator"
echo " macOS/Linux 설치 및 실행 스크립트"
echo "========================================"

# Python 설치 확인
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python3가 설치되지 않았습니다."
    echo "Python 3.12 이상을 설치해주세요:"
    echo "macOS: brew install python@3.12"
    echo "Ubuntu: sudo apt update && sudo apt install python3.12 python3.12-venv"
    exit 1
fi

echo "[INFO] Python 버전 확인 중..."
python3 --version

# 가상환경 생성 및 활성화
echo "[INFO] 가상환경 생성 중..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "[SUCCESS] 가상환경이 성공적으로 생성되었습니다."
else
    echo "[INFO] 가상환경이 이미 존재합니다."
fi

echo "[INFO] 가상환경 활성화 중..."
source venv/bin/activate

# 의존성 설치
echo "[INFO] 의존성 패키지 설치 중..."
pip install --upgrade pip
pip install -r requirements.txt

# .env 파일 확인
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo "[WARNING] .env 파일이 없습니다. .env.example을 참고하여 .env 파일을 생성해주세요."
    else
        echo "[WARNING] .env 파일이 없습니다. OpenAI API 키 등 환경 변수를 설정해주세요."
    fi
    echo "[INFO] .env 파일 생성 후 다시 실행해주세요."
    exit 1
fi

# Streamlit 애플리케이션 실행
echo "[INFO] Streamlit 애플리케이션을 시작합니다..."
echo "[INFO] 브라우저에서 http://localhost:8501 로 접속하세요."
echo "[INFO] 종료하려면 Ctrl+C를 누르세요."
echo "========================================"

streamlit run app.py 