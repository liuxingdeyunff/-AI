import os
import sqlite3
from contextlib import contextmanager
from datetime import date, timedelta
from pathlib import Path
from bank import bank, grade
from courses import units


@contextmanager
def db():
    path = Path(
        os.environ.get("ZHIXU_DB", Path(__file__).parent / "data" / "learning.db")
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path)
    con.row_factory = sqlite3.Row
    try:
        with con:
            con.execute(
                "CREATE TABLE IF NOT EXISTS attempts (id INTEGER PRIMARY KEY, q TEXT NOT NULL, answer TEXT NOT NULL, ok INTEGER NOT NULL, day TEXT NOT NULL, mode TEXT NOT NULL)"
            )
            con.execute(
                "CREATE TABLE IF NOT EXISTS receipts (token TEXT PRIMARY KEY, q TEXT, answer TEXT, mode TEXT)"
            )
            yield con
    finally:
        con.close()


def record(data):
    q = bank[data["q"]]
    answer = data["answer"]
    if not isinstance(answer, str) or len(answer) > 120:
        raise ValueError("答案格式无效")
    mode = data["mode"]
    if mode not in ("quiz", "review", "practice") or (
        mode == "quiz" and not q["diagnostic"]
    ):
        raise ValueError("答题模式无效")
    from coaching import ensure_evidence, initial, save
    evidence=initial(data.get("steps",""),data.get("hints",0))
    ok = grade(q["id"], answer)
    with db() as c:
        ensure_evidence(c)
        c.execute("CREATE TABLE IF NOT EXISTS receipt_attempts(token TEXT PRIMARY KEY, attempt INTEGER)")
        token = data.get("request_id")
        new = True
        if token is not None:
            if not isinstance(token, str) or len(token) != 36:
                raise ValueError("提交编号无效")
            new = (
                c.execute(
                    "INSERT OR IGNORE INTO receipts VALUES (?,?,?,?)",
                    (token, q["id"], answer, mode),
                ).rowcount
                == 1
            )
            if not new and tuple(
                c.execute(
                    "SELECT q,answer,mode FROM receipts WHERE token=?", (token,)
                ).fetchone()
            ) != (q["id"], answer, mode):
                raise ValueError("这次提交已经处理，请刷新记录。")
        if new:
            cursor=c.execute(
                "INSERT INTO attempts(q,answer,ok,day,mode) VALUES (?,?,?,?,?)",
                (q["id"], answer, int(ok), date.today().isoformat(), mode),
            )
            attempt=cursor.lastrowid
            save(c,attempt,evidence)
            if token:
                c.execute("INSERT INTO receipt_attempts VALUES (?,?)",(token,attempt))
        else:
            match=c.execute("SELECT attempt FROM receipt_attempts WHERE token=?",(token,)).fetchone()
            attempt=match[0] if match else None
    return dict(
        attempt=attempt,
        ok=bool(ok),
        solution=(
            q["choices"][q["expected"]]
            if q["choices"]
            else str(q["expected"]).replace("**", "^")
        ),
        reason=q["reason"],
        error=q["error"],
        prereq=(
            q["unit"]
            if not units[q["unit"]]["prereq"]
            else units[q["unit"]]["prereq"][0]
        ),
    )


def state():
    with db() as c:
        rows = [dict(r) for r in c.execute("SELECT * FROM attempts ORDER BY id")]
        from coaching import ensure_evidence
        import json
        ensure_evidence(c)
        evidence={r[0]:json.loads(r[1]) for r in c.execute("SELECT attempt,payload FROM study_evidence")}
        for row in rows:
            if row["id"] in evidence: row["evidence"]=evidence[row["id"]]
    latest = {r["q"]: r for r in rows}
    reviews = []
    for key in dict.fromkeys(r["q"] for r in rows if not r["ok"]):
        r = latest[key]
        due = date.fromisoformat(r["day"]) + timedelta(days=3 if r["ok"] else 0)
        reviews.append(
            dict(
                q=key,
                unit=bank[key]["unit"],
                due=due.isoformat(),
                ready=due <= date.today(),
                resolved=bool(r["ok"]),
                error=bank[key]["error"],
            )
        )
    scores = {}
    for u in units:
        sample = [r for k, r in latest.items() if bank[k]["unit"] == u["id"]]
        if sample:
            scores[u["id"]] = round(100 * sum(r["ok"] for r in sample) / len(sample))
    return dict(
        attempts=rows, reviews=sorted(reviews, key=lambda r: r["due"]), scores=scores
    )
