# NOTICE

이 플러그인은 MIT 라이선스입니다([LICENSE](./LICENSE)). 아래 파일은 다른 MIT 프로젝트에서 가져왔고 각 저작권 표시를 그대로 유지합니다. 허가 문구는 LICENSE의 MIT 본문과 같습니다.

## im-not-ai (Humanize KR)

    skills/humanize-korean/**                   그대로. SKILL.md 설명의 트리거 문구 "AI detector bypass 한글" 하나만 뺌
    skills/humanize/**                          그대로
    skills/humanize-redo/**                     그대로
    agents/humanize-monolith.md                 그대로. 런타임이 쓰는 에이전트 셋만 가져오고 개발용 여섯은 두지 않음
    agents/humanize-diagnostician.md            그대로
    agents/humanize-finalizer.md                그대로
    scripts/prepare_monolith_input.py           그대로. 아래 아홉은 스킬·에이전트가 부르는 스크립트와 그 import
    scripts/verify_gates.py
    scripts/restore_modality.py
    scripts/strip_injected_commas.py
    scripts/sanitize_text.py
    scripts/reassemble_chunks.py
    scripts/verify_change_rate.py
    scripts/console.py
    scripts/checks.py

    가져온 판: 커밋 9747f036cdc2 (2026-09-06)

    MIT License
    Copyright (c) 2026 epoko77-ai
    https://github.com/epoko77-ai/im-not-ai

## k-skill

    skills/korean-character-count/scripts/korean_character_count.js   수정 없음
    skills/korean-character-count/instruction.md                      실행 경로만 수정
    skills/korean-character-count/SKILL.md                            원본을 바탕으로 다시 씀

    MIT License
    Copyright (c) 2026
    https://github.com/NomaDamas/k-skill
