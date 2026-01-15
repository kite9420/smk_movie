import streamlit as st
from fastapi import FastAPI
import requests
from PIL import Image
from datetime import date
import subprocess
import time
import os


#구현 예정 기능
# 프론트엔드 : streamlit
##영화 목록 표시 (제목, 포스터 이미지, 평균 평점 표시)
##영화 추가 (제목, 포스터이미지 URL, 개봉일, 감독, 장르 입력)

# 백엔드 : FastAPI
#영화 관리 (등록: 제목, 개봉일, 감독, 장르, 포스터 URL (나무위키 에서), 전체/특정 영화 조회, 삭제)
#모든 데이터는 백엔드에서 관리

#해당 py파일은 프론트엔드와 백엔드 코드가 분리되어야 하므로, 프론트엔드 코드만 작성된 상태입니다

#메인은 영화 목록을 표시하고, 사이드바에 영화 추가 등 기능 구현 예정

# 사이드바의 영화 추가 기능 구현
# 사이드 바에서 영화 추가 하기를 누르면 메인 화면에서 영화 추가 폼이 나타나도록 구현
# import requests  # FastAPI 사용할 때 활성화


#구현한 기능 : 로컬 session_state상에 캐싱하여 속도를 최적화
#중간에 Fast_api 서버가 꺼지더라도 현재 캐싱이 사라지지 않도록 구현


