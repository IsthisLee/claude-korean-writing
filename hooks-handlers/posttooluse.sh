#!/usr/bin/env bash
# PostToolUse: 한국어 비중이 높은 .md 파일 편집 후 AI 티 패턴을 검사한다.
# 편집을 되돌리지는 않는다. 걸린 항목을 알려 고치게 한다.
#
# 대상  : Edit / Write / MultiEdit 로 수정한 .md 파일. 편집분의 한글 비중이 30% 이상이면 전체를,
#         미만이면 한글 비중 30% 이상인 줄만 모아 검사한다 (영어 문서 안의 한국어 문단)
# 제외  : 코드블록(``` 과 ~~~), 인라인 코드, 링크 URL, 표 행, HTML 주석
# 임계  : 스킬(korean-writing)의 권고보다 느슨하게 잡는다. 오탐으로 작업을 막지 않기 위해서다.
# 누적  : 줄표(K1)와 연결어미 뒤 쉼표(K10)는 이번 편집에 하나라도 있으면 파일 전체로 판정한다. 문단
#         하나씩 고치는 동안 쌓이는 것을 잡기 위해서다. 이번 편집에 없으면 파일에 아무리 많아도 잡지 않는다.
# 코드  : K1 줄표 · K2 추상 구조어 · K3 것 구문 · K4 AI 관용구 · K5 첫째둘째 · K6 승패 의인화
#         K7 사물 의인화 · K8 번역투 · K9 부정 대구 · K10 연결어미 뒤 쉼표

set -uo pipefail

# 끄기. 세션 단위는 환경변수, 파일 단위는 파일 머리의 <!-- korean-writing: ignore --> 표시(아래 python).
[ "${KOREAN_WRITING_HOOK_DISABLED:-0}" = "1" ] && exit 0
# python3 가 없으면 검사하지 않는다. 검사기가 작업을 막는 것보다 낫다.
command -v python3 >/dev/null 2>&1 || exit 0

IN=$(cat)

# 아래 작은따옴표는 의도다. 안쪽은 python 코드라 셸이 확장하면 안 된다.
# shellcheck disable=SC2016
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

# 파일 전체가 아니라 이번에 쓴 부분만 본다 (줄표는 예외, 아래 K1).
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

# 파일 단위 끄기. 문서 머리에 <!-- korean-writing: ignore --> 를 한 줄로 두면 검사하지 않는다.
# 격식 문서(계약·약관)나 나쁜 예를 모아 둔 규칙집처럼 매번 걸리는 것이 맞지 않는 파일용이다.
#
# 줄 하나로 선 표시만 지시로 본다. 예전에는 문자열이 어디에 있든 껐는데, 그러면 이 기능을
# 설명하는 문서가 자기 검사를 통째로 건너뛴다. 이 저장소의 README·CLAUDE.md·CHANGELOG 등
# 일곱 문서가 본문과 표에서 표시 문자열을 인용한 탓에 CI 의 자기 검사를 공허하게 통과했다.
MARK_RE = re.compile(r"^[ \t]*<!--[ \t]*korean-writing:[ \t]*ignore[ \t]*-->[ \t]*$", re.M)
MARK_HEAD_LINES = 10

def marked(text):
    return bool(MARK_RE.search("\n".join(text.split("\n")[:MARK_HEAD_LINES])))

try:
    head = open(path, encoding="utf-8", errors="ignore").read(4000)
except Exception:
    head = ""
if marked(raw) or marked(head):
    sys.exit(0)

def clean(text):
    # 검사 대상에서 제외할 구간을 걷어낸다.
    # 표는 산문이 아니다. 라벨·비교·교정 예시(전/후)가 들어가므로 산문 규칙을 적용하면
    # 나쁜 예를 인용한 것까지 위반으로 잡는다. 실제로 이 플러그인의 README 가 그렇게 걸렸다.
    text = re.sub(r"```.*?```", "", text, flags=re.S)     # 코드블록
    text = re.sub(r"~~~.*?~~~", "", text, flags=re.S)     # ~~~ 울타리 코드블록
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)    # HTML 주석
    text = re.sub(r"`[^`\n]+`", "", text)                 # 인라인 코드
    text = re.sub(r"https?://\S+", "", text)              # URL
    text = re.sub(r"^\s*\|.*$", "", text, flags=re.M)     # 표 행 전체
    return text

