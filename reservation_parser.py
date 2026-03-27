"""
予約CSVを読み込んで日別集計に変換するモジュール（強化版）
"""
import pandas as pd
import re
from datetime import datetime, timedelta


# ── プラン分類ルール ──────────────────────────────────────
PLAN_RULES = {
    "宿泊":   lambda p: any(k in p for k in ["素泊まり","シンプルステイ","朝食付","夕朝食","夕食付","夕食",
                                              "フルコース","【早割","【事前","【LUX","【OPEN","【サウナ",
                                              "ステイ","宿泊"]),
    "肉割烹": lambda p: "肉割烹" in p,
    "ライト":  lambda p: any(k in p for k in ["炭火","SUMIKA","サウナ","OND SAUNA","ライト"]),
    "日帰り": lambda p: any(k in p for k in ["日帰り","炭火","SUMIKA","会議室","ホール","利用料",
                                              "夕食のみ","《","デイ"]),
}


# ── 食事フラグ ───────────────────────────────────────────
def has_dinner(plan: str) -> bool:
    return any(k in plan for k in ["夕食", "夕朝食", "肉割烹", "フルコース"])

def has_breakfast(plan: str) -> bool:
    return any(k in plan for k in ["朝食", "夕朝食"])


# ── 最強CSVローダー ──────────────────────────────────────
def robust_read_csv(filepath_or_buffer):
    """
    どんなCSVでもできるだけ読む
    - 文字コード自動判定
    - 区切り文字自動判定
    - Streamlit uploaded_file対応
    """
    encodings = ["utf-8-sig", "utf-8", "cp932", "shift_jis"]
    last_error = None

    for enc in encodings:
        try:
            if hasattr(filepath_or_buffer, "seek"):
                filepath_or_buffer.seek(0)

            df = pd.read_csv(
                filepath_or_buffer,
                encoding=enc,
                sep=None,
                engine="python",
            )

            print(f"✅ CSV読み込み成功: encoding={enc}, shape={df.shape}")

            if df.empty:
                raise ValueError("CSVは読み込めたが中身が空です")

            return df

        except Exception as e:
            print(f"❌ 失敗: encoding={enc} → {e}")
            last_error = e

    raise ValueError(f"CSV読み込み完全失敗: {last_error}")


# ── 日付抽出 ──────────────────────────────────────────────
def extract_ci_co(row) -> tuple:
    ci_raw = row.get("C/I", None)
    co_raw = row.get("C/O", None)

    def try_parse(v):
        if pd.isna(v) or v == "#######":
            return None
        if isinstance(v, datetime):
            return v.date()
        if isinstance(v, str):
            for fmt in ("%Y/%m/%d", "%Y-%m-%d", "%m/%d/%Y", "%Y年%m月%d日"):
                try:
                    return datetime.strptime(v.strip(), fmt).date()
                except ValueError:
                    pass
        return None

    ci = try_parse(ci_raw)
    co = try_parse(co_raw)

    if ci is None:
        combined = " ".join([
            str(row.get("OTA備考", "") or ""),
            str(row.get("メモ", "") or ""),
        ])
        dates_found = re.findall(r"ZZ(\d{4}/\d{2}/\d{2})", combined)
        dates_found = sorted(set(dates_found))
        if dates_found:
            ci = datetime.strptime(dates_found[0], "%Y/%m/%d").date()
            nights_found = re.findall(r"(\d+)泊目", combined)
            max_night = max(int(n) for n in nights_found) if nights_found else 1
            co = ci + timedelta(days=max_night)

    return ci, co


