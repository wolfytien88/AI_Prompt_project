# 實作 B 講師資料

- `ref/`：參考答案，複製到 `make_repo.sh` 建出的專案根目錄（含隱藏資料夾 `.claude/`、`.agents/`）。
- 練習專案的未提交修改刻意包含兩個風險：`with_tax` 的負數檢查被刪、`API_KEY = "sk-test-FAKE-0000"`（虛構）。

巡迴重點：
- Skill 沒有任何輸出時，先檢查 `` !`指令` `` 能否在終端機單獨執行；含 `$(...)` 的指令在驗證時會讓 Skill 靜默失敗。
- 第 5 步沒加 `--allowedTools "Skill(diff-risk)"` 時，Skill 呼叫會出現在 `permission_denials`，模型改成自己執行 git diff；正好用來說明非互動模式的權限預設。
- Codex 指令中的 `$changelog` 要用單引號。
- Windows 學員：
  - 用 `make_repo.ps1` 建專案。在 PowerShell 打 `bash` 通常會進 WSL。
  - 在 Git Bash 跑 `claude -p "/changelog …"` 沒反應、寫檔被拒時，先檢查有沒有 `export MSYS_NO_PATHCONV=1`，因為 Git Bash 會把 `/changelog` 改寫成 `C:/Program Files/Git/changelog`。
  - 複製參考答案用 `Copy-Item -Recurse -Force instructor\ref\* <專案>\`，再用 `Get-ChildItem -Force` 確認 `.claude`、`.agents` 都在。
