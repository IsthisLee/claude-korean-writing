#!/usr/bin/env python3
"""pretooluse-skill.sh 회귀 테스트.

pytest 없이 돈다. 실행: python3 tests/test_pretooluse.py

이 훅은 모델이 korean-writing 스킬을 스스로 부를 때 호출을 막고 Claude 에게 한국어로 물으라고 시킨다.
사용자가 「적용」 을 고르면 다음 호출을 통과시키고 다른 답이면 스킬 없이 이어 가게 한다.
세션 기록을 못 읽으면 예전처럼 권한 창(ask)으로 묻는다.
다른 스킬과 다른 도구는 그대로 지나보내야 하고 이상 입력에 죽으면 안 된다.
첫 실패에서 멈추지 않고 전부 모아 보고한다.
"""
import json
import os
import pathlib
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent
# 릴리스 zip 을 풀어 그것을 대고 돌릴 때는 KW_PLUGIN_ROOT 로 가리킨다.
PLUGIN = pathlib.Path(os.environ.get("KW_PLUGIN_ROOT") or (REPO / "plugin")).resolve()
HOOK = PLUGIN / "hooks-handlers" / "pretooluse-skill.sh"
MARK = "korean-writing 문체 규칙을 적용할까요"
MORE = "적용하고 설명은 넉넉히"
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


def decision(out):
    try:
        return json.loads(out)["hookSpecificOutput"]
    except Exception:
        return {}


# 기록 한 줄씩. 실제 세션 기록(~/.claude/projects/*/<세션>.jsonl)과 같은 모양이다.
def human(text):
    return {"type": "user", "message": {"role": "user", "content": text}}


def ask_tool(qid, question):
    return {"type": "assistant", "message": {"role": "assistant", "content": [
        {"type": "tool_use", "id": qid, "name": "AskUserQuestion",
         "input": {"questions": [{"question": question, "header": "문체 규칙",
                                  "options": [{"label": "적용"}, {"label": "적용 안 함"}]}]}}]}}


def answered(qid, question, label, structured=True):
    e = {"type": "user", "message": {"role": "user", "content": [
        {"type": "tool_result", "tool_use_id": qid,
         "content": f"Your questions have been answered: \"{question}\"=\"{label}\". You can now continue."}]}}
    if structured:
        e["toolUseResult"] = {"questions": [{"question": question}], "answers": {question: label}}
    return e


def transcript(*entries):
    f = tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False, encoding="utf-8")
    for e in entries:
        f.write(json.dumps(e, ensure_ascii=False) + "\n")
    f.close()
    return f.name


def call(name="korean-writing:korean-writing", args=None, tp=None, tool="Skill"):
    ti = {"skill": name}
    if args is not None:
        ti["args"] = args
    p = {"hook_event_name": "PreToolUse", "tool_name": tool, "tool_input": ti}
    if tp is not None:
        p["transcript_path"] = tp
    return p


Q = f"「운영팀 슬랙 공지」 작성에 {MARK}?"
REQ = "운영팀에 보낼 옵션 변경 안내문 써줘. 슬랙에 캐주얼하게."

print("처음 부르면 막고 한국어로 물으라고 시킨다")
for name in ("korean-writing:korean-writing", "korean-writing"):
    rc, out, _ = run(call(name, tp=transcript(human(REQ))))
    h = decision(out)
    why = h.get("permissionDecisionReason", "")
    check(f"{name} → exit 0, deny", rc == 0 and h.get("permissionDecision") == "deny", out[:120])
    check(f"{name} → AskUserQuestion 으로 묻고 작업을 멈추지 않게 한다",
          "AskUserQuestion" in why and "멈추지 않는다" in why and "이어 간다" in why, why[:120])
    check(f"{name} → 한국어 선택지 둘과 표지 문구", "「적용」" in why and "「적용 안 함」" in why and MARK in why, why[:120])
    check(f"{name} → 요청 맥락을 질문 예시에 넣는다(요청 요약이 없으면 사용자 요청)", "운영팀에 보낼 옵션 변경" in why, why[:160])
    check(f"{name} → 줄어드는 것은 곁가지 설명이라고 구체적으로 적고 실측 언급은 없다",
          "곁가지 설명" in why and "모두 담습니다" in why and "EVALUATION" not in why and "J3" not in why, why[:160])
    check(f"{name} → 추천하는 쪽을 표시하게 한다", "(추천)" in why, why[:160])
    check(f"{name} → 묻는 자리에 제 의견을 붙이게 한다", "네 의견을 한 문장" in why, why[:160])

