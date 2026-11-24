"""建立實作 D 的練習資料庫 orders.db（虛構的客戶與訂單）。用法：python3 seed_db.py [路徑]"""
import sqlite3
import sys

path = sys.argv[1] if len(sys.argv) > 1 else "orders.db"
conn = sqlite3.connect(path)
conn.executescript("""
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS orders;
CREATE TABLE customers (id TEXT PRIMARY KEY, name TEXT, city TEXT);
CREATE TABLE orders (id TEXT PRIMARY KEY, customer_id TEXT, order_date TEXT, amount INTEGER, status TEXT);
""")
conn.executemany("INSERT INTO customers VALUES (?,?,?)", [
    ("C01", "星河貿易", "台北"), ("C02", "青山文具", "台中"), ("C03", "海風咖啡", "高雄"),
    ("C04", "木森家具", "台北"), ("C05", "晨光書店", "台南"),
])
conn.executemany("INSERT INTO orders VALUES (?,?,?,?,?)", [
    ("O-1001", "C01", "2026-09-03", 12800, "delivered"), ("O-1002", "C02", "2026-09-11", 3400, "delivered"),
    ("O-1003", "C03", "2026-09-20", 8900, "cancelled"), ("O-1004", "C01", "2026-10-02", 15600, "shipped"),
    ("O-1005", "C04", "2026-10-08", 42000, "pending"), ("O-1006", "C05", "2026-10-12", 2100, "pending"),
    ("O-1007", "C02", "2026-10-15", 7600, "shipped"), ("O-1008", "C03", "2026-10-21", 5300, "pending"),
])
conn.commit()
print(f"已建立 {path}：5 位客戶、8 筆訂單")
