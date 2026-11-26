"""拆除實驗執行器：用同一份測試集，比較「完整版」與「拿掉一個元件」的分數、輪數與 Token。

每一題都以 Agent Loop 執行（模型可使用 bash 工具），最後的文字回覆必須包含 must_include 的所有關鍵字才算通過。
結果會附加到 CSV，一次實驗一列，欄位與拆除實驗紀錄表相同。

範例：
  python3 ablate.py --label 基準 --system system_full.txt --fewshot fewshot.txt
  python3 ablate.py --label A --removed "System Prompt 第 2 段" --system system_no_rule2.txt --fewshot fewshot.txt
  python3 ablate.py --label B --removed "Few-shot 範例" --system system_full.txt
  python3 ablate.py --label C --removed "截斷長度 5000 → 不截斷" --system system_full.txt --fewshot fewshot.txt --truncate 0
"""
import argparse, csv, json, os, subprocess

import anthropic

MODEL = "claude-sonnet-5-5"  # 依上課當下可用的模型調整
BASH_TOOL = {
    "name": "bash",
    "description": "在目前資料夾執行一個 shell 指令，回傳輸出",
    "input_schema": {"type": "object",
                     "properties": {"command": {"type": "string"}},
                     "required": ["command"]},
}


def run_case(client, system, question, truncate, max_rounds):
    """執行一題，回傳 (最後文字, 輪數, 輸入 Token, 輸出 Token)。"""
    messages = [{"role": "user", "content": question}]
    rounds = tok_in = tok_out = 0
    while True:
        resp = client.messages.create(model=MODEL, max_tokens=2048, system=system,
                                      tools=[BASH_TOOL], messages=messages)
        rounds += 1
        tok_in += resp.usage.input_tokens
        tok_out += resp.usage.output_tokens
        messages.append({"role": "assistant", "content": resp.content})
        if resp.stop_reason != "tool_use" or rounds >= max_rounds:
            break
        results = []
        for block in resp.content:
            if block.type == "tool_use":
                # encoding 指定 UTF-8：Windows 預設用 cp950 解碼，遇到中文輸出會中斷
                out = subprocess.run(block.input["command"], shell=True,
                                     capture_output=True, text=True, timeout=60,
                                     encoding="utf-8", errors="replace",
                                     env={**os.environ, "PYTHONIOENCODING": "utf-8"})
                text = out.stdout + out.stderr
                if truncate > 0:
                    text = text[-truncate:]
                results.append({"type": "tool_result", "tool_use_id": block.id, "content": text})
        messages.append({"role": "user", "content": results})
    final = "".join(b.text for b in resp.content if b.type == "text")
    return final, rounds, tok_in, tok_out


def main():
    ap = argparse.ArgumentParser(description="拆除實驗執行器")
    ap.add_argument("--label", required=True, help="實驗代號，例如 基準、A、B")
    ap.add_argument("--removed", default="（無，完整版）", help="這次拿掉的元件")
    ap.add_argument("--cases", default="cases.json", help="測試集，格式同前一單元的 cases.json")
    ap.add_argument("--system", required=True, help="System Prompt 檔案")
    ap.add_argument("--fewshot", default=None, help="Few-shot 範例檔，會接在 System Prompt 後面；不給 = 拿掉範例")
    ap.add_argument("--truncate", type=int, default=5000, help="工具輸出保留的字元數，0 = 不截斷")
    ap.add_argument("--runs", type=int, default=2, help="重複次數，至少 2 次才看得出隨機波動")
    ap.add_argument("--max-rounds", type=int, default=10, help="每題最多輪數，避免失控")
    ap.add_argument("--out", default="ablation_results.csv")
    args = ap.parse_args()

    system = open(args.system, encoding="utf-8").read()
    if args.fewshot:
        system += "\n\n" + open(args.fewshot, encoding="utf-8").read()
    cases = json.load(open(args.cases, encoding="utf-8"))
    client = anthropic.Anthropic()

    passed_runs, rounds_all, tokens_all = [], [], []
    for r in range(args.runs):
        passed = 0
        for c in cases:
            text, rounds, t_in, t_out = run_case(client, system, c["input"], args.truncate, args.max_rounds)
            ok = all(k in text for k in c["must_include"])
            passed += ok
            rounds_all.append(rounds)
            tokens_all.append(t_in + t_out)
            print(f"第 {r + 1} 次｜{'PASS' if ok else 'FAIL'}｜{rounds} 輪｜{c['input'][:24]}")
        passed_runs.append(passed)

    n = len(cases)
    row = {
        "實驗": args.label,
        "拿掉的元件": args.removed,
        "通過數（平均）": f"{sum(passed_runs) / len(passed_runs):.1f} / {n}",
        "各次通過數": " ".join(str(p) for p in passed_runs),
        "平均輪數": f"{sum(rounds_all) / len(rounds_all):.2f}",
        "平均 Token（每題）": f"{sum(tokens_all) / len(tokens_all):.0f}",
        "判讀": "",
    }
    new_file = not os.path.exists(args.out)
    with open(args.out, "a", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(row))
        if new_file:
            w.writeheader()
        w.writerow(row)
    print(f"\n{args.label}：通過 {row['通過數（平均）']}（各次 {row['各次通過數']}），平均 {row['平均輪數']} 輪，"
          f"每題平均 {row['平均 Token（每題）']} Token → 已寫入 {args.out}")


if __name__ == "__main__":
    main()
