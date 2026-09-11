#!/usr/bin/env python3
"""디바운스 설명의 세부 11항목이 답에 나왔는지 조건을 모르는 판정자에게 묻고 조건별로 모은다 (EVALUATION.md H13).

정규식으로 세지 않는다. 처음에 그렇게 했다가 「중간 글자들」·「전부 살아남아」 같은 표현을 놓쳐
8점짜리 답을 5점으로 셌다.

usage: judge.py      out/<조건>_<표본>.json 을 전부 채점한다. 판정은 judge/ 에 캐시한다.
       조건 A 가 있으면 다른 조건을 그것과 견줘 순열검정과 기본값 항목의 Fisher 검정을 낸다.
"""
import concurrent.futures as cf
import itertools
import json
import math
import pathlib
import random
import re
import statistics
import subprocess
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "out"
JUDGE = HERE / "judge"
JUDGE.mkdir(exist_ok=True)

ITEMS = {
    "default300": "delay 의 기본값이 300ms 라는 점",
    "usecase": "쓰임새 예시(검색어 입력, API 호출 줄이기 등)",
    "cleanup_before_next": "cleanup 이 다음 effect 가 실행되기 직전에 호출된다는 점",
    "cleanup_unmount": "cleanup 이 컴포넌트 언마운트 때도 호출된다는 점",
    "pileup": "cleanup 이 없으면 이전 타이머들이 취소되지 않고 남아 각각 실행된다는 점",
    "stale": "그 결과 중간 값이나 옛 값이 debounced 에 잠깐이라도 반영된다는 점",
    "rerender": "그 결과 불필요한 리렌더(재렌더)가 생긴다는 점",
    "unmount_setstate": "언마운트 뒤에 setState 가 호출되는 문제(경고·누수)",
    "delay_dep": "delay 가 바뀌어도 effect 가 다시 돌아 타이머를 새로 건다는 점(의존성에 delay 포함)",
    "last_only": "결국 마지막 값(마지막 타이머) 하나만 반영된다는 점",
    "concrete_example": "구체적인 입력 순서나 시각을 들어 보인 예시(예: 'r'→'re', t=0/t=100)",
}

PROMPT = """아래 [답변]은 React 훅 useDebouncedValue 를 설명한 글이다. 도구는 없다. 답변만 보고 판정하라.
각 항목이 답변에 **실제로 설명되어 있는지** true/false 로 판정한다. 표현이 달라도 뜻이 같으면 true, 암시만 하고 말하지 않았으면 false.
글의 문체나 품질은 판정하지 않는다.

항목:
{items}

JSON 객체 하나만 출력한다. 키는 위 항목 id, 값은 true/false. 다른 말은 쓰지 않는다.

[답변]
{answer}
"""


def hangul(t):
    return len(re.findall(r"[가-힣]", t))


def judge(name, text):
    cache = JUDGE / f"{name}.json"
    if cache.exists():
        return name, json.loads(cache.read_text())
    items = "\n".join(f"- {k}: {v}" for k, v in ITEMS.items())
    with tempfile.TemporaryDirectory() as neutral:
        r = subprocess.run(
            ["claude", "-p", PROMPT.format(items=items, answer=text), "--no-session-persistence",
             "--tools", "", "--strict-mcp-config", "--setting-sources", "", "--model", "claude-opus-5",
             "--output-format", "json"],
            cwd=neutral, stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=300)
    try:
        res = json.loads(r.stdout).get("result", "")
    except Exception:
        res = r.stdout
    m = re.search(r"\{.*\}", res, re.S)
    if not m:
        print(f"파싱 실패 {name}: {res[:200]!r}")
        return name, None
    v = json.loads(m.group(0))
    if set(v) != set(ITEMS):
        print(f"키 불일치 {name}: {sorted(v)}")
        return name, None
    cache.write_text(json.dumps(v, ensure_ascii=False))
    return name, v


def perm_p(a, b, rounds=20000):
    """합계 차이에 대한 양측 순열검정. 경우의 수가 작으면 전수, 크면 무작위로 뽑는다."""
    pool, na = a + b, len(a)
    obs = abs(sum(a) / len(a) - sum(b) / len(b))
    total = sum(pool)
    combos = math.comb(len(pool), na)
    if combos <= 50000:
        it = (sum(pool[i] for i in idx) for idx in itertools.combinations(range(len(pool)), na))
        n = combos
    else:
        rng = random.Random(0)
        it = (sum(rng.sample(pool, na)) for _ in range(rounds))
        n = rounds
    hit = sum(1 for sa in it if abs(sa / na - (total - sa) / (len(pool) - na)) >= obs - 1e-12)
    return hit / n


def fisher_p(a, b, c, d):
    """2x2 표 [[a, b], [c, d]] 의 양측 Fisher 정확 검정."""
    n, r1, c1 = a + b + c + d, a + b, a + c

    def pr(x):
        return math.comb(r1, x) * math.comb(n - r1, c1 - x) / math.comb(n, c1)

    p0 = pr(a)
    return sum(pr(x) for x in range(max(0, c1 - (n - r1)), min(r1, c1) + 1) if pr(x) <= p0 + 1e-12)


answers = {}
for p in sorted(OUT.glob("*.json")):
    text = json.loads(p.read_text()).get("result") or ""
    # 계정 사용량이 떨어지면 답 자리에 안내 문구가 들어온다. 세지 않고 이름을 찍는다.
    if hangul(text) < 150:
        print(f"답이 아닌 표본: {p.name}")
        continue
    answers[p.stem] = text

with cf.ThreadPoolExecutor(4) as ex:
    got = {k: v for k, v in ex.map(lambda kv: judge(*kv), answers.items()) if v is not None}

groups = {}
for name in sorted(got):
    groups.setdefault(name.rsplit("_", 1)[0], []).append(name)

for g, ns in sorted(groups.items()):
    per = [sum(got[n].values()) for n in ns]
    print(f"[{g}] 표본 {len(ns)}  항목 {sum(per)}/{len(ns) * len(ITEMS)} ({sum(per) / (len(ns) * len(ITEMS)):.0%})"
          f"  표본별 {per}  한글 중앙값 {statistics.median(hangul(answers[n]) for n in ns):.0f}")
    for k in ITEMS:
        print(f"    {k:20} {sum(got[n][k] for n in ns)}/{len(ns)}")

if "A" in groups:
    base = groups["A"]
    ta = [sum(got[n].values()) for n in base]
    da = sum(got[n]["default300"] for n in base)
    for g, ns in sorted(groups.items()):
        if g == "A":
            continue
        tb = [sum(got[n].values()) for n in ns]
        db = sum(got[n]["default300"] for n in ns)
        print(f"A 대 {g}: 순열검정 p={perm_p(ta, tb):.3f}   default300 {da}/{len(base)} 대 {db}/{len(ns)}"
              f" Fisher p={fisher_p(da, len(base) - da, db, len(ns) - db):.3f}")
