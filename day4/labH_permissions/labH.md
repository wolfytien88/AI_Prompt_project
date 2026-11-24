# 實作 H：權限規則、沙箱與自動審查

> 在 VS Code 中操作本實作的方式，見 [`../../vscode.md`](../../vscode.md)。

## 目的

- 分清楚三層：**權限規則**決定 Agent 能不能呼叫某個工具，**沙箱**決定指令實際碰得到哪些檔案與網路，**自動審查**決定誰來回答核准請求。
- 在 Claude Code 與 Codex 寫出同一份政策：工作區可寫、家目錄不可寫、任何 `.env` 都不可讀、網路只開 `pypi.org`。
- 用同一組探測指令（P1–P7）實測兩邊，填出探測矩陣，找出兩家預設行為的差異。

## 形式

個人實作，兩人一組對照結果。

## 前置

| 項目 | 說明 |
| --- | --- |
| 軟體 | Git、Python 3.10+、Claude Code CLI、Codex CLI 0.165 以上 |
| 沙箱元件 | macOS：內建 Seatbelt，不必另裝。Linux／WSL2：`sudo apt install bubblewrap socat`（Claude Code 需要兩者；Codex 自帶 Linux 沙箱）。原生 Windows：Claude Code 沙箱不支援，改用 WSL2 |
| 教材檔案 | `setup.sh`、`probes.txt`、`codex_probes.sh`、`claude_probe_prompt.txt`、`claude/settings.json`、`codex/config.toml`、`record_template.md` |
| 安全 | `.env` 只放假金鑰；探測指令只寫入練習資料夾與家目錄的測試檔 |

## 步驟

### 1. 建立練習專案

```bash
bash <教材路徑>/setup.sh            # 預設建立 ~/labH/proj 與 ~/labH/codex-home
cd ~/labH/proj
export CODEX_HOME=~/labH/codex-home  # 讓 Codex 只讀這份練習設定，不動到你平常的 ~/.codex
```

`setup.sh` 會放兩個假機密檔（根目錄 `.env`、`sub/app.env`），並把兩邊的設定檔複製到位。

### 2. 讀懂 Claude Code 的設定（`.claude/settings.json`）

| 區塊 | 內容 | 重點 |
| --- | --- | --- |
| `permissions.allow` | `Bash(git status)`、`Bash(npm run *)` 等 | 免詢問直接執行 |
| `permissions.ask` | `Bash(git push *)` | 每次都要問 |
| `permissions.deny` | `Read(./.env)`、`Read(./**/*.env)`、`Bash(git push --force *)` | 直接拒絕 |
| `sandbox.enabled` | `true` | Bash 指令在 OS 層隔離中執行 |
| `sandbox.allowUnsandboxedCommands` | `false` | 嚴格模式：不允許指令改到沙箱外執行 |
| `sandbox.filesystem.denyRead` | `["./.env"]` | 沙箱層也禁讀 |
| `sandbox.network.allowedDomains` | `pypi.org` 等 | 其他網域一律擋 |

兩個容易寫錯的地方：

- **判斷順序是 deny → ask → allow**，與規則寫得多精確無關。`allow: Bash(git push *)` 加上 `deny: Bash(git *)`，結果是拒絕。
- **星號前的空白有意義**。`Bash(touch *)` 只符合 `touch` 加參數；`Bash(touch*)` 連 `touchall` 這種別的指令都會放行（官方文件的例子是 `Bash(ls*)` 會符合 `lsof`）。

### 3. 讀懂 Codex 的設定（`codex/config.toml`）

```toml
approval_policy = "on-request"
approvals_reviewer = "auto_review"
default_permissions = "lab"

[permissions.lab]
extends = ":workspace"

[permissions.lab.filesystem]
glob_scan_max_depth = 3

[permissions.lab.filesystem.":workspace_roots"]
"**/*.env" = "deny"

[permissions.lab.network]
enabled = true

[permissions.lab.network.domains]
"pypi.org" = "allow"

[features]
network_proxy = true
```

