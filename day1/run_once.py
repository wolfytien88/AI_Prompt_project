"""實作 1 用：把一份 Prompt 和一筆輸入送給指定模型，印出回覆。

用法：
  python3 run_once.py --provider claude --prompt prompts/A/v2.txt --input "商品拆封了還能退嗎？"
  python3 run_once.py --provider openai --prompt prompts/C/v3.txt --input-file my_invoice.txt
"""
import argparse
from llm import call

p = argparse.ArgumentParser()
p.add_argument("--provider", choices=["claude", "openai"], required=True)
p.add_argument("--prompt", required=True, help="System Prompt 檔案")
g = p.add_mutually_exclusive_group(required=True)
g.add_argument("--input", help="使用者訊息文字")
g.add_argument("--input-file", help="使用者訊息檔案")
a = p.parse_args()

system = open(a.prompt, encoding="utf-8").read()
user = a.input if a.input is not None else open(a.input_file, encoding="utf-8").read()
print(call(a.provider, system, user))
