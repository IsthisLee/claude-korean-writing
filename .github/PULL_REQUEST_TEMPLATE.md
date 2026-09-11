## 무엇을 바꿨나

<!-- 한 줄로. 왜 바꿨는지도 한 줄. -->

## 확인한 것

<!-- 돌린 명령과 결과를 붙여 주세요. 통과했다는 말보다 출력이 낫습니다. -->

- [ ] `python3 tests/test_posttooluse.py`
- [ ] `python3 tests/test_pretooluse.py`
- [ ] `plugin/scripts/check.sh <고친 .md 파일>`

## 판정 규칙(K1~K10)을 바꿨다면

<!-- 규칙을 안 건드렸으면 이 절은 지우세요. -->

- [ ] `tools/measure.sh` 로 실제 문서에 돌린 결과를 아래에 적었습니다
- [ ] `tests/test_posttooluse.py` 에 회귀 테스트를 넣었습니다

```
대상 문서 N개 / 변경 전 걸림 N개 / 변경 후 걸림 N개
줄어들거나 늘어난 건이 사람의 글인지 Claude 의 글인지:
```

## 문서를 바꿨다면

- [ ] `README.md` 와 `README.en.md` 를 같이 고쳤습니다
- [ ] 가져온 파일을 고쳤다면 `plugin/NOTICE.md` 의 수정 범위도 고쳤습니다

<!--
English is welcome. See CONTRIBUTING.en.md.
Please do not bump the version by hand: plugin.json is the single source of truth.
-->
