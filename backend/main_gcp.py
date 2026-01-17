from fastapi import FastAPI
from fastapi import HTTPException
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
    id: int
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
def add_movie(movie: dict):
    movies = load_from_gcs("movies.json")

    next_id = (max([m.get("id", 0) for m in movies]) + 1) if movies else 1

    movie_obj = {
        "id": next_id,
        "title": movie["title"],
        "poster_url": movie["poster_url"],
        "release_date": movie["release_date"],
        "director": movie["director"],
        "genre": movie["genre"],
    }

    movies.append(movie_obj)
    save_to_gcs("movies.json", movies)
    return {"message": "영화 등록 완료", "id": next_id}

@app.get("/movies/{movie_id}/reviews", response_model=List[Review])
def get_reviews(movie_id: int):
    all_reviews = load_from_gcs("reviews.json")
    return [r for r in all_reviews if r["movie_id"] == movie_id]

@app.post("/reviews")
def add_review(review: dict):
    all_reviews = load_from_gcs("reviews.json")

    next_id = (max([r.get("id", 0) for r in all_reviews]) + 1) if all_reviews else 1

    review_obj = {
        "id": next_id,
        "movie_id": review["movie_id"],
        "author": review["author"],
        "content": review["content"],
        "score": review["score"],
    }

    all_reviews.append(review_obj)
    save_to_gcs("reviews.json", all_reviews)
    return {"message": "리뷰 등록 완료", "id": next_id}

@app.delete("/reviews/{review_id}")
def delete_review(review_id: int):
    all_reviews = load_from_gcs("reviews.json")
    new_reviews = [r for r in all_reviews if r.get("id") != review_id]

    if len(new_reviews) == len(all_reviews):
        raise HTTPException(status_code=404, detail="Review not found")

    save_to_gcs("reviews.json", new_reviews)
    return {"message": "리뷰 삭제 완료"}


@app.delete("/movies/{movie_id}")
def delete_movie(movie_id: int):
    # 1) 영화 삭제
    movies = load_from_gcs("movies.json")
    new_movies = [m for m in movies if m.get("id") != movie_id]

    if len(new_movies) == len(movies):
        raise HTTPException(status_code=404, detail="Movie not found")

    save_to_gcs("movies.json", new_movies)

    # 2) 해당 영화의 리뷰도 함께 삭제
    all_reviews = load_from_gcs("reviews.json")
    new_reviews = [r for r in all_reviews if r.get("movie_id") != movie_id]
    save_to_gcs("reviews.json", new_reviews)

    return {"message": "영화 및 해당 리뷰 삭제 완료"}

