import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime, timedelta
import urllib.parse
import json

from calendar_component import render_calendar_component
from reservation_parser import load_reservation_csv, build_daily_summary, PLAN_RULES

# ──────────────────────────────────────────
# 設定
# ──────────────────────────────────────────
SPREADSHEET_ID = "1BE8rI5_Em5xe8eAMhpdzG6AvMSwEcMGv-qKdrrpZd08"
GAS_URL = "https://script.google.com/macros/s/AKfycbzyv5CnTxPW3vPlarYsola88A_sDq1xvc1L6jorKEG_QjXtgleAx0Krf96Jf-vMbuRmNw/exec"

st.set_page_config(layout="wide", page_title="共有シフト管理システム")

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
# データ読み込み
# ──────────────────────────────────────────
@st.cache_data(ttl=5)
def load_data():
    sheet_name = urllib.parse.quote("シフトデータ")
    url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    try:
        df = pd.read_csv(url, dtype={"開始": str, "終了": str})
        df["開始"] = pd.to_datetime(df["開始"], errors="coerce")
        df["終了"] = pd.to_datetime(df["終了"], errors="coerce")
        df = df.dropna(subset=["開始", "終了"])
        df = df[df["開始"] < df["終了"]]
        return df
    except Exception:
        return pd.DataFrame(columns=["従業員", "部門", "開始", "終了"])


@st.cache_data(ttl=5)
def load_masters():
    sheet_name = urllib.parse.quote("マスター")
    url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    try:
        master_df = pd.read_csv(url)
        staff_list = master_df["従業員リスト"].dropna().unique().tolist() if "従業員リスト" in master_df.columns else []
        dept_list  = master_df["部門リスト"].dropna().unique().tolist()  if "部門リスト"  in master_df.columns else []
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
            requests.get(GAS_URL, params={"action": "add_master", "type": "staff", "value": new_staff})
            st.cache_data.clear(); st.rerun()
    st.divider()
    if STAFF_MASTER:
        del_staff = st.selectbox("削除する従業員", STAFF_MASTER)
        if st.button("選択した従業員を削除"):
            requests.get(GAS_URL, params={"action": "del_master", "type": "staff", "value": del_staff})
            st.cache_data.clear(); st.rerun()

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
    with st.expander("⚙️ GASに削除機能を追加する（del_shiftアクション）", expanded=False):
        st.code("""
  // ← 既存の add_shift, add_master, del_master の後に追加
  if (action === 'del_shift') {
    var name  = e.parameter.name;
    var dept  = e.parameter.dept;
    var start = e.parameter.start; // "YYYY-MM-DD HH:MM"
    var sheet = ss.getSheetByName('シフトデータ'); // ss = getActiveSpreadsheet()
    var data  = sheet.getDataRange().getValues();
    for (var i = data.length - 1; i >= 1; i--) {
      var rowStart = Utilities.formatDate(new Date(data[i][2]), 'JST', 'yyyy-MM-dd HH:mm');
      if (String(data[i][0]) === name && String(data[i][1]) === dept && rowStart === start) {
        sheet.deleteRow(i + 1); break;
      }
    }
    return ContentService.createTextOutput('deleted').setMimeType(ContentService.MimeType.TEXT);
  }
""", language="javascript")

    render_calendar_component(df, STAFF_MASTER, DEPT_MASTER, GAS_URL)

# ── シフト登録フォーム ──────────────────────
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
        if st.form_submit_button("スプレッドシートに保存"):
            if name == "未登録" or dept == "未登録":
                st.error("先に管理パネルから従業員と部門を登録してください。")
            elif start_t >= end_t:
                st.error("終了時間は開始時間より後に設定してください。")
            else:
                requests.get(GAS_URL, params={"action":"add_shift","name":name,"dept":dept,
                                              "start":f"{date} {start_t}","end":f"{date} {end_t}"})
                st.success(f"保存しました: {name} ({start_t}〜{end_t})")
                st.cache_data.clear(); st.rerun()

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
        with st.expander("📋 対応フォーマット（CSVカラム）", expanded=False):
            st.markdown("""
            | カラム名 | 説明 |
            |----------|------|
            | `#予約番号` | 予約ID |
            | `プラン名` | プラン名（分類に使用） |
            | `C/I` | チェックイン日（`YYYY/MM/DD`形式推奨） |
            | `C/O` | チェックアウト日 |
            | `大人人数` | 大人の人数 |
            | `子供人数` | 子供の人数 |
            | `部屋タイプ` | 部屋名 |
            | `ステータス` | `キャンセル`は自動除外 |
            | `OTA備考` | C/Iが不明な場合の日付補完に使用 |
            """)

