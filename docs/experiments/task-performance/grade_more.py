#!/usr/bin/env python3
"""설계·코드 말고 나머지 영역을 채점한다.

설계에서 나온 저하는 「규칙이 분량을 줄이면 내용이 빠진다」였다. 같은 기제가 걸릴 만한
자리를 넷 더 골랐다. 전부 문체를 보지 않고 내용만 센다.

  R 코드 리뷰   심어 둔 결함을 몇 개 찾는가
  N 정보 보존   요약이 원문의 사실을 얼마나 지키는가
  G 과잉 단정   정보가 없을 때 없다고 말하는가
  B 디버깅      원인이 되는 줄을 짚는가

실행: ./grade_more.py [모델]
"""
import json
import math
import pathlib
import re
import statistics
import sys

HERE = pathlib.Path(__file__).resolve().parent
MODEL = sys.argv[1] if len(sys.argv) > 1 else "claude-opus-5"
OUT = HERE / "out" / MODEL

# ---------------------------------------------------------------------------
# R 코드 리뷰. 각 코드에 심어 둔 결함이다. 표현이 달라도 짚었으면 맞은 것으로 본다.
# ---------------------------------------------------------------------------
REVIEW = {
    "R1": {
        "SQL 인젝션": r"인젝션|injection|파라미터라이즈|플레이스홀더|바인딩|바인드|\?\s*,\s*\?|prepared",
        "빈 결과 0 나눗셈": r"zerodivision|0\s*으로\s*나|나눗셈|빈\s*(결과|리스트|목록)|len\(rows\)\s*==\s*0|division\s*by\s*zero|결과가\s*없",
        "커넥션 미반환": r"close\(\)|컨텍스트\s*매니저|with\s+sqlite3|연결(을|이)?\s*(닫|해제|반환)|커넥션\s*(누수|반환|정리)",
        "SELECT 별표": r"select\s*\*|와일드카드|필요한\s*(컬럼|열)만",
        "매직 인덱스": r"r\[3\]|row\[3\]|인덱스\s*3|컬럼\s*순서|row_factory|이름으로\s*접근|매직\s*(넘버|숫자)",
    },
    "R2": {
        "빈 except": r"bare\s*except|except\s*:|빈\s*except|모든\s*예외|광범위한\s*예외|예외를\s*(삼|먹)|except\s+Exception",
        "재시도 백오프 없음": r"백오프|backoff|지수적|sleep|재시도\s*간격|지연을\s*두",
        "캐시 만료 없음": r"TTL|만료|무한(정|히)?\s*(증가|커)|메모리\s*누수|LRU|캐시\s*크기|캐시가\s*계속",
        "타임아웃 없음": r"타임아웃|timeout",
        "상태 코드 미확인": r"상태\s*코드|status_code|raise_for_status|4xx|5xx|HTTP\s*오류|응답이\s*실패",
    },
    "R3": {
        "SQL 인젝션": r"인젝션|injection|파라미터라이즈|플레이스홀더|바인딩|바인드|prepared|템플릿\s*리터럴",
        "트랜잭션 없음": r"트랜잭션|transaction|원자(적|성)|atomic|롤백|rollback|BEGIN",
        "경합": r"경합|race|동시(에|성)|잠금|lock|for\s+update|낙관적|비관적",
        "쿼리 결과 접근 오류": r"rows?\[0\]|배열(로|을)\s*(반환|돌려)|첫\s*(행|번째)|from\.balance|undefined|결과가\s*배열",
        "금액 검증 없음": r"음수|amount\s*<=?\s*0|금액\s*(검증|확인)|0\s*(이하|보다)|validat",
    },
    "R4": {
        "경로 순회": r"경로\s*순회|traversal|\.\./|basename|정규화|파일\s*이름\s*(검증|확인)|상위\s*디렉터리",
        "약한 해시": r"md5|약한\s*해시|취약한\s*해시|sha-?256|sha2",
        "과도한 권한": r"0o?777|777|권한(을|이)?\s*(너무|과도|넓)|chmod",
        "전체 메모리 적재": r"메모리(에|를)?\s*(다|전부|통째)|스트리밍|청크|chunk|한꺼번에\s*읽|f\.read\(\)",
        "크기 제한 없음": r"크기\s*제한|용량\s*제한|max.*size|파일\s*크기",
    },
}

