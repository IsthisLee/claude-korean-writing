#!/usr/bin/env bash
# PreToolUse(Skill): 모델이 korean-writing 스킬을 스스로 부르면 먼저 사용자에게 한국어로 묻게 한다.
#
# 왜  : 이 스킬로 쓴 설명 문서에서 요청에 없던 곁가지 설명(기본값, 동작 원리)이 줄었다(EVALUATION.md J3).
#       요청에 적어 준 사실은 그대로 담겼다. 적용할지는 쓰는 사람이 정한다.
# 방식: Claude Code 의 권한 창(ask)은 선택지가 영어이고 거절하면 작업이 멈췄다(2026-09-11 사용자 보고).
#       그래서 호출을 막고(deny) 그 사유로 Claude 에게 AskUserQuestion 으로 한국어 질문을 띄우라고 지시한다.
#       사용자가 「적용」 을 고르면 다음 호출을 통과시키고 다른 답이면 스킬 없이 작업을 잇게 한다.
#       답은 세션 기록(transcript_path)에서 이번 요청 뒤에 남은 AskUserQuestion 결과로 찾는다.
#       기록을 읽을 수 없으면 답을 확인할 길이 없으므로 예전처럼 권한 창(ask)으로 묻는다.
# 통과: 사용자가 이번 요청에서 korean-writing 스킬을 쓰라고 직접 말했으면 묻지 않는다. /korean-writing 을
#       직접 친 경우는 Skill 도구를 거치지 않아 이 훅에 오지 않는다.
# 대상: korean-writing 하나. 글자 수·윤문 스킬은 건드리지 않는다.
# 끄기: KOREAN_WRITING_HOOK_DISABLED=1 은 이 플러그인의 훅 전체를 끈다.
# 읽는 것: 훅 입력과 이 세션의 기록 파일(뒤쪽 4MB). 아무것도 쓰지 않고 네트워크를 쓰지 않는다.
#
# 입력을 못 읽거나 python3 가 없으면 아무것도 내지 않고 exit 0 으로 끝낸다.
set -uo pipefail

[ "${KOREAN_WRITING_HOOK_DISABLED:-0}" = "1" ] && exit 0
command -v python3 >/dev/null 2>&1 || exit 0

# 아래 작은따옴표는 의도다. 안쪽은 python 코드라 셸이 확장하면 안 된다.
# shellcheck disable=SC2016
python3 -c '
import json, os, re, sys

try:
    d = json.load(sys.stdin)
except Exception:
    sys.exit(0)
if not isinstance(d, dict) or d.get("tool_name") != "Skill":
    sys.exit(0)
ti = d.get("tool_input") or {}
if not isinstance(ti, dict):
    sys.exit(0)
if str(ti.get("skill", "")) not in ("korean-writing", "korean-writing:korean-writing"):
    sys.exit(0)

# 사용자의 답을 찾는 표지. Claude 에게 이 말을 질문에 그대로 넣으라고 시킨다.
MARK = "korean-writing 문체 규칙을 적용할까요"
# 규칙은 지키되 곁가지 설명은 줄이지 않는 선택지. 줄어드는 것이 곁가지 설명이라는 J3 측정을 그대로 겨냥한다.
MORE = "적용하고 설명은 넉넉히"
# 주의 문구는 J3 에서 잰 만큼만 말한다. 적어 준 사실은 그대로였고 곁가지 설명이 줄어 글이 짧아졌다.
EFFECT = ("요청에 적은 내용은 모두 담습니다. 다만 요청에 없던 곁가지 설명(기본값, 동작 원리 같은 것)은 "
          "Claude 가 덜 덧붙여 글이 짧아질 수 있습니다.")


def one_line(s, n=60):
    s = " ".join(str(s).split())
    return s if len(s) <= n else s[:n].rstrip() + "…"


def emit(decision, reason, show=False):
    out = {"hookSpecificOutput": {"hookEventName": "PreToolUse",
                                  "permissionDecision": decision,
                                  "permissionDecisionReason": reason}}
    if show:
        out["systemMessage"] = reason
    print(json.dumps(out, ensure_ascii=False))
    sys.exit(0)


def human_text(e):
    # 사람이 친 메시지면 그 글을, 아니면 None 을 돌려준다. 도구 결과와 메타 메시지는 사람의 말이 아니다.
    if not isinstance(e, dict) or e.get("type") != "user" or e.get("isMeta") or e.get("isSidechain"):
        return None
    c = (e.get("message") or {}).get("content")
    if isinstance(c, str):
        return c
    if isinstance(c, list):
        if any(isinstance(b, dict) and b.get("type") == "tool_result" for b in c):
            return None
        t = [str(b.get("text", "")) for b in c if isinstance(b, dict) and b.get("type") == "text"]
        return "\n".join(t) if t else None
    return None


ANS_RE = re.compile(r"\"[^\"]*" + re.escape(MARK) + r"[^\"]*\"=\"([^\"]*)\"")


def answer_of(e):
    # 이 항목이 우리 질문에 대한 AskUserQuestion 답이면 고른 선택지를 돌려준다.
    if not isinstance(e, dict):
        return None
    r = e.get("toolUseResult")
    if isinstance(r, dict) and isinstance(r.get("answers"), dict):
        for q, a in r["answers"].items():
            if MARK in str(q):
                return str(a)
    c = (e.get("message") or {}).get("content")
    if isinstance(c, list):
        for b in c:
            if isinstance(b, dict) and b.get("type") == "tool_result":
                t = b.get("content")
                t = t if isinstance(t, str) else json.dumps(t, ensure_ascii=False)
                m = ANS_RE.search(t)
                if m:
                    return m.group(1)
    return None


