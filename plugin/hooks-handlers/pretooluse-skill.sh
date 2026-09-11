#!/usr/bin/env bash
# PreToolUse(Skill): 모델이 korean-writing 스킬을 스스로 부르기 전에 사용자에게 적용할지 묻는다.
#
# 왜 : 문체 규칙을 답변에 주입하니 기본값 같은 세부가 빠졌다(EVALUATION.md H13). 이 스킬도 같은
#      규칙집을 쓰므로 세부를 잃으면 안 되는 문서에서는 사람이 먼저 정해야 한다.
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

reason = ("korean-writing 규칙으로 쓸지 정해 주세요. 문체는 다듬어지지만 규칙이 세부를 빼는 경우가 "
          "실측됐습니다(EVALUATION.md H13). 세부를 잃으면 안 되는 문서라면 거절하세요. 거절하면 규칙 없이 씁니다.")
print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse",
                                         "permissionDecision": "ask",
                                         "permissionDecisionReason": reason}}, ensure_ascii=False))
'
exit 0
