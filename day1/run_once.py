"""實作 1 用：把一份 Prompt 和一筆輸入送給指定模型，印出回覆。

用法：
  python3 run_once.py --provider claude --prompt prompts/A/v2.txt --input "商品拆封了還能退嗎？"
  python3 run_once.py --provider openai --prompt prompts/C/v3.txt --input-file my_invoice.txt
"""
import argparse
from pathlib import Path
from llm import call

BASE_DIR = Path(__file__).resolve().parent


def resolve_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    cwd_path = Path.cwd() / path
    if cwd_path.exists():
        return cwd_path
    return BASE_DIR / path


p = argparse.ArgumentParser()
p.add_argument("--provider", choices=["claude", "openai"], required=True)
p.add_argument("--prompt", required=True, help="System Prompt 檔案")
g = p.add_mutually_exclusive_group(required=True)
g.add_argument("--input", help="使用者訊息文字")
g.add_argument("--input-file", help="使用者訊息檔案")
a = p.parse_args()

prompt_path = resolve_path(a.prompt)
if not prompt_path.is_file():
    p.error(f"找不到 Prompt 檔案：{a.prompt}")

system = prompt_path.read_text(encoding="utf-8")
if a.input is not None:
    user = a.input
else:
    input_path = resolve_path(a.input_file)
    if not input_path.is_file():
        p.error(f"找不到輸入檔案：{a.input_file}")
    user = input_path.read_text(encoding="utf-8")
print(call(a.provider, system, user))
