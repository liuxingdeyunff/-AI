"""Build a self-contained Windows distribution. Run npm ci and npm run build first."""
import argparse
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
RUNTIME_URL = "https://api.nuget.org/v3-flatcontainer/python/3.12.10/python.3.12.10.nupkg"
RUNTIME_SHA = "0eb85c2dfccccf1b17352de4c397f69194035b7d37149eacc16f1147d93de3b8"
NAME = "ZhixuAI-Windows-x64"


def build(output, runtime, compiler):
    output.mkdir(parents=True,exist_ok=True)
    if not runtime.exists():
        urllib.request.urlretrieve(RUNTIME_URL,runtime)
    if hashlib.sha256(runtime.read_bytes()).hexdigest()!=RUNTIME_SHA:
        raise SystemExit("Windows Python runtime checksum mismatch")
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)/NAME
        app = root/"app"
        app.mkdir(parents=True)
        with zipfile.ZipFile(runtime) as source:
            for name in source.namelist():
                if name.startswith("tools/") and not name.endswith("/"):
                    dest=root/"runtime"/name[6:]
                    dest.parent.mkdir(parents=True,exist_ok=True)
                    with source.open(name) as src,dest.open("wb") as dst:
                        shutil.copyfileobj(src,dst)
        # Application requirements are universal wheels, usable on both build hosts.
        site=root/"runtime/Lib/site-packages"
        subprocess.run([sys.executable,"-m","pip","install","--only-binary=:all:","--platform","win_amd64","--python-version","3.12","--no-compile","--target",str(site),"-r",str(ROOT/"requirements.txt")],check=True)
        for mod in ROOT.glob("*.py"):
            if mod.name!="launcher.py": shutil.copy2(mod,app/mod.name)
        shutil.copy2(ROOT/"portable/portable.py",app)
        shutil.copytree(ROOT/"dist",app/"dist")
        shutil.copytree(ROOT/"examples",root/"示例资料")
        shutil.copy2(ROOT/"docs/Windows使用说明.md",root/"使用说明.txt")
        licenses=root/"licenses"
        licenses.mkdir()
        for pkg in ("katex","lucide"):
            license_file=next((ROOT/"node_modules"/pkg).glob("LICENSE*"))
            shutil.copy2(license_file, licenses/(pkg+".txt"))
        exe=root/"知序AI.exe"
        source=str(ROOT/"portable/launcher.c")
        if os.name=="nt":
            subprocess.run([compiler or "cl","/nologo","/utf-8","/O2","/MT",source,"/Fe:"+str(exe),"/link","/SUBSYSTEM:WINDOWS","user32.lib"],cwd=temp,check=True)
        else:
            subprocess.run([compiler or "x86_64-w64-mingw32-gcc","-O2","-s","-mwindows","-static",source,"-o",str(exe)],check=True)
        archive=shutil.make_archive(str(output/NAME),"zip",root.parent,root.name)
        digest=hashlib.sha256(Path(archive).read_bytes()).hexdigest()
        (output/"SHA256SUMS.txt").write_text(f"{digest}  {NAME}.zip\n","ascii")
        print(archive,digest,flush=True)

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",type=Path,default=ROOT/"out")
    parser.add_argument("--runtime",type=Path,default=Path(tempfile.gettempdir())/"python-3.12.10.nupkg")
    parser.add_argument("--compiler")
    args=parser.parse_args()
    build(args.output.resolve(),args.runtime,args.compiler)

