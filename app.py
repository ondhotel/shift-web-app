import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime

# ==========================================
# 1. 設定
# ==========================================
SPREADSHEET_ID = "1BE8rI5_Em5xe8eAMhpdzG6AvMSwEcMGv-qKdrrpZd08"
GAS_URL = "https://script.google.com/macros/s/AKfycbxpJ_yQ84FozwUVhNH4lMCtwTkyrHA8txwCqiG5zFTabjNy2CQzSab7u65dHBqqtmeUXA/exec"

st.set_page_config(layout="wide", page_title="共有シフト管理システム")

# ==========================================
# 2. データの読み込み関数
# ==========================================

# シフトデータの読み込み
@st.cache_data(ttl=5)
def load_data():
    url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet=シフトデータ"
    try:
        df = pd.read_csv(url)
        df['開始'] = pd.to_datetime(df['開始'], errors='coerce')
        df['終了'] = pd.to_datetime(df['終了'], errors='coerce')
        return df.dropna(subset=['開始', '終了'])
    except:
        return pd.DataFrame(columns=["従業員", "部門", "開始", "終了"])

# マスターデータ（従業員・部門）の読み込み
@st.cache_data(ttl=60) # マスターは頻繁に変わらないので1分間キャッシュ
def load_masters():
    url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet=マスター"
    try:
        master_df = pd.read_csv(url)
        st.write("デバッグ用（列名）:", master_df.columns.tolist()) # これを足すと列名が見える
        staff_list = master_df['従業員リスト'].dropna().tolist()
        dept_list = master_df['部門リスト'].dropna().tolist()
        return staff_list, dept_list
    except Exception as e:
        st.error(f"詳細なエラー: {e}") # ここで何がダメか教えてくれます
        return ["エラー"], ["エラー"]

# ==========================================
# 3. メイン画面
# ==========================================
st.title("☁️ 職域別・時間割シフト管理")

# マスターデータの取得
STAFF_MASTER, DEPT_MASTER = load_masters()

with st.expander("📝 新しいシフトを登録する", expanded=True):
    with st.form("input_form", clear_on_submit=False):
        col1, col2 = st.columns(2)
        
        with col1:
            # スプシから読み込んだリストを選択肢に表示
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
                params = {"name": name, "dept": dept, "start": start_dt, "end": end_dt}
                res = requests.get(GAS_URL, params=params)
                if res.text == "Success":
                    st.success(f"✅ 保存完了！ {name}")
                    st.cache_data.clear()
                    st.rerun()

# --- グラフ表示 ---
st.divider()
df = load_data()
if not df.empty:
    fig = px.timeline(df, x_start="開始", x_end="終了", y="従業員", color="部門", text="部門",
                     color_discrete_sequence=px.colors.qualitative.Pastel)
    fig.update_yaxes(autorange="reversed")
    st.plotly_chart(fig, use_container_width=True)

# --- 管理機能（サイドバー） ---
if st.sidebar.button("マスターデータを再読込"):
    st.cache_data.clear()
    st.rerun()
