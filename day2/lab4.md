# 實作 4：一個 Skill 裝進兩套 Harness，加上 edit 工具，再做拆除實驗

> 在 VS Code 中操作本實作的方式，見 [`../vscode.md`](../vscode.md)。

## 目的

- 驗證同一份 `SKILL.md` 可以同時被 Claude Code 與 Codex 載入使用。
- 替自己的 Agent 加上宣告式的 `read_file` / `edit_file` 工具，體會「有型別的工具才能把關」。
- 用拆除實驗找出哪些元件真正必要（詳見 `ablation.md`）。

## 前置

| 項目 | 指令或說明 |
| --- | --- |
| Claude Code | `claude --version` |
| Codex CLI | `codex --version`（需可使用 Codex 的 ChatGPT 帳號或 OpenAI API Key） |
| git | `git --version` |
| 套件 | `pip install anthropic pytest` |
| 本資料夾的檔案 | `skills/weekly-report/SKILL.md`、`make_sample_repo.sh`（Windows 用 `make_sample_repo.ps1`）、`edit_tool.py`、`test_edit_tool.py`、`mini_agent_edit.py`、`test_mini_agent_edit.py` |

### Windows 注意事項

Windows 請全程使用 **PowerShell**，並在 `day2` 資料夾開啟終端機。每個步驟都附有 PowerShell 版指令。

| 問題 | 原因與做法 |
| --- | --- |
| `python3` 出現 “Python was not found” | Windows 的 `python3` 通常是 Microsoft Store 的空殼。一律改用 `python`（或 `py`）。 |
| 在 PowerShell 執行 `bash make_sample_repo.sh` 失敗或跑到 WSL | PowerShell 的 `bash` 通常是 WSL，不是 Git Bash。改用 `make_sample_repo.ps1`。 |
| `rm -rf`、`export`、結尾的 `&` 無法使用 | 這些是 bash 語法，下面的 PowerShell 版指令分別改用 `Remove-Item -Recurse -Force`、`$env:變數 = "值"`、`Start-Process`。 |
| Agent 的 bash 工具其實是 cmd.exe | `mini_agent_edit.py` 在 Windows 以 `cmd.exe` 執行指令，並已在工具描述中提醒模型用 `dir`、`type`、`python`；子程序輸出以 UTF-8 解讀，避免 cp950 解碼錯誤。 |
| 終端機中文亂碼 | 先執行 `chcp 65001`。只影響顯示，不影響檔案內容。 |

## Part A：一個 Skill，兩套 Harness

### A1. 建立範例 Repo

```bash
bash make_sample_repo.sh ~/weekly-demo
cd ~/weekly-demo
git log --oneline
```

Windows（PowerShell）：

```powershell
powershell -ExecutionPolicy Bypass -File make_sample_repo.ps1 $HOME\weekly-demo
cd $HOME\weekly-demo
git log --oneline
Get-ChildItem -Force -Recurse .claude, .agents -Name   # 確認兩個 SKILL.md 都在（以 . 開頭的資料夾預設隱藏）
```

腳本會建立近 7 天內 8 筆 commit（feat、fix、docs 各數筆），並把 `SKILL.md` 放到兩個位置：

| 工具 | 位置 |
| --- | --- |
| Claude Code | `.claude/skills/weekly-report/SKILL.md` |
| Codex | `.agents/skills/weekly-report/SKILL.md` |

目標資料夾已存在時，腳本會停止並提示，不會覆蓋。

### A2. 在 Claude Code 中觸發 Skill

```bash
cd ~/weekly-demo        # Windows：cd $HOME\weekly-demo
claude
```

輸入：`幫我寫本週週報`

預期：Claude Code 呼叫 `weekly-report` Skill，執行 `git log --since="7 days ago" --oneline`，並寫出 `reports/weekly-YYYY-MM-DD.md`，內容依「新功能 / 修正 / 文件」分類。Windows 上 Claude Code 通常會用 PowerShell 工具執行這行 `git log`，結果相同。

### A3. 在 Codex 中觸發同一個 Skill

先把 Claude Code 產生的週報改名，避免混淆：

```bash
mv reports reports_claude
codex
```

Windows（PowerShell）：`Rename-Item reports reports_claude`，再執行 `codex`。Codex 在 Windows 以 PowerShell 執行 Skill 裡的 `git log --since="7 days ago" --oneline`，這行指令在 PowerShell 也能直接執行。

輸入：`幫我寫本週週報`

### A4. 比較兩邊的結果

| 比較項目 | Claude Code | Codex |
| --- | --- | --- |
| 有沒有觸發 weekly-report Skill | | |
| 執行了哪些指令 | | |
| 輸出檔名與位置 | | |
| 分類是否正確（3 新功能、3 修正、2 文件） | | |
| 其他差異 | | |

## Part B：替 Agent 加上含過期檢查的 edit 工具

### B1. 先跑 edit_tool 的測試

```bash
python3 -m pytest -q test_edit_tool.py     # Windows：python -m pytest -q test_edit_tool.py
```

預期：`6 passed`。六個測試涵蓋：未讀先改被拒、讀後修改成功、自己改完可連續修改、外部修改後被拒（且檔案沒被覆蓋）、old 不唯一被拒、old 不存在被拒。

