# 實作 I 參考結果（講師實測）

測試環境：Linux 容器、Claude Code 2.1.312、Codex CLI 0.165.0。

## Claude Code（`verify_claude_plugin.sh`，真實模型）

| 項目 | 結果 |
|---|---|
| `claude plugin validate` 外掛 | `√ Validation passed`。沒有 `license` 時，會出現外掛目錄（官方市集）不收的提示；本機或團隊使用不影響 |
| `claude plugin validate` 市集 | 沒有 `description` 時，會是 `√ Validation passed with warnings` |
| `-p "/acme-team-kit:pr-summary reviewer" --plugin-dir …` | 依 `git diff` 產生三段摘要，約 0.07 美元 |
| 外掛 Hook | `git push origin main` 被擋，訊息為「禁止直接推送到 main，請開 PR」，遠端沒有分支。Claude Code 不需另外信任外掛的 Hook |
| `claude plugin details` | Skills 1、Agents 1、Hooks 1（PreToolUse，不占模型上下文）；Always-on 約 127 token |
| `@agent-acme-team-kit:security-reviewer` | Agent 工具的 `subagent_type` 為 `acme-team-kit:security-reviewer`；找出硬編碼金鑰與指令注入 |
| `marketplace add` 後寫入 `~/.claude/settings.json` | `extraKnownMarketplaces.acme-tools.source = {"source":"directory","path":…}`、`enabledPlugins["acme-team-kit@acme-tools"] = true` |

## Codex（`verify_codex_plugin.sh`，模擬模型）

| 情境 | 結果 |
|---|---|
| `codex plugin marketplace add` 指向 Claude 格式的市集 | 成功，讀的是 `.claude-plugin/marketplace.json` |
| `codex plugin add acme-team-kit@acme-tools` | 安裝到 `$CODEX_HOME/plugins/cache/acme-tools/acme-team-kit/1.0.0`；`config.toml` 新增 `[marketplaces.acme-tools]` 與 `[plugins."acme-team-kit@acme-tools"] enabled = true` |
| Skill 是否進入模型上下文 | 是，`skills_instructions` 中出現 `acme-team-kit:pr-summary: 依目前尚未提交的變更寫出 PR 摘要…` |
| Markdown 格式的 Subagent | 沒有出現在請求中 |
| Hook，未信任 | 被略過，`git push origin main` 成功，遠端出現 main |
| Hook，`--dangerously-bypass-hook-trust` | 被擋：`Command blocked by PreToolUse hook: 禁止直接推送到 main，請開 PR`，遠端沒有分支 |
| Codex 原生格式（`.agents/plugins/marketplace.json` + `.codex-plugin/plugin.json`） | 安裝成功，Hook 行為同上 |
| `${CLAUDE_PLUGIN_ROOT}` | Codex 執行外掛 Hook 時也會設定，同一份 `hooks.json` 兩邊通用 |

## 討論題參考答案

- **兩邊通用**：Skill（`SKILL.md`）、Hook（`hooks.json` 與腳本）、市集清單（Codex 可讀 Claude 格式）。
- **各寫一份**：
  - Subagent：Claude Code 用 Markdown，Codex 用 TOML。
  - 團隊佈署：Claude Code 用專案 `settings.json`，Codex 用每人的 `config.toml`。
- **為什麼要另外信任 Hook**：Hook 會在使用者電腦上執行任意指令。Codex 讓信任綁定 Hook 內容的雜湊值，外掛更新改了 Hook 就得重新信任，避免供應鏈攻擊悄悄生效。
