# 기여 안내

<p><strong>한국어</strong> · <a href="CONTRIBUTING.en.md">English</a></p>

기여를 환영합니다. 이 문서는 무엇을 보내면 좋은지, 보낸 것이 어떤 기준으로 받아들여지는지 적습니다.

## 가장 필요한 것은 실제 문장입니다

이 저장소의 판정 기준은 합성 예문이 아니라 **Claude Code 가 실제로 생성했던 문장**으로 만듭니다. 지어낸 나쁜 예는 만들기 쉽지만, 그것으로 임계를 정하면 현실에서 안 나오는 표현을 잡고 정작 나오는 표현을 놓칩니다.

그래서 가장 값진 기여는 코드가 아니라 문장입니다.

- Claude 가 쓴 어색한 한국어를 봤다면 [어색한 문장 제보](https://github.com/IsthisLee/claude-korean-writing/issues/new?template=awkward-sentence.yml) 로 보내 주세요. 고치지 않은 원문 그대로가 필요합니다.
- 훅이 멀쩡한 문장을 잡았다면 그것도 같은 양식으로 보내 주세요. 오탐은 미탐보다 심각합니다. 사람이 검사기를 꺼버리게 만들기 때문입니다.

제보한 문장은 `hooks-handlers/ground-truth.json` 이나 `clean.json` 에 들어가 회귀 테스트가 됩니다.

## 시작하기

빌드가 없습니다. 받아서 바로 돌리면 됩니다.

```bash
git clone https://github.com/IsthisLee/claude-korean-writing
cd claude-korean-writing

python3 hooks-handlers/test_posttooluse.py    # 훅 회귀 테스트
scripts/check.sh README.md CONTRIBUTING.md    # 문서가 자기 훅을 통과하는가
```

| 필요한 것 | 쓰는 곳                         | 없으면                              |
| --------- | ------------------------------- | ----------------------------------- |
| `bash`    | 훅과 스크립트                   | 훅이 안 돕니다                      |
| `python3` | 훅의 판정 부분, 테스트          | 훅이 검사 없이 통과합니다           |
| `node`    | 글자 수 스크립트                | 그 스킬만 못 씁니다                 |

macOS 와 Linux 에서 CI 가 돌고 있습니다. Windows 는 Git Bash 나 WSL 이 필요합니다.

## 판정 규칙을 바꾸려면 실측이 있어야 합니다

`hooks-handlers/posttooluse.sh` 의 K1~K8 을 넣거나 빼거나 임계를 조정하는 변경은 **숫자를 함께 보내 주세요.** 느낌으로 조정하면 오탐이 조용히 늘어납니다.

```bash
scripts/measure.sh ~/내문서폴더 ~/다른폴더
```

한국어 `.md` 를 모아 둔 폴더에 돌리면 몇 개 파일이 걸리는지, 어떤 코드로 걸리는지 나옵니다. 걸린 파일이 사람이 쓴 글이면 오탐이고, Claude 가 쓴 글이면 맞게 잡은 것입니다. 그 구분은 사람이 합니다.

PR 에 이렇게 적어 주시면 충분합니다.

```
대상 문서 143개 / 변경 전 걸림 12개 / 변경 후 걸림 4개
줄어든 8개는 전부 2022~23년에 사람이 쓴 글이었습니다
```

실제로 K7 에서 "죽다" 를 뺀 것과 K8 에서 `~에 대해` 횟수를 안 세기로 한 것이 이 절차로 결정됐습니다. 판별력이 없는 규칙은 사람의 글만 잡습니다. 배경은 [EVALUATION.md](EVALUATION.md) 에 있습니다.

**판정을 바꿨으면 회귀 테스트도 함께 넣어 주세요.** `hooks-handlers/test_posttooluse.py` 에 통과해야 할 문장과 걸려야 할 문장을 추가합니다. 기존 테스트가 실패하면 테스트가 아니라 코드를 고칩니다. 요구가 바뀌어 테스트가 틀린 경우라면 무엇이 바뀌었는지 PR 에 한 줄 적어 주세요.

## 문서를 고치려면

한국어 문서는 이 저장소의 규칙을 지켜야 합니다. 자기 규칙을 어기는 저장소는 설득력이 없습니다.

```bash
scripts/check.sh 고친파일.md
```

나쁜 예를 일부러 싣는 문서라면 파일 머리에 `<!-- korean-writing: ignore -->` 를 넣습니다.

README 를 고칠 때는 한국어판과 영어판을 같이 고쳐 주세요. 한쪽만 바뀌면 다음 사람이 어느 쪽을 믿어야 할지 모릅니다.

## PR 보내기

1. 브랜치를 따서 작업합니다. `main` 에 직접 커밋하지 않습니다.
2. 위 검사를 로컬에서 통과시킵니다.
3. PR 을 엽니다. CI 가 macOS 와 Linux 양쪽에서 같은 검사를 돌립니다.

커밋 메시지는 Conventional Commits 를 쓰고 제목은 한국어로 씁니다.

```
feat: 줄표는 이번 편집에 하나라도 있으면 파일 전체 개수로 판정
fix: 릴리스 태그 메시지에서 ### 헤딩이 주석으로 잘리던 문제
docs: 스킬 유무 비교 기록
```

버전 번호는 손대지 마세요. `.claude-plugin/plugin.json` 이 정본이고 릴리스할 때 `scripts/release.sh` 가 README 배지와 CHANGELOG 를 맞춥니다.

## 가져온 파일

`skills/humanize-korean/**`, `skills/humanize/**`, `skills/humanize-redo/**`, `agents/**`, `scripts/*.py`(im-not-ai), `skills/crafting-effective-readmes/**`, `skills/korean-character-count/scripts/**` 는 다른 MIT 프로젝트에서 가져왔습니다. 고쳐야 한다면 [NOTICE.md](NOTICE.md) 의 수정 범위도 함께 고쳐 주세요. 원 저작자의 저작권 표시는 지우지 않습니다.

## 규칙과 라이선스

참여하는 모든 사람은 [행동 강령](CODE_OF_CONDUCT.md) 을 따릅니다. 보안 문제는 공개 이슈 대신 [SECURITY.md](SECURITY.md) 의 절차를 씁니다.

보내 주신 기여는 이 저장소와 같은 [MIT 라이선스](LICENSE) 로 배포됩니다.
