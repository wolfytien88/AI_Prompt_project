import json
from pathlib import Path
from llm import call

BASE_DIR = Path(__file__).resolve().parent
cases = json.loads((BASE_DIR / "cases.json").read_text(encoding="utf-8"))
# cases.json 格式：[{"input": "...", "must_include": ["關鍵字1", "關鍵字2"]}]
prompt = (BASE_DIR / "prompt_v2.txt").read_text(encoding="utf-8")

passed = 0
for c in cases:
    text = call("openai", prompt, c["input"])
    ok = all(k in text for k in c["must_include"])
    passed += ok
    print("PASS" if ok else "FAIL", c["input"][:30])
print(f"通過 {passed}/{len(cases)}")
