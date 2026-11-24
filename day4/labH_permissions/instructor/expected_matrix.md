# 實作 H 參考結果（講師實測）

測試環境：Linux 容器、Claude Code 2.1.312（bubblewrap 0.9 + socat）、Codex CLI 0.165.0。
macOS（Seatbelt）的細節可能不同，開課前請在學員機型上用 `verify_*.sh` 再跑一次。

| 編號 | 探測 | Claude Code（沙箱＋規則） | Codex（設定檔 lab） | Codex（內建 :workspace，對照） |
|---|---|---|---|---|
| P1 | 寫入工作區 | 成功 | 成功 | 成功 |
| P2 | 寫入家目錄 | 擋：Read-only file system（沙箱） | 擋：Read-only file system（沙箱） | 擋 |
| P3 | 讀 .env | 擋：Permission denied（沙箱 denyRead） | 擋：Permission denied（設定檔 deny） | **讀得到** |
| P4 | 讀 sub/app.env | 擋：Permission denied（`Read(./**/*.env)` 規則併入沙箱讀取限制） | 擋：Permission denied（`**/*.env`） | **讀得到** |
| P5 | 連 pypi.org | 200 | 200 | 擋：無法解析主機（:workspace 預設無網路） |
| P6 | 連 github.com | 擋：CONNECT 403，沙箱回報 `deny network-outbound github.com:443` | 擋：CONNECT 403；`codex exec` 下的訊息為 `domain is not on the allowlist` | 擋（無網路） |
| P7 | 寫入 .git | **成功**（Claude Code 沙箱預設不保護 .git） | 擋：Read-only（`.git`、`.agents`、`.codex`、`.aws` 一律唯讀） | 擋 |

## 其他實測

- **拿掉 `network_proxy`**：Codex P6 變成連得上（HTTP 400 來自 GitHub 本身），證實沒有 proxy 時網域規則不生效。
- **Glob 寫法**：`[permissions.lab.filesystem]` 底下直接寫 `"**/*.env" = "deny"`，0.165 回報 `filesystem path '**/*.env' must be absolute, use '~/...', or start with ':'`；寫成 `":workspace_roots/**/*.env"` 也失敗。可用的寫法是 `[permissions.lab.filesystem.":workspace_roots"]` 表格底下的 `"**/*.env" = "deny"`。
- **`**` 在 Linux**：`codex exec` 會警告不原生支援 `**`，建議設 `glob_scan_max_depth`。
- **快照時機**：在同一個 `codex sandbox` 處理程序中新建的 `sub/app.env` 可以寫入；下一個處理程序就讀不到了，符合文件「deny glob 在每個處理程序啟動時快照」的說明。
- **權限規則（`verify_claude_rules.sh`）**：
  - `Bash(touch *)` 拒絕 `touchall`。
  - `Bash(touch*)` 放行 `touchall`。
  - `allow Bash(git push *)` 加 `deny Bash(git *)` 時，推送被拒。
- **Read 工具**：`deny Read(./.env)` 會讓 Read 工具讀 `.env` 時出現在 `permission_denials`。
- **未信任資料夾**：`claude -p` 印出 `Ignoring N permissions.allow entries from .claude/settings.json: this workspace has not been trusted`；deny 與沙箱仍生效。
- **Auto mode**：`claude -p --permission-mode auto` 請它 `git push --force origin main` 到本機 bare repo，分類器放行（使用者明確要求、目標是本機）。教學重點：不可接受的動作要用 deny 規則或 Hook 鎖死。
- **Approve for me（用模擬模型）**：
  - 模擬模型要求 `sandbox_permissions: require_escalated` 寫入 `/root`。Codex 把請求送給審查者，審查者本身也呼叫模型。
  - 模擬伺服器回的不是 JSON，所以結果是 `Automatic approval review failed: guardian assessment was not valid JSON … This is a review failure, not a determination that the action is unsafe`，動作沒有執行，即失敗時預設拒絕。
  - 真實模型下的放行與拒絕判斷尚未驗證。
- **已移除**：`codex exec --full-auto` 回 `unexpected argument '--full-auto'`；`approval_policy = "untrusted"` 回 `no longer supported; remove this setting`。
