"""Exercise the ordinary GUI launch and close the actual native status window."""
import ctypes
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
from urllib.request import urlopen

def check(root):
    from ctypes import wintypes
    user32=ctypes.windll.user32
    user32.FindWindowW.argtypes=[wintypes.LPCWSTR,wintypes.LPCWSTR]
    user32.FindWindowW.restype=wintypes.HWND
    user32.PostMessageW.argtypes=[wintypes.HWND,wintypes.UINT,wintypes.WPARAM,wintypes.LPARAM]
    with tempfile.TemporaryDirectory() as tmp:
        env={**os.environ,"LOCALAPPDATA":tmp}
        env.pop("ZHIXU_ACCEPTANCE",None)
        p=subprocess.Popen([str(root/"知序AI.exe")],env=env)
        profile=Path(tmp)/"ZhixuAI"
        try:
            for _ in range(450):
                handle=user32.FindWindowW(None,"知序 AI · 学习服务运行中")
                if handle and (profile/"instance.json").is_file(): break
                if p.poll() is not None: raise RuntimeError("Desktop application exited early")
                time.sleep(.2)
            else: raise RuntimeError("Native status window never appeared")
            port=json.loads((profile/"instance.json").read_text())["port"]
            assert len(json.load(urlopen(f"http://127.0.0.1:{port}/api/units")))==10
            assert user32.PostMessageW(handle,0x0010,0,0)
            assert p.wait(timeout=30)==0
            assert not (profile/"instance.json").exists()
            assert "浏览器打开请求已交给系统" in (profile/"startup.log").read_text("utf-8")
            print("PASS ordinary EXE, Windows browser launch request, native status window, WM_CLOSE and graceful exit")
        finally:
            if p.poll() is None: p.terminate()
if __name__=="__main__": check(Path(sys.argv[1]).resolve())

