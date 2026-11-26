# 實作 B：Skill 與自訂指令

> 在 VS Code 中操作本實作的方式，見 [`../../vscode.md`](../../vscode.md)。
> 本實作補充實作 4 的 weekly-report Skill：實作 4 看「同一份 Skill 能否在兩套工具觸發」，這裡練習參數、動態內容、工具權限，以及「只能手動呼叫」與「讓模型自己挑」的差別。

## 目的

- 寫兩個 Skill：
  - `changelog`：只能由使用者手動呼叫，帶參數，會寫檔。
  - `diff-risk`：讓模型依描述自行選用。
- 在 Claude Code 用 `` !`指令` `` 在載入時就把 git 資料塞進 Skill，用 `allowed-tools` 預先核准它需要的工具。
- 在 Codex 寫對應版本：`.agents/skills/` 加上 `agents/openai.yaml` 與 `scripts/`。
- 知道兩個變化：Claude Code 的自訂指令（`.claude/commands/`）已併入 Skill；Codex 的自訂提示（`~/.codex/prompts/`）已不建議使用，官方建議改寫成 Skill。

## 形式

個人實作。

## 前置

| 項目 | 指令或說明 |
| --- | --- |
| Claude Code／Codex | 版本見 `../../README.md` |
| 練習專案 | macOS／Linux：`bash make_repo.sh ~/lab/invoice-tool`<br>Windows（PowerShell）：`powershell -ExecutionPolicy Bypass -File make_repo.ps1 $HOME\lab\invoice-tool`<br>有 `v1.1.0` 標籤、之後 5 筆 commit，以及一筆尚未提交的修改（拿掉負數檢查、寫死測試金鑰） |
| 參考答案 | `instructor/ref/`（`.claude/skills/`、`.agents/skills/`） |

### Windows 注意事項

本實作在 Windows 上建議全程使用 **PowerShell**，下面的指令都能直接貼上執行。

