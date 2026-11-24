import os

read_times = {}  # 路徑 → 上次讀取時的修改時間

def read_file(path):
    read_times[path] = os.path.getmtime(path)
    return open(path, encoding="utf-8").read()

def edit_file(path, old, new):
    if read_times.get(path) != os.path.getmtime(path):
        return "錯誤：檔案在上次讀取後被修改過，請先重新讀取"
    text = open(path, encoding="utf-8").read()
    if text.count(old) != 1:
        return "錯誤：old 必須在檔案中剛好出現一次"
    open(path, "w", encoding="utf-8").write(text.replace(old, new))
    read_times[path] = os.path.getmtime(path)
    return "已修改"
