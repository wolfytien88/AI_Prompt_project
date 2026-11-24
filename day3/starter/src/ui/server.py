"""ui 層：HTTP 伺服器與網頁。可依賴所有下層。

啟動：python3 -m src.ui.server（預設 http://localhost:5173）
"""
import json
import os
import pathlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from src.repo.todo_repo import JsonTodoRepo
from src.service.todo_service import TodoService

ROOT = pathlib.Path(__file__).resolve().parents[2]
STATIC = pathlib.Path(__file__).resolve().parent / "static"
DATA_FILE = os.environ.get("TODO_DATA", str(ROOT / "data" / "todos.json"))
PORT = int(os.environ.get("PORT", "5173"))

service = TodoService(JsonTodoRepo(DATA_FILE))


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):  # 日誌寫到 stderr，由 init.sh 導到 logs/server.log
        super().log_message(fmt, *args)

    def send_json(self, status: int, payload) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/api/health":
            self.send_json(200, {"status": "ok"})
        elif self.path == "/api/todos":
            self.send_json(200, [t.to_dict() for t in service.list_todos()])
        elif self.path in ("/", "/index.html"):
            body = (STATIC / "index.html").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_json(404, {"error": "找不到路徑"})


def main() -> None:
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"伺服器啟動：http://localhost:{PORT}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
