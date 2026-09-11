# CLAUDE.md

이 저장소에서 작업하는 Claude Code 를 위한 규칙입니다. 사람이 읽어도 됩니다.

## 이 저장소가 무엇인가

Claude Code 가 쓰는 한국어 글의 품질과 자연스러움을 맡는 플러그인입니다. 이 저장소가 쓴 스킬 셋, im-not-ai 에서 내장한 윤문 스킬 셋과 에이전트 셋, 훅 둘(모델이 korean-writing 스킬을 부르기 전 확인, 편집 뒤 검사), 슬래시 명령 하나, 검사·릴리스 스크립트로 이루어집니다. 구조와 사용법은 [README.md](README.md), 판정 기준은 [EVALUATION.md](EVALUATION.md) 에 있습니다.

## 저장소는 두 층이다

`plugin/` 만 설치한 사람의 기계로 갑니다. 나머지는 여기 남습니다.

```
plugin/     설치본. 매니페스트·훅·스킬·에이전트·명령·런타임 스크립트·LICENSE·NOTICE
tests/      회귀 테스트와 정답 데이터
tools/      관리자 스크립트(release·measure·install-git-hook)
docs/        실험과 그림
.github/    CI·이슈 양식·CI 전용 npm 도구
루트 문서    README·CHANGELOG·EVALUATION·CONTRIBUTING·SECURITY·SUPPORT·CODE_OF_CONDUCT
```

**플러그인 설치는 `source` 가 가리키는 폴더를 통째로 복사하고 무엇을 빼는 수단이 없습니다.**
`.claude-plugin/marketplace.json` 의 `source` 가 `./plugin` 인 이유가 이것입니다. 테스트·실험·CI·저장소
문서를 `plugin/` 안에 두면 설치한 사람이 그것까지 내려받습니다. 나눠 두기 전에는 219개 파일 1.8MB 가
갔고 지금은 53개 590KB 가 갑니다.

새 파일을 어디에 둘지는 한 가지만 물으면 됩니다. **설치한 사람이 이것을 쓰는가.** 아니면 `plugin/` 밖입니다.
CI 의 `설치본 경계` 작업이 테스트·실험 산출물·CI 설정·관리자 스크립트·저장소 문서·잠금 파일이
`plugin/` 에 들어오는 것을 막고, `LICENSE`·`NOTICE.md`·매니페스트가 빠지는 것도 막습니다.

**설치는 작업 트리를 그대로 복사합니다. git 이 무시하는 파일도 따라갑니다.** 로컬에서 설치해 보기 전에
`find plugin -name __pycache__ -type d -exec rm -rf {} +` 로 치웁니다. 실측에서 `py_compile` 을 돌린 뒤
설치하니 `.pyc` 11개가 같이 갔습니다. CI 의 같은 작업이 `??` 와 `!!` 상태 파일을 막습니다.

경로를 옮길 때 같이 봐야 하는 곳은 `.gitattributes`(linguist), `.github/CODEOWNERS`,
`.github/workflows/*.yml`, `.claude/settings.json` 의 권한 목록, `tools/*.sh` 입니다.

설치본이 제대로 도는지는 격리된 HOME 에 실제로 깔아 봅니다.

```bash
HOME=/tmp/kw-home claude plugin marketplace add "$PWD"
HOME=/tmp/kw-home claude plugin install korean-writing@claude-korean-writing
find /tmp/kw-home/.claude/plugins/cache -type f | wc -l    # 설치본 파일 수
```

## 먼저 돌린다

작업을 시작하면 기준선부터 잡습니다. 무엇이 원래 깨져 있었는지 모르면 내가 깬 것과 구분할 수 없습니다.

```bash
python3 tests/test_posttooluse.py     # 검사 훅 회귀 테스트
python3 tests/test_pretooluse.py      # 스킬 확인 훅 회귀 테스트
plugin/scripts/check.sh --all         # 저장소가 쓴 .md 가 자기 훅을 통과하는가
```

## 지켜야 하는 것

**네트워크를 쓰지 않습니다.** 훅도 스킬도 스크립트도 원문을 외부로 보내지 않습니다. README 가 이것을 약속하고 있으므로, 네트워크 호출을 넣는 변경은 그 약속을 깨뜨립니다. 필요하다고 판단되면 코드를 넣기 전에 이슈로 먼저 논의합니다.

**훅은 편집을 되돌리지 않습니다.** 걸린 항목을 stderr 로 알리고 종료 코드 2 로 끝냅니다. 사람이 쓰던 작업을 막는 설계가 아닙니다.

**평소 답변과 서브에이전트에는 규칙을 주입하지 않습니다.** 2026-09-11 에 두 주입을 뺐습니다. 문체 규칙을 주입하면 답변에서 기본값 같은 세부가 빠졌습니다. 규칙을 어휘 수준으로 줄이고 세부를 빼지 말라고 적어도 막지 못했고, 같은 길이의 중립 문장을 넣었을 때는 빠지지 않았습니다(EVALUATION.md H13). 주입을 되살리려면 그 측정을 다시 통과해야 합니다.

