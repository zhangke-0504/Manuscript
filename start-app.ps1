#!/usr/bin/env pwsh
# filepath: d:/my_projects/personal/Manuscript/start-app.ps1
# Simple launcher to run the unpacked app or installer (Windows PowerShell)
$paths = @(
  "$PSScriptRoot\build_dist\win-unpacked\manuscript-desktop.exe",
  "$PSScriptRoot\dist\win-unpacked\manuscript-desktop.exe",
  "$PSScriptRoot\build_dist\manuscript-desktop Setup 1.0.0.exe",
  "$PSScriptRoot\dist\manuscript-desktop Setup 1.0.0.exe"
)

$exe = $paths | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $exe) {
  Write-Host "No application executable or installer found."
  Write-Host "Please run `npm run dist` in the project root to build the app."
  Write-Host "Press Enter to exit..."
  [void][System.Console]::ReadLine()
  exit 1
}

Write-Host "Launching:`n  $exe`n"
Start-Process -FilePath $exe
