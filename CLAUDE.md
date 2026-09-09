# CLAUDE.md

이 저장소에서 작업하는 Claude Code 를 위한 규칙입니다. 사람이 읽어도 됩니다.

## 이 저장소가 무엇인가

Claude Code 가 쓰는 한국어의 품질과 자연스러움을 맡는 플러그인입니다. 스킬 넷과 PostToolUse 훅 하나, 검사·릴리스 스크립트로 이루어집니다. 구조와 사용법은 [README.md](README.md), 판정 기준은 [EVALUATION.md](EVALUATION.md) 에 있습니다.

## 먼저 돌린다

작업을 시작하면 기준선부터 잡습니다. 무엇이 원래 깨져 있었는지 모르면 내가 깬 것과 구분할 수 없습니다.

```bash
python3 hooks-handlers/test_posttooluse.py     # 훅 회귀 테스트
scripts/check.sh README.md CLAUDE.md           # 문서가 자기 훅을 통과하는가
```

## 지켜야 하는 것

**네트워크를 쓰지 않습니다.** 훅도 스킬도 스크립트도 원문을 밖으로 보내지 않습니다. README 가 이것을 약속하고 있으므로, 네트워크 호출을 넣는 변경은 그 약속을 깨뜨립니다. 필요하다고 판단되면 코드를 넣기 전에 이슈로 먼저 논의합니다.

**훅은 편집을 되돌리지 않습니다.** 걸린 항목을 stderr 로 알리고 종료 코드 2 로 끝냅니다. 사람이 쓰던 작업을 막는 설계가 아닙니다.

**한국어 문서를 고쳤으면 `scripts/check.sh` 를 통과시킵니다.** CI 가 같은 검사를 돌리므로 여기서 걸리면 거기서도 걸립니다. 나쁜 예를 일부러 싣는 문서라면 파일 머리에 `<!-- korean-writing: ignore -->` 를 넣습니다.

**밖으로 나갈 한국어를 쓸 때는 이 저장소의 규칙을 씁니다.** 커밋 메시지, README, 이슈 답변 모두 해당합니다. 규칙은 [SKILL.md](SKILL.md) 에 있습니다. 자기 규칙을 어기는 저장소는 설득력이 없습니다.

## 건드리지 않는 것

`references/taxonomy.md` 와 `references/quick-rules.md`, `skills/crafting-effective-readmes/**`, `skills/korean-character-count/scripts/**` 는 다른 MIT 프로젝트에서 가져온 파일입니다. 출처와 수정 범위가 [NOTICE.md](NOTICE.md) 에 적혀 있습니다. 고쳐야 하면 NOTICE.md 의 해당 줄도 함께 고칩니다.

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

패턴 하나를 넣거나 빼는 결정은 실측으로 합니다. 근거 없이 임계를 조정하지 않습니다. `scripts/measure.sh` 로 실제 문서 뭉치의 오탐을 재고, 결과를 EVALUATION.md 에 남깁니다. 실제로 K7 의 "죽다" 와 K8 의 `~에 대해` 는 그렇게 재고 뺐습니다.
