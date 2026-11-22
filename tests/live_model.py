"""Opt-in, real Ollama integration. Only synthetic student data is used."""
import base64
import json
import os
import sys
import tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from materials import upload
from model_studio import analyze, configure, local_call
from coaching import tutor_chat
from learning import record

def run():
    name=os.environ["ZHIXU_LIVE_MODEL"]
    with tempfile.TemporaryDirectory() as tmp:
        os.environ["ZHIXU_DB"]=str(Path(tmp)/"live.db")
        configure(dict(name=name))
        excerpt="# 相消极限\n直接用 x 替代 sin(x) 会抹去差中的三次项。\n当 x 趋于零时，sin(x) = x - x^3/6 + o(x^3)。"
        doc=upload(dict(name="原创研读样本.md",content=base64.b64encode(excerpt.encode()).decode()))
        g=analyze(dict(doc=doc['id'],start=0,count=1,consent=True))
        assert all(u['quote'] in excerpt for u in g['units'])
        r=record(dict(q='1-0',answer='0',steps='我把 sin(x) 换成了 x，再相减。',mode='quiz',hints=1))
        assert r['ok'] is False
        ctx=tutor_chat(dict(attempt=r["attempt"],preview=True))
        reply=tutor_chat(dict(attempt=r['attempt'],context=ctx['context'],question='怎样检查这一步代换？请给一个提示。',consent=True))
        assert reply['answer'].strip()
        digest=next(m.get("digest") for m in local_call("tags")["models"] if m['name']==name)
        result=dict(model=name,digest=digest,api_charge_usd=0,material=g,dialogue=reply,objective_grade=r['ok'])
        path=Path(os.environ.get('ZHIXU_LIVE_REPORT','live-model.json'))
        path.write_text(json.dumps(result,ensure_ascii=False,indent=2),'utf-8')
        print(f"PASS real {name} · {len(g['units'])} source-linked units · {g['meta']['seconds']}s extraction · {reply['meta']['seconds']}s feedback · API USD 0",flush=True)
        if os.environ.get('GITHUB_STEP_SUMMARY'):
            with open(os.environ['GITHUB_STEP_SUMMARY'],'a',encoding='utf-8') as out:
                out.write(f"模型 {name}，生成 {len(g['units'])} 个可定位单元，用时 {g['meta']['seconds']} 秒。学习追问用时 {reply['meta']['seconds']} 秒，模型 API 费用 0 美元。\n")
if __name__=='__main__': run()

