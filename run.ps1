$ErrorActionPreference = 'Stop'

$repoRoot = $PSScriptRoot
$venvActivate = Join-Path $repoRoot '.venv\Scripts\Activate.ps1'
$configPath = Join-Path $repoRoot 'config.yaml'

if (-not (Test-Path $venvActivate)) {
  throw "Venv not found at $venvActivate. Create it with: python -m venv .venv"
}

Write-Host "[run] repoRoot = $repoRoot"
Write-Host "[run] venvActivate = $venvActivate"
Write-Host "[run] configPath = $configPath"
Write-Host "[run] args = $($args -join ' ')"

. $venvActivate

Write-Host "[run] python = $(Get-Command python | Select-Object -ExpandProperty Source)"
Write-Host "[run] python -V = $(python -V)"
Write-Host "[run] starting watcher..."

# Run watcher with config.yaml; support subcommands like "panel" or "roi".
if ($args.Count -gt 0 -and ($args[0] -eq "panel" -or $args[0] -eq "roi")) {
  $command = $args[0]
  $rest = @()
  if ($args.Count -gt 1) { $rest = $args[1..($args.Count - 1)] }
  python -m watcher $command --config $configPath @rest
} else {
  python -m watcher --config $configPath @args
}
