# 實作 6：Evaluator ＋ 機械化約束

> 在 VS Code 中操作本實作的方式，見 [`../vscode.md`](../vscode.md)。

## 目的

為實作 5 的待辦清單 App 加上兩種品質把關：用自訂 Lint 把分層規則寫成會擋人的程式，以及用獨立的 Evaluator 依 Rubric 實測成果。最後讓 Claude Code 與 Codex 各跑一次同一個任務，比較兩種把關方式與兩套工具。

## 前置

- 完成實作 5 的專案 `~/lab5-todo`（沒有完成時，見 Part B 的「從參考答案建立」）
- Node.js 18 以上（Playwright MCP 需要）
- 教材路徑：`export M=/你的路徑/範例程式/day3`

## 會用到的檔案

| 檔案 | 用途 |
| --- | --- |
| `$M/layer_demo/` | 分層檢查示範，含一個故意違規的檔案 |
| `$M/harness/` | 要加進專案的 AGENTS.md、CLAUDE.md、Makefile、tools/check_layers.py |
| `$M/prompts/evaluator.md` | Evaluator 指令 |
| `$M/rubric.md` | 評分標準與門檻 |

## Part A：分層檢查示範

```bash
cp -r "$M/layer_demo" ~/layer-demo && cd ~/layer-demo
make test     # OK：程式能跑
make lint     # 失敗
```

`make lint` 的輸出：

```
ERROR：service 層不可依賴 ui 層： src/service/report_service.py
修正方式：把共用型別移到 src/types/，或改由 ui 層呼叫 service。
```

依錯誤訊息修正：

1. 新增 `src/types/text.py`，把 `format_title` 移過來：

   ```python
   """types 層：純文字格式化。"""


   def format_title(title: str, done: bool) -> str:
       """完成的項目在標題前加上 [完成]。"""
       return f"[完成] {title}" if done else title
   ```

2. `src/service/report_service.py` 的 import 改成：

   ```python
   from src.types.text import format_title
   ```

3. `src/ui/formatting.py` 刪掉自己的 `format_title`，改為：

   ```python
   from src.types.text import format_title
   ```

4. 重新檢查：

   ```bash
   make check    # lint 與 test 都通過
   ```

討論：修正前 `make test` 就已經通過了。測試證明程式能跑，Lint 才證明架構沒被破壞。

也可以不自己改，直接對 Agent 說「執行 make lint 並修正問題」，觀察它是否照錯誤訊息裡的修正方式處理。

## Part B：把機械化約束加進專案

```bash
cd ~/lab5-todo
cp "$M/harness/AGENTS.md" "$M/harness/CLAUDE.md" "$M/harness/Makefile" .
cp "$M/harness/tools/check_layers.py" tools/
make lint          # 通過（沒有違規）
make check         # lint 與 test 都通過
make status        # 功能清單通過數與需求快照比對
git add -A && git commit -m "加入 AGENTS.md、CLAUDE.md 與 make lint"
```

- `AGENTS.md` 是約 10 行的目錄，指向各份文件，並寫明完成定義。
- `CLAUDE.md` 只有一行 `@AGENTS.md`，讓 Claude Code 與 Codex 讀同一套規則。

**從參考答案建立**（實作 5 沒有完成時）：

```bash
mkdir -p ~/lab5-todo && cp -r "$M/starter/." ~/lab5-todo/ && cd ~/lab5-todo
cp "$M/spec.md" "$M/examples/feature_list.json" "$M/examples/claude-progress.txt" "$M/examples/init.sh" .
chmod +x init.sh
python3 tools/feature_status.py --save-baseline
git init && git add -A && git commit -m "從參考答案建立"
```

接著回到 Part B 開頭的指令。

## Part C：Evaluator

### 1. 安裝 Playwright MCP

Claude Code：

```bash
claude mcp add playwright -- npx @playwright/mcp@latest
```

Codex：

```bash
codex mcp add playwright -- npx @playwright/mcp@latest
```

在 Linux 以 root 執行（例如雲端容器）時，Chromium 沙箱會啟動失敗，要在指令最後加上 `--no-sandbox`；沒有螢幕的環境加上 `--headless`。

### 2. 執行 Evaluator

```bash
cd ~/lab5-todo
cp "$M/rubric.md" .
./init.sh
claude -p "$(cat "$M/prompts/evaluator.md")" --allowedTools Bash Read Write "mcp__playwright__*"
```

Codex：

```bash
codex exec -s workspace-write "$(cat "$M/prompts/evaluator.md")"
```

Evaluator 必須在新的上下文中執行，不能在剛寫完程式的同一段對話裡請它評分。

### 3. 讀 evaluation.md

- 判定是否依「任一項低於門檻即不通過」，而不是平均分數？
- 每個缺陷是否都有重現步驟、預期結果、實際結果？
- `git status` 確認 Evaluator 沒有修改任何程式或 feature_list.json。

在只完成少數功能的專案上，預期結果是「不通過」：功能完整度可能拿高分（標為通過的都可用），但產品深度會低於門檻。

## Part D：兩套工具與自評的比較

1. 建立兩個分支，各交給一套工具跑一個 Coding Session：

   ```bash
   git switch -c try-claude
   claude -p "$(cat "$M/prompts/coding_agent.md")" --allowedTools Bash Read Write Edit "mcp__playwright__*"
   git switch -
   git switch -c try-codex
   codex exec -s workspace-write "$(cat "$M/prompts/coding_agent.md")"
   ```

2. 在每個分支上，先請 Generator 自評，再請 Evaluator 評分：

   ```bash
   claude -p "依 rubric.md 為這個專案目前的成果打分，格式與 prompts/evaluator.md 的輸出相同，寫入 self_evaluation.md。" --allowedTools Read Write
   claude -p "$(cat "$M/prompts/evaluator.md")" --allowedTools Bash Read Write "mcp__playwright__*"
   ```

   > `claude -p` 在沒有指定權限模式時，遇到需要確認的動作會直接拒絕，所以每個指令都要用 `--allowedTools` 列出允許的工具（或加 `--permission-mode acceptEdits`）。

3. 填寫比較表：

| 分支 | 完成的項目 | make lint | make test | 自評總判定 | Evaluator 總判定 | 分數差最大的標準 |
| --- | --- | --- | --- | --- | --- | --- |
| try-claude | | | | | | |
| try-codex | | | | | | |

## 預期結果

- `layer_demo` 修正前 `make lint` 失敗、修正後 `make check` 通過。
- 專案的 `make lint`、`make test` 通過，AGENTS.md 與 CLAUDE.md 已 commit。
- evaluation.md 有四項分數、判定與缺陷清單；自評分數通常高於 Evaluator。

## 檢核點

- [ ] 能說明為什麼 `make test` 通過時 `make lint` 仍可能失敗
- [ ] Lint 錯誤訊息包含修正方式，Agent 或學員能照著修
- [ ] Evaluator 在獨立的上下文中執行，且沒有修改任何檔案
- [ ] 判定依門檻，不依平均
- [ ] 比較表已填完，並能指出自評與 Evaluator 落差最大的標準

## 延伸題

1. 擴充 `check_layers.py`：再加一條「repo 不可依賴 service」，錯誤訊息同樣附修正方式。
2. 依 `rubric.md` 最後的「校正」一節，挑兩份成果比較 Evaluator 與你自己的評分，把差距最大的標準改寫進 `evaluator.md`，再跑一次看分數是否更接近。
3. 用 `prompts/planner.md` 把一句新需求（例如「加上分類標籤」）擴寫成規格，再交給 Initializer 產生新的功能清單。
