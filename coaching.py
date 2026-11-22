"""Evidence collected after an objective attempt. Students confirm their own strategy."""
import json
from functools import lru_cache
from hashlib import sha256
import sympy as s
from bank import bank, polynomial, x
from learning import db
from model_studio import dialogue

METHODS = {
    "substitution": "我在分子中把 sin(x) 换成了 x",
    "expansion": "我写了展开式，但不确定应保留哪一阶",
    "calculation": "我用了定义或公式，可能算错了",
    "unsure": "我还不确定",
}
def ensure_evidence(c):
    c.execute("CREATE TABLE IF NOT EXISTS study_evidence(attempt INTEGER PRIMARY KEY, payload TEXT)")

def initial(steps="", hints=0):
    if not isinstance(steps,str) or len(steps)>800 or type(hints)!=int or not 0<=hints<=2:
        raise ValueError("解题步骤或提示记录无效。")
    return dict(steps=steps,hints=hints,method="",trials=[],conversation=[])

def save(c,attempt,evidence):
    c.execute("INSERT OR REPLACE INTO study_evidence VALUES(?,?)",(attempt,json.dumps(evidence,ensure_ascii=False)))

def read_attempt(c,attempt):
    if type(attempt)!=int: raise ValueError("作答编号无效。")
    row=c.execute("SELECT a.*,e.payload FROM attempts a LEFT JOIN study_evidence e ON e.attempt=a.id WHERE a.id=?",(attempt,)).fetchone()
    if row is None: raise ValueError("找不到此次作答。")
    return row,json.loads(row["payload"]) if row["payload"] else initial()

def next_level(e):
    if not e["trials"]: return 2 if e["method"]=="expansion" else 1
    last=e["trials"][-1]
    return min(3,last["level"]+1) if last["ok"] else max(1,last["level"]-1)

@lru_cache(maxsize=300)
def variant(unit,level,a):
    """Generate a fresh parameterized problem and independently derive its answer."""
    if unit==7:
        poly=s.exp(a*x).series(x,0,level).removeO()
        f=(s.exp(a*x)-poly)/x**level
        return s.latex(s.Limit(f,x,0)),s.limit(f,x,0),"检查不定式类型，再比较足够阶数的导数。"
    if unit==8:
        degree=level+1
        f=s.log(1+a*x)
        return rf"f(x)=\ln(1+{a}x),\quad P_{{{degree}}}(x;0)=?",f.series(x,0,degree+1).removeO(),"逐阶匹配在原点的导数，留意内层系数。"
    if unit==9:
        n=level+1
        return rf"|f^{{({n})}}|\le {n}!,\ |x|=1/{a},\quad |R_{{{n-1}}}(x;0)|\le\,?",s.Rational(1,a**n),"用高一阶导数的区间上界估算拉格朗日余项。"
    if unit in (0,1):
        if level==1:
            f=s.sin(a*x)/x
            return rf"\lim_{{x\to0}}\frac{{\sin({a}x)}}x",s.limit(f,x,0),"用基本极限核对一次项。"
        if level==2:
            f=(s.sin(a*x)-a*x)/x**3
            return rf"\lim_{{x\to0}}\frac{{\sin({a}x)-{a}x}}{{x^3}}",s.limit(f,x,0),"一次项消去，比较两边三次项的系数。"
        correction=s.Rational(a**3,6)*x**3
        f=(s.sin(a*x)-a*x+correction)/x**5
        return rf"\lim_{{x\to0}}\frac{{\sin({a}x)-{a}x+({a}x)^3/6}}{{x^5}}",s.limit(f,x,0),"一次和三次项均已消去，继续到五次。"
    if unit==2:
        f=(x**(level+1)-a**(level+1))/(x-a)
        return rf"\lim_{{x\to {a}}}\frac{{x^{level+1}-{a**(level+1)}}}{{x-{a}}}",s.limit(f,x,a),"先消去公因子再确定连续延拓的点值。"
    if unit==5:
        return rf"y=x^{level+1},\quad x={a},\quad dx=0.01,\quad dy=?",s.diff(x**(level+1),x).subs(x,a)/100,"用基点处导数乘自变量增量。"
    if unit==6:
        return rf"f(x)=x^{level+1},\ [0,{a}]:\quad f'(\xi)=?",s.Integer(a)**level,"中值定理给出内点导数等于端点割线斜率。"
    f=(a*x+1)**(level+1)
    return rf"f(x)=({a}x+1)^{level+1},\quad f'(1)=?",s.diff(f,x).subs(x,1),"外层幂函数求导后，乘以内层导数。"

def topic_family(key):
    return key=="1-0" or key=="1-4"

