# 고치면서 세부가 빠지는가

이 폴더는 세 가지를 잽니다. 결과와 판단은 [EVALUATION.md](../../../EVALUATION.md) 에 있습니다.

| 측정 | 묻는 것 | 절 |
| --- | --- | --- |
| 검사 훅 안내 | 훅 알림을 받고 고친 글에서 원문의 정보가 사라지는가 | I1 |
| 규칙 주입 | 규칙을 주입한 답변에서 세부가 빠지는가 | H13 |
| 스킬 | 스킬로 쓴 글에서 적어 준 사실과 덧붙이는 설명이 빠지는가 | J3 |

## 검사 훅 안내 (I1)

```bash
docs/experiments/detail-retention/run.sh                        # 저장소의 훅
docs/experiments/detail-retention/run.sh /경로/고친-훅.sh 3      # 안내를 고친 사본
```

`drafts/control.txt` 는 K1·K4·K5·K9·K10 이 한꺼번에 걸리도록 쓴 배포 공지입니다. 날짜와 개수, 담당자, 예외, 시각 같은 세부가 문장마다 들어 있습니다. 모델에게 이 초안을 `doc.md` 로 저장하게 하고 PostToolUse 검사 훅만 켭니다. 훅이 걸리면 모델이 알림을 받고 고칩니다. `analyze.py` 가 처음 저장한 글과 고친 글을 조건을 모르는 판정자에게 주고 사라진 정보와 약해진 뉘앙스, 새로 생긴 정보를 따로 세게 합니다. 사라진 정보가 하나라도 있으면 종료 코드 1 입니다.

초안을 `.txt` 로 둔 이유는 저장소의 자기 검사가 `.md` 만 보기 때문입니다. 일부러 AI 티를 넣은 글이라 `.md` 로 두면 걸립니다. 제외 표시를 넣으면 모델이 그 표시까지 저장해 훅이 돌지 않습니다.

2026-09-11 결과입니다.

| 초안 | 옛 안내 | 새 안내 |
| --- | --- | --- |
| 대조군 6건 (Sonnet 5·Opus 5 셋씩) | 9건 사라짐 | 0건 |
| 훅에 걸린 실제 초안 15건 | 4건 사라짐 | 0건 |

실제 초안 15건은 `docs/experiments/skill-vs-imnotai/prompts/` 의 글 작성 프롬프트 14개를 Sonnet 5 와 Haiku 4.5 에 두 번씩 쓰게 해서 훅에 걸린 것입니다. 원문은 커밋하지 않았습니다.

## 규칙 주입 (H13)

주입 기능은 이 결과로 뺐습니다. 다시 넣으려는 판이 있으면 여기서 먼저 잽니다.

```bash
cd docs/experiments/detail-retention/injection
for s in 1 2 3 4 5 6 7 8; do ./gen_rule.sh A rules/none.md "$s"; ./gen_rule.sh B 새규칙.md "$s"; done
python3 judge.py
```

`gen_rule.sh` 는 규칙 파일을 SessionStart 훅으로 주입하고 디바운스 훅을 설명해 달라는 질문(`docs/experiments/always-on/prompts/01.txt`)을 claude-sonnet-5 에 묻습니다. `judge.py` 는 답마다 세부 11항목이 설명됐는지 조건을 모르는 판정자에게 묻고 조건별로 모읍니다. 조건 `A` 가 있으면 다른 조건을 그것과 견줘 순열검정과 기본값 항목의 Fisher 검정을 냅니다.

| 규칙 파일 | 조건 |
| --- | --- |
| `rules/none.md` | 주입 없음 |
| `rules/always-on-removed.md` | 뺀 규칙 그대로 |
| `rules/slim.md` | 어휘 규칙만 남기고 세부를 빼지 말라고 적은 판 |
| `rules/neutral.md` | 문체와 관계없는 같은 길이의 메모 |

2026-09-11 결과는 주입 없음 72/88, 뺀 규칙 64/88, 줄인 판 62/88, 중립 메모 67/88 이었습니다. `delay` 기본값 300ms 가 나온 답은 차례로 5/8, 0/8, 0/8, 4/8 입니다.

## 스킬 (J3)

```bash
cd docs/experiments/detail-retention/skill
python3 make_neutral.py
for t in notice incident debounce; do for c in A S; do for s in 1 2 3 4 5 6 7 8; do ./gen.sh "$t" "$c" "$s"; done; done; done
for s in 1 2 3 4 5 6 7 8; do ./gen.sh debounce N "$s"; done
python3 judge.py
```

`gen.sh` 는 `plugin/SKILL.md` 를 시스템 프롬프트에 붙인 조건(S), 붙이지 않은 조건(A), 같은 글자 수의 무관한 문서를 붙인 대조군(N)으로 과제에 답하게 합니다. 과제는 사실을 준 슬랙 공지와 장애 보고서, 사실을 주지 않은 설명 문서 셋이고 항목표는 `items.json` 입니다. `judge.py` 가 조건을 모르는 판정자에게 항목마다 묻고 측정 전에 정한 기준으로 과제별 판정을 냅니다. 합계 순열검정 p<0.05 로 S 가 낮거나 항목 하나라도 Fisher p<0.05 로 S 에서 줄면 「빠진다」 입니다.

2026-09-11 결과는 공지 96/96 대 96/96, 보고서 120/120 대 120/120, 설명 문서 72/88 대 63/88 이었습니다. 설명 문서는 한글 661자에서 450자로 짧아졌고 `delay` 가 바뀌어도 타이머를 새로 건다는 설명이 8/8 에서 3/8 로 줄었습니다. 대조군 N 은 70/88, 같은 항목 6/8 로 A 와 갈리지 않았습니다. 확인 창의 주의 문구가 이 결과를 따릅니다.

## 먼저 읽을 것

- **stream-json 에는 훅 알림이 남지 않습니다.** 훅이 걸렸는지는 첫 Write 의 내용에 훅을 다시 돌려 봅니다. `analyze.py` 가 그렇게 합니다.
- **판정 캐시는 실행 폴더마다 따로 둡니다.** 이름만으로 두었더니 같은 이름의 다른 모델 표본이 앞 판정을 받아 온 적이 있습니다.
- **세부를 정규식으로 세지 않습니다.** 처음에 그렇게 했다가 「중간 글자들」 같은 표현을 놓쳐 8점짜리 답을 5점으로 셌습니다.
- `claude -p` 에는 `--strict-mcp-config` 와 `--setting-sources ""` 를 붙이고 빈 임시 폴더에서 돌립니다. 빼면 MCP 도구 정의와 사용자 훅이 섞여 조건을 가를 수 없습니다.
- 산출물은 `out/` 과 `judge/` 에 쌓이고 커밋하지 않습니다.
