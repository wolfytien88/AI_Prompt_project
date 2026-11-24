# 實作 H 驗證紀錄

環境：Linux 容器（root）、Claude Code 2.1.312、Codex CLI 0.165.0、bubblewrap 與 socat（用 apt 安裝）、Python 3。

## 已實際執行

| 項目 | 指令 | 結果 |
|---|---|---|
| 設定檔語法 | `tomllib` 載入 `codex/config.toml`、`json` 載入 `claude/settings.json` | 通過；頂層鍵 `approval_policy`、`approvals_reviewer`、`default_permissions` 位置正確 |
| 建立練習專案 | `bash setup.sh ~/labH_run` | 通過 |
| Codex 沙箱探測 | `bash instructor/verify_codex_sandbox.sh ~/labH_v` | P1 允許；P2、P3、P4、P6、P7 擋；P5 通。對照組 `:workspace`：P3、P4 讀得到，P5 不通。拿掉 `network_proxy` 後 P6 變成連得上 |
| Codex 已移除設定 | 同上 | `--full-auto` 與 `approval_policy="untrusted"` 皆報錯 |
| Codex 經模型（模擬）執行 | `codex exec` + `day4/codex_check/mock_codex.py`，模擬模型依序要求 4 個指令 | `.env` Permission denied；github.com 回報 `domain is not on the allowlist for the current sandbox mode`；pypi 200；家目錄 Read-only |
| Approve for me（模擬） | `codex exec --approve-for-me`，模擬模型要求 `require_escalated` | approval 變成 `on-request`；請求送到審查者；審查者回覆不是 JSON，所以拒絕執行（fail-closed） |
| Claude Code 沙箱探測（真實模型） | 在 `~/labH_run/proj` 執行 `claude -p "$(cat claude_probe_prompt.txt)"` | P1、P5、P7 通；P2、P3、P4、P6 擋。費用約 0.12 美元 |
| Claude Code 規則陷阱（真實模型） | `bash instructor/verify_claude_rules.sh ~/labH_rules` | 三項都符合預期，詳見 `instructor/expected_matrix.md` |
| Claude Code Auto mode（真實模型） | `claude -p ... --permission-mode auto`，force push 到本機 bare repo | 被分類器放行 |

## 與功能清單不符、已改寫的地方

- 清單寫的 `codex sandbox linux -P lab --log-denials -- CMD`，在 0.165 Linux 版不存在：
  - 沒有 `linux` 子指令（會被當成要執行的程式），也沒有 `--log-denials`。
  - 實際用法是 `codex sandbox -P <設定檔> -C <目錄> -- <指令>`，且 `-P` 是必填。教材已照實際用法撰寫。
- 清單範例的 `"**/*.env" = "deny"` 直接寫在 `[permissions.lab.filesystem]` 會報錯。教材改成 `[permissions.lab.filesystem.":workspace_roots"]`。
- `codex exec` 提示的 `glob_scan_max_depth` 不在功能清單內，是從 0.165 的警告訊息得知，已加進設定檔並實測可用。

## 尚未驗證

- macOS Seatbelt 與 Windows（WSL2）下的探測結果。
- 真實 OpenAI 模型下 Approve for me 的放行與拒絕判斷、熔斷條件（連續 3 次、50 次中 10 次），以及 `/approve`。目前只依文件撰寫。
- Claude Code 互動模式下的信任對話框與 Shift+Tab 切換。容器內無法操作 TUI，只用 `-p` 驗證。
- 互動模式下 Auto mode 的暫停條件（連續 3 次、累計 20 次）。
- `[auto_review].policy` 自訂政策（延伸題 3）。