- 權限設定檔（permission profiles，beta）取代舊的 `sandbox_mode`。兩者不要混用，只要任何地方出現 `sandbox_mode`，Codex 就改回舊系統。
- 內建設定檔有 `:read-only`、`:workspace`、`:danger-full-access`。
- `"**/*.env"` 要寫在 `":workspace_roots"` 表格底下。直接寫在 `[permissions.lab.filesystem]` 會出現「path must be absolute」錯誤（0.165 實測）。
- Linux 不原生支援 `**`，所以加上 `glob_scan_max_depth`。
- 只開 `network.enabled` 而沒有開 `features.network_proxy`，網域規則不會生效，網路等於全開。
- TOML 的頂層設定（`approval_policy` 等）必須寫在第一個 `[表格]` 之前。

### 4. 先不靠模型，直接探測 Codex 沙箱

`codex sandbox` 可以不經過模型，直接在指定的權限設定檔裡跑指令：

```bash
bash <教材路徑>/codex_probes.sh ~/labH/proj lab          # 你的設定檔
bash <教材路徑>/codex_probes.sh ~/labH/proj :workspace   # 內建設定檔，對照用
```

把結果填進 `record_template.md` 的 Codex 欄。

### 5. 用 Claude Code 跑同一組探測

```bash
cd ~/labH/proj
claude                                   # 第一次開啟：同意信任此資料夾，專案的 allow 規則才會生效
```

在對話中貼上 `claude_probe_prompt.txt` 的內容。也可以用非互動模式：

```bash
claude -p "$(cat <教材路徑>/claude_probe_prompt.txt)" --output-format json > probe.json
```

把結果填進 Claude Code 欄。注意：沒有信任過的資料夾，`claude -p` 會忽略專案設定裡的 `allow` 規則（會印出警告），但 deny 與沙箱照樣生效。

### 6. 驗證兩個規則陷阱

```bash
mkdir -p ~/labH/bin && printf '#!/bin/sh\ntouch touched && echo TOUCHALL-RAN\n' > ~/labH/bin/touchall && chmod +x ~/labH/bin/touchall
export PATH=~/labH/bin:$PATH
claude -p "只執行一個 Bash 指令：touchall，不要改用其他方法" --settings '{"permissions":{"allow":["Bash(touch *)"]}}' --output-format json | jq '.permission_denials'
claude -p "只執行一個 Bash 指令：touchall，不要改用其他方法" --settings '{"permissions":{"allow":["Bash(touch*)"]}}'  --output-format json | jq '.permission_denials'
```

第一個應拒絕 `touchall`，第二個會放行。`claude -p` 在沒有指定模式時以 Manual 模式執行，凡是需要詢問的動作都直接拒絕，所以結果可以從 `permission_denials` 讀出來。

### 7. 權限模式與自動審查

| | Claude Code | Codex |
| --- | --- | --- |
| 模式 | `default`（Manual）、`acceptEdits`、`plan`、`auto`、`dontAsk`、`bypassPermissions`；Shift+Tab 切換，或 `--permission-mode` | `approval_policy`：`on-request`、`never`；沙箱：設定檔或 `-s` |
| 交給模型判斷 | **Auto mode**：分類器逐一審查每個動作 | **Approve for me**：`approvals_reviewer = "auto_review"` 或 `--approve-for-me`，審查者只回答沙箱邊界上的核准請求 |
| 停損 | 連續 3 次或累計 20 次被擋就暫停 | 連續 3 次拒絕，或最近 50 次中有 10 次拒絕，就中止這一輪；`/approve` 可重試一次被拒的動作 |
| 注意 | Auto mode 期間，`Bash(*)` 這類寬鬆 allow 規則會被丟掉；專案設定不能把 `defaultMode` 設成 `auto` 或 `bypassPermissions` | 自動審查只換「誰來審」，不會多給權限；`never`、`--yolo`、`:danger-full-access` 不會產生核准請求，也就沒有東西可審 |

實際試一次：

1. **Claude Code**：在練習專案建一個本機 bare repo 當遠端，用 `claude --permission-mode auto` 請它 `git push --force origin main`，觀察分類器的決定。
2. **Codex**：用 `codex --approve-for-me` 請它把檔案寫到工作區以外的路徑，觀察審查結果與 `/approve` 的效果。

討論：使用者明確要求時，分類器可能放行（講師實測：推到本機 bare repo 的 force push 被放行）。所以「絕對不行」的事，要用 deny 規則或 Hook 鎖死，不能交給模型判斷。

### 8. 已退役的寫法