### B2. 把工具接進 Agent

對照 `mini_agent_edit.py`，在你的 `mini_agent.py` 中：

1. 新增 `read_file` 與 `edit_file` 兩個工具定義。
2. 寫一個 `run_tool(name, args)` 依名稱分派，並把例外轉成錯誤文字回給模型。
3. 在 bash 工具的 description 中說明「修改檔案請用 edit_file」。

分派邏輯的測試（不呼叫模型）：

```bash
python3 -m pytest -q test_mini_agent_edit.py     # Windows：python -m pytest -q test_mini_agent_edit.py
```

Windows：`bash` 工具實際上由 `cmd.exe` 執行。對照 `mini_agent_edit.py`，`subprocess.run` 要加上 `encoding="utf-8", errors="replace"`，否則 pytest 或 git 輸出中文時會出現 `UnicodeDecodeError: 'cp950' codec can't decode…`。

預期：`5 passed`。

### B3. 用新版 Agent 修 buggy_shop

```bash
rm -rf shop_work && cp -r buggy_shop shop_work && cd shop_work
python3 ../mini_agent_edit.py
python3 -m pytest -q
```

Windows（PowerShell）：

```powershell
Remove-Item -Recurse -Force shop_work -ErrorAction SilentlyContinue; Copy-Item -Recurse buggy_shop shop_work; cd shop_work
python ..\mini_agent_edit.py
python -m pytest -q
```

預期：Agent 先用 `read_file` 讀 `shop/pricing.py`，再用 `edit_file` 修改，畫面會印出每次修改的 `old → new`；最後 `7 passed`。

觀察：

- 模型有沒有改用 bash（例如 `sed`）繞過 edit_file？如果有，description 該怎麼改？
- 有沒有出現「檔案在上次讀取後被修改過」的錯誤？模型收到後怎麼處理？

## Part C：拆除實驗

依 `ablation.md` 進行，結果填入 `ablation/ablation_sheet.md`。

Windows：`ablation.md` 裡的 `python3 ablate.py …` 一律改成 `python ablate.py …`，`export ANTHROPIC_API_KEY="..."` 改成 `$env:ANTHROPIC_API_KEY = "..."`，`cat ablation_results.csv` 改成 `Get-Content ablation_results.csv -Encoding UTF8`。`ablate.py` 已改用 UTF-8 解讀工具輸出。

## 預期結果

- Part A：兩邊都產生分類正確的週報檔；Claude Code 會明確顯示呼叫 Skill。
- Part B：`test_edit_tool.py` 6 passed、`test_mini_agent_edit.py` 5 passed；用 `mini_agent_edit.py` 修完後 `7 passed`。
- Part C：至少完成基準與兩組拆除，並寫下判讀。

## 檢核點

- [ ] `weekly-demo` 中兩個 Skill 位置都有 `SKILL.md`
- [ ] Claude Code 與 Codex 各產生一份週報，並完成比較表
- [ ] `test_edit_tool.py` 與 `test_mini_agent_edit.py` 全數通過
- [ ] 新版 Agent 修完 buggy_shop 後 `7 passed`
- [ ] 拆除實驗紀錄表至少填完基準與兩組

## 沒有 API 金鑰時

Part B 的兩個測試檔不需要金鑰。Agent 本身可用模擬伺服器確認能跑完：

```bash
python3 ../../mock/mock_api.py 8899 &
export ANTHROPIC_BASE_URL=http://127.0.0.1:8899 ANTHROPIC_API_KEY=x
python3 ../mini_agent_edit.py      # 模擬伺服器只會要求執行 bash，不會呼叫 read_file / edit_file
```

Windows（PowerShell，在 `shop_work` 內）：

```powershell
$mock = Start-Process python -ArgumentList "..\..\mock\mock_api.py", "8899" -PassThru -WindowStyle Hidden
$env:ANTHROPIC_BASE_URL = "http://127.0.0.1:8899"; $env:ANTHROPIC_API_KEY = "x"
python ..\mini_agent_edit.py
Stop-Process -Id $mock.Id        # 用完關掉模擬伺服器
Remove-Item Env:ANTHROPIC_BASE_URL, Env:ANTHROPIC_API_KEY   # 之後要用真實 API 時記得清掉
```

模擬伺服器送來的指令是 `python3 -c 'print(6*7)'`，在 Windows 的 cmd.exe 會失敗（`python3` 是空殼，單引號也不被 cmd 接受），但 Agent 會把錯誤文字回傳後正常結束。這裡只是確認迴圈能跑完。

## 延伸題

1. 在 `SKILL.md` 旁加一個 `scripts/collect.sh`，把 `git log` 的指令放進腳本，再在 `SKILL.md` 中改成執行這個腳本。兩邊都還能正確觸發嗎？
2. 讓 `edit_file` 在寫入前印出差異，並用 `input("確認修改？(y/n) ")` 要求人工確認。這屬於依「可逆性」分級的哪一級？
3. 把 `read_times` 的比對從修改時間改成檔案內容的 SHA-256 雜湊，處理時間解析度不足的檔案系統。
4. 把 `read_file` / `edit_file` 移植到 `mini_agent_openai.py`。
