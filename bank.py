"""Original exercises. Graded expressions use a deliberately small polynomial grammar."""

import ast
import re
import sympy as s
from courses import units

x = s.Symbol("x", real=True)
bank = {}


def question(
    uid, index, text, tex, answer, reason, hints, choices=(), error="计算或化简有误"
):
    key = f"{uid}-{index}"
    bank[key] = dict(
        id=key,
        unit=uid,
        diagnostic=index == 0,
        level=["诊断", "基础", "基础", "进阶", "挑战"][index],
        text=text,
        tex=tex,
        expected=answer,
        reason=reason,
        hints=hints,
        choices=choices,
        error=error,
        source="内置原创示例",
    )


for i in range(5):
    a = i + 1
    question(
        0,
        i,
        "求极限（角度用弧度）。",
        rf"\lim_{{x\to0}}\frac{{\sin({a}x)}}{{x}}",
        s.Integer(a),
        f"将分母改写为 {a}x，再补上系数 {a}。",
        ["把正弦的自变量视作整体。", "构造 sin(t)/t 的基本极限。"],
    )
    if i == 0:
        question(
            1,
            i,
            "相消后，首个非零项贡献多少？",
            r"\lim_{x\to0}\frac{\sin x-x}{x^3}",
            -s.Rational(1, 6),
            "正弦的一次项消去，三次项系数为 −1/6。",
            ["注意分子的两项相减。", "将正弦展开到三次项。"],
            error="忽略相消后的高阶项",
        )
    else:
        question(
            1,
            i,
            "求无穷小的阶数，即下式中的正整数 k。",
            rf"1-\cos(x^{i})\sim \tfrac12 x^k\quad(x\to0)",
            s.Integer(2 * i),
            f"令 t 为 x 的 {i} 次方，1−cos(t) 与 t²/2 等价。",
            ["先观察余弦自变量。", "把它代入余弦的二次主项。"],
        )
    question(
        2,
        i,
        "怎样取点值 c 才能使函数在断点连续？",
        rf"f(x)=\begin{{cases}}(x^2-{a*a})/(x-{a}),&x\ne {a}\\ c,&x={a}\end{{cases}}",
        s.Integer(2 * a),
        "在去心邻域约去公因子，再将极限作为点值。",
        ["先把分子分解。", "去心邻域内表达式等于两个加数之和。"],
        error="未核对极限与点值",
    )
    question(
        3,
        i,
        "求曲线在指定点的切线斜率。",
        rf"y=x^{a+1},\quad x=2",
        s.Integer((a + 1) * 2**a),
        f"幂法则给出 ({a+1})x^{a}，代入 2。",
        ["切线斜率等于导数。", "先求导，再代入切点。"],
    )
    question(
        4,
        i,
        "写出导数（用 x 表示）。",
        rf"y=({a}x+1)^2",
        s.expand(2 * a * (a * x + 1)),
        f"外层平方求导后，还要乘内层的导数 {a}。",
        ["将括号看作 u。", "使用 2u 乘 u′。"],
        error="链式法则因子遗漏",
    )
    question(
        5,
        i,
        "用微分给出函数增量的一阶估计。",
        rf"y=x^2,\quad x={a},\quad \Delta x=0.01",
        s.Rational(a, 50),
        "一阶估计是 2x 乘自变量增量。",
        ["区分 Δy 和 dy。", "代入 dy=2x dx。"],
        error="混淆函数增量与微分",
    )
    if i == 0:
        question(
            6,
            i,
            "选择应用拉格朗日中值定理的正确顺序。",
            "",
            1,
            "先核对连续与可导条件，计算割线斜率，再寻找导数相等的内点。",
            ["结论取决于区间上的条件。", "平均斜率由两个端点给出。"],
            [
                "任选内点 → 求平均值 → 检验端点",
                "核对条件 → 算割线斜率 → 解内点导数方程",
                "只验端点 → 令导数为零",
            ],
            "定理条件或推导顺序有误",
        )
    else:
        question(
            6,
            i,
            "求满足中值定理等式的内点。",
            rf"f(x)=x^2,\quad x\in[0,{2*i}]",
            s.Integer(i),
            f"割线斜率是 {2*i}，令 2ξ 等于它。",
            ["计算端点差商。", "把平均斜率与内点导数相等。"],
        )
    question(
        7,
        i,
        "求极限，留意能否再次使用洛必达法则。",
        rf"\lim_{{x\to0}}\frac{{e^{{{a}x}}-1-{a}x}}{{x^2}}",
        s.Rational(a * a, 2),
        f"两次都是零比零型，两次分别求导后极限为 {a*a}/2。",
        ["检查第一次求导后的型。", "再对分子分母分别求一次导数。"],
        error="遗漏二阶贡献",
    )
    question(
        8,
        i,
        "写出零点处三阶泰勒多项式（只输入多项式）。",
        rf"f(x)=\ln(1+{a}x)",
        a * x - a * a * x * x / 2 + a**3 * x**3 / 3,
        "把 ax 代入对数展开 t−t²/2+t³/3。三阶 Peano 余项为 o(x³)。",
        ["前两项符号交替。", "三次项来自三阶导数除以 3!。"],
        error="展开系数或符号有误",
    )
    if i == 0:
        question(
            9,
            i,
            "函数在零点附近足够光滑。三阶泰勒多项式的 Peano 余项满足什么性质？",
            "",
            2,
            "误差除以 x³ 趋于零，是局部的阶估计。",
            ["考虑误差与 x³ 的商。", "高阶无穷小描述的是极限性质。"],
            ["误差处处恒为零", "余项恰好等于 x³", "余项为 o(x³)"],
            "混淆恒等式与局部近似",
        )
    else:
        question(
            9,
            i,
            "用拉格朗日余项给出题设能保证的标准误差上界。",
            rf"|f^{{({i+1})}}|\le {(i+1)}!,\quad |x|=\tfrac12,\quad |f(x)-P_{i}(x)|\le\,?",
            s.Rational(1, 2 ** (i + 1)),
            "展开中心为零，导数上界除以阶乘后再乘 |x| 的对应幂。",
            ["使用高一阶导数的区间上界（区间含零与 x）。", "阶乘在题设中恰好约去。"],
        )

