import streamlit as st # フロントエンドを扱うstreamlitの機能をインポート
from openai import OpenAI # openAIのchatGPTのAIを活用するための機能をインポート


# アクセスの為のキーをos.environ["OPENAI_API_KEY"]に代入し、設定

import os # OSが持つ環境変数OPENAI_API_KEYにAPIを入力するためにosにアクセスするためのライブラリをインポート
# ここにご自身のAPIキーを入力してください！
API_KEY = st.secrets["OPENAI_API_KEY"]

# openAIの機能をclientに代入
client = OpenAI(api_key=API_KEY)

# chatGPTにリクエストするためのメソッドを設定。引数には書いてほしい内容と文章のテイストと最大文字数を指定
def run_gpt(content_text_to_gpt):
    # リクエスト内容を決める
    request_to_gpt = content_text_to_gpt + "そんな時のおすすめの映画を教えてください。おすすめの映画はTMDBの映画IDで返してください。"
    
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

st.write('おすすめ映画アプリ')# タイトル

# 書かせたい内容
content_text_to_gpt = st.text_input("今日の気分を入力してください！")

#output_content_text = run_gpt(content_text_to_gpt)
#st.write(output_content_text)

# ボタンがクリックされた場合のみ GPT を実行
if st.button("おすすめの映画を教えて！"):
    if content_text_to_gpt:
        output_content_text = run_gpt(content_text_to_gpt)
        st.write(output_content_text)
    else:
        st.write("気分を入力してください！")