import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime, timedelta
import urllib.parse

from calendar_component import render_calendar_component

# ==========================================
# 1. 設定
# ==========================================
SPREADSHEET_ID = "1BE8rI5_Em5xe8eAMhpdzG6AvMSwEcMGv-qKdrrpZd08"
GAS_URL = "https://script.google.com/macros/s/AKfycbzBRZcKTqoigPZGJY4NvDky0mJOAwtNf4NWvF0wE7pkNVOz-QxSEaCmq0NgkordTTxLJg/exec"

st.set_page_config(layout="wide", page_title="共有シフト管理システム")

# ==========================================
# 2. データ読み込み
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
    except Exception:
        return pd.DataFrame(columns=["従業員", "部門", "開始", "終了"])


@st.cache_data(ttl=5)
def load_masters():
    sheet_name = urllib.parse.quote("マスター")
    url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    try:
        master_df = pd.read_csv(url)
        staff_list = master_df['従業員リスト'].dropna().unique().tolist() if '従業員リスト' in master_df.columns else []
        dept_list  = master_df['部門リスト'].dropna().unique().tolist()  if '部門リスト'  in master_df.columns else []
        return staff_list, dept_list
    except:
        return [], []

# ==========================================
# 3. サイドバー
# ==========================================
st.sidebar.title("🛠 管理パネル")
STAFF_MASTER, DEPT_MASTER = load_masters()

# --- 従業員管理 ---
with st.sidebar.expander("👤 従業員の追加・削除"):
    new_staff = st.text_input("新メンバー名", key="new_staff_input")
    if st.button("従業員を追加"):
        if new_staff:
            requests.get(GAS_URL, params={"action": "add_master", "type": "staff", "value": new_staff})
            st.cache_data.clear(); st.rerun()
    st.divider()
    if STAFF_MASTER:
        del_staff = st.selectbox("削除する従業員", STAFF_MASTER)
        if st.button("選択した従業員を削除"):
            requests.get(GAS_URL, params={"action": "del_master", "type": "staff", "value": del_staff})
            st.cache_data.clear(); st.rerun()

# --- 部門管理 ---
with st.sidebar.expander("🏢 部門の追加・削除"):
    new_dept = st.text_input("新部門名", key="new_dept_input")
    if st.button("部門を追加"):
        if new_dept:
            requests.get(GAS_URL, params={"action": "add_master", "type": "dept", "value": new_dept})
            st.cache_data.clear(); st.rerun()
    st.divider()
    if DEPT_MASTER:
        del_dept = st.selectbox("削除する部門", DEPT_MASTER)
        if st.button("選択した部門を削除"):
            requests.get(GAS_URL, params={"action": "del_master", "type": "dept", "value": del_dept})
            st.cache_data.clear(); st.rerun()

# --- 更新ボタン ---
if st.sidebar.button("🔄 画面を強制更新"):
    st.cache_data.clear(); st.rerun()

# --- CSV ダウンロード（常時サイドバーに表示）---
st.sidebar.divider()
st.sidebar.subheader("📥 データエクスポート")
_df_for_csv = load_data()
if not _df_for_csv.empty:
    csv_all = _df_for_csv.to_csv(index=False).encode('utf_8_sig')
    st.sidebar.download_button(
        label="📥 全データ CSV ダウンロード",
        data=csv_all,
        file_name=f"shift_all_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=True,
    )
else:
    st.sidebar.caption("まだシフトデータがありません")

# ==========================================
# 4. メイン：タブ切り替え
# ==========================================
st.title("職域別・時間割シフト管理")

tab_calendar, tab_register, tab_chart = st.tabs(["📅 カレンダー", "📝 シフト登録", "📊 タイムライン"])

# ==========================================
# タブ1: カレンダー
# ==========================================
with tab_calendar:
    df = load_data()
    st.info(
        "💡 **操作ガイド**: "
        "日ビューでスタッフ列をドラッグ→シフト登録 ／ "
        "シフトブロックをクリック→詳細・削除 ／ "
        "← → キーでページ移動 ／ "
        "日ビューは **0:00〜翌6:00** の30時間表示",
        icon="ℹ️"
    )

    with st.expander("⚙️ GASに削除機能を追加する（del_shiftアクション）", expanded=False):
        st.markdown("GASスクリプトの `doGet` 関数に以下を追加することで、カレンダーからの削除がスプレッドシートにも反映されます。")
        st.code("""
  // シフト削除アクション
  if (action === 'del_shift') {
    const name  = e.parameter.name;
    const dept  = e.parameter.dept;
    const start = e.parameter.start; // "YYYY-MM-DD HH:MM"
    const sheet = SpreadsheetApp.openById(SHEET_ID).getSheetByName('シフトデータ');
    const data  = sheet.getDataRange().getValues();
    for (let i = data.length - 1; i >= 1; i--) {
      const rowStart = Utilities.formatDate(new Date(data[i][2]), 'JST', 'yyyy-MM-dd HH:mm');
      if (String(data[i][0]) === name && String(data[i][1]) === dept && rowStart === start) {
        sheet.deleteRow(i + 1);
        break;
      }
    }
    return ContentService.createTextOutput('deleted').setMimeType(ContentService.MimeType.TEXT);
  }
""", language="javascript")

    render_calendar_component(df, STAFF_MASTER, DEPT_MASTER, GAS_URL)

