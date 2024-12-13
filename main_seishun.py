import streamlit as st # フロントエンドを扱うstreamlitの機能をインポート
from openai import OpenAI # openAIのchatGPTのAIを活用するための機能をインポート
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
st.sidebar.title(':rainbow[_映画提案アプリ_]')

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
text_input1 = st.sidebar.text_input('誰と映画を見るの？')

text_input2 = st.sidebar.text_input(
    "今の気分は？",
    "",
)
text_area = st.sidebar.text_area(
    "映画を見てどんな気分になりたい？",
    "",
)

#KJ追記
# 全ての入力値をまとめて1つの変数に格納
content_text_to_gpt =(
    f"私は{option_selectbox}の{option_radio}です。今日は{text_input1}と映画を見ようとしています。\n"
    f"今の気分は{text_input2}です。\n"
    f"映画をみてどんな気分になりたいかと言われれば、{text_area}です。そんな私におすすめの映画を教えてください。\n"
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
# APIキーを指定
api_key = "054f72271ae8d8ea2beea5ae520ca6d2"

# Streamlitアプリの構成（もっちゃんコードと重複のためコメントアウト by KJ）
#st.title("映画情報検索アプリ")
#st.write("映画のタイトルを入力して、詳細情報を取得してください。")

# ユーザーが映画タイトルを入力（KJコードから引き渡すため、コメントアウト by KJ）
#movie_title = st.text_input("") #説明なくてもよさそうなので空欄

# full_image_url を初期化（初期化しないとエラーとなったので初期化処理を入れた by KJ）
full_image_url = None

movie_title = output_content_text
#ユーザー入力前、APIリクエストをスキップするように条件分岐を追加
if movie_title:
    title = movie_title

    # APIのURLを生成
    search_url = "https://api.themoviedb.org/3/search/movie"
    search_params = {
        "api_key": api_key,
        "query": title,
        "include_adult": "false",
        "language": "ja",
    }

    # APIを呼び出す(映画ID取得用)
    search_response = requests.get(search_url, params=search_params)
    if search_response.status_code == 200:
        search_data = search_response.json()

        # タイトルの類似度を評価して最も近い映画を選択
        def get_title_similarity(s1, s2):
            return difflib.SequenceMatcher(None, s1.lower(), s2.lower()).ratio()

        most_similar_movie = max(
            search_data["results"],
            key=lambda movie: get_title_similarity(movie["title"], title)
        )
        movie_id = most_similar_movie["id"]

        # 映画詳細情報の取得
        detail_url = f"https://api.themoviedb.org/3/movie/{movie_id}"
        detail_params = {"api_key": api_key, "language": "ja"}
        detail_response = requests.get(detail_url, params=detail_params)
        if detail_response.status_code == 200:
            detail_data = detail_response.json()
            
              # ポスター情報の取得
            images_url = f"https://api.themoviedb.org/3/movie/{movie_id}/images"
            poster_size = "w300" 

            images_params = {
                "api_key": api_key, 
                "include_image_language": "ja",
            }   
            images_response = requests.get(images_url, images_params)
            if images_response.status_code == 200:
                images_data = images_response.json()
                posters = images_data.get("posters", [])
                if posters:
                    file_path = posters[0].get("file_path")
                    full_image_url = f"https://image.tmdb.org/t/p/{poster_size}{file_path}"  # フルURLを構築st.write("### 映画情報")
                    
            #映画情報とポスターを表示
            st.subheader(f"{detail_data['title']} ({detail_data['original_title']})")
            if full_image_url:
                st.image(full_image_url)
            st.write(f" {detail_data.get('overview', 'N/A')}")
            st.write(f"**公開日**: {detail_data.get('release_date', 'N/A')}")
            st.write(f"**上映時間**: {detail_data.get('runtime', 'N/A')} 分")
            st.write(f"**評価スコア** :{detail_data.get('vote_average', 'N/A')} /10")
            st.write(f"**評価数** :{detail_data.get('vote_count', 'N/A')} 件")


            
        # 製作者、キャスト情報の取得
        credits_url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits"
        credits_params = {"api_key": api_key, "language": "ja"}
        credits_response = requests.get(credits_url, params=credits_params)
        if credits_response.status_code == 200:
            credits_data = credits_response.json()
            
            st.write("### 製作者情報")
            crew = credits_data.get("crew", []) 
            filtered_roles = ["Director", "Screenplay", "Producer", "Writer", "Composer"]
            filtered_crew = [
            member for member in crew if member.get("job") in filtered_roles
            ]
            for member in filtered_crew[:5]:  # 上位5人まで
                name = member.get("name", "N/A")
                job = member.get("job", "N/A")
                st.write(f"- {job}:{name}")

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

    else:
        st.write("映画情報の取得に失敗しました。")
   
    #　レビュー情報の取得
    reviews_url = f"https://api.themoviedb.org/3/movie/{movie_id}/reviews"
    reviews_params = {
        "api_key": api_key, 
        "language": "en-US",
    }    
    
    reviews_response = requests.get(reviews_url, params= reviews_params)

    reviews_data = reviews_response.json()
    reviews = reviews_data.get("results",[])
    if reviews:
        st.write("### レビュー")
        for review in reviews[:3]: 
            author = review.get("author", "Unknown")
            content = review.get("content", "No content")
            st.write(f"**Reviewer :  {author}さんのレビュー**")
            st.write(f"Review :  {content}\n")
    else:
        st.write("None")
else:
    st.write("") #説明なくてもよさそうなので空欄
    
##最後に変数を初期化（by KJ）
output_content_text = ""
search_response = ""
detail_response = ""
credits_response = ""
reviews_data = ""

