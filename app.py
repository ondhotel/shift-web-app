import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime
import urllib.parse

# ==========================================
# 1. 設定（あなたの情報に書き換え）
# ==========================================
SPREADSHEET_ID = "1BE8rI5_Em5xe8eAMhpdzG6AvMSwEcMGv-qKdrrpZd08"
GAS_URL = "https://script.google.com/macros/s/AKfycbz-Kay6gzHiTduLJONn8QPp3hIdj0M_AiAc_5XTJQzEJmde8MTL0Z4ul0yjJEx4dDgbRg/exec"

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
        staff_list = master_df['従業員リスト'].dropna().unique().tolist()
        dept_list = master_df['部門リスト'].dropna().unique().tolist()
        return staff_list, dept_list
    except:
        return ["エラー"], ["エラー"]

# ==========================================
# 3. サイドバー：マスター管理（追加・削除）
# ==========================================
st.sidebar.title("🛠 管理パネル")
STAFF_MASTER, DEPT_MASTER = load_masters()

# --- 従業員管理 ---
with st.sidebar.expander("👤 従業員の追加・削除"):
    new_staff = st.text_input("新メンバー名")
    if st.button("従業員を追加"):
        res = requests.get(GAS_URL, params={"action": "add_master", "type": "staff", "value": new_staff})
        st.cache_data.clear()
        st.rerun()
    
# --- 従業員削除ボタンの修正 ---
if st.button("選択した従業員を削除"):
    # type=staff を追加
    res = requests.get(GAS_URL, params={"action": "del_master", "type": "staff", "value": del_staff})
    st.cache_data.clear()
    st.rerun()

# --- 部門管理 ---
with st.sidebar.expander("🏢 部門の追加・削除"):
    new_dept = st.text_input("新部門名")
    if st.button("部門を追加"):
        res = requests.get(GAS_URL, params={"action": "add_master", "type": "dept", "value": new_dept})
        st.cache_data.clear()
        st.rerun()
    
# --- 部門削除ボタンの修正 ---
if st.button("選択した部門を削除"):
    # type=dept を追加
    res = requests.get(GAS_URL, params={"action": "del_master", "type": "dept", "value": del_dept})
    st.cache_data.clear()
    st.rerun()

# ==========================================
# 4. メイン画面：シフト登録
# ==========================================
st.title("職域別・時間割シフト管理")

with st.expander("📝 新しいシフトを登録する", expanded=True):
    with st.form("shift_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.selectbox("従業員名", STAFF_MASTER)
            dept = st.selectbox("部門", DEPT_MASTER)
        with col2:
            date = st.date_input("日付", datetime.now())
            t1, t2 = st.columns(2)
            start_t = t1.time_input("開始", datetime.strptime("09:00", "%H:%M"))
            end_t = t2.time_input("終了", datetime.strptime("18:00", "%H:%M"))
        
        if st.form_submit_button("保存"):
            params = {
                "action": "add_shift",
                "name": name, "dept": dept,
                "start": f"{date} {start_t}", "end": f"{date} {end_t}"
            }
            requests.get(GAS_URL, params=params)
            st.cache_data.clear()
            st.rerun()

# ==========================================
# 5. グラフ表示
# ==========================================
df = load_data()
if not df.empty:
    fig = px.timeline(df, x_start="開始", x_end="終了", y="従業員", color="部門", text="部門")
    fig.update_yaxes(autorange="reversed")
    st.plotly_chart(fig, use_container_width=True)

# CSV出力
csv = df.to_csv(index=False).encode('utf_8_sig')
st.sidebar.download_button("ToT用CSV出力", csv, "shift.csv", "text/csv")
