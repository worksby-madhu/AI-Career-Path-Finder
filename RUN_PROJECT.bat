@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Creating virtual environment...
  py -m venv .venv
  if errorlevel 1 goto error
)
call ".venv\Scripts\activate.bat"
echo Installing/checking required packages...
python -m pip install -r requirements.txt
if errorlevel 1 goto error
python manage.py check
if errorlevel 1 goto error
python manage.py migrate
if errorlevel 1 goto error
echo Starting AI Career Path Finder at http://127.0.0.1:8000/
python manage.py runserver
 goto end
:error
echo.
echo Setup failed. Read the error above, then contact support or run the README steps manually.
pause
:end
endlocal