# =========================
# 백엔드 서버 자동 실행 로직
# =========================
@st.cache_resource # 앱이 실행될 때 딱 한 번만 실행되도록 캐싱
def start_backend():
    # 백엔드 파일 경로 (프로젝트 구조에 따라 "backend/main.py" 등으로 수정 필요)
    backend_path = "backend/main_gcp.py" 
    
    if os.path.exists(backend_path):
        # uvicorn을 백그라운드 프로세스로 실행
        proc = subprocess.Popen(
            ["uvicorn", "backend.main_gcp:app", "--host", "0.0.0.0", "--port", "8000"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        # 서버가 완전히 뜰 때까지 잠시 대기
        time.sleep(5)
        return proc
    return None

# 서버 시작
backend_process = start_backend()


st.set_page_config(layout="wide", page_title="스프린트 미션 18 영화 평점 사이트")
st.title("🎬 영화 평점")


# =========================
# FastAPI 연동 함수
# =========================

BASE_API_URL = "http://127.0.0.1:8000/" #로컬과 다른 차이점

def get_reviews_api(movie_id):
    try:
        response = requests.get(f"{BASE_API_URL}movies/{movie_id}/reviews", timeout=3)
        return response.json() if response.status_code == 200 else []
    except:
        return []
    
    
def save_movie_api(movie):
    try:
        response = requests.post(f"{BASE_API_URL}movies", json=movie, timeout=3)
        return response.status_code == 200
    except:
        return False

def get_movies_api():
    try:
        response = requests.get(f"{BASE_API_URL}/movies",timeout=3)
        if response.status_code == 200:
            return response.json()
        return []
    except requests.exceptions.RequestException:
        # FastAPI가 꺼져 있거나 네트워크 오류
        return None
    
def save_review_api(movie_id, author, content, score):
    review_data = {
        "movie_id": movie_id, # 여기서 영화 ID를 할당!
        "author": author,
        "content": content,
        "score": score
    }
    # POST로 백엔드 /reviews에 저장
    requests.post(f"{BASE_API_URL}reviews", json=review_data)


# =========================
# 상태 변수 초기화
# =========================
if "show_add_form" not in st.session_state:
    st.session_state.show_add_form = False

if "show_add_review" not in st.session_state:
    st.session_state.show_add_review = {}

if "movies" not in st.session_state:
    st.session_state.movies = get_movies_api() or []

# =========================
# 사이드바
# =========================
st.sidebar.title("영화 관리")

# 토글 버튼
if st.sidebar.button("영화 추가"):
    st.session_state.show_add_form = not st.session_state.show_add_form
    st.rerun()


if st.sidebar.button("새로고침"):
    movies = get_movies_api()
    if movies is not None:
        st.session_state.movies = movies

# =========================
# 메인 - 영화 추가 폼
# =========================
if st.session_state.show_add_form:
    st.subheader("영화 추가")

    movie_title = st.text_input("영화 제목")
    movie_poster_url = st.text_input("포스터 이미지 URL")
    movie_release_date = st.date_input("개봉일", value=date.today())
    movie_director = st.text_input("감독")
    movie_genre = st.text_input("장르")

    if st.button("저장"):
        if movie_title and movie_poster_url and movie_director and movie_genre:
            movie = {
                "id": len(st.session_state.movies) + 1,
                "title": movie_title,
                "poster_url": movie_poster_url,
                "release_date": str(movie_release_date),
                "director": movie_director,
                "genre": movie_genre
            }

            success = save_movie_api(movie)
            if not success:
                st.error("서버 저장 실패")
                st.stop()

            st.success("영화가 저장되었습니다.")

            # 저장 후 창 닫기, 저장 성공 후에만 서버와 동기화
            st.session_state.movies = get_movies_api()

            st.session_state.show_add_form = False
            st.rerun()
        else:
            st.warning("모든 항목을 입력하세요.")

# =========================
# 메인 - 영화 목록
# =========================
st.subheader("영화 목록")
movies = st.session_state.movies

if not movies:
    st.info("등록된 영화가 없습니다.")
else:
    for movie in movies:
        key = f"review_open_{movie['id']}"
        if key not in st.session_state:
            st.session_state[key] = False
        
        col1, col2 = st.columns([1, 3])

        with col1:
            st.image(movie["poster_url"], width=150)

        with col2:
            st.markdown(f"**제목:** {movie['title']}")
            st.markdown(f"개봉일: {movie['release_date']}")
            st.markdown(f"감독: {movie['director']}")
            st.markdown(f"장르: {movie['genre']}")

            btn_col1, btn_col2, btn_col3, _ = st.columns([1, 1, 1, 12]) 

            with btn_col1:
                if st.button("리뷰 보기", key=f"view_{movie['id']}"):
                    st.session_state[key] = not st.session_state[key]
                    
                    review_storage_key = f"reviews_{movie['id']}"
                    #보관함에 없을 때만 API를 호출
                    if review_storage_key not in st.session_state:
                        st.session_state[review_storage_key] = get_reviews_api(movie['id'])

            with btn_col2:
                add_review_key = f"add_review_open_{movie['id']}"
                if add_review_key not in st.session_state:
                    st.session_state[add_review_key] = False

                if st.button("리뷰 추가", key=f"btn_add_{movie['id']}"):
                    st.session_state[add_review_key] = not st.session_state[add_review_key]

            # --- 리뷰 추가 입력 폼 ---
            if st.session_state[add_review_key]:
                with st.container():
                    st.write(f"--- {movie['title']} 리뷰 작성 ---")
                    author = st.text_input("작성자", key=f"auth_{movie['id']}")
                    content = st.text_area("내용", key=f"cont_{movie['id']}")

                    st.write("평점")
                    score_index = st.feedback("stars", key=f"score_{movie['id']}")
                    score = (score_index + 1) if score_index is not None else 5 # 기본값 5점
                    
                    if st.button("리뷰 저장", key=f"save_rev_{movie['id']}"):
                        if author and content and score:
                            # 1. API 호출 (사용자님이 만든 save_review_api 사용)
                            save_review_api(movie['id'], author, content, score)
                            
                            # 2. 세션 스테이트의 해당 영화 리뷰 목록 즉시 갱신 (캐싱 업데이트)
                            st.session_state[f"reviews_{movie['id']}"] = get_reviews_api(movie['id'])
                            
                            # 3. 입력 칸 닫기 및 알림
                            st.session_state[add_review_key] = False
                            st.success("리뷰가 등록되었습니다!")
                            st.rerun()
                        else:
                            st.warning("작성자와 내용, 평점을 모두 입력해주세요.")
            with btn_col3:
                # 개별 영화의 리뷰를 강제로 다시 불러오는 갱신 버튼입니다.
                if st.button("🔄 갱신", key=f"refresh_{movie['id']}"):
                    # 보관함을 최신 API 결과로 덮어씌웁니다.
                    st.session_state[f"reviews_{movie['id']}"] = get_reviews_api(movie['id'])
                    st.toast(f"'{movie['title']}' 리뷰 갱신 완료!") # 갱신 알림 (선택 사항)
              
            if st.session_state[key]:
                st.subheader("영화 리뷰")
                current_reviews = st.session_state.get(f"reviews_{movie['id']}", [])
                if not current_reviews:
                    st.info("등록된 리뷰가 없습니다")
                else:
                    for review in current_reviews:
                        st.markdown(f"**작성자:** {review['author']}")
                        st.markdown(f"**내용:** {review['content']}")
                        st.markdown(f"**평점:** ⭐ {review['score']}")
                        st.divider()




                    