def korean_body(text):
    # 한국어 글이면 (본문, False). 영어가 대부분이면 한글 비중 30% 이상인 줄만 모아 (본문, True).
    # 모은 한글이 20자 미만이면 (None, True). 영어 줄이 빠지므로 영어 산문의 줄표는 세지 않는다.
    body = clean(text)
    ko = len(re.findall(r"[가-힣]", body))
    if ko >= 20 and ko / max(len(body), 1) >= 0.30:
        return body, False
    lines = [l for l in body.split("\n") if l.strip()]
    lines = [l for l in lines if len(re.findall(r"[가-힣]", l)) / max(len(l), 1) >= 0.30]
    body = "\n".join(lines)
    if len(re.findall(r"[가-힣]", body)) < 20:
        return None, True
    return body, True

body, korean_lines_only = korean_body(raw)
if body is None:
    sys.exit(0)   # 한국어 글이 아니면 대상 아님

hits = []

# 파일 전체 본문. 문단 하나씩 고치는 동안 쌓이는 패턴(K1 줄표, K10 연결어미 쉼표)을 위해 한 번만 읽는다.
# Write 는 이번 내용이 곧 파일 전체라 다시 읽지 않는다.
_FILE_BODY = []

def file_body():
    if not _FILE_BODY:
        fb = None
        if tool != "Write":
            try:
                fb, _ = korean_body(open(path, encoding="utf-8", errors="ignore").read())
            except Exception:
                fb = None
        _FILE_BODY.append(fb)
    return _FILE_BODY[0]

# K1 줄표 삽입구
# 양쪽에 공백과 실제 문자가 있는 것만 센다. 표 셀을 가르는 줄표는 표 행 제외로 이미 빠져 있다.
# 이번 편집분에 하나라도 있으면 파일 전체(같은 제외·한국어 규칙)의 개수로 판정한다. 실측 문서에서
# 줄표 34개, 66개, 207개짜리 파일이 문단 하나씩 고치는 동안 만들어졌고, 편집분만 세면 한 번도 안 걸린다.
DASH = r"[^|\s]\s[—–]\s[^|\s]"
n = len(re.findall(DASH, body))
n_file = n
if n >= 1:
    fbody = file_body()
    if fbody is not None:
        n_file = max(n, len(re.findall(DASH, fbody)))
if n_file >= 4:
    what = f"줄표(—) 삽입구 {n}개" if n_file == n else f"줄표(—) 삽입구 이번 편집 {n}개, 파일 전체 {n_file}개"
    hits.append(("K1", what, "쉼표나 문장 분리로 바꾼다. 한국어에서 가장 강한 AI 티다"))

# K2 추상 구조어
# 축은 압축·건축 등에 섞이므로 앞 글자가 한글이면 제외한다.
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

# K6 승패 의인화. 정답 데이터 G06(Claude Code 의 실제 생성물)에 있는 패턴.
# 한 문서 1회는 허용하고 2회부터 잡는다(EVALUATION 4번).
m = re.findall(r"(?:가|이)\s*이(?:긴다|깁니다|겼다|겼습니다|기고|기는|길\s)", body)
if len(m) >= 2:
    hits.append(("K6", f"승패 의인화 {len(m)}회", "우선한다·따른다·앞선다 로 직결한다"))

# K7 사물 의인화 — 영어 비유 직역. 사물 명사 + 사람이 하는 동작.
THING = r"(?:화면|서버|장비|시스템|페이지|프로세스|코드|스크립트|훅|모듈|테스트|빌드)"
# 죽다는 뺀다. 서버가 죽다·프로세스가 죽다는 개발자의 일상어라 실측 문서에서 자연스럽게 쓰였다.
m = re.findall(THING + r"(?:이|가)\s*(?:굳|쓰러지|쓰러졌|넘어지|일어서|잠들)", body)
m += re.findall(r"(?:넘어뜨리|일으켜\s*세우|쓰러뜨리)", body)
if m:
    hits.append(("K7", f"사물 의인화 {len(m)}회", "굳다·쓰러지다 같은 직역 비유 대신 멈춘다·죽는다처럼 사실대로 서술한다. 예: 화면이 굳어 → 화면이 멈춰"))

# K8 번역투
# "~에 대해"·"~를 통해" 횟수는 세지 않는다. 실측(한국어 문서 143개)에서 3회 이상인 문서 10개가
# 전부 사람이 2022~23년에 쓴 글이었고, 2026년에 Claude 가 쓴 문서는 하나도 걸리지 않았다.
# 판별력이 없는 규칙은 사람의 글만 잡는다. 생성 단계의 회피는 스킬이 맡는다.
tr = []
n_ga = len(re.findall(r"가지고\s*있", body))
if n_ga: tr.append(f"가지고 있다 {n_ga}회")
n_pas = len(re.findall(r"되어지|지게\s*된다|되어진다", body))
if n_pas: tr.append(f"이중 피동 {n_pas}회")
n_uy = len(re.findall(r"에\s*의해", body))
if n_uy >= 2: tr.append(f"~에 의해 {n_uy}회")
if tr:
    hits.append(("K8", " / ".join(tr), "능동으로 바꾸거나 조사를 구체화한다"))

