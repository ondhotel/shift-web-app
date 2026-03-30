import streamlit as st
import pandas as pd
import threading  # ← これを追加！
import plotly.express as px
import requests
from datetime import datetime, timedelta
import urllib.parse
import json
import gspread
from google.oauth2.credentials import Credentials

from calendar_component import render_calendar_component
from reservation_parser import load_reservation_csv, build_daily_summary, PLAN_RULES

# ──────────────────────────────────────────
# 設定
# ──────────────────────────────────────────
# 既存のIDを維持
SPREADSHEET_ID = "1BE8rI5_Em5xe8eAMhpdzG6AvMSwEcMGv-qKdrrpZd08"
# 直接書き込みにするため、GAS_URLは基本不要になりますが、
# 既存のカレンダーコンポーネントが内部でGASを叩いている可能性があるため定義だけ残します
GAS_URL = "https://script.google.com/macros/s/AKfycbwX_A4Iqk_xdQmAF81v9PbB1jCJ39lkCIAb0LprRLDd42WxBAtKF04XAA1p08yRvaAQBQ/exec"

# --- ここから追加 ---
def get_gspread_client():
    try:
        creds_info = st.secrets["gcp_service_account"]
        creds = Credentials.from_authorized_user_info(creds_info)
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"認証エラー: {e}")
        return None
# --- ここまで追加 ---

st.set_page_config(layout="wide", page_title="共有シフト管理システム")

# ──────────────────────────────────────────
# [新設] Google Sheets 直接接続用関数
# ──────────────────────────────────────────
def get_gspread_client():
    """Streamlit Secretsのtoken情報を使って認証"""
    try:
        creds_info = st.secrets["gcp_service_account"]
        creds = Credentials.from_authorized_user_info(creds_info)
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"認証エラー: {e}\nStreamlitのSecrets設定を確認してください。")
        return None

# ──────────────────────────────────────────
# デフォルト分類ルール定義（テキスト編集用）
# ──────────────────────────────────────────
DEFAULT_RULES_TEXT = """\
# プラン分類ルール設定
# 書式: カテゴリ名 = キーワード1, キーワード2, ...
# 行頭が # はコメント。空行は無視されます。
# プラン名にいずれかのキーワードが「含まれる」場合にそのカテゴリと判定されます。

宿泊 = 素泊まり, シンプルステイ, 朝食付, 夕朝食, 夕食付, フルコース, 早割, 事前決済, LUX SALE, OPEN1周年, サウナ満喫, ステイ, 宿泊
肉割烹 = 肉割烹
ライト = 炭火, SUMIKA, サウナ, OND SAUNA, ライト
日帰り = 日帰り, 炭火, SUMIKA, 会議室, ホール, 利用料, 夕食のみ, デイ
夕食 = 夕食, 夕朝食, 肉割烹, フルコース
朝食 = 朝食, 夕朝食
"""

RULES_SESSION_KEY = "plan_rules_text"

def parse_rules_text(text: str) -> dict:
    """テキストからルール辞書を生成"""
    rules = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        cat, kws_raw = line.split("=", 1)
        cat = cat.strip()
        kws = [k.strip() for k in kws_raw.split(",") if k.strip()]
        if cat and kws:
            rules[cat] = kws
    return rules

# ──────────────────────────────────────────
# データ読み込み（gspreadで高速化）
# ──────────────────────────────────────────
@st.cache_data(ttl=600)
def load_data():
    client = get_gspread_client()
    if not client: return pd.DataFrame()
    try:
        sh = client.open_by_key(SPREADSHEET_ID)
        sheet = sh.worksheet("シフトデータ")
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        if df.empty: return df
        
        # カラム名の揺れ（従業員/名前など）を考慮しつつ変換
        if "開始" in df.columns and "終了" in df.columns:
            df["開始"] = pd.to_datetime(df["開始"], errors="coerce")
            df["終了"] = pd.to_datetime(df["終了"], errors="coerce")
            df = df.dropna(subset=["開始", "終了"])
            df = df[df["開始"] < df["終了"]]
        return df
    except Exception as e:
        st.error(f"データ読み込みエラー: {e}")
        return pd.DataFrame(columns=["従業員", "部門", "開始", "終了"])


@st.cache_data(ttl=600)
def load_masters():
    client = get_gspread_client()
    if not client: return [], []
    try:
        sh = client.open_by_key(SPREADSHEET_ID)
        sheet = sh.worksheet("マスター")
        data = sheet.get_all_records()
        master_df = pd.DataFrame(data)
        staff_list = master_df["従業員リスト"].replace('', pd.NA).dropna().unique().tolist() if "従業員リスト" in master_df.columns else []
        dept_list  = master_df["部門リスト"].replace('', pd.NA).dropna().unique().tolist()  if "部門リスト"  in master_df.columns else []
        return staff_list, dept_list
    except:
        return [], []

