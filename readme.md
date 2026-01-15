🎬 코드잇 스프린트 18: 영화 리뷰 서비스 (GCP 연동형)
📌 프로젝트 개요
로컬 파일 저장 방식의 한계를 넘어, **Google Cloud Storage(GCS)**를 백엔드 데이터베이스로 활용한 영구 저장형 영화 리뷰 서비스입니다. 사용자가 입력한 영화 정보와 리뷰 데이터는 JSON 형태로 구글 클라우드 버킷에 실시간 저장되어, 서버 재시작이나 클라우드 배포 환경에서도 데이터가 유실되지 않고 안전하게 보존됩니다.

🛠 주요 기술 스택
Frontend: Streamlit (사용자 UI 및 백엔드 서버 자동 실행 제어)

Backend: FastAPI (GCS 연동 API 서버)

Cloud Storage: Google Cloud Platform (GCP) - JSON 파일 기반 영구 데이터 보관

Deployment: Streamlit Cloud & GitHub (Secrets를 활용한 보안 인증 관리)

🌟 핵심 구현 기능
GCS 기반 데이터 영구화: 백엔드 종료 후에도 데이터가 유지되는 클라우드 버킷 연동 환경 구축

보안 인증 최적화: GCP 서비스 계정(JSON 키)을 활용하되, 로컬(파일)과 클라우드(Secrets 환경변수) 양쪽에서 유연하게 작동하는 인증 로직 구현

FastAPI 엔드포인트: 영화 목록 조회/추가 및 영화별 리뷰 필터링 기능을 제공하는 RESTful API 설계

사용자 경험: 영화 포스터 URL 연동, 별점 피드백 시스템, 실시간 리뷰 갱신 기능 포함