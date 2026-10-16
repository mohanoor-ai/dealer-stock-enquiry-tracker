param([int]$Port=8090)
$ErrorActionPreference='Stop'
Set-Location (Join-Path $PSScriptRoot '..')
$TaskPython=Join-Path (Get-Location) '.venv/Scripts/python.exe'
if (-not (Test-Path -LiteralPath $TaskPython)) { throw 'First run: python -m venv .venv, then .venv\Scripts\python.exe -m pip install -r requirements.txt' }
& $TaskPython start.py --port $Port
if ($LASTEXITCODE -ne 0) { throw 'Application stopped with an error. Read the output above.' }
