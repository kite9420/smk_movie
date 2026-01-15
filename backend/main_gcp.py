from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google.cloud import storage
from google.oauth2 import service_account
import json
import os
from typing import List

app = FastAPI()


def get_gcs_client():
    # 로컬용 키 파일 경로
    OS_AUTH_KEY = "backend/sprintmission18backend-34b4ac021f8f.json"
    
    # 1. 로컬에 파일이 있으면 파일을 써서 인증
    if os.path.exists(OS_AUTH_KEY):
        return storage.Client.from_service_account_json(OS_AUTH_KEY)
    
    # 2. 클라우드(스트림릿)라면 시스템 환경변수를 써서 자동 인증
    # (Secrets에 넣은 정보는 구글 라이브러리가 자동으로 찾아냅니다)
    return storage.Client()

client = get_gcs_client()
BUCKET_NAME = "smk_main_home"
bucket = client.bucket(BUCKET_NAME)

# 2. 데이터 모델 정의
class Movie(BaseModel):
    id: int
    title: str
    poster_url: str
    release_date: str
    director: str
    genre: str

class Review(BaseModel):
    movie_id: int
    author: str
    content: str
    score: int

# 3. GCP 파일 읽기/쓰기 헬퍼 함수
def save_to_gcs(filename: str, data: list):
    blob = bucket.blob(filename)
    blob.upload_from_string(
        data=json.dumps(data, ensure_ascii=False),
        content_type='application/json'
    )

def load_from_gcs(filename: str) -> list:
    blob = bucket.blob(filename)
    if not blob.exists():
        return []
    return json.loads(blob.download_as_text())

# 4. API 엔드포인트
@app.get("/movies", response_model=List[Movie])
def get_movies():
    return load_from_gcs("movies.json")

@app.post("/movies")
def add_movie(movie: Movie):
    movies = load_from_gcs("movies.json")
    movies.append(movie.dict())
    save_to_gcs("movies.json", movies)
    return {"message": "영화 등록 완료"}

@app.get("/movies/{movie_id}/reviews", response_model=List[Review])
def get_reviews(movie_id: int):
    all_reviews = load_from_gcs("reviews.json")
    # 해당 영화 ID에 맞는 리뷰만 필터링
    return [r for r in all_reviews if r['movie_id'] == movie_id]

@app.post("/reviews")
def add_review(review: Review):
    all_reviews = load_from_gcs("reviews.json")
    all_reviews.append(review.dict())
    save_to_gcs("reviews.json", all_reviews)
    return {"message": "리뷰 등록 완료"}