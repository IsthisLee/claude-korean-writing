#!/usr/bin/env bash
# 파일을 통째로 훅에 넣어 검사한다.
#
# 훅은 Claude Code 가 방금 편집한 부분만 본다. 이미 써 둔 문서를 점검하거나 CI·pre-commit 에서
# 돌릴 때는 파일 전체를 편집분으로 넣는다. 판정 기준과 메시지는 훅과 같다.
#
# 사용  : plugin/scripts/check.sh FILE...
#         plugin/scripts/check.sh --all      저장소가 쓴 .md 를 전부 검사한다 (가져온 파일은 뺀다)
# 종료  : 걸린 파일이 하나라도 있으면 1, 없으면 0. 인자가 없으면 2. .md 가 아닌 파일은 건너뛴다.
# 끄기  : 파일 머리에 <!-- korean-writing: ignore --> 가 있으면 그 파일은 통과한다.
#
# 세션 단위 끄기 스위치는 여기서 걷어낸다. 이 스크립트를 부르는 것 자체가 검사하라는 뜻이다.
# 걷어내지 않으면 훅이 stdin 을 읽기 전에 끝나 파이프가 끊기고, 검사가 아니라 exit 120 이 나온다.
set -uo pipefail
unset KOREAN_WRITING_HOOK_DISABLED
unset CLAUDE_PLUGIN_OPTION_EDIT_CHECK

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HOOK="$ROOT/hooks-handlers/posttooluse.sh"

# --all 이 훑지 않는 곳. 다른 MIT 프로젝트에서 가져온 파일이라 이 저장소의 규칙 대상이 아니다.
# plugin/NOTICE.md 에 적힌 목록과 같아야 한다. 저장소에서는 plugin/ 아래에 있고
# 설치본에서는 루트에 있으므로 접두사를 선택으로 둔다.
VENDORED='^(plugin/)?(skills/(humanize|humanize-korean|humanize-redo|crafting-effective-readmes)/|agents/)'

if [ "${1:-}" = "--all" ]; then
  command -v git >/dev/null 2>&1 || { echo "--all 은 git 이 있어야 한다" >&2; exit 2; }
  # 지금 있는 저장소 전체를 본다. 이 스크립트는 설치본 안(plugin/)에 있으므로
  # 스크립트 위치를 기준으로 삼으면 저장소 루트의 README·CHANGELOG 를 놓친다.
  TOP="$(git rev-parse --show-toplevel 2>/dev/null)" \
    || { echo "--all 은 git 저장소 안에서 돌린다" >&2; exit 2; }
  # 목록을 손으로 적으면 새 문서가 조용히 빠진다. 실제로 REPORT.md 가 그렇게 빠져 있었다.
  # mapfile 은 쓰지 않는다. macOS 기본 bash 3.2 에 없고 CI 가 macOS 에서도 돈다.
  FILES=()
  while IFS= read -r line; do FILES+=("$line"); done < <(
    cd "$TOP" && git ls-files '*.md' | grep -Ev "$VENDORED"
  )
  [ "${#FILES[@]}" -gt 0 ] || { echo "검사할 .md 가 없다" >&2; exit 2; }
  cd "$TOP" || exit 2
  set -- "${FILES[@]}"
elif [ $# -eq 0 ]; then
  echo "사용: plugin/scripts/check.sh FILE...  또는  plugin/scripts/check.sh --all" >&2
  exit 2
fi

bad=0
for f in "$@"; do
  if [ ! -f "$f" ]; then echo "없음: $f" >&2; bad=1; continue; fi
  case "$f" in *.md) ;; *) echo "건너뜀 (.md 아님): $f"; continue ;; esac
  abs="$(cd "$(dirname "$f")" && pwd)/$(basename "$f")"
  out=$(python3 -c 'import json, sys
p = sys.argv[1]
print(json.dumps({"tool_name": "Write", "tool_input": {"file_path": p, "content": open(p, encoding="utf-8").read()}}, ensure_ascii=False))' "$abs" | "$HOOK" 2>&1 >/dev/null)
  rc=$?
  case "$rc" in
    0) echo "통과: $f" ;;
    2) echo "$out"; bad=1 ;;
    *) echo "오류 (exit $rc): $f"; echo "$out"; bad=1 ;;
  esac
done
exit $bad