# ==========================================
# タブ2: シフト登録フォーム
# ==========================================
with tab_register:
    with st.form("shift_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.selectbox("従業員名", STAFF_MASTER if STAFF_MASTER else ["未登録"])
            dept = st.selectbox("部門",     DEPT_MASTER  if DEPT_MASTER  else ["未登録"])
        with col2:
            date = st.date_input("日付", datetime.now())
            t1, t2 = st.columns(2)
            start_t = t1.time_input("開始", datetime.strptime("09:00", "%H:%M"))
            end_t   = t2.time_input("終了", datetime.strptime("18:00", "%H:%M"))

        if st.form_submit_button("スプレッドシートに保存"):
            if name == "未登録" or dept == "未登録":
                st.error("先に管理パネルから従業員と部門を登録してください。")
            elif start_t >= end_t:
                st.error("終了時間は開始時間より後に設定してください。")
            else:
                requests.get(GAS_URL, params={
                    "action": "add_shift", "name": name, "dept": dept,
                    "start": f"{date} {start_t}", "end": f"{date} {end_t}"
                })
                st.success(f"保存しました: {name} ({start_t}〜{end_t})")
                st.cache_data.clear(); st.rerun()

# ==========================================
# タブ3: タイムライン（表示期間設定付き）
# ==========================================
with tab_chart:
    df = load_data()

    if not df.empty:
        # ---- 表示期間の設定 UI ----
        st.subheader("📅 表示期間の設定")

        # データの日付範囲を取得してデフォルト値に使う
        data_min = df['開始'].min().date()
        data_max = df['終了'].max().date()

        period_mode = st.radio(
            "期間プリセット",
            ["今日", "今週", "今月", "過去7日", "過去30日", "カスタム"],
            horizontal=True,
            key="period_mode"
        )

        today = datetime.now().date()
        if period_mode == "今日":
            range_start, range_end = today, today
        elif period_mode == "今週":
            range_start = today - timedelta(days=today.weekday())
            range_end   = range_start + timedelta(days=6)
        elif period_mode == "今月":
            range_start = today.replace(day=1)
            range_end   = (today.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
        elif period_mode == "過去7日":
            range_start, range_end = today - timedelta(days=6), today
        elif period_mode == "過去30日":
            range_start, range_end = today - timedelta(days=29), today
        else:  # カスタム
            c1, c2 = st.columns(2)
            range_start = c1.date_input("開始日", value=data_min, key="custom_start")
            range_end   = c2.date_input("終了日", value=data_max, key="custom_end")

        # ---- フィルタリング ----
        valid_df = df[df['開始'] < df['終了']].copy()
        mask = (
            (valid_df['開始'].dt.date <= range_end) &
            (valid_df['終了'].dt.date >= range_start)
        )
        filtered_df = valid_df[mask].sort_values(by=["従業員", "開始"])

        st.caption(
            f"表示期間: **{range_start}** 〜 **{range_end}** "
            f"（{len(filtered_df)} 件 / 全 {len(valid_df)} 件）"
        )

        # ---- 追加フィルター ----
        with st.expander("🔍 スタッフ・部門で絞り込む", expanded=False):
            fc1, fc2 = st.columns(2)
            sel_staff = fc1.multiselect("スタッフ", STAFF_MASTER, default=[], key="tl_staff")
            sel_dept  = fc2.multiselect("部門",     DEPT_MASTER,  default=[], key="tl_dept")
            if sel_staff:
                filtered_df = filtered_df[filtered_df['従業員'].isin(sel_staff)]
            if sel_dept:
                filtered_df = filtered_df[filtered_df['部門'].isin(sel_dept)]

        st.divider()

        # ---- グラフ ----
        if not filtered_df.empty:
            fig = px.timeline(
                filtered_df,
                x_start="開始",
                x_end="終了",
                y="従業員",
                color="部門",
                text="部門",
                color_discrete_sequence=px.colors.qualitative.Pastel,
                title=f"シフト配置図（{range_start} 〜 {range_end}）"
            )
            fig.update_layout(
                barmode='group',
                xaxis_title="日付・時刻",
                yaxis_title="スタッフ",
                height=max(400, len(filtered_df['従業員'].unique()) * 50 + 150),
                xaxis=dict(
                    type='date',
                    range=[
                        f"{range_start} 00:00:00",
                        f"{range_end} 23:59:59"
                    ],
                    tickformat="%m/%d %H:%M"
                ),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            fig.update_yaxes(autorange="reversed", type='category')
            st.plotly_chart(fig, use_container_width=True)

            # 期間内データのCSVダウンロード（タブ内にも置く）
            csv_period = filtered_df.to_csv(index=False).encode('utf_8_sig')
            st.download_button(
                label=f"📥 この期間のデータをCSVダウンロード ({len(filtered_df)}件)",
                data=csv_period,
                file_name=f"shift_{range_start}_{range_end}.csv",
                mime="text/csv",
            )
        else:
            st.warning(f"選択期間（{range_start} 〜 {range_end}）にシフトデータがありません。")

    else:
        st.info("登録されているシフトデータがありません。")
