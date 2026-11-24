# acme-team-kit

Acme 團隊共用的 Claude Code 外掛（虛構範例）。

| 元件 | 名稱 | 用法 |
|---|---|---|
| Skill | `pr-summary` | `/acme-team-kit:pr-summary reviewer` |
| Subagent | `security-reviewer` | `@agent-security-reviewer` 或讓 Claude 自動委派 |
| Hook | `hooks/guard.py` | PreToolUse（Bash）：擋推送到 main/master、`rm -rf /`、`curl … \| sh` |

## 安裝

```
/plugin marketplace add ./acme-marketplace
/plugin install acme-team-kit@acme-tools
```
