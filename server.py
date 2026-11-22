import argparse
import json
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit
from courses import units

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
        if urlsplit(self.path).path == "/api/units":
            return self.reply(units)
        super().do_GET()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    app = ThreadingHTTPServer(("127.0.0.1", args.port), partial(Handler, directory=str(ROOT / "dist")))
    print(f"知序 AI  http://127.0.0.1:{app.server_port}", flush=True)
    app.serve_forever()
