@echo off
rem filepath: d:/my_projects/personal/Manuscript/start-app.bat
rem Launcher: will run packaged app if present; otherwise try to build then run.
setlocal

set "EXE="
set "ROOT=%~dp0"

rem check common locations for unpacked exe or installer
if exist "%ROOT%build_dist\win-unpacked\manuscript-desktop.exe" set "EXE=%ROOT%build_dist\win-unpacked\manuscript-desktop.exe"
if "%EXE%"=="" if exist "%ROOT%dist\win-unpacked\manuscript-desktop.exe" set "EXE=%ROOT%dist\win-unpacked\manuscript-desktop.exe"
if "%EXE%"=="" if exist "%ROOT%build_dist\manuscript-desktop Setup 1.0.0.exe" set "EXE=%ROOT%build_dist\manuscript-desktop Setup 1.0.0.exe"
if "%EXE%"=="" if exist "%ROOT%dist\manuscript-desktop Setup 1.0.0.exe" set "EXE=%ROOT%dist\manuscript-desktop Setup 1.0.0.exe"

if "%EXE%"=="" (
  echo No executable or installer found. Attempting to build distributables now (npm run dist)...
  echo Requirements: Node.js + npm, Python + pyinstaller; this may take several minutes.
  pushd "%ROOT%" >nul 2>&1 || (echo Failed to change to project root: %ROOT% & pause & exit /b 1)
  call npm run dist
  set "RC=%ERRORLEVEL%"
  popd >nul 2>&1
  if not "%RC%"=="0" (
    echo Build failed (exit %RC%). Check the console output above for errors.
    pause
    exit /b %RC%
  )

  rem re-check for exe after build
  if exist "%ROOT%build_dist\win-unpacked\manuscript-desktop.exe" set "EXE=%ROOT%build_dist\win-unpacked\manuscript-desktop.exe"
  if "%EXE%"=="" if exist "%ROOT%dist\win-unpacked\manuscript-desktop.exe" set "EXE=%ROOT%dist\win-unpacked\manuscript-desktop.exe"
  if "%EXE%"=="" if exist "%ROOT%build_dist\manuscript-desktop Setup 1.0.0.exe" set "EXE=%ROOT%build_dist\manuscript-desktop Setup 1.0.0.exe"
  if "%EXE%"=="" if exist "%ROOT%dist\manuscript-desktop Setup 1.0.0.exe" set "EXE=%ROOT%dist\manuscript-desktop Setup 1.0.0.exe"
)

if "%EXE%"=="" (
  echo No executable or installer found after build.
  echo Please ensure you have Node, npm, Python and pyinstaller installed, then run "npm run dist" manually.
  pause
  endlocal
  exit /b 1
)

echo Launching: %EXE%
start "" "%EXE%"
endlocal
