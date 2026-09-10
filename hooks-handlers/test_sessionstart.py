#!/usr/bin/env python3
"""sessionstart.sh 회귀 테스트.

pytest 없이 assert 만 쓴다. 실행: python3 hooks-handlers/test_sessionstart.py

이 훅은 판정하지 않고 주입만 한다. 그래서 검사할 것은 세 가지다.
무엇이 나오는가, 끄면 안 나오는가, 무슨 일이 있어도 세션을 막지 않는가.

크기 상한도 함께 잡는다. 규칙이 한 줄씩 늘어나면 상시 비용이 조용히 커진다.
EVALUATION.md 의 D2 가 그 예산이고, 여기서 회귀를 잡는다.
"""
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
HOOK = HERE / "sessionstart.sh"
RULES = HERE / "always-on.md"
MARK = "korean-writing: ignore"

# 주입문 한글 상한. 현재 402 자다.
# 올리려면 EVALUATION.md 의 D2 예산을 먼저 고치고 실측을 남긴다.
# 2026-09-10 에 연결어미 쉼표·부정 대구 한 줄을 더하며 400 에서 420 으로 올렸다.
# 그 줄의 효과와 올린 뒤의 실측 비용은 EVALUATION.md 의 C8 에 있다.
MAX_HANGUL = 420

# 규칙 항목. 하나가 조용히 빠지면 잡는다.
REQUIRED = [
    "높임",
    "주어는 사람이나 조직",
    "축·갈래·결·레이어",
    "연결어미 뒤 쉼표",
    "대구를 잇지 않는다",
    "줄표",
    "번역투 금지",
    "AI 관용구 금지",
    "문장 길이",
    "계약서·약관은 예외",
    "korean-writing 스킬을 먼저 로드",
]

FAILS = []


def run(env=None, stdin=""):
    full = {**os.environ, **env} if env else None
    p = subprocess.run(
        [str(HOOK)], input=stdin, capture_output=True, text=True, env=full, timeout=10
    )
    return p.returncode, p.stdout, p.stderr


def check(name, cond, detail=""):
    if cond:
        print(f"  o {name}")
    else:
        FAILS.append(f"{name}: {detail}")
        print(f"  X {name}  {detail}")


print("주입문을 낸다")
rc, out, err = run()
check("종료 코드 0", rc == 0, f"rc={rc} err={err.strip()[:120]}")
check("규칙이 나온다", "[korean-writing]" in out, f"머리 40자: {out[:40]!r}")
check("stderr 는 비어 있다", err.strip() == "", f"err={err.strip()[:120]}")

print("\n주입문에 들어가면 안 되는 것")
check(
    "제외 표시가 빠진다",
    MARK not in out,
    "이 표시가 주입되면 모델이 지시문으로 읽는다",
)
check("파일에는 제외 표시가 있다", MARK in RULES.read_text(encoding="utf-8"))

print("\n규칙 항목이 남아 있다")
for token in REQUIRED:
    check(f"'{token}'", token in out)

print("\n크기 상한")
hangul = len(re.findall(r"[가-힣]", out))
check(
    f"한글 {hangul}자 <= {MAX_HANGUL}",
    hangul <= MAX_HANGUL,
    "상시 비용이 커졌다. EVALUATION.md 의 D2 를 먼저 고쳐라",
)

print("\n끄면 안 나온다")
for var in ("KOREAN_WRITING_HOOK_DISABLED", "KOREAN_WRITING_ALWAYS_ON_DISABLED"):
    rc, out2, _ = run(env={var: "1"})
    check(f"{var}=1", rc == 0 and out2 == "", f"rc={rc} out={out2[:60]!r}")

rc, out2, _ = run(env={"KOREAN_WRITING_HOOK_DISABLED": "0"})
check("0 은 끄지 않는다", rc == 0 and "[korean-writing]" in out2, f"rc={rc}")

print("\n무슨 일이 있어도 세션을 막지 않는다")
rc, out2, _ = run(stdin='{"hook_event_name":"SessionStart","source":"startup"}')
check("stdin 을 줘도 같다", rc == 0 and out2 == out, f"rc={rc}")

tmp = tempfile.mkdtemp()
try:
    shutil.copy(HOOK, pathlib.Path(tmp) / "sessionstart.sh")
    p = subprocess.run(
        [str(pathlib.Path(tmp) / "sessionstart.sh")],
        input="",
        capture_output=True,
        text=True,
        timeout=10,
    )
    check(
        "규칙 파일이 없어도 exit 0",
        p.returncode == 0 and p.stdout == "",
        f"rc={p.returncode} out={p.stdout[:60]!r}",
    )
finally:
    shutil.rmtree(tmp, ignore_errors=True)

print("\n같은 규칙이 놓인 세 곳이 어긋나지 않았는가")
# 규칙 본문은 SKILL.md 한 곳이 정본이지만, 사본이 둘 더 필요하다. 상시 규칙은 스킬이
# 안 뜨는 평소 답변을 맡고, CLAUDE.md 는 훅도 스킬도 전달되지 않는 서브에이전트를 맡는다
# (EVALUATION.md N1 실측). 플랫폼이 강요한 중복이라 없앨 수는 없고, 어긋나는 것만 막는다.
# 실사고: 2026-09-10 에 대구·연결어미 쉼표를 SKILL.md 와 상시 규칙에만 넣고 CLAUDE.md 를
# 빠뜨렸다. 실측 최강 신호 둘이 서브에이전트에만 안 걸린 채로 남을 뻔했다.
_ROOT = HERE.parent
# 항목마다 표지를 여럿 둔다. 세 문서가 같은 규칙을 다른 문장으로 쓰기 때문이다.
# 상시 규칙은 "사람처럼 행동시키지 않는다" 로, SKILL.md 는 "사물 의인화" 로 적는다.
_CORE = [
    ("대구", ("대구",)),
    ("연결어미 뒤 쉼표", ("연결어미",)),
    ("줄표", ("줄표",)),
    ("사물 의인화", ("의인화", "사람처럼")),
    ("추상 구조어", ("축·갈래·결·레이어", "축·갈래")),
    ("번역투", ("번역투",)),
    ("AI 관용구", ("AI 관용구", "관용구")),
]
_COPIES = [("상시 규칙", RULES), ("CLAUDE.md", _ROOT / "CLAUDE.md")]
_skill = (_ROOT / "SKILL.md").read_text(encoding="utf-8")
for label, path in _COPIES:
    body = path.read_text(encoding="utf-8")
    missing = [
        name for name, keys in _CORE
        if any(k in _skill for k in keys) and not any(k in body for k in keys)
    ]
    check(
        f"{label} 에 핵심 항목이 다 있다",
        not missing,
        f"빠진 항목: {missing}",
    )

print()
if FAILS:
    print(f"실패 {len(FAILS)}건")
    for f in FAILS:
        print(f"  - {f}")
    sys.exit(1)
print("전부 통과")
