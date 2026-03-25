import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime
import urllib.parse

# カレンダーコンポーネントをインポート
from calendar_component import render_calendar_component

# ==========================================
# 1. 設定（あなたの情報に書き換え）
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
        df = pd.read_csv(url, dtype={'開始': str, '終了': str})
        df['開始'] = pd.to_datetime(df['開始'], errors='coerce')
        df['終了'] = pd.to_datetime(df['終了'], errors='coerce')
        df = df.dropna(subset=['開始', '終了'])
        df = df[df['開始'] < df['終了']]
        return df
    except Exception as e:
        return pd.DataFrame(columns=["従業員", "部門", "開始", "終了"])


@st.cache_data(ttl=5)
def load_masters():
    sheet_name = urllib.parse.quote("マスター")
    url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    try:
        master_df = pd.read_csv(url)
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

if st.sidebar.button("🔄 画面を強制更新"):
    st.cache_data.clear()
    st.rerun()

# ==========================================
# 4. タブで画面を切り替える
# ==========================================
st.title("職域別・時間割シフト管理")

tab_calendar, tab_register, tab_chart = st.tabs(["📅 カレンダー", "📝 シフト登録", "📊 タイムライン"])

# ==========================================
# タブ1: カレンダー（メイン機能）
# ==========================================
with tab_calendar:
    df = load_data()
    st.markdown("""
    <style>
    /* カレンダーのiframeを画面全体に近いサイズに */
    iframe[title="streamlit_component_1"] {
        border: none !important;
        border-radius: 12px;
        overflow: hidden;
    }
    </style>
    """, unsafe_allow_html=True)

    st.info("💡 **操作ガイド**: 日ビューでスタッフ列をドラッグして時間帯を選択→シフト登録 / シフトブロックをクリックで詳細確認 / ←→キーでページ移動", icon="ℹ️")

    # GASのdel_shiftアクションがない場合の注意
    with st.expander("⚙️ GASスクリプトに削除機能を追加する場合", expanded=False):
        st.code("""
// GASに以下を追加（deleteShift関数）
function doGet(e) {
  const action = e.parameter.action;
  // ... 既存のコード ...

  // シフト削除
  if (action === 'del_shift') {
    const name  = e.parameter.name;
    const dept  = e.parameter.dept;
    const start = e.parameter.start;
    const sheet = SpreadsheetApp.openById(SHEET_ID).getSheetByName('シフトデータ');
    const data  = sheet.getDataRange().getValues();
    for (let i = data.length - 1; i >= 1; i--) {
      const rowStart = Utilities.formatDate(new Date(data[i][2]), 'JST', 'yyyy-MM-dd HH:mm');
      if (data[i][0] == name && data[i][1] == dept && rowStart == start) {
        sheet.deleteRow(i + 1);
        break;
      }
    }
    return ContentService.createTextOutput('deleted');
  }
}
        """, language="javascript")

    render_calendar_component(df, STAFF_MASTER, DEPT_MASTER, GAS_URL)

# ==========================================
# タブ2: シフト登録（既存フォーム）
# ==========================================
with tab_register:
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
# タブ3: タイムライン（既存グラフ）
# ==========================================
with tab_chart:
    df = load_data()

    if not df.empty:
        # --- 表示期間の設定を追加 ---
        st.subheader("🔍 表示期間の絞り込み")
        col_t1, col_t2 = st.columns(2)
        
        # デフォルトで「今日」を表示
        with col_t1:
            start_filter = st.date_input("開始日", datetime.now().date())
        with col_t2:
            end_filter = st.date_input("終了日", datetime.now().date())

        # データを期間でフィルタリング
        # start_filterの00:00:00から、end_filterの23:59:59まで
        mask = (df['開始'].dt.date >= start_filter) & (df['開始'].dt.date <= end_filter)
        display_df = df.loc[mask].copy()

        if not display_df.empty:
            valid_df = display_df[display_df['開始'] < display_df['終了']].copy()

            if not valid_df.empty:
                valid_df = valid_df.sort_values(by=["従業員", "開始"])
                fig = px.timeline(
                    valid_df,
                    x_start="開始",
                    x_end="終了",
                    y="従業員",
                    color="部門",
                    text="部門",
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                fig.update_layout(
                    barmode='group',
                    xaxis_title="日付・時刻",
                    yaxis_title="スタッフ",
                    height=max(400, len(valid_df['従業員'].unique()) * 50), # 人数に合わせて高さを調整
                    xaxis=dict(
                        type='date',
                        tickformat="%m/%d %H:%M",
                        # グラフの端っこを、選択した日付の範囲に固定する
                        range=[
                            datetime.combine(start_filter, datetime.min.time()),
                            datetime.combine(end_filter, datetime.max.time())
                        ]
                    )
                )
                fig.update_yaxes(autorange="reversed", type='category')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("選択された期間に有効なシフトデータがありません。")
        else:
            st.info(f"{start_filter} から {end_filter} の期間にデータは見つかりませんでした。")

        # ダウンロードボタンはここに配置
        csv = df.to_csv(index=False).encode('utf_8_sig')
        st.download_button(
            "📥 全データをCSVダウンロード",
            csv,
            f"shift_all_{datetime.now().strftime('%Y%m%d')}.csv",
            "text/csv"
        )
    else:
        st.info("登録されているシフトデータがありません。")
