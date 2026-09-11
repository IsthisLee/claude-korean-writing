#!/usr/bin/env bash
# 세 가지를 한 번에 돌린다. 이미 있는 결과는 건너뛰므로 중간에 끊고 다시 돌려도 된다.
#
#   1. 정확도      답이 하나로 떨어지는 기술 문제 10개. 주입 유무로 정답률이 갈리는가
#   2. 지시 준수   규칙과 반대되는 것을 사용자가 명시로 요청했을 때 사용자를 따르는가
#   3. 코드 품질   모델이 쓴 함수를 실제로 돌려 경계 조건을 챙겼는지 본다
#   4. 설계 능력   빠지면 설계가 틀리는 개념이 실제로 나왔는지 센다
#                 짧은 과제(개념 8)와 장문 과제(개념 16)를 나눠 본다. 규칙이 분량을 누르면
#                 장문에서 먼저 드러난다. 길이 게이트가 여기 붙어 있다
#   5. 코드 리뷰   심어 둔 결함 다섯 개를 몇 개 찾는가
#   6. 정보 보존   요약이 원문의 사실 열둘을 얼마나 지키는가
#   7. 과잉 단정   정보가 없을 때 없다고 말하는가
#   8. 디버깅      원인이 되는 줄을 짚는가
#   9. 서브에이전트  주입이 서브에이전트의 조사 결과를 흐리는가
#  10. 스킬 오발동  코드 작업에서 글 작성 스킬이 잘못 뜨는가 (양성 대조 포함)
#
# LLM 을 부르므로 CI 에 넣지 않는다. 규칙 파일을 고쳤으면 릴리스 전에 돌린다.
# 결과는 out/ subout/ skillout/ 에 쌓이고 grade.py 가 읽는다.
set -uo pipefail
cd "$(dirname "$0")" || exit 1

HAIKU=claude-haiku-4-5-20251001
OPUS=claude-opus-5
T="T01 T02 T03 T04 T05 T06 T07 T08 T09 T10"
C="C1 C2 C3 C4 C5"
E="E1 E2 E3 E4 E5"
D="D1 D2 D3 D4 D5"
L="L1 L2 L3"          # 장문 설계. 빠짐없이 늘어놓아야 하는 과제
R="R1 R2 R3 R4"      # 코드 리뷰
N="N1 N2 N3"         # 정보 보존
G="G1 G2 G3 G4"      # 과잉 단정
B="B1 B2 B3 B4"      # 디버깅

jobs=()
# 작은 모델은 여유가 있어 저하가 드러난다. 큰 모델은 실제로 쓰는 조건이다.
for id in $T; do for c in A B; do for s in 1 2 3 4; do jobs+=("$id $c $s $HAIKU"); done; done; done
for id in $T; do for c in A B; do for s in 1 2 3;   do jobs+=("$id $c $s $OPUS");  done; done; done
for id in $C; do for c in A B; do for s in 1 2 3 4 5; do jobs+=("$id $c $s $OPUS"); done; done; done
# 코드는 두 모델에서, 설계는 큰 모델에서 본다. 설계는 표본 넷이라야 구간이 쓸 만해진다.
for id in $E; do for c in A B; do for s in 1 2 3 4; do jobs+=("$id $c $s $HAIKU"); done; done; done
for id in $E; do for c in A B; do for s in 1 2 3;   do jobs+=("$id $c $s $OPUS");  done; done; done
for id in $D; do for c in A B; do for s in 1 2 3 4 5 6 7 8; do jobs+=("$id $c $s $OPUS"); done; done; done
for id in $L; do for c in A B; do for s in 1 2 3 4 5 6 7 8; do jobs+=("$id $c $s $OPUS"); done; done; done
# 나머지 넷. 큰 모델은 대개 만점이라 작은 모델을 같이 본다. 리뷰는 표본을 여덟까지 늘려야 갈린다.
for id in $R $N $G $B; do for c in A B; do for s in 1 2 3; do jobs+=("$id $c $s $OPUS"); done; done; done
for id in $N $G $B;     do for c in A B; do for s in 1 2 3; do jobs+=("$id $c $s $HAIKU"); done; done; done
for id in $R;           do for c in A B; do for s in 1 2 3 4 5 6 7 8; do jobs+=("$id $c $s $HAIKU"); done; done; done
echo "정확도·지시 준수·코드·설계·리뷰·보존·단정·디버깅 ${#jobs[@]}건"
printf '%s\n' "${jobs[@]}" | xargs -P 8 -L 1 ./run_one.sh

subs=()
for id in S1 S2; do for c in A B; do for s in 1 2 3; do subs+=("$id $c $s"); done; done; done
echo "서브에이전트 ${#subs[@]}건"
printf '%s\n' "${subs[@]}" | xargs -P 4 -L 1 ./run_sub.sh

sk=()
for id in K1 K2 K3 K4; do for c in A B; do for s in 1 2; do sk+=("$id $c $s"); done; done; done
sk+=("POS B 1")
echo "스킬 오발동 ${#sk[@]}건"
printf '%s\n' "${sk[@]}" | xargs -P 4 -L 1 ./run_skill.sh

./grade.py
./grade_code.py "$OPUS"
./grade_code.py "$HAIKU"
./grade_more.py "$OPUS"
./grade_more.py "$HAIKU"

# 설계는 마지막에 둔다. 길이 게이트가 실패하면 이 스크립트도 실패한다.
# 개념 적중이 아직 안 갈렸어도 길이가 먼저 무너지므로 그 앞단에서 잡는다.
./grade_design.py "$OPUS"