# ──────────────────────────────────────────
# サイドバー
# ──────────────────────────────────────────
st.sidebar.title("🛠 管理パネル")
STAFF_MASTER, DEPT_MASTER = load_masters()

with st.sidebar.expander("👤 従業員の追加・削除"):
    new_staff = st.text_input("新メンバー名", key="new_staff_input")
    if st.button("従業員を追加"):
        if new_staff:
            client = get_gspread_client()
            sh = client.open_by_key(SPREADSHEET_ID).worksheet("マスター")
            # 1列目に名前を追加
            sh.append_row([new_staff, ""])
            st.cache_data.clear(); st.rerun()
    st.divider()
    if STAFF_MASTER:
        del_staff = st.selectbox("削除する従業員", STAFF_MASTER)
        if st.button("選択した従業員を削除"):
            client = get_gspread_client()
            sh = client.open_by_key(SPREADSHEET_ID).worksheet("マスター")
            cells = sh.find(del_staff)
            if cells: sh.delete_rows(cells.row)
            st.cache_data.clear(); st.rerun()

with st.sidebar.expander("🏢 部門の追加・削除"):
    new_dept = st.text_input("新部門名", key="new_dept_input")
    if st.button("部門を追加"):
        if new_dept:
            client = get_gspread_client()
            sh = client.open_by_key(SPREADSHEET_ID).worksheet("マスター")
            # 2列目に部門を追加
            sh.append_row(["", new_dept])
            st.cache_data.clear(); st.rerun()
    st.divider()
    if DEPT_MASTER:
        del_dept = st.selectbox("削除する部門", DEPT_MASTER)
        if st.button("選択した部門を削除"):
            client = get_gspread_client()
            sh = client.open_by_key(SPREADSHEET_ID).worksheet("マスター")
            cells = sh.find(del_dept)
            if cells: sh.delete_rows(cells.row)
            st.cache_data.clear(); st.rerun()

if st.sidebar.button("🔄 画面を強制更新"):
    st.cache_data.clear(); st.rerun()

# CSV ダウンロード（常時）
st.sidebar.divider()
st.sidebar.subheader("📥 データエクスポート")
_df_csv = load_data()
if not _df_csv.empty:
    st.sidebar.download_button(
        label="📥 全データ CSV ダウンロード",
        data=_df_csv.to_csv(index=False).encode("utf_8_sig"),
        file_name=f"shift_all_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=True,
    )
else:
    st.sidebar.caption("まだシフトデータがありません")

# ──────────────────────────────────────────
# メイン
# ──────────────────────────────────────────
st.title("職域別・時間割シフト管理")

tab_calendar, tab_register, tab_reservation, tab_chart = st.tabs([
    "📅 カレンダー", "📝 シフト登録", "🏨 予約集計", "📊 タイムライン"
])

# ── カレンダー ──────────────────────────────
with tab_calendar:
    df = load_data()
    st.info(
        "💡 **操作ガイド**: "
        "ドラッグ→シフト登録 ／ "
        "ブロッククリック→詳細・**📋コピー**・削除 ／ "
        "コピー後に貼り付け先をクリック→ペースト ／ "
        "← → キーでページ移動",
        icon="ℹ️"
    )
    # カレンダーコンポーネント内での削除(GAS呼び出し)を維持するためURLを渡す
    render_calendar_component(df, STAFF_MASTER, DEPT_MASTER, GAS_URL)

