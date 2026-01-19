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

## 🧰 Architecture & Tools

본 서비스는 프론트엔드–백엔드–클라우드 스토리지를 명확히 분리한 구조로 설계되었습니다.

### Frontend
- **Streamlit**
  - 사용자 인터페이스(UI) 구성
  - FastAPI 백엔드와 REST API 통신
  - 세션 상태(`st.session_state`)를 활용한 캐싱
  - Streamlit Secrets를 통한 관리자 PIN 등 민감 정보 관리

### Backend
- **FastAPI**
  - 영화 및 리뷰 CRUD REST API 제공
  - ID 자동 생성 로직
  - 사용자 비밀번호 기반 삭제 권한 검증
  - 관리자 토큰 기반 관리자 삭제 처리

### Cloud Platform
- **Google Cloud Run**
  - FastAPI 백엔드 컨테이너 배포
  - 서버 관리 없이 자동 확장되는 서버리스 환경
  - 환경변수(`ADMIN_TOKEN`)를 통한 관리자 권한 관리

- **Google Cloud Storage (GCS)**
  - movies.json / reviews.json 저장
  - JSON 파일 기반 영구 데이터 보관
  - 서버 재시작·재배포 시에도 데이터 유지

### Authentication & Security
- **GCP Service Account (ADC)**
  - Cloud Run 런타임에서 자동 인증
- **Secrets / Environment Variables**
  - 관리자 토큰: Cloud Run 환경변수
  - 관리자 PIN: Streamlit Secrets

---
<img width="1536" height="1024" alt="image" src="https://github.com/user-attachments/assets/6fd82df1-c335-4197-af51-c32cd6578bab" />
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

---

