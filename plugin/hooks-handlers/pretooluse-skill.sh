#!/usr/bin/env bash
# PreToolUse(Skill): 모델이 korean-writing 스킬을 스스로 부르기 전에 사용자에게 적용할지 묻는다.
#
# 왜 : 이 스킬로 쓴 설명 문서에서 Claude 가 덧붙이는 설명이 약 1/3 짧아지고 곁가지 설명이 빠졌다
#      (EVALUATION.md J3). 요청에 적어 준 사실은 그대로 담겼다. 적용할지는 쓰는 사람이 정한다.
# 무엇: Skill 도구로 korean-writing 을 부르면 permissionDecision "ask" 를 돌려준다. Claude Code 가
#      평소 권한 흐름대로 확인을 받고, 거절하면 모델은 스킬 없이 쓴다. 헤드리스 실측에서 사용자가
#      /korean-writing 을 직접 친 경우는 Skill 도구를 거치지 않아 이 훅에 걸리지 않았다.
# 대상: korean-writing 하나. 글자 수·README·윤문 스킬은 건드리지 않는다.
# 끄기: KOREAN_WRITING_HOOK_DISABLED=1 은 이 플러그인의 훅 전체를 끈다.
#
# 이 훅은 무엇도 막지 않는다. 입력을 못 읽거나 python3 가 없으면 아무것도 내지 않고 exit 0 으로 끝낸다.
set -uo pipefail

[ "${KOREAN_WRITING_HOOK_DISABLED:-0}" = "1" ] && exit 0
command -v python3 >/dev/null 2>&1 || exit 0

# 아래 작은따옴표는 의도다. 안쪽은 python 코드라 셸이 확장하면 안 된다.
# shellcheck disable=SC2016
python3 -c '
import json, sys

try:
    d = json.load(sys.stdin)
except Exception:
    sys.exit(0)
if not isinstance(d, dict) or d.get("tool_name") != "Skill":
    sys.exit(0)
ti = d.get("tool_input") or {}
skill = str(ti.get("skill", "")) if isinstance(ti, dict) else ""
if skill not in ("korean-writing", "korean-writing:korean-writing"):
    sys.exit(0)

# 무엇을 쓰려는지 보여 준다. args 는 모델이 요청을 요약해 넘긴 것이다. 60자에서 자른다.
args = " ".join(str(ti.get("args", "")).split()) if isinstance(ti, dict) else ""
if len(args) > 60:
    args = args[:60].rstrip() + "…"
head = f"「{args}」 작성에 korean-writing 문체 규칙을 적용할까요?" if args else "이 글에 korean-writing 문체 규칙을 적용할까요?"
# 주의 문구는 J3 에서 잰 만큼만 말한다. 적어 준 사실은 그대로였고 덧붙이는 설명이 짧아졌다.
reason = (head + " 요청에 적은 내용은 그대로 담지만 Claude 가 덧붙이는 설명은 짧아질 수 있습니다. "
          "거절하면 규칙 없이 씁니다.")
# 확인 창에 사유가 보이는지 공식 문서에 적혀 있지 않아 같은 문장을 systemMessage 로도 낸다.
print(json.dumps({"systemMessage": reason,
                  "hookSpecificOutput": {"hookEventName": "PreToolUse",
                                         "permissionDecision": "ask",
                                         "permissionDecisionReason": reason}}, ensure_ascii=False))
'
exit 0
