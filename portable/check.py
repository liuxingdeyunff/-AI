"""Launch and test the actual unpacked ZIP, on Windows or with WINE64 set."""
import json
import os
from pathlib import Path
import socket
import subprocess
import tempfile
import time
from urllib.request import Request, urlopen
import zipfile
import sys

ROOT=Path(__file__).resolve().parents[1]

def winpath(path):
    return "Z:"+str(path).replace("/","\\") if os.name!="nt" else str(path)

class PackagedServer:
    def __init__(self,root,profile):
        self.profile=profile/"ZhixuAI"
        self.env={**os.environ,"ZHIXU_TEST_PROFILE":winpath(profile),"LOCALAPPDATA":winpath(profile),"ZHIXU_ACCEPTANCE":"1","PYTHONPATH":"","PYTHONHOME":""}
        self.env["PATH"]=os.environ.get("SystemRoot","C:\\Windows")+"\\System32" if os.name=="nt" else "/usr/bin:/bin"
        self.cmd=([os.environ["WINE64"]] if os.name!="nt" else [])+[str(root/"知序AI.exe")]
        self.p=self.spawn()
        marker=self.profile/"instance.json"
        for _ in range(600):
            if self.p.poll() is not None: raise RuntimeError("Packaged process exited: "+str(self.p.returncode))
            if marker.exists():
                data=json.loads(marker.read_text("utf-8"))
                self.url=f"http://127.0.0.1:{data['port']}"
                if self.get("instance")==data["instance"]: break
            time.sleep(.2)
        else:
            self.p.terminate()
            raise RuntimeError("Packaged startup timeout")
    def spawn(self): return subprocess.Popen(self.cmd,env=self.env)
    def get(self,route): return json.load(urlopen(self.url+"/api/"+route,timeout=10))
    def stop(self):
        (self.profile/"stop-test").touch()
        assert self.p.wait(timeout=45)==0
        assert not (self.profile/"instance.json").exists()

def check(archive):
    with tempfile.TemporaryDirectory() as d:
        work=Path(d)
        with zipfile.ZipFile(archive) as z: z.extractall(work)
        root=work/"ZhixuAI-Windows-x64"
        profile=work/"用户 数据"
        with socket.socket() as occupied:
            try: occupied.bind(("127.0.0.1",8765)); occupied.listen()
            except OSError: pass
            app=PackagedServer(root,profile)
            try:
                assert not app.url.endswith(":8765")
                assert len(app.get("units"))==10
                assert b'type="module"' in urlopen(app.url).read()
                assert app.spawn().wait(timeout=40)==0
                req=Request(app.url+"/api/answer",json.dumps({"q":"1-0","answer":"-1/6","mode":"quiz"}).encode(),{"Content-Type":"application/json"})
                assert json.load(urlopen(req))["ok"]
                print("PASS extracted Windows EXE: frontend, bundled SymPy, occupied port, duplicate launch",flush=True)
            finally: app.stop()
        app=PackagedServer(root,profile)
        try:
            assert len(app.get("state")["attempts"])==1
            print("PASS graceful stop, restart and per-user SQLite persistence",flush=True)
        finally: app.stop()

if __name__=="__main__": check(Path(sys.argv[1]))

