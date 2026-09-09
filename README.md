# korean-writing

밖으로 나갈 한국어 글에서 번역투와 AI 관용구를 **처음 쓸 때부터** 걷어내는 Claude Code 플러그인.

사후 윤문을 강제하지 않는다. 생성 단계에서 잡는 것이 싸고 정확하다.

## 무엇이 들어 있나

| 구성                            | 하는 일                                                 |
| ------------------------------- | ------------------------------------------------------- |
| `SKILL.md`                      | 밖으로 나갈 글을 쓸 때 로드된다. 원칙·품질 바·교정 예시 |
| `skills/humanize-korean`        | 이미 써둔 글을 다듬는다. 사실 불변, 변경률 50% 상한     |
| `skills/korean-character-count` | grapheme·줄·바이트를 정확히 센다. 외부 호출 없음        |
| `references/quick-rules.md`     | 다듬기용 압축 룰북                                      |
| `references/taxonomy.md`        | 전체 패턴 10분류 73항목. 판정이 애매할 때만 연다        |
| `hooks/`                        | `.md` 편집 시 K1~K8 자동 검사                           |

## 훅이 잡는 것

이번에 쓴 부분만 검사한다. 파일 전체를 보면 예전 표현이 매 편집마다 다시 걸려 소음이 된다.

| 코드 | 패턴                                          | 임계      |
| ---- | --------------------------------------------- | --------- |
| K1   | 줄표(`—`) 삽입구                              | 4개       |
| K2   | 추상 구조어 `축`·`갈래`·`결이 다`·`레이어`    | 3회       |
| K3   | 번역투 `것들이었`                             | 1회       |
| K4   | AI 관용구 `결론적으로`·`혁신적`               | 1회       |
| K5   | `첫째`·`둘째` 기계적 병렬                     | 동시 등장 |
| K6   | 승패 의인화 `이깁니다`                        | 2회       |
| K7   | 사물 의인화 `화면이 굳어`                     | 1회       |
| K8   | 번역투 `되어지`·`가지고 있다`·`~에 대해` 남발 | 항목별    |

코드블록·인라인 코드·URL·표 행은 제외한다. 한글 20자 미만이거나 비중 30% 미만이면 검사하지 않는다.

## 설치

```bash
claude plugin marketplace add <사용자명>/korean-writing
claude plugin install korean-writing@korean-writing
```

## 개발

저장소를 `~/.claude/skills/` 로 링크하면 `korean-writing@skills-dir` 로 자동 로드된다. 마켓플레이스를 거치지 않아 고치는 즉시 반영된다.

```bash
ln -s "$PWD" ~/.claude/skills/korean-writing
claude plugin list                              # loaded 확인
python3 hooks-handlers/test_posttooluse.py      # 회귀 27건
```

## 검증

`EVALUATION.md` 에 합격 기준과 측정 결과가 있다.

```
위반 검출  10/10      정상 오탐    0/5
분류 정확  10/10      실문서 오탐  1/227
변이 검출  15/15      회귀 테스트  27/27
외부 호출   0건       상시 비용   416 토큰
```

정답 데이터(`hooks-handlers/ground-truth.json`)는 실제로 생성됐던 어색한 문장이다. 합성 예문이 아니다.

## 출처

`references/` 는 [claude-forge](https://github.com/sangrokjung/claude-forge), `korean-character-count` 는 [k-skill](https://github.com/NomaDamas/k-skill) 에서 가져왔다. 둘 다 MIT 이고 `LICENSE` 에 표시를 남겼다.

맞춤법 검사 스킬은 원문을 외부 서버로 전송해 가져오지 않았다.
