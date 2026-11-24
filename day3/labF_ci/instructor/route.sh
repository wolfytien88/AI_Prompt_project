#!/bin/bash
# 參考答案：依分析結果決定通知對象；pass 不輸出
# 用法：./route.sh out/claude_ci_01_assert.json
jq -r 'select(.status != "pass")
       | "[\(.status)] 通知 \(.suggested_owner)：\(.failed_tests | join(", ") | if . == "" then "（無失敗測試）" else . end)\n  原因：\(.root_cause)\n  下一步：\(.next_step)"' "$1"
