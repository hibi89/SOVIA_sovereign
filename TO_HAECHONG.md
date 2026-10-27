# TO_HAECHONG.md — 해총님에게
> SOVIA Sovereign 개발 총괄 / 2026-10-28 KST
> 제출 대상: PUBLIC `hibi89/SOVIA_sovereign` / 실제 개발 브랜치 `develop`
> 검수 질문: **기존 병목은 무엇이며, 실제로 없앤 작업 절차와 새로 완성한 기능은 무엇인가?**

## 1. 기존 병목 TOP 3

1. **문서·원격 CI 과잉:** 기능 병합 후 HANDOFF/STATUS/GAP_MATRIX를 여러 번 되풀이 편집·커밋해 전체 4-환경 CI를 재가동. PR #65–#67 이력에서 반복된 절차. 기능 진척에 직접 필요하지 않은 재검증 부담.
2. **GitHub 파일별 API 수정과 같은 SHA 재조회:** 제한적인 개발 환경에서 작은 수정도 원격 blobs/trees/refs 작업과 상태 확인이 반복됨. *작업시간 전체에 대한 계측 없음*.
3. **집중 테스트보다 전체 CI에서 플랫폼 결함 발견:** PR #66의 Windows SQLite 연결 해제 문제는 두 번의 Windows CI 실패 후 해결. PR #67 첫 CI도 기존 `INPUT_OUTPUT_PATH_COLLISION` 오류 코드 호환성을 놓쳤다가 재수정. 회귀 실행 자체는 필요하지만 발견 순서가 비효율적이었음.

## 2. 병목 발생 원인

- 문서 분리 원칙 부재 및 과도한 10개 항목 인수인계 복제; GitHub push마다 4-job CI가 실행되는 워크플로.
- GitHub API 기반 파일 단위 수정 및 불필요한 HEAD/CI 폴링; 직접적인 API·사용자 대기시간 절감량은 **미측정**.
- Windows SQLite 잠금/기존 에러 코드 등 소규모 계약 테스트를 전체 CI 뒤에 발견. GitHub-hosted Windows CI는 존재하므로 'Windows 테스트 자체 불가'는 사실이 아님.

## 3. 실제 적용한 개선 / 아직 미개선인 것