# K9 부정 대구 "A가 아니라 B" (im-not-ai taxonomy C-8)
# 그 규칙집에서 실측 판별력이 가장 큰 항목이다. 사람 대비 밀도 9.2배, 개인 블로그 대비 18배이고
# 세 모델과 세 과업 조건에서 모두 재현됐다. 규칙집의 임계는 2회지만 훅은 3회부터 잡는다.
# 이 머신의 한국어 .md 205개 실측에서 3회 이상은 2023년 이전 문서 0/32, 2026년 문서 30/173 이다.
# 정규식은 규칙집 구현(metrics_v2._ANTITHESIS_RE)을 따르되 조건절 "아니라면"·"아니라서"만 뺐다. 대구가
# 아니라 가정이다. 생성물 실측에서 "일요일 기준이 아니라면"이 대구로 잡혔다. 문서 205개 판정은 그대로다.
# 대안을 더 넓히는 쪽(것은 아니다·인가,)도 재 봤는데 2026년 적중이 하나 늘고 2회 임계에서 오탐이 하나 났다.
m = re.findall(r"(?:가|이)\s*아니라(?![면서])|이기\s*이전에|되기\s*이전에|이기보다", body)
if len(m) >= 3:
    hits.append(("K9", f"부정 대구 {len(m)}회", "하나만 남기고 나머지는 그냥 단언한다. 예: A가 아니라 B다 → B다"))

# K10 연결어미 뒤 쉼표 (im-not-ai taxonomy C-11)
# 그 규칙집에서 단일 지표 분리도가 가장 큰 항목이다(KatFish ACL 2025, 에세이 사람 4.10% 대 AI 19.83%).
# 한국어는 연결어미가 이미 호흡을 끊으므로 쉼표를 덧붙일 자리가 드문데, 영어 감각이 옮으면 자동으로 찍는다.
# 개수만 보면 긴 문서가 불리하고 비율만 보면 짧은 문서가 불리해 둘 다 넘을 때만 잡는다.
# 이 머신 실측에서 6회 이상이면서 30% 이상은 2023년 이전 문서 0/32, 2026년 문서 21/173 이다.
# 줄표와 같은 이유로 파일 전체로 판정한다. 문단씩 고치는 동안 쌓이는 것이 이 패턴의 실제 모습이다.
ENDING = r"(?:고|며|지만|면서|아서|어서)"

def comma_ratio(t):
    total = len(re.findall(ENDING + r"(?=[\s,\.!?、。]|$)", t))
    return len(re.findall(ENDING + r"\s*,", t)), total

n, total = comma_ratio(body)
n_file, total_file = n, total
if n >= 1:
    fbody = file_body()
    if fbody is not None:
        fn, ft = comma_ratio(fbody)
        if fn > n:
            n_file, total_file = fn, ft
if n_file >= 6 and total_file and n_file / total_file >= 0.30:
    pct = round(n_file / total_file * 100)
    what = f"연결어미 뒤 쉼표 {n_file}회 (연결어미의 {pct}%)"
    if n_file != n:
        what = f"연결어미 뒤 쉼표 이번 편집 {n}회, 파일 전체 {n_file}회 (연결어미의 {pct}%)"
    hits.append(("K10", what, "쉼표를 지운다. 예: 훅을 더했고, 규칙집을 바꿨다 → 훅을 더했고 규칙집을 바꿨다"))

if not hits:
    sys.exit(0)

name = os.path.basename(path)
print(f"[korean-writing] {name} 에 AI 티 패턴이 있다. 편집은 그대로 두었으니 확인하고 고쳐라.", file=sys.stderr)
if korean_lines_only:
    print("  (영어가 대부분인 편집이라 한글 비중 30% 이상인 줄만 검사했다)", file=sys.stderr)
for code, what, how in hits:
    print(f"  {code}  {what} — {how}", file=sys.stderr)
print("  교정 규칙은 korean-writing 스킬에 있다. 격식 문서(계약·약관·법률)면 파일 머리에 <!-- korean-writing: ignore --> 를 넣으면 다시 알리지 않는다.", file=sys.stderr)
sys.exit(2)
'
