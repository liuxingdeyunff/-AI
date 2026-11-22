@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  py -3.12 -m venv .venv
  if errorlevel 1 goto :python_needed
)
".venv\Scripts\python.exe" launcher.py
if errorlevel 1 pause
exit /b
:python_needed
echo Install Python 3.12 with the Python Launcher for Windows, then run start.cmd again.
pause
exit /b 1
