<!-- korean-writing: ignore -->
# 상시 규칙 전후 비교에 쓴 질문

실험 프롬프트 01. `docs/experiments/always-on/prompts/01.txt` 와 같다.

```
이 함수가 뭘 하는지 설명해줘. 특히 cleanup 이 왜 필요한지.

```ts
export function useDebouncedValue<T>(value: T, delay = 300): T {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const id = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(id);
  }, [value, delay]);
  return debounced;
}
```
```
