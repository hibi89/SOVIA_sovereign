# SOVIA Audit Lite — 최소작동단위(MVP), 2026-10-28

## 목적 및 현재 상태
고객 출시가 아닌 합성 데이터 기반의 **실행 가능한 최소작동단위**. 검증된 Python 3.11+ 환경에서 추가 라이브러리·서버·프론트엔드 설치 없이 JSON 감사 → 한국어 HTML·JSON 보고서 → SQLite v2 이력까지 한 명령으로 생성한다. 기존 보고서 HTML을 임시 프론트엔드로 쓴다.

## 1회 실행 — 개발 소스의 develop 또는 별도 v0.12 ZIP 검증·압축 해제 후
출력 디렉터리는 **존재하지 않는 새 경로**여야 한다. ZIP을 압축 해제했다면 그 폴더에서:

```shell
python -I -B sovia_mvp_v012.py --input examples/demo_five_rules.json --output-dir ../sovia-mvp-output --synthetic-only
```

## 검증 가능한 결과
`../sovia-mvp-output/report.html` (브라우저로 열 수 있는 한국어 감사 결과), `report.json` (기계가 읽는 발견 사항), `history.sqlite3` (기본 메타데이터 이력) 3개. `demo_five_rules`: 3 events, 5 findings. `demo_temporal_boundary`: 3 events, 0 burst findings. 새 폴더 밖의 입력과 기존 파일을 덮어쓰지 않으며, 이미 있는 결과 폴더는 거부한다. 도중 강제 종료되면 새 폴더에 일부 파일이 남을 수 있으므로 **기존 경로를 재사용하지 않고 새 폴더로 다시 실행**한다.

## 증거
[PR #59](https://github.com/hibi89/SOVIA_sovereign/pull/59) 머지, [GitHub Actions #40526564129](https://github.com/hibi89/SOVIA_sovereign/actions/runs/40526564129): Windows/Ubuntu × Python 3.11/3.13 4/4 성공, 환경마다 840개 테스트 발견·0 실패, 패키지 압축 해제 독립 실행 PASS. v0.12 현재 *CI 합성 후보* SHA256 `1084cd267b7f8a00d656a13c6f55ff0c8795fcd507679de30ab59b8924e26b2c`. 과거 파일 SHA 고정, 새 후보는 별도.

## 명확히 후순위로 미룬 범위
프론트엔드 개편, 대시보드 디자인, SaaS/Cloud/Private, 추가 규칙, 고객용 설치 마법사, 외부 결제와 마케팅. 실제 n8n 원천 데이터 자동 수집·승인된 고객 데이터 감사·권한 및 동의의 독립 확인·개인정보 무검출 보증은 **이번 MVP에 없음**. `--synthetic-only`는 실제 증빙 없이 운영자가 합성 데이터라고 선언하는 플래그이므로 고객 원본 로그는 사용하지 않는다. Windows CI는 사용자 본인 PC·Defender·SmartScreen·수동 인쇄 확인을 대체하지 못한다. 보존·약관·지원·라이선스·서명·판매/배포 승인 없음.

## 다음 실행 단계
1. `develop`의 최신 CI 4/4 확인.
2. 사용자 로컬 PC에서 위 합성 입력으로 새 설치/열기/출력을 확인(필요 시).
3. 실제 데이터 사용은 출처·동의·스키마·비식별·보존·권한 검증 및 명시적 승인 이후 별도 구현.
4. UI·부가기능은 최소단위 안정성 확보 뒤 진행.
