# acme-team-kit（Codex 版）

| 元件 | 名稱 | 用法 |
|---|---|---|
| Skill | `pr-summary` | `$acme-team-kit:pr-summary`，或讓 Codex 依描述自動選用 |
| Hook | `hooks/guard.py` | PreToolUse（Bash）：擋推送到 main/master、`rm -rf /`、`curl … \| sh`。安裝後要先用 `/hooks` 信任才會執行 |

Subagent 不放在外掛裡：Codex 的自訂 Agent 是 TOML 檔，放在專案的 `.codex/agents/`，範本見教材的 `starter/.codex/agents/security-reviewer.toml`。