# Each final exercise changes the mathematical task as well as its parameters.
question(
    0,
    4,
    "左右极限分别是什么关系？",
    r"f(x)=\frac{|x|}{x},\quad x\to0",
    1,
    "左侧恒为 −1，右侧恒为 1，因此双侧极限不存在。",
    ["按 x 的符号分别化简。", "比较两个单侧极限。"],
    ["都等于 0", "左为 −1，右为 1", "都等于 1"],
    "单侧与双侧极限混淆",
)
question(
    1,
    4,
    "求相消后的首个非零项所决定的极限。",
    r"\lim_{x\to0}\frac{\sin(2x)-2\sin x}{x^3}",
    -s.Integer(1),
    "一次项消去，三次系数是 −8/6+2/6=−1。",
    ["分别展开两个正弦函数。", "保留三次项，注意内层系数也要立方。"],
    error="相消或复合系数有误",
)
question(
    2,
    4,
    "使下列函数在零点连续，a 应取何值？",
    r"f(x)=\begin{cases}\sin(2x)/x,&x<0\\ a,&x=0\\ (e^{2x}-1)/x,&x>0\end{cases}",
    s.Integer(2),
    "两侧基本极限都是 2，因此点值也必须是 2。",
    ["左右两侧使用不同的基本极限。", "再把点值与共同极限相等。"],
)
question(
    3,
    4,
    "求切线方程右侧的多项式 y(x)。",
    r"f(x)=x^3,\quad x_0=-1",
    3 * x + 2,
    "切点是 (−1,−1)，斜率为 3，所以 y+1=3(x+1)。",
    ["求出切点坐标和斜率。", "用点斜式并整理。"],
    error="只给出了斜率或截距错误",
)
question(
    4,
    4,
    "求复合函数在零点的导数值。",
    r"f(x)=\ln(1+e^{2x})",
    s.Integer(1),
    "导数为 2exp(2x)/(1+exp(2x))，零点处等于 1。",
    ["从最外层对数开始。", "连乘指数函数与 2x 的导数。"],
)
question(
    5,
    4,
    "用 x=4 处的线性近似估计下式。",
    r"\sqrt{4.04}\approx\,?",
    s.Rational(201, 100),
    "基点的函数值是 2，导数是 1/4，线性修正是 0.01。",
    ["区分基点值和修正量。", "将基点值与微分相加。"],
)
question(
    6,
    4,
    "在哪个区间可直接对绝对值函数应用拉格朗日中值定理？",
    r"f(x)=|x|",
    2,
    "零点在开区间内会破坏可导性。[0,2] 只要求在端点零处连续。",
    ["注意定理对开区间与闭区间的不同要求。", "检查尖点是不是内点。"],
    ["[−1,1]", "[−2,1]", "[0,2]"],
    "定理适用条件有误",
)
question(
    7,
    4,
    "先将乘积改写为商，再求右极限。",
    r"\lim_{x\to0^+} x\ln x",
    s.Integer(0),
    "写成 ln(x)/(1/x)，求导后的商是 −x，右极限为零。",
    ["原式为零乘无穷型。", "选择能得到无穷比无穷的分母。"],
)
question(
    8,
    4,
    "求 f 在 x=1 处的二阶泰勒多项式（用 x 表示）。",
    r"f(x)=\ln x",
    x - 1 - (x - 1) ** 2 / 2,
    "中心变为 1，对 ln(1+t) 取 t=x−1，保留二阶项。",
    ["令 t=x−1。", "二次项的系数是 f″(1)/2。"],
)
question(
    9,
    4,
    "判断对数展开的正确表述。",
    r"\ln(1+x)=x-x^2/2+x^3/3+R_3(x)",
    1,
    "三阶导数连续保证此处的 Peano 展开，误差相对 x³ 趋于零。",
    ["检查表述的趋近过程。", "多项式截断后仍有高阶误差。"],
    ["对所有 x>−1 余项恒为零", "当 x→0 时余项是 o(x³)", "三次项应归入二阶以下的主项"],
    "误解余项阶数",
)


