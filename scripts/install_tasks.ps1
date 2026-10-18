# Cree les taches planifiees Windows (a lancer une fois, quand tu es d'accord) :
#   - AION-HDV-hourly : toutes les heures (prix de tout le marche, analyses, alertes, rapport)
#   - AION-HDV-daily  : chaque jour a 17h30 (volumes de reference publies a minuit heure coreenne, activite, resume Discord)
# Suppression : Unregister-ScheduledTask -TaskName AION-HDV-hourly,AION-HDV-daily -Confirm:$false
$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$ps = "powershell.exe"
$hourly = New-ScheduledTaskAction -Execute $ps -Argument "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$root\run.ps1`" hourly" -WorkingDirectory $root
$daily  = New-ScheduledTaskAction -Execute $ps -Argument "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$root\run.ps1`" daily" -WorkingDirectory $root
$tHourly = New-ScheduledTaskTrigger -Once -At (Get-Date).Date.AddMinutes(7) -RepetitionInterval (New-TimeSpan -Hours 1)
$tDaily  = New-ScheduledTaskTrigger -Daily -At 17:30
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -DontStopIfGoingOnBatteries -AllowStartIfOnBatteries -ExecutionTimeLimit (New-TimeSpan -Minutes 50) -MultipleInstances IgnoreNew
Register-ScheduledTask -TaskName "AION-HDV-hourly" -Action $hourly -Trigger $tHourly -Settings $settings -Description "Aion 2 HDV : collecte horaire" -Force | Out-Null
Register-ScheduledTask -TaskName "AION-HDV-daily" -Action $daily -Trigger $tDaily -Settings $settings -Description "Aion 2 HDV : collecte quotidienne" -Force | Out-Null
Get-ScheduledTask -TaskName "AION-HDV-*" | Select-Object TaskName, State
