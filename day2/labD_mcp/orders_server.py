"""訂單 MCP Server（stdio），使用官方 Python SDK（mcp 2.x 的 MCPServer）。

工具：
  list_customers(city)              唯讀：列出客戶，可依城市篩選
  query_orders(customer_id, status) 唯讀：查詢訂單
  order_summary(month)              唯讀：某月各狀態的筆數與金額
  update_order_status(order_id, status)  寫入：修改訂單狀態

資料庫路徑由環境變數 ORDERS_DB 指定（預設 ./orders.db）。
安裝：pip install "mcp>=2,<3"
"""
import os
import sqlite3

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError  # 訊息會原樣回給 Agent
from mcp.types import ToolAnnotations

DB = os.environ.get("ORDERS_DB", "orders.db")
STATUSES = {"pending", "shipped", "delivered", "cancelled"}
server = MCPServer("orders", instructions="虛構公司的客戶與訂單資料庫。金額單位為新台幣元。")
READ_ONLY = ToolAnnotations(readOnlyHint=True)


def _rows(sql, args=()):
    if not os.path.exists(DB):
        raise ToolError(f"找不到資料庫 {DB}，請先執行 seed_db.py")
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    try:
        return [dict(r) for r in conn.execute(sql, args).fetchall()]
    finally:
        conn.close()


@server.tool(annotations=READ_ONLY)
def list_customers(city: str = "") -> list[dict]:
    """列出客戶。city 留空表示全部。"""
    if city:
        return _rows("SELECT id, name, city FROM customers WHERE city = ? ORDER BY id", (city,))
    return _rows("SELECT id, name, city FROM customers ORDER BY id")


@server.tool(annotations=READ_ONLY)
def query_orders(customer_id: str = "", status: str = "", limit: int = 20) -> list[dict]:
    """查詢訂單，可依客戶編號（例如 C01）與狀態（pending／shipped／delivered／cancelled）篩選。"""
    sql, args = "SELECT o.id, o.customer_id, c.name AS customer, o.order_date, o.amount, o.status FROM orders o JOIN customers c ON c.id = o.customer_id WHERE 1=1", []
    if customer_id:
        sql += " AND o.customer_id = ?"; args.append(customer_id)
    if status:
        sql += " AND o.status = ?"; args.append(status)
    sql += " ORDER BY o.order_date LIMIT ?"; args.append(max(1, min(limit, 100)))
    return _rows(sql, args)


@server.tool(annotations=READ_ONLY)
def order_summary(month: str) -> list[dict]:
    """某個月（YYYY-MM）各狀態的訂單筆數與金額合計。"""
    return _rows("SELECT status, COUNT(*) AS orders, SUM(amount) AS total FROM orders WHERE substr(order_date,1,7) = ? GROUP BY status ORDER BY status", (month,))


@server.tool(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False))
def update_order_status(order_id: str, status: str) -> str:
    """修改訂單狀態。status 只能是 pending、shipped、delivered、cancelled。"""
    if status not in STATUSES:
        raise ToolError(f"不支援的狀態 {status}")
    conn = sqlite3.connect(DB)
    try:
        cur = conn.execute("UPDATE orders SET status = ? WHERE id = ?", (status, order_id))
        conn.commit()
    finally:
        conn.close()
    if cur.rowcount == 0:
        raise ToolError(f"找不到訂單 {order_id}")
    return f"{order_id} 已改為 {status}"


if __name__ == "__main__":
    server.run("stdio")
