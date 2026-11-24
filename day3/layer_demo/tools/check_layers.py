# tools/check_layers.py：service 層不可依賴 ui 層
import pathlib, re, sys

bad = [str(f) for f in pathlib.Path("src/service").rglob("*.py")
       if re.search(r"^\s*(from|import)\s+src\.ui", f.read_text(encoding="utf-8"), re.M)]
if bad:
    print("ERROR：service 層不可依賴 ui 層：", ", ".join(bad))
    print("修正方式：把共用型別移到 src/types/，或改由 ui 層呼叫 service。")
    sys.exit(1)
