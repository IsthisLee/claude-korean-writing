#!/usr/bin/env bash
# PostToolUse: 한국어 비중이 높은 .md 파일 편집 후 AI 티 패턴을 검사한다.
# 편집을 되돌리지는 않는다. 걸린 항목을 알려 고치게 한다.
#
# 대상  : Edit / Write / MultiEdit 로 수정한 .md 파일 중 한글 비중 30% 이상
# 제외  : 코드블록, 인라인 코드, 링크 URL, 표 구분선
# 임계  : 스킬(korean-writing)의 권고보다 느슨하게 잡는다. 오탐으로 작업을 막지 않기 위해서다.

set -uo pipefail
IN=$(cat)

printf '%s' "$IN" | python3 -c '
import sys, json, re, os

try:
    d = json.load(sys.stdin)
except Exception:
    sys.exit(0)

tool = d.get("tool_name", "")
if tool not in ("Edit", "Write", "MultiEdit", "NotebookEdit"):
    sys.exit(0)

ti = d.get("tool_input") or {}
path = ti.get("file_path") or ti.get("notebook_path") or ""
if not path.endswith(".md"):
    sys.exit(0)

# 파일 전체가 아니라 이번에 쓴 부분만 본다.
# 전체를 보면 예전부터 있던 표현이 매 편집마다 다시 걸려 경고가 소음이 된다.
parts = []
if ti.get("content"):
    parts.append(str(ti["content"]))
if ti.get("new_string"):
    parts.append(str(ti["new_string"]))
for e in (ti.get("edits") or []):
    if isinstance(e, dict) and e.get("new_string"):
        parts.append(str(e["new_string"]))
raw = "\n".join(parts)
if not raw:
    sys.exit(0)

# --- 검사 대상에서 제외할 구간을 걷어낸다 ---
body = re.sub(r"```.*?```", "", raw, flags=re.S)     # 코드블록
body = re.sub(r"`[^`\n]+`", "", body)                 # 인라인 코드
body = re.sub(r"https?://\S+", "", body)              # URL
body = re.sub(r"^\s*\|.*$", "", body, flags=re.M)             # 표 행 전체
# 표는 산문이 아니다. 라벨·비교·교정 예시(전/후)가 들어가므로 산문 규칙을 적용하면
# 나쁜 예를 인용한 것까지 위반으로 잡는다. 실제로 이 플러그인의 README 가 그렇게 걸렸다.

ko = len(re.findall(r"[가-힣]", body))
if ko < 20 or ko / max(len(body), 1) < 0.30:
    sys.exit(0)   # 한국어 문서가 아니면 대상 아님

hits = []

# K1 줄표 삽입구
# 양쪽에 공백과 실제 문자가 있는 것만 센다(Forge 의 INTERJECT 와 같은 기준).
n = len(re.findall(r"[^|\s]\s[—–]\s[^|\s]", body))
if n >= 4:
    hits.append(("K1", f"줄표(—) 삽입구 {n}개", "쉼표나 문장 분리로 바꾼다. 한국어에서 가장 강한 AI 티다"))

# K2 추상 구조어
# '축'은 압축·건축 등에 섞이므로 앞 글자가 한글이면 제외한다.
n = len(re.findall(r"(?<![가-힣])축(?:이|은|을|으로)|갈래|결(?:이|은)\s*다르|레이어", body))
if n >= 3:
    hits.append(("K2", f"추상 구조어 {n}회", "기준·경우·종류·단계 같은 구체 명사로 바꾼다"))

# K3 번역투 것 구문
m = re.findall(r"것들이[었다]|것들을|하는 것이 가능", body)
if m:
    hits.append(("K3", f"번역투 것 구문 {len(m)}회", "구체 명사로 바꾼다. 예: 탈이 날 것들이었다 → 탈이 날 문제였다"))

# K4 AI 관용구
m = re.findall(r"결론적으로|종합하면|요약하자면|중요한 점은|시사하는 바가 크|주목할 만하|혁신적|획기적|압도적|라고 할 수 있(?:습니다|다)", body)
if m:
    hits.append(("K4", f"AI 관용구 {len(m)}회", "대부분 삭제해도 뜻이 통한다"))

# K5 기계적 병렬
if re.search(r"첫째[,.]", body) and re.search(r"둘째[,.]", body):
    hits.append(("K5", "첫째·둘째 병렬", "하나둘은 서술문으로 녹인다"))

# K6 승패 의인화 — 외부 출판사 편집부가 줄표와 함께 AI 의심 표현으로 지목한 패턴
# taxonomy D-8 의 처방이 "한 문서 1회 이하" 이므로 2회부터 잡는다.
m = re.findall(r"(?:가|이)\s*이(?:긴다|깁니다|겼다|겼습니다|기고|기는|길\s)", body)
if len(m) >= 2:
    hits.append(("K6", f"승패 의인화 {len(m)}회", "우선한다·따른다·앞선다 로 직결한다"))

# K7 사물 의인화 — 영어 비유 직역. 사물 명사 + 사람이 하는 동작.
THING = r"(?:화면|서버|장비|시스템|페이지|프로세스|코드|스크립트|훅|모듈|테스트|빌드)"
m = re.findall(THING + r"(?:이|가)\s*(?:굳|쓰러지|쓰러졌|넘어지|일어서|죽어|잠들)", body)
m += re.findall(r"(?:넘어뜨리|일으켜\s*세우|쓰러뜨리)", body)
if m:
    hits.append(("K7", f"사물 의인화 {len(m)}회", "멈춘다·죽는다 대신 사실대로 서술한다. 예: 화면이 굳어 → 화면이 멈춰"))

# K8 번역투
tr = []
n_dae = len(re.findall(r"에\s*대해|에\s*대하여|에\s*대한", body))
n_tong = len(re.findall(r"(?:를|을)\s*통해|(?:를|을)\s*통하여", body))
if n_dae >= 3: tr.append(f"~에 대해 {n_dae}회")
if n_tong >= 3: tr.append(f"~를 통해 {n_tong}회")
n_ga = len(re.findall(r"가지고\s*있", body))
if n_ga: tr.append(f"가지고 있다 {n_ga}회")
n_pas = len(re.findall(r"되어지|지게\s*된다|되어진다", body))
if n_pas: tr.append(f"이중 피동 {n_pas}회")
n_uy = len(re.findall(r"에\s*의해", body))
if n_uy >= 2: tr.append(f"~에 의해 {n_uy}회")
if tr:
    hits.append(("K8", " / ".join(tr), "능동으로 바꾸거나 조사를 구체화한다"))

if not hits:
    sys.exit(0)

name = os.path.basename(path)
print(f"[korean-writing] {name} 에 AI 티 패턴이 있다. 편집은 그대로 두었으니 확인하고 고쳐라.", file=sys.stderr)
for code, what, how in hits:
    print(f"  {code}  {what} — {how}", file=sys.stderr)
print("  교정 규칙은 korean-writing 스킬에 있다. 격식 문서(계약·약관·법률)면 무시해도 된다.", file=sys.stderr)
sys.exit(2)
'
