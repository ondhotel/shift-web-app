import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime

# --- 設定（あなたの情報に書き換えてください） ---
SPREADSHEET_ID = "1BE8rI5_Em5xe8eAMhpdzG6AvMSwEcMGv-qKdrrpZd08"
GAS_URL = "https://script.google.com/macros/s/AKfycbxpJ_yQ84FozwUVhNH4lMCtwTkyrHA8txwCqiG5zFTabjNy2CQzSab7u65dHBqqtmeUXA/exec"

st.set_page_config(layout="wide", page_title="共有シフト管理")

# スプシから読み込み
@st.cache_data(ttl=5)
def load_data():
    url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv"
    df = pd.read_csv(url)
    df['開始'] = pd.to_datetime(df['開始'])
    df['終了'] = pd.to_datetime(df['終了'])
    return df

st.title("職域別・時間割シフト管理システム")

# シフト入力フォーム
with st.expander("➕ 新しいシフトを登録する"):
    with st.form("input_form"):
        name = st.text_input("従業員名")
        dept = st.selectbox("部門", ["レジ", "品出し", "キッチン", "休憩"])
        date = st.date_input("日付", datetime.now())
        start_t = st.time_input("開始", datetime.strptime("09:00", "%H:%M"))
        end_t = st.time_input("終了", datetime.strptime("18:00", "%H:%M"))
        
        if st.form_submit_button("保存"):
            start_dt = f"{date} {start_t}"
            end_dt = f"{date} {end_t}"
            res = requests.get(GAS_URL, params={"name":name, "dept":dept, "start":start_dt, "end":end_dt})
            if res.text == "Success":
                st.success("保存完了！")
                st.cache_data.clear()
                st.rerun()

# タイムライン表示
df = load_data()
if not df.empty:
    fig = px.timeline(df, x_start="開始", x_end="終了", y="従業員", color="部門", text="部門")
    fig.update_yaxes(autorange="reversed")
    st.plotly_chart(fig, use_container_width=True)



# --- 6. TouchOnTime (ToT) 連携用CSV出力 ---
st.divider()
st.subheader("📥 勤怠システム連携")

if not df.empty:
    # ToTのインポート形式に合わせてデータを整形（例：従業員コード, 日付, 開始時刻, 終了時刻...）
    # ここでは簡易的に現在のデータをCSV化しますが、ToTの仕様に合わせて列名を変更可能です
    tot_df = df.copy()
    
    # 時間の表示をToTが読み込みやすい "HH:mm" 形式に整える
    tot_df['開始時刻'] = tot_df['開始'].dt.strftime('%H:%M')
    tot_df['終了時刻'] = tot_df['終了'].dt.strftime('%H:%M')
    tot_df['日付'] = tot_df['開始'].dt.strftime('%Y/%m/%d')
    
    # 必要な列だけを抽出（ToTの並び順に合わせる）
    output_df = tot_df[['従業員', '日付', '開始時刻', '終了時刻', '部門']]

    # CSVボタンの設置
    csv = output_df.to_csv(index=False).encode('utf_8_sig')
    st.download_button(
        label="TouchOnTime用CSVをダウンロード",
        data=csv,
        file_name=f"tot_shift_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
    )
else:
    st.write("データがないためCSVは作成できません。")
