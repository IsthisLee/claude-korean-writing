#!/usr/bin/env python3
"""pretooluse-skill.sh 회귀 테스트.

pytest 없이 돈다. 실행: python3 tests/test_pretooluse.py

이 훅은 모델이 korean-writing 스킬을 스스로 부를 때만 사용자에게 적용할지 묻게 한다.
다른 스킬과 다른 도구는 그대로 지나보내야 하고, 어떤 입력에도 작업을 막으면 안 된다.
첫 실패에서 멈추지 않고 전부 모아 보고한다.
"""
import json
import os
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent
# 릴리스 zip 을 풀어 그것을 대고 돌릴 때는 KW_PLUGIN_ROOT 로 가리킨다.
PLUGIN = pathlib.Path(os.environ.get("KW_PLUGIN_ROOT") or (REPO / "plugin")).resolve()
HOOK = PLUGIN / "hooks-handlers" / "pretooluse-skill.sh"
FAILS = []


def run(payload, env=None):
    stdin = payload if isinstance(payload, str) else json.dumps(payload, ensure_ascii=False)
    full = {**os.environ, **env} if env else None
    p = subprocess.run([str(HOOK)], input=stdin, capture_output=True, text=True, env=full, timeout=10)
    return p.returncode, p.stdout.strip(), p.stderr.strip()


def check(name, cond, detail=""):
    if cond:
        print(f"  o {name}")
    else:
        FAILS.append(f"{name}: {detail}")
        print(f"  x {name}  {detail}")


def skill(name, tool="Skill"):
    return {"hook_event_name": "PreToolUse", "tool_name": tool, "tool_input": {"skill": name, "args": "공지 써 줘"}}


print("korean-writing 을 부르면 묻는다")
for name in ("korean-writing:korean-writing", "korean-writing"):
    rc, out, err = run(skill(name))
    try:
        hso = json.loads(out)["hookSpecificOutput"]
    except Exception:
        hso = {}
    check(f"{name} → exit 0", rc == 0, f"exit {rc}")
    check(f"{name} → permissionDecision ask", hso.get("permissionDecision") == "ask", out[:120])
    check(f"{name} → hookEventName PreToolUse", hso.get("hookEventName") == "PreToolUse", out[:120])
    why = hso.get("permissionDecisionReason", "")
    check(f"{name} → 사유에 요청 맥락, 담는 것과 줄어드는 것, 거절 안내가 있고 실측 언급은 없다",
          "「공지 써 줘」" in why and "그대로 담지만" in why and "거절" in why
          and "H13" not in why and "EVALUATION" not in why, why[:120])

print("\n묻는 문장")
rc, out, err = run({"tool_name": "Skill", "tool_input": {"skill": "korean-writing", "args": "가" * 100}})
why = json.loads(out)["hookSpecificOutput"]["permissionDecisionReason"] if out else ""
check("긴 요청은 60자에서 자르고 … 을 붙인다", ("「" + "가" * 60 + "…」") in why, why[:80])
rc, out, err = run({"tool_name": "Skill", "tool_input": {"skill": "korean-writing"}})
d = json.loads(out) if out else {}
why = d.get("hookSpecificOutput", {}).get("permissionDecisionReason", "")
check("요청 요약이 없으면 맥락 없이 묻고 같은 문장을 systemMessage 로도 낸다",
      why.startswith("이 글에 korean-writing 문체 규칙을 적용할까요?") and d.get("systemMessage") == why, out[:120])

print("\n나머지는 그대로 지나보낸다")
for label, payload in [
    ("윤문 스킬", skill("korean-writing:humanize-korean")),
    ("글자 수 스킬", skill("korean-writing:korean-character-count")),
    ("README 스킬", skill("korean-writing:crafting-effective-readmes")),
    ("이름이 비슷한 다른 플러그인의 스킬", skill("other:korean-writing-extra")),
    ("Skill 이 아닌 도구", skill("korean-writing", tool="Bash")),
]:
    rc, out, err = run(payload)
    check(f"{label} → 출력 없이 exit 0", rc == 0 and out == "", f"exit {rc} out={out[:80]}")

print("\n끄기")
rc, out, err = run(skill("korean-writing:korean-writing"), env={"KOREAN_WRITING_HOOK_DISABLED": "1"})
check("KOREAN_WRITING_HOOK_DISABLED=1 이면 묻지 않는다", rc == 0 and out == "", f"exit {rc} out={out[:80]}")

print("\n이상 입력에 죽지 않고 막지도 않는다")
for label, payload in [
    ("빈 입력", ""),
    ("빈 객체", "{}"),
    ("JSON 아님", "not json"),
    ("배열", "[]"),
    ("tool_input null", '{"tool_name":"Skill","tool_input":null}'),
    ("tool_input 문자열", '{"tool_name":"Skill","tool_input":"korean-writing"}'),
]:
    rc, out, err = run(payload)
    check(f"{label} → 출력 없이 exit 0", rc == 0 and out == "", f"exit {rc} out={out[:80]}")

print()
if FAILS:
    print(f"실패 {len(FAILS)}건")
    for f in FAILS:
        print(f"  {f}")
    sys.exit(1)
print("전부 통과")