def read_tail(path, limit=4 * 1024 * 1024):
    # 기록이 커도 이번 요청은 끝부분에 있다. 뒤쪽만 읽고 잘린 첫 줄은 버린다.
    with open(os.path.expanduser(path), "rb") as f:
        f.seek(0, 2)
        size = f.tell()
        f.seek(max(0, size - limit))
        data = f.read().decode("utf-8", "replace")
    lines = data.split("\n")
    if size > limit:
        lines = lines[1:]
    out = []
    for line in lines:
        try:
            out.append(json.loads(line))
        except Exception:
            pass
    return out


tp = d.get("transcript_path")
entries = None
if isinstance(tp, str) and tp:
    try:
        entries = read_tail(tp)
    except Exception:
        entries = None

prompt = ""
turn = []
if entries is not None:
    last = max((i for i, e in enumerate(entries) if human_text(e) is not None), default=-1)
    prompt = human_text(entries[last]) if last >= 0 else ""
    turn = entries[last + 1:]

hint = one_line(ti.get("args") or prompt or "")
question = f"「{hint}」 작성에 korean-writing 문체 규칙을 적용할까요?" if hint else "이 글에 korean-writing 문체 규칙을 적용할까요?"

if entries is None:
    # 기록을 못 읽으면 답을 확인할 수 없다. 예전처럼 Claude Code 권한 창으로 묻는다.
    emit("ask", f"{question} {EFFECT} 거절하면 규칙 없이 씁니다.", show=True)

answers = [a for a in (answer_of(e) for e in turn) if a is not None]
if answers:
    a = answers[-1].strip()
    if a.startswith("적용") and not re.search(r"안|않|말", a):
        sys.exit(0)
    emit("deny", "[korean-writing] 사용자가 이번 글에는 korean-writing 문체 규칙을 쓰지 않기로 했다. "
                 "이 스킬을 다시 부르지 말고 규칙 없이 하던 작업을 이어 간다.")

# 사용자가 이번 요청에서 이 스킬을 쓰라고 직접 말했으면 묻지 않는다. 이름만 나온 것은 요청으로 보지 않는다.
if re.search(r"korean-writing\s*(스킬|규칙)\s*(을|를|로|으로)?[^\n]{0,30}?(써|쓰|적용|사용|켜)", prompt):
    sys.exit(0)

HEAD = "[korean-writing] 쓰기 전에 사용자에게 적용 여부를 묻는다."
NO_ASK = ("AskUserQuestion 이 없으면 찾거나 이 스킬을 다시 부르지 말고 규칙 없이 요청한 글만 쓴다. "
          "묻지 못했다는 말은 답에도 글에도 적지 않는다.")


def said_before(e):
    # 이번 요청 안에서 이미 이 안내를 받았는가. 받고도 묻지 않고 다시 부르면 짧게 돌려보낸다.
    c = (e.get("message") or {}).get("content") if isinstance(e, dict) else None
    for b in (c if isinstance(c, list) else []):
        if isinstance(b, dict) and b.get("type") == "tool_result":
            t = b.get("content")
            t = t if isinstance(t, str) else json.dumps(t, ensure_ascii=False)
            if HEAD in t:
                return True
    return False


if any(said_before(e) for e in turn):
    emit("deny", f"{HEAD} 이미 안내했다. " + NO_ASK)

emit("deny", "\n".join([
    f"{HEAD} 작업은 멈추지 않는다.",
    "AskUserQuestion 이 있으면 한 번만 묻는다.",
    f"- question: 무엇을 어디에 쓰는 글인지 넣는다. 예: {question} 질문에 「{MARK}」 를 그대로 넣는다.",
    "- header: 문체 규칙",
    f"- 첫째 선택지 label 「적용」, description 「번역투와 AI 티를 피해 씁니다. {EFFECT}」",
    f"- 둘째 선택지 label 「{MORE}」, description 「규칙대로 쓰되 요청에 없던 배경·기본값·동작 원리 설명도 "
    "평소만큼 덧붙입니다. 글이 짧아지지 않습니다.」",
    "- 셋째 선택지 label 「적용 안 함」, description 「규칙 없이 평소대로 씁니다.」",
    f"- 추천하는 쪽 label 끝에 「 (추천)」 을 붙인다. 남이 읽을 글이면 「적용」 이고, 기본값이나 동작 원리 같은 "
    f"곁가지 설명까지 있어야 쓸모가 있는 참고 문서면 「{MORE}」 이고, 원문 표현을 그대로 두어야 하는 "
    "격식 문서면 「적용 안 함」 이다.",
    "- question 끝에 네 의견을 한 문장 덧붙인다. 이 글이 어떤 글이라서 그 쪽을 추천하는지만 적고 "
    "확인하지 않은 것을 단정하지 않는다.",
    "- 「적용」 이면 이 스킬을 다시 부른다.",
    f"- 「{MORE}」 이면 이 스킬을 다시 부르고, 규칙을 지키면서 요청에 없던 곁가지 설명을 평소만큼 덧붙여 쓴다. "
    "설명을 줄이지 않는다.",
    "- 「적용 안 함」 이면 스킬 없이 하던 작업을 이어 간다.",
    NO_ASK,
]))
'
exit 0
