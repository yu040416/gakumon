"""テストの問題をテンプレートから作る。正解はPythonで計算する。

答えはすべて整数にしてある(入力のしかたで迷わないように)。
"""

import random
import unicodedata


def _num(n):
    """負の数はかっこをつける:-3 → (-3)"""
    return f"({n})" if n < 0 else str(n)


def _lin(a, b):
    """a x + b の形の文字列"""
    if b >= 0:
        return f"{a}x + {b}"
    return f"{a}x − {abs(b)}"


def _nonzero(rng, lo, hi):
    n = 0
    while n == 0:
        n = rng.randint(lo, hi)
    return n


# ===== 単元1:正負の数 =====

def _add(rng):
    a, b = _nonzero(rng, -9, 9), _nonzero(rng, -9, 9)
    return f"{_num(a)} + {_num(b)} を計算しなさい。", a + b, "正負の数の加法"


def _sub(rng):
    a, b = _nonzero(rng, -9, 9), _nonzero(rng, -9, 9)
    return f"{_num(a)} − {_num(b)} を計算しなさい。", a - b, "正負の数の減法"


def _mul(rng):
    a, b = _nonzero(rng, -9, 9), _nonzero(rng, -9, 9)
    return f"{_num(a)} × {_num(b)} を計算しなさい。", a * b, "正負の数の乗法"


def _div(rng):
    b, q = _nonzero(rng, -9, 9), _nonzero(rng, -9, 9)
    return f"{_num(b * q)} ÷ {_num(b)} を計算しなさい。", q, "正負の数の除法"


# ===== 単元2:文字と式 =====

def _eval1(rng):
    a, b, x = rng.randint(2, 9), _nonzero(rng, -9, 9), _nonzero(rng, -5, 5)
    return (f"x = {x} のとき、{_lin(a, b)} の値を求めなさい。", a * x + b,
            "文字式の値(1次式)")


def _eval2(rng):
    c, d, v = _nonzero(rng, -9, 9), rng.randint(2, 9), _nonzero(rng, -5, 5)
    return (f"a = {v} のとき、{c} − {d}a の値を求めなさい。", c - d * v,
            "文字式の値(ひき算)")


# ===== 単元3:方程式 =====

def _eq1(rng):
    a, b, x = rng.randint(2, 9), _nonzero(rng, -9, 9), _nonzero(rng, -9, 9)
    return f"方程式 {_lin(a, b)} = {a * x + b} を解きなさい。(x = ?)", x, "1次方程式(基本)"


def _eq2(rng):
    x = _nonzero(rng, -9, 9)
    a = rng.randint(3, 9)
    c = rng.randint(1, a - 1)
    b = _nonzero(rng, -9, 9)
    d = (a - c) * x + b
    left = _lin(a, b)
    right = _lin(c, d)
    return f"方程式 {left} = {right} を解きなさい。(x = ?)", x, "1次方程式(両辺に文字)"


TEMPLATES = {
    1: [("add", _add), ("sub", _sub), ("mul", _mul), ("div", _div)],
    2: [("eval1", _eval1), ("eval2", _eval2)],
    3: [("eq1", _eq1), ("eq2", _eq2)],
}


def generate_test(unit_id, count, rng=None):
    """count問の問題を作る。同じ問題文は出さない。
    戻り値: [{template_key, text, answer(文字列), summary}, ...]
    """
    rng = rng or random.Random()
    templates = TEMPLATES[unit_id]
    items, seen = [], set()
    i = 0
    while len(items) < count:
        key, fn = templates[i % len(templates)]   # テンプレートを順番にまわす
        i += 1
        text, answer, summary = fn(rng)
        if text in seen:
            continue
        seen.add(text)
        items.append({"template_key": key, "text": text,
                      "answer": str(answer), "summary": summary})
    return items


def normalize_answer(s):
    """答えを比べる前にそろえる(全角→半角、マイナス記号、空白、「x=」)"""
    if s is None:
        return ""
    s = unicodedata.normalize("NFKC", str(s))
    for ch in ("−", "ー", "―", "－"):
        s = s.replace(ch, "-")
    s = s.replace(" ", "").replace("　", "").lower()
    if s.startswith("x="):
        s = s[2:]
    return s


def is_same_answer(a, b):
    return normalize_answer(a) == normalize_answer(b)
