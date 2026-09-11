#!/usr/bin/env python3
"""코드 과제의 숨은 테스트.

경계 조건을 얼마나 챙겼는지가 여기서 갈린다. 뻔한 입력은 양쪽 다 맞히므로
빈 입력, 맞닿는 구간, 안정 정렬, 멀티바이트 글자, 루트 위로 올라가는 .. 을 넣었다.

이 파일은 두 가지로 쓴다.
  python3 code_tests.py --self    참조 구현으로 테스트 자체가 맞는지 본다 (측정 도구 점검)
  grade_code.py 가 import 해서 모델이 쓴 코드를 채점한다
"""
from __future__ import annotations

import re
import sys

# 각 항목은 (설명, 호출 가능한 검사). 검사는 참/거짓을 낸다. 예외가 나면 실패다.
CASES: dict[str, list] = {}


def raises(fn, exc=ValueError):
    try:
        fn()
    except exc:
        return True
    except Exception:
        return False
    return False


CASES["merge_intervals"] = [
    ("빈 입력", lambda f: list(f([])) == []),
    ("겹치는 것 합치기", lambda f: [tuple(x) for x in f([(1, 3), (2, 6), (8, 10), (15, 18)])]
     == [(1, 6), (8, 10), (15, 18)]),
    ("정렬 안 된 입력", lambda f: [tuple(x) for x in f([(8, 10), (1, 3), (2, 6)])]
     == [(1, 6), (8, 10)]),
    ("끝이 맞닿으면 합친다", lambda f: [tuple(x) for x in f([(1, 3), (3, 5)])] == [(1, 5)]),
    ("완전히 포함", lambda f: [tuple(x) for x in f([(1, 10), (2, 3)])] == [(1, 10)]),
    ("길이 0 구간", lambda f: [tuple(x) for x in f([(5, 5)])] == [(5, 5)]),
    ("원본을 바꾸지 않는다", lambda f: (lambda a: (f(a), a == [(3, 4), (1, 2)])[1])([(3, 4), (1, 2)])),
]

CASES["parse_duration"] = [
    ("1h30m", lambda f: f("1h30m") == 5400),
    ("45s", lambda f: f("45s") == 45),
    ("2d", lambda f: f("2d") == 172800),
    ("공백 섞임", lambda f: f("1h 30m 10s") == 5410),
    ("0s", lambda f: f("0s") == 0),
    ("빈 문자열은 ValueError", lambda f: raises(lambda: f(""))),
    ("글자만은 ValueError", lambda f: raises(lambda: f("abc"))),
    ("모르는 단위는 ValueError", lambda f: raises(lambda: f("1x"))),
    ("단위 없는 숫자는 ValueError", lambda f: raises(lambda: f("30"))),
]

CASES["chunk_by_bytes"] = [
    ("빈 입력", lambda f: f([], 10) == []),
    ("한 묶음에 들어간다", lambda f: f(["a", "b"], 10) == [["a", "b"]]),
    ("넘치면 나눈다", lambda f: f(["aaaa", "bbbb"], 5) == [["aaaa"], ["bbbb"]]),
    ("혼자서도 넘치면 혼자 간다", lambda f: f(["aaaaaaa"], 3) == [["aaaaaaa"]]),
    ("한글은 3바이트", lambda f: f(["가", "나"], 3) == [["가"], ["나"]]),
    ("한글 둘이 6바이트", lambda f: f(["가", "나"], 6) == [["가", "나"]]),
    ("limit 0 은 ValueError", lambda f: raises(lambda: f(["a"], 0))),
    ("limit 음수는 ValueError", lambda f: raises(lambda: f(["a"], -1))),
]

CASES["normalize_path"] = [
    ("절대 경로의 ..", lambda f: f("/a/b/../c") == "/a/c"),
    ("루트 위로는 못 간다", lambda f: f("/../a") == "/a"),
    ("점과 끝 슬래시", lambda f: f("a/./b/") == "a/b"),
    ("연속 슬래시", lambda f: f("//a//b") == "/a/b"),
    ("상대 경로의 .. 는 남는다", lambda f: f("../a") == "../a"),
    ("루트", lambda f: f("/") == "/"),
    ("빈 문자열", lambda f: f("") == "."),
    ("상대가 비면 점", lambda f: f("a/..") == "."),
    ("절대가 비면 루트", lambda f: f("/a/..") == "/"),
]

