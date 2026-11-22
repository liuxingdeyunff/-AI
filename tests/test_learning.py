import os
import tempfile
import unittest
from unittest.mock import patch
import sympy as s
from bank import bank,grade,x
from learning import record,state

class MathTests(unittest.TestCase):
    def test_reference_answers(self):
        self.assertEqual(len(bank),50)
        for q in bank.values():
            a=int(q['id'].split('-')[1])+1
            i=q['unit']
            if i==0: v=s.limit(s.sin(a*x)/x,x,0)
            elif i==1: v=s.limit((s.sin(x)-x)/x**3,x,0) if a==1 else (1-s.cos(x**(a-1))).as_leading_term(x).as_powers_dict()[x]
            elif i==2: v=s.limit((x**2-a*a)/(x-a),x,a)
            elif i==3: v=s.diff(x**(a+1),x).subs(x,2)
            elif i==4: v=s.diff((a*x+1)**2,x)
            elif i==5: v=s.diff(x*x,x).subs(x,a)/100
            elif i==6: v=1 if a==1 else s.solve(2*x-2*(a-1),x)[0]
            elif i==7: v=s.limit((s.exp(a*x)-1-a*x)/x**2,x,0)
            elif i==8: v=s.log(1+a*x).series(x,0,4).removeO()
            else: v=2 if a==1 else s.Rational(1,2)**a
            self.assertTrue(grade(q['id'],str(v)),q['id'])
    def test_common_mistakes(self):
        for k,a in [('1-0','0'),('7-0','1'),('8-0','x-x^2/2'),('9-0','0')]:
            self.assertFalse(grade(k,a))
        for a in ['x/x','unknown(x)','2**9999','1/0']:
            with self.assertRaises(ValueError): grade('0-0',a)

class HistoryTests(unittest.TestCase):
    def test_review(self):
        with tempfile.TemporaryDirectory() as d, patch.dict(os.environ,ZHIXU_DB=d+'/db'):
            for answer,mode in [('0','quiz'),('-1/6','review'),('-1/6','review')]:
                record(dict(q='1-0',answer=answer,mode=mode))
            snap=state()
            self.assertEqual(len(snap['reviews']),1)
            self.assertEqual(snap['scores'][1],100)
            self.assertFalse(snap['reviews'][0]['ready'])

