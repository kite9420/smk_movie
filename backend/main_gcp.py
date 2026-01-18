from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import Request
from pydantic import BaseModel
from google.cloud import storage
from typing import List
import json



# 비밀번호 설정을 위한 기능 추가
import hashlib, hmac, secrets


app = FastAPI()
ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", "")  # Cloud Run env로 설정

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



#영화마다 salt 와 hash를 추가
@app.post("/movies")
def add_movie(movie: dict):
    movies = load_from_gcs("movies.json")

    # 필수: author, password 받기
    pw = movie["password"]
    pw_rec = make_pw_record(pw)

    next_id = (max([m.get("id", 0) for m in movies]) + 1) if movies else 1

    movie_obj = {
        "id": next_id,
        "title": movie["title"],
        "poster_url": movie["poster_url"],
        "release_date": movie["release_date"],
        "director": movie["director"],
        "genre": movie["genre"],
        "author": movie["author"],
        "pw_salt": pw_rec["salt"],
        "pw_hash": pw_rec["hash"],
    }

    movies.append(movie_obj)
    save_to_gcs("movies.json", movies)
    return {"message": "영화 등록 완료", "id": next_id}




@app.get("/movies/{movie_id}/reviews", response_model=List[Review])
def get_reviews(movie_id: int):
    all_reviews = load_from_gcs("reviews.json")
    return [r for r in all_reviews if r["movie_id"] == movie_id]


#게시글마다 salt 와 hash를 추가
@app.post("/reviews")
def add_review(review: dict):
    all_reviews = load_from_gcs("reviews.json")

    pw = review["password"]
    pw_rec = make_pw_record(pw)

    next_id = (max([r.get("id", 0) for r in all_reviews]) + 1) if all_reviews else 1

    review_obj = {
        "id": next_id,
        "movie_id": review["movie_id"],
        "author": review["author"],
        "content": review["content"],
        "score": review["score"],
        "pw_salt": pw_rec["salt"],
        "pw_hash": pw_rec["hash"],
    }

    all_reviews.append(review_obj)
    save_to_gcs("reviews.json", all_reviews)
    return {"message": "리뷰 등록 완료", "id": next_id}




@app.delete("/reviews/{review_id}")
def delete_review(review_id: int, request: Request, body: dict = None):
    all_reviews = load_from_gcs("reviews.json")

    target = next((r for r in all_reviews if r.get("id") == review_id), None)
    if not target:
        raise HTTPException(status_code=404, detail="Review not found")

    if not is_admin(request):
        if not body or "password" not in body:
            raise HTTPException(status_code=400, detail="Password required")
        if not verify_password(body["password"], target["pw_salt"], target["pw_hash"]):
            raise HTTPException(status_code=403, detail="Wrong password")

    new_reviews = [r for r in all_reviews if r.get("id") != review_id]
    save_to_gcs("reviews.json", new_reviews)
    return {"message": "리뷰 삭제 완료"}


@app.delete("/movies/{movie_id}")
def delete_movie(movie_id: int, request: Request, body: dict = None):
    movies = load_from_gcs("movies.json")

    target = next((m for m in movies if m.get("id") == movie_id), None)
    if not target:
        raise HTTPException(status_code=404, detail="Movie not found")

    if not is_admin(request):
        if not body or "password" not in body:
            raise HTTPException(status_code=400, detail="Password required")
        if not verify_password(body["password"], target["pw_salt"], target["pw_hash"]):
            raise HTTPException(status_code=403, detail="Wrong password")

    new_movies = [m for m in movies if m.get("id") != movie_id]
    save_to_gcs("movies.json", new_movies)

    all_reviews = load_from_gcs("reviews.json")
    new_reviews = [r for r in all_reviews if r.get("movie_id") != movie_id]
    save_to_gcs("reviews.json", new_reviews)

    return {"message": "영화 및 해당 리뷰 삭제 완료"}



#비밀번호 관련 함수

# 평문 비밀번호를 PBKDF2-HMAC-SHA256 방식으로 해싱 / 알고리즘 sha256 / pw 사용자 비밀번호 / salt 무작위 문자열 / 12만회 반복 해싱
def hash_password(pw: str, salt: str) -> str:
    dk = hashlib.pbkdf2_hmac("sha256", pw.encode("utf-8"), salt.encode("utf-8"), 120_000)
    return dk.hex()

# 비밀번호 저장용 레코드 생성
def make_pw_record(pw: str) -> dict:
    salt = secrets.token_hex(16)
    return {"salt": salt, "hash": hash_password(pw, salt)}

# 비밀번호 검증
def verify_password(pw: str, salt: str, pw_hash: str) -> bool:
    return hmac.compare_digest(hash_password(pw, salt), pw_hash)

def is_admin(request) -> bool:
    if not ADMIN_TOKEN:
        return False
    return request.headers.get("X-Admin-Token", "") == ADMIN_TOKEN