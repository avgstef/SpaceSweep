@echo off
cd /d "%~dp0"
py spacesweep.py
if errorlevel 1 pause
