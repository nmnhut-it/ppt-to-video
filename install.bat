@echo off
echo ==========================================
echo   PPT to Video - Setup
echo ==========================================
echo.

:: Check Python
echo [1/4] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo  X  Python not found. Please install from https://www.python.org/downloads/
    echo     Make sure to check "Add to PATH" during installation.
    pause
    exit /b 1
)
for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do echo  OK Python %%v

:: Check FFmpeg
echo.
echo [2/4] Checking FFmpeg...
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo  !  FFmpeg not found. Installing via winget...
    winget install Gyan.FFmpeg --accept-package-agreements --accept-source-agreements
    if errorlevel 1 (
        echo  X  FFmpeg install failed. Please install manually from https://ffmpeg.org/download.html
        pause
        exit /b 1
    )
    echo  OK FFmpeg installed. You may need to restart your terminal for it to work.
) else (
    echo  OK FFmpeg found
)

:: Install Python packages
echo.
echo [3/4] Installing Python packages...
pip install -r requirements.txt fastapi uvicorn python-multipart python-dotenv comtypes
if errorlevel 1 (
    echo  X  Package install failed. Check the error above.
    pause
    exit /b 1
)
echo  OK Packages installed

:: Setup .env
echo.
echo [4/4] Setting up configuration...
if not exist .env (
    if exist .env.example (
        copy .env.example .env >nul
        echo  !  Created .env file. Please edit it and add your Gemini API key.
        echo     Open .env with Notepad and replace "your-gemini-api-key" with your key.
        echo     Get a free key at: https://aistudio.google.com/apikey
    )
) else (
    echo  OK .env already exists
)

echo.
echo ==========================================
echo   Setup complete!
echo ==========================================
echo.
echo   To start the app, run:
echo     start.bat
echo.
echo   Or manually:
echo     python -m uvicorn app:app --port 8765
echo.
echo   Then open http://localhost:8765
echo.
pause
