# Global Research Portal V4.2
기존 V4.1 기반. 캘린더가 첫 화면이며 월간/주간/연간, 국내, IDEC, 교육, 논문 마감, 충청권, 즐겨찾기 및 검색을 제공한다. 기존 43건 및 IDEC 14건(신청 시작/마감 포함). 기존 데이터는 재검증 필요. IDEC 초기 데이터는 2026-11-24 공식 페이지 확인분. 제목 일부가 생략된 항목은 표시함.

## Windows 실행
ZIP을 C:\global_research_portal_v42 에 풀고 CMD에서:
```
cd /d C:\global_research_portal_v42
python -m http.server 8000 --directory docs
```
http://localhost:8000 접속. 기존 서버가 있으면 종료하거나 다른 포트 사용.

## GitHub Pages 공개
기존 저장소를 백업하고 파일 구조를 유지해 복사(숨김 .github 포함). 기존 사용자가 추가한 events.json은 먼저 백업하고 아래 import 명령으로 병합. GitHub Desktop에서 commit/push. 신규 저장소라면 공개 저장소를 생성하고 main에 push. Settings > Pages > Source: GitHub Actions. Actions > Publish research portal > Run workflow. Actions > Daily research event collection > Run workflow 로 수집 테스트. 공개 사이트이므로 비공개 자료를 넣지 말 것.

## 자동 수집
한국 시간 오전 8시(전체, 해외 일반 출처 순환), 오후 6시(국내). 예약 실행은 지연될 수 있다. 공개 저장소 표준 runner 무료 운영 조건 및 GitHub 정책 적용. 사이트가 장기간 비활성 상태이면 예약 실행이 중단될 수 있다. Python 로컬 테스트:
```
python -m pip install -r requirements.txt
python scripts/deep.py
python scripts/test_collect.py
```
구조화된 행사는 병합하며 일반 HTML/PDF 날짜는 Review 검토 후보로 저장한다. IDEC 일반 HTML은 자동 확정되지 않으며 검토 후 import 필요. 크롤러는 등록 출처의 같은 호스트 하위 페이지를 최대 4개 탐색하며 robots 정책을 따른다. 로그인, 이미지 PDF, 동적 JS 페이지 제외. 실제 인터넷 수집 및 GitHub 배포는 미검증. 출처 105개, 국내 분류 54개(도메인 기반 추정 포함), 학회 후보 248개. 300/500/500 목표 미달. verified 표기는 해당 페이지 내용 확인이지 자동수집 성공을 의미하지 않음.

## 데이터 추가
웹 업로드는 브라우저 로컬에만 저장. 공개 데이터에 반영:
```
python scripts/collect.py --import-file 추가일정.json
```
이후 docs/data/events.json commit/push. 신청 시작일/마감일은 별도 이벤트. 교육 정보 미발표 항목은 추정하지 않음. Google Calendar 및 OpenAI API 미사용.
