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

## 尚未驗證
- 真實 GPT 模型執行 `$changelog` 與 diff-risk 的結果。
- 互動模式下 `/changelog` 的 `argument-hint` 顯示畫面。