rc, out, _ = run(call(args="가" * 100, tp=transcript(human(REQ))))
check("요청 요약(args)이 있으면 그것을 60자에서 잘라 쓴다", ("「" + "가" * 60 + "…」") in decision(out).get("permissionDecisionReason", ""), out[:100])
rc, out, _ = run(call(tp=transcript()))
check("기록에 사람의 말이 없으면 맥락 없이 묻는다",
      "이 글에 korean-writing 문체 규칙을 적용할까요?" in decision(out).get("permissionDecisionReason", ""), out[:120])

print("\n사용자의 답을 따른다")
rc, out, _ = run(call(tp=transcript(human(REQ), ask_tool("q1", Q), answered("q1", Q, "적용"))))
check("「적용」 을 고르면 출력 없이 통과", rc == 0 and out == "", out[:120])
rc, out, _ = run(call(tp=transcript(human(REQ), ask_tool("q1", Q), answered("q1", Q, "적용", structured=False))))
check("구조화 필드가 없어도 결과 문자열에서 「적용」 을 읽는다", rc == 0 and out == "", out[:120])
rc, out, _ = run(call(tp=transcript(human(REQ), ask_tool("q1", Q), answered("q1", Q, "적용 안 함"))))
h = decision(out)
check("「적용 안 함」 이면 막고 스킬 없이 이어 가게 한다",
      h.get("permissionDecision") == "deny" and "쓰지 않기로" in h.get("permissionDecisionReason", "")
      and "이어 간다" in h.get("permissionDecisionReason", ""), out[:160])
rc, out, _ = run(call(tp=transcript(human(REQ), ask_tool("q1", Q), answered("q1", Q, "나중에 정할게"))))
check("다른 자유 답도 적용으로 보지 않는다", decision(out).get("permissionDecision") == "deny", out[:120])
rc, out, _ = run(call(tp=transcript(human(REQ), ask_tool("q1", Q), answered("q1", Q, "적용 (추천)"))))
check("추천 표시가 붙은 「적용 (추천)」 도 적용으로 읽는다", rc == 0 and out == "", out[:120])
rc, out, _ = run(call(tp=transcript(human(REQ), ask_tool("q1", Q), answered("q1", Q, "적용 안 함 (추천)"))))
check("「적용 안 함 (추천)」 은 적용으로 보지 않는다", decision(out).get("permissionDecision") == "deny", out[:120])
rc, out, _ = run(call(tp=transcript(human(REQ), ask_tool("q1", Q), answered("q1", Q, MORE))))
check(f"「{MORE}」 도 통과시킨다", rc == 0 and out == "", out[:120])
rc, out, _ = run(call(tp=transcript(human(REQ), ask_tool("q1", Q), answered("q1", Q, MORE + " (추천)"))))
check(f"「{MORE} (추천)」 도 통과시킨다", rc == 0 and out == "", out[:120])
rc, out, _ = run(call(tp=transcript(human("어제 쓴 공지 고쳐줘"), ask_tool("q1", Q), answered("q1", Q, "적용"), human(REQ))))
check("지난 요청에서 받은 답은 이번 요청에 쓰지 않고 다시 묻는다",
      "AskUserQuestion" in decision(out).get("permissionDecisionReason", ""), out[:120])
other = "어느 브랜치에 올릴까요?"
rc, out, _ = run(call(tp=transcript(human(REQ), ask_tool("q9", other), answered("q9", other, "적용"))))
check("다른 질문의 답은 무시한다", "AskUserQuestion" in decision(out).get("permissionDecisionReason", ""), out[:120])

