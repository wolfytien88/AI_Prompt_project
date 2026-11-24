# 安全邊界、腦手解耦與專題實作｜範例與實作教材

| 檔案 | 用途 | 對象 |
| --- | --- | --- |
| `lab7.md` | 實作 7 完整步驟、預期結果、檢核點、延伸題 | 學員 |
| `traps.md` | 三個安全陷阱的重現步驟與實測結果 | 學員、講師 |
| `capstone.md` | 專題實作題庫、必要元件、發表、評量、交付清單 | 學員 |
| `harness_checklist.md` | Harness 檢核清單（專題自評用） | 學員 |
| `rubric.md` | 專題評分表、互評表、實作 7 紀錄表 | 講師、學員 |
| `guard.py` | 兩家共用的守門腳本 | 學員 |
| `test_guard.sh` | 不靠模型測試 guard.py | 學員 |
| `claude_settings.json` | 複製為 `.claude/settings.json` | 學員 |
| `codex_hooks.json` | 複製為 `.codex/hooks.json` | 學員 |
| `codex_config.toml` | 複製為 `.codex/config.toml` | 學員 |
| `redteam/README.md` | 紅隊測試用 README（HTML 註解藏有惡意指令） | 學員 |
| `redteam/env.example` | 假的 .env 內容（只有假金鑰） | 學員 |
| `claude_check/run_claude_check.sh` | 用真實 Claude Code 驗證 Hook、deny 規則、陷阱 2、紅隊 README | 講師課前驗證 |
| `codex_check/run_codex_check.sh` | 用模擬 Responses API 驗證 Codex 的 Hook 信任與沙箱（陷阱 1、3） | 講師課前驗證 |
| `codex_check/mock_codex.py` | 上一支腳本使用的假 Responses API | 講師課前驗證 |

講師課前驗證：

```bash
bash test_guard.sh
bash claude_check/run_claude_check.sh     # 需已登入 claude CLI，會消耗少量用量
bash codex_check/run_codex_check.sh       # 需 codex CLI，不需 OpenAI 連線
```