舊教學常見但現在會失敗的寫法：

| 寫法 | 0.165 的結果 | 改用 |
| --- | --- | --- |
| `codex --full-auto` | `unexpected argument '--full-auto'` | `--sandbox workspace-write` 或 `--approve-for-me` |
| `approval_policy = "untrusted"` | `no longer supported; remove this setting`，Codex 無法啟動 | `on-request`；要更嚴格，用 `[projects."<路徑>"] trust_level = "untrusted"` |
| `[profiles.x]` 表格 | 不再讀取（0.134 起） | `~/.codex/x.config.toml` 搭配 `--profile x` |

## 觀察重點

- 兩邊都禁讀 `.env` 時，子目錄的 `sub/app.env` 有沒有一起擋到？靠的是哪一條設定？
- 兩邊對 `.git` 的預設處理一樣嗎？
- 沒開 `network_proxy` 時，未允許的網域連得上嗎？
- Claude Code 的 deny 規則擋的是「Read 工具」，沙箱擋的是「指令實際讀檔」。只有其中一層時，請 Agent 用 `python3 -c "print(open('.env').read())"` 讀檔，結果會怎樣？

## 檢核點

- [ ] `record_template.md` 的 P1–P7 兩欄都填完，並標出擋下的是哪一層
- [ ] 能說明 `Bash(touch *)` 與 `Bash(touch*)` 的差別，並有 `permission_denials` 的輸出佐證
- [ ] Codex 設定檔沒有 `sandbox_mode`，且 `network_proxy = true`
- [ ] 能說出自動審查與 Auto mode 各自的停損條件

## 延伸題

1. 把 Codex 的 `.env` 規則改成 `"*.env"`、`"*/*.env"` 兩條明確深度的寫法，比較與 `**` 加 `glob_scan_max_depth` 的差異。
2. 在 Claude Code 加上 `sandbox.excludedCommands`，讓某個指令改在沙箱外執行，觀察 `allowUnsandboxedCommands: false` 的影響。
3. 寫一份 `[auto_review].policy`（Markdown），規定「任何推送到 main 都拒絕」，再測一次 Approve for me。
4. 把這份權限設定和實作 7 的 Hook 一起裝，列出每個探測是被哪一層先擋下。

## 沒有 API 金鑰時

- 步驟 4 的 `codex sandbox` 探測不呼叫模型，不需要金鑰。
- Claude Code 的探測需要可用的帳號。沒有帳號時，可以只做 Codex 欄，再對照 `instructor/expected_matrix.md` 的 Claude Code 實測結果。

## 兩邊比較

| 面向 | Claude Code | Codex |
|---|---|---|
| 規則寫在哪 | `.claude/settings.json` 的 `permissions.allow／ask／deny` | `config.toml` 的權限設定檔 `[permissions.<名稱>]` |
| 規則對象 | 工具呼叫（`Bash(...)`、`Read(...)`、`WebFetch(domain:...)`） | 沙箱內的檔案路徑與網域 |
| 沙箱 | `sandbox.enabled`；Linux 需 bubblewrap＋socat | 內建；Linux 用 bwrap＋seccomp |
| 網域白名單 | `sandbox.network.allowedDomains` | `network.domains` 加 `features.network_proxy = true` |
| `.git` 預設 | 可寫 | 唯讀（與 `.codex`、`.agents`、`.aws` 一起） |
| 交給模型審查 | Auto mode（審每個動作） | Approve for me（只審沙箱邊界的請求） |
| 不經模型直接測沙箱 | 無對應指令 | `codex sandbox -P <設定檔> -C <目錄> -- <指令>` |

## 參考

- Claude Code 權限：https://code.claude.com/docs/en/permissions
- Claude Code 權限模式：https://code.claude.com/docs/en/permission-modes
- Claude Code 沙箱：https://code.claude.com/docs/en/sandboxing
- Claude Code 設定：https://code.claude.com/docs/en/settings
- Codex 核准與安全：https://learn.chatgpt.com/docs/agent-approvals-security
- Codex 權限設定檔：https://learn.chatgpt.com/codex/permissions
- Codex 自動審查：https://learn.chatgpt.com/codex/sandboxing/auto-review
- Codex 設定參考：https://learn.chatgpt.com/docs/config-file/config-reference
