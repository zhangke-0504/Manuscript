# Safe cleaner for old build artifacts. Run in PowerShell as administrator.
param(
  [switch]$Force
)

$paths = @(
  "$PSScriptRoot\dist",
  "$PSScriptRoot\build_dist",
  "$PSScriptRoot\node_modules\app-builder-bin",
  "$PSScriptRoot\node_modules\electron",
  "$env:LOCALAPPDATA\electron-builder\Cache"
)

Write-Host "The following paths will be checked for removal:`n"
$paths | ForEach-Object { Write-Host " - $_" }

if (-not $Force) {
  Write-Host "`nPress Enter to list existing paths or Ctrl+C to cancel..."
  [void][System.Console]::ReadLine()
}

foreach ($p in $paths) {
  if (Test-Path $p) {
    Write-Host "Found: $p"
    try {
      Remove-Item -Recurse -Force -ErrorAction Stop $p
      Write-Host "Removed: $p"
    } catch {
      Write-Warning "Failed to remove $p : $_"
    }
  } else {
    Write-Host "Not found: $p"
  }
}

Write-Host "Cleanup complete."