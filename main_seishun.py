import streamlit as st # フロントエンドを扱うstreamlitの機能をインポート
from openai import OpenAI # openAIのchatGPTのAIを活用するための機能をインポート
import sqlite3
from datetime import date
import difflib
import requests

# アクセスの為のキーをos.environ["OPENAI_API_KEY"]に代入し、設定

import os # OSが持つ環境変数OPENAI_API_KEYにAPIを入力するためにosにアクセスするためのライブラリをインポート

##API_KEYを渡す（streamlitで動かすとき）ローカルで動かす時はこちらをコメント
API_KEY = st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=API_KEY)

##API_KEYを渡す（ローカルで動かすとき）streamlitで動かす時はこちらをコメントアウト
#ターミナルでこれを実行　→ export OPENAI_API_KEY="sk-XXXXXXXXXXXX"
#API_KEY = os.getenv("OPENAI_API_KEY")
#client = OpenAI(api_key=API_KEY)

# chatGPTにリクエストするためのメソッドを設定。引数には書いてほしい内容と文章のテイストと最大文字数を指定
def run_gpt(content_text_to_gpt):
    # リクエスト内容を決める
    request_to_gpt = content_text_to_gpt
    
    # 決めた内容を元にclient.chat.completions.createでchatGPTにリクエスト。オプションとしてmodelにAIモデル、messagesに内容を指定
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": request_to_gpt },
        ],
    )

    # 返って来たレスポンスの内容はresponse.choices[0].message.content.strip()に格納されているので、これをoutput_contentに代入
    output_content = response.choices[0].message.content.strip()
    return output_content # 返って来たレスポンスの内容を返す

##もっちゃんコード
#タイトル
st.sidebar.title(':rainbow[_Seishun Cinema_]')

#アプリの説明文
st.sidebar.write('『今日映画何見る？』の提案アプリ！')
st.sidebar.write('&nbsp;','&nbsp;','以下質問に答えてね:smile:')

#質問たち
option_radio = st.sidebar.radio(
    "性別を教えて！",
    ["男性", "女性", "その他"],
)
option_selectbox = st.sidebar.selectbox(
    "年齢を教えて！",
    ("10代以下", "10代", "20代", "30代", "40代", "50代", "60代", "70代", "80代以上"),
)
text_input1 = st.sidebar.selectbox(
    "誰と映画を見るの？",
    ("お友達", "彼氏", "彼女" , "夫", "妻", "子ども", "両親", "好きな人"),
)
text_input2 = st.sidebar.selectbox(
    "今の気分は？",
    ("落ち込み気味" , "悲しい気持ち" , "不安な気持ち" ,"怒り気味" , "普通" , "楽しい気持ち" , "嬉しい気持ち" , "興奮気味", "Techモード"),
)
text_area = st.sidebar.selectbox(
    "映画を見てどんな気分になりたい？",
    ("感動したい", "温かい気持ちになりたい", "興奮したい", "恐怖に怯えたい", "熱い気持ちになりたい", "キュンキュンしたい"),
    
)

#KJ追記
# 全ての入力値をまとめて1つの変数に格納
content_text_to_gpt =(
    f"私は{option_selectbox}の{option_radio}です。今日は{text_input1}と映画を見ようとしています。\n"
    f"今の気分は{text_input2}です。\n"
    f"映画をみて{text_area}私に、おすすめの映画を教えてください。\n"
    f"回答の形式はTMDBに登録されている映画のタイトルのみでお願いします。回答は１つだけ。TMDBのIDではありません。タイトル以外の言葉は書かないでください。）\n"
)

#KJ追記
# 初期値を設定して変数を定義
output_content_text = ""

# ボタンがクリックされた場合のみ GPT を実行
if st.sidebar.button('おすすめの映画を教えて！',type="primary"):
    if content_text_to_gpt:
        output_content_text = run_gpt(content_text_to_gpt)
        st.write("おすすめの映画です！")
    else:
        st.write("気分を入力してください！")

##やまけんさんコード  
# TMDBのAPIキーをStreamlitのsecretsから取得
api_key = st.secrets["TMDB_API_KEY"]

# Streamlitアプリの構成（もっちゃんコードと重複のためコメントアウト by KJ）
#st.title("映画情報検索アプリ")
#st.write("映画のタイトルを入力して、詳細情報を取得してください。")

# ユーザーが映画タイトルを入力（KJコードから引き渡すため、コメントアウト by KJ）
#movie_title = st.text_input("") #説明なくてもよさそうなので空欄

# full_image_url を初期化（初期化しないとエラーとなったので初期化処理を入れた by KJ）
full_image_url = None

##ともさん＆やまけんさんコードマージ【開始①】
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

##ともさん＆やまけんさんコードマージ【終了①】

movie_title = output_content_text

##ともさん＆やまけんさんコードマージ【開始②】

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

##ともさん＆やまけんさんコードマージ【終了②】

    
##最後に変数を初期化（by KJ）
output_content_text = ""
search_response = ""
detail_response = ""
credits_response = ""
reviews_data = ""

