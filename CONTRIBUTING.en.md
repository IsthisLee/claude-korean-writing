# Contributing

<p><a href="CONTRIBUTING.md">한국어</a> · <strong>English</strong></p>

Contributions are welcome. This page covers what is most useful to send and how it gets evaluated.

## Real sentences matter most

The thresholds in this project are calibrated on **sentences Claude Code actually produced**, not on invented examples. Synthetic bad examples are easy to write, but tuning on them catches phrasing that never occurs in practice while missing the phrasing that does.

So the most valuable contribution here is not code. It is a sentence.

- Saw Claude write awkward Korean? Send it through [the report form](https://github.com/IsthisLee/claude-korean-writing/issues/new?template=awkward-sentence.yml). Paste the original, uncorrected.
- Did the hook flag a perfectly normal sentence? Send that too. False positives are worse than misses, because they make people turn the checker off.

Reported sentences become regression tests in `tests/ground-truth.json` or `clean.json`.

## Getting started

There is no build step.

```bash
git clone https://github.com/IsthisLee/claude-korean-writing
cd claude-korean-writing

python3 tests/test_posttooluse.py       # hook regression tests
plugin/scripts/check.sh README.en.md CONTRIBUTING.en.md # do the docs pass their own hook
```

| Requirement | Used for                       | If missing                         |
| ----------- | ------------------------------ | ---------------------------------- |
| `bash`      | The hook and the scripts       | The hook will not run              |
| `python3`   | Hook logic and the test suite  | The hook exits quietly, no checking |
| `node`      | Character-count script         | Only that one skill is unavailable |

CI runs on macOS and Linux. On Windows you need Git Bash or WSL.

## Changing a rule requires measurement

If your change adds, removes, or retunes any of K1–K8 in `plugin/hooks-handlers/posttooluse.sh`, **include numbers.** Tuning by intuition grows the false-positive rate silently.

```bash
tools/measure.sh ~/some/docs ~/other/docs
```

Point it at folders of Korean `.md` files. It reports how many files trip the hook and under which codes. A flagged file written by a human is a false positive; one written by Claude is a true catch. A person makes that call.

Something like this in the PR body is enough:

```
143 documents scanned / 12 flagged before / 4 flagged after
All 8 that stopped being flagged were written by humans in 2022-23
```

This is how "죽다" was dropped from K7 and how counting `~에 대해` was dropped from K8. A rule with no discriminating power only catches human writing. See [EVALUATION.md](EVALUATION.md) for the details.

**Ship a regression test with any behavior change.** Add the sentence that must pass and the sentence that must be caught to `tests/test_posttooluse.py`. If an existing test fails, fix the code, not the test. If a requirement genuinely changed, say in one line what changed and why that test is now wrong.

## Changing the docs

Korean documents in this repo have to satisfy the repo's own rules. A project that breaks its own rules is not convincing.

```bash
plugin/scripts/check.sh path/to/file.md
```

For documents that deliberately quote bad examples, put `<!-- korean-writing: ignore -->` at the top of the file.

When you edit a README, edit both the Korean and the English one. If only one side changes, the next reader cannot tell which to trust.

## Sending a PR

1. Work on a branch. Do not commit straight to `main`.
2. Get the checks above passing locally.
3. Open the PR. CI runs the same checks on macOS and Linux.

Commit messages follow Conventional Commits, with the subject written in Korean:

```
feat: 줄표는 이번 편집에 하나라도 있으면 파일 전체 개수로 판정
fix: 릴리스 태그 메시지에서 ### 헤딩이 주석으로 잘리던 문제
docs: 스킬 유무 비교 기록
```

Leave version numbers alone. `plugin/.claude-plugin/plugin.json` is the single source of truth, and `tools/release.sh` syncs the README badges and CHANGELOG at release time.

## Vendored files

`plugin/skills/humanize-korean/**`, `plugin/skills/humanize/**`, `plugin/skills/humanize-redo/**`, `plugin/agents/**`, `plugin/scripts/*.py` (im-not-ai), `plugin/skills/crafting-effective-readmes/**` and `plugin/skills/korean-character-count/scripts/**` come from other MIT projects. If you change one, update the corresponding entry in [plugin/NOTICE.md](plugin/NOTICE.md) too, and never remove an upstream copyright notice.

## Conduct and license

Everyone taking part follows the [Code of Conduct](CODE_OF_CONDUCT.md). For security issues, use the process in [SECURITY.md](SECURITY.md) rather than a public issue.

Contributions are released under the same [MIT License](LICENSE) as the project.
