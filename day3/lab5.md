# 實作 5：跨 Session 的長任務

> 在 VS Code 中操作本實作的方式，見 [`../vscode.md`](../vscode.md)。

## 目的

用「Initializer Agent ＋ Coding Agent」的雙 Agent 架構開發待辦清單 App，連跑 3 個 Coding Session，每次都開新的上下文，觀察 Agent 能否只靠檔案（功能清單、進度檔、git）正確接手。

## 前置

- Python 3.10 以上、git、make、curl
- Claude Code 或 Codex CLI 其中一套（兩套都有更好）
- 選用：Playwright MCP，讓 Agent 用瀏覽器驗證（設定方式見 lab6.md 的 Part C；沒有時 Agent 會改用 curl 驗證，並在進度檔註明）
- Windows 請在 WSL 中操作

先設定教材路徑，之後的指令都會用到：

```bash
export M=/你的路徑/範例程式/day3
```

## 會用到的檔案

| 檔案 | 用途 |
| --- | --- |
| `$M/starter/` | 起始專案：已有健康檢查 API、列出待辦 API、會顯示清單的首頁 |
| `$M/spec.md` | 產品規格（Planner 的輸出範例） |
| `$M/prompts/initializer.md` | Session 1 使用的指令 |
| `$M/prompts/coding_agent.md` | Session 2 之後每次使用的指令 |
| `$M/examples/` | 參考答案：feature_list.json、claude-progress.txt、init.sh |

## 步驟

### 1. 建立專案

```bash
mkdir -p ~/lab5-todo
cp -r "$M/starter/." ~/lab5-todo/
cp "$M/spec.md" ~/lab5-todo/
cd ~/lab5-todo
make test
```

`make test` 應顯示 `Ran 3 tests` 與 `OK`。

### 2. Session 1：Initializer

Claude Code：

```bash
claude -p "$(cat "$M/prompts/initializer.md")" --allowedTools Bash Read Write Edit
```

Codex：

```bash
codex exec -s workspace-write "$(cat "$M/prompts/initializer.md")"
```

也可以開互動模式（`claude` 或 `codex`），把 `initializer.md` 的內容貼上。

### 3. 檢查 Initializer 的產出

```bash
ls                                        # 應出現 feature_list.json、init.sh、claude-progress.txt
python3 tools/feature_status.py           # 功能總數約 20–30 項，已通過 0
python3 tools/feature_status.py --check-baseline   # PASS：需求快照已建立
./init.sh                                 # 伺服器已啟動：http://localhost:5173
make smoke                                # PASS 基本端對端檢查通過
git log --oneline                         # 一個 commit
```

用瀏覽器開 http://localhost:5173，應看到「待辦清單」與空狀態文字。

把 Agent 的 `feature_list.json` 與 `$M/examples/feature_list.json` 對照：拆法不必相同，但每項都要是使用者看得到的行為、要有測試步驟、passes 全部是 false。

### 4. Session 2–4：Coding Agent

每個 Session 都要開新的上下文。非互動模式每次執行就是新的上下文；互動模式請先離開再重新啟動，不要在同一段對話裡接著做。

Claude Code：

```bash
claude -p "$(cat "$M/prompts/coding_agent.md")" --allowedTools Bash Read Write Edit
```

Codex：

```bash
codex exec -s workspace-write "$(cat "$M/prompts/coding_agent.md")"
```

每個 Session 結束後檢查：

```bash
git log --oneline -3                              # 多一個 commit，訊息寫明完成哪一項
python3 tools/feature_status.py --check-baseline  # 必須 PASS
tail -15 claude-progress.txt                      # 新增一段 Session 紀錄
make test && make smoke                           # 都通過
```

### 5. 記錄交接情形

| Session | 選了哪一項 | 有沒有先跑開場五步驟 | 驗證方式（瀏覽器／curl） | passes 改了幾項 | check-baseline | 交接問題 |
| --- | --- | --- | --- | --- | --- | --- |
| 2 | | | | | | |
| 3 | | | | | | |
| 4 | | | | | | |

## 預期結果

- 3 個 Coding Session 後，通過數約 3–5 項，git log 有 4 個 commit。
- 每個 Session 只完成一項，且 passes 只在實際驗證後才改為 true。
- 進度檔每段都有「完成、測試、發現、下一步」，新 Session 的第一個動作是讀這份檔案。

## 檢核點

- [ ] feature_list.json 每項都有 category、description、steps、passes
- [ ] init.sh 重複執行不會啟動第二個伺服器
- [ ] 每個 Session 後 `--check-baseline` 都是 PASS
- [ ] 沒有一個 Session 同時完成多項功能
- [ ] 進度檔記錄了未修的問題，而不是只寫做完的事

## 常見問題

| 狀況 | 處理方式 |
| --- | --- |
| 5173 埠號被占用 | `PORT=5174 ./init.sh`，並告訴 Agent 改用新網址 |
| check-baseline 失敗 | Agent 改了需求。用 `git diff feature_list.json` 找出改動，退回後在下個 Session 指令中再強調規則 |
| Agent 一次做很多項 | 正常的失敗模式之一，記錄下來，討論哪一段指令沒有擋住 |
| 想重來 | `make stop`，刪除專案資料夾，從步驟 1 重新開始 |

## 延伸題

1. 故意不給 Initializer：直接把 `coding_agent.md` 交給一個空專案，觀察會出現哪一種失敗模式。
2. 把 `feature_list.json` 改成 Markdown 清單再跑一次，比較 Agent 是否更容易改動需求。
3. 刪掉 `coding_agent.md` 中「先跑 smoke_test 與 make test」那一步，故意在程式中留一個 bug，觀察下一個 Session 是否發現。
