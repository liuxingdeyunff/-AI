import os
import tempfile
import unittest
from unittest.mock import patch
import sympy as s
from learning import record, state
from bank import grade
from coaching import session,variant,tutor_chat
from materials import restore, upload
from model_studio import analyze,guides,validate_guide,configure
from test_materials import payload

class StudioTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        setting=patch.dict(os.environ,ZHIXU_DB=self.tmp.name+"/test.db")
        setting.start()
        self.addCleanup(setting.stop)

    def test_math_precision(self):
        self.assertFalse(grade("7-0","0.49999999999999999999"))
        self.assertTrue(grade("7-0","0.50000000000000000000"))

    def test_adaptation_evidence_and_restore(self):
        attempt=record(dict(q="1-0",mode="quiz",answer="0",hints=2,steps="把正弦换为一次项"))["attempt"]
        coach=lambda **k:session(dict(attempt=attempt,**k))
        self.assertIn("多种可能",coach()["guidance"])
        simple=coach(method="substitution")
        self.assertIn("替换",simple["guidance"])
        harder=coach(index=0,answer=str(simple["task"]["param"]))
        self.assertEqual(harder["task"]["level"],2)
        easy=coach(index=1,answer="0")
        self.assertEqual(easy["task"]["level"],1)
        with self.assertRaises(ValueError): coach(index=1,answer="0")
        rows=state()["attempts"]
        self.assertEqual(rows[0]["evidence"]["hints"],2)
        rows[0]["evidence"]["trials"][1]["ok"]=True
        restore(dict(attempts=rows,version=1))
        recovered=state()["attempts"][0]["evidence"]
        self.assertEqual(recovered["steps"],"把正弦换为一次项")
        self.assertFalse(recovered["trials"][1]["ok"])
        self.assertEqual(len(recovered["trials"]),2)

    def test_other_reported_strategy(self):
        attempt=record(dict(q="1-0",mode="practice",answer="1/6"))["attempt"]
        self.assertIn("符号",session(dict(attempt=attempt))["guidance"])
        self.assertEqual(session(dict(attempt=attempt,method="expansion"))["task"]["level"],2)
        with self.assertRaisesRegex(ValueError,"确认"):
            ctx=tutor_chat(dict(attempt=attempt,preview=True))
            tutor_chat(dict(attempt=attempt,context=ctx["context"],question="为什么？",consent=False))

    def test_generated_variants(self):
        self.assertEqual(variant(1,3,3)[1],s.Rational(3**5,120))
        self.assertEqual(variant(7,2,4)[1],8)
        self.assertEqual(variant(9,2,5)[1],s.Rational(1,125))
        for uid in range(10):
            for level in range(1,4):
                tex,expected,reason=variant(uid,level,3)
                self.assertTrue(tex and reason)
                self.assertFalse(expected.has(s.oo,s.nan))

    def test_citations_and_structure(self):
        doc=upload(payload("原创.md","# 教学\n多项式的余项反映局部误差。".encode()))
        node=dict(title="截断误差",chapter="局部展开",kind="概念",requires=[],formula="invented",condition="",citation="0.1",lesson="从余项观察误差。",question="为什么截断会带来误差？")
        with patch("model_studio.generate",return_value=({"units":[node]},{"model":"contract fixture"})):
            g=analyze(dict(doc=doc["id"],start=0,count=1,consent=True))
        u=g["units"][0]
        self.assertEqual(u["quote"],"多项式的余项反映局部误差。")
        self.assertEqual(u["formula"],"")
        self.assertTrue(u["warning"])
        self.assertEqual(guides()[0]["id"],g["id"])
        for change in [dict(requires=[0]),dict(quote="并不存在于原文")]:
            with self.assertRaises(ValueError): validate_guide({"units":[{**u,**change}]},{0:u["quote"]})
        with patch("model_studio.generate") as call:
            with self.assertRaises(ValueError): analyze(dict(doc=doc["id"],start=0,count=1,consent=False))
            call.assert_not_called()
    def test_configuration(self):
        with patch("model_studio.available",return_value=["local:test"]):
            with self.assertRaises(ValueError): configure(dict(name="unknown"))
            self.assertEqual(configure(dict(name="local:test")),"local:test")