# ── CSV読み込み＆正規化 ───────────────────────────────────
def load_reservation_csv(filepath_or_buffer) -> pd.DataFrame:

    # ファイル名判定
    if hasattr(filepath_or_buffer, "name"):
        fname = filepath_or_buffer.name
    else:
        fname = str(filepath_or_buffer)

    # Excel対応
    if fname.endswith((".xlsx", ".xlsm", ".xls")):
        xl = pd.ExcelFile(filepath_or_buffer)
        sheet = "当月分CSV" if "当月分CSV" in xl.sheet_names else xl.sheet_names[0]
        df = pd.read_excel(filepath_or_buffer, sheet_name=sheet, header=0)

    else:
        df = robust_read_csv(filepath_or_buffer)

    # ── キャンセル除外
    if "ステータス" in df.columns:
        df = df[df["ステータス"] != "キャンセル"].copy()

    # ── 日付抽出
    ci_list, co_list = [], []
    for _, row in df.iterrows():
        ci, co = extract_ci_co(row)
        ci_list.append(ci)
        co_list.append(co)

    df["CI_date"] = ci_list
    df["CO_date"] = co_list

    # ── 人数
    df["大人人数"] = pd.to_numeric(df.get("大人人数", 0), errors="coerce").fillna(0).astype(int)
    df["子供人数"] = pd.to_numeric(df.get("子供人数", 0), errors="coerce").fillna(0).astype(int)
    df["合計人数"] = df["大人人数"] + df["子供人数"]

    # ── プラン分類
    df["プラン名_str"] = df.get("プラン名", "").fillna("").astype(str)

    for cat, rule in PLAN_RULES.items():
        df[f"is_{cat}"] = df["プラン名_str"].apply(rule)

    df["is_夕食"] = df["プラン名_str"].apply(has_dinner)
    df["is_朝食"] = df["プラン名_str"].apply(has_breakfast)

    return df


# ── 日別集計 ──────────────────────────────────────────────
def build_daily_summary(df: pd.DataFrame) -> pd.DataFrame:

    rows = []

    for _, r in df.iterrows():
        ci = r.get("CI_date")
        co = r.get("CO_date")

        if ci is None:
            continue

        plan = r["プラン名_str"]

        # ── 日帰り
        if r["is_日帰り"] and not r["is_宿泊"]:
            rows.append({
                "日付": ci,
                "宿泊室数": 0,
                "宿泊人数": 0,
                "日帰り室数": 1,
                "日帰り人数": int(r["合計人数"]),
                "肉割烹人数": 0,
                "ライト人数": int(r["合計人数"]) if r["is_ライト"] else 0,
                "夕食人数": int(r["合計人数"]) if r["is_夕食"] else 0,
                "朝食人数": 0,
                "予約番号": r.get("#予約番号", ""),
                "部屋タイプ": str(r.get("部屋タイプ", "") or ""),
                "プラン名": plan,
            })
            continue

        # ── 宿泊
        if co is None:
            co = ci + timedelta(days=1)

        stay_dates = [ci + timedelta(days=i) for i in range((co - ci).days)]
        if not stay_dates:
            stay_dates = [ci]

        for stay_date in stay_dates:
            rows.append({
                "日付": stay_date,
                "宿泊室数": 1,
                "宿泊人数": int(r["大人人数"]),
                "日帰り室数": 0,
                "日帰り人数": 0,
                "肉割烹人数": int(r["合計人数"]) if (r["is_肉割烹"] and stay_date == ci) else 0,
                "ライト人数": int(r["合計人数"]) if (r["is_ライト"] and stay_date == ci) else 0,
                "夕食人数": int(r["合計人数"]) if (r["is_夕食"] and stay_date == ci) else 0,
                "朝食人数": int(r["合計人数"]) if r["is_朝食"] else 0,
                "予約番号": r.get("#予約番号", ""),
                "部屋タイプ": str(r.get("部屋タイプ", "") or ""),
                "プラン名": plan,
            })

    detail_df = pd.DataFrame(rows)

    if detail_df.empty:
        return pd.DataFrame(columns=[
            "日付","宿泊室数","宿泊人数","日帰り室数","日帰り人数",
            "肉割烹人数","ライト人数","夕食人数","朝食人数"
        ])

    summary = detail_df.groupby("日付").agg(
        宿泊室数=("宿泊室数", "sum"),
        宿泊人数=("宿泊人数", "sum"),
        日帰り室数=("日帰り室数", "sum"),
        日帰り人数=("日帰り人数", "sum"),
        肉割烹人数=("肉割烹人数", "sum"),
        ライト人数=("ライト人数", "sum"),
        夕食人数=("夕食人数", "sum"),
        朝食人数=("朝食人数", "sum"),
    ).reset_index().sort_values("日付")

    summary["日付"] = pd.to_datetime(summary["日付"])

    return summary
