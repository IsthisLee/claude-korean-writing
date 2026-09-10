#!/usr/bin/env bash
# SessionStart: 한국어 답변 규칙을 세션이 시작할 때 한 번 주입한다.
#
# 왜 : 채팅 답변은 파일이 아니라 PostToolUse 훅이 볼 수 없고, 스킬은 글 작성 요청에만 로드된다.
#      그 사이에 남는 것이 평소의 한국어 답변이고, 이 훅이 그것을 맡는다.
# 무엇: hooks-handlers/always-on.md 를 stdout 으로 낸다. Claude Code 가 추가 컨텍스트로 넣는다.
# 크기: 약 660 토큰. 세션당 한 번이고 프롬프트 캐시에 들어가 턴마다 다시 들지 않는다.
# 끄기: KOREAN_WRITING_HOOK_DISABLED=1 은 이 플러그인의 훅 전체를,
#      KOREAN_WRITING_ALWAYS_ON_DISABLED=1 은 이 훅만 끈다.
#
# 이 훅은 무엇도 막지 않는다. 규칙 파일이 없거나 읽히지 않아도 exit 0 으로 끝낸다.
set -uo pipefail

[ "${KOREAN_WRITING_HOOK_DISABLED:-0}" = "1" ] && exit 0
[ "${KOREAN_WRITING_ALWAYS_ON_DISABLED:-0}" = "1" ] && exit 0

d="$(cd "$(dirname "$0")" && pwd)"
f="$d/always-on.md"
[ -r "$f" ] || exit 0

# 제외 표시는 이 저장소의 검사 도구용이다. 주입문에 들어가면 지시문으로 읽힐 수 있어 뺀다.
sed '/korean-writing: ignore/d' "$f"
exit 0
