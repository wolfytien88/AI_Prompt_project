# 起始素材：Acme 團隊散落在各專案的設定

| 檔案 | 是什麼 | 要放進外掛的哪裡 |
|---|---|---|
| `.claude/skills/pr-summary/SKILL.md` | 寫 PR 摘要的 Skill | 外掛的 `skills/pr-summary/SKILL.md` |
| `.claude/agents/security-reviewer.md` | Claude Code 的資安審查 Subagent | 外掛的 `agents/security-reviewer.md` |
| `.codex/agents/security-reviewer.toml` | Codex 的資安審查 Agent | 不進外掛，留在專案的 `.codex/agents/` |
| `hooks/guard.py` | 實作 7 的守門腳本 | 外掛的 `hooks/guard.py`，再寫一份 `hooks/hooks.json` |