CASES["topk_by"] = [
    ("큰 순서로 둘", lambda f: list(f([3, 1, 2], lambda x: x, 2)) == [3, 2]),
    ("같은 값은 원래 순서", lambda f: list(f(
        [("a", 1), ("b", 1), ("c", 2)], lambda t: t[1], 3)) == [("c", 2), ("a", 1), ("b", 1)]),
    ("k 가 길이보다 크다", lambda f: list(f([1, 2], lambda x: x, 5)) == [2, 1]),
    ("k 가 0", lambda f: list(f([1, 2], lambda x: x, 0)) == []),
    ("k 가 음수", lambda f: list(f([1, 2], lambda x: x, -1)) == []),
    ("빈 입력", lambda f: list(f([], lambda x: x, 3)) == []),
    ("원본을 바꾸지 않는다", lambda f: (lambda a: (f(a, lambda x: x, 1), a == [1, 3, 2])[1])([1, 3, 2])),
]

TASK_FUNC = {
    "E1": "merge_intervals",
    "E2": "parse_duration",
    "E3": "chunk_by_bytes",
    "E4": "normalize_path",
    "E5": "topk_by",
}


def run(func_name, fn):
    """(통과 수, 전체 수, 실패한 항목 이름들)"""
    cases = CASES[func_name]
    failed = []
    for name, check in cases:
        try:
            ok = bool(check(fn))
        except Exception:
            ok = False
        if not ok:
            failed.append(name)
    return len(cases) - len(failed), len(cases), failed


# --------------------------------------------------------------------------
# 참조 구현. 테스트가 맞는지 확인하는 용도이고 채점에는 쓰지 않는다.
# --------------------------------------------------------------------------
def _ref_merge_intervals(intervals):
    xs = sorted((tuple(i) for i in intervals), key=lambda t: (t[0], t[1]))
    out = []
    for s, e in xs:
        if out and s <= out[-1][1]:
            out[-1] = (out[-1][0], max(out[-1][1], e))
        else:
            out.append((s, e))
    return out


def _ref_parse_duration(text):
    if not isinstance(text, str) or not text.strip():
        raise ValueError("빈 값")
    s = text.replace(" ", "")
    if not re.fullmatch(r"(?:\d+[dhms])+", s):
        raise ValueError(f"형식이 아니다: {text}")
    unit = {"d": 86400, "h": 3600, "m": 60, "s": 1}
    return sum(int(n) * unit[u] for n, u in re.findall(r"(\d+)([dhms])", s))


def _ref_chunk_by_bytes(items, limit):
    if limit <= 0:
        raise ValueError("limit 은 양수여야 한다")
    out, cur, size = [], [], 0
    for it in items:
        b = len(it.encode("utf-8"))
        if cur and size + b > limit:
            out.append(cur)
            cur, size = [], 0
        cur.append(it)
        size += b
        if size > limit:
            out.append(cur)
            cur, size = [], 0
    if cur:
        out.append(cur)
    return out


def _ref_normalize_path(p):
    absolute = p.startswith("/")
    parts = []
    for seg in p.split("/"):
        if seg in ("", "."):
            continue
        if seg == "..":
            if parts and parts[-1] != "..":
                parts.pop()
            elif not absolute:
                parts.append("..")
            continue
        parts.append(seg)
    joined = "/".join(parts)
    if absolute:
        return "/" + joined if joined else "/"
    return joined if joined else "."


def _ref_topk_by(items, key, k):
    if k <= 0:
        return []
    order = sorted(range(len(items)), key=lambda i: (-key(items[i]), i))
    return [items[i] for i in order[:k]]


REFS = {
    "merge_intervals": _ref_merge_intervals,
    "parse_duration": _ref_parse_duration,
    "chunk_by_bytes": _ref_chunk_by_bytes,
    "normalize_path": _ref_normalize_path,
    "topk_by": _ref_topk_by,
}

if __name__ == "__main__":
    if "--self" not in sys.argv:
        print("사용: python3 code_tests.py --self")
        sys.exit(2)
    bad = 0
    for name, fn in REFS.items():
        ok, total, failed = run(name, fn)
        mark = "o" if ok == total else "X"
        print(f"  {mark} {name}: {ok}/{total}" + (f"  실패 {failed}" if failed else ""))
        if ok != total:
            bad = 1
    print("\n참조 구현이 전부 통과한다. 테스트를 믿을 수 있다." if not bad
          else "\n테스트가 틀렸다. 채점에 쓰기 전에 고쳐라.")
    sys.exit(bad)
