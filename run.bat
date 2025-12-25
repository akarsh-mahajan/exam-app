@echo off
setlocal

REM Set the project root directory
set "PROJECT_ROOT=%~dp0"

REM --- Dependency Checks ---
echo Checking for dependencies...

echo Checking for python...
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo python is not found. Please install it and add it to your PATH.
    pause
    exit /b 1
)

echo Checking for node...
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo node is not found. Please install it and add it to your PATH.
    pause
    exit /b 1
)

echo Checking for npm...
where npm >nul 2>nul
if %errorlevel% neq 0 (
    echo npm is not found. Please install it and add it to your PATH.
    pause
    exit /b 1
)

echo All dependencies are found.


REM --- Backend Setup ---
echo Setting up the backend...

REM Create and activate virtual environment in project root
cd /d "%PROJECT_ROOT%"
if not exist test_env (
    echo Creating virtual environment 'test_env'...
    python -m venv test_env
)

echo Activating virtual environment...
call test_env\Scripts\activate.bat

@REM echo Upgrading pip...
@REM python -m pip install --upgrade pip

@REM echo Installing backend dependencies...
@REM pip install -r backend/requirements.txt


cd /d "%PROJECT_ROOT%backend"

@REM echo Running database migrations...
@REM python manage.py migrate

echo Starting Django server...
start "Backend" /B python manage.py runserver

REM --- Frontend Setup ---
echo Setting up the frontend...
cd /d "%PROJECT_ROOT%frontend"

@REM echo Installing frontend dependencies...
@REM npm install

echo Starting React server...
start "Frontend" /B npm start

echo.
echo Both servers are starting up.
echo The backend should be available at http://127.0.0.1:8000
echo The frontend should open automatically in your browser at http://localhost:3000
echo.
echo IMPORTANT: Close this window to stop both servers.
echo.

REM --- Wait for user to close ---
:wait_loop
timeout /t 5 >nul
REM Check if servers are still running by checking for the process names.
REM This is not foolproof but a decent heuristic.
tasklist /fi "IMAGENAME eq python.exe" /nh | find /i "python.exe" >nul
if %errorlevel% neq 0 (
    echo Backend server seems to have stopped.
    goto cleanup
)
tasklist /fi "IMAGENAME eq node.exe" /nh | find /i "node.exe" >nul
if %errorlevel% neq 0 (
    echo Frontend server seems to have stopped.
    goto cleanup
)
goto wait_loop

:cleanup
echo Shutting down servers...
REM Kill the processes started by this script.
taskkill /f /fi "WINDOWTITLE eq Backend" /t >nul
taskkill /f /fi "WINDOWTITLE eq Frontend" /t >nul
call test_env\Scripts\activate

echo Servers stopped.
endlocal
