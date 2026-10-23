# Lance une commande de l'outil : .\run.ps1 hourly   (voir .\run.ps1 help)
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root
# journal des ventes : le site l'enregistre sur la branche journal (sans effet hors ligne)
git fetch -q origin journal 2>$null; if ($LASTEXITCODE -eq 0) { git show FETCH_HEAD:journal.json | Set-Content -Encoding utf8 journal.json }
& "$root\.runtime\python\python.exe" -X utf8 -m aionhdv @args
exit $LASTEXITCODE
