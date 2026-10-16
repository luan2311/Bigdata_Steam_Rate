# Wrapper for TV2 batch steps on Windows local mode.
# Usage: .\scripts\run_tv2.ps1 etl --source data\sample\smoke.csv --level smoke
#        .\scripts\run_tv2.ps1 ml-prepare --run-id <run>
# Input/output and exit codes: see docs/runbooks/tv2_local_pipeline.md
$root = Split-Path -Parent $PSScriptRoot
if (-not $env:HADOOP_HOME) { $env:HADOOP_HOME = [Environment]::GetEnvironmentVariable("HADOOP_HOME", "User") }
$env:PYTHONPATH = Join-Path $root "src"
$env:PYTHONIOENCODING = "utf-8"
$pythonExe = Join-Path $root ".venv\Scripts\python.exe"
if (Test-Path $pythonExe) {
    & $pythonExe -m steam_reviews.presentation.cli.main @args
} else {
    py -3.13 -m steam_reviews.presentation.cli.main @args
}
exit $LASTEXITCODE
