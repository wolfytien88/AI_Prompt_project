# 三個安全陷阱：重現步驟與實測結果

驗證環境：Claude Code 2.1.310（真實模型）、Codex CLI 0.164.0（本機模擬模型，Hook 與沙箱為真實執行）。自動化腳本：`claude_check/run_claude_check.sh`、`codex_check/run_codex_check.sh`。

## 陷阱 1：Codex 的 Hook 未信任就被靜默略過

**現象**：專案層 `.codex/hooks.json` 已經寫好，但專案未信任，或 Hook 未在 `/hooks` 審查並信任時，Codex 不會執行 Hook，也不會顯示任何警告。

**重現步驟**

1. 依 `lab7.md` 步驟 1、4 建好專案與 `.codex/hooks.json`，但先不要信任專案。
2. 請 Codex 執行 `git push origin main`。
3. 檢查遠端：`git --git-dir=../remote.git show-ref`。
4. 只信任專案、不在 `/hooks` 信任 Hook，再做一次。
5. 兩者都信任後，再做一次。

**實測結果**（`run_codex_check.sh` 案例 A–E）

| 案例 | 設定 | 結果 |
| --- | --- | --- |
| A | 沒有 Hook（對照組） | 推送成功，遠端 refs=1 |
| B | 專案層 Hook，專案未信任 | 推送成功，遠端 refs=1，沒有警告 |
| C | 專案已信任，Hook 未審查 | 推送成功，遠端 refs=1，沒有警告 |
| D | 專案已信任，Hook 已信任 | 被擋：`Command blocked by PreToolUse hook: 禁止直接推送到 main，請開 PR. Command: git push origin main`，遠端 refs=0 |
| E | 使用者層 `~/.codex/hooks.json`，Hook 已信任 | 被擋，訊息同上，遠端 refs=0 |

**對策**：裝好 Hook 後，一定用一個「應該被擋」的指令實測。Claude Code 的專案設定則是直接生效（同意信任資料夾後）。

## 陷阱 2：deny 規則不是完整邊界

**現象**：Claude Code 的 `Read(./.env)` deny 規則擋得住 Read 工具與 `cat .env`，但擋不住其他程式讀檔。

**重現步驟**：依 `lab7.md` 步驟 8，依序要求三種讀法。

**實測結果**（`run_claude_check.sh` 案例 2–4）

| 讀法 | 結果 |
| --- | --- |
| Read 工具讀 `./.env` | 被拒：`File is in a directory that is denied by your permission settings.` |
| Bash 執行 `cat .env` | 被拒：`Permission to use Bash with command cat .env has been denied.` |
| Bash 執行 `python3 -c "print(open(chr(46)+chr(101)+chr(110)+chr(118)).read())"` | 成功讀出 `SECRET_TOKEN=sk-fake-123456 DB_PASSWORD=not-a-real-password` |

**對策**：機密靠 OS 沙箱保護，或根本不放在 Agent 的工作目錄；正式環境參考 Managed Agents 的做法，把憑證放在 Vault，由 Proxy 代為呼叫。

## 陷阱 3：沙箱可寫範圍比想像寬

**現象**：Codex 的 `workspace-write` 除了工作目錄，也允許寫入 `/tmp` 與 `$TMPDIR`。

**重現步驟**

1. 建一個放在 `/tmp` 下的 bare repo 當遠端，專案不裝 Hook，以 `codex exec -s workspace-write` 請 Codex 推送。
2. 再建一個放在家目錄（工作區與 `/tmp` 以外）的 bare repo，重做一次。

**實測結果**（`run_codex_check.sh` 案例 F、G）

| 案例 | 遠端位置 | 結果 |
| --- | --- | --- |
| F | `/tmp` 底下 | 推送成功，遠端 refs=1（本機追蹤分支因 `.git` 不可寫而更新失敗：`unable to create directory for .git/refs/remotes/origin/main`） |
| G | 家目錄 | 被沙箱擋下：`unable to create temporary object directory … ! [remote rejected]`，遠端 refs=0 |

Codex 啟動時顯示的沙箱範圍為 `workspace-write [workdir, /tmp, $TMPDIR]`。

**對策**：清楚列出可寫目錄（`sandbox_workspace_write.writable_roots`），敏感資源不放在預設可寫的位置。

## 另外兩點

- `codex exec` 非互動模式沒有人能核准，啟動訊息顯示 `approval: never`，即使設定為 `on-request`。
- Linux 的沙箱使用 bubblewrap；找不到時 Codex 會改用內建版本並顯示警告。
