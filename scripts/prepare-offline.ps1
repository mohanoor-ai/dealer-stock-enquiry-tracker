$ErrorActionPreference='Stop'
Set-Location (Join-Path $PSScriptRoot '..')
New-Item -ItemType Directory -Force 'offline-wheels' | Out-Null
python -m pip download -r requirements.txt --dest offline-wheels
if ($LASTEXITCODE -ne 0) { throw 'Dependency preparation failed.' }
npm.cmd ci --prefix frontend-v2
if ($LASTEXITCODE -ne 0) { throw 'Frontend dependency preparation failed.' }
npm.cmd run build --prefix frontend-v2
if ($LASTEXITCODE -ne 0) { throw 'Frontend build failed.' }
Write-Output 'Offline assets prepared for this Python/OS architecture. Install using pip --no-index --find-links offline-wheels -r requirements.txt. No Python runtime or AI model is bundled.'
