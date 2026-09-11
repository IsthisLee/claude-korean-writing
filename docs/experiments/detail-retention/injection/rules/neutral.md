<!-- korean-writing: ignore -->
[session-notes] 이 세션의 작업 환경 메모. 답변 방식과는 관계없는 참고 사항이다.
- 작업 기기는 macOS 이고 기본 셸은 zsh 다. 시간대는 한국 표준시(UTC+9)를 쓴다.
- 저장소의 기본 브랜치는 main 이다. 원격 저장소는 GitHub 에 있고 CI 는 GitHub Actions 로 돈다.
- 패키지 관리자는 저장소마다 다르다. Node 프로젝트는 npm 이나 pnpm 을, Python 프로젝트는 pip 과 venv 를 쓴다.
- 로컬 개발 서버는 보통 3000 번이나 8080 번 포트를 쓴다. 이미 점유돼 있으면 다른 번호로 띄운다.
- 데이터베이스는 개발용과 운영용이 나뉘어 있다. 개발용은 로컬 도커 컨테이너에서 돈다.
- 문서는 저장소 루트의 README 와 docs 폴더에 있다. 변경 이력은 CHANGELOG 에 적는다.
- 테스트는 저장소마다 명령이 다르다. package.json 의 scripts 나 Makefile 을 먼저 확인한다.
- 비밀 값은 .env 파일에 두고 저장소에 올리지 않는다. 예시 값은 .env.example 에 둔다.
- 이미지와 폰트 같은 정적 파일은 public 이나 assets 폴더에 둔다. 빌드 산출물은 dist 에 생긴다.
- 로그는 개발 중에는 콘솔로, 운영에서는 수집 서비스로 보낸다. 로그 수준은 환경 변수로 바꾼다.
