"""Local launcher for an activated or explicitly selected Python environment."""

import hashlib
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def fingerprint(names):
    h = hashlib.sha256()
    for name in names:
        h.update((ROOT / name).read_bytes())
    return h.hexdigest()


def launch():
    if sys.version_info[:2] != (3, 12) or sys.prefix == sys.base_prefix:
        raise SystemExit("Run start.cmd or use a Python 3.12 virtual environment.")
    if shutil.which("node") is None or shutil.which("npm") is None:
        raise SystemExit("Install Node.js 22.12+ with npm, then reopen the launcher.")
    cache = ROOT / "data"
    cache.mkdir(exist_ok=True)
    deps = ROOT / "requirements.txt"
    marker = Path(sys.prefix) / ".zhixu-installed"
    signature = fingerprint([deps])
    if not marker.exists() or marker.read_text() != signature:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", str(deps)],
            check=True,
            cwd=ROOT,
        )
        marker.write_text(signature)
    files = ["package.json", "package-lock.json", *sorted((ROOT / "web").glob("*"))]
    signature = fingerprint(
        [p for p in files if not isinstance(p, Path) or p.is_file()]
    )
    marker = cache / ".frontend-build"
    if (
        not marker.exists()
        or marker.read_text() != signature
        or not (ROOT / "dist/index.html").is_file()
    ):
        npm = shutil.which("npm")
        subprocess.run([npm, "ci", "--no-audit", "--no-fund"], check=True, cwd=ROOT)
        subprocess.run([npm, "run", "build"], check=True, cwd=ROOT)
        marker.write_text(signature)
    subprocess.run([sys.executable, "server.py", "--open"], cwd=ROOT, check=True)


if __name__ == "__main__":
    try:
        launch()
    except subprocess.CalledProcessError as exc:
        raise SystemExit(exc.returncode)
    except KeyboardInterrupt:
        pass
