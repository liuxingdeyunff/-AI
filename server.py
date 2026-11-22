import argparse
import json
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit
from courses import units
from materials import documents, upload, restore
from provider import ask, model
from bank import bank, public
from learning import record, state

ROOT = Path(__file__).resolve().parent

class Handler(SimpleHTTPRequestHandler):
    def reply(self, value, status=200):
        raw = json.dumps(value, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        if self.headers.get("Host") not in (f"127.0.0.1:{self.server.server_port}",f"localhost:{self.server.server_port}"): return self.reply({"error":"仅限本机"},403)
        if self.path == "/api/documents": return self.reply(documents())
        if self.path == "/api/model": return self.reply(model())
        if urlsplit(self.path).path == "/api/units":
            return self.reply(units)
        if self.path == "/api/state": return self.reply(state())
        if self.path == "/api/questions": return self.reply([public(q) for q in bank.values()])
        super().do_GET()

    def do_POST(self):
        origin=self.headers.get("Origin")
        if self.headers.get("Host") not in (f"127.0.0.1:{self.server.server_port}",f"localhost:{self.server.server_port}") or (origin and origin != "http://"+self.headers.get("Host","")):
            return self.reply({"error":"只允许本机同源请求"},403)
        try:
            size=int(self.headers.get("Content-Length","0"))
            if not 0<size<=8_000_000: raise ValueError("请求为空或超过大小限制")
            if self.headers.get_content_type()!="application/json": raise ValueError("请求必须为 JSON")
            data=json.loads(self.rfile.read(size))
            if not isinstance(data,dict): raise ValueError("需要 JSON 对象")
            for route,action in [("/api/upload",upload),("/api/restore",restore),("/api/ask",ask)]:
                if self.path==route: return self.reply(action(data))
            if self.path=="/api/answer": return self.reply(record(data))
            return self.reply({"error":"接口不存在"},404)
        except (ValueError,KeyError,TypeError) as error:
            self.reply({"error":str(error)},400)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    app = ThreadingHTTPServer(("127.0.0.1", args.port), partial(Handler, directory=str(ROOT / "dist")))
    print(f"知序 AI  http://127.0.0.1:{app.server_port}", flush=True)
    app.serve_forever()