# ── シフト登録フォーム（高速化） ──────────────────────
with tab_register:
    with st.form("shift_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.selectbox("従業員名", STAFF_MASTER if STAFF_MASTER else ["未登録"])
            dept = st.selectbox("部門",     DEPT_MASTER  if DEPT_MASTER  else ["未登録"])
        with col2:
            date    = st.date_input("日付", datetime.now())
            t1, t2  = st.columns(2)
            start_t = t1.time_input("開始", datetime.strptime("09:00", "%H:%M"))
            end_t   = t2.time_input("終了", datetime.strptime("18:00", "%H:%M"))

        # ★ ここからインデントを揃えてください（with st.form の中に入っています）
        if st.form_submit_button("スプレッドシートに保存"):
            if name == "未登録" or dept == "未登録":
                st.error("先に管理パネルから従業員と部門を登録してください。")
            elif start_t >= end_t:
                st.error("終了時間は開始時間より後に設定してください。")
            else:
                # 保存データを準備
                save_row = [name, dept, f"{date} {start_t}", f"{date} {end_t}"]

                # 裏側で保存する関数を定義
                def bg_save(data):
                    client = get_gspread_client()
                    if client:
                        try:
                            sh = client.open_by_key(SPREADSHEET_ID).worksheet("シフトデータ")
                            sh.append_row(data)
                        except:
                            pass

                # 保存の完了を待たずに別スレッドで実行
                thread = threading.Thread(target=bg_save, args=(save_row,))
                thread.start()

                # 即座に完了メッセージ
                st.success(f"✅ 受付完了！ (裏で保存しています: {name})")
                
                # 注意：ここでは st.cache_data.clear() はしません（すると読み込みで待たされるため）

# ── 予約集計 ───────────────────────────────
with tab_reservation:
    st.subheader("🏨 予約CSVインポート & 日別集計")

    # ── 分類ルール編集 ──
    with st.expander("⚙️ プラン分類ルールを編集", expanded=False):
        st.markdown("""
        プラン名のキーワードでカテゴリを自動判定します。  
        書式: `カテゴリ名 = キーワード1, キーワード2, ...`  
        `#` から始まる行はコメントです。
        """)
        if RULES_SESSION_KEY not in st.session_state:
            st.session_state[RULES_SESSION_KEY] = DEFAULT_RULES_TEXT

        edited_rules = st.text_area(
            "分類ルール",
            value=st.session_state[RULES_SESSION_KEY],
            height=260,
            key="rules_editor"
        )
        rc1, rc2 = st.columns([1, 1])
        if rc1.button("✅ ルールを適用", use_container_width=True):
            st.session_state[RULES_SESSION_KEY] = edited_rules
            st.success("ルールを更新しました")
        if rc2.button("↩️ デフォルトに戻す", use_container_width=True):
            st.session_state[RULES_SESSION_KEY] = DEFAULT_RULES_TEXT
            st.rerun()

        # 現在のルールをプレビュー
        current_rules = parse_rules_text(st.session_state[RULES_SESSION_KEY])
        st.caption(f"現在のカテゴリ数: {len(current_rules)}")
        for cat, kws in current_rules.items():
            st.caption(f"**{cat}**: {', '.join(kws[:5])}{'...' if len(kws)>5 else ''}")

    st.divider()

    # ── CSVアップロード ──
    uploaded = st.file_uploader(
        "予約CSVまたはExcelファイルをアップロード",
        type=["csv", "xlsx", "xlsm", "xls"],
        help="予約システムからエクスポートした当月分のCSV/Excelを読み込みます。C/I・C/O列に正しい日付が入っているCSVが最適です。"
    )

    if uploaded:
        try:
            with st.spinner("データを読み込み中..."):
                res_df = load_reservation_csv(uploaded)

                # セッションのルールを reservation_parser に動的に適用
                current_rules = parse_rules_text(st.session_state.get(RULES_SESSION_KEY, DEFAULT_RULES_TEXT))
                def apply_custom_rules(df, rules):
                    for cat, kws in rules.items():
                        col = f"is_{cat}"
                        df[col] = df["プラン名_str"].apply(lambda p: any(k in p for k in kws))
                    return df
                res_df = apply_custom_rules(res_df, current_rules)

                summary = build_daily_summary(res_df)

            total  = len(res_df)
            dated  = res_df["CI_date"].notna().sum()
            undated = total - dated

            st.success(f"✅ {total}件読み込み完了（日付確定: {dated}件 / 日付不明: {undated}件）")
            if undated > 0:
                st.warning(f"⚠️ {undated}件はC/I日付を特定できませんでした。予約システムから日付付きCSVを直接エクスポートすると全件反映されます。", icon="⚠️")

            # ── 日別集計テーブル ──
            st.subheader("📊 日別集計")

            # 表示月フィルター
            months = sorted(summary["日付"].dt.strftime("%Y年%m月").unique())
            sel_month = st.selectbox("月を選択", months) if len(months) > 1 else (months[0] if months else None)
            if sel_month:
                ym = sel_month.replace("年", "-").replace("月", "")
                disp = summary[summary["日付"].dt.strftime("%Y-%m") == ym].copy()
            else:
                disp = summary.copy()

            if not disp.empty:
                disp["日付"] = disp["日付"].dt.strftime("%m/%d(%a)")
                disp.columns = ["日付","宿泊\n室数","宿泊\n人数","日帰り\n室数","日帰り\n人数","肉割烹\n人数","ライト\n人数","夕食\n人数","朝食\n人数"]

                # テーブル表示（色ハイライト付き）
                def color_cells(val):
                    if isinstance(val, (int, float)) and val > 0:
                        if val >= 10:
                            return "background-color: rgba(91,138,240,.4); font-weight:700"
                        elif val >= 5:
                            return "background-color: rgba(91,138,240,.2)"
                        else:
                            return "background-color: rgba(91,138,240,.08)"
                    return ""

                styled = disp.style.applymap(color_cells, subset=disp.columns[1:])
                st.dataframe(styled, use_container_width=True, height=500)

                # ── グラフ ──
                st.subheader("📈 日別推移グラフ")
                g_cols = {
                    "宿泊\n室数": "宿泊室数", "宿泊\n人数": "宿泊人数",
                    "肉割烹\n人数": "肉割烹", "夕食\n人数": "夕食", "朝食\n人数": "朝食"
                }
                plot_df = disp[["日付"] + list(g_cols.keys())].copy()
                plot_df = plot_df.rename(columns=g_cols)
                plot_melt = plot_df.melt(id_vars="日付", var_name="項目", value_name="数")
                fig = px.bar(
                    plot_melt, x="日付", y="数", color="項目",
                    barmode="group", height=350,
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                fig.update_layout(
                    xaxis_tickangle=-45,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    margin=dict(t=40, b=80)
                )
                st.plotly_chart(fig, use_container_width=True)

                # ── CSV出力 ──
                csv_out = disp.to_csv(index=False).encode("utf_8_sig")
                st.download_button(
                    "📥 集計CSVダウンロード",
                    data=csv_out,
                    file_name=f"reservation_summary_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )

            # ── 不明予約リスト ──
            if undated > 0:
                with st.expander(f"⚠️ 日付不明の予約 ({undated}件)", expanded=False):
                    unk = res_df[res_df["CI_date"].isna()][["#予約番号","プラン名","大人人数","部屋タイプ"]].copy()
                    st.dataframe(unk, use_container_width=True)

        except Exception as ex:
            st.error(f"読み込みエラー: {ex}")
            import traceback; st.code(traceback.format_exc())
    else:
        st.info("予約システムからエクスポートしたCSVまたはExcelファイルをアップロードしてください。")

# ── タイムライン ────────────────────────────
with tab_chart:
    df = load_data()
    if not df.empty:
        # ── カスタムCSS ──
        st.markdown("""
        <style>
        .tl-header {
            background: linear-gradient(135deg, #1a1d27 0%, #22263a 100%);
            border: 1px solid #2d3148;
            border-radius: 12px;
            padding: 16px 20px;
            margin-bottom: 16px;
        }
        .tl-stat {
            background: #1a1d27;
            border: 1px solid #2d3148;
            border-radius: 8px;
            padding: 12px 16px;
            text-align: center;
        }
        .tl-stat-num { font-size: 1.6rem; font-weight: 700; color: #5b8af0; line-height: 1; }
        .tl-stat-lbl { font-size: 0.72rem; color: #6b7094; margin-top: 4px; }
        </style>
        """, unsafe_allow_html=True)

        # ── 期間設定 ──
        data_min = df["開始"].min().date()
        data_max = df["終了"].max().date()
        today    = datetime.now().date()

        col_period, col_filter = st.columns([3, 2])
        with col_period:
            period_mode = st.radio(
                "📅 表示期間",
                ["今日", "今週", "今月", "過去7日", "過去30日", "カスタム"],
                horizontal=True, key="period_mode"
            )
        if   period_mode == "今日":     range_start, range_end = today, today
        elif period_mode == "今週":     range_start = today - timedelta(days=today.weekday()); range_end = range_start + timedelta(days=6)
        elif period_mode == "今月":     range_start = today.replace(day=1); range_end = (today.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
        elif period_mode == "過去7日":  range_start, range_end = today - timedelta(days=6), today
        elif period_mode == "過去30日": range_start, range_end = today - timedelta(days=29), today
        else:
            c1, c2 = st.columns(2)
            range_start = c1.date_input("開始日", value=data_min, key="cs")
            range_end   = c2.date_input("終了日", value=data_max, key="ce")

        valid_df    = df[df["開始"] < df["終了"]].copy()
        mask        = (valid_df["開始"].dt.date <= range_end) & (valid_df["終了"].dt.date >= range_start)
        filtered_df = valid_df[mask].sort_values(by=["従業員", "開始"])

        # ── 絞り込み ──
        with col_filter:
            with st.expander("🔍 スタッフ・部門で絞り込み", expanded=False):
                sel_staff = st.multiselect("スタッフ", STAFF_MASTER, default=[], key="tl_s")
                sel_dept  = st.multiselect("部門",     DEPT_MASTER,  default=[], key="tl_d")
        if sel_staff: filtered_df = filtered_df[filtered_df["従業員"].isin(sel_staff)]
        if sel_dept:  filtered_df = filtered_df[filtered_df["部門"].isin(sel_dept)]

        # ── サマリーカード ──
        n_staff  = filtered_df["従業員"].nunique()
        n_shifts = len(filtered_df)
        n_days   = (range_end - range_start).days + 1
        total_h  = (filtered_df["終了"] - filtered_df["開始"]).dt.total_seconds().sum() / 3600 if not filtered_df.empty else 0

        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(f'<div class="tl-stat"><div class="tl-stat-num">{n_staff}</div><div class="tl-stat-lbl">スタッフ数</div></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="tl-stat"><div class="tl-stat-num">{n_shifts}</div><div class="tl-stat-lbl">シフト件数</div></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="tl-stat"><div class="tl-stat-num">{n_days}</div><div class="tl-stat-lbl">表示日数</div></div>', unsafe_allow_html=True)
        c4.markdown(f'<div class="tl-stat"><div class="tl-stat-num">{total_h:.0f}h</div><div class="tl-stat-lbl">合計稼働時間</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        if not filtered_df.empty:
            # ── カラーパレット（見やすい濃い目） ──
            dept_colors = [
                "#5b8af0", "#e07b5a", "#34d399", "#b07fc7", "#f59e0b",
                "#5abfcc", "#e07bb0", "#7ec45a", "#c47e5a", "#f87171",
                "#c4b05a", "#5ac4a2", "#c45a7e", "#8fc45a", "#c45ab0", "#5a8fc4"
            ]

            fig = px.timeline(
                filtered_df,
                x_start="開始", x_end="終了", y="従業員",
                color="部門", text="部門",
                color_discrete_sequence=dept_colors,
                title=None,
            )

            bar_h = 28
            n_rows = len(filtered_df["従業員"].unique())
            chart_h = max(360, n_rows * (bar_h + 16) + 120)

            fig.update_layout(
                height=chart_h,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="#0f1117",
                font=dict(family="'Noto Sans JP', sans-serif", color="#e8eaf2", size=12),
                xaxis=dict(
                    title=None,
                    type="date",
                    range=[f"{range_start} 00:00:00", f"{range_end} 23:59:59"],
                    tickformat="%m/%d\n%H:%M",
                    tickfont=dict(size=11, color="#6b7094"),
                    gridcolor="#2d3148",
                    gridwidth=1,
                    showline=True,
                    linecolor="#2d3148",
                    zeroline=False,
                ),
                yaxis=dict(
                    title=None,
                    autorange="reversed",
                    type="category",
                    tickfont=dict(size=12, color="#e8eaf2"),
                    gridcolor="#2d3148",
                    gridwidth=1,
                    showline=False,
                    zeroline=False,
                ),
                legend=dict(
                    orientation="h",
                    yanchor="bottom", y=1.02,
                    xanchor="right", x=1,
                    bgcolor="rgba(26,29,39,0.9)",
                    bordercolor="#2d3148",
                    borderwidth=1,
                    font=dict(size=11, color="#e8eaf2"),
                ),
                margin=dict(l=10, r=10, t=20, b=40),
                hoverlabel=dict(
                    bgcolor="#22263a",
                    bordercolor="#5b8af0",
                    font=dict(size=12, color="#e8eaf2"),
                ),
                bargap=0.25,
                bargroupgap=0.1,
            )

            fig.update_traces(
                textfont=dict(size=10, color="#ffffff"),
                textposition="inside",
                insidetextanchor="middle",
                marker=dict(line=dict(width=0)),
                hovertemplate="<b>%{y}</b><br>部門: %{text}<br>開始: %{base|%m/%d %H:%M}<br>終了: %{x|%m/%d %H:%M}<extra></extra>",
            )

            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

            # ── フッター ──
            fc1, fc2 = st.columns([3, 1])
            fc1.caption(f"表示期間: **{range_start}** 〜 **{range_end}**　|　{n_shifts} 件 / 全 {len(valid_df)} 件")
            fc2.download_button(
                "📥 CSVダウンロード",
                data=filtered_df.to_csv(index=False).encode("utf_8_sig"),
                file_name=f"shift_{range_start}_{range_end}.csv",
                mime="text/csv",
                use_container_width=True,
            )
        else:
            st.warning(f"選択期間（{range_start} 〜 {range_end}）にデータがありません。")
    else:
        st.info("登録されているシフトデータがありません。")
