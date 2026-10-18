# Premiere collecte complete (a lancer une seule fois apres "init")
$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $root
$py = "$root\.runtime\python\python.exe"
& $py -X utf8 -c "from aionhdv.db import connect; from aionhdv.catalog import check_names; print('noms', check_names(connect()))"
foreach ($c in 'snapshot', 'servers', 'refvolume', 'activity', 'backfill', 'icons', 'analyze') {
    & $py -X utf8 -m aionhdv $c
}
