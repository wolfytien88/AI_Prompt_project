import json
from openai import OpenAI

client = OpenAI()
MODEL = "gpt-5"  # 依上課當下可用的模型調整
cases = json.load(open("cases.json", encoding="utf-8"))
# cases.json 格式：[{"input": "...", "must_include": ["關鍵字1", "關鍵字2"]}]
prompt = open("prompt_v2.txt", encoding="utf-8").read()

passed = 0
for c in cases:
    r = client.responses.create(model=MODEL, instructions=prompt, input=c["input"])
    text = r.output_text
    ok = all(k in text for k in c["must_include"])
    passed += ok
    print("PASS" if ok else "FAIL", c["input"][:30])
print(f"通過 {passed}/{len(cases)}")