def public(q):
    return {k: v for k, v in q.items() if k not in ("expected", "reason", "error")}


def polynomial(text):
    text = text.strip().replace("^", "**").replace("−", "-")
    if len(text) > 120 or not re.fullmatch(r"[0-9.x+*/() \-]+", text):
        raise ValueError(
            "请输入含 x、整数或小数的多项式，乘法使用 *，分母须为非零常数。"
        )

    def read(n):
        if isinstance(n, ast.Name) and n.id == "x":
            return x
        if isinstance(n, ast.Constant) and type(n.value) in (int, float):
            return s.Rational(str(n.value))
        if isinstance(n, ast.UnaryOp) and isinstance(n.op, (ast.USub, ast.UAdd)):
            v = read(n.operand)
            return -v if isinstance(n.op, ast.USub) else v
        if isinstance(n, ast.BinOp):
            a, b = read(n.left), read(n.right)
            if isinstance(n.op, ast.Add):
                v = a + b
            elif isinstance(n.op, ast.Sub):
                v = a - b
            elif isinstance(n.op, ast.Mult):
                v = a * b
            elif isinstance(n.op, ast.Div) and b.is_Rational and b != 0:
                v = a / b
            elif isinstance(n.op, ast.Pow) and b.is_Integer and 0 <= b <= 8:
                v = a**b
            else:
                raise ValueError("分母须为非零常数，指数限 0 至 8。")
            v = s.Poly(v, x)
            if v.degree() > 12 or any(
                max(abs(c.p).bit_length(), c.q.bit_length()) > 512
                for c in v.all_coeffs()
            ):
                raise ValueError("表达式超出练习范围。")
            return v.as_expr()
        raise ValueError("无法识别此表达式。")

    try:
        return read(ast.parse(text, mode="eval").body)
    except (SyntaxError, TypeError, ZeroDivisionError):
        raise ValueError("请检查表达式格式。") from None


def grade(key, answer):
    q = bank[key]
    if q["choices"]:
        if answer not in [str(i) for i in range(len(q["choices"]))]:
            raise ValueError("请选择一个选项。")
        return int(answer) == q["expected"]
    return s.expand(polynomial(answer) - q["expected"]) == 0
