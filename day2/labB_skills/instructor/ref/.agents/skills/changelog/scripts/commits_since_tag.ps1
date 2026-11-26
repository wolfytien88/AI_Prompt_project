# commits_since_tag.sh 的 Windows PowerShell 版本：輸出最新標籤，以及該標籤之後的 commit（一行一筆）
[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false)
$tag = git describe --tags --abbrev=0 2>$null
if ($LASTEXITCODE -ne 0 -or -not $tag) {
    Write-Output "沒有標籤"
    git log --oneline
    exit 0
}
Write-Output "最新標籤：$tag"
git log --oneline "$tag..HEAD"
