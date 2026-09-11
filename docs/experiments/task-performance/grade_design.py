#!/usr/bin/env python3
"""설계 과제를 채점한다. 문체를 보지 않는 객관 지표다.

설계 답을 사람이 읽고 견주면 문체에 끌린다. 주입을 받은 쪽은 불릿과 소제목이 없어
같은 내용이라도 다르게 읽힌다. 그래서 여기서는 **그 설계에 반드시 나와야 하는 개념이
실제로 나왔는지**만 센다. 표현이 어떻든 개념을 짚었으면 맞은 것이다.

개념 목록은 각 문제에서 빠지면 설계가 틀리는 것들이다. 정규식은 한국어와 영어를 함께 받는다.
길이도 같이 낸다. 주입 규칙이 글을 짧게 만들어 개념이 덜 나왔다면 그것도 저하이기 때문이다.

실행: ./grade_design.py [모델]
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

# 문제마다 "빠지면 설계가 틀리는" 개념이다. 표현이 달라도 되게 대안을 넉넉히 뒀다.
CONCEPTS = {
    "D1": {
        "멱등 처리": r"멱등|idempoten",
        "이벤트 식별자": r"이벤트\s*(ID|아이디|식별자)|event[_\s]?id|delivery[_\s]?id|웹훅\s*(ID|아이디)|메시지\s*(ID|아이디)",
        "유니크 제약": r"유니크|unique|고유\s*(제약|인덱스)|중복\s*키|기본\s*키|primary\s*key",
        "트랜잭션": r"트랜잭션|transaction|원자적|atomic",
        "순서 판별": r"버전|version|시퀀스|sequence|타임스탬프|timestamp|발생\s*시각|occurred|이벤트\s*시각",
        "상태 전이": r"상태\s*(전이|기계|머신)|state\s*machine|전이\s*규칙|되돌아가지",
        "경합 처리": r"경합|race|잠금|lock|for\s+update|동시에\s*들어",
        "실패 처리": r"재시도|retry|데드\s*레터|dead[-\s]?letter|DLQ|실패\s*(큐|처리)",
    },
    "D2": {
        "테넌트 식별자": r"테넌트|tenant|고객사\s*(ID|아이디|식별자)|org(anization)?[_\s]?id",
        "행 수준 보안": r"row[-\s]?level\s*security|RLS|행\s*수준|정책\s*기반\s*접근",
        "격리 방식 선택": r"스키마\s*(분리|별|당)|데이터베이스\s*(분리|별)|공유\s*(스키마|테이블)|silo|pool",
        "세션 컨텍스트": r"세션\s*(변수|컨텍스트)|current_setting|SET\s+\w|커넥션\s*(풀|당)",
        "복합 인덱스": r"인덱스|index|기본\s*키.*테넌트|테넌트.*기본\s*키",
        "실수 방지 계층": r"기본\s*(필터|스코프)|default\s*scope|미들웨어|리포지토리|ORM|공통\s*계층|강제",
        "떼어내기": r"샤드|shard|분리\s*이전|이전|migrat|전용\s*(DB|데이터베이스|인스턴스)",
        "감사와 점검": r"감사|audit|점검|테스트|검증",
    },
    "D3": {
        "직접 업로드": r"presigned|프리사인|직접\s*업로드|S3|오브젝트\s*스토리지|블롭|blob",
        "비동기 처리": r"큐|queue|워커|worker|잡|job|비동기|백그라운드",
        "스트리밍 처리": r"스트리밍|stream|청크|chunk|배치|batch|한\s*줄씩|메모리에\s*다\s*올리지",
        "진행 상황": r"진행\s*(률|상황|상태)|progress|퍼센트",
        "재개": r"재개|resume|체크포인트|checkpoint|오프셋|offset|이어서",
        "대량 적재": r"COPY|벌크|bulk|대량\s*(삽입|적재)|batch\s*insert",
        "검증 단계": r"검증|validat|스키마\s*확인|헤더\s*확인",
        "중복 방지": r"멱등|idempoten|중복|dedup",
    },
    "D4": {
        "만료 시간": r"TTL|만료|expire|유효\s*기간",
        "무효화": r"무효화|invalidat|퍼지|purge|삭제\s*이벤트|쓰기\s*시\s*(갱신|삭제)",
        "스탬피드": r"스탬피드|stampede|thundering|한꺼번에|동시에\s*몰|싱글\s*플라이트|single[-\s]?flight|뮤텍스|잠금|lock",
        "낡은 값": r"stale|낡은|오래된|일관성|eventual|SWR",
        "키 설계": r"키\s*(설계|이름|전략)|cache\s*key|캐시\s*키",
        "계층": r"로컬\s*캐시|인메모리|in[-\s]?memory|CDN|L1|다층|여러\s*단계",
        "갱신 방식": r"write[-\s]?through|write[-\s]?behind|캐시\s*어사이드|cache[-\s]?aside|lazy",
        "적중률 관측": r"적중률|hit\s*rate|지표|모니터|관측",
    },
    "D5": {
        "확장 수축": r"확장.*수축|expand.*contract|단계적\s*(변경|배포)",
        "새 컬럼 추가": r"추가|add\s+column|새\s*컬럼",
        "이중 쓰기": r"이중\s*쓰기|dual[-\s]?write|양쪽\s*(에|다)\s*쓰|둘\s*다\s*쓰",
        "백필": r"백필|backfill|채워\s*넣|기존\s*(행|데이터).*채",
        "읽기 전환": r"읽기(를|를 새|는).*(전환|옮|바꾸)|read\s*from\s*new|새\s*컬럼(에서|을)\s*읽",
        "배포 순서": r"단계|순서|먼저|그다음|배포\s*순",
        "롤백": r"롤백|rollback|되돌|복구",
        "옛 컬럼 제거 시점": r"(삭제|제거|drop).*(컬럼|column)|컬럼.*(삭제|제거|drop)",
    },
}


# 장문 설계. 빠짐없이 늘어놓아야 하는 과제다. 규칙이 분량을 누르면 여기서 가장 먼저 드러난다.
# 항목이 열여섯이라 짧은 과제(여덟)보다 잃을 것이 많다.
LONG_CONCEPTS = {
    "L1": {
        "PG 장애·타임아웃": r"PG|외부\s*결제|결제사|타임아웃|timeout",
        "멱등·재시도": r"멱등|idempoten|재시도|retry",
        "Kafka 유실·지연": r"kafka|이벤트\s*(유실|지연|누락)|컨슈머\s*랙|lag|오프셋",
        "이벤트 순서": r"순서|ordering|파티션|partition",
        "아웃박스·이중 쓰기": r"아웃박스|outbox|이중\s*쓰기|dual[-\s]?write|CDC",
        "DB 복제·페일오버": r"복제|replica|페일오버|failover|standby|이중화",
        "커넥션 풀": r"커넥션\s*(풀|수)|connection\s*pool|풀\s*고갈|커넥션이\s*모자",
        "Redis 공유 결합": r"redis.{0,20}(공유|같이|한\s*개|하나)|캐시(를)?\s*공유|캐시\s*분리",
        "단일 장애점": r"SPOF|단일\s*장애|단일\s*지점|한\s*군데가\s*죽",
        "게이트웨이 병목": r"게이트웨이|rate\s*limit|레이트\s*리밋|스로틀|throttl|병목",
        "배치 실패·재실행": r"배치.{0,20}(실패|재실행|재처리|중단)|정산.{0,20}(실패|재실행|재처리)",
        "정합성·대사": r"불일치|정합성|대사|reconcil|맞춰\s*보|검증",
        "서킷·백프레셔": r"서킷|circuit|백프레셔|backpressure|벌크헤드|bulkhead|격벽",
        "사가·분산 트랜잭션": r"사가|saga|보상\s*(트랜잭션|처리)|2PC|분산\s*트랜잭션|최종\s*일관성",
        "관측·알림": r"모니터|관측|알림|알럿|alert|메트릭|대시보드",
        "데드레터·재처리": r"데드\s*레터|dead[-\s]?letter|DLQ|재처리\s*큐",
    },
    "L2": {
        "인증·인가": r"인증|인가|권한|authn|authz|OAuth|세션",
        "시크릿 관리": r"시크릿|secret|키\s*관리|자격\s*증명|환경\s*변수|볼트|vault",
        "취약점 점검": r"취약점|스캔|의존성\s*점검|SAST|DAST|펜테스트|모의\s*해킹",
        "전송 암호화": r"TLS|HTTPS|전송\s*(구간)?\s*암호",
        "저장 암호화": r"저장\s*(시)?\s*암호|at[-\s]?rest|디스크\s*암호|컬럼\s*암호",
        "부하 시험": r"부하\s*(시험|테스트)|load\s*test|스트레스|k6|성능\s*시험",
        "응답 시간 목표": r"응답\s*시간|p9[59]|레이턴시|SLO|SLA|지연\s*목표",
        "자동 확장": r"오토\s*스케일|auto\s*scal|자동\s*확장|스케일\s*아웃",
        "모니터링·알림": r"모니터|관측|알림|알럿|alert|메트릭|대시보드",
        "로그 수집": r"로그\s*(수집|집계|보관)|로깅|구조화\s*로그",
        "배포·롤백": r"롤백|rollback|배포\s*(전략|절차)|카나리|블루그린",
        "온콜·장애 대응": r"온콜|on[-\s]?call|장애\s*(대응|훈련)|런북|runbook|비상\s*연락",
        "백업·복구": r"백업|복구|restore|RPO|RTO|재해",
        "데이터 마이그레이션": r"마이그레이션|migrat|이관|스키마\s*변경",
        "개인정보·규정": r"개인정보|GDPR|프라이버시|동의|약관|보존\s*기간",
        "감사 로그": r"감사\s*(로그|추적)|audit",
    },
    "L3": {
        "스트랭글러": r"스트랭글러|strangler|점진(적)?\s*(분리|이관)|조금씩\s*떼",
        "경계 식별": r"경계|바운디드|bounded\s*context|도메인\s*(분석|모델)|책임\s*분리",
        "외래키 정리": r"외래\s*키|foreign\s*key|\bFK\b|참조(를)?\s*(끊|제거|분리)|조인(을)?\s*(제거|없)",
        "DB 분리": r"(DB|데이터베이스|스키마)(를)?\s*(분리|쪼개|나누)|전용\s*(DB|데이터베이스)",
        "이중 쓰기·CDC": r"이중\s*쓰기|dual[-\s]?write|CDC|아웃박스|outbox|동기화",
        "게이트웨이·라우팅": r"게이트웨이|라우팅|프록시|proxy|앞단에서\s*갈",
        "계약 테스트": r"계약\s*테스트|contract\s*test|스키마\s*호환|하위\s*호환|backward",
        "무중단 전환": r"무중단|expand|확장.{0,6}수축|블루그린|카나리|canary|점진\s*전환",
        "롤백": r"롤백|rollback|되돌리|복구",
        "사가·최종 일관성": r"사가|saga|보상|최종\s*일관성|eventual|분산\s*트랜잭션",
        "관측성": r"관측|모니터|추적|tracing|분산\s*추적|로그\s*수집",
        "조직·소유": r"팀(을|이|마다)|조직|소유(권|자)|ownership|콘웨이|conway",
        "네트워크 지연": r"네트워크|지연|레이턴시|latency|홉|원격\s*호출|호출\s*비용",
        "정합성 검증": r"정합성|대사|reconcil|비교(해)?\s*검증|이중\s*검증|섀도",
        "단계 순서": r"1\s*단계|첫\s*단계|단계(별|를)|순서(대로|를)|먼저.{0,30}그다음",
        "되돌리기 어려운 지점": r"되돌리(기|기가)\s*(어렵|힘)|불가역|되돌릴\s*수\s*없|이후에는\s*되돌",
    },
}

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


# 길이가 개념 적중을 끄는 관계는 남아 있다(EVALUATION.md H11). 그래서 주입을 받은 쪽이
# 얼마나 짧아졌는지를 게이트로 둔다. 개념 적중이 아직 안 갈려도 길이가 먼저 무너진다.
LENGTH_FLOOR = 0.85   # B 의 길이 중앙값이 A 의 이 비율 아래로 내려가면 경고한다


def run_group(label, table):
    if not any(OUT.glob(f"{pid}_A_*.json") for pid in table):
        return None
    tot = {"A": [0, 0], "B": [0, 0]}
    lens = {"A": [], "B": []}
    missed = {"A": {}, "B": {}}
    print(f"\n■ {label}")
    print(f"\n  {'과제':<8} {'A 주입없음':<24} {'B 주입있음':<24}")
    print("  " + "-" * 62)
    for pid in sorted(table):
        cells = []
        for c in "AB":
            per = []
            for f in sorted(OUT.glob(f"{pid}_{c}_*.json")):
                text = json.loads(f.read_text(encoding="utf-8")).get("result") or ""
                lens[c].append(len(text))
                hit = 0
                for name, rx in table[pid].items():
                    if re.search(rx, text, re.I):
                        hit += 1
                    else:
                        key = f"{pid} {name}"
                        missed[c][key] = missed[c].get(key, 0) + 1
                per.append((hit, len(table[pid])))
            tot[c][0] += sum(h for h, _ in per)
            tot[c][1] += sum(t for _, t in per)
            cells.append(f"{sum(h for h,_ in per)}/{sum(t for _,t in per)} n={len(per)}")
        print(f"  {pid:<8} {cells[0]:<24} {cells[1]:<24}")
    print("  " + "-" * 62)
    a, b = tot["A"], tot["B"]
    lo, hi = diff_ci(a[0], a[1], b[0], b[1])
    verdict = "차이 없음" if lo <= 0 <= hi else ("저하" if hi < 0 else "개선")
    print(f"  개념 적중  A {a[0]}/{a[1]} ({a[0]/a[1]*100:.0f}%)   B {b[0]}/{b[1]} ({b[0]/b[1]*100:.0f}%)"
          f"   차이 95% CI [{lo*100:+.1f}, {hi*100:+.1f}]%p → {verdict}")
    ma, mb = statistics.median(lens["A"]), statistics.median(lens["B"])
    ratio = mb / ma if ma else 1.0
    mark = "OK" if ratio >= LENGTH_FLOOR else f"경고 (하한 {LENGTH_FLOOR:.0%})"
    print(f"  길이 중앙값  A {ma:.0f}자   B {mb:.0f}자   비율 {ratio*100:.0f}%  → {mark}")
    gaps = [k for k in set(missed["A"]) | set(missed["B"])
            if missed["B"].get(k, 0) - missed["A"].get(k, 0) >= 2]
    if gaps:
        print("  B 가 더 많이 놓친 개념")
        for k in sorted(gaps, key=lambda k: missed["A"].get(k, 0) - missed["B"].get(k, 0)):
            print(f"    {k:<28} A {missed['A'].get(k,0)}  B {missed['B'].get(k,0)}")
    return ratio, (lo, hi)


print("=" * 78)
print(f"설계 능력 — {MODEL}. 빠지면 설계가 틀리는 개념이 실제로 나왔는지 센다")
print("A 주입 없음 / B 주입 있음. 문체와 서식은 채점하지 않는다")
print("=" * 78)

results = []
for label, table in (("짧은 설계 (개념 8개)", CONCEPTS), ("장문 설계 (개념 16개)", LONG_CONCEPTS)):
    r = run_group(label, table)
    if r:
        results.append((label, r))

bad = [lbl for lbl, (ratio, _) in results if ratio < LENGTH_FLOOR]
print()
if bad:
    print(f"길이 게이트 실패: {', '.join(bad)}")
    print("  주입을 받은 답이 지나치게 짧다. 개념 적중이 아직 안 갈렸어도 그 앞단이 무너진 것이다.")
    print("  plugin/hooks-handlers/always-on.md 의 서식·분량 관련 줄을 먼저 본다. EVALUATION.md H11.")
    sys.exit(1)
print("길이 게이트 통과. 주입을 받은 답이 짧아지지 않았다.")
