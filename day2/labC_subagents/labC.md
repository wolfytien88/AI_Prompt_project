# 實作 C：用子 Agent 平行審查程式

> 在 VS Code 中操作本實作的方式，見 [`../../vscode.md`](../../vscode.md)。

## 目的

- 定義三個專職審查員：安全、測試、效能。每個都有自己的指示、可用工具與模型。
- 讓主 Agent 同時派出三個審查員，再把結果合併成一份去重、排序過的報告。
- 體會子 Agent 的好處：每個審查員有獨立的 Context，主對話只收到結論，不會塞滿讀檔過程。也要看到代價：Token 用量增加。
- 比較 Claude Code（Markdown）與 Codex（TOML）的子 Agent 定義方式與權限繼承。

## 形式

個人或兩人一組。

## 前置

| 項目 | 指令或說明 |
| --- | --- |
| 練習專案 | `bash make_repo.sh ~/lab/member-service`：虛構的會員服務，刻意留下安全、測試與效能問題 |
| 參考答案 | `instructor/ref/`（審查員設定）、`instructor/ANSWER.md`（埋了哪些問題，先不要看） |

練習專案：

```
member-service/
├── member_service/store.py    SQLite 存取、密碼雜湊
├── member_service/export.py   匯出 CSV、去重、各等級計數
└── tests/test_export.py       只有一個測試
```

## 步驟

### Part 1：Claude Code

1. 建立 `.claude/agents/security-reviewer.md`：

   ```markdown
   ---
   name: security-reviewer
   description: 安全審查專家。檢查注入（SQL、指令）、密碼與金鑰處理、路徑走訪等問題。程式碼審查時使用，只讀不改。
   tools: Read, Grep, Glob
   model: sonnet
   ---
   你是資安審查員，只負責安全問題，不評論風格、測試或效能。
   1. 讀取指定的檔案，追蹤使用者可控制的輸入流到哪裡。
   2. 檢查：SQL 字串組合、os.system／subprocess 的 shell 字串、雜湊演算法與加鹽、檔案路徑組合。
   3. 每個問題輸出一行：[高|中|低] 檔案:行號 — 問題 — 建議修正。
   最後一行寫「安全問題共 N 項」。
   ```

   | 欄位 | 作用 |
   | --- | --- |
   | `name`、`description` | 必填。description 決定主 Agent 什麼時候會派它 |
   | `tools` | 只給讀取類工具，審查員無法改檔 |
   | `model` | 可依工作難度選 `sonnet`、`haiku`、`opus` 或 `inherit` |

2. 依同樣格式建立 `test-reviewer.md`（找沒測到的函式、缺少的邊界案例、修改全域狀態的測試）與 `perf-reviewer.md`（找重複查詢、O(n²) 迴圈、一次載入全部資料；`model: haiku`）。

3. 派出三個審查員並合併：

   ```bash
   claude -p "請同時派出 @agent-security-reviewer、@agent-test-reviewer、@agent-perf-reviewer 三個審查員，平行審查 member_service/ 與 tests/。全部回來後，合併成一份 REVIEW.md：依嚴重度排序、重複的問題合併、每項標明是哪個審查員找到的。不要修改程式。" \
     --allowedTools "Agent,Read,Grep,Glob,Edit(REVIEW.md)" \
     --output-format stream-json --verbose > review.jsonl
   ```

   - `@agent-<名稱>` 保證交給指定的子 Agent。
   - 互動模式下子 Agent 預設在背景執行，主對話會先回「已派出」，結果回來後再合併。

4. 在 `review.jsonl` 找三筆 `"name":"Agent"` 的工具呼叫，確認 `subagent_type` 分別是三個審查員；最後一行 `result` 的 `total_cost_usd` 記下來。

5. 對照組：不用子 Agent，讓主 Agent 自己做完同樣的審查：

   ```bash
   claude -p "審查 member_service/ 與 tests/ 的安全、測試與效能問題，寫成 REVIEW_single.md。不要修改程式。" \
     --allowedTools "Read,Grep,Glob,Edit(REVIEW_single.md)" --output-format json > single.json
   ```

   比較兩份報告找到的問題數、成本，以及主對話的 Context 大小。

### Part 2：Codex

