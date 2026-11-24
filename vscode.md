# 在 VS Code 中進行實作

所有實作都能只用終端機完成；VS Code 是建議的操作環境，把編輯檔案、內建終端機、檢視 Agent 的修改與切換 Agent 集中在同一個視窗。
本文件依 VS Code 官方文件與 1.143 版發行說明整理（2026 年 10 月）。VS Code 的 Agent 功能更新很快，開課前請講師實際操作一次，並對照最新文件。

## 1. 版本與安裝

| 項目 | 內容 |
|---|---|
| VS Code | 1.143 以上（2026 年 10 月的穩定版）。用 `code --version` 確認 |
| Python 擴充套件 | 執行與偵錯 Python、在測試面板跑 pytest |
| AI 功能 | 啟用 VS Code 的 AI 功能並登入 GitHub（使用 Copilot Harness 時需要） |
| OpenAI Codex 擴充套件 | Marketplace ID `openai.chatgpt`，在 VS Code 中使用 Codex Harness |
| Claude Harness | VS Code 內建整合，設定 `github.copilot.chat.claudeAgent.enabled` 控制是否啟用 |

帳號與計費：
- **Claude Harness**：可走 GitHub Copilot 訂閱計費，或自備 Anthropic API Key（由 Anthropic 計費）。同一個 Session 內可在兩種來源的模型間切換。
- **Codex Harness**：透過 Codex 擴充套件時，依該擴充套件的登入方式（ChatGPT 帳號）；實驗性的 Agent Host 整合可用 Copilot Pro+ 或 ChatGPT 帳號登入。
- **不登入 GitHub 使用 Claude**（實驗功能）：把 `ANTHROPIC_API_KEY` 設在環境變數或 `~/.claude/settings.json` 的 `env`，並開啟 `chat.agentHost.allowSignedOutWhenUsable`。

## 2. 三個要分開看的概念：Model、Harness、Host

課程中「模型是大腦、Harness 是雙手雙眼」的觀念，在 VS Code 裡多了一層 Host：

| 層 | 是什麼 | 在 VS Code 中的例子 |
|---|---|---|
| Model | 負責推理的模型 | Claude、GPT 等模型 |
| Harness | 驅動 Agent 的執行框架：準備上下文、呼叫工具、跑 Agent Loop、管理 Session | Copilot（GitHub Copilot SDK）、Claude（Claude Agent SDK）、Codex、Local |
| Host | 承載 Session 的處理程序，讓多個介面連到同一個 Session | Agent Host（獨立處理程序）、Extension Host（舊架構） |

同一個模型放在不同 Harness 裡，行為會不一樣，因為指令格式、可用工具、上下文管理方式都不同。例如在 Copilot Harness 裡選 Claude 模型，和直接選 Claude Harness，是兩種不同的執行方式。

### Chat 的 Session Target

| 選項 | 執行方式 | 特性 |
|---|---|---|
| Copilot | GitHub Copilot SDK，跑在 Agent Host | 新 Session 的預設；關掉資料夾後仍可繼續 |
| Local | VS Code 內建的舊 Harness，跑在 Extension Host | 關掉編輯器視窗就停止；Agents 視窗中不可用 |
| Claude | Anthropic Claude Agent SDK | 沿用 Claude 專案設定與權限模式，保留 slash commands 與 hooks |
| Codex | OpenAI Codex（擴充套件或實驗性 Agent Host 整合） | 每個視窗只會出現一種 Codex 實作 |
| Cloud | 遠端執行，不是 Harness | 需要 GitHub Repo，結果以 Pull Request 回來；沒有本機工具與上下文 |

### Agent Host 帶來的改變
- Agent 從各視窗的 Extension Host 移到獨立的 Agent Host 處理程序。Session 由 Agent Host 擁有，不再綁定某一個視窗。
- 關掉專案資料夾，進行中的工作仍會繼續；重新打開資料夾即可看到進度。本機的 Agent Host 由 VS Code 管理，所以 VS Code 本身必須保持執行。
- 編輯器與 Agents 視窗連到同一個 Session，兩邊同步更新。
- Agent Host 也可在遠端機器執行，從桌面版或瀏覽器查看進度、審查變更。
- 各介面與 Agent Host 之間用開放的 Agent Host Protocol（AHP）同步：主機保存權威狀態，介面先收到快照、再收到有序的動作流，斷線後可補齊錯過的動作。AHP 只統一 Session 的介面，不規定 Agent 如何推理或呼叫工具。

