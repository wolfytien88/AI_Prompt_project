# 建立實作 B 的練習專案 invoice-tool（虛構）：有 v1.1.0 標籤、之後 5 筆 commit、一筆未提交的修改。
# make_repo.sh 的 Windows PowerShell 版本，不需要 Git Bash 或 WSL。
# 用法：powershell -ExecutionPolicy Bypass -File make_repo.ps1 [目的資料夾，預設 .\invoice-tool]
param([string]$Dest = ".\invoice-tool")
$ErrorActionPreference = "Stop"

if (Test-Path $Dest) { Write-Host "$Dest 已存在"; exit 1 }
New-Item -ItemType Directory -Path $Dest | Out-Null
$Dest = (Resolve-Path $Dest).Path
Set-Location $Dest

# 一律以 UTF-8（無 BOM）、LF 換行寫檔，內容與 make_repo.sh 產生的完全相同
$utf8 = New-Object System.Text.UTF8Encoding($false)
function Write-Lf([string]$Path, [string]$Text) {
    [System.IO.File]::WriteAllText((Join-Path $Dest $Path), ($Text -replace "`r`n", "`n"), $utf8)
}
function Read-Lf([string]$Path) {
    [System.IO.File]::ReadAllText((Join-Path $Dest $Path), $utf8)
}
function Invoke-Git {
    & git -c user.email=lab@example.com -c user.name=lab -c core.autocrlf=false @args
    if ($LASTEXITCODE -ne 0) { throw "git $args 失敗" }
}

Invoke-Git init -q -b main
Invoke-Git config core.autocrlf false

Write-Lf "invoice.py" @'
"""發票工具：計算含稅金額。"""
TAX_RATE = 0.05


def with_tax(amount):
    if amount < 0:
        raise ValueError("金額不可為負")
    return round(amount * (1 + TAX_RATE))

'@
Write-Lf "README.md" "# invoice-tool`n`n虛構的發票小工具。`n"
Write-Lf "CHANGELOG.md" "# 更新紀錄`n`n## v1.1.0（2026-09-15）`n- 第一個正式版本`n"
Invoke-Git add -A; Invoke-Git commit -qm "feat: 第一個正式版本"; Invoke-Git tag v1.1.0

Write-Lf "invoice.py" ((Read-Lf "invoice.py") + @'


def split_amount(total, n):
    """把總額平均分給 n 個人，餘數加在第一個人。"""
    base, rest = divmod(total, n)
    return [base + rest] + [base] * (n - 1)

'@)
Invoke-Git commit -qam "feat: 新增分攤金額 split_amount"

Write-Lf "invoice.py" ((Read-Lf "invoice.py").Replace("round(amount * (1 + TAX_RATE))", "int(amount * (1 + TAX_RATE) + 0.5)"))
Invoke-Git commit -qam "fix: 含稅金額改為四捨五入到整數，修正 0.5 進位錯誤"

Write-Lf "README.md" ((Read-Lf "README.md") + "`n## 使用方式`n`n``````python`nfrom invoice import with_tax`nwith_tax(100)  # 105`n```````n")
Invoke-Git commit -qam "docs: README 加上使用方式"

Write-Lf "test_invoice.py" @'
from invoice import with_tax, split_amount


def test_with_tax():
    assert with_tax(100) == 105


def test_split():
    assert split_amount(100, 3) == [34, 33, 33]

'@
Invoke-Git add -A; Invoke-Git commit -qm "test: 補上 with_tax 與 split_amount 測試"

Write-Lf "invoice.py" ((Read-Lf "invoice.py").Replace('"""把總額平均分給 n 個人，餘數加在第一個人。"""', '"""把總額平均分給 n 個人，餘數加在第一個人。n 必須大於 0。"""'))
Invoke-Git commit -qam "docs: split_amount 註明 n 的限制"

# 未提交的修改：拿掉負數檢查、寫死測試金鑰（供 diff-risk 找出風險）
$src = (Read-Lf "invoice.py").Replace("    if amount < 0:`n        raise ValueError(`"金額不可為負`")`n", "")
Write-Lf "invoice.py" ($src + "`nAPI_KEY = `"sk-test-FAKE-0000`"  # 暫時測試用`n")

Write-Host "已建立 $Dest：標籤 v1.1.0 之後有 5 筆 commit，另有未提交的修改"