# ── タイムライン ────────────────────────────
with tab_chart:
    df = load_data()
    if not df.empty:
        st.subheader("📅 表示期間の設定")
        data_min = df["開始"].min().date()
        data_max = df["終了"].max().date()
        today    = datetime.now().date()

        period_mode = st.radio(
            "期間プリセット",
            ["今日","今週","今月","過去7日","過去30日","カスタム"],
            horizontal=True, key="period_mode"
        )
        if   period_mode == "今日":    range_start,range_end = today,today
        elif period_mode == "今週":    range_start=today-timedelta(days=today.weekday()); range_end=range_start+timedelta(days=6)
        elif period_mode == "今月":    range_start=today.replace(day=1); range_end=(today.replace(day=28)+timedelta(days=4)).replace(day=1)-timedelta(days=1)
        elif period_mode == "過去7日":  range_start,range_end = today-timedelta(days=6),today
        elif period_mode == "過去30日": range_start,range_end = today-timedelta(days=29),today
        else:
            c1,c2 = st.columns(2)
            range_start = c1.date_input("開始日", value=data_min, key="cs")
            range_end   = c2.date_input("終了日", value=data_max, key="ce")

        valid_df    = df[df["開始"] < df["終了"]].copy()
        mask        = (valid_df["開始"].dt.date <= range_end) & (valid_df["終了"].dt.date >= range_start)
        filtered_df = valid_df[mask].sort_values(by=["従業員","開始"])

        with st.expander("🔍 絞り込み", expanded=False):
            fc1,fc2   = st.columns(2)
            sel_staff = fc1.multiselect("スタッフ", STAFF_MASTER, default=[], key="tl_s")
            sel_dept  = fc2.multiselect("部門",     DEPT_MASTER,  default=[], key="tl_d")
            if sel_staff: filtered_df = filtered_df[filtered_df["従業員"].isin(sel_staff)]
            if sel_dept:  filtered_df = filtered_df[filtered_df["部門"].isin(sel_dept)]

        st.caption(f"表示期間: **{range_start}** 〜 **{range_end}**（{len(filtered_df)} 件 / 全 {len(valid_df)} 件）")
        st.divider()

        if not filtered_df.empty:
            fig = px.timeline(
                filtered_df, x_start="開始", x_end="終了", y="従業員",
                color="部門", text="部門",
                color_discrete_sequence=px.colors.qualitative.Pastel,
                title=f"シフト配置図（{range_start} 〜 {range_end}）"
            )
            fig.update_layout(
                barmode="group", xaxis_title="日付・時刻", yaxis_title="スタッフ",
                height=max(400, len(filtered_df["従業員"].unique())*50+150),
                xaxis=dict(type="date",
                           range=[f"{range_start} 00:00:00",f"{range_end} 23:59:59"],
                           tickformat="%m/%d %H:%M"),
                legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1)
            )
            fig.update_yaxes(autorange="reversed",type="category")
            st.plotly_chart(fig, use_container_width=True)
            st.download_button(
                f"📥 この期間のCSVダウンロード（{len(filtered_df)}件）",
                data=filtered_df.to_csv(index=False).encode("utf_8_sig"),
                file_name=f"shift_{range_start}_{range_end}.csv", mime="text/csv"
            )
        else:
            st.warning(f"選択期間（{range_start} 〜 {range_end}）にデータがありません。")
    else:
        st.info("登録されているシフトデータがありません。")
