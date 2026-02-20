@echo off
@echo off
rem 调用 PowerShell 脚本以获得更可靠的启动行为（双击仍可工作）
rem 使用 Bypass 避免执行策略阻止脚本
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0start.ps1"
exit /b %ERRORLEVEL%
