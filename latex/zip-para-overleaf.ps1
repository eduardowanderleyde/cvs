# Gera cv-overleaf.zip na pasta pai (Downloads/cvs/cvs/)
$latexDir = $PSScriptRoot
$zipPath = Join-Path (Split-Path $latexDir -Parent) "cv-overleaf.zip"

if (Test-Path $zipPath) { Remove-Item $zipPath -Force }

Compress-Archive -Path (Join-Path $latexDir "*") -DestinationPath $zipPath -Force
Write-Host "[ok] Zip criado: $zipPath"
Write-Host "     Suba este arquivo no Overleaf (Upload Project)."
