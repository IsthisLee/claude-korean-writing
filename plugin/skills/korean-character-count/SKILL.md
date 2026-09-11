---
name: korean-character-count
description: 한국어 글자 수·줄 수·바이트를 정확히 세야 할 때 사용한다. "500자 이내로", "글자 수 세줘", "자소서 분량 맞춰줘", "폼 제한에 맞나 확인", 지원서·자기소개서·카피처럼 길이 제한이 걸린 글이 트리거. 눈대중이나 단순 문자열 길이로는 틀린다.
---

# 한국어 글자 수 세기

한국어는 세는 기준에 따라 숫자가 달라진다. 폼이 "500자 이내"라고 할 때 무엇을 세는지에 따라 통과와 초과가 갈린다.

- `각`은 1글자지만 UTF-8로 3바이트다
- 조합형 자모(`ㄱ`+`ㅏ`+`ㄱ`)는 눈에는 1글자, 코드포인트로는 3개다
- 이모지와 결합 문자는 grapheme cluster로 세야 맞다

**추정하지 말고 스크립트를 돌린다.**

## 쓰는 법

```bash
node scripts/korean_character_count.js --text "각 글자 세기" --format text
node scripts/korean_character_count.js --file <경로>
cat <파일> | node scripts/korean_character_count.js --stdin
```

옵션.

| 옵션 | 값 |
|---|---|
| `--profile` | `default`(grapheme + UTF-8) 또는 `neis`(교육행정시스템 기준) |
| `--format` | `json`(기본) 또는 `text` |

Node 18 이상이 필요하다. `Intl.Segmenter`를 쓰기 때문이다. **외부 패키지를 받지 않는다** — `node:fs`만 쓴다.

## 나오는 값

```
characters                      grapheme cluster 기준. 대개 이게 "글자 수"다
characters_without_whitespace   공백 제외
code_points                     유니코드 코드포인트
utf16_code_units                JavaScript 의 .length
lines                           줄 수
bytes_utf8                      UTF-8 바이트
bytes_neis                      NEIS 기준 바이트
```

## 어느 값을 쓰나

**폼이 무엇을 세는지 확인하고 고른다.** 명시가 없으면 `characters`(grapheme)가 사람이 세는 방식과 가장 가깝다.

| 상황 | 값 |
|---|---|
| 일반 폼 "N자 이내" | `characters` |
| 공백 제외 명시 | `characters_without_whitespace` |
| NEIS·교육행정 양식 | `bytes_neis` (`--profile neis`) |
| DB 컬럼 길이 확인 | `bytes_utf8` |

## 자세한 계약

세는 규칙의 전문은 `instruction.md`에 있다. grapheme 경계, 줄바꿈 처리(CRLF·LF·CR·U+2028·U+2029), 바이트 계산 근거가 적혀 있다.

## 이 스킬이 아닌 것

문체 교정은 `korean-writing`, 이미 쓴 글 윤문은 `humanize-korean`이다. 이 스킬은 **세기만** 한다.
