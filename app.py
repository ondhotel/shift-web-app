import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime

# ==========================================
# 1. 設定（あなたの情報に書き換えてください）
# ==========================================
SPREADSHEET_ID = "ここにスプレッドシートのIDを貼る"
GAS_URL = "ここにGASのURLを貼る"

# マスターデータ（ここを編集すれば選択肢が変わります）
STAFF_MASTER = ["田中", "佐藤", "鈴木", "高橋", "伊藤", "山田"]
DEPT_MASTER = ["レジ", "品出し", "キッチン", "休憩", "検品", "掃除"]

st.set_page_config(layout="wide", page_title="共有シフト管理システム")

# ==========================================
# 2. データの読み込み関数
# ==========================================
@st.cache_data(ttl=5)
def load_data():
    url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv"
    try:
        df = pd.read_csv(url)
        # 時間列を変換（エラー行は除外）
        df['開始'] = pd.to_datetime(df['開始'], errors='coerce')
        df['終了'] = pd.to_datetime(df['終了'], errors='coerce')
        df = df.dropna(subset=['開始', '終了'])
        return df
    except:
        return pd.DataFrame(columns=["従業員", "部門", "開始", "終了"])

# ==========================================
# 3. メイン画面：タイトルと入力フォーム
# ==========================================
st.title("☁️ 職域別・時間割シフト管理")

# 入力フォームを広げた状態で表示
with st.expander("📝 新しいシフトを登録する", expanded=True):
    with st.form("input_form", clear_on_submit=False):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.selectbox("従業員名を選択", STAFF_MASTER)
            dept = st.selectbox("担当部門を選択", DEPT_MASTER)
        
        with col2:
            date = st.date_input("日付", datetime.now())
            t_col1, t_col2 = st.columns(2)
            with t_col1:
                start_t = st.time_input("開始", datetime.strptime("09:00", "%H:%M"))
            with t_col2:
                end_t = st.time_input("終了", datetime.strptime("18:00", "%H:%M"))
        
        submit = st.form_submit_button("スプレッドシートに保存")

        if submit:
            if start_t >= end_t:
                st.error("エラー：終了時間は開始時間より後にしてください。")
            else:
                start_dt = f"{date} {start_t}"
                end_dt = f"{date} {end_t}"
                
                # GAS経由でスプシへ送信
                params = {"name": name, "dept": dept, "start": start_dt, "end": end_dt}
                try:
                    res = requests.get(GAS_URL, params=params, timeout=10)
                    if res.text == "Success":
                        st.success(f"✅ 保存完了！ {name} : {start_t} 〜 {end_t}")
                        st.cache_data.clear()
                        # 反映のために再読み込み
                        st.rerun()
                    else:
                        st.error("保存に失敗しました。GASの設定を確認してください。")
                except Exception as e:
                    st.error(f"接続エラー: {e}")

# ==========================================
# 4. グラフ（タイムライン）表示
# ==========================================
st.divider()
df = load_data()

if not df.empty:
    st.subheader(f"📊 シフト配置図")
    
    # グラフの作成
    fig = px.timeline(
        df, 
        x_start="開始", 
        x_end="終了", 
        y="従業員", 
        color="部門",
        text="部門",
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    
    # 見やすく調整（上から名前順、24時間表示など）
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(xaxis_title="時間", yaxis_title="スタッフ")
    
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("現在、登録されているシフトはありません。上のフォームから登録してください。")

# ==========================================
# 5. TouchOnTime (ToT) 連携・管理機能
# ==========================================
st.sidebar.header("⚙️ 管理メニュー")

# 最新状態にするボタン
if st.sidebar.button("画面を更新する"):
    st.cache_data.clear()
    st.rerun()

# CSVダウンロード
if not df.empty:
    st.sidebar.subheader("📥 データ出力")
    tot_df = df.copy()
    tot_df['日付'] = tot_df['開始'].dt.strftime('%Y/%m/%d')
    tot_df['開始時刻'] = tot_df['開始'].dt.strftime('%H:%M')
    tot_df['終了時刻'] = tot_df['終了'].dt.strftime('%H:%M')
    
    output_df = tot_df[['従業員', '日付', '開始時刻', '終了時刻', '部門']]
    csv = output_df.to_csv(index=False).encode('utf_8_sig')
    
    st.sidebar.download_button(
        label="ToT用CSVをダウンロード",
        data=csv,
        file_name=f"shift_export_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
    )
