#!/usr/bin/env bash
# 릴리스: 버전 하나로 plugin.json·README 배지·CHANGELOG 를 맞추고 커밋·태그한다.
#
# 사용
#   scripts/release.sh <major.minor.patch>          로컬에서 커밋과 태그까지
#   scripts/release.sh <major.minor.patch> --push   여기에 push 와 GitHub 릴리스까지
#
# 순서
#   1. 검사: 작업 트리 clean, 버전 형식, 새 버전이 현재 이상, 같은 태그 없음
#   2. CHANGELOG: [Unreleased] 의 내용을 [<버전>] - <오늘> 절로 옮기고 비교 링크를 갱신한다
#      (비어 있으면 중단. 릴리스 노트를 먼저 쓴다)
#   3. README.md·README.en.md 상단 인용구에 v<버전> 이 있어야 한다 (없으면 중단)
#   4. 버전 반영: plugin.json, 두 README 의 version 배지
#   5. 회귀 테스트, claude plugin validate
#   6. 커밋 "release: v<버전>", 주석 태그 v<버전> (메시지는 CHANGELOG 절)
#   7. --push 면 git push --follow-tags, gh release create. 아니면 다음 명령만 출력
#
# 버전의 정본은 .claude-plugin/plugin.json 이다. 공식 문서: 마켓플레이스 항목에도
# 버전이 있으면 plugin.json 이 우선한다. 그래서 marketplace.json 에는 버전을 두지 않는다.
set -euo pipefail
cd "$(dirname "$0")/.."

VER="${1:-}"; MODE="${2:-}"
[[ "$VER" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]] || { echo "사용: scripts/release.sh <major.minor.patch> [--push]" >&2; exit 1; }
TAG="v$VER"; TODAY="$(date +%Y-%m-%d)"
REPO="https://github.com/IsthisLee/claude-korean-writing"

fail() { echo "중단: $*" >&2; git checkout -q -- . 2>/dev/null || true; exit 1; }

# 1. 검사
[ -z "$(git status --porcelain)" ] || fail "작업 트리가 clean 이 아니다. 먼저 커밋한다"
git rev-parse -q --verify "refs/tags/$TAG" >/dev/null && fail "$TAG 태그가 이미 있다"
CUR="$(python3 -c "import json;print(json.load(open('.claude-plugin/plugin.json'))['version'])")"
python3 -c "
import sys
cur=tuple(map(int,'$CUR'.split('.'))); new=tuple(map(int,'$VER'.split('.')))
sys.exit(0 if new>=cur else 1)" || fail "새 버전 $VER 이 현재 $CUR 보다 낮다"
PREV_TAG="$(git describe --tags --abbrev=0 2>/dev/null || true)"

# 2. CHANGELOG
python3 - "$VER" "$TODAY" "$PREV_TAG" "$REPO" <<'PY' || fail "CHANGELOG 처리 실패"
import io, re, sys
ver, today, prev, repo = sys.argv[1:5]
p = "CHANGELOG.md"; s = io.open(p, encoding="utf-8").read()
if re.search(rf"^## \[{re.escape(ver)}\]", s, re.M):
    print(f"  CHANGELOG: [{ver}] 절이 이미 있다")
else:
    m = re.search(r"^## \[Unreleased\]\n(.*?)(?=^## \[|^\[|\Z)", s, re.M | re.S)
    body = (m.group(1) if m else "").strip()
    if not body:
        print("CHANGELOG 의 [Unreleased] 절이 비어 있다. 릴리스 노트를 먼저 쓴다", file=sys.stderr); sys.exit(1)
    s = s.replace(m.group(0), f"## [Unreleased]\n\n## [{ver}] - {today}\n\n{body}\n\n", 1)
    print(f"  CHANGELOG: [Unreleased] → [{ver}] - {today}")
link_unrel = f"[Unreleased]: {repo}/compare/v{ver}...HEAD"
link_ver = f"[{ver}]: {repo}/compare/{prev}...v{ver}" if prev else f"[{ver}]: {repo}/releases/tag/v{ver}"
s = re.sub(r"^\[Unreleased\]: .*$", link_unrel, s, flags=re.M)
if not re.search(rf"^\[{re.escape(ver)}\]: ", s, re.M):
    s = s.replace(link_unrel, link_unrel + "\n" + link_ver, 1)
io.open(p, "w", encoding="utf-8").write(s)
PY

# 3. README 릴리스 인용구
for f in README.md README.en.md; do
  grep -q "v$VER" "$f" || fail "$f 상단 릴리스 인용구에 v$VER 이 없다. 릴리스 노트를 먼저 쓴다"
done

# 4. 버전 반영
python3 - "$VER" <<'PY'
import io, re, sys
ver = sys.argv[1]
p = ".claude-plugin/plugin.json"; s = io.open(p, encoding="utf-8").read()
s = re.sub(r'("version":\s*")[^"]+(")', lambda m: m.group(1) + ver + m.group(2), s, count=1)
io.open(p, "w", encoding="utf-8").write(s)
for p in ("README.md", "README.en.md"):
    s = io.open(p, encoding="utf-8").read()
    s = re.sub(r"(badge/version-)[^-]+(-lightgrey)", lambda m: m.group(1) + ver + m.group(2), s)
    io.open(p, "w", encoding="utf-8").write(s)
print(f"  plugin.json·README 배지 → {ver}")
PY

# 5. 검사
python3 hooks-handlers/test_posttooluse.py >/dev/null 2>&1 || fail "회귀 테스트 실패 (python3 hooks-handlers/test_posttooluse.py)"
claude plugin validate . 2>&1 | grep -q "Validation passed" || fail "claude plugin validate 실패"
echo "  회귀 테스트·validate 통과"

# 6. 커밋·태그
NOTES="$(python3 - "$VER" <<'PY'
import io, re, sys
ver = sys.argv[1]; s = io.open("CHANGELOG.md", encoding="utf-8").read()
m = re.search(rf"^## \[{re.escape(ver)}\][^\n]*\n(.*?)(?=^## \[|^\[|\Z)", s, re.M | re.S)
print((m.group(1) if m else "").strip())
PY
)"
git add -A
git commit -q -m "release: $TAG"
git tag -a "$TAG" -m "$TAG" -m "$NOTES"
echo "  커밋 $(git rev-parse --short HEAD) · 태그 $TAG"

# 7. push
if [ "$MODE" = "--push" ]; then
  git push origin HEAD --follow-tags
  gh release create "$TAG" --title "$TAG" --notes "$NOTES"
  echo "  push 와 GitHub 릴리스 완료"
else
  echo "  다음: git push origin main --follow-tags && gh release create $TAG --title $TAG --notes-file <(git tag -l --format='%(contents:body)' $TAG)"
fi
