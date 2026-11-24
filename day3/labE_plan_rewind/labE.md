# 實作 E：先規劃再動手，做錯了倒回去

> 在 VS Code 中操作本實作的方式，見 [`../../vscode.md`](../../vscode.md)。

## 目的

在待辦清單起始專案上加一個跨四層的小功能，練習三件事：

- 讓 Agent 先規劃，你修改計畫後才動手
- 實作走錯方向時倒回去
- 知道哪些改動倒得回來、哪些倒不回來

Claude Code 用 plan mode 與 checkpoint／`/rewind`；Codex 用 `/plan`、`/fork`、`/side`，程式碼的退路改靠 git 與 worktree。

## 形式

個人實作。本實作以互動模式為主，請開兩個終端機（或 VS Code 的兩個終端機分頁）。

## 前置

- Claude Code、Codex CLI、git、Python 3.10 以上
- 單元三的起始專案 `starter/`

```bash
export E=/你的路徑/範例程式/day3/labE_plan_rewind
export M=/你的路徑/範例程式/day3
for t in claude codex; do
  cp -r "$M/starter" ~/labE-$t
  (cd ~/labE-$t && git init -q && git add -A && git commit -qm "starter")
done
```

## 會用到的檔案

| 檔案 | 用途 |
| --- | --- |
| `feature_request.md` | 要實作的功能：POST /api/todos |
| `instructor/sample_plan.md` | 參考：Claude Code 產生的計畫 |
| `instructor/verify_labE.sh` | 講師用：自動驗證 plan mode 不改檔、`--worktree` 隔離 |

## Part A：Claude Code

### 1. 進入 plan mode

```bash
cd ~/labE-claude && claude
```

按 Shift+Tab 切換模式，直到狀態列顯示 plan mode（順序：default → acceptEdits → plan → …）。也可以直接輸入 `/plan`，或啟動時加 `--permission-mode plan`。

貼上 `feature_request.md` 的內容。plan mode 下 Claude 只讀檔與提問，不會修改專案。

### 2. 修改計畫

計畫出來後，按 Ctrl+G 在編輯器中修改。至少改一處，例如：

- 標題上限原本若是 200，計畫應包含改成 100
- 指定測試檔名稱，或要求先寫失敗的測試
- 刪掉你認為多餘的步驟（例如順便改文件）

存檔關閉後回到 Claude Code，選擇核准。核准選項中有「Yes, and use auto mode」，本實作請選一般的核准，保留逐步確認。

### 3. 實作並確認

讓 Claude 完成實作，然後自己跑：

```bash
make test
git status --short
```

### 4. 故意走錯，再倒回去

在同一個對話輸入：

```
把 service 層改成直接讀寫 data/todos.json，不要經過 repo 層。
```

這違反分層規則。改完後按兩次 Esc（或輸入 `/rewind`），選擇這個提示之前的 checkpoint，再選「restore code and conversation」。確認：

```bash
git diff --stat      # service 應回到上一版的實作
```

Rewind 的五個選項：

- 程式與對話一起還原
- 只還原對話
- 只還原程式
- 從此處摘要
- 摘要到此處

### 5. Checkpoint 管不到的改動

輸入：

```
用 Bash 執行：echo "# 臨時註記" >> README.md
```

接著再要求 Claude 用編輯工具在 `docs/architecture.md` 末尾加一行。然後 rewind 到這兩步之前，選擇「restore code」。

```bash
git diff --stat
```

`docs/architecture.md` 的修改被還原，`README.md` 的那一行還在：透過 Bash 做的改動不在 checkpoint 範圍內。外部編輯、背景 subagent 的修改也一樣。真正的退路仍然是 git。

### 6. 想比較兩種做法時

`/rewind` 會丟掉後面的內容。如果想保留目前的進度、另開一條路試別的做法，用 `/branch`，或在命令列以 `claude --resume <session ID> --fork-session` 開出新的 Session。

## Part B：Codex

### 7. 規劃

```bash
cd ~/labE-codex && codex
```

輸入 `/plan`，再貼上 `feature_request.md` 的內容。檢查計畫，直接在對話中要求修改（與第 2 步改同樣的地方），確認後再讓它實作。

### 8. 邊做邊問：`/side`

實作進行中想問與主線無關的問題（例如「unittest 的 subTest 怎麼用」），用 `/side` 開暫時的旁支對話，不會污染主線的上下文。

### 9. 分叉對話：`/fork`

在實作完成後輸入 `/fork`，在分出的對話中要求第 4 步那個違反分層的改法。Codex 沒有 checkpoint，對話分叉了，檔案卻是同一份：

```bash
git diff --stat
git restore . && git clean -fd     # 用 git 回到上一次 commit（記得先 commit 好的版本）
```

### 10. 用 worktree 隔離實驗

要讓實驗性的修改完全不碰目前的工作目錄，在 TUI 中用 `/worktree`，或用非互動模式：

```bash
codex exec --worktree -s workspace-write "把 service 層改成直接讀寫 data/todos.json"
git worktree list
git status --short          # 目前的工作目錄沒有變動
```

Codex 在 `$CODEX_HOME/worktrees/` 底下建立獨立的 worktree（detached HEAD），修改都在那裡。

## 比較

| 項目 | Claude Code | Codex |
| --- | --- | --- |
| 進入規劃 | Shift+Tab、`/plan`、`--permission-mode plan` | `/plan` |
| 修改計畫 | Ctrl+G 開編輯器 | 在對話中要求修改 |
| 還原程式 | Checkpoint：Esc Esc、`/rewind`（保留最近 100 個） | 沒有 checkpoint；靠 git |
| 還原範圍的限制 | Bash、外部編輯、背景 subagent 的改動不還原 | — |
| 分叉對話 | `/branch`、`--fork-session` | `/fork` |
| 旁支提問 | — | `/side` |
| 隔離實驗 | worktree（背景 Session 預設用 `.claude/worktrees/`） | `/worktree`、`codex exec --worktree` |

## 觀察重點

- 你在計畫中改掉的那一處，實作有照做嗎？
- 第 5 步之後，哪些檔案被還原、哪些沒有？為什麼？
- `/rewind` 與 `/fork` 都能「回到過去」，各自保留了什麼、丟掉了什麼？
- 如果 Agent 在 Bash 中執行了 `rm`，哪一種退路還救得回來？

## 檢核點

- [ ] 兩邊的 `make test` 都通過，且 `POST /api/todos` 能建立待辦
- [ ] 計畫中至少有一處是你修改過的，並能在程式中找到對應
- [ ] Claude Code：第 4 步成功還原；第 5 步能說明 README.md 為何沒被還原
- [ ] Codex：用 git 或 worktree 讓違反分層的修改不留在主線

## 延伸題

1. 用 `claude -p --permission-mode plan` 只產生計畫，存成檔案交給同學審查，再交回 Claude 實作。
2. 在 Codex 中把第 10 步的 worktree 結果比較後，挑好的一邊合併回主線。
3. 把「先規劃」寫進 CLAUDE.md／AGENTS.md：哪些規模的任務必須先規劃？

## 參考

- Claude Code 權限模式（含 plan mode）：https://code.claude.com/docs/en/permission-modes
- Claude Code checkpoint：https://code.claude.com/docs/en/checkpointing
- Codex 斜線指令：https://learn.chatgpt.com/codex/reference/slash-commands
- Codex 非互動模式（`--worktree`）：https://learn.chatgpt.com/docs/cli/reference
