"""Entry point executed by the interpreter included in the Windows ZIP."""
import ctypes
import json
import logging
from logging.handlers import RotatingFileHandler
import msvcrt
import os
from pathlib import Path
import socket
import sys
import threading
import time
import uuid
import webbrowser
from urllib.request import ProxyHandler, build_opener

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
PROFILE = Path(os.environ["LOCALAPPDATA"]) / "ZhixuAI"
if os.environ.get("ZHIXU_ACCEPTANCE") and os.environ.get("ZHIXU_TEST_PROFILE"):
    PROFILE=Path(os.environ["ZHIXU_TEST_PROFILE"]) / "ZhixuAI"


def open_browser(port):
    if not os.environ.get("ZHIXU_ACCEPTANCE"):
        if webbrowser.open(f"http://127.0.0.1:{port}"):
            logging.info("浏览器打开请求已交给系统")
        else:
            logging.warning("请在浏览器中打开运行窗口显示的本机地址")


def existing_instance():
    for _ in range(120):
        try:
            record = json.loads((PROFILE / "instance.json").read_text("utf-8"))
            port = int(record["port"])
            with build_opener(ProxyHandler({})).open(f"http://127.0.0.1:{port}/api/instance",timeout=.4) as r:
                if json.load(r) == record["instance"]:
                    open_browser(port)
                    return
        except (OSError, ValueError, KeyError):
            pass
        time.sleep(.25)
    raise RuntimeError("另一个学习窗口正在启动，请稍后重试。")


def main():
    PROFILE.mkdir(parents=True, exist_ok=True)
    log = RotatingFileHandler(PROFILE / "startup.log",maxBytes=300000,backupCount=2,encoding="utf-8")
    logging.basicConfig(level=logging.INFO,handlers=[log],format="%(asctime)s %(levelname)s %(message)s")
    with (PROFILE/"session.lock").open("a+b") as lock:
        lock.seek(0)
        try:
            msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
        except OSError:
            existing_instance()
            return
        marker = PROFILE/"instance.json"
        marker.unlink(missing_ok=True)
        try:
            from server import Handler, ThreadingHTTPServer, partial
            from learning import state
            os.environ["ZHIXU_DB"] = str(PROFILE / "learning.db")
            state()
            if not (ROOT/"dist/index.html").is_file():
                raise FileNotFoundError("界面文件缺失。")
            class LocalHandler(Handler):
                def log_message(self, fmt, *args):
                    if self.command and self.path.startswith("/api/") and len(args)>1 and str(args[1]).startswith("5"):
                        logging.warning("本地 API 暂时失败")
            factory = partial(LocalHandler,directory=str(ROOT/"dist"))
            try:
                server = ThreadingHTTPServer(("127.0.0.1",8765), factory)
            except OSError:
                server = ThreadingHTTPServer(("127.0.0.1",0), factory)
            with server:
                port = server.server_port
                server.instance = str(uuid.uuid4())
                worker = threading.Thread(target=server.serve_forever,daemon=True)
                worker.start()
                try:
                    tmp = marker.with_suffix(".tmp")
                    tmp.write_text(json.dumps(dict(port=port,instance=server.instance)),"utf-8")
                    tmp.replace(marker)
                    logging.info("本地服务已就绪 port=%s",port)
                    open_browser(port)
                    if os.environ.get("ZHIXU_ACCEPTANCE"):
                        # Test controller requests the same graceful shutdown as the window.
                        while not (PROFILE/"stop-test").exists(): time.sleep(.15)
                        (PROFILE/"stop-test").unlink()
                    else:
                        ctypes.windll.user32.MessageBoxW(None,
                            f"学习界面已在浏览器中打开。\n\n如需重新打开，请双击知序 AI。\n本机地址  http://127.0.0.1:{port}\n\n学习期间保留此窗口。点击「确定」或关闭本窗口即可退出软件。",
                            "知序 AI · 学习服务运行中",0x40)
                finally:
                    server.shutdown()
                    worker.join()
                    logging.info("服务已正常退出")
        finally:
            marker.unlink(missing_ok=True)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logging.exception("启动失败")
        sys.exit(1)

