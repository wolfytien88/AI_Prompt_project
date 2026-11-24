# 實作 F 驗證紀錄（2026-10-29／30，Claude Code 2.1.312、Codex CLI 0.165.0）

## 已實際執行
| 項目 | 結果 |
| --- | --- |
| `triage_claude.sh` × 4 份記錄（真實模型） | 全部輸出符合 Schema 的 JSON（`instructor/sample_out/`）。01→fail/code_bug、02→infra_error/environment、03→fail 並在 root_cause 註明「記錄中含可疑指示」且 next_step 寫明不要執行 curl、04→pass |
| `--json-schema` 的結果位置 | 在 `--output-format json` 的 `.structured_output` |
| `triage_codex.sh`（假伺服器） | Codex 以 `text.format = {type: json_schema, strict: true, name: codex_output_schema}` 送出 Schema；`-o` 檔只含最後一則訊息；進度輸出在 stderr。見 `instructor/verify_codex_mock.sh`（「結果：通過」） |
| `instructor/route.sh` | 對 4 份參考輸出正確分派，pass 不輸出 |
| workflow YAML | 兩份皆可被 PyYAML 解析；`review_schema.json` 為合法 JSON |

## 尚未驗證
- 真實 GPT 模型對四份記錄的判斷（本環境無 OpenAI 金鑰；假伺服器的回覆是固定內容）
- 兩份 workflow 在 GitHub Actions 上的實際執行（本環境沒有 GitHub repo）。課前請在練習 repo 跑一次，特別確認：
  - claude-code-action 的自動化模式能用 `gh pr comment` 留言（`--allowedTools` 中已列 `Bash(gh pr comment *)`）
  - codex-action 的 `codex-args: --output-schema ...` 與 `final-message` 輸出能被第二個 job 的 `JSON.parse` 讀取
- 延伸題的 `codex review --base main`、`@codex review`
