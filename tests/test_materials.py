import base64
import io
import os
import tempfile
import unittest
from unittest.mock import patch
from pypdf import PdfWriter
from pypdf.generic import DictionaryObject, NameObject, DecodedStreamObject
from materials import prepare, upload, documents, restore
from learning import state
from provider import ask

def pdf(text=True):
    w=PdfWriter()
    page=w.add_blank_page(300,300)
    if text:
        font=DictionaryObject({NameObject('/Type'):NameObject('/Font'),NameObject('/Subtype'):NameObject('/Type1'),NameObject('/BaseFont'):NameObject('/Helvetica')})
        page[NameObject('/Resources')]=DictionaryObject({NameObject('/Font'):DictionaryObject({NameObject('/F1'):font})})
        stream=DecodedStreamObject()
        stream.set_data(b'BT /F1 12 Tf 20 200 Td (Taylor polynomial near zero) Tj ET')
        page[NameObject('/Contents')]=w._add_object(stream)
        w.add_blank_page(300,300)
    dest=io.BytesIO()
    w.write(dest)
    return dest.getvalue()

def payload(name,b): return dict(name=name,content=base64.b64encode(b).decode())

class Imports(unittest.TestCase):
    def test_pdf(self):
        d=prepare(payload('notes.pdf',pdf()))
        self.assertEqual(d['empty'],[2])
        self.assertEqual(d['sections'][0]['anchor'],'第 1 页')
        self.assertEqual(d['sections'][0]['matches']['8'],'Taylor')
        with self.assertRaisesRegex(ValueError,'OCR'): prepare(payload('scan.pdf',pdf(False)))
    def test_text_anchors(self):
        with tempfile.TemporaryDirectory() as d, patch.dict(os.environ,ZHIXU_DB=d+'/db'):
            item=payload('讲义.md','# 极限\n正文\n## 泰勒\n余项'.encode())
            upload(item)
            upload(item)
            self.assertEqual(len(documents()),1)
            self.assertEqual(documents()[0]['sections'][1]['anchor'],'## 泰勒')
            self.assertEqual(prepare(payload('a.txt','连续'.encode()))['sections'][0]['matches'],{'2':'连续'})
            with self.assertRaises(ValueError): prepare(payload('b.txt',b''))
    def test_restore_is_atomic(self):
        with tempfile.TemporaryDirectory() as d, patch.dict(os.environ,ZHIXU_DB=d+'/db'):
            row=dict(q='1-0',day='2026-01-01',mode='quiz',answer='0',ok=1)
            restore(dict(version=1,attempts=[row]))
            with self.assertRaises(KeyError): restore(dict(version=1,attempts=[row,{}]))
            self.assertEqual([r['ok'] for r in state()['attempts']],[0])
    def test_model_permission(self):
        with patch.dict(os.environ,ZHIXU_OLLAMA_MODEL='test'):
            with self.assertRaisesRegex(ValueError,'确认'): ask(dict(question='解释',excerpt='一段文字',consent=False))

