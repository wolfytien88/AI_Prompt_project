# 專題實作：設計一個可運作、可量測、有安全防護的 Harness

> 在 VS Code 中操作本實作的方式，見 [`../vscode.md`](../vscode.md)。

3–4 人一組，整合全課程內容，交出一個 Harness，並用 Claude Code 與 Codex 各跑一次。

## 題庫（擇一，也可自訂）

| 題目 | 任務 | 建議驗證方式 | 主要風險 |
| --- | --- | --- | --- |
| A 網頁 App 生成 | 依 1–4 句需求做出可用的小型網頁 App | 功能清單＋Playwright MCP 實測 | 宣告完成過早、推送到 main |
| B 文件自動整理 | 把一個資料夾的文件分類、改名、產出索引 | 檢查檔名規則與索引完整性的腳本 | 誤刪或覆蓋原始檔案 |
| C 資料清理與報表 | 清理 CSV 並產出固定格式的週報 | 欄位、筆數、數值的確定性檢查 | 讀到含個資或金鑰的檔案 |
| D 知識庫問答 | 依內部文件回答問題，附引用來源 | Eval 測試集，檢查引用是否正確 | 文件中藏 Prompt Injection |

**自訂題目的條件**：有明確的完成定義、能寫出自動驗證、至少有一個不可逆或高風險動作需要防護，且資料可在課堂上公開使用（去識別化）。

## 五個必要元件

| 元件 | 要求 | 交付物 |
| --- | --- | --- |
| 1. 規格 | 由 Planner 產生或人工撰寫，寫明完成定義 | `spec.md` 與 `AGENTS.md`（或 `CLAUDE.md`） |
| 2. 工具 | 以通用工具為主，必要時加 Skill 或 MCP | 工具清單與選擇理由 |
| 3. 狀態檔 | 新的上下文能從檔案接手工作 | `feature_list.json`、進度檔、git 紀錄 |
| 4. 驗證 | Evaluator 或機械化檢查，至少一種 | Eval 測試集與分數、Lint 或測試腳本 |
| 5. 安全 | 至少一個 Hook，並通過紅隊測試 | Hook 腳本、設定檔、紅隊測試紀錄 |

同一個 Repo 要能讓兩套工具都跑起來：`CLAUDE.md` 只寫一行 `@AGENTS.md` 共用規則；Skill 同時放在 `.claude/skills/` 與 `.agents/skills/`；Hook 腳本同時註冊到 `.claude/settings.json` 與 `.codex/hooks.json`，並完成 Codex 的專案信任與 `/hooks` 審查。

## 發表內容

1. **完整執行示範**：從規格到驗證通過跑一次；可預先錄好備用。
2. **Eval 分數**：Claude Code 與 Codex 各自的分數，以及差異最大的題目。
3. **拆除實驗**：拿掉哪個元件分數會下降、哪個拿掉也沒差，附數字。
4. **紅隊測試結果**：用了哪些攻擊、哪一層擋下、有沒有漏網之魚。
5. **兩套工具的差異**：設定、行為與結果的差異，以及這個題目適合哪一套。

**互評**：每組依 `rubric.md` 的互評表為其他組評分，並各提一個改進建議。

## 評量比重

| 項目 | 比重 | 評分重點 |
| --- | --- | --- |
| 課堂實作 | 30% | 實作 1–7 是否完成並可執行 |
| 各單元產出 | 30% | Prompt 模板庫與 Eval、mini_agent 與 Skill、長任務狀態檔與 Evaluator、Hook 設定 |
| 專題實作 | 40% | 五個必要元件、Eval 分數、拆除實驗、紅隊測試、兩套工具比較、發表清晰度 |

分數高不一定好。能說清楚「哪個元件為什麼存在、拿掉會怎樣」、紅隊測試誠實列出沒擋住的情況，比單純高分更重要。

## 交付清單

```text
專題 Repo/
├── AGENTS.md                 # 約 100 行的目錄：架構、規則、啟動與測試指令、完成定義
├── CLAUDE.md                 # 只寫一行：@AGENTS.md
├── spec.md                   # 規格與完成定義
├── feature_list.json         # 功能清單，每項含 passes 欄位
├── claude-progress.txt       # 進度檔
├── init.sh                   # 啟動環境
├── .claude/
│   ├── settings.json         # deny 規則與 Hook
│   ├── hooks/guard.py
│   └── skills/<名稱>/SKILL.md
├── .agents/skills/<名稱>/SKILL.md
├── .codex/
│   ├── hooks.json
│   ├── hooks/guard.py
│   └── config.toml           # sandbox_mode、approval_policy
├── evals/
│   ├── cases.json            # 測試集
│   └── eval.py               # 自動評分
└── reports/
    ├── ablation.md           # 拆除實驗紀錄
    ├── redteam.md            # 紅隊測試紀錄
    └── comparison.md         # Claude Code 與 Codex 比較
```

另交：發表簡報（或錄影連結）、`harness_checklist.md` 自評結果。
