@echo off
title TEMU Claude
color 0C
setlocal

rem ---- settings you can edit ------------------------------------------
rem Model: claude-opus-5-5 (best), claude-sonnet-5-5 (half price), claude-haiku-5-5 (cheapest)
if "%MODEL%"=="" set "MODEL=claude-opus-5-5"
rem Loop mode: minutes between wake-ups, and the spend cap in dollars
set "LOOP_MINUTES=5"
set "MAX_USD=10"
rem The API key is NOT in this file. It goes in API-KEY-GOES-HERE.txt next to it.
rem ----------------------------------------------------------------------

rem ---- first start: install whatever is missing -------------------------
set "INSTALLED="
call :need uv astral-sh.uv "uv (runs the script and fetches Python for it)"
if not "%CHAT%"=="1" (
  call :need git Git.Git "Git"
  call :need gh GitHub.cli "GitHub CLI"
  call :need python Python.Python.3.13 "Python (used by the agent chat tool)"
)
if defined INSTALLED (
  echo.
  echo Setup installed new programs. Close this window and start again so they are found.
  pause
  exit /b
)

rem ---- API key ------------------------------------------------------------
set "KEYFILE=%~dp0API-KEY-GOES-HERE.txt"
if not exist "%KEYFILE%" (
  >"%KEYFILE%" echo Paste your Anthropic API key on the line below ^(it starts with sk-ant-^), save, close.
)
if "%ANTHROPIC_API_KEY%"=="" (
  findstr /b /c:"sk-ant-" "%KEYFILE%" >nul 2>nul
  if errorlevel 1 (
    echo.
    echo No API key yet. Notepad is opening API-KEY-GOES-HERE.txt:
    echo paste your key on its own line, save, close Notepad, then start again.
    start "" notepad "%KEYFILE%"
    pause
    exit /b
  )
)

rem "TEMU Claude Chat.bat" calls this file with CHAT=1: plain chat, no folder, no tools.
if "%CHAT%"=="1" (
  title TEMU Claude Chat
  cd /d "%~dp0"
  chcp 65001 >nul
  uv run "%~dp0temu_claude.py" --model %MODEL% --chat
  echo.
  pause
  exit /b
)

rem ---- GitHub login (agent only) -----------------------------------------
gh auth status >nul 2>nul
if errorlevel 1 (
  echo.
  echo GitHub is not logged in on this PC. Starting the login now:
  gh auth login
)

set "PROJ=%~1"
if "%PROJ%"=="" (
  echo Which folder should Claude work in?
  echo Drag a folder into this window, or just press Enter to use the "workspace" folder next to this file.
  set /p "PROJ=Folder: "
)
if "%PROJ%"=="" set "PROJ=%~dp0workspace"
set "PROJ=%PROJ:"=%"
if "%PROJ%"=="%~dp0workspace" if not exist "%PROJ%\" mkdir "%PROJ%"
if not exist "%PROJ%\" (
  echo.
  echo That folder does not exist: %PROJ%
  pause
  exit /b 1
)

echo.
echo Keep working unattended? It wakes every %LOOP_MINUTES% min to check the agent chat, up to $%MAX_USD%.
set "ANS="
set /p "ANS=Loop mode [y/N]: "
set "LOOP="
if /i "%ANS%"=="y" set "LOOP=--loop %LOOP_MINUTES% --max-usd %MAX_USD%"

cd /d "%PROJ%"
echo.
rem chcp must stay after the questions above: before them it breaks scripted answers.
chcp 65001 >nul
uv run "%~dp0temu_claude.py" --model %MODEL% --yolo %LOOP%
echo.
pause
exit /b

rem ---- :need <command> <winget id> <description> -------------------------
:need
%1 --version >nul 2>nul
if not errorlevel 1 exit /b 0
echo.
echo Missing: %~3. Installing it now...
winget --version >nul 2>nul
if errorlevel 1 (
  echo   Cannot install automatically: winget is not available on this PC.
  echo   Install "%~3" by hand, then start again.
  pause
  exit
)
winget install --id %2 -e --accept-source-agreements --accept-package-agreements
if not %errorlevel%==0 (
  echo   Installing %~3 failed. Install it by hand, then start again.
  pause
  exit
)
set "INSTALLED=1"
exit /b 0
