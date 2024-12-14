import requests
import streamlit as st
import sqlite3
from datetime import date
import difflib

# TMDBのAPIキーをStreamlitのsecretsから取得
api_key = "054f72271ae8d8ea2beea5ae520ca6d2"

# データベース接続設定
conn = sqlite3.connect("database.db")
cur = conn.cursor()

# テーブルの作成
cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    movie_day TEXT,
    name TEXT,
    release_date TEXT,
    Director TEXT,
    hyouka TEXT,
    comment TEXT
)
""")
conn.commit()

# StreamlitアプリのUI
st.title("映画情報管理アプリ")

# 映画タイトル入力欄
movie_title = st.text_input("映画のタイトルを入力してください", placeholder="例）トップガン")

if movie_title:
    # TMDB APIで映画を検索
    search_url = "https://api.themoviedb.org/3/search/movie"
    search_params = {
        "api_key": api_key,
        "query": movie_title,
        "include_adult": "false",
        "language": "ja",
    }

    search_response = requests.get(search_url, params=search_params)
    if search_response.status_code == 200:
        search_data = search_response.json()

        # タイトルの類似度を評価して最も近い映画を選択
        def get_title_similarity(s1, s2):
            return difflib.SequenceMatcher(None, s1.lower(), s2.lower()).ratio()

        most_similar_movie = max(
            search_data["results"],
            key=lambda movie: get_title_similarity(movie["title"], movie_title)
        )
        movie_id = most_similar_movie["id"]

        # 映画詳細情報の取得
        detail_url = f"https://api.themoviedb.org/3/movie/{movie_id}"
        detail_params = {"api_key": api_key, "language": "ja"}
        detail_response = requests.get(detail_url, params=detail_params)
        if detail_response.status_code == 200:
            detail_data = detail_response.json()
            title = detail_data['title']
            release_date = detail_data.get('release_date', 'N/A')
            director_name = None

            # 製作者情報の取得
            credits_url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits"
            credits_params = {"api_key": api_key, "language": "ja"}
            credits_response = requests.get(credits_url, params=credits_params)
            if credits_response.status_code == 200:
                credits_data = credits_response.json()
                crew = credits_data.get("crew", [])
                directors = [member for member in crew if member.get("job") == "Director"]
                if directors:
                    director_name = directors[0].get("name", "N/A")

            # 映画情報表示
            st.subheader(f"{title} ({detail_data['original_title']})")
            
            # ポスター画像表示
            poster_path = detail_data.get("poster_path", None)
            if poster_path:
                poster_url = f"https://image.tmdb.org/t/p/w300{poster_path}"
                st.image(poster_url, caption="Movie Poster")    
                        

            st.write(f"**概要**: {detail_data.get('overview', 'N/A')}")

            st.write(f"**公開日**: {release_date}")
            st.write(f"**監督**: {director_name or 'N/A'}")
            st.write(f"**上映時間**: {detail_data.get('runtime', 'N/A')} 分")
            st.write(f"**評価スコア** :{detail_data.get('vote_average', 'N/A')} /10")
            st.write(f"**評価数** :{detail_data.get('vote_count', 'N/A')} 件")
            
            st.write("### キャスト情報")
            cast = credits_data.get("cast", [])
            for actor in cast[:5]:
                name = actor.get("name", "N/A")
                character = actor.get("character", "N/A")
                profile_path = actor.get("profile_path", None)
                st.write((f"- {name} ( {character} )"))
                if profile_path:
                    profile_url = f"https://image.tmdb.org/t/p/w200{profile_path}"
                    st.image(profile_url,width=100)  
                    #画像サイズが大きかったので調整（url部分を直そうとしたらエラーとなったので、ここで調整）
                else:
                    st.write("(No image available)")

            # ユーザーが補足情報を入力
            movie_day_input = st.date_input("映画を見た日", value=date.today())
            user_rating = st.selectbox(
                "評価を選んでください",
                ["★☆☆☆☆", "★★☆☆☆", "★★★☆☆", "★★★★☆", "★★★★★"],
                index=0
            )
            user_comment = st.text_input("感想コメント", value="")

            # データベース保存ボタン
            if st.button("Add to Database"):
                cur.execute("""
                    INSERT INTO users (movie_day, name, release_date, Director, hyouka, comment)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    str(movie_day_input),
                    title,
                    release_date,
                    director_name or "N/A",
                    user_rating,
                    user_comment
                ))
                conn.commit()
                st.success(f"'{title}' がデータベースに追加されました！")



import pandas as pd

# データベース内容の表示
st.write("## 保存された映画情報")
cur.execute("SELECT * FROM users")
rows = cur.fetchall()

if rows:
    # データをDataFrameに変換（ID列を削除）
    df = pd.DataFrame(rows, columns=["ID", "映画を見た日", "映画名", "公開日", "監督", "評価", "コメント"])
    df = df.drop(columns=["ID"])  # ID列を削除

    # インデックスを1から順番に設定
    df.index = range(1, len(df) + 1)
    df.index.name = "No."  # インデックス列の名前を設定

    # Streamlitで表形式で表示
    st.dataframe(df, use_container_width=True)  # コンテナ幅に合わせて表示
else:
    st.write("データベースに保存された映画情報はありません。")


