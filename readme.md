🎬 코드잇 스프린트 18: 영화 리뷰 서비스 (GCP 연동형)
📌 프로젝트 개요

본 프로젝트는 로컬 파일 저장 방식의 한계를 극복하고,
**Google Cloud Storage(GCS)**를 백엔드 데이터 저장소로 활용한
클라우드 기반 영화 리뷰 서비스입니다.

영화 정보와 리뷰 데이터는 JSON 형태로 GCS 버킷에 저장되며,
서버 재시작·재배포·클라우드 환경에서도 데이터가 유실되지 않는
영구 저장 구조를 구현했습니다.

프론트엔드와 백엔드를 완전히 분리하고,
백엔드는 GCP Cloud Run에 배포하여 실제 서비스 환경과 유사한 구조로 설계했습니다.

🛠 주요 기술 스택
Frontend

Streamlit

사용자 인터페이스(UI)

FastAPI 백엔드와 HTTP 통신

Streamlit Secrets를 활용한 보안 정보 관리

Backend

FastAPI

RESTful API 서버

영화/리뷰 CRUD 로직 처리

인증 및 삭제 권한 검증

Cloud & Storage

Google Cloud Storage (GCS)

JSON 파일 기반 영구 데이터 저장소

Google Cloud Run

FastAPI 컨테이너 배포 및 운영

Deployment & Security

GitHub

Streamlit Cloud

Environment Variables / Secrets

서비스 계정 키

관리자 토큰

관리자 PIN

🌟 핵심 구현 기능
1. GCS 기반 데이터 영구화

movies.json / reviews.json을 GCS 버킷에 저장

서버 재시작·재배포 후에도 데이터 유지

로컬 파일 시스템 의존성 제거

2. 프론트엔드 / 백엔드 완전 분리

Streamlit: UI 및 API 호출만 담당

FastAPI: 모든 데이터 처리 및 검증 담당

프론트에서 로컬 서버 실행 없이 Cloud Run API 호출

3. ID 기반 데이터 관리

영화 및 리뷰 ID는 백엔드에서 자동 생성

프론트는 ID를 생성하지 않음

삭제·조회 시 정확한 대상 식별 가능

4. 데이터 정합성 처리

영화 삭제 시:

movies.json에서 영화 삭제

reviews.json에서 해당 movie_id 리뷰도 함께 삭제

“고아 리뷰” 데이터 발생 방지

5. 사용자 비밀번호 기반 삭제 권한

영화 / 리뷰 생성 시 비밀번호 설정

비밀번호는 평문 저장 ❌

PBKDF2-HMAC-SHA256 + salt 방식으로 해싱 저장

삭제 시 입력한 비밀번호 검증 후 삭제 허용

6. 관리자 삭제 권한 (Admin Override)

관리자 토큰(ADMIN_TOKEN)은 Cloud Run 환경변수로 관리

관리자 PIN(ADMIN_PIN)은 Streamlit Secrets에만 저장

삭제 비밀번호 입력창 하나로 처리:

입력값이 관리자 PIN과 같으면 → 관리자 삭제

아니면 → 일반 사용자 비밀번호 검증

7. 보안 설계

관리자 토큰 프론트 코드 하드코딩 ❌

Streamlit Secrets / Cloud Run 환경변수 분리 관리

프론트 노출 URL만으로 관리자 권한 획득 불가

8. 데이터 마이그레이션

기존 ID 없는 데이터 대응

마이그레이션 API 제공:

/migrate/movies

/migrate/reviews

기존 JSON 데이터에 ID 자동 부여

9. 사용자 경험(UI)

영화 포스터 이미지 URL 표시

별점 기반 리뷰 입력 (피드백 UI)

리뷰 실시간 갱신

세션 상태 기반 캐싱으로 불필요한 API 호출 최소화

📦 배포 구조 요약

Backend

Dockerized FastAPI

Google Cloud Run 배포

Frontend

Streamlit Cloud

Cloud Run API URL 연동

재배포 정책

백엔드 수정 시에만 Cloud Run 재배포

프론트는 URL 기반 연동

✅ 프로젝트 결과 요약

클라우드 환경에서 동작하는 실서비스형 구조 구현

데이터 영구성, 보안, 권한, 정합성 문제 직접 해결

단순 CRUD를 넘어 실제 운영 환경을 고려한 설계 경험 확보

------------