6. 建立 `.codex/agents/security-reviewer.toml`：

   ```toml
   name = "security-reviewer"
   description = "安全審查專家。檢查注入（SQL、指令）、密碼與金鑰處理、路徑走訪等問題。程式碼審查時使用，只讀不改。"
   developer_instructions = """
   你是資安審查員，只負責安全問題，不評論風格、測試或效能。
   ……（同 Part 1）
   不要修改任何檔案。最後一行寫「安全問題共 N 項」。
   """
   ```

   - 必填 `name`、`description`、`developer_instructions`。辨識用的是 `name`，不是檔名。
   - 可選 `model`、`model_reasoning_effort`；效能審查員可設 `model_reasoning_effort = "low"`。

7. 依同樣格式建立 `test-reviewer.toml`、`perf-reviewer.toml`。

8. 用唯讀沙箱派出三個審查員：

   ```bash
   codex -s read-only "Spawn three subagents in parallel: security-reviewer, test-reviewer and perf-reviewer. Each reviews member_service/ and tests/. Merge their findings into one report sorted by severity, de-duplicated, and note which reviewer found each item."
   ```

   Codex 的子 Agent 繼承主 Agent 的沙箱與核准設定，agent 檔不能自己設定 `sandbox_mode` 或 `approval_policy`。所以要讓審查員「只讀」，是從主 Agent 用 `-s read-only` 限制。

9. 對照 `instructor/ANSWER.md`，兩家各找到幾項？漏掉哪些？

## 觀察重點

- 子 Agent 的價值在 Context 隔離：三個審查員各自讀檔、推理，主對話只拿到三份結論。
- 代價是 Token：三個審查員各自讀了一次同樣的檔案。驗證時（Claude Code、真實模型）平行審查約 0.29 美元，單一 Agent 對照組約 0.15 美元，兩份報告涵蓋的問題相近。專案這麼小時，子 Agent 不划算；專案越大、主對話越需要保留 Context 給後續工作，子 Agent 的價值越明顯。
- 角色越專一，越不容易互相干擾。可以試著把三個審查員合成一個，看報告是否變得籠統。
- 審查員限制工具的方式不同：Claude Code 在 agent 檔用 `tools` 限制，Codex 由主 Agent 的沙箱決定。

## 檢核點

- [ ] stream-json 中有三筆 Agent 呼叫，對應三個審查員
- [ ] REVIEW.md 依嚴重度排序，每項標明找到者，重複項目已合併
- [ ] 至少找到 SQL 注入、指令注入、MD5、O(n²) 去重、重複全表掃描、只驗證檔案存在的測試
- [ ] Codex 的三個 `.toml` 能被辨識（主 Agent 的角色清單出現三個名稱）
- [ ] 能說明為什麼 Codex 審查員要靠 `-s read-only` 才能保證不改檔

## 兩家對照

| 面向 | Claude Code | Codex |
| --- | --- | --- |
| 定義檔 | `.claude/agents/<名稱>.md`（Markdown＋frontmatter） | `.codex/agents/<名稱>.toml` |
| 必填 | `name`、`description` | `name`、`description`、`developer_instructions` |
| 限制工具 | `tools`、`disallowedTools` | 繼承主 Agent 的沙箱；可用 `features.shell_tool=false` 等功能開關 |
| 指定模型 | `model: sonnet／haiku／opus／inherit` | `model`、`model_reasoning_effort` |
| 指定派給誰 | `@agent-<名稱>` | 在提示中點名角色 |
| 內建角色 | Explore、Plan、general-purpose 等 | `default`、`worker`、`explorer` |
| 執行方式 | 預設在背景，最多 3 層巢狀 | 平行執行後合併；`[agents] max_concurrent_threads_per_session` |

## 延伸題

1. 在 security-reviewer 加上 `isolation: worktree` 與 `Edit` 工具，讓它在獨立的 worktree 直接修好 SQL 注入，再比較修改。
2. 用 `claude --agent security-reviewer` 讓整個 Session 以審查員身分執行。
3. 在 Codex 的 `~/.codex/config.toml` 設 `[agents] default_subagent_model`，讓子 Agent 改用較便宜的模型，比較成本。

## 沒有 API 金鑰時

Claude Code 部分需要模型。Codex 部分可用模擬伺服器（`../../mock/mock_responses.py`）確認三個角色被辨識：Codex 送出的工具清單中有 `multi_agent_v1`，其說明的「Available roles」會列出三個審查員與它們的 description。做法見 `VERIFY.md`。

## 參考

- Claude Code：Subagents https://code.claude.com/docs/en/sub-agents.md
- Codex：Subagents https://learn.chatgpt.com/codex/agent-configuration/subagents
