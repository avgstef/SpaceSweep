@echo off
setlocal
cd /d "%~dp0"
py -m pip install --upgrade pip
py -m pip install pyinstaller
py -m PyInstaller --noconfirm --clean --windowed --onefile --name SpaceSweep --icon spacesweep.ico --add-data "spacesweep.ico;." spacesweep.py
if errorlevel 1 (
  echo Build failed. Check the messages above.
  pause
  exit /b 1
)
echo.
echo Build complete: dist\SpaceSweep.exe
pause