print("\n안내를 받고도 묻지 않고 다시 부르면")
first = run(call(tp=transcript(human(REQ))))[1]
reason1 = decision(first).get("permissionDecisionReason", "")
again = {"type": "user", "message": {"role": "user", "content": [
    {"type": "tool_result", "tool_use_id": "s1", "is_error": True, "content": reason1}]}}
rc, out, _ = run(call(tp=transcript(human(REQ), again)))
why = decision(out).get("permissionDecisionReason", "")
check("짧게 막고 규칙 없이 글만 쓰게 한다", decision(out).get("permissionDecision") == "deny"
      and "이미 안내했다" in why and "다시 부르지" in why and "적지 않는다" in why and "question:" not in why, why[:160])
check("묻지 못했다는 말을 글에 적지 말라는 지시가 처음 안내에도 있다", "적지 않는다" in reason1, reason1[-120:])

print("\n사용자가 직접 쓰라고 했으면 묻지 않는다")
rc, out, _ = run(call(tp=transcript(human("korean-writing 스킬로 릴리스 노트 써줘"))))
check("「korean-writing 스킬로 … 써줘」 → 통과", rc == 0 and out == "", out[:120])
rc, out, _ = run(call(tp=transcript(human("korean-writing 저장소 README 의 오타 고쳐줘"))))
check("이름만 나온 요청은 묻는다", decision(out).get("permissionDecision") == "deny", out[:120])

print("\n기록을 못 읽으면 예전처럼 권한 창으로 묻는다")
for label, tp in [("transcript_path 없음", None), ("없는 파일", "/nonexistent/kw-transcript.jsonl")]:
    rc, out, _ = run(call(args="공지 써 줘", tp=tp))
    d = json.loads(out) if out else {}
    h = d.get("hookSpecificOutput", {})
    why = h.get("permissionDecisionReason", "")
    check(f"{label} → ask, 요청 맥락·거절 안내·같은 문장의 systemMessage",
          h.get("permissionDecision") == "ask" and "「공지 써 줘」" in why and "거절" in why
          and d.get("systemMessage") == why, out[:140])

print("\n나머지는 그대로 지나보낸다")
tp = transcript(human(REQ))
for label, payload in [
    ("윤문 스킬", call("korean-writing:humanize-korean", tp=tp)),
    ("글자 수 스킬", call("korean-writing:korean-character-count", tp=tp)),
    ("이름이 비슷한 다른 플러그인의 스킬", call("other:korean-writing-extra", tp=tp)),
    ("Skill 이 아닌 도구", call("korean-writing", tool="Bash", tp=tp)),
]:
    rc, out, _ = run(payload)
    check(f"{label} → 출력 없이 exit 0", rc == 0 and out == "", f"exit {rc} out={out[:80]}")

print("\n끄기")
rc, out, _ = run(call(tp=tp), env={"KOREAN_WRITING_HOOK_DISABLED": "1"})
check("KOREAN_WRITING_HOOK_DISABLED=1 이면 묻지 않는다", rc == 0 and out == "", f"exit {rc} out={out[:80]}")

print("\n이상 입력에 죽지 않는다")
bad = tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False)
bad.write("not json\n{\"type\":\"user\"}\n[1,2]\n")
bad.close()
for label, payload in [
    ("빈 입력", ""),
    ("빈 객체", "{}"),
    ("JSON 아님", "not json"),
    ("배열", "[]"),
    ("tool_input null", '{"tool_name":"Skill","tool_input":null}'),
    ("tool_input 문자열", '{"tool_name":"Skill","tool_input":"korean-writing"}'),
]:
    rc, out, _ = run(payload)
    check(f"{label} → 출력 없이 exit 0", rc == 0 and out == "", f"exit {rc} out={out[:80]}")
rc, out, _ = run(call(tp=bad.name))
check("깨진 기록 줄은 건너뛰고 묻는다", rc == 0 and decision(out).get("permissionDecision") == "deny", out[:100])

print()
if FAILS:
    print(f"실패 {len(FAILS)}건")
    for f in FAILS:
        print(f"  {f}")
    sys.exit(1)
print("전부 통과")
