#!/bin/bash

# macOS/Linux 설치 및 실행 스크립트
echo "========================================"
echo " Automated Course Content Generator"
echo " macOS/Linux 설치 및 실행 스크립트"
echo "========================================"

# Python 설치 확인
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python3가 설치되지 않았습니다."
    echo "Python 3.9 이상을 설치해주세요:"
    echo "macOS: brew install python@3.10"
    echo "Ubuntu: sudo apt update && sudo apt install python3.10 python3.10-venv"
    exit 1
fi

echo "[INFO] Python 버전 확인 중..."
python3 --version

# 플랫폼 감지
PLATFORM=$(uname -s)
ARCH=$(uname -m)
echo "[INFO] 플랫폼: $PLATFORM, 아키텍처: $ARCH"

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

# 플랫폼별 PyTorch 설치
if [[ "$PLATFORM" == "Darwin" ]]; then
    if [[ "$ARCH" == "arm64" ]]; then
        # Apple Silicon (M1/M2/M3)
        echo "[INFO] Apple Silicon용 PyTorch 확인 중..."
        if ! python3 -c "import torch" 2>/dev/null; then
            echo "[INFO] PyTorch가 설치되지 않았습니다. 설치 중..."
            pip install torch torchvision torchaudio
        else
            echo "[INFO] PyTorch가 이미 설치되어 있습니다."
        fi
        echo "[SUCCESS] Apple Silicon 최적화 PyTorch가 설치되었습니다."
    else
        # Intel Mac
        echo "[INFO] Intel Mac용 PyTorch 확인 중..."
        if ! python3 -c "import torch" 2>/dev/null; then
            echo "[INFO] PyTorch가 설치되지 않았습니다. 설치 중..."
            pip install torch torchvision torchaudio
        else
            echo "[INFO] PyTorch가 이미 설치되어 있습니다."
        fi
        echo "[SUCCESS] Intel Mac용 PyTorch가 설치되었습니다."
    fi
elif [[ "$PLATFORM" == "Linux" ]]; then
    # NVIDIA GPU 확인 (Linux)
    if command -v nvidia-smi &> /dev/null; then
        echo "[SUCCESS] NVIDIA GPU가 감지되었습니다. CUDA 버전을 확인합니다."
        if ! python3 -c "import torch; torch.cuda.is_available()" 2>/dev/null; then
            echo "[INFO] CUDA PyTorch가 설치되지 않았습니다. 설치 중..."
            pip uninstall -y torch torchvision torchaudio
            pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
        else
            echo "[INFO] CUDA PyTorch가 이미 설치되어 있습니다."
        fi
        echo "[SUCCESS] PyTorch CUDA 버전이 설치되었습니다."
        
        # xformers 설치 (메모리 최적화)
        echo "[INFO] xformers 설치 중 (메모리 최적화)..."
        pip install xformers --index-url https://download.pytorch.org/whl/cu121
        if [ $? -ne 0 ]; then
            echo "[WARNING] xformers 설치에 실패했습니다. 계속 진행합니다."
        else
            echo "[SUCCESS] xformers가 설치되었습니다."
        fi
    else
        echo "[INFO] NVIDIA GPU가 감지되지 않았습니다. CPU 버전을 확인합니다."
        if ! python3 -c "import torch" 2>/dev/null; then
            echo "[INFO] CPU PyTorch가 설치되지 않았습니다. 설치 중..."
            pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
        else
            echo "[INFO] CPU PyTorch가 이미 설치되어 있습니다."
        fi
        echo "[SUCCESS] PyTorch CPU 버전이 설치되었습니다."
    fi
fi

# GPU/MPS 감지 확인
echo "[INFO] PyTorch 가속 장치 확인 중..."
if [[ "$PLATFORM" == "Darwin" && "$ARCH" == "arm64" ]]; then
    python3 -c "import torch; print('MPS available:', torch.backends.mps.is_available()); print('MPS built:', torch.backends.mps.is_built())"
else
    python3 -c "import torch; print('CUDA available:', torch.cuda.is_available()); print('Device count:', torch.cuda.device_count() if torch.cuda.is_available() else 0)"
fi

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