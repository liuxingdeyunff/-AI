import base64
import hashlib
import io
import json
import re
from datetime import date
from pathlib import Path
from pypdf import PdfReader
from pypdf.errors import PyPdfError
from learning import db
from bank import bank, grade

terms = [
    ["函数极限", "极限", "limit"],
    ["无穷小", "等价代换"],
    ["连续", "间断"],
    ["切线", "导数", "求导"],
    ["链式", "复合函数"],
    ["线性近似", "微分增量", "全微分"],
    ["中值定理", "罗尔"],
    ["洛必达", "洛必塔"],
    ["泰勒", "Taylor", "展开式"],
    ["余项", "Peano", "Lagrange"],
]


def prepare(data):
    name = data["name"]
    if not isinstance(name, str) or not 0 < len(name) <= 240:
        raise ValueError("无效文件名")
    raw = base64.b64decode(data["content"], validate=True)
    ext = Path(name).suffix.lower()
    if len(raw) > 4_000_000:
        raise ValueError("单个文件限 4 MB")
    sections = []
    empty = []
    if ext == ".pdf":
        try:
            reader = PdfReader(io.BytesIO(raw))
            if reader.is_encrypted:
                raise ValueError("请导入已解密的 PDF")
            if len(reader.pages) > 120:
                raise ValueError("请分卷导入，每卷最多 120 页")
            for i, p in enumerate(reader.pages, 1):
                t = (p.extract_text() or "").strip()
                if t:
                    sections.append((f"第 {i} 页", t))
                else:
                    empty.append(i)
        except (PyPdfError, IndexError, KeyError) as exc:
            raise ValueError("PDF 损坏或无法解析") from exc
        if not sections:
            raise ValueError(
                "PDF 没有可提取文本，本地 OCR 不可用。请先 OCR，或改传 Markdown / TXT。"
            )
    elif ext in (".md", ".txt"):
        try:
            src = raw.decode("utf-8-sig")
        except UnicodeDecodeError:
            raise ValueError("请另存为 UTF-8 文本再导入") from None
        if "\x00" in src:
            raise ValueError("无效文本编码")
        parts = re.split(r"(?m)(?=^#{1,6}\s+\S)", src) if ext == ".md" else [src]
        for i, part in enumerate(parts, 1):
            if part.strip():
                sections.append(
                    (
                        (
                            part.splitlines()[0][:120]
                            if part.startswith("#")
                            else f"片段 {i}"
                        ),
                        part.strip(),
                    )
                )
    else:
        raise ValueError("请选择 PDF、Markdown 或 TXT")
    if not sections:
        raise ValueError("文件为空，请选择含有正文的文件")
    if sum(len(t) for _, t in sections) > 600000 or len(sections) > 800:
        raise ValueError("资料过长，请分卷导入")
    fragments = []
    for anchor, body in sections:
        matches = {
            str(i): next((w for w in words if w.casefold() in body.casefold()), None)
            for i, words in enumerate(terms)
        }
        fragments.append(
            dict(
                anchor=anchor,
                text=body,
                matches={k: w for k, w in matches.items() if w},
            )
        )
    return dict(
        id=hashlib.sha256(name.encode() + b"\0" + raw).hexdigest(),
        name=name,
        sections=fragments,
        empty=empty,
    )


def ensure(c):
    c.execute(
        "CREATE TABLE IF NOT EXISTS materials (id TEXT PRIMARY KEY, doc TEXT NOT NULL)"
    )


def documents():
    with db() as c:
        ensure(c)
        return [
            json.loads(r[0])
            for r in c.execute("SELECT doc FROM materials ORDER BY rowid")
        ]


def upload(data):
    doc = prepare(data)
    with db() as c:
        ensure(c)
        c.execute(
            "INSERT OR IGNORE INTO materials VALUES (?,?)",
            (doc["id"], json.dumps(doc, ensure_ascii=False)),
        )
    return doc


def restore(data):
    rows = data.get("attempts")
    if data.get("version") != 1 or not isinstance(rows, list) or len(rows) > 50000:
        raise ValueError("不支持的学习进度备份")
    values = []
    for r in rows:
        k, a, m, d = r["q"], r["answer"], r["mode"], r["day"]
        if (
            k not in bank
            or not isinstance(a, str)
            or len(a) > 120
            or m not in ("quiz", "practice", "review")
            or (m == "quiz" and not bank[k]["diagnostic"])
        ):
            raise ValueError("备份记录无效")
        if date.fromisoformat(d).year >= 9999:
            raise ValueError("备份日期无效")
        values.append((k, a, int(grade(k, a)), date.fromisoformat(d).isoformat(), m))
    with db() as c:
        c.execute("DELETE FROM receipts")
        c.execute("DELETE FROM attempts")
        c.executemany(
            "INSERT INTO attempts(q,answer,ok,day,mode) VALUES (?,?,?,?,?)", values
        )
    return dict(count=len(values))
