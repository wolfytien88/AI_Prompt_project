# 實作 C 驗證紀錄（2026-10-30）

環境：Claude Code 2.1.312（真實模型）、Codex CLI 0.165.0（模擬 Responses API）。專案由 `make_repo.sh` 建立，複製 `instructor/ref/`；`python3 -m pytest -q` → 1 passed。

## Claude Code（真實模型）
1. 第 3 步指令（`--allowedTools "Agent,Read,Grep,Glob,Edit(REVIEW.md)"`）→ stream-json 有三筆 Agent 呼叫，`subagent_type` 為 security-reviewer、test-reviewer、perf-reviewer；主 Agent 合併成 160 行的 REVIEW.md（原始 24 項 → 合併 20 項），涵蓋 `instructor/ANSWER.md` 全部 11 項。成本 0.285 美元、8 輪。範例存於 `instructor/sample_REVIEW_claude.md`。
2. 早先一次以空白分隔並寫 `Write(REVIEW.md)` 的執行：三個子 Agent 正常回報，但寫入 REVIEW.md 被拒絕；改用 `Edit(REVIEW.md)` 後成功。
3. 第 5 步對照組（單一 Agent）→ REVIEW_single.md 133 行，成本 0.152 美元、7 輪，涵蓋的問題與平行版相近。
4. 子 Agent 在背景執行：第一次執行的 stream-json 出現多個 result 事件（「已派出」→「安全審查員已回報」→…→ 最終合併）。

## Codex（模擬伺服器，Codex 本身真實執行）
5. `codex exec --cd member-service "Spawn one subagent for security risks…"` → 送出的工具清單含 `multi_agent_v1`，其說明的 Available roles 列出 perf-reviewer（附註 reasoning effort 固定為 low）、security-reviewer、test-reviewer，以及內建 default、explorer。

## 尚未驗證
- 真實 GPT 模型實際派出三個子 Agent 並合併的結果。
- `codex -s read-only` 下子 Agent 的實際行為（只確認文件記載子 Agent 繼承沙箱）。