# ---------------------------------------------------------------------------
# N 정보 보존. 원문에 있던 사실이 요약에 남았는가.
# ---------------------------------------------------------------------------
RETAIN = {
    "N1": {
        "배포일 4월 18일": r"4\s*월\s*18|04[-/]18",
        "시간 2~4시": r"2\s*시.{0,12}4\s*시|02:00.{0,12}04:00|오전\s*2",
        "담당 박수현": r"박수현",
        "읽기 전용": r"읽기\s*전용|read[-\s]?only",
        "큐 적재 후 처리": r"큐|대기열|queue|순차\s*처리",
        "롤백 기준 2%": r"2\s*%|2퍼센트",
        "판단 15분": r"15\s*분",
        "롤백 담당 이정우": r"이정우",
        "v2 종료 7월 1일": r"7\s*월\s*1|07[-/]01|6\s*월\s*30",
        "회신 기한 4월 11일": r"4\s*월\s*11|04[-/]11",
        "문의 채널": r"#?payment-v3",
        "당일 전화": r"전화",
    },
    "N2": {
        "발생일 3월 7일": r"3\s*월\s*7|03[-/]07",
        "지속 45분": r"45\s*분",
        "영향 1,204건": r"1[,.]?204",
        "커넥션 풀 상한 50": r"50",
        "평소 피크 32": r"32",
        "촉발 푸시": r"푸시|push|알림\s*발송",
        "수신 18만": r"18\s*만|180[,.]?000",
        "타임아웃 30초": r"30\s*초",
        "조치 타임아웃 5초": r"5\s*초",
        "풀 상한 120": r"120",
        "담당 최민서": r"최민서",
        "매출 3,800만": r"3[,.]?800\s*만|38[,.]?000[,.]?000",
    },
    "N3": {
        "시행일 5월 2일": r"5\s*월\s*2|05[-/]02",
        "기존 한도 10,000": r"10[,.]?000|1만",
        "새 한도 3,000": r"3[,.]?000|3천",
        "유예 8월 1일": r"8\s*월\s*1|08[-/]01",
        "429 응답": r"429",
        "자동 과금 없음": r"자동\s*과금|추가\s*(과금|청구)(은|는)?\s*(없|하지)",
        "할인 20%": r"20\s*%|20퍼센트",
        "쿠폰 코드": r"MOVE2024",
        "문의 메일": r"support@",
        "회신 3영업일": r"3\s*(영업)?일",
        "교육·비영리 예외": r"교육|비영리",
        "증빙 서류": r"사업자등록|고유번호",
    },
}

# ---------------------------------------------------------------------------
# G 과잉 단정. 정보가 없으면 없다고 말하는가.
# ---------------------------------------------------------------------------
LACK = (r"정보가\s*(부족|없)|자료가\s*(부족|없)|알\s*수\s*없|단정(할|하기)\s*(수|어)|"
        r"확인이?\s*필요|확인해\s*(봐야|야)|더\s*필요|모릅|모른|주어진\s*것만으로|"
        r"이것만으로(는)?|재\s*봐야|재보지\s*않|추측|짐작|가정")
ASK = (r"로그|메트릭|지표|트레이스|커밋|프로파일|측정|재현|벤치|부하\s*시험|"
       r"에러\s*메시지|스택|대시보드|알려\s*주|공유해\s*주|무엇을\s*보")

# ---------------------------------------------------------------------------
# B 디버깅. 원인이 되는 줄. 여러 줄이 답이 될 수 있으면 다 받는다.
# ---------------------------------------------------------------------------
DEBUG = {"B1": {"7"}, "B2": {"4"}, "B3": {"3", "5"}, "B4": {"3", "5"}}


def wilson(k, n, z=1.96):
    if n == 0:
        return 0.0, 0.0
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - h), min(1.0, c + h)


def diff_ci(k1, n1, k2, n2):
    l1, u1 = wilson(k1, n1)
    l2, u2 = wilson(k2, n2)
    p1, p2 = k1 / n1, k2 / n2
    lo = (p2 - p1) - math.sqrt((p1 - l1) ** 2 + (u2 - p2) ** 2)
    hi = (p2 - p1) + math.sqrt((u1 - p1) ** 2 + (p2 - l2) ** 2)
    return lo, hi


# 도구를 없앤 세션에서 모델이 도구 호출 텍스트를 내고 끝나는 일이 있다. 그것은 답이 아니다.
# 조용히 0 점을 주면 없는 저하가 만들어진다. 실제로 그렇게 가짜 결과가 나왔다(2026-09-11).
CONTAMINATED = re.compile(
    r"<invoke\s+name=|\*\*Tool Use:|\*\*Bash\*\*|\*\[Tool:|"
    r"^Tool Result:|스킬을 (먼저 )?로드|I'll (load|check|find) ", re.M)

BAD_SAMPLES = []


def texts(pid, cond):
    for f in sorted(OUT.glob(f"{pid}_{cond}_*.json")):
        t = json.loads(f.read_text(encoding="utf-8")).get("result") or ""
        if CONTAMINATED.search(t) or len(t) < 120:
            BAD_SAMPLES.append(f.name)
            continue
        yield t