這和安全邊界與腦手解耦單元中 Managed Agents 的設計方向一致：把 Session 狀態和「執行 Agent 的地方」拆開。

## 3. 各實作在 VS Code 中的做法

| 實作 | VS Code 中的做法 |
|---|---|
| 實作 1、2 | 在編輯器寫 `prompts/`、`cases/`；在內建終端機（`` Ctrl+` ``）執行 `run_once.py`、`compare.py`；`results/` 的 Markdown 用預覽開啟 |
| 實作 3 | 在終端機執行 `mini_agent.py` 修 `buggy_shop`，用「原始檔控制」檢視 Agent 改了哪些行；再用 Chat 選 **Claude** Harness 修同一份專案，比較兩者的步驟 |
| 實作 4 | 同一份 `SKILL.md` 放在 `.claude/skills/` 與 `.agents/skills/`；分別在 Chat 選 **Claude**、**Codex** Harness 要求「寫本週週報」，再與 CLI 的結果比較 |
| 拆除實驗 | 終端機執行 `ablation/ablate.py`；CSV 用編輯器開啟或匯入試算表 |
| 實作 5 | 用 Claude Harness 執行 Initializer 與 Coding Agent；開 Agents 視窗觀察 Session，嘗試關掉資料夾再打開，確認工作仍在進行 |
| 實作 6 | Evaluator 需要 Playwright MCP，注意下一節的 MCP 設定位置；`make lint` 的錯誤訊息可直接點檔名跳到違規的行 |
| 實作 7 | 編輯 `.claude/settings.json` 與 `.codex/hooks.json` 時有 JSON 語法提示；在 VS Code 的 Claude、Codex Harness 中重做「推送到 main」的測試，確認 Hook 是否同樣生效 |

## 4. MCP 與工具設定：不同 Harness 位置不同

| Harness | 工具與 MCP 設定方式 |
|---|---|
| Local | Chat 輸入框旁的「Configure Tools」，設定只對該次請求有效；MCP 設定檔為 `.vscode/mcp.json` |
| Copilot | `F1` → `Chat: Open Customizations` → Tools；設定存在目前的 VS Code Profile。新增 MCP Server 用 `MCP: Add Server`。全域設定檔預設為 `~/.copilot/mcp-config.json` |
| Claude | 沿用 Claude 專案設定（`CLAUDE.md`、`.claude/settings.json` 等） |
| Codex | 沿用 Codex 設定（`AGENTS.md`、`~/.codex/config.toml` 等） |

切換 Harness 後，不要假設工具已經可用：先請 Agent 列出可用工具，或直接呼叫一次確認。目前 Copilot Harness 無法像 Local 一樣逐一開關某些 MCP Server 的個別工具（VS Code Issue #341962）。

## 5. 權限與沙箱

- **Claude Harness**：在 Chat 輸入框選權限模式：自動編輯、要求核准、先規劃（Plan）。設定 `github.copilot.chat.claudeAgent.allowDangerouslySkipPermissions` 會略過所有權限檢查，只能在隔離、無網路的環境使用。
- **Codex Harness**：使用 Codex 的核准預設。
- **終端機沙箱**：Session 的權限選單中有「Sandboxing for terminal」開關；企業可用 `permissions.deny`、`sandbox.enabled` 統一管理。
- 課程中 Hook、deny 規則、沙箱的實測都在 CLI 完成。在 VS Code 中是否表現相同，請在實作 7 自行驗證並記錄。

## 6. 已知限制
- 本機 Agent Host 需要 VS Code 持續執行；完全關閉 VS Code，Session 會停止。
- Codex 在 Agent Host 上的整合仍是實驗功能。
- Copilot Harness 無法使用所有內建工具與擴充套件工具。
- 在企業管理設定下，Claude、Codex Harness 可能被停用。

## 參考資料
- VS Code 1.143 Release Notes：https://code.visualstudio.com/updates
- Introducing the Agent Host for persistent, portable agent sessions（VS Code 官方部落格，2026-08-26）：https://code.visualstudio.com/blogs/2026/08/26/agent-host-architecture
- Choose and use an agent harness：https://code.visualstudio.com/docs/agents/run/agent-harnesses
- Using third-party agents in VS Code：https://code.visualstudio.com/learn/agents/4-using-third-party-agents-in-vs-code
- 延伸閱讀：〈VS Code Agent Host 新架構〉，studyhost：https://article.studyhost.com.tw/Articles/VS%20Code%20Agent%20Host%20%E6%96%B0%E6%9E%B6%E6%A7%8B.html
