@echo off
setlocal

echo ========================================
echo  Automated Course Content Generator
echo  Robust Installation and Run Script
echo ========================================

REM Activate venv or create if it doesn't exist
if not exist "venv" (
    echo [INFO] Creating virtual environment...
    python -m venv venv
)
call venv\Scripts\activate.bat

echo [INFO] Upgrading pip...
python -m pip install --upgrade pip

echo [INFO] Installing all dependencies from requirements_windows.txt...
pip install -r requirements_windows.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies from requirements_windows.txt.
    pause
    exit /b 1
)

REM Check for NVIDIA GPU to decide on PyTorch version
nvidia-smi >nul 2>&1
if errorlevel 1 (
    echo [INFO] No NVIDIA GPU detected. Installing PyTorch CPU version...
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
) else (
    echo [INFO] NVIDIA GPU detected. Installing PyTorch CUDA version...
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
)
if errorlevel 1 (
    echo [ERROR] PyTorch installation failed.
    echo Please try running fix_pytorch.bat or check your internet connection.
    pause
    exit /b 1
)


REM Crucial step: Uninstall xformers as it's incompatible with CPU mode and can cause issues.
echo [INFO] Ensuring xformers is uninstalled...
pip uninstall -y xformers >nul 2>&1


REM Final verification
echo [INFO] Verifying final installation...
python -c "import torch; import diffusers; import transformers; print('[SUCCESS] All major libraries are installed.')"
if errorlevel 1 (
    echo [ERROR] Verification failed. Some libraries are still missing or broken.
    pause
    exit /b 1
)

echo.
echo [SUCCESS] Installation and setup complete.
echo Starting the application...
echo.

call run_app.bat

endlocal
pause 