<!-- korean-writing: ignore -->

# 상시 규칙 실험 장비

`hooks-handlers/always-on.md` 를 세션마다 주입하는 것이 평소 답변의 한국어를 낫게 하는지 잰 장비입니다. 결과는 [`EVALUATION.md`](../../../EVALUATION.md) 의 C5 에 있고, 실행 기록과 판정 기준은 이 디렉터리의 `CRITERIA.md` 와 `REPORT.md` 에 있습니다.

규칙을 고칠 때 다시 돌리라고 남겨 둔 것입니다. 처음부터 만들면 아래 함정을 다시 밟습니다.

## 먼저 읽을 것

`claude -p` 를 반복 호출하는 실험에는 함정이 둘 있습니다. 둘 다 실제로 밟았습니다.

**커넥터 도구 정의.** `--strict-mcp-config` 를 붙이지 않으면 claude.ai 커넥터의 도구 정의가 프롬프트에 실립니다. 호출당 입력이 22만에서 30만 토큰이 되고 캐시도 안 맞습니다. 네 번 돌리는 데 21달러가 나갔습니다. 붙이면 호출당 1만 토큰입니다.

**사용자 전역 훅.** 도구를 끈 헤드리스 세션에서 `no-guess-gate` 의 Stop 훅이 턴 종료를 막습니다. 도구를 한 번도 안 쓴 턴에 "확인이 필요", "것 같다", 파일명 같은 표현이 있으면 실측을 요구하는데, 도구가 없으니 모델이 가짜 도구 호출을 텍스트로 씁니다. 1차 실행에서 48건 중 24건이 그렇게 망가졌습니다. `--setting-sources ""` 로 사용자 설정을 빼면 사라지고, 전역 지침이 필요하면 `--append-system-prompt` 로 되살립니다.

그래서 공통 플래그가 이렇습니다.

```bash
--strict-mcp-config --setting-sources "" \
  --model claude-fable-5-1 --effort xhigh --tools "" \
  --append-system-prompt "$(cat ~/.claude/CLAUDE.md)"
```

## 파일

| 파일               | 무엇                                                                     |
| ------------------ | ------------------------------------------------------------------------ |
| `CRITERIA.md`      | 실행 전에 고정한 판정 기준과 도중에 고친 기록                            |
| `REPORT.md`        | 결과 보고. 측정값, 무효 처리한 실행, 비용, 한계                          |
| `prompts/`         | 프롬프트 12개. 스킬이 뜨지 않는 평소 답변만 고름                         |
| `inject.v1~v4.md`  | 주입문 초안. `inject.md` 가 채택본이고 저장소의 `always-on.md` 와 같음   |
| `gen_one.sh`       | 프롬프트 하나를 한 조건으로 생성                                         |
| `run_all.sh`       | 12 × 2조건 × 2표본 = 48건 생성                                           |
| `judge_one.sh`     | 한 쌍을 블라인드로 판정. 순서를 바꿔 두 번 돌림                          |
| `judge_all.sh`     | 24쌍 × 2순서 = 48회 판정                                                 |
| `aggregate.py`     | 판정 집계. 순서가 엇갈리면 무승부                                        |
| `score.py`         | 훅 검사기와 원시 패턴 횟수 채점                                          |
| `register.py`      | 종결어미 분포. 높임이 기우는지 봄                                        |
| `validate.py`      | 생성물이 실제 답변인지 검사. 가짜 도구 호출과 빈 출력을 걸러냄           |
| `factcheck_one.sh` | 문체를 빼고 기술 오류만 보는 검사                                        |
| `settings-B.json`  | 주입 조건의 SessionStart 훅 설정                                         |

## 돌리는 순서

```bash
./run_all.sh                 # 생성 48건
python3 validate.py out      # 판정 전에 유효성부터. invalid 가 0 이어야 함
python3 score.py > scores.csv
./judge_all.sh               # 판정 48회
python3 aggregate.py
```

`validate.py` 를 건너뛰지 마세요. 1차 실행에서 무효 24건을 그대로 판정에 넣었다가 결과를 통째로 버렸습니다.

## 생성물 원본은 어디에

이 디렉터리에는 스크립트와 프롬프트와 보고서만 둡니다. 생성물과 판정 원본 2MB 는 저장소 밖 `korean-writing-experiments/2026-09-10/` 에 있습니다. 재현에 필요한 것은 여기 있는 것이고, 원본은 다시 돌리면 새로 만들어집니다.

## 비용

2026-09-10 실행 전체가 약 75달러입니다. 그중 21달러는 `--strict-mcp-config` 를 빠뜨려 낭비한 값입니다. 제대로 붙이면 생성 48건에 9.5달러, 판정 48회에 10.8달러, 사실 검사 48건에 11.4달러입니다.
