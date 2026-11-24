# 實作 I 驗證紀錄

環境：Linux 容器、Claude Code 2.1.312（真實模型）、Codex CLI 0.165.0（模擬模型 `day4/codex_check/mock_codex.py`）。

## 已實際執行

| 項目 | 指令 | 結果 |
|---|---|---|
| Claude 外掛與市集驗證 | `claude plugin validate`（含 `--strict`） | 通過 |
| `--plugin-dir` + Skill | `instructor/verify_claude_plugin.sh` 第 2 步 | 通過 |
| 外掛 Hook（Claude） | 同上第 3 步 | 推送被擋，遠端無分支 |
| 市集安裝與元件清單 | 同上第 4 步 | 通過；結束時已移除 |
| 外掛 Subagent（Claude） | 同上第 5 步 | 委派給 `acme-team-kit:security-reviewer` |
| `extraKnownMarketplaces`／`enabledPlugins` 格式 | `marketplace add` 後讀 `~/.claude/settings.json` | 得到 `directory` 來源的格式，已寫進 `team/` |
| Codex 讀 Claude 格式市集與外掛 | `instructor/verify_codex_plugin.sh` | 通過 |
| Codex 原生格式 | 同上 | 通過 |
| Codex Hook 信任 | 同上 | 未信任時推送成功；略過信任後推送被擋 |
| Codex 是否載入 Skill 與 Subagent | 用 `mock/mock_responses.py` 擷取完整請求 | Skill 出現，Markdown Subagent 沒有出現 |
| TOML 語法 | `tomllib` 載入 `security-reviewer.toml`、`codex_config_snippet.toml` | 通過 |

## 與功能清單不符或清單未涵蓋的地方

- 功能清單只寫 Codex 外掛用 `.codex-plugin/plugin.json`。以下兩點是實測得知，文件頁面沒有讀到：
  - Codex 也接受 `.claude-plugin/` 格式。
  - 原生市集清單放在 `.agents/plugins/marketplace.json`。
- `${CLAUDE_PLUGIN_ROOT}` 在 Codex 中可用，是實測結果，不是文件記載。

## 尚未驗證

- Codex 互動模式的 `/hooks` 信任流程（容器內無法操作 TUI；只用 `--dangerously-bypass-hook-trust` 驗證 Hook 本身）。
- Codex 中以 `$acme-team-kit:pr-summary` 明確叫用 Skill（只確認 Skill 已進入上下文）。
- `extraKnownMarketplaces` 的 `github` 來源與「同仁信任資料夾後自動提示安裝」的流程。只驗證了 `directory` 來源寫入使用者設定。
- `.claude/settings.json` 由專案層提交時的實際提示畫面。
- 延伸題（`.mcp.json`、`claude plugin tag`、`update`）。
