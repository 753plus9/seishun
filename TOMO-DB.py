#、「Streamlit」というPythonのライブラリを使ってSQLiteデータベースにデータを保存し、ウェブアプリとしてデータを操作する仕組みを構築する
import streamlit as st
import sqlite3
from datetime import date


# データベースへの接続（database.dbという名前のファイルに保存される。ファイルが無ければ作成される）
conn = sqlite3.connect("database.db")
cur = conn.cursor()


# userという名前のテーブルを作成。すでにテーブルが存在すれば作成されない。idは自動で増加させる。nameや評価などを保存する列をつくる
# movie_day(映画を見た日) name(映画名) release_date(公開日) Director(監督) hyouka(自分の★評価) comment（フリーコメント）
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
conn.commit() #データベースの変更を確定させるる


# StreamlitでUIを作成。タイトル作成
st.title("SQLite Write Example")


# 例の部分の色を薄くする簡単なCSS　（Placeholderとして変数設定）
st.markdown(
    """
    <style>
    input::placeholder {
        color: #d3d3d3;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# streamlitで映画名入力欄作成
name_input = st.text_input("映画名",placeholder="例）トップガン")
# streamlitで公開日入力欄作成
release_date_input = st.text_input("公開日(YYYY/MM/DD)",placeholder="例）1996/03/10") #文字列で公開日を入力
# streamlitで監督入力欄作成
Director_input = st.text_input("監督",placeholder="例）殿")
# 映画を見た日をカレンダーで選択（デフォルトは今日にして、カレンダーから選べるようにする）
movie_day_input = st.date_input("映画を見た日", value=date.today())

# ★の評価を選択する機能を作る
selected_star = st.selectbox(
    "評価を選んでください",
    ["★☆☆☆☆", "★★☆☆☆", "★★★☆☆", "★★★★☆", "★★★★★"],
    index=0  # 初期値を「1つ星」に設定
)
# 選択した★を表示
st.markdown(f"あなたの評価は: **{selected_star}** です！")


# streamlitで感想入力
comment_input = st.text_input("感想コメント",value="")


# データベースに保存　st.button("Add to Database")：ボタンをクリックすると以下の処理が実行される
# name_inputが空でない場合は入力内容を挿入（INSERT)  cur.executeはデータベースにデータを追加するSQL文
# conn.commit()はデータベースに変更を保存。成功した場合はst.success、失敗した場合はst.warningで警告を出す
if st.button("Add to Database"):
    if not name_input:
        st.warning("映画名を入力してください。")
    elif not release_date_input:
        st.warning("公開日を入力してください。")
    elif not Director_input:
        st.warning("監督名を入力してください。")
    else:
        comment = comment_input or "" # コメントが空の場合は空文字列を挿入
        
        # DBに挿入        
        cur.execute("INSERT INTO users (movie_day, name, release_date, Director, hyouka, comment) VALUES (?, ?, ?, ?, ?, ?)", 
                    (
                        str(movie_day_input), 
                        name_input, 
                        release_date_input, 
                        Director_input, 
                        selected_star, 
                        comment_input if comment_input else "", #感想コメントだけは必須ではなく任意設定
                        ),
                    )
        conn.commit()
        st.success(f"'{name_input}' was added to the database!")



# データベース内容の表示　cur.execute("SELECT * FROM users")：usersテーブルの全データを取得
# cur.fetchall()：取得したデータをリスト形式で格納。st.write(rows)：データベースに保存されているデータを画面に表示します。
st.write("## Current Database Entries")
cur.execute("SELECT * FROM users")
rows = cur.fetchall()
st.write(rows)


# 初学者向けのコア概念：
#SQLiteの基礎：テーブルの作成、データの挿入・取得。
#StreamlitのUI：テキスト入力、選択肢、ボタンなど。
#連携：入力データをデータベースに保存し、画面に結果を表示。
