# 🎬 코드잇 스프린트 18: 영화 리뷰 서비스 (GCP 연동형)

## 📌 프로젝트 개요

본 프로젝트는 로컬 파일 저장 방식의 한계를 극복하고,  
**Google Cloud Storage(GCS)**를 데이터 저장소로 활용한  
**클라우드 기반 영화 리뷰 서비스**입니다.

영화 및 리뷰 데이터는 JSON 형태로 GCS 버킷에 저장되며,  
서버 재시작·재배포·클라우드 환경에서도 데이터가 유실되지 않는  
**영구 저장 구조**를 구현했습니다.

프론트엔드(Streamlit)와 백엔드(FastAPI)를 완전히 분리하고,  
백엔드는 **Google Cloud Run**에 배포하여  
실제 운영 환경과 유사한 아키텍처를 구성했습니다.

---

## 🛠 기술 스택

### Frontend
- **Streamlit**
  - 사용자 UI 렌더링
  - FastAPI 백엔드와 REST API 통신
  - 세션 상태(`st.session_state`) 기반 캐싱
  - Streamlit Secrets를 통한 민감 정보 관리

### Backend
- **FastAPI**
  - 영화 / 리뷰 CRUD API
  - ID 자동 생성
  - 비밀번호 기반 삭제 권한 검증
  - 관리자 권한 처리

### Cloud & Storage
- **Google Cloud Storage (GCS)**
  - JSON 파일 기반 영구 데이터 저장
- **Google Cloud Run**
  - FastAPI 컨테이너 배포 및 운영

### Security
- **Service Account (ADC)**
  - Cloud Run 런타임 자동 인증
- **Secrets / Environment Variables**
  - 관리자 토큰, 관리자 PIN 분리 관리

---

## 🧱 전체 아키텍처 다이어그램

```mermaid
flowchart TD
  U[User Browser] -->|HTTPS| S[Streamlit Cloud<br/>Frontend]

  S -->|REST API<br/>GET / POST / DELETE| R[Cloud Run<br/>FastAPI Backend]

  R -->|Google Cloud Storage Client| G[(GCS Bucket<br/>movies.json<br/>reviews.json)]

  S --- SS[Streamlit Secrets<br/>ADMIN_PIN]
  R --- ENV[Cloud Run Env<br/>ADMIN_TOKEN]
  R --- SA[Cloud Run Service Account<br/>ADC Authentication]
