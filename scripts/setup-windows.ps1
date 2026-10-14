[CmdletBinding()]
param(
    [string]$Destination = 'F:\AiProjects\dealer-stock-enquiry-tracker',
    [switch]$InstallMissingTools
)
$ErrorActionPreference = 'Stop'
$Commit = '820dfd95b3e4b63567b1f4a351d1c2a2115057ac'

function Run-Checked {
    param([string]$Command, [string[]]$Arguments)
    & $Command @Arguments
    if ($LASTEXITCODE -ne 0) { throw "$Command failed (exit $LASTEXITCODE). Setup stopped." }
}
function Refresh-Path {
    $env:Path = [Environment]::GetEnvironmentVariable('Path','Machine') + ';' + [Environment]::GetEnvironmentVariable('Path','User')
}
function Install-Tool {
    param([string]$Id)
    if (-not $InstallMissingTools) { throw "Missing tool. Install with: winget install --id $Id --exact --source winget; reopen PowerShell and rerun. Or rerun this script with -InstallMissingTools." }
    if (-not (Get-Command winget -ErrorAction SilentlyContinue)) { throw 'Windows App Installer/winget is required to install missing tools. Install Python 3.12+ and Node 22.12+ from their official websites, then rerun.' }
    # Any installer or agreement prompts are left for the user.
    Run-Checked 'winget' @('install','--id',$Id,'--exact','--source','winget')
    Refresh-Path
}
function Find-Python {
    if (Get-Command py -ErrorAction SilentlyContinue) {
        & py -3.12 -c 'import sys; assert sys.version_info >= (3,12)' 2>$null
        if ($LASTEXITCODE -eq 0) { return @{Command='py'; Prefix=@('-3.12')} }
    }
    if (Get-Command python -ErrorAction SilentlyContinue) {
        & python -c 'import sys; assert sys.version_info >= (3,12)' 2>$null
        if ($LASTEXITCODE -eq 0) { return @{Command='python'; Prefix=@()} }
    }
    return $null
}

if (Test-Path $Destination) { throw "Folder already exists: $Destination. No files overwritten. Choose another -Destination or rename the existing folder." }
$DriveRoot = [IO.Path]::GetPathRoot($Destination)
if (-not (Test-Path $DriveRoot)) { throw "Drive is not available: $DriveRoot" }
$Python = Find-Python
if (-not $Python) { Install-Tool 'Python.Python.3.12'; $Python = Find-Python }
if (-not $Python) { throw 'Python is still unavailable. Reopen PowerShell and rerun.' }
if (-not (Get-Command node -ErrorAction SilentlyContinue)) { Install-Tool 'OpenJS.NodeJS.LTS' }
if (-not (Get-Command node -ErrorAction SilentlyContinue)) { throw 'Reopen PowerShell so Node is on PATH, then rerun.' }
Run-Checked 'node' @('-e','const [a,b]=process.versions.node.split(".").map(Number); if(a<22 || (a===22 && b<12))process.exit(1)')
$Npm = (Get-Command npm.cmd -ErrorAction Stop).Source
$Parent = Split-Path -Parent $Destination
New-Item -ItemType Directory -Path $Parent -Force | Out-Null
$Scratch = Join-Path $Parent ('dealer-download-' + [Guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $Scratch | Out-Null
$Archive = Join-Path $Scratch 'source.zip'
Write-Host "Downloading project snapshot $Commit ..."
Invoke-WebRequest -Uri "https://github.com/mohanoor-ai/dealer-stock-enquiry-tracker/archive/$Commit.zip" -OutFile $Archive -UseBasicParsing
Expand-Archive -Path $Archive -DestinationPath $Scratch
$Source = Get-ChildItem -Path $Scratch -Directory | Where-Object { Test-Path (Join-Path $_.FullName 'pyproject.toml') } | Select-Object -First 1
if (-not $Source) { throw 'Downloaded archive did not contain the expected project.' }
Move-Item -Path $Source.FullName -Destination $Destination
Push-Location $Destination
try {
    Start-Transcript -Path 'windows-setup-results.txt' | Out-Null
    Write-Host 'Installing bootstrap uv in an isolated environment ...'
    $Args = @($Python.Prefix) + @('-m','venv','.bootstrap-tools')
    Run-Checked $Python.Command $Args
    $BootstrapPython = Join-Path $Destination '.bootstrap-tools\Scripts\python.exe'
    Run-Checked $BootstrapPython @('-m','pip','install','uv')
    $Uv = Join-Path $Destination '.bootstrap-tools\Scripts\uv.exe'
    Run-Checked $Uv @('sync','--locked')
    Run-Checked $Uv @('run','python','-m','pytest','-q')
    Run-Checked $Uv @('run','python','scripts/check_v2_database.py')
    Push-Location 'frontend-v2'
    try {
        Run-Checked $Npm @('ci')
        Run-Checked $Npm @('run','build')
        Run-Checked $Npm @('test')
    } finally { Pop-Location }
    @"
Source commit: $Commit
Project: $Destination
Result: required setup checks passed on this machine.
Prototype: React UI with temporary fictional data.
Storage: SQLAlchemy/Alembic foundation; v2 HTTP routes not connected yet.
Not checked: full browser journey, Docker/Postgres, deployment or live LLM.
"@ | Set-Content -Path 'WINDOWS_SETUP_STATUS.txt'
    Write-Host "Setup checks passed. Project folder: $Destination"
    Write-Host 'Start the React prototype:'
    Write-Host "  cd '$Destination\frontend-v2'"
    Write-Host '  npm.cmd run dev'
    Write-Host 'Open the local address Vite prints. Stop with Ctrl+C.'
    Write-Host 'Baseline server: .\.bootstrap-tools\Scripts\uv.exe run python start.py'
    Write-Host 'New frontend and v2 storage are not connected yet. No Docker, model or paid cloud service was installed.'
} finally {
    try { Stop-Transcript | Out-Null } catch { }
    Pop-Location
}
