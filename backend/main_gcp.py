from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google.cloud import storage
from google.oauth2 import service_account
import streamlit as st
import json
import os
from typing import List

app = FastAPI()


def get_gcs_client():
    creds = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"]
    )
    return storage.Client(credentials=creds)


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