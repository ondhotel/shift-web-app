import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime
import urllib.parse

# ==========================================
# 1. 設定
# ==========================================
SPREADSHEET_ID = "1BE8rI5_Em5xe8eAMhpdzG6AvMSwEcMGv-qKdrrpZd08"
GAS_URL = "https://script.google.com/macros/s/AKfycbzBRZcKTqoigPZGJY4NvDky0mJOAwtNf4NWvF0wE7pkNVOz-QxSEaCmq0NgkordTTxLJg/exec"

st.set_page_config(layout="wide", page_title="共有シフト管理システム")

# ==========================================
# 2. データの読み込み関数
# ==========================================
@st.cache_data(ttl=5)
def load_data():
    sheet_name = urllib.parse.quote("シフトデータ")
    url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    try:
        df = pd.read_csv(url)
        df['開始'] = pd.to_datetime(df['開始'], errors='coerce')
        df['終了'] = pd.to_datetime(df['終了'], errors='coerce')
        return df.dropna(subset=['開始', '終了'])
    except:
        return pd.DataFrame(columns=["従業員", "部門", "開始", "終了"])

@st.cache_data(ttl=5)
def load_masters():
    sheet_name = urllib.parse.quote("マスター")
    url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    try:
        master_df = pd.read_csv(url)
        staff = master_df['従業員リスト'].dropna().unique().tolist() if '従業員リスト' in master_df.columns else []
        dept = master_df['部門リスト'].dropna().unique().tolist() if '部門リスト' in master_df.columns else []
        return staff, dept
    except:
        return [], []

# データ読み込み
STAFF_MASTER, DEPT_MASTER = load_masters()
df = load_data()

# ==========================================
# 3. メイン画面（登録）
# ==========================================
st.title("職域別・時間割シフト管理")

with st.expander("📝 新しいシフトを登録する", expanded=True):
    with st.form("shift_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.selectbox("従業員名", STAFF_MASTER if STAFF_MASTER else ["未登録"])
            dept = st.selectbox("部門", DEPT_MASTER if DEPT_MASTER else ["未登録"])
        with col2:
            date = st.date_input("日付", datetime.now())
            t1, t2 = st.columns(2)
            start_t = t1.time_input("開始", datetime.strptime("09:00", "%H:%M"))
            end_t = t2.time_input("終了", datetime.strptime("18:00", "%
