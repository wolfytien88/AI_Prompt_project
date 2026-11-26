# 建立給 weekly-report Skill 練習用的範例 Repo：近 7 天內 8 筆不同類型的 commit，
# 並把 SKILL.md 放到 Claude Code 與 Codex 各自讀取的位置。
# make_sample_repo.sh 的 Windows PowerShell 版本，不需要 Git Bash 或 WSL。
# 用法：powershell -ExecutionPolicy Bypass -File make_sample_repo.ps1 [目標資料夾，預設 .\weekly-demo]
param([string]$Target = ".\weekly-demo")
$ErrorActionPreference = "Stop"

$Here = $PSScriptRoot
if (Test-Path $Target) {
    Write-Host "錯誤：$Target 已存在，請換一個資料夾名稱或先自行移除"
    exit 1
}
New-Item -ItemType Directory -Path $Target | Out-Null
$Target = (Resolve-Path $Target).Path
Set-Location $Target

$utf8 = New-Object System.Text.UTF8Encoding($false)
function Invoke-Git {
    & git @args
    if ($LASTEXITCODE -ne 0) { throw "git $args 失敗" }
}

Invoke-Git init -q -b main
Invoke-Git config user.name "課程範例"
Invoke-Git config user.email "demo@example.com"
Invoke-Git config core.autocrlf false

function Add-Commit([int]$Days, [string]$Msg, [string]$File) {
    $path = Join-Path $Target $File
    New-Item -ItemType Directory -Force -Path (Split-Path $path) | Out-Null
    [System.IO.File]::AppendAllText($path, "$Msg`n", $utf8)   # 同 bash 的 echo >>：UTF-8、LF
    Invoke-Git add -A
    $when = (Get-Date).AddDays(-$Days).ToString("yyyy-MM-ddTHH:mm:ss")
    $env:GIT_AUTHOR_DATE = $when; $env:GIT_COMMITTER_DATE = $when
    try { Invoke-Git commit -qm $Msg }
    finally { Remove-Item Env:GIT_AUTHOR_DATE, Env:GIT_COMMITTER_DATE }
}

Add-Commit 6 "feat: 新增會員登入頁" "src/login.py"
Add-Commit 5 "fix: 修正購物車金額未乘數量" "src/cart.py"
Add-Commit 5 "docs: 更新 README 安裝步驟" "README.md"
Add-Commit 4 "feat: 訂單列表支援匯出 CSV" "src/orders.py"
Add-Commit 3 "fix: 滿額免運邊界條件錯誤" "src/cart.py"
Add-Commit 2 "feat: 新增商品搜尋關鍵字建議" "src/search.py"
Add-Commit 1 "docs: 補上 API 錯誤碼說明" "docs/api.md"
Add-Commit 0 "fix: 登入失敗訊息顯示亂碼" "src/login.py"

foreach ($dir in ".claude\skills\weekly-report", ".agents\skills\weekly-report") {
    New-Item -ItemType Directory -Force -Path $dir | Out-Null
    Copy-Item (Join-Path $Here "skills\weekly-report\SKILL.md") (Join-Path $dir "SKILL.md")
}

Write-Host "已建立 $Target"
Write-Host "commit 數：$(git rev-list --count HEAD)"
Write-Host "Skill 位置：.claude\skills\weekly-report\  與  .agents\skills\weekly-report\"
