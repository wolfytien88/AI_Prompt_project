#!/bin/bash
# 不需模型：用假的 Hook 輸入測 guard.py
t(){ printf '%-40s' "$1"; echo "{\"tool_input\":{\"command\":\"$1\"}}" | python3 "$(dirname "$0")/guard.py" 2>/dev/null; r=$?; [ $r = $2 ] && echo "OK (exit $r)" || echo "失敗：exit $r，預期 $2"; }
t "git push origin main" 2; t "git push -u origin master" 2; t "git push origin HEAD:main" 2
t "git push origin feature/main-menu" 0; t "git push origin maintenance-fix" 0
t "rm -rf /" 2; t "rm -rf ~" 2; t "rm -rf /tmp/build" 0; t "ls -la" 0