**모델이 korean-writing 스킬을 스스로 부르기 전에 사용자에게 묻습니다.** `plugin/hooks-handlers/pretooluse-skill.sh` 가 이 스킬의 Skill 호출에 `permissionDecision: "ask"` 를 돌려줍니다. 스킬도 같은 문체 규칙집을 쓰고 세부를 빼는지는 아직 재지 않았기 때문입니다(EVALUATION.md J1). 이 확인을 없애려면 H13 과 같은 세부 보존 측정을 스킬에 먼저 돌립니다. 이 훅도 무엇을 막지 않고 입력을 못 읽으면 exit 0 으로 지나갑니다.

**한국어 문서를 고쳤으면 `plugin/scripts/check.sh` 를 통과시킵니다.** CI 가 같은 검사를 돌리므로 여기서 걸리면 거기서도 걸립니다. 나쁜 예를 일부러 싣는 문서라면 파일 머리에 `<!-- korean-writing: ignore -->` 를 넣습니다.

**한국어 글 작성 요청에는 이 저장소의 규칙을 씁니다.** 커밋 메시지, README, 이슈 답변, 작업 메모처럼 남에게 보내든 안에 남기든 모두 해당합니다. 규칙은 [plugin/SKILL.md](plugin/SKILL.md) 에 있습니다. 자기 규칙을 어기는 저장소는 설득력이 없습니다.

## 건드리지 않는 것

`plugin/skills/humanize-korean/**`, `plugin/skills/humanize/**`, `plugin/skills/humanize-redo/**`, `plugin/agents/**`, `plugin/scripts/*.py`, `plugin/skills/crafting-effective-readmes/**`, `plugin/skills/korean-character-count/scripts/**` 는 다른 MIT 프로젝트에서 가져온 파일입니다. 출처와 수정 범위가 [plugin/NOTICE.md](plugin/NOTICE.md) 에 적혀 있습니다. 고쳐야 하면 그 파일의 해당 줄도 함께 고칩니다.

윤문 파이프라인은 im-not-ai 의 런타임 부분집합을 그대로 내장한 것입니다. 새 판을 받으려면 원본 저장소를 그 커밋으로 받아 같은 경로에 복사하고 plugin/NOTICE.md 에 적힌 한 줄 수정(트리거 문구)을 다시 적용한 뒤, `python3 -m py_compile plugin/scripts/*.py` 와 격리된 HOME 에서 `/korean-writing:humanize` 실행으로 확인하고 plugin/NOTICE.md 의 커밋을 올립니다. 스크립트는 `plugin/scripts/` 와 `plugin/skills/humanize-korean/references/` 의 상대 위치로 서로를 찾으므로 둘의 관계를 바꾸지 않습니다.

## 버전

정본은 `plugin/.claude-plugin/plugin.json` 한 곳입니다. README 배지와 마켓플레이스 매니페스트는 `tools/release.sh` 가 맞춰 줍니다. 손으로 따로 고치지 않습니다. CI 의 `버전 표기 일치` 작업이 어긋남을 잡습니다.

## 커밋

Conventional Commits 를 쓰고 제목은 한국어로 씁니다.

```
feat: 줄표는 이번 편집에 하나라도 있으면 파일 전체 개수로 판정
fix: 릴리스 태그 메시지에서 ### 헤딩이 주석으로 잘리던 문제
docs: 스킬 유무 비교 기록
```

훅 판정을 바꾸는 변경이면 `tests/test_posttooluse.py` 에 회귀 테스트를 함께 넣습니다. 테스트가 실패하면 테스트가 아니라 코드를 고칩니다.

## 판정 기준을 바꿀 때

패턴 하나를 넣거나 빼는 결정은 실측으로 합니다. 근거 없이 임계를 조정하지 않습니다. `tools/measure.sh` 로 실제 문서 뭉치의 오탐을 재고 결과를 EVALUATION.md 에 남깁니다. 실제로 K7 의 "죽다" 와 K8 의 `~에 대해` 는 그렇게 재고 뺐습니다.

**정규식으로 센 표지 개수는 품질의 근거가 아닙니다.** 표지를 표본당 1.95 에서 0.25 로 줄인 판이 블라인드 쌍대 판정에서는 옛 판을 이기지 못한 적이 있습니다. 규칙을 지키느라 문장을 짧게 끊어 리듬이 죽은 것이고, 길이 균일성은 규칙집의 E-1 항목입니다. `plugin/SKILL.md` 를 고쳤으면 릴리스 전에 블라인드 판정을 돌립니다.

```bash
docs/experiments/skill-vs-imnotai/run.sh                      # 스킬을 고쳤을 때
docs/experiments/detail-retention/run.sh                      # 검사 훅의 안내를 고쳤을 때
```

**검사 훅의 안내 문구도 규칙집 처방을 따릅니다.** 모델은 훅이 알린 대로 고칩니다. 안내를 한 줄로 줄이다 보존 조건을 떨어뜨리면 고치는 동안 정보가 지워집니다. 실제로 `A가 아니라 B다 → B다` 라는 안내가 부정한 쪽의 정보를 지우게 했습니다(EVALUATION.md I1). 안내를 바꾸면 [rewriting-playbook.md](plugin/skills/humanize-korean/references/rewriting-playbook.md) 의 해당 처방과 대조하고 고친 전후를 잽니다.

둘 다 LLM 을 부르므로 CI 에 넣지 않습니다. 스킬 쪽은 im-not-ai 로 사후 윤문한 글과 붙여 이 플러그인의 목표를 그대로 잽니다. 계정 사용량이 떨어지면 판정 출력 자리에 안내 문구가 들어오므로 실패 건수를 먼저 봅니다.
