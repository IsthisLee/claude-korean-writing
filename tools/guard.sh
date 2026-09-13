#!/usr/bin/env bash
# 공개 저장소 가드. 개인 식별 정보와 개인 파일이 저장소에 들어오는 것을 막는다.
#
# 사용  : tools/guard.sh --staged   스테이지된 파일을 본다. .githooks/pre-commit 이 커밋 직전에 부른다
#         tools/guard.sh --all      추적 중인 파일 전부를 본다. CI 의 「설치본 경계」 작업이 부른다
# 막는 것:
#   경로  .private/ 아래 파일
#   내용  홈 경로(/Users/<이름>, /home/<이름>), Claude Code 세션 임시 경로(/private/tmp/claude-<숫자>),
#         .private/guard-patterns 에 적은 개인 패턴(한 줄에 하나, # 은 주석). .private/ 는 git 이 무시한다
# 종료  : 걸리면 1, 없으면 0, 사용법이 틀리면 2
# 이 파일은 검사에서 뺀다. 무엇을 막는지 적으려면 그 패턴 문자열이 들어가야 해서다.
# 2026-09-11 에 always-on 실험 파일 셋이 /Users/<이름> 절대 경로를 담은 채 공개돼 있던 것을 계기로 넣었다.
set -u
mode=${1:---staged}
root="$(git rev-parse --show-toplevel 2>/dev/null)" || { echo "git 저장소 안에서 부른다" >&2; exit 2; }
cd "$root" || exit 2
pattern='/Users/[A-Za-z]|/home/[A-Za-z]|/private/tmp/claude-[0-9]'
if [ -f .private/guard-patterns ]; then
  extra=$(grep -v -E '^[[:space:]]*(#|$)' .private/guard-patterns | paste -sd '|' -)
  [ -n "$extra" ] && pattern="$pattern|$extra"
fi
case "$mode" in
  --staged) files=$(git diff --cached --name-only --diff-filter=ACMR) ;;
  --all)    files=$(git ls-files) ;;
  *) echo "사용: tools/guard.sh --staged|--all" >&2; exit 2 ;;
esac
content() { if [ "$mode" = --staged ]; then git show ":$1"; else cat "$1"; fi; }
fail=0; n=0
while IFS= read -r f; do
  [ -n "$f" ] || continue
  n=$((n + 1))
  case "$f" in
    .private/*) echo "guard: .private/ 아래 파일은 올리지 않는다: $f"; fail=1; continue ;;
    tools/guard.sh) continue ;;
  esac
  [ -f "$f" ] || [ "$mode" = --staged ] || continue
  hits=$(content "$f" 2>/dev/null | grep -n -I -E "$pattern" | head -3)
  if [ -n "$hits" ]; then
    echo "guard: 개인 식별 정보가 있다: $f"
    printf '%s\n' "$hits" | cut -c1-160 | sed 's/^/    /'
    fail=1
  fi
done <<< "$files"
if [ "$fail" -ne 0 ]; then
  echo "막았다. 절대 경로는 상대 경로로 바꾸고 개인 파일은 .private/ 에 둔다."
  exit 1
fi
echo "guard: 통과 (파일 ${n}개)"
