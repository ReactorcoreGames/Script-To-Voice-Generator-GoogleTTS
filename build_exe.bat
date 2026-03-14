@echo off
echo ============================================
echo Script to Voice Generator
echo Building EXE with PyInstaller
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

echo Installing/Upgrading PyInstaller...
pip install --upgrade pyinstaller
echo.

echo Installing required dependencies...
pip install -r requirements.txt
echo.

echo Building executable...
pyinstaller --onefile --windowed ^
    --name "ScriptToVoiceGenerator" ^
    --icon=script_to_voice.ico ^
    --hidden-import=config ^
    --hidden-import=config_manager ^
    --hidden-import=character_profiles ^
    --hidden-import=data_models ^
    --hidden-import=script_parser ^
    --hidden-import=audio_generator ^
    --hidden-import=audio_merger ^
    --hidden-import=file_manager ^
    --hidden-import=gui ^
    --hidden-import=gui_theme ^
    --hidden-import=gui_tab1 ^
    --hidden-import=gui_tab2 ^
    --hidden-import=gui_tab2_state ^
    --hidden-import=gui_tab3 ^
    --hidden-import=gui_tab4 ^
    --hidden-import=gui_handlers ^
    --hidden-import=gui_generation ^
    --hidden-import=reference_writer ^
    app.py

if %errorlevel% neq 0 (
    echo.
    echo ============================================
    echo BUILD FAILED!
    echo ============================================
    echo Please check the error messages above.
    echo.
    pause
    exit /b 1
)

echo.
echo Build succeeded. Assembling release package...
echo.

REM Create fresh RELEASE folder
if exist RELEASE rmdir /S /Q RELEASE
mkdir RELEASE

REM Copy the compiled executable
echo Copying executable...
copy "dist\ScriptToVoiceGenerator.exe" "RELEASE\ScriptToVoiceGenerator.exe"

REM Copy the icon (required for window/taskbar icon at runtime)
echo Copying icon...
copy "script_to_voice.ico" "RELEASE\script_to_voice.ico"

REM Copy documentation files
echo Copying README.md...
copy "README.md" "RELEASE\README.md"

echo Copying promo.md...
copy "promo.md" "RELEASE\promo.md"

REM Copy !docs folder tree
echo Copying !docs folder...
xcopy /E /I /Y "!docs" "RELEASE\!docs"

echo.
echo ============================================
echo BUILD SUCCESSFUL!
echo ============================================
echo.
echo Release package created in: RELEASE\
echo.
echo   ScriptToVoiceGenerator.exe
echo   script_to_voice.ico
echo   README.md
echo   promo.md
echo   !docs\  (guides, example scripts, prompt templates)
echo.
echo NOTE: Users need FFMPEG on their system PATH for:
echo   - Audio effects (Radio, Reverb, Distortion, etc.)
echo   - Merged audio output
echo   - Volume normalization
echo Get it here: https://reactorcore.itch.io/ffmpeg-to-path-installer
echo.
echo NOTE: Users need a Google Cloud service account JSON key for TTS.
echo   Set the credentials path in Tab 4 (Settings) on first launch.
echo.

pause
