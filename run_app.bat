@echo off
echo === Running Automated Course Content Generator ===
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Run Streamlit
echo Starting Streamlit app...
echo Open http://localhost:8501 in your browser
echo Press Ctrl+C to stop
echo.

streamlit run app.py

pause 