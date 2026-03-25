"""
カレンダービューコンポーネント
既存のシフト管理アプリに追加するモジュール
"""

import streamlit.components.v1 as components
import json
import pandas as pd
from datetime import datetime, timedelta
import calendar


def render_calendar_component(df: pd.DataFrame, staff_list: list, dept_list: list, gas_url: str):
    """
    月・週・日の3ビューカレンダーをStreamlitに埋め込む
    ドラッグで時間帯を選択してシフト登録できる
    """
    
    # DataFrameをJSON化（日時をISO文字列に変換）
    shifts_json = []
    if not df.empty:
        for _, row in df.iterrows():
            try:
                shifts_json.append({
                    "staff": str(row.get("従業員", "")),
                    "dept": str(row.get("部門", "")),
                    "start": row["開始"].isoformat() if pd.notna(row["開始"]) else "",
                    "end": row["終了"].isoformat() if pd.notna(row["終了"]) else "",
                })
            except Exception:
                pass

    staff_json = json.dumps(staff_list, ensure_ascii=False)
    dept_json = json.dumps(dept_list, ensure_ascii=False)
    shifts_json_str = json.dumps(shifts_json, ensure_ascii=False)

    # 部門ごとのカラーパレット（最大16部門）
    color_palette = [
        "#4f86c6", "#e07b5a", "#5aad8f", "#b07fc7", "#e0b84a",
        "#5abfcc", "#e07bb0", "#7ec45a", "#c47e5a", "#5a7ec4",
        "#c4b05a", "#5ac4a2", "#c45a7e", "#8fc45a", "#c45ab0", "#5a8fc4"
    ]

    html_code = f"""
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
  @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@300;400;500;700&family=JetBrains+Mono:wght@400;600&display=swap');

  :root {{
    --bg: #0f1117;
    --surface: #1a1d27;
    --surface2: #22263a;
    --border: #2d3148;
    --text: #e8eaf2;
    --text-muted: #6b7094;
    --accent: #5b8af0;
    --accent2: #8b5cf6;
    --success: #34d399;
    --danger: #f87171;
    --today: rgba(91, 138, 240, 0.12);
    --hover: rgba(91, 138, 240, 0.08);
    --drag: rgba(91, 138, 240, 0.25);
    --radius: 8px;
    --font: 'Noto Sans JP', sans-serif;
    --mono: 'JetBrains Mono', monospace;
  }}

  * {{ margin: 0; padding: 0; box-sizing: border-box; }}

  body {{
    font-family: var(--font);
    background: var(--bg);
    color: var(--text);
    font-size: 13px;
    user-select: none;
  }}

  /* ===== TOP BAR ===== */
  .topbar {{
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 16px;
    background: var(--surface);
    border-bottom: 1px solid var(--border);
    flex-wrap: wrap;
  }}

  .view-tabs {{
    display: flex;
    background: var(--surface2);
    border-radius: var(--radius);
    padding: 3px;
    gap: 2px;
  }}

  .view-tab {{
    padding: 6px 16px;
    border-radius: 6px;
    cursor: pointer;
    font-size: 12px;
    font-weight: 500;
    color: var(--text-muted);
    transition: all 0.18s;
    border: none;
    background: transparent;
  }}
  .view-tab.active {{
    background: var(--accent);
    color: #fff;
    box-shadow: 0 2px 8px rgba(91,138,240,0.4);
  }}
  .view-tab:hover:not(.active) {{
    background: var(--hover);
    color: var(--text);
  }}

  .nav-group {{
    display: flex;
    align-items: center;
    gap: 8px;
  }}
  .nav-btn {{
    width: 32px; height: 32px;
    border-radius: 6px;
    border: 1px solid var(--border);
    background: var(--surface2);
    color: var(--text);
    cursor: pointer;
    font-size: 15px;
    display: flex; align-items: center; justify-content: center;
    transition: all 0.15s;
  }}
  .nav-btn:hover {{ background: var(--hover); border-color: var(--accent); }}

  .period-label {{
    font-size: 15px;
    font-weight: 700;
    min-width: 180px;
    text-align: center;
    letter-spacing: 0.02em;
    color: var(--text);
  }}

  .today-btn {{
    padding: 6px 14px;
    border-radius: 6px;
    border: 1px solid var(--border);
    background: var(--surface2);
    color: var(--text);
    cursor: pointer;
    font-size: 12px;
    font-family: var(--font);
    font-weight: 500;
    transition: all 0.15s;
  }}
  .today-btn:hover {{ border-color: var(--accent); color: var(--accent); }}

  /* Filter */
  .filter-group {{
    display: flex;
    gap: 8px;
    margin-left: auto;
    align-items: center;
  }}
  .filter-select {{
    padding: 5px 10px;
    border-radius: 6px;
    border: 1px solid var(--border);
    background: var(--surface2);
    color: var(--text);
    font-size: 12px;
    font-family: var(--font);
    cursor: pointer;
  }}

  /* ===== CALENDAR WRAPPER ===== */
  #calendar-root {{
    flex: 1;
    overflow: hidden;
    display: flex;
    flex-direction: column;
  }}

  /* ===== MONTH VIEW ===== */
  .month-view {{
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }}
  .month-header {{
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    border-bottom: 1px solid var(--border);
  }}
  .month-header-cell {{
    padding: 8px 0;
    text-align: center;
    font-size: 11px;
    font-weight: 600;
    color: var(--text-muted);
    letter-spacing: 0.08em;
    text-transform: uppercase;
  }}
  .month-header-cell:first-child {{ color: #f87171; }}
  .month-header-cell:last-child {{ color: #60a5fa; }}

  .month-grid {{
    flex: 1;
    display: grid;
    grid-template-rows: repeat(6, 1fr);
    overflow-y: auto;
  }}
  .month-row {{
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    border-bottom: 1px solid var(--border);
    min-height: 100px;
  }}
  .month-cell {{
    border-right: 1px solid var(--border);
    padding: 6px;
    cursor: pointer;
    transition: background 0.12s;
    overflow: hidden;
    min-height: 90px;
  }}
  .month-cell:hover {{ background: var(--hover); }}
  .month-cell.other-month {{ opacity: 0.35; }}
  .month-cell.today {{ background: var(--today); }}
  .month-cell.sunday .day-num {{ color: #f87171; }}
  .month-cell.saturday .day-num {{ color: #60a5fa; }}
  .day-num {{
    font-size: 12px;
    font-weight: 600;
    margin-bottom: 4px;
    width: 24px; height: 24px;
    display: flex; align-items: center; justify-content: center;
    border-radius: 50%;
    font-family: var(--mono);
  }}
  .today .day-num {{
    background: var(--accent);
    color: #fff;
  }}
  .month-shift-chip {{
    font-size: 10px;
    padding: 2px 5px;
    border-radius: 3px;
    margin-bottom: 2px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    font-weight: 500;
    cursor: pointer;
  }}
  .month-more {{
    font-size: 10px;
    color: var(--text-muted);
    padding: 1px 4px;
    cursor: pointer;
  }}
  .month-more:hover {{ color: var(--accent); }}

  /* ===== WEEK VIEW ===== */
  .week-view {{
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }}
  .week-header {{
    display: grid;
    grid-template-columns: 56px repeat(7, 1fr);
    border-bottom: 2px solid var(--border);
    background: var(--surface);
    flex-shrink: 0;
  }}
  .week-header-corner {{ padding: 10px 0; }}
  .week-header-day {{
    padding: 8px 4px;
    text-align: center;
    border-left: 1px solid var(--border);
    cursor: pointer;
  }}
  .week-header-day:hover {{ background: var(--hover); }}
  .week-dow {{
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--text-muted);
  }}
  .week-date-num {{
    font-size: 20px;
    font-weight: 700;
    font-family: var(--mono);
    line-height: 1.2;
  }}
  .week-header-day.today-col .week-date-num {{
    color: var(--accent);
  }}
  .week-header-day.sunday-col .week-dow, .week-header-day.sunday-col .week-date-num {{ color: #f87171; }}
  .week-header-day.saturday-col .week-dow, .week-header-day.saturday-col .week-date-num {{ color: #60a5fa; }}

  .week-body {{
    flex: 1;
    display: flex;
    overflow-y: auto;
    overflow-x: hidden;
  }}
  .week-time-col {{
    width: 56px;
    flex-shrink: 0;
    border-right: 1px solid var(--border);
    background: var(--surface);
    position: sticky;
    left: 0;
    z-index: 2;
  }}
  .week-time-slot {{
    height: 48px;
    padding: 4px 6px 0;
    border-bottom: 1px solid var(--border);
    font-size: 10px;
    color: var(--text-muted);
    font-family: var(--mono);
    text-align: right;
  }}
  .week-time-slot:first-child {{ padding-top: 0; }}
  .week-day-cols {{
    flex: 1;
    display: grid;
    grid-template-columns: repeat(7, 1fr);
  }}
  .week-day-col {{
    border-right: 1px solid var(--border);
    position: relative;
    cursor: crosshair;
  }}
  .week-day-col.today-col {{ background: var(--today); }}
  .week-hour-slot {{
    height: 48px;
    border-bottom: 1px solid var(--border);
  }}
  .week-half-slot {{
    height: 24px;
    border-bottom: 1px dashed rgba(255,255,255,0.04);
  }}

  /* ===== DAY VIEW ===== */
  .day-view {{
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }}
  .day-staff-header {{
    display: flex;
    border-bottom: 2px solid var(--border);
    background: var(--surface);
    flex-shrink: 0;
  }}
  .day-time-corner {{
    width: 64px;
    flex-shrink: 0;
    padding: 10px 6px;
    font-size: 10px;
    color: var(--text-muted);
    text-align: center;
    border-right: 1px solid var(--border);
  }}
  .day-staff-col-header {{
    flex: 1;
    min-width: 100px;
    padding: 8px 6px;
    text-align: center;
    border-right: 1px solid var(--border);
    font-weight: 600;
    font-size: 12px;
  }}
  .day-body {{
    flex: 1;
    display: flex;
    overflow-y: auto;
  }}
  .day-time-col {{
    width: 64px;
    flex-shrink: 0;
    border-right: 1px solid var(--border);
    background: var(--surface);
    position: sticky;
    left: 0;
    z-index: 2;
  }}
  .day-time-slot {{
    height: 48px;
    padding: 4px 8px 0;
    border-bottom: 1px solid var(--border);
    font-size: 10px;
    color: var(--text-muted);
    font-family: var(--mono);
    text-align: right;
  }}
  .day-staff-cols {{
    flex: 1;
    display: flex;
  }}
  .day-staff-col {{
    flex: 1;
    min-width: 100px;
    border-right: 1px solid var(--border);
    position: relative;
    cursor: crosshair;
  }}
  .day-hour-slot {{
    height: 48px;
    border-bottom: 1px solid var(--border);
  }}
  .day-half-slot {{
    height: 24px;
    border-bottom: 1px dashed rgba(255,255,255,0.04);
  }}

  /* ===== SHIFT BLOCK (week/day) ===== */
  .shift-block {{
    position: absolute;
    left: 2px;
    right: 2px;
    border-radius: 4px;
    padding: 3px 5px;
    font-size: 10px;
    font-weight: 600;
    overflow: hidden;
    z-index: 1;
    cursor: pointer;
    transition: filter 0.12s;
    border: 1px solid rgba(255,255,255,0.1);
  }}
  .shift-block:hover {{ filter: brightness(1.2); z-index: 3; }}
  .shift-block .sb-name {{ white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
  .shift-block .sb-time {{ font-size: 9px; opacity: 0.8; font-family: var(--mono); }}

  /* ===== DRAG SELECTION ===== */
  .drag-selection {{
    position: absolute;
    left: 2px; right: 2px;
    background: var(--drag);
    border: 2px dashed var(--accent);
    border-radius: 4px;
    z-index: 10;
    pointer-events: none;
  }}

  /* ===== MODAL ===== */
  .modal-overlay {{
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,0.65);
    z-index: 1000;
    display: flex;
    align-items: center;
    justify-content: center;
    backdrop-filter: blur(4px);
  }}
  .modal {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 24px;
    width: 380px;
    max-width: 95vw;
    box-shadow: 0 20px 60px rgba(0,0,0,0.5);
    animation: modalIn 0.2s ease;
  }}
  @keyframes modalIn {{
    from {{ transform: scale(0.92); opacity: 0; }}
    to {{ transform: scale(1); opacity: 1; }}
  }}
  .modal-title {{
    font-size: 16px;
    font-weight: 700;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    gap: 8px;
  }}
  .modal-title .icon {{ font-size: 20px; }}
  .form-group {{
    margin-bottom: 14px;
  }}
  .form-label {{
    display: block;
    font-size: 11px;
    font-weight: 600;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 6px;
  }}
  .form-input, .form-select {{
    width: 100%;
    padding: 9px 12px;
    border-radius: 6px;
    border: 1px solid var(--border);
    background: var(--surface2);
    color: var(--text);
    font-size: 13px;
    font-family: var(--font);
    transition: border-color 0.15s;
  }}
  .form-input:focus, .form-select:focus {{
    outline: none;
    border-color: var(--accent);
    box-shadow: 0 0 0 3px rgba(91,138,240,0.15);
  }}
  .time-row {{
    display: grid;
    grid-template-columns: 1fr auto 1fr;
    align-items: center;
    gap: 8px;
  }}
  .time-sep {{ color: var(--text-muted); font-size: 16px; text-align: center; }}
  .modal-actions {{
    display: flex;
    gap: 10px;
    margin-top: 20px;
  }}
  .btn {{
    flex: 1;
    padding: 10px;
    border-radius: 6px;
    border: none;
    font-size: 13px;
    font-family: var(--font);
    font-weight: 600;
    cursor: pointer;
    transition: all 0.15s;
  }}
  .btn-primary {{
    background: var(--accent);
    color: #fff;
  }}
  .btn-primary:hover {{ background: #4a77e0; box-shadow: 0 4px 12px rgba(91,138,240,0.4); }}
  .btn-secondary {{
    background: var(--surface2);
    color: var(--text);
    border: 1px solid var(--border);
  }}
  .btn-secondary:hover {{ border-color: var(--accent); color: var(--accent); }}
  .btn-danger {{
    background: var(--danger);
    color: #fff;
    flex: 0;
    padding: 10px 16px;
  }}
  .btn-danger:hover {{ background: #ef4444; }}

  /* Detail Modal */
  .detail-chip {{
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    margin-bottom: 14px;
  }}
  .detail-row {{
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 0;
    border-bottom: 1px solid var(--border);
    font-size: 13px;
  }}
  .detail-row:last-child {{ border-bottom: none; }}
  .detail-icon {{ font-size: 16px; width: 24px; text-align: center; }}

  /* Toast */
  .toast {{
    position: fixed;
    bottom: 20px;
    right: 20px;
    background: var(--success);
    color: #fff;
    padding: 12px 20px;
    border-radius: 8px;
    font-weight: 600;
    font-size: 13px;
    z-index: 9999;
    box-shadow: 0 8px 24px rgba(52,211,153,0.4);
    animation: toastIn 0.3s ease;
  }}
  @keyframes toastIn {{
    from {{ transform: translateY(20px); opacity: 0; }}
    to {{ transform: translateY(0); opacity: 1; }}
  }}

  .loading {{
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 9998;
    font-size: 14px;
    color: var(--text);
    gap: 10px;
  }}
  .spinner {{
    width: 20px; height: 20px;
    border: 2px solid var(--border);
    border-top-color: var(--accent);
    border-radius: 50%;
    animation: spin 0.7s linear infinite;
  }}
  @keyframes spin {{ to {{ transform: rotate(360deg); }} }}

  .empty-state {{
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 200px;
    color: var(--text-muted);
    gap: 8px;
    font-size: 13px;
  }}
  .empty-icon {{ font-size: 40px; }}
</style>
</head>
<body>

<div style="display:flex;flex-direction:column;height:100vh;">

  <!-- TOP BAR -->
  <div class="topbar">
    <div class="view-tabs">
      <button class="view-tab active" onclick="setView('day')">日</button>
      <button class="view-tab" onclick="setView('week')">週</button>
      <button class="view-tab" onclick="setView('month')">月</button>
    </div>

    <div class="nav-group">
      <button class="nav-btn" onclick="navigate(-1)">&#8249;</button>
      <div class="period-label" id="period-label"></div>
      <button class="nav-btn" onclick="navigate(1)">&#8250;</button>
    </div>

    <button class="today-btn" onclick="goToday()">今日</button>

    <div class="filter-group">
      <select class="filter-select" id="filter-staff" onchange="renderView()">
        <option value="">全スタッフ</option>
      </select>
      <select class="filter-select" id="filter-dept" onchange="renderView()">
        <option value="">全部門</option>
      </select>
    </div>
  </div>

  <!-- CALENDAR ROOT -->
  <div id="calendar-root"></div>

</div>

<!-- REGISTER MODAL -->
<div class="modal-overlay" id="reg-modal" style="display:none" onclick="if(event.target===this)closeModal()">
  <div class="modal">
    <div class="modal-title"><span class="icon">📋</span>シフト登録</div>
    <div class="form-group">
      <label class="form-label">従業員</label>
      <select class="form-select" id="m-staff"></select>
    </div>
    <div class="form-group">
      <label class="form-label">部門</label>
      <select class="form-select" id="m-dept"></select>
    </div>
    <div class="form-group">
      <label class="form-label">日付</label>
      <input type="date" class="form-input" id="m-date">
    </div>
    <div class="form-group">
      <label class="form-label">時間</label>
      <div class="time-row">
        <input type="time" class="form-input" id="m-start" value="09:00">
        <div class="time-sep">→</div>
        <input type="time" class="form-input" id="m-end" value="18:00">
      </div>
    </div>
    <div class="modal-actions">
      <button class="btn btn-secondary" onclick="closeModal()">キャンセル</button>
      <button class="btn btn-primary" onclick="saveShift()">保存</button>
    </div>
  </div>
</div>

<!-- DETAIL MODAL -->
<div class="modal-overlay" id="detail-modal" style="display:none" onclick="if(event.target===this)closeDetail()">
  <div class="modal">
    <div class="modal-title"><span class="icon">📌</span>シフト詳細</div>
    <div id="detail-content"></div>
    <div class="modal-actions" style="margin-top:16px">
      <button class="btn btn-secondary" onclick="closeDetail()">閉じる</button>
      <button class="btn btn-danger" id="delete-btn" onclick="deleteShift()">削除</button>
    </div>
  </div>
</div>

<script>
// ===================== DATA =====================
const GAS_URL = "{gas_url}";
const STAFF_LIST = {staff_json};
const DEPT_LIST = {dept_json};
let SHIFTS = {shifts_json_str};

const COLORS = {color_palette};

function getDeptColor(dept) {{
  const idx = DEPT_LIST.indexOf(dept);
  if (idx >= 0) return COLORS[idx % COLORS.length];
  // fallback hash
  let hash = 0;
  for (let c of dept) hash = (hash * 31 + c.charCodeAt(0)) & 0xffffffff;
  return COLORS[Math.abs(hash) % COLORS.length];
}}

function hexToRgba(hex, alpha) {{
  const r = parseInt(hex.slice(1,3),16);
  const g = parseInt(hex.slice(3,5),16);
  const b = parseInt(hex.slice(5,7),16);
  return `rgba(${{r}},${{g}},${{b}},${{alpha}})`;
}}

// ===================== STATE =====================
let currentView = 'day';
let currentDate = new Date();
currentDate.setHours(0,0,0,0);

// ===================== INIT =====================
window.onload = function() {{
  // Populate filters
  const fs = document.getElementById('filter-staff');
  const fd = document.getElementById('filter-dept');
  STAFF_LIST.forEach(s => {{ const o = new Option(s,s); fs.appendChild(o); }});
  DEPT_LIST.forEach(d => {{ const o = new Option(d,d); fd.appendChild(o); }});

  // Populate modal selects
  const ms = document.getElementById('m-staff');
  const md = document.getElementById('m-dept');
  STAFF_LIST.forEach(s => ms.appendChild(new Option(s,s)));
  DEPT_LIST.forEach(d => md.appendChild(new Option(d,d)));

  renderView();
}};

// ===================== VIEW CONTROL =====================
function setView(v) {{
  currentView = v;
  document.querySelectorAll('.view-tab').forEach((el,i) => {{
    el.classList.toggle('active', ['day','week','month'][i] === v);
  }});
  renderView();
}}

function navigate(dir) {{
  if (currentView === 'day') {{
    currentDate.setDate(currentDate.getDate() + dir);
  }} else if (currentView === 'week') {{
    currentDate.setDate(currentDate.getDate() + dir*7);
  }} else {{
    currentDate.setMonth(currentDate.getMonth() + dir);
  }}
  renderView();
}}

function goToday() {{
  currentDate = new Date();
  currentDate.setHours(0,0,0,0);
  renderView();
}}

function getFilteredShifts() {{
  const fs = document.getElementById('filter-staff')?.value || '';
  const fd = document.getElementById('filter-dept')?.value || '';
  return SHIFTS.filter(s =>
    (!fs || s.staff === fs) &&
    (!fd || s.dept === fd)
  );
}}

function renderView() {{
  if (currentView === 'day') renderDay();
  else if (currentView === 'week') renderWeek();
  else renderMonth();
}}

// ===================== DATE UTILS =====================
const DAYS_JP = ['日','月','火','水','木','金','土'];
const MONTHS_JP = ['1月','2月','3月','4月','5月','6月','7月','8月','9月','10月','11月','12月'];

function fmt(date) {{
  const y = date.getFullYear(), m = date.getMonth()+1, d = date.getDate();
  return `${{y}}-${{String(m).padStart(2,'0')}}-${{String(d).padStart(2,'0')}}`;
}}

function todayStr() {{ return fmt(new Date()); }}

function parseShiftDate(isoStr) {{
  // Returns local Date object
  return new Date(isoStr);
}}

function shiftsOnDate(dateStr, shifts) {{
  return shifts.filter(s => {{
    if (!s.start) return false;
    const d = parseShiftDate(s.start);
    return fmt(d) === dateStr;
  }});
}}

function minutesToTime(mins) {{
  const h = String(Math.floor(mins/60)).padStart(2,'0');
  const m = String(mins%60).padStart(2,'0');
  return `${{h}}:${{m}}`;
}}

function timeToMinutes(timeStr) {{
  const [h,m] = timeStr.split(':').map(Number);
  return h*60 + m;
}}

// ===================== MONTH VIEW =====================
function renderMonth() {{
  const y = currentDate.getFullYear(), mo = currentDate.getMonth();
  document.getElementById('period-label').textContent = `${{y}}年 ${{MONTHS_JP[mo]}}`;

  const first = new Date(y, mo, 1);
  const startDow = first.getDay(); // 0=Sun
  const daysInMonth = new Date(y, mo+1, 0).getDate();
  const prevDays = new Date(y, mo, 0).getDate();
  const today = todayStr();
  const filtered = getFilteredShifts();

  let cells = [];
  // prev month fill
  for (let i = startDow - 1; i >= 0; i--) {{
    cells.push({{ day: prevDays - i, month: mo - 1, year: y, other: true }});
  }}
  for (let d = 1; d <= daysInMonth; d++) {{
    cells.push({{ day: d, month: mo, year: y, other: false }});
  }}
  while (cells.length < 42) {{
    cells.push({{ day: cells.length - daysInMonth - startDow + 1, month: mo+1, year: y, other: true }});
  }}

  const rows = [];
  for (let r = 0; r < 6; r++) rows.push(cells.slice(r*7, r*7+7));

  const root = document.getElementById('calendar-root');
  root.innerHTML = '';

  const mv = document.createElement('div');
  mv.className = 'month-view';

  // Header
  const mh = document.createElement('div');
  mh.className = 'month-header';
  DAYS_JP.forEach(d => {{
    const c = document.createElement('div');
    c.className = 'month-header-cell';
    c.textContent = d;
    mh.appendChild(c);
  }});
  mv.appendChild(mh);

  const mg = document.createElement('div');
  mg.className = 'month-grid';

  rows.forEach(row => {{
    const mr = document.createElement('div');
    mr.className = 'month-row';
    row.forEach((cell, ci) => {{
      const cellDate = new Date(cell.year, cell.month, cell.day);
      const ds = fmt(cellDate);
      const dow = cellDate.getDay();
      const mc = document.createElement('div');
      mc.className = 'month-cell' +
        (cell.other ? ' other-month' : '') +
        (ds === today ? ' today' : '') +
        (dow === 0 ? ' sunday' : '') +
        (dow === 6 ? ' saturday' : '');

      const dn = document.createElement('div');
      dn.className = 'day-num';
      dn.textContent = cell.day;
      mc.appendChild(dn);

      // Show shifts for this date
      const dayShifts = shiftsOnDate(ds, filtered);
      const maxShow = 3;
      dayShifts.slice(0, maxShow).forEach(s => {{
        const chip = document.createElement('div');
        chip.className = 'month-shift-chip';
        const col = getDeptColor(s.dept);
        chip.style.background = hexToRgba(col, 0.25);
        chip.style.color = col;
        chip.style.borderLeft = `3px solid ${{col}}`;
        const st = parseShiftDate(s.start);
        const et = parseShiftDate(s.end);
        chip.textContent = `${{s.staff}} ${{String(st.getHours()).padStart(2,'0')}}:${{String(st.getMinutes()).padStart(2,'0')}}-${{String(et.getHours()).padStart(2,'0')}}:${{String(et.getMinutes()).padStart(2,'0')}}`;
        chip.onclick = (e) => {{ e.stopPropagation(); showDetail(s); }};
        mc.appendChild(chip);
      }});
      if (dayShifts.length > maxShow) {{
        const more = document.createElement('div');
        more.className = 'month-more';
        more.textContent = `+${{dayShifts.length - maxShow}}件`;
        mc.appendChild(more);
      }}

      mc.onclick = () => openRegModal(ds);
      mr.appendChild(mc);
    }});
    mg.appendChild(mr);
  }});
  mv.appendChild(mg);
  root.appendChild(mv);
}}

// ===================== WEEK VIEW =====================
function getWeekStart(date) {{
  const d = new Date(date);
  d.setDate(d.getDate() - d.getDay()); // Sunday start
  return d;
}}

function renderWeek() {{
  const ws = getWeekStart(currentDate);
  const we = new Date(ws); we.setDate(we.getDate()+6);
  const y1 = ws.getFullYear(), m1 = ws.getMonth()+1, d1 = ws.getDate();
  const y2 = we.getFullYear(), m2 = we.getMonth()+1, d2 = we.getDate();
  document.getElementById('period-label').textContent =
    y1 === y2
      ? `${{y1}}年${{m1}}/${{d1}} - ${{m2}}/${{d2}}`
      : `${{y1}}/${{m1}}/${{d1}} - ${{y2}}/${{m2}}/${{d2}}`;

  const today = todayStr();
  const filtered = getFilteredShifts();
  const hours = Array.from({{length:24}}, (_,i) => i);

  const root = document.getElementById('calendar-root');
  root.innerHTML = '';

  const wv = document.createElement('div');
  wv.className = 'week-view';

  // Header
  const wh = document.createElement('div');
  wh.className = 'week-header';
  const corner = document.createElement('div');
  corner.className = 'week-header-corner';
  wh.appendChild(corner);

  for (let i = 0; i < 7; i++) {{
    const d = new Date(ws); d.setDate(d.getDate() + i);
    const ds = fmt(d);
    const dow = d.getDay();
    const hd = document.createElement('div');
    hd.className = 'week-header-day' +
      (ds === today ? ' today-col' : '') +
      (dow === 0 ? ' sunday-col' : '') +
      (dow === 6 ? ' saturday-col' : '');
    hd.innerHTML = `<div class="week-dow">${{DAYS_JP[dow]}}</div><div class="week-date-num">${{d.getDate()}}</div>`;
    hd.onclick = () => {{ currentDate = new Date(d); setView('day'); }};
    wh.appendChild(hd);
  }}
  wv.appendChild(wh);

  // Body
  const wb = document.createElement('div');
  wb.className = 'week-body';

  // Time col
  const tc = document.createElement('div');
  tc.className = 'week-time-col';
  hours.forEach(h => {{
    const ts = document.createElement('div');
    ts.className = 'week-time-slot';
    ts.textContent = h > 0 ? String(h).padStart(2,'0') + ':00' : '';
    tc.appendChild(ts);
  }});
  wb.appendChild(tc);

  // Day columns
  const dc = document.createElement('div');
  dc.className = 'week-day-cols';

  for (let i = 0; i < 7; i++) {{
    const d = new Date(ws); d.setDate(d.getDate() + i);
    const ds = fmt(d);
    const dow = d.getDay();
    const col = document.createElement('div');
    col.className = 'week-day-col' + (ds === today ? ' today-col' : '');

    // Hour slots (background)
    hours.forEach(() => {{
      const hs = document.createElement('div');
      hs.className = 'week-hour-slot';
      col.appendChild(hs);
    }});

    // Drag handling
    setupDragOnCol(col, ds, null);

    // Shift blocks
    const dayShifts = shiftsOnDate(ds, filtered);
    dayShifts.forEach(s => {{
      const block = createShiftBlock(s, true);
      col.appendChild(block);
    }});

    dc.appendChild(col);
  }}
  wb.appendChild(dc);
  wv.appendChild(wb);
  root.appendChild(wv);
}}

// ===================== DAY VIEW =====================
function renderDay() {{
  const y = currentDate.getFullYear();
  const mo = currentDate.getMonth()+1;
  const d = currentDate.getDate();
  const dow = currentDate.getDay();
  document.getElementById('period-label').textContent =
    `${{y}}年${{mo}}月${{d}}日（${{DAYS_JP[dow]}}）`;

  const ds = fmt(currentDate);
  const today = todayStr();
  const filtered = getFilteredShifts();
  const hours = Array.from({{length:24}}, (_,i) => i);

  // Determine which staff to show
  const fsVal = document.getElementById('filter-staff')?.value || '';
  const staffToShow = fsVal ? [fsVal] : STAFF_LIST;

  const root = document.getElementById('calendar-root');
  root.innerHTML = '';

  if (staffToShow.length === 0) {{
    root.innerHTML = '<div class="empty-state"><div class="empty-icon">👥</div><div>先にスタッフを登録してください</div></div>';
    return;
  }}

  const dv = document.createElement('div');
  dv.className = 'day-view';

  // Staff header
  const sh = document.createElement('div');
  sh.className = 'day-staff-header';
  const corner = document.createElement('div');
  corner.className = 'day-time-corner';
  corner.textContent = ds === today ? '今日' : '';
  sh.appendChild(corner);

  staffToShow.forEach(staff => {{
    const hc = document.createElement('div');
    hc.className = 'day-staff-col-header';
    hc.textContent = staff;
    sh.appendChild(hc);
  }});
  dv.appendChild(sh);

  // Body
  const db = document.createElement('div');
  db.className = 'day-body';

  // Time col
  const tc = document.createElement('div');
  tc.className = 'day-time-col';
  hours.forEach(h => {{
    const ts = document.createElement('div');
    ts.className = 'day-time-slot';
    ts.textContent = h > 0 ? String(h).padStart(2,'0') + ':00' : '';
    tc.appendChild(ts);
  }});
  db.appendChild(tc);

  // Staff columns
  const sc = document.createElement('div');
  sc.className = 'day-staff-cols';

  staffToShow.forEach(staff => {{
    const col = document.createElement('div');
    col.className = 'day-staff-col';

    // Hour slots
    hours.forEach(() => {{
      const hs = document.createElement('div');
      hs.className = 'day-hour-slot';
      col.appendChild(hs);
    }});

    // Drag
    setupDragOnCol(col, ds, staff);

    // Shifts for this staff on this day
    const staffShifts = filtered.filter(s => {{
      if (s.staff !== staff) return false;
      if (!s.start) return false;
      return fmt(parseShiftDate(s.start)) === ds;
    }});
    staffShifts.forEach(s => {{
      const block = createShiftBlock(s, false);
      col.appendChild(block);
    }});

    sc.appendChild(col);
  }});
  db.appendChild(sc);
  dv.appendChild(db);
  root.appendChild(dv);
}}

// ===================== SHIFT BLOCKS =====================
const HOUR_HEIGHT = 48; // px per hour

function createShiftBlock(shift, showStaff) {{
  const st = parseShiftDate(shift.start);
  const et = parseShiftDate(shift.end);
  const startMins = st.getHours()*60 + st.getMinutes();
  const endMins = et.getHours()*60 + et.getMinutes();
  const top = (startMins / 60) * HOUR_HEIGHT;
  const height = Math.max(((endMins - startMins) / 60) * HOUR_HEIGHT, 16);
  const col = getDeptColor(shift.dept);

  const block = document.createElement('div');
  block.className = 'shift-block';
  block.style.top = top + 'px';
  block.style.height = height + 'px';
  block.style.background = hexToRgba(col, 0.3);
  block.style.borderLeft = `3px solid ${{col}}`;
  block.style.color = col;

  const nameEl = document.createElement('div');
  nameEl.className = 'sb-name';
  nameEl.textContent = showStaff ? shift.staff : shift.dept;
  block.appendChild(nameEl);

  if (height > 28) {{
    const timeEl = document.createElement('div');
    timeEl.className = 'sb-time';
    timeEl.textContent = `${{String(st.getHours()).padStart(2,'0')}}:${{String(st.getMinutes()).padStart(2,'0')}} - ${{String(et.getHours()).padStart(2,'0')}}:${{String(et.getMinutes()).padStart(2,'0')}}`;
    block.appendChild(timeEl);
  }}

  block.onclick = (e) => {{ e.stopPropagation(); showDetail(shift); }};
  return block;
}}

// ===================== DRAG SELECTION =====================
let dragState = null;

function setupDragOnCol(col, dateStr, staffName) {{
  let dragEl = null;
  let startY = 0;
  let startMins = 0;

  col.addEventListener('mousedown', (e) => {{
    if (e.button !== 0) return;
    if (e.target.classList.contains('shift-block')) return;
    e.preventDefault();

    const rect = col.getBoundingClientRect();
    const relY = e.clientY - rect.top + col.scrollTop;
    startY = relY;
    startMins = snapMins(yToMins(relY));

    dragEl = document.createElement('div');
    dragEl.className = 'drag-selection';
    dragEl.style.top = (startMins / 60 * HOUR_HEIGHT) + 'px';
    dragEl.style.height = '0px';
    col.appendChild(dragEl);
    dragState = {{ col, dateStr, staffName, startMins, dragEl }};
  }});

  col.addEventListener('mousemove', (e) => {{
    if (!dragState || dragState.col !== col) return;
    const rect = col.getBoundingClientRect();
    const relY = e.clientY - rect.top + col.scrollTop;
    const endMins = snapMins(yToMins(relY));
    const top = Math.min(dragState.startMins, endMins) / 60 * HOUR_HEIGHT;
    const height = Math.abs(endMins - dragState.startMins) / 60 * HOUR_HEIGHT;
    dragEl.style.top = top + 'px';
    dragEl.style.height = height + 'px';
    dragState.currentMins = endMins;
  }});

  col.addEventListener('mouseup', (e) => {{
    if (!dragState || dragState.col !== col) return;
    const endMins = dragState.currentMins || dragState.startMins + 60;
    const s = Math.min(dragState.startMins, endMins);
    const en = Math.max(dragState.startMins, endMins);
    if (dragEl) dragEl.remove();
    dragState = null;

    if (en - s < 15) {{
      // Too short: treat as click → open modal with defaults
      openRegModal(dateStr, minutesToTime(s), minutesToTime(s+60), staffName);
    }} else {{
      openRegModal(dateStr, minutesToTime(s), minutesToTime(en), staffName);
    }}
  }});
}}

document.addEventListener('mouseup', () => {{
  if (dragState && dragState.dragEl) dragState.dragEl.remove();
  dragState = null;
}});

function yToMins(y) {{
  return (y / HOUR_HEIGHT) * 60;
}}

function snapMins(mins) {{
  return Math.round(mins / 15) * 15; // 15分スナップ
}}

// ===================== MODAL =====================
function openRegModal(dateStr, startTime, endTime, staffName) {{
  document.getElementById('m-date').value = dateStr || fmt(currentDate);
  document.getElementById('m-start').value = startTime || '09:00';
  document.getElementById('m-end').value = endTime || '18:00';
  if (staffName) {{
    const sel = document.getElementById('m-staff');
    for (let o of sel.options) {{ if (o.value === staffName) {{ sel.value = staffName; break; }} }}
  }}
  document.getElementById('reg-modal').style.display = 'flex';
}}

function closeModal() {{
  document.getElementById('reg-modal').style.display = 'none';
}}

async function saveShift() {{
  const staff = document.getElementById('m-staff').value;
  const dept = document.getElementById('m-dept').value;
  const date = document.getElementById('m-date').value;
  const start = document.getElementById('m-start').value;
  const end = document.getElementById('m-end').value;

  if (!staff || !dept || !date || !start || !end) {{
    alert('すべての項目を入力してください');
    return;
  }}
  if (start >= end) {{
    alert('終了時間は開始時間より後にしてください');
    return;
  }}

  closeModal();
  showLoading();

  try {{
    const params = new URLSearchParams({{
      action: 'add_shift',
      name: staff,
      dept: dept,
      start: `${{date}} ${{start}}`,
      end: `${{date}} ${{end}}`
    }});
    await fetch(`${{GAS_URL}}?${{params}}`);

    // Optimistically add to local data
    SHIFTS.push({{
      staff, dept,
      start: `${{date}}T${{start}}:00`,
      end: `${{date}}T${{end}}:00`
    }});

    hideLoading();
    showToast('✅ シフトを保存しました');
    renderView();
  }} catch(err) {{
    hideLoading();
    showToast('❌ 保存に失敗しました');
    console.error(err);
  }}
}}

// ===================== DETAIL MODAL =====================
let currentDetailShift = null;
let currentDetailIndex = -1;

function showDetail(shift) {{
  currentDetailShift = shift;
  currentDetailIndex = SHIFTS.indexOf(shift);

  const st = parseShiftDate(shift.start);
  const et = parseShiftDate(shift.end);
  const col = getDeptColor(shift.dept);

  const content = document.getElementById('detail-content');
  content.innerHTML = `
    <span class="detail-chip" style="background:${{hexToRgba(col,0.25)}};color:${{col}}">${{shift.dept}}</span>
    <div class="detail-row"><span class="detail-icon">👤</span><span>${{shift.staff}}</span></div>
    <div class="detail-row"><span class="detail-icon">📅</span><span>${{fmt(st)}}</span></div>
    <div class="detail-row"><span class="detail-icon">🕐</span><span>${{String(st.getHours()).padStart(2,'0')}}:${{String(st.getMinutes()).padStart(2,'0')}} → ${{String(et.getHours()).padStart(2,'0')}}:${{String(et.getMinutes()).padStart(2,'0')}}</span></div>
    <div class="detail-row"><span class="detail-icon">⏱️</span><span>${{Math.round((et - st)/60000)}}分</span></div>
  `;
  document.getElementById('detail-modal').style.display = 'flex';
}}

function closeDetail() {{
  document.getElementById('detail-modal').style.display = 'none';
  currentDetailShift = null;
}}

async function deleteShift() {{
  if (!currentDetailShift) return;
  if (!confirm(`${{currentDetailShift.staff}} のシフトを削除しますか？`)) return;

  const s = currentDetailShift;
  closeDetail();
  showLoading();

  try {{
    const startStr = s.start.replace('T', ' ').slice(0,16);
    const params = new URLSearchParams({{
      action: 'del_shift',
      name: s.staff,
      dept: s.dept,
      start: startStr
    }});
    await fetch(`${{GAS_URL}}?${{params}}`);

    // Remove from local cache
    if (currentDetailIndex >= 0) SHIFTS.splice(currentDetailIndex, 1);

    hideLoading();
    showToast('🗑️ シフトを削除しました');
    renderView();
  }} catch(err) {{
    hideLoading();
    showToast('❌ 削除に失敗しました');
  }}
}}

// ===================== UI HELPERS =====================
function showToast(msg) {{
  const t = document.createElement('div');
  t.className = 'toast';
  t.textContent = msg;
  document.body.appendChild(t);
  setTimeout(() => t.remove(), 3000);
}}

function showLoading() {{
  const l = document.createElement('div');
  l.className = 'loading';
  l.id = 'loading-overlay';
  l.innerHTML = '<div class="spinner"></div><span>保存中...</span>';
  document.body.appendChild(l);
}}

function hideLoading() {{
  const l = document.getElementById('loading-overlay');
  if (l) l.remove();
}}

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {{
  if (e.key === 'Escape') {{ closeModal(); closeDetail(); }}
  if (e.key === 'ArrowLeft' && !e.target.matches('input,select')) navigate(-1);
  if (e.key === 'ArrowRight' && !e.target.matches('input,select')) navigate(1);
}});
</script>
</body>
</html>
"""

    components.html(html_code, height=700, scrolling=False)
