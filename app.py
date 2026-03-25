import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime
import urllib.parse

# 1. 設定
SPREADSHEET_ID = "1BE8rI5_Em5xe8eAMhpdzG6AvMSwEcMGv-qKdrrpZd08"
GAS_URL = "https://script.google.com/macros/s/AKfycbzBRZcKTqoigPZGJY4NvDky0mJOAwtNf4NWvF0wE7pkNVOz-QxSEaCmq0NgkordTTxLJg/exec"

st.set_page_config(layout="wide", page_title="シフト管理")

# 2. 関数
@st.cache_data(ttl=5)
def load_data():
    s_name = urllib.parse.quote("シフトデータ")
    url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet={s_name}"
    try:
        df = pd.read_csv(url)
        df['開始'] = pd.to_datetime(df['開始'], errors='coerce')
        df['終了'] = pd.to_datetime(df['終了'], errors='coerce')
        return df.dropna(subset=['開始', '終了'])
    except:
        return pd.DataFrame(columns=["従業員", "部門", "開始", "終了"])

@st.cache_data(ttl=5)
def load_masters():
    s_name = urllib.parse.quote("マスター")
    url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet={s_name}"
    try:
        m_df = pd.read_csv(url)
        staff = m_df['従業員リスト'].dropna().unique().tolist()
        dept = m_df['部門リスト'].dropna().unique().tolist()
        return staff, dept
    except:
        return [], []

# データ取得
STAFF_MASTER, DEPT_MASTER = load_masters()
df = load_data()

# 3. 画面表示
st.title("職域別・時間割シフト管理")

with st.expander("📝 登録フォーム", expanded=True):
    with st.form("shift_form"):
        c1, c2 = st.columns(2)
        with c1:
            name = st.selectbox("名前", STAFF_MASTER if STAFF_MASTER else ["未設定"])
            dept = st.selectbox("部門", DEPT_MASTER if DEPT_MASTER else ["未設定"])
        with c2:
            date = st.date_input("日付", datetime.now())
            t1, t2 = st.columns(2)
            st_t = t1.time_input("開始", datetime.strptime("09:00", "%H:%M"))
            en_t = t2.time_input("終了", datetime.strptime("18:00", "%H:%M"))
        if st.form_submit_button("スプレッドシートに保存"):
            p = {"action":"add_shift","name":name,"dept":dept,"start":f"{date} {st_t}","end":f"{date} {en_t}"}
            requests.get(GAS_URL, params=p)
            st.cache_data.clear()
            st.rerun()

st.divider()

if not df.empty:
    st.subheader("📊 シフト配置図")
    # 開始 < 終了 のみ表示
    p_df = df[df['開始'] < df['終了']].copy()
    if not p_df.empty:
        fig = px.timeline(p_df, x_start="開始", x_end="終了", y="従業員", color="部門", text="部門")
        fig.update_yaxes(type='category', autorange="reversed")
        fig.update_layout(barmode='group', height=400 + (len(p_df['従業員'].unique()) * 40))
        st.plotly
