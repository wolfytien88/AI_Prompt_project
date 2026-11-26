# 實作 B 驗證紀錄（2026-10-30）

環境：Claude Code 2.1.312（真實模型）、Codex CLI 0.165.0（模擬 Responses API）。專案由 `make_repo.sh` 建立，複製 `instructor/ref/`。

## Claude Code（真實模型）
1. `claude -p "/changelog v1.2.0 2026-11-01"` → CHANGELOG.md 新增 `## v1.2.0（2026-11-01）`，分「新功能 1／修正 1／文件與測試 3」；未提交 commit；`permission_denials` 為空（`allowed-tools` 的 `Edit(CHANGELOG.md)` 生效）。
2. 第一版 Skill 使用 `` !`git log --oneline $(git describe --tags --abbrev=0)..HEAD` `` → 執行成功但結果為空字串，CHANGELOG 未變更；改為 `` !`git log --oneline --decorate -20` `` 後正常。教材已採用後者並在觀察重點說明。
3. `claude -p "幫我寫 v1.2.0 的更新紀錄"` → 未呼叫 Skill（disable-model-invocation 生效），模型自行執行 git，Edit 被拒（列在 permission_denials），改為輸出草稿。
4. `claude -p "我改了什麼？這些修改可以提交了嗎？"`（無 --allowedTools）→ 模型呼叫 `Skill(diff-risk)`，但被列入 permission_denials，改為自己執行 git diff。
5. 同一句加 `--allowedTools "Skill(diff-risk)"` → Skill 執行成功，未再呼叫 Bash（diff 由 `` !`git diff HEAD` `` 提供），指出拿掉負數檢查與寫死金鑰。

## Codex（模擬伺服器，Codex 本身真實執行）
6. `codex exec "我改了什麼？"` → 請求的 `<skills_instructions>` 列出 diff-risk（含中文描述），未列出 changelog（`allow_implicit_invocation: false` 生效）。
7. `codex exec '$changelog v1.2.0 2026-11-01'` → 請求中多一則 user 訊息 `<skill><name>changelog</name><path>…/SKILL.md</path>…`，含 SKILL.md 全文。

## Windows 驗證（2026-11-26）
環境：Windows 10、Windows PowerShell 5.1、Git for Windows、Claude Code 2.1.332（真實模型）；Codex 未安裝。
1. `make_repo.ps1` 建出的四個檔案與 `make_repo.sh`（Git Bash）逐位元組相同，commit 訊息與 `git diff HEAD` 也相同。
2. Git Bash 未設 `MSYS_NO_PATHCONV=1` 時，`claude -p "/changelog v1.2.0 2026-11-01"` 收到的是 `C:/Program Files/Git/changelog …`，Skill 未觸發，Edit 被拒。設定後正常。
3. PowerShell 執行 `/changelog v1.2.0 2026-11-01` → 新增 v1.2.0 段落（新功能 1／修正 1／文件與測試 3），`permission_denials` 為空，未建立 commit 或標籤。
4. PowerShell 執行「幫我寫 v1.2.0 的更新紀錄」→ 0 次 Skill 呼叫；`permission_denials` 為 PowerShell、PowerShell、Edit；CHANGELOG.md 未變更。
5. PowerShell 執行 diff-risk 指令並以 `Select-String '"name":"Skill"'` 過濾 → 找到 `"name":"Skill","input":{"skill":"diff-risk"}`，指出寫死金鑰（高）與拿掉負數檢查（中）。
6. `commits_since_tag.ps1` 輸出 `最新標籤：v1.1.0` 與 5 筆 commit，UTF-8 編碼正確。

## 尚未驗證
- Windows 上真實 Codex 執行 `$changelog`（是否選用 `commits_since_tag.ps1`）。
- 真實 GPT 模型執行 `$changelog` 與 diff-risk 的結果。
- 互動模式下 `/changelog` 的 `argument-hint` 顯示畫面。
