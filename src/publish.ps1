# Pulls, builds, checks, commits and pushes rivanstudio.com, then tells IndexNow (Bing, Yandex, etc.) the pages changed.
# Source of truth: this src/ folder inside the site repo (template.html, i18n-no.json, head.json, faq.json).
# Pushes use the website-only deploy key (C:\Users\aksel\.ssh\rivanstudio_deploy), so GitHub CLI can stay logged out.
# Usage: .\src\publish.ps1 "Commit message"
param([Parameter(Mandatory = $true)][string]$Message)
# No $ErrorActionPreference = "Stop": in Windows PowerShell 5.1 it turns git's harmless stderr warnings into errors.
$git = "D:\AI\VeraLocal\tools\mingit\cmd\git.exe"
$site = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$key = "707c13c4360b6365d0b25884be957ed8"

# Pull first, so a merged branch that changed src/ is what gets built.
& $git -C $site pull -q origin main
if ($LASTEXITCODE -ne 0) { throw "pull failed" }
wsl.exe -e bash -lc "cd '/mnt/c/Users/aksel/OneDrive/Documents/ChatGPT/rivanstudio-site' && python3 src/build.py && python3 src/check.py"
if ($LASTEXITCODE -ne 0) { throw "build or check failed" }

& $git -C $site add -A
& $git -C $site diff --cached --quiet
if ($LASTEXITCODE -eq 0) { "Nothing to publish."; exit 0 }
& $git -C $site commit -q -m $Message -m "Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>"
& $git -C $site push -q origin main
if ($LASTEXITCODE -ne 0) { throw "push failed" }
& $git -C $site log --oneline -1

Start-Sleep 60
$body = @{ host = "rivanstudio.com"; key = $key; keyLocation = "https://rivanstudio.com/$key.txt";
           urlList = @("https://rivanstudio.com/", "https://rivanstudio.com/no/") } | ConvertTo-Json
$r = Invoke-WebRequest -Uri "https://api.indexnow.org/indexnow" -Method Post -ContentType "application/json; charset=utf-8" -Body $body -UseBasicParsing
"IndexNow: $($r.StatusCode)"
