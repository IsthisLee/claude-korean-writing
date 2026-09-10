# CLAUDE.md

이 저장소에서 작업하는 Claude Code 를 위한 규칙입니다. 사람이 읽어도 됩니다.

## 이 저장소가 무엇인가

Claude Code 가 쓰는 모든 한국어의 품질과 자연스러움을 맡는 플러그인입니다. 이 저장소가 쓴 스킬 셋, im-not-ai 에서 내장한 윤문 스킬 셋과 에이전트 셋, 훅 둘(세션 시작의 상시 규칙 주입, 편집 뒤 검사), 검사·릴리스 스크립트로 이루어집니다. 구조와 사용법은 [README.md](README.md), 판정 기준은 [EVALUATION.md](EVALUATION.md) 에 있습니다.

## 먼저 돌린다

작업을 시작하면 기준선부터 잡습니다. 무엇이 원래 깨져 있었는지 모르면 내가 깬 것과 구분할 수 없습니다.

```bash
python3 hooks-handlers/test_posttooluse.py     # 검사 훅 회귀 테스트
python3 hooks-handlers/test_sessionstart.py    # 상시 규칙 주입 회귀 테스트
scripts/check.sh README.md CLAUDE.md           # 문서가 자기 훅을 통과하는가
```

## 지켜야 하는 것

**네트워크를 쓰지 않습니다.** 훅도 스킬도 스크립트도 원문을 밖으로 보내지 않습니다. README 가 이것을 약속하고 있으므로, 네트워크 호출을 넣는 변경은 그 약속을 깨뜨립니다. 필요하다고 판단되면 코드를 넣기 전에 이슈로 먼저 논의합니다.

**훅은 편집을 되돌리지 않습니다.** 걸린 항목을 stderr 로 알리고 종료 코드 2 로 끝냅니다. 사람이 쓰던 작업을 막는 설계가 아닙니다.

**상시 규칙 주입은 무엇도 막지 않습니다.** `hooks-handlers/sessionstart.sh` 는 어떤 경우에도 종료 코드 0 으로 끝납니다. 규칙 파일이 없거나 읽히지 않아도 마찬가지입니다. 주입문을 늘리면 상시 비용이 커지므로 EVALUATION.md 의 D2 예산을 먼저 보고 늘렸으면 `usage` 로 실측해 그 값을 남깁니다.

**한국어 문서를 고쳤으면 `scripts/check.sh` 를 통과시킵니다.** CI 가 같은 검사를 돌리므로 여기서 걸리면 거기서도 걸립니다. 나쁜 예를 일부러 싣는 문서라면 파일 머리에 `<!-- korean-writing: ignore -->` 를 넣습니다.

**한국어 글 작성 요청에는 이 저장소의 규칙을 씁니다.** 커밋 메시지, README, 이슈 답변, 작업 메모처럼 남에게 보내든 안에 남기든 모두 해당합니다. 규칙은 [SKILL.md](SKILL.md) 에 있습니다. 자기 규칙을 어기는 저장소는 설득력이 없습니다.

**서브에이전트도 같은 규칙을 씁니다.** 이 저장소의 훅과 스킬은 서브에이전트에 전달되지 않습니다(실측: 세션 시작 훅은 서브에이전트를 위해 돌지 않고 서브에이전트 시작 훅은 돌지만 출력이 안 가고 스킬 목록도 안 감). 전달되는 것은 이 파일뿐이므로 여기 적습니다. 한국어로 답하거나 한국어 글을 쓸 때 `A가 아니라 B` 대구 연쇄, 연결어미 뒤 쉼표(`~하고,`), 사물 의인화, 영어 직역 비유, 축·갈래·결·레이어, 줄표 삽입구, 첫째·둘째 병렬, 번역투, AI 관용구를 쓰지 않습니다. 앞의 둘이 실측에서 사람 글과 가장 크게 갈린 항목입니다. 요청받은 글만 내고 분량 보고나 후속 제안을 붙이지 않습니다. 자세한 규칙은 [SKILL.md](SKILL.md) 에 있습니다.

## 건드리지 않는 것

`skills/humanize-korean/**`, `skills/humanize/**`, `skills/humanize-redo/**`, `agents/**`, `scripts/*.py`, `skills/crafting-effective-readmes/**`, `skills/korean-character-count/scripts/**` 는 다른 MIT 프로젝트에서 가져온 파일입니다. 출처와 수정 범위가 [NOTICE.md](NOTICE.md) 에 적혀 있습니다. 고쳐야 하면 NOTICE.md 의 해당 줄도 함께 고칩니다.

윤문 파이프라인은 im-not-ai 의 런타임 부분집합을 그대로 내장한 것입니다. 새 판을 받으려면 원본 저장소를 그 커밋으로 받아 같은 경로에 복사하고 NOTICE.md 에 적힌 한 줄 수정(트리거 문구)을 다시 적용한 뒤, `python3 -m py_compile scripts/*.py` 와 격리된 HOME 에서 `/korean-writing:humanize` 실행으로 확인하고 NOTICE.md 의 커밋을 올립니다. 스크립트는 `scripts/` 와 `skills/humanize-korean/references/` 의 상대 위치로 서로를 찾으므로 경로를 옮기지 않습니다.

## 버전

정본은 `.claude-plugin/plugin.json` 한 곳입니다. README 배지와 CHANGELOG 는 `scripts/release.sh` 가 맞춰 줍니다. 손으로 따로 고치지 않습니다. CI 의 `버전 표기 일치` 작업이 어긋남을 잡습니다.

## 커밋

Conventional Commits 를 쓰고 제목은 한국어로 씁니다.

```
feat: 줄표는 이번 편집에 하나라도 있으면 파일 전체 개수로 판정
fix: 릴리스 태그 메시지에서 ### 헤딩이 주석으로 잘리던 문제
docs: 스킬 유무 비교 기록
```

훅 판정을 바꾸는 변경이면 `hooks-handlers/test_posttooluse.py` 에 회귀 테스트를 함께 넣습니다. 테스트가 실패하면 테스트가 아니라 코드를 고칩니다.

## 판정 기준을 바꿀 때

패턴 하나를 넣거나 빼는 결정은 실측으로 합니다. 근거 없이 임계를 조정하지 않습니다. `scripts/measure.sh` 로 실제 문서 뭉치의 오탐을 재고 결과를 EVALUATION.md 에 남깁니다. 실제로 K7 의 "죽다" 와 K8 의 `~에 대해` 는 그렇게 재고 뺐습니다.

**정규식으로 센 표지 개수는 품질의 근거가 아닙니다.** 표지를 표본당 1.95 에서 0.25 로 줄인 판이 블라인드 쌍대 판정에서는 옛 판을 이기지 못한 적이 있습니다. 규칙을 지키느라 문장을 짧게 끊어 리듬이 죽은 것이고, 길이 균일성은 규칙집의 E-1 항목입니다. `SKILL.md` 나 `hooks-handlers/always-on.md` 를 고쳤으면 릴리스 전에 블라인드 판정을 돌립니다.

```bash
docs/experiments/always-on/regress.sh 옛규칙.md 새규칙.md      # 상시 규칙을 고쳤을 때
docs/experiments/skill-vs-imnotai/run.sh                      # 스킬을 고쳤을 때
```

둘 다 LLM 을 부르므로 CI 에 넣지 않습니다. 스킬 쪽은 im-not-ai 로 사후 윤문한 글과 붙여 이 플러그인의 목표를 그대로 잽니다. 계정 사용량이 떨어지면 판정 출력 자리에 안내 문구가 들어오므로 실패 건수를 먼저 봅니다.
