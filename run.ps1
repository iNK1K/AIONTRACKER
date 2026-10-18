# Lance une commande de l'outil : .\run.ps1 hourly   (voir .\run.ps1 help)
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root
& "$root\.runtime\python\python.exe" -X utf8 -m aionhdv @args
exit $LASTEXITCODE
