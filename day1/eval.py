import anthropic, json

client = anthropic.Anthropic()
MODEL = "claude-sonnet-5-5"  # 依上課當下可用的模型調整
cases = json.load(open("cases.json", encoding="utf-8"))
# cases.json 格式：[{"input": "...", "must_include": ["關鍵字1", "關鍵字2"]}]
prompt = open("prompt_v2.txt", encoding="utf-8").read()

passed = 0
for c in cases:
    r = client.messages.create(
        model=MODEL, max_tokens=1024, system=prompt,
        messages=[{"role": "user", "content": c["input"]}],
    )
    # 只取文字區塊；開啟 extended thinking 時第一個區塊會是思考內容
    text = "".join(b.text for b in r.content if b.type == "text")
    ok = all(k in text for k in c["must_include"])
    passed += ok
    print("PASS" if ok else "FAIL", c["input"][:30])
print(f"通過 {passed}/{len(cases)}")
