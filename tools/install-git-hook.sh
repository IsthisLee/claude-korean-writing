#!/usr/bin/env bash
# 커밋 직전에 스테이지된 .md 를 검사하는 git 훅을 깔거나 지운다.
#
# 왜 : 편집 훅은 Claude Code 가 고칠 때만 돈다. 사람이 에디터로 고친 문단은 CI 까지 간다.
#      그 사이를 막는 자리가 pre-commit 이다.
# 무엇: .git/hooks/pre-commit 을 만든다. 안에서 이 저장소의 plugin/scripts/check.sh 를 부른다.
#      플러그인으로 설치했으면 다른 저장소에 깔아도 된다. 절대 경로로 박아 넣는다.
#
# 사용  : tools/install-git-hook.sh [--uninstall] [대상 저장소]
#        대상을 안 주면 지금 디렉터리의 저장소에 깐다.
# 종료  : 0 성공, 1 실패(이미 다른 훅이 있거나 저장소가 아님)
# 끄기  : git commit --no-verify. 아예 지우려면 --uninstall
#
# 스테이지된 내용이 아니라 작업 트리의 파일을 본다. 부분 스테이징을 하면 커밋될 내용과
# 검사한 내용이 다를 수 있다. 그 경우까지 맞추려면 임시 트리로 체크아웃해야 하는데,
# 커밋 하나마다 그 값을 치를 만큼 얻는 것이 크지 않아 하지 않는다.
set -uo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CHECK="$ROOT/plugin/scripts/check.sh"
MARK="# korean-writing pre-commit"

MODE="install"
TARGET="."
for a in "$@"; do
  case "$a" in
    --uninstall) MODE="uninstall" ;;
    -h|--help) sed -n '2,15p' "$0"; exit 0 ;;
    *) TARGET="$a" ;;
  esac
done

cd "$TARGET" 2>/dev/null || { echo "그런 디렉터리가 없다: $TARGET" >&2; exit 1; }
GITDIR="$(git rev-parse --git-dir 2>/dev/null)" || { echo "git 저장소가 아니다: $TARGET" >&2; exit 1; }
HOOK="$GITDIR/hooks/pre-commit"

if [ "$MODE" = "uninstall" ]; then
  if [ ! -e "$HOOK" ]; then echo "깔린 것이 없다: $HOOK"; exit 0; fi
  grep -q "$MARK" "$HOOK" || { echo "이 스크립트가 깐 훅이 아니다. 직접 확인해라: $HOOK" >&2; exit 1; }
  rm -f "$HOOK"
  echo "지웠다: $HOOK"
  exit 0
fi

[ -x "$CHECK" ] || { echo "검사 스크립트를 찾지 못했다: $CHECK" >&2; exit 1; }

if [ -e "$HOOK" ] && ! grep -q "$MARK" "$HOOK"; then
  echo "이미 다른 pre-commit 훅이 있다: $HOOK" >&2
  echo "덮어쓰지 않는다. 그 훅 안에 아래 두 줄을 직접 넣어라." >&2
  echo "  git diff --cached --name-only --diff-filter=ACM -z -- '*.md' \\" >&2
  echo "    | xargs -0 -r \"$CHECK\" || exit 1" >&2
  exit 1
fi

mkdir -p "$(dirname "$HOOK")"
cat > "$HOOK" <<EOF
#!/usr/bin/env bash
$MARK
# tools/install-git-hook.sh 가 만들었다. 지우려면 --uninstall 로 부른다.
# 건너뛰려면 git commit --no-verify.
set -uo pipefail
CHECK="$CHECK"
[ -x "\$CHECK" ] || exit 0

files=()
while IFS= read -r -d '' f; do files+=("\$f"); done < <(
  git diff --cached --name-only --diff-filter=ACM -z -- '*.md'
)
[ \${#files[@]} -gt 0 ] || exit 0

if ! "\$CHECK" "\${files[@]}"; then
  echo "" >&2
  echo "[korean-writing] 위 항목을 고치고 다시 커밋해라. 이대로 넣으려면 git commit --no-verify." >&2
  exit 1
fi
EOF
chmod +x "$HOOK"
echo "깔았다: $HOOK"
echo "검사기: $CHECK"
echo "건너뛰기: git commit --no-verify / 지우기: tools/install-git-hook.sh --uninstall"
