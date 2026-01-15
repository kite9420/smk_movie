from fastapi import FastAPI
from pydantic import BaseModel
from google.cloud import storage
from typing import List
import json

app = FastAPI()

@app.get("/")
def health_check():
    return {"status": "ok"}

# Cloud Run 서비스 계정으로 자동 인증 (방법 B)
client = storage.Client()
BUCKET_NAME = "smk_main_home2"
bucket = client.bucket(BUCKET_NAME)

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

def save_to_gcs(filename: str, data: list):
    blob = bucket.blob(filename)
    blob.upload_from_string(
        data=json.dumps(data, ensure_ascii=False),
        content_type="application/json",
    )

def load_from_gcs(filename: str) -> list:
    blob = bucket.blob(filename)
    if not blob.exists():
        return []
    return json.loads(blob.download_as_text())

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
    return [r for r in all_reviews if r["movie_id"] == movie_id]

@app.post("/reviews")
def add_review(review: Review):
    all_reviews = load_from_gcs("reviews.json")
    all_reviews.append(review.dict())
    save_to_gcs("reviews.json", all_reviews)
    return {"message": "리뷰 등록 완료"}
