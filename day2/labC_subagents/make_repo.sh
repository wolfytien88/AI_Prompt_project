#!/bin/bash
# 建立實作 C 的練習專案 member-service（虛構的會員服務），內含刻意留下的安全、測試與效能問題。
# 用法：bash make_repo.sh [目的資料夾，預設 ./member-service]
set -e
DEST="${1:-./member-service}"
[ -e "$DEST" ] && { echo "$DEST 已存在"; exit 1; }
mkdir -p "$DEST"/member_service "$DEST"/tests && cd "$DEST"
cat > member_service/__init__.py <<'PY'
PY
cat > member_service/store.py <<'PY'
"""會員資料存取（SQLite）。"""
import hashlib
import os
import sqlite3

DB_PATH = os.environ.get("MEMBER_DB", "members.db")


def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("CREATE TABLE IF NOT EXISTS members (id INTEGER PRIMARY KEY, email TEXT, name TEXT, pw TEXT, tier TEXT)")
    return conn


def add_member(conn, email, name, password, tier="basic"):
    pw = hashlib.md5(password.encode()).hexdigest()
    conn.execute(f"INSERT INTO members (email, name, pw, tier) VALUES ('{email}', '{name}', '{pw}', '{tier}')")
    conn.commit()


def find_by_email(conn, email):
    return conn.execute(f"SELECT id, email, name, tier FROM members WHERE email = '{email}'").fetchone()


def all_members(conn):
    return conn.execute("SELECT id, email, name, tier FROM members").fetchall()
PY
cat > member_service/export.py <<'PY'
"""把會員資料匯出成 CSV，並壓縮後放到指定資料夾。"""
import csv
import os

from .store import all_members


def dedupe(rows):
    result = []
    for r in rows:
        dup = False
        for x in result:
            if x[1].lower() == r[1].lower():
                dup = True
        if not dup:
            result.append(r)
    return result


def export_csv(conn, out_dir, filename):
    rows = dedupe(all_members(conn))
    path = out_dir + "/" + filename
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        for r in rows:
            w.writerow(r)
    os.system(f"gzip -f {path}")
    return path + ".gz"


def tier_counts(conn):
    counts = {}
    for tier in ["basic", "gold", "vip"]:
        counts[tier] = len([m for m in all_members(conn) if m[3] == tier])
    return counts
PY
cat > tests/test_export.py <<'PY'
import os
import tempfile

from member_service import store
from member_service.export import export_csv


def test_export_creates_file():
    d = tempfile.mkdtemp()
    store.DB_PATH = os.path.join(d, "t.db")
    conn = store.connect()
    store.add_member(conn, "amy@example.com", "Amy", "pw1")
    out = export_csv(conn, d, "m.csv")
    assert os.path.exists(out)
PY
printf '# member-service\n\n虛構的會員服務，練習用。測試：`python3 -m pytest -q`\n' > README.md
git init -q -b main
git -c user.email=lab@example.com -c user.name=lab add -A
git -c user.email=lab@example.com -c user.name=lab commit -qm "init member-service"
echo "已建立 $(pwd)"