| 問題 | 原因與做法 |
| --- | --- |
| 在 PowerShell 執行 `bash make_repo.sh` 失敗或跑到 WSL | PowerShell 的 `bash` 通常是 `C:\Windows\system32\bash.exe`（WSL），不是 Git Bash。改用 `make_repo.ps1`。 |
| 在 Git Bash 執行 `claude -p "/changelog …"`，Skill 沒有觸發、寫檔被拒 | Git Bash 會把開頭是 `/` 的參數當成路徑，改寫成 `C:/Program Files/Git/changelog`。先執行 `export MSYS_NO_PATHCONV=1`，或改用 PowerShell。 |
| 複製參考答案 | PowerShell：`Copy-Item -Recurse -Force instructor\ref\* $HOME\lab\invoice-tool\`（`*` 會包含 `.claude`、`.agents` 隱藏資料夾）。檔案總管預設不顯示以 `.` 開頭的資料夾，可用 `Get-ChildItem -Force` 確認。 |
| `` !`指令` `` 在 Windows 怎麼執行 | Claude Code 在 Windows 透過 Git Bash 執行這些指令，所以 `` !`git diff HEAD \|\| true` `` 這類 bash 語法照樣可用；前提是已安裝 Git for Windows。 |
| 終端機中文亂碼 | 先執行 `chcp 65001`，或在 PowerShell 執行 `[Console]::OutputEncoding = [Text.Encoding]::UTF8`。只影響顯示，不影響檔案內容。 |

## 步驟

### Part 1：Claude Code 的 `changelog`（手動呼叫、帶參數）

1. 建立 `.claude/skills/changelog/SKILL.md`：

   ```markdown
   ---
   description: 依 git 紀錄替指定版本寫更新紀錄，寫入 CHANGELOG.md。
   argument-hint: <版本號> [發布日期]
   disable-model-invocation: true
   allowed-tools:
     - Read
     - Edit(CHANGELOG.md)
   ---
   ## 最新的版本標籤
   !`git describe --tags --abbrev=0`

   ## 最近的 commit（標籤以 tag: 標示）
   !`git log --oneline --decorate -20`

   ## 指示
   新版本號：$0
   發布日期：$1（空白就用今天的日期）
   1. 依 commit 前綴分組：feat →「新功能」、fix →「修正」、docs 與 test →「文件與測試」。
   2. 每項一行，改寫成使用者看得懂的句子。
   3. 把新段落插在「# 更新紀錄」標題下方、上一個版本之前。
   4. 不要建立 commit 或標籤。
   ```

   | 欄位 | 作用 |
   | --- | --- |
   | `disable-model-invocation: true` | 模型不會自己選用，只能輸入 `/changelog` |
   | `argument-hint` | 輸入 `/changelog` 時提示要帶什麼參數 |
   | `$0`、`$1` | 第 1、第 2 個參數（從 0 起算）；`$ARGUMENTS` 是整串參數 |
   | `` !`指令` `` | 載入 Skill 時先執行，輸出直接放進內容，模型不用再呼叫工具 |
   | `allowed-tools` | Skill 執行期間不必再詢問的工具，`Edit(CHANGELOG.md)` 只限這個檔案 |

2. 互動模式輸入 `/changelog v1.2.0 2026-11-01`；非互動模式：

   ```bash
   claude -p "/changelog v1.2.0 2026-11-01"
   ```

   不需要另外給權限參數，因為 `allowed-tools` 已核准 `Edit(CHANGELOG.md)`。

   > Windows：在 PowerShell 直接執行上面的指令即可。若在 Git Bash 執行，請先 `export MSYS_NO_PATHCONV=1`，否則 `/changelog` 會被改寫成路徑，Skill 不會觸發，寫檔會出現在 `permission_denials`。

3. 對照實驗：還原 CHANGELOG.md（`git checkout CHANGELOG.md`），改用一般句子：

   ```bash
   claude -p "幫我寫 v1.2.0 的更新紀錄"
   ```

   因為 `disable-model-invocation: true`，模型不會用這個 Skill，而是自己跑 git 指令；寫檔時也沒有 Skill 的預先核准，非互動模式會被拒絕。

   > Windows：模型可能改用 PowerShell 工具執行 git，這些呼叫同樣沒有預先核准，會和 Edit 一起出現在 `permission_denials`。這正好對照出 Skill 用 `` !`指令` `` 在載入時取資料的好處：不必再請求任何工具權限。

### Part 2：Claude Code 的 `diff-risk`（讓模型自己挑）

4. 建立 `.claude/skills/diff-risk/SKILL.md`。description 寫清楚「什麼時候用」，模型就是靠這段判斷：

   ```markdown
   ---
   description: 檢查尚未提交的修改有沒有風險，例如拿掉輸入檢查、寫死金鑰或密碼、刪掉測試。使用者問「我改了什麼」「這些修改安全嗎」「可以提交了嗎」時使用。
   allowed-tools:
     - Read
   ---
   ## 目前尚未提交的修改
   !`git diff HEAD || true`

   ## 指示
   1. 用兩到三點摘要修改內容。
   2. 列出風險，每項標示嚴重度（高／中／低）、所在檔案與行，並給一句修正建議。
   3. 沒有風險就明說「未發現風險」。不要修改任何檔案。
   ```

5. 不提 Skill 名稱，直接問：

   ```bash
   claude -p "我改了什麼？這些修改可以提交了嗎？" --allowedTools "Skill(diff-risk)" --output-format stream-json --verbose
   ```

   在輸出中找 `"name":"Skill"`，確認模型選用了 diff-risk。Windows PowerShell 可以直接過濾：

   ```powershell
   claude -p "我改了什麼？這些修改可以提交了嗎？" --allowedTools "Skill(diff-risk)" --output-format stream-json --verbose | Select-String '"name":"Skill"'
   ```

   （macOS／Linux 用 `| grep '"name":"Skill"'`。）非互動模式下，呼叫 Skill 本身也需要核准，所以要加 `--allowedTools "Skill(diff-risk)"`；互動模式會跳出詢問。

### Part 3：Codex 版本

6. 建立 `.agents/skills/changelog/`：

   ```
   .agents/skills/changelog/
   ├── SKILL.md                  frontmatter 必填 name 與 description
   ├── agents/openai.yaml        policy.allow_implicit_invocation: false
   └── scripts/
       ├── commits_since_tag.sh    macOS／Linux
       └── commits_since_tag.ps1   Windows（PowerShell）
   ```

   Codex 在 Windows 以 PowerShell 執行指令，`bash` 可能是 WSL 或不存在，所以 SKILL.md 要分平台寫清楚該跑哪個腳本（參考答案已示範）。

   Codex 的 Skill 沒有 `` !`指令` `` 與 `$0` 這類替換，所以：
   - 把「取得 commit」寫成 `scripts/` 裡的腳本，在 SKILL.md 指示 Codex 執行它。
   - 參數直接寫在呼叫後面，由 SKILL.md 說明如何解讀。

   `agents/openai.yaml`：

   ```yaml
   policy:
     allow_implicit_invocation: false
   ```

7. 建立 `.agents/skills/diff-risk/SKILL.md`（name、description 與 Claude 版相同，內容改為「執行 `git diff HEAD`」）。

8. 呼叫：

   ```bash
   codex '$changelog v1.2.0 2026-11-01'
   codex "我改了什麼？這些修改可以提交了嗎？"
   ```

   注意 `$changelog` 要用單引號，否則 shell 會把 `$changelog` 當成變數（bash 與 PowerShell 都一樣）。
   互動模式下也可以先輸入 `$` 從清單挑選。

## 觀察重點

- `` !`指令` `` 失敗時整個 Skill 會中止，沒有任何輸出。本教材驗證時發現 `` !`git log $(git describe ...)..HEAD` `` 這類含 `$(...)` 的寫法會讓 Skill 靜默失敗；請改成單純的指令，或在結尾加 `|| true`。
- 模型自選的準確度取決於 description。把 diff-risk 的 description 改成「檢查程式」，再問同一句話，看它還會不會被選用。
- Codex 一開始只把 Skill 的名稱與描述放進 Context；`allow_implicit_invocation: false` 的 Skill 不會出現在這份清單裡，只有明確輸入 `$changelog` 時才載入全文。

## 檢核點

- [ ] `/changelog v1.2.0 2026-11-01` 在 CHANGELOG.md 新增 v1.2.0 段落，分組正確，沒有建立 commit
- [ ] 不用斜線的一般句子不會觸發 changelog
- [ ] 問「我改了什麼」時，Claude Code 選用 diff-risk，指出「拿掉負數檢查」與「寫死金鑰」兩個風險
- [ ] Codex 的兩個 Skill 放在 `.agents/skills/`，`$changelog` 能載入
- [ ] 能說明 `disable-model-invocation`（Claude Code）與 `allow_implicit_invocation`（Codex）的對應

## 兩家對照

| 面向 | Claude Code | Codex |
| --- | --- | --- |
| 位置 | `.claude/skills/<名稱>/SKILL.md`、`~/.claude/skills/` | `.agents/skills/<名稱>/SKILL.md`、`~/.agents/skills/` |
| 必填欄位 | 都是選填（建議寫 description） | `name`、`description` |
| 手動呼叫 | `/名稱 參數` | `$名稱 參數` |
| 禁止模型自選 | `disable-model-invocation: true` | `agents/openai.yaml` 的 `policy.allow_implicit_invocation: false` |
| 參數替換 | `$ARGUMENTS`、`$0`、`$1`、`$name` | 無；由 SKILL.md 說明如何解讀 |
| 載入時執行指令 | `` !`指令` `` | 無；放在 `scripts/` 由 Agent 執行 |
| 預先核准工具 | `allowed-tools` | 依 Codex 的沙箱與核准設定 |
| 舊機制 | `.claude/commands/*.md` 已併入 Skill，同名時 Skill 優先 | `~/.codex/prompts/` 自訂提示已不建議使用 |

## 延伸題

1. 把 changelog 改成 `context: fork`，在獨立的 Context 執行，比較主對話少了多少 Token（`/context`）。
2. 用 `/skill-doctor`（Claude Code）查看每個 Skill 的使用次數與成本。
3. 在 Codex 執行 `$skill-creator`，讓它幫你產生第三個 Skill，再檢查它寫的 description。
4. 把舊的 `.claude/commands/release.md` 改寫成 Skill，比較兩種寫法。

## 沒有 API 金鑰時

Claude Code 部分需要模型。Codex 部分可用模擬伺服器（`../../mock/mock_responses.py`）確認 Skill 是否被發現：檢查送出的請求，`<skills_instructions>` 區塊會列出 diff-risk，不會列出 changelog；輸入 `$changelog` 時，請求中會多一則 `<skill><name>changelog</name>…` 訊息。做法見 `VERIFY.md`。

## 參考

- Claude Code：Skills https://code.claude.com/docs/en/skills.md
- Claude Code：Commands https://code.claude.com/docs/en/commands.md
- Codex：Build skills https://learn.chatgpt.com/codex/build-skills
- Codex：Skills and plugins https://learn.chatgpt.com/codex/skills-and-plugins
- Codex：Custom prompts（已不建議使用）https://learn.chatgpt.com/docs/custom-prompts
