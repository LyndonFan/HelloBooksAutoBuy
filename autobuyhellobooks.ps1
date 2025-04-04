$alwaysOn = (powercfg /list | Select-String -Pattern "GUID:.+[0-9a-f\-]+.+\(AlwaysOn\)").Matches[0].Value -replace ".*GUID: " -replace " +\(.*"
$balanced = (powercfg /list | Select-String -Pattern "GUID:.+[0-9a-f\-]+.+\(Balanced\)").Matches[0].Value -replace ".*GUID: " -replace " +\(.*"
Write-Host "Switching power plan to AlwaysOn: $alwaysOn"
powercfg /setactive $alwaysOn
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir
uv run python main.py
Write-Host "Switching power plan to Balanced: $balanced"
powercfg /setactive $balanced