def guidance(key,method,answer):
    if topic_family(key):
        if method=="substitution":
            return "按你确认的这一步，替换改变了相减后的首个非零项。若只知道 sin(x)/x 趋于 1，能否知道二者相差到几阶？先在变式中校准一次项。"
        if method=="expansion":
            return "你选择了展开法。把分子写成一次项、三次项和余项，逐项划掉相消的部分；再检查余项除以分母后是否趋于零。"
        if key=="1-0" and not method:
            value=polynomial(answer)
            if value==0: return "结果为零有多种可能：把等价替换用于差，或在一次项处截断了展开。你当时保留到了哪一项？"
            if value==s.Rational(1,6): return "结果的绝对值与参考结果一致，可以先检查三阶项的符号。还需对照你的步骤确定原因。"
    if method=="calculation": return "先用简单参数核验符号和系数，再把同一方法带回原题。一次误答尚不足以定位是哪一步算错。"
    return "先把已知条件和要比较的量分别写下。用一个较短的变式查明需要补的是概念还是运算。"

def task_for(row,e):
    index=len(e["trials"])
    if index>=30: raise ValueError("本次作答已积累 30 条变式记录，请回到单元开始新练习。")
    level=next_level(e)
    a=2+int(sha256(f"{row['id']}:{row['q']}:{index}".encode()).hexdigest()[:8],16)%8
    tex,expected,reason=variant(bank[row["q"]]["unit"],level,a)
    return dict(index=index,level=level,param=a,tex=tex),expected,reason

def session(data):
    attempt=data.get("attempt")
    with db() as c:
        c.execute("BEGIN IMMEDIATE")
        ensure_evidence(c)
        row,e=read_attempt(c,attempt)
        method=data.get("method")
        if method is not None:
            if method not in METHODS or (method in ("substitution","expansion") and not topic_family(row["q"])): raise ValueError("请选择适用的方法。")
            e["method"]=method
        result=None
        if "answer" in data:
            task,expected,reason=task_for(row,e)
            if data.get("index")!=task["index"]: raise ValueError("这道变式已更新，请重新打开练习。")
            answer=data["answer"]
            if not isinstance(answer,str) or len(answer)>120: raise ValueError("答案无效。")
            ok=bool(s.expand(polynomial(answer)-expected)==0)
            result={**task,"answer":answer,"ok":ok,"reason":reason}
            e["trials"].append(result)
        save(c,attempt,e)
        next_task=task_for(row,e)[0] if len(e["trials"])<30 else None
    return dict(task=next_task,result=result,guidance=guidance(row["q"],e["method"],row["answer"]),evidence=e)

def tutor_chat(data):
    attempt=data["attempt"]
    with db() as c:
        ensure_evidence(c);row,e=read_attempt(c,attempt)
    q=bank[row["q"]]
    ctx=dict(question=q["text"],formula=q["tex"],answer=row["answer"],checked=bool(row["ok"]),steps=e["steps"],method=METHODS.get(e["method"],""),hint_count=e["hints"],last_trials=e["trials"][-2:],previous=e["conversation"][-2:])
    # Bound the exact context; the client displays this string before authorizing it.
    context=json.dumps(ctx,ensure_ascii=False)[:2400]
    if data.get("preview") is True: return dict(context=context)
    if data.get("context")!=context: raise ValueError("学习记录已改变，请重新预览发送内容。")
    reply=dialogue(dict(context=context,question=data["question"],consent=data.get("consent")))
    with db() as c:
        c.execute("BEGIN IMMEDIATE")
        _,e=read_attempt(c,attempt)
        e["conversation"]=(e["conversation"]+[dict(question=data["question"],answer=reply["answer"],meta=reply["meta"])])[-8:]
        save(c,attempt,e)
    return reply


def checked_backup(key,raw):
    if not isinstance(raw,dict): raise ValueError("学习证据无效。")
    result=initial(raw.get("steps",""),raw.get("hints",0))
    method=raw.get("method","")
    if method and method not in METHODS: raise ValueError("未知学习方法。")
    result["method"]=method
    trials=raw.get("trials",[])
    if not isinstance(trials,list) or len(trials)>30: raise ValueError("变式记录无效。")
    for i,t in enumerate(trials):
        level,param=t["level"],t["param"]
        if type(level)!=int or level not in (1,2,3) or type(param)!=int or not 2<=param<=9: raise ValueError("变式参数无效。")
        tex,expected,reason=variant(bank[key]["unit"],level,param)
        answer=t["answer"]
        if not isinstance(answer,str) or len(answer)>120: raise ValueError("变式答案无效。")
        result["trials"].append(dict(index=i,level=level,param=param,tex=tex,reason=reason,answer=answer,ok=bool(s.expand(polynomial(answer)-expected)==0)))
    chat=raw.get("conversation",[])
    if not isinstance(chat,list) or len(chat)>8: raise ValueError("对话记录无效。")
    for pair in chat:
        q,a=pair["question"],pair["answer"]
        if not isinstance(q,str) or len(q)>400 or not isinstance(a,str) or len(a)>3500: raise ValueError("对话过长。")
        result["conversation"].append(dict(question=q,answer=a))
    return result
