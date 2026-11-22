$ErrorActionPreference = 'Stop'
$tools = @(Get-Command python,python3,py,node,npm,vite -ErrorAction SilentlyContinue)
if ($tools.Count) { throw "The clean image unexpectedly contains a developer runtime." }
Write-Output 'PASS clean Windows Server Core image contains no Python, Node.js, npm or Vite commands'
Expand-Archive C:\payload\ZhixuAI-Windows-x64.zip -DestinationPath C:\app
$exe = Get-ChildItem C:\app\ZhixuAI-Windows-x64 -Filter *.exe | Select-Object -First 1
$env:ZHIXU_ACCEPTANCE = '1'
$profileDir = Join-Path $env:LOCALAPPDATA 'ZhixuAI'
$p = Start-Process -FilePath $exe.FullName -PassThru
try {
    $record = Join-Path $profileDir 'instance.json'
    for ($i=0; $i -lt 180 -and !(Test-Path $record); $i++) {
        if ($p.HasExited) { throw "Portable process exited early: $($p.ExitCode)" }
        Start-Sleep -Seconds 1
    }
    $port = (Get-Content $record -Raw | ConvertFrom-Json).port
    $base = "http://127.0.0.1:$port"
    if ((Invoke-RestMethod "$base/api/units").Count -ne 10) { throw 'Course load failed' }
    $result = Invoke-RestMethod "$base/api/answer" -Method Post -ContentType 'application/json' -Body '{"q":"1-0","answer":"-1/6","mode":"quiz"}'
    if (!$result.ok) { throw 'Bundled symbolic grader failed' }
    Write-Output 'PASS extracted GUI executable serves lessons and grades exact result in a developer-tool-free OS image'
} finally {
    if (Test-Path $profileDir) { New-Item "$profileDir\stop-test" -ItemType File -Force | Out-Null }
    if (!$p.WaitForExit(30000)) { $p.Kill(); throw 'Application did not shut down' }
}
if ($p.ExitCode -ne 0) { throw "Portable process failed: $($p.ExitCode)" }

