# filepath: d:\my_projects\personal\Manuscript\start.ps1
param(
    [int]$ApiPort = 8890,
    [int]$StaticPort = 5500
)

Add-Type -AssemblyName System.Windows.Forms
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$exePath = Join-Path $scriptDir 'backend\dist\server.exe'
$wwwDir = Join-Path $scriptDir 'backend\dist\www'
# log files reserved (not used when backend serves static files)

function Show-Error([string]$msg) {
    [System.Windows.Forms.MessageBox]::Show($msg, 'Start Error', [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Error) | Out-Null
}

if (-not (Test-Path $exePath)) {
    Show-Error ("Backend executable not found: {0}`nPlease build backend and place server.exe in backend\\dist." -f $exePath)
    exit 1
}

# Start backend
try {
    Start-Process -FilePath $exePath -WindowStyle Minimized
} catch {
    Show-Error ("Failed to start backend: {0}" -f $_.Exception.Message)
    exit 1
}

# No Python dependency required: backend now serves static files directly

# Wait for backend to serve static files on ApiPort
$ready = $false
for ($i = 0; $i -lt 15; $i++) {
    try {
        $r = Invoke-WebRequest -Uri ("http://127.0.0.1:$ApiPort/") -UseBasicParsing -TimeoutSec 2
        if ($r.StatusCode -eq 200) { $ready = $true; break }
    } catch {
        Start-Sleep -Seconds 1
    }
}

if ($ready) {
    Start-Process ("http://127.0.0.1:$ApiPort/")
} else {
    Show-Error ("Backend static site not available. Please check server logs.")
}
