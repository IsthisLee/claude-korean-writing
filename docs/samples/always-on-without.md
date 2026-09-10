<!-- korean-writing: ignore -->
<!-- 2026-09-10, claude-sonnet-5, claude -p --setting-sources "" --strict-mcp-config --plugin-dir <저장소> --max-turns 1. 조건: 상시 규칙 주입 없음 (KOREAN_WRITING_ALWAYS_ON_DISABLED=1). 손대지 않은 원문. -->

이 훅은 `value`가 바뀔 때마다 즉시 반영하지 않고, `delay`(기본 300ms) 동안 값이 안정적으로 유지된 뒤에야 `debounced` 상태를 갱신합니다. 검색어 입력처럼 타이핑할 때마다 API 호출하는 걸 막는 용도로 씁니다.

**동작 흐름**
1. `value`가 바뀌면 `useEffect`가 재실행되면서 `setTimeout`으로 `delay` 후 `setDebounced(value)`를 예약합니다.
2. 그 `delay` 안에 `value`가 또 바뀌면, effect가 다시 실행되기 전에 cleanup 함수(`clearTimeout(id)`)가 먼저 호출되어 **이전에 예약해둔 타이머를 취소**합니다.
3. 이 과정이 반복되다가, 사용자가 타이핑을 멈춰서 `delay` 동안 `value`가 더 이상 바뀌지 않으면 그때 예약된 타이머가 끝까지 살아남아 `setDebounced`가 실행됩니다.

**cleanup이 왜 필요한가**

React는 의존성(`[value, delay]`)이 바뀔 때마다 "다음 effect 실행 직전" 또는 "컴포넌트 언마운트 시"에 이전 effect가 반환한 cleanup 함수를 호출합니다. 만약 `clearTimeout(id)`가 없다면:

- 사용자가 "r" → "re" → "rea" → "reac" 처럼 빠르게 타이핑할 때마다 `setTimeout`이 계속 쌓입니다.
- 각 타이머가 취소되지 않으므로, 이전 글자들에 대한 `setDebounced` 호출까지 전부 뒤늦게 실행됩니다 (불필요한 리렌더링 발생, 그리고 결과적으로 최신 값이 아닌 중간 값들로 상태가 여러 번 튀었다가 마지막에야 맞는 값이 됨).
- 컴포넌트가 언마운트된 후에도 타이머가 남아있다가 `setDebounced`를 호출하면, 이미 사라진 컴포넌트의 상태를 갱신하려는 시도가 발생합니다 (React 18 이전에는 메모리 누수 경고가 뜨는 경우).

즉 cleanup은 "값이 바뀔 때마다 이전 예약을 취소하고 새로 예약한다"는 디바운스의 핵심 로직 자체를 구현하는 부분이며, 동시에 언마운트 시 잔여 타이머로 인한 부수효과(불필요한 state 업데이트)를 막아주는 역할도 합니다.