- **적용:** [PR #68](https://github.com/hibi89/SOVIA_sovereign/pull/68)에서 기능 코드·합성 fixture·집중 테스트·Windows 원클릭 검증·AGENTS 가속 지침·CI 연동을 **하나의 기능 커밋** `cf27922d6d76ae0c0d7ced5d80fda5623da10c83`에 묶어 구현. 동일 기능 뒤에 HANDOFF/STATUS/GAP_MATRIX 개별 커밋은 만들지 않음.
- **적용:** `verify_local.ps1` 제공. 기본(quick)은 버전/소스 구문/LA 계획 핵심 테스트/실행 스모크; `-Full`은 전체 unittest + v0.12 portable smoke. 신규 임시 폴더에 PASS/FAIL/SKIP, 실행별 시간, 로그와 `summary.json` 저장. 기본 모드는 전체 검증을 수행했다고 표시하지 않음. 고객 데이터/기존 DB 변경 없음.
- **적용:** GitHub Windows Python3.11 job이 스크립트를 실제 실행하도록 CI 구성. 기능 브랜치에서는 4-job 검증 후 병합. 단일 개발 루프를 `AGENTS.md` 첫 부분에 기록.
- **미개선/미계측:** 기존 GitHub Actions의 모든 문서 수정 재실행 조건 자체는 제거하지 않음; 특히 이번 보고서 커밋도 CI 실행을 촉발할 수 있음. API 총 호출 수, 총 소요시간, 개발 속도 향상률은 전후 계측이 없어 **측정 불가**. 직접 구현 대비 전 방식의 시간 단축 효과는 입증되지 않았음.

## 4. 개선 이후 실제 기능 진척

- 신규 `sovia_la_plan_preflight.py`: **LA 우선 전략**을 반영한 독립형 *합성·사전 정제 계획 메타데이터* 위험평가. 계획의 허용 도구/목적지 정책 위반, 민감 대상과 승인 주장, 외부 송신/로컬 쓰기/결제/파괴적 행동, 미분류 부작용을 판정해 근거 미검증 소견을 반환.
- 실제 파서·CLI·예제·테스트를 추가하고 실제 CI에서 실행. 위험 소견 0건이어도 `execution_authorized=false`; **실제 LA IR/실행 로그를 읽는 연동, 실행 중 차단, 권한/승인 인증 또는 제품 출시가 아님**.
- 검증 자동화는 개발 속도 보조 작업으로, 제품 기능 자체와 구분함.

## 5. 전후 SHA 및 실행 증거

| 지점 | 검증 가능한 증거 |
|---|---|
| 변경 전 `develop` | `ccc8e0b3527efb7f59f6adb3513eb4356e3bdb99`; [Actions #40549170143](https://github.com/hibi89/SOVIA_sovereign/actions/runs/40549170143) 4/4 성공 |
| 기능 PR 소스 SHA | `cf27922d6d76ae0c0d7ced5d80fda5623da10c83`; [PR #68](https://github.com/hibi89/SOVIA_sovereign/pull/68), **6개 변경 파일** (아래) |
| PR 실제 전체 CI | [Actions #40552872841](https://github.com/hibi89/SOVIA_sovereign/actions/runs/40552872841) Windows/Ubuntu × Python3.11/3.13 **4/4 PASS**, 각 환경 **890개 발견/0 FAIL**; Win3.11 **879 PASS+11 SKIP**, Ubuntu3.11 **869 PASS+21 SKIP** |
| PR 병합 SHA | `9556828deeb95a54c520c55631fb5e2923c377fb` → `develop` |
| 병합 후 실제 CI | [Actions #40553343917](https://github.com/hibi89/SOVIA_sovereign/actions/runs/40553343917) **4/4 SUCCESS**, 해당 병합 SHA와 매칭 |
| Windows 단일 명령 | PR CI Windows3.11 step `Windows single-command focused offline verifier` 실제 성공. 사용자 본인 PC 실행은 **미실시** |

변경 파일: `sovia_la_plan_preflight.py`, `tests/test_sovia_la_plan_preflight.py`, `examples/demo_la_plan_review.json`, `verify_local.ps1`, `AGENTS.md`, `.github/workflows/sovia-offline-regression.yml`. 테스트를 *작성*한 사실과 실제 **hosted CI 실행**을 분리하여 보고함.

## 6. 남아 있는 병목 / 담당 가능 여부

- **AI 자체 처리 가능:** SOVIA 코드·테스트·합성 계약 발전, 작은 단위 집중 테스트, 무해한 CI/스크립트 자동화, 부적합 오류 코드 회귀 수정, 레포 내 기능 병합.
- **연동 공동작업 필요:** LA 측 실제 IR·계획·영수증에서 SOVIA로 전달할 **비밀 없는 버전 고정 최소 메타데이터 계약 합의**. 현재 SOVIA 계획 검토는 임의 합성 정제 사실의 독립형 평가이지 통합 연동은 아님.
- **사용자 Windows/승인 필요:** 본인 PC Defender/SmartScreen, 한국어 브라우저/PDF 시각 확인, 실제 고객 기록·권한·동의·보존/삭제·법무, 서명된 상용 패키지·배포/판매 승인. GitHub CI 성공으로 이 항목들을 대체하지 않음.
- **완화 불가 경계:** 파일 경로 TOCTOU, 휴리스틱 개인정보 미탐, 서명되지 않은 operator claim. 실제 보안/권한 검사를 속도 명목으로 생략하지 않음.

## 7. 다음 개발 계획 및 완료조건

1. **최우선:** LA 계획/승인/실행 영수증의 *정제된 공통 사실 계약*을 실제 LA 총괄과 정하고, SOVIA로 전달·비교하는 재현 가능한 종단 간 합성 실행 통합을 완성. 사전 계획 위험과 사후 관측 행동/증거 부재를 대조해야 함. 사전 계획 검토 함수만 있는 현 단계와 구분.
2. **즉시 개발 가능:** SOVIA 측 계획→관측 결과 불일치/미관측/증거 누락 검토 기능 구현, 로컬 fixture 집중 테스트 후 기능 단위 CI. LA의 사설 내부 구조를 공개 레포에 복제하지 않음.
3. **통합 완료 조건:** LA에서 생성한 한 건의 합성 실행 흐름이 SOVIA의 사전 계획 점검 → 실행 관측 대조 → 위험·미확인 보고로 연결되고, 무승인/스키마 불일치/부재/재실행/오류 테스트를 통과. 전체 Windows/Ubuntu 회귀를 통합점에서 확인.
4. **최종 Audit Lite:** P1 합성 MVP는 작동·CI 검증되었으나 최종 판매형 제품은 미완료. 실제 LA 출처·승인 근거·고객 격리, Windows 수동 QA, 정책/보존, 지원·설치·서명 등 미해결. Cloud/Private는 후속 단계이며 이 보고의 완료 범위 밖.

**검수 판정은 해총님에게 위임.** 개발 프로세스 변경은 `AGENTS.md`, 실제 기능은 PR #68 및 테스트 기록으로 교차검증. 이 보고서 최초 제출은 사용자 요청에 따른 1회 예외적 문서 커밋이며 제품 완료 선언이 아니다.
