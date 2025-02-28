@echo off
echo ===== Starting YouTube Subtitle Extractor =====

echo Checking for virtual environment...

if not exist venv (
    echo Virtual environment not found. Running setup...
    call setup_env.bat
) else (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
    
    echo Installing/updating dependencies...
    pip install -r requirements.txt
)

echo ===== Starting Flask Application =====
echo.
echo IMPORTANT: If the application shows "whisper_available = False", it means Whisper was not initialized properly.
echo Check that all dependencies are correctly installed and the model can be downloaded.
echo.

echo Starting the application...
python app.py
