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
GAS_URL = "https://script.google.com/macros/s/AKfycbzBRZcKTqoigPZGJY4NvDky0mJOAwtNf4NWvF0wE7pkNVOz-QxSEaCmq0NgkordTTxLJg/exec"

st.set_page_config(layout="wide", page_title="共有シフト管理システム")

# ==========================================
# 2. データの読み込み関数
# ==========================================

# シフトデータの読み込み
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

# マスターデータ（従業員・部門）の読み込み
@st.cache_data(ttl=5)
def load_masters():
    sheet_name = urllib.parse.quote("マスター")
    url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    try:
        master_df = pd.read_csv(url)
        # 列名が存在するか確認してリスト化
        staff_list = master_df['従業員リスト'].dropna().unique().tolist() if '従業員リスト' in master_df.columns else []
        dept_list = master_df['部門リスト'].dropna().unique().tolist() if '部門リスト' in master_df.columns else []
        return staff_list, dept_list
    except:
        return ["読み込みエラー"], ["読み込みエラー"]

# ==========================================
# 3. サイドバー：マスター管理（追加・削除）
# ==========================================
st.sidebar.title("🛠 管理パネル")
STAFF_MASTER, DEPT_MASTER = load_masters()

# --- 従業員管理 ---
with st.sidebar.expander("👤 従業員の追加・削除"):
    new_staff = st.text_input("新メンバー名", key="new_staff_input")
    if st.button("従業員を追加"):
        if new_staff:
            requests.get(GAS_URL, params={"action": "add_master", "type": "staff", "value": new_staff})
            st.cache_data.clear()
            st.rerun()
    
    st.divider()
    if STAFF_MASTER:
        del_staff = st.selectbox("削除する従業員", STAFF_MASTER)
        if st.button("選択した従業員を削除"):
            requests.get(GAS_URL, params={"action": "del_master", "type": "staff", "value": del_staff})
            st.cache_data.clear()
            st.rerun()

# --- 部門管理 ---
with st.sidebar.expander("🏢 部門の追加・削除"):
    new_dept = st.text_input("新部門名", key="new_dept_input")
    if st.button("部門を追加"):
        if new_dept:
            requests.get(GAS_URL, params={"action": "add_master", "type": "dept", "value": new_dept})
            st.cache_data.clear()
            st.rerun()
    
    st.divider()
    if DEPT_MASTER:
        del_dept = st.selectbox("削除する部門", DEPT_MASTER)
        if st.button("選択した部門を削除"):
            requests.get(GAS_URL, params={"action": "del_master", "type": "dept", "value": del_dept})
            st.cache_data.clear()
            st.rerun()

# --- その他設定 ---
if st.sidebar.button("🔄 画面を強制更新"):
    st.cache_data.clear()
    st.rerun()

# ==========================================
# 4. メイン画面：シフト登録
# ==========================================
st.title("職域別・時間割シフト管理")

with st.expander("📝 新しいシフトを登録する", expanded=True):
    with st.form("shift_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.selectbox("従業員名", STAFF_MASTER if STAFF_MASTER else ["未登録"])
            dept = st.selectbox("部門", DEPT_MASTER if DEPT_MASTER else ["未登録"])
        with col2:
            date = st.date_input("日付", datetime.now())
            t1, t2 = st.columns(2)
            start_t = t1.time_input("開始", datetime.strptime("09:00", "%H:%M"))
            end_t = t2.time_input("終了", datetime.strptime("18:00", "%H:%M"))
        
        if st.form_submit_button("スプレッドシートに保存"):
            if name == "未登録" or dept == "未登録":
                st.error("先に左の管理パネルから従業員と部門を登録してください。")
            elif start_t >= end_t:
                st.error("終了時間は開始時間より後に設定してください。")
            else:
                params = {
                    "action": "add_shift",
                    "name": name,
                    "dept": dept,
                    "start": f"{date} {start_t}",
                    "end": f"{date} {end_t}"
                }
                requests.get(GAS_URL, params=params)
                st.success(f"保存しました: {name} ({start_t}〜{end_t})")
                st.cache_data.clear()
                st.rerun()

# ==========================================
# 5. グラフ（タイムライン）表示
# ==========================================
st.divider()
df = load_data()

if not df.empty:
    st.subheader("📊 シフト配置図")
    
    # 【解決策】表示用のラベルを作る
    # 同じ人でも、部門が違えば別の行に見えるように「名前 (部門)」という列を作ります
    display_df = df.copy()
    display_df['表示ラベル'] = display_df['従業員'] + " (" + display_df['部門'] + ")"
    
    # 時間順・名前順に並び替え
    display_df = display_df.sort_values(by=["従業員", "開始"])

    fig = px.timeline(
        display_df, 
        x_start="開始", 
        x_end="終了", 
        y="表示ラベル",  # 縦軸を「名前(部門)」にする
        color="部門", 
        text="部門",
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    
    # レイアウトの調整
    fig.update_layout(
        xaxis_title="時間", 
        yaxis_title="スタッフ (担当)", 
        height=len(display_df) * 40 + 100, # 人数に合わせてグラフの高さを自動調整
        showlegend=True,
        xaxis=dict(
            tickformat="%H:%M",  # 24時間表示
            dtick=3600000 * 1    # 1時間刻みにメモリを振る
        )
    )
    
    # 見やすく調整（上から順）
    fig.update_yaxes(autorange="reversed", type='category')
    
    st.plotly_chart(fig, use_container_width=True)

    # --- CSVダウンロード機能 ---
    csv = df.to_csv(index=False).encode('utf_8_sig')
    st.sidebar.download_button(
        label="📥 CSVダウンロード",
        data=csv,
        file_name=f"shift_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
    )


else:
    st.info("登録されているシフトデータがありません。")