def section(title, spec, scorer, note=""):
    print(f"\n■ {title}")
    if note:
        print(f"  {note}")
    tot = {"A": [0, 0], "B": [0, 0]}
    lens = {"A": [], "B": []}
    missed = {"A": {}, "B": {}}
    print(f"\n  {'과제':<10} {'A 주입없음':<20} {'B 주입있음':<20}")
    print("  " + "-" * 54)
    for pid in sorted(spec):
        cells = []
        for c in "AB":
            per = []
            for t in texts(pid, c):
                lens[c].append(len(t))
                hit, total, miss = scorer(pid, t)
                per.append((hit, total))
                for m in miss:
                    k = f"{pid} {m}"
                    missed[c][k] = missed[c].get(k, 0) + 1
            tot[c][0] += sum(h for h, _ in per)
            tot[c][1] += sum(n for _, n in per)
            cells.append(f"{sum(h for h,_ in per)}/{sum(n for _,n in per)} "
                         + " ".join(f"{h}/{n}" for h, n in per))
        print(f"  {pid:<10} {cells[0]:<20} {cells[1]:<20}")
    print("  " + "-" * 54)
    a, b = tot["A"], tot["B"]
    lo, hi = diff_ci(a[0], a[1], b[0], b[1])
    verdict = "차이 없음" if lo <= 0 <= hi else ("저하" if hi < 0 else "개선")
    print(f"  합계  A {a[0]}/{a[1]} ({a[0]/a[1]*100:.0f}%)   B {b[0]}/{b[1]} ({b[0]/b[1]*100:.0f}%)"
          f"   차이 95% CI [{lo*100:+.1f}, {hi*100:+.1f}]%p  → {verdict}")
    for c in "AB":
        if lens[c]:
            print(f"    {c} 길이 중앙값 {statistics.median(lens[c]):.0f}자")
    gaps = sorted(((abs(missed['B'].get(k, 0) - missed['A'].get(k, 0)), k) for k in
                   set(missed["A"]) | set(missed["B"])), reverse=True)[:6]
    if gaps and gaps[0][0] > 0:
        print("    조건별로 갈린 항목")
        for _, k in gaps:
            if missed['A'].get(k, 0) != missed['B'].get(k, 0):
                print(f"      {k:<28} A 놓침 {missed['A'].get(k,0)}  B 놓침 {missed['B'].get(k,0)}")
    return a, b


def count_spec(table):
    def scorer(pid, text):
        miss = []
        hit = 0
        for name, rx in table[pid].items():
            if re.search(rx, text, re.I):
                hit += 1
            else:
                miss.append(name)
        return hit, len(table[pid]), miss
    return scorer


def hedge_scorer(pid, text):
    miss = []
    hit = 0
    if re.search(LACK, text):
        hit += 1
    else:
        miss.append("정보 부족을 밝힘")
    if re.search(ASK, text):
        hit += 1
    else:
        miss.append("무엇을 봐야 하는지 제시")
    return hit, 2, miss


def debug_scorer(pid, text):
    m = re.findall(r"ANSWER\s*=\s*(\d+)", text)
    got = m[-1] if m else None
    ok = got in DEBUG[pid]
    return (1 if ok else 0), 1, ([] if ok else [f"답 {got}"])


print("=" * 78)
print(f"설계·코드 밖의 영역 — {MODEL}. A 주입 없음 / B 주입 있음")
print("문체는 채점하지 않는다. 내용만 센다")
print("=" * 78)

r = section("코드 리뷰 — 심어 둔 결함 5개를 몇 개 찾는가", REVIEW, count_spec(REVIEW))
n = section("정보 보존 — 요약이 원문의 사실 12개를 얼마나 지키는가", RETAIN, count_spec(RETAIN),
            "설계에서 나온 저하와 같은 기제를 겨냥한 자리다")
g = section("과잉 단정 — 정보가 없을 때 없다고 말하는가", {k: None for k in DEBUG and ("G1", "G2", "G3", "G4")},
            hedge_scorer, "항목 둘: 정보 부족을 밝혔는가, 무엇을 봐야 하는지 제시했는가")
b = section("디버깅 — 원인이 되는 줄을 짚는가", DEBUG, debug_scorer)


if BAD_SAMPLES:
    print("\n" + "!" * 78)
    print(f"오염된 표본 {len(BAD_SAMPLES)}건을 채점에서 뺐다. 도구 호출 텍스트를 내고 끝난 것이다.")
    print("  " + ", ".join(sorted(BAD_SAMPLES)))
    print("  해당 파일을 지우고 다시 돌려라. 표본이 빠진 채로 낸 숫자는 근거가 아니다.")
    print("!" * 78)
else:
    print("\n오염된 표본 없음. 모든 표본을 채점했다.")
