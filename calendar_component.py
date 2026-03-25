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
    日ビュー: 0時〜翌6時（30時間表示）
    """

    # DataFrameをJSON化（行インデックスも付与して削除時に照合に使う）
    shifts_json = []
    if not df.empty:
        for idx, row in df.iterrows():
            try:
                shifts_json.append({
                    "rowIndex": int(idx),
                    "staff": str(row.get("従業員", "")),
                    "dept": str(row.get("部門", "")),
                    "start": row["開始"].isoformat() if pd.notna(row["開始"]) else "",
                    "end": row["終了"].isoformat() if pd.notna(row["終了"]) else "",
                })
            except Exception:
                pass

    staff_json     = json.dumps(staff_list, ensure_ascii=False)
    dept_json      = json.dumps(dept_list, ensure_ascii=False)
    shifts_json_str = json.dumps(shifts_json, ensure_ascii=False)

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
<style>
  @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@300;400;500;700&family=JetBrains+Mono:wght@400;600&display=swap');

  :root {{
    --bg:#0f1117; --surface:#1a1d27; --surface2:#22263a; --border:#2d3148;
    --text:#e8eaf2; --text-muted:#6b7094; --accent:#5b8af0; --accent2:#8b5cf6;
    --success:#34d399; --danger:#f87171;
    --today:rgba(91,138,240,0.12); --hover:rgba(91,138,240,0.08);
    --drag:rgba(91,138,240,0.25); --next-day:rgba(139,92,246,0.06);
    --font:'Noto Sans JP',sans-serif; --mono:'JetBrains Mono',monospace;
  }}
  *{{margin:0;padding:0;box-sizing:border-box;}}
  body{{font-family:var(--font);background:var(--bg);color:var(--text);font-size:13px;user-select:none;}}

  /* TOP BAR */
  .topbar{{display:flex;align-items:center;gap:12px;padding:12px 16px;background:var(--surface);border-bottom:1px solid var(--border);flex-wrap:wrap;}}
  .view-tabs{{display:flex;background:var(--surface2);border-radius:8px;padding:3px;gap:2px;}}
  .view-tab{{padding:6px 16px;border-radius:6px;cursor:pointer;font-size:12px;font-weight:500;color:var(--text-muted);transition:all .18s;border:none;background:transparent;}}
  .view-tab.active{{background:var(--accent);color:#fff;box-shadow:0 2px 8px rgba(91,138,240,.4);}}
  .view-tab:hover:not(.active){{background:var(--hover);color:var(--text);}}
  .nav-group{{display:flex;align-items:center;gap:8px;}}
  .nav-btn{{width:32px;height:32px;border-radius:6px;border:1px solid var(--border);background:var(--surface2);color:var(--text);cursor:pointer;font-size:15px;display:flex;align-items:center;justify-content:center;transition:all .15s;}}
  .nav-btn:hover{{background:var(--hover);border-color:var(--accent);}}
  .period-label{{font-size:15px;font-weight:700;min-width:180px;text-align:center;}}
  .today-btn{{padding:6px 14px;border-radius:6px;border:1px solid var(--border);background:var(--surface2);color:var(--text);cursor:pointer;font-size:12px;font-family:var(--font);font-weight:500;transition:all .15s;}}
  .today-btn:hover{{border-color:var(--accent);color:var(--accent);}}
  .filter-group{{display:flex;gap:8px;margin-left:auto;align-items:center;}}
  .filter-select{{padding:5px 10px;border-radius:6px;border:1px solid var(--border);background:var(--surface2);color:var(--text);font-size:12px;font-family:var(--font);cursor:pointer;}}

  /* CALENDAR ROOT */
  #calendar-root{{flex:1;overflow:hidden;display:flex;flex-direction:column;}}

  /* MONTH */
  .month-view{{flex:1;display:flex;flex-direction:column;overflow:hidden;}}
  .month-header{{display:grid;grid-template-columns:repeat(7,1fr);border-bottom:1px solid var(--border);}}
  .month-header-cell{{padding:8px 0;text-align:center;font-size:11px;font-weight:600;color:var(--text-muted);letter-spacing:.08em;}}
  .month-header-cell:first-child{{color:#f87171;}}
  .month-header-cell:last-child{{color:#60a5fa;}}
  .month-grid{{flex:1;display:grid;grid-template-rows:repeat(6,1fr);overflow-y:auto;}}
  .month-row{{display:grid;grid-template-columns:repeat(7,1fr);border-bottom:1px solid var(--border);min-height:100px;}}
  .month-cell{{border-right:1px solid var(--border);padding:6px;cursor:pointer;transition:background .12s;overflow:hidden;min-height:90px;}}
  .month-cell:hover{{background:var(--hover);}}
  .month-cell.other-month{{opacity:.35;}}
  .month-cell.today{{background:var(--today);}}
  .month-cell.sunday .day-num{{color:#f87171;}}
  .month-cell.saturday .day-num{{color:#60a5fa;}}
  .day-num{{font-size:12px;font-weight:600;margin-bottom:4px;width:24px;height:24px;display:flex;align-items:center;justify-content:center;border-radius:50%;font-family:var(--mono);}}
  .today .day-num{{background:var(--accent);color:#fff;}}
  .month-shift-chip{{font-size:10px;padding:2px 5px;border-radius:3px;margin-bottom:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-weight:500;cursor:pointer;}}
  .month-more{{font-size:10px;color:var(--text-muted);padding:1px 4px;cursor:pointer;}}
  .month-more:hover{{color:var(--accent);}}

  /* WEEK */
  .week-view{{flex:1;display:flex;flex-direction:column;overflow:hidden;}}
  .week-header{{display:grid;grid-template-columns:56px repeat(7,1fr);border-bottom:2px solid var(--border);background:var(--surface);flex-shrink:0;}}
  .week-header-corner{{padding:10px 0;}}
  .week-header-day{{padding:8px 4px;text-align:center;border-left:1px solid var(--border);cursor:pointer;}}
  .week-header-day:hover{{background:var(--hover);}}
  .week-dow{{font-size:10px;font-weight:600;letter-spacing:.1em;text-transform:uppercase;color:var(--text-muted);}}
  .week-date-num{{font-size:20px;font-weight:700;font-family:var(--mono);line-height:1.2;}}
  .week-header-day.today-col .week-date-num{{color:var(--accent);}}
  .week-header-day.sunday-col .week-dow,.week-header-day.sunday-col .week-date-num{{color:#f87171;}}
  .week-header-day.saturday-col .week-dow,.week-header-day.saturday-col .week-date-num{{color:#60a5fa;}}
  .week-body{{flex:1;display:flex;overflow-y:auto;}}
  .week-time-col{{width:56px;flex-shrink:0;border-right:1px solid var(--border);background:var(--surface);position:sticky;left:0;z-index:2;}}
  .week-time-slot{{height:48px;padding:4px 6px 0;border-bottom:1px solid var(--border);font-size:10px;color:var(--text-muted);font-family:var(--mono);text-align:right;}}
  .week-day-cols{{flex:1;display:grid;grid-template-columns:repeat(7,1fr);}}
  .week-day-col{{border-right:1px solid var(--border);position:relative;cursor:crosshair;}}
  .week-day-col.today-col{{background:var(--today);}}
  .week-hour-slot{{height:48px;border-bottom:1px solid var(--border);}}

  /* DAY */
  .day-view{{flex:1;display:flex;flex-direction:column;overflow:hidden;}}
  .day-staff-header{{display:flex;border-bottom:2px solid var(--border);background:var(--surface);flex-shrink:0;}}
  .day-time-corner{{width:64px;min-width:64px;flex-shrink:0;padding:10px 6px;font-size:10px;color:var(--text-muted);text-align:center;border-right:1px solid var(--border);}}
  .day-staff-col-header{{flex:1;min-width:100px;padding:8px 6px;text-align:center;border-right:1px solid var(--border);font-weight:600;font-size:12px;white-space:nowrap;}}
  .day-body{{flex:1;display:flex;overflow-y:auto;position:relative;}}
  .day-time-col{{width:64px;min-width:64px;flex-shrink:0;border-right:1px solid var(--border);background:var(--surface);position:sticky;left:0;z-index:2;}}
  .day-time-slot{{height:48px;padding:4px 8px 0;border-bottom:1px solid var(--border);font-size:10px;color:var(--text-muted);font-family:var(--mono);text-align:right;}}
  .day-time-slot.day-boundary{{border-top:2px solid var(--accent2);color:var(--accent2);font-weight:700;}}
  .day-staff-cols{{flex:1;display:flex;overflow-x:auto;}}
  .day-staff-col{{flex:1;min-width:100px;border-right:1px solid var(--border);position:relative;cursor:crosshair;}}
  .day-hour-slot{{height:48px;border-bottom:1px solid var(--border);}}
  .next-day-zone{{position:absolute;left:0;right:0;background:var(--next-day);border-top:1px dashed var(--accent2);pointer-events:none;z-index:0;}}

  /* SHIFT BLOCK */
  .shift-block{{position:absolute;left:2px;right:2px;border-radius:4px;padding:3px 5px;font-size:10px;font-weight:600;overflow:hidden;z-index:1;cursor:pointer;transition:filter .12s;border:1px solid rgba(255,255,255,.1);}}
  .shift-block:hover{{filter:brightness(1.2);z-index:3;}}
  .sb-name{{white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}}
  .sb-time{{font-size:9px;opacity:.8;font-family:var(--mono);}}

  /* DRAG */
  .drag-selection{{position:absolute;left:2px;right:2px;background:var(--drag);border:2px dashed var(--accent);border-radius:4px;z-index:10;pointer-events:none;}}

  /* CURRENT TIME LINE */
  .now-line{{position:absolute;left:0;right:0;height:2px;background:#f87171;z-index:5;pointer-events:none;}}
  .now-line::before{{content:'';position:absolute;left:-4px;top:-3px;width:8px;height:8px;border-radius:50%;background:#f87171;}}

  /* MODAL */
  .modal-overlay{{position:fixed;inset:0;background:rgba(0,0,0,.65);z-index:1000;display:flex;align-items:center;justify-content:center;backdrop-filter:blur(4px);}}
  .modal{{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:24px;width:380px;max-width:95vw;box-shadow:0 20px 60px rgba(0,0,0,.5);animation:modalIn .2s ease;}}
  @keyframes modalIn{{from{{transform:scale(.92);opacity:0;}}to{{transform:scale(1);opacity:1;}}}}
  .modal-title{{font-size:16px;font-weight:700;margin-bottom:20px;display:flex;align-items:center;gap:8px;}}
  .form-group{{margin-bottom:14px;}}
  .form-label{{display:block;font-size:11px;font-weight:600;color:var(--text-muted);text-transform:uppercase;letter-spacing:.08em;margin-bottom:6px;}}
  .form-input,.form-select{{width:100%;padding:9px 12px;border-radius:6px;border:1px solid var(--border);background:var(--surface2);color:var(--text);font-size:13px;font-family:var(--font);transition:border-color .15s;}}
  .form-input:focus,.form-select:focus{{outline:none;border-color:var(--accent);box-shadow:0 0 0 3px rgba(91,138,240,.15);}}
  .time-row{{display:grid;grid-template-columns:1fr auto 1fr;align-items:center;gap:8px;}}
  .time-sep{{color:var(--text-muted);font-size:16px;text-align:center;}}
  .modal-actions{{display:flex;gap:10px;margin-top:20px;}}
  .btn{{flex:1;padding:10px;border-radius:6px;border:none;font-size:13px;font-family:var(--font);font-weight:600;cursor:pointer;transition:all .15s;}}
  .btn-primary{{background:var(--accent);color:#fff;}}
  .btn-primary:hover{{background:#4a77e0;box-shadow:0 4px 12px rgba(91,138,240,.4);}}
  .btn-secondary{{background:var(--surface2);color:var(--text);border:1px solid var(--border);}}
  .btn-secondary:hover{{border-color:var(--accent);color:var(--accent);}}
  .btn-danger{{background:var(--danger);color:#fff;flex:0;padding:10px 16px;}}
  .btn-danger:hover{{background:#ef4444;}}
  .detail-chip{{display:inline-block;padding:3px 10px;border-radius:20px;font-size:12px;font-weight:600;margin-bottom:14px;}}
  .detail-row{{display:flex;align-items:center;gap:10px;padding:8px 0;border-bottom:1px solid var(--border);font-size:13px;}}
  .detail-row:last-child{{border-bottom:none;}}
  .detail-icon{{font-size:16px;width:24px;text-align:center;}}

  /* TOAST */
  .toast{{position:fixed;bottom:20px;right:20px;background:var(--success);color:#fff;padding:12px 20px;border-radius:8px;font-weight:600;font-size:13px;z-index:9999;box-shadow:0 8px 24px rgba(52,211,153,.4);animation:toastIn .3s ease;max-width:320px;}}
  .toast.error{{background:var(--danger);box-shadow:0 8px 24px rgba(248,113,113,.4);}}
  .toast.warn{{background:#f59e0b;box-shadow:0 8px 24px rgba(245,158,11,.4);}}
  @keyframes toastIn{{from{{transform:translateY(20px);opacity:0;}}to{{transform:translateY(0);opacity:1;}}}}
  .loading{{position:fixed;inset:0;background:rgba(0,0,0,.5);display:flex;align-items:center;justify-content:center;z-index:9998;font-size:14px;color:var(--text);gap:10px;}}
  .spinner{{width:20px;height:20px;border:2px solid var(--border);border-top-color:var(--accent);border-radius:50%;animation:spin .7s linear infinite;}}
  @keyframes spin{{to{{transform:rotate(360deg);}}}}
</style>
</head>
<body>
<div style="display:flex;flex-direction:column;height:100vh;">

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
      <select class="filter-select" id="filter-staff" onchange="renderView()"><option value="">全スタッフ</option></select>
      <select class="filter-select" id="filter-dept"  onchange="renderView()"><option value="">全部門</option></select>
    </div>
  </div>

  <div id="calendar-root"></div>
</div>

<!-- REGISTER MODAL -->
<div class="modal-overlay" id="reg-modal" style="display:none" onclick="if(event.target===this)closeModal()">
  <div class="modal">
    <div class="modal-title">📋 シフト登録</div>
    <div class="form-group"><label class="form-label">従業員</label><select class="form-select" id="m-staff"></select></div>
    <div class="form-group"><label class="form-label">部門</label><select class="form-select" id="m-dept"></select></div>
    <div class="form-group"><label class="form-label">日付</label><input type="date" class="form-input" id="m-date"></div>
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
    <div class="modal-title">📌 シフト詳細</div>
    <div id="detail-content"></div>
    <div class="modal-actions" style="margin-top:16px">
      <button class="btn btn-secondary" onclick="closeDetail()">閉じる</button>
      <button class="btn btn-danger" onclick="deleteShift()">削除</button>
    </div>
  </div>
</div>

<script>
const GAS_URL    = "{gas_url}";
const STAFF_LIST = {staff_json};
const DEPT_LIST  = {dept_json};
let   SHIFTS     = {shifts_json_str};

const COLORS = {color_palette};

function getDeptColor(dept) {{
  const i = DEPT_LIST.indexOf(dept);
  if (i >= 0) return COLORS[i % COLORS.length];
  let h = 0; for (let c of dept) h = (h*31+c.charCodeAt(0))&0xffffffff;
  return COLORS[Math.abs(h) % COLORS.length];
}}
function hexToRgba(hex, a) {{
  return `rgba(${{parseInt(hex.slice(1,3),16)}},${{parseInt(hex.slice(3,5),16)}},${{parseInt(hex.slice(5,7),16)}},${{a}})`;
}}

// STATE
let currentView = 'day';
let currentDate = new Date(); currentDate.setHours(0,0,0,0);

// Day view constants: 0:00〜翌6:00（30時間）
const DAY_START_H = 0;
const DAY_END_H   = 30;   // 翌6時 = hour index 30
const DAY_HOURS   = 30;
const MIDNIGHT_H  = 24;   // 翌0時の区切り
const HOUR_PX     = 48;

// INIT
window.onload = () => {{
  ['filter-staff','m-staff'].forEach(id => STAFF_LIST.forEach(s => document.getElementById(id).appendChild(new Option(s,s))));
  ['filter-dept', 'm-dept' ].forEach(id => DEPT_LIST.forEach(d => document.getElementById(id).appendChild(new Option(d,d))));
  renderView();
}};

// VIEW CONTROL
function setView(v) {{
  currentView = v;
  document.querySelectorAll('.view-tab').forEach((el,i) => el.classList.toggle('active', ['day','week','month'][i]===v));
  renderView();
}}
function navigate(dir) {{
  if (currentView==='day')        currentDate.setDate(currentDate.getDate()+dir);
  else if (currentView==='week')  currentDate.setDate(currentDate.getDate()+dir*7);
  else                            currentDate.setMonth(currentDate.getMonth()+dir);
  renderView();
}}
function goToday() {{ currentDate=new Date(); currentDate.setHours(0,0,0,0); renderView(); }}
function getFilteredShifts() {{
  const fs=document.getElementById('filter-staff')?.value||'';
  const fd=document.getElementById('filter-dept')?.value||'';
  return SHIFTS.filter(s=>(!fs||s.staff===fs)&&(!fd||s.dept===fd));
}}
function renderView() {{
  if (currentView==='day') renderDay();
  else if (currentView==='week') renderWeek();
  else renderMonth();
}}

// DATE UTILS
const DAYS_JP=['日','月','火','水','木','金','土'];
const MONTHS_JP=['1月','2月','3月','4月','5月','6月','7月','8月','9月','10月','11月','12月'];
function fmt(d) {{ return `${{d.getFullYear()}}-${{String(d.getMonth()+1).padStart(2,'0')}}-${{String(d.getDate()).padStart(2,'0')}}`; }}
function todayStr() {{ return fmt(new Date()); }}
function parseD(s) {{ return new Date(s); }}
function shiftsOn(ds, shifts) {{ return shifts.filter(s=>s.start&&fmt(parseD(s.start))===ds); }}
function minsToTime(m) {{ const mm=m%1440; return `${{String(Math.floor(mm/60)).padStart(2,'0')}}:${{String(mm%60).padStart(2,'0')}}`; }}
function mk(tag, cls, extra) {{ const e=document.createElement(tag); if(cls)e.className=cls; if(extra)Object.assign(e,extra); return e; }}

// ===== MONTH =====
function renderMonth() {{
  const y=currentDate.getFullYear(), mo=currentDate.getMonth();
  document.getElementById('period-label').textContent=`${{y}}年 ${{MONTHS_JP[mo]}}`;
  const first=new Date(y,mo,1), sdow=first.getDay(), dim=new Date(y,mo+1,0).getDate(), prev=new Date(y,mo,0).getDate();
  const today=todayStr(), fil=getFilteredShifts();
  let cells=[];
  for(let i=sdow-1;i>=0;i--) cells.push({{day:prev-i,month:mo-1,year:y,other:true}});
  for(let d=1;d<=dim;d++) cells.push({{day:d,month:mo,year:y,other:false}});
  while(cells.length<42) cells.push({{day:cells.length-dim-sdow+1,month:mo+1,year:y,other:true}});
  const rows=[]; for(let r=0;r<6;r++) rows.push(cells.slice(r*7,r*7+7));

  const root=document.getElementById('calendar-root'); root.innerHTML='';
  const mv=mk('div','month-view');
  const mh=mk('div','month-header');
  DAYS_JP.forEach(d=>{{ const c=mk('div','month-header-cell'); c.textContent=d; mh.appendChild(c); }});
  mv.appendChild(mh);
  const mg=mk('div','month-grid');
  rows.forEach(row=>{{
    const mr=mk('div','month-row');
    row.forEach(cell=>{{
      const cd=new Date(cell.year,cell.month,cell.day), ds=fmt(cd), dow=cd.getDay();
      const mc=mk('div','month-cell'+(cell.other?' other-month':'')+(ds===today?' today':'')+(dow===0?' sunday':dow===6?' saturday':''));
      const dn=mk('div','day-num'); dn.textContent=cell.day; mc.appendChild(dn);
      const ds_shifts=shiftsOn(ds,fil);
      ds_shifts.slice(0,3).forEach(s=>{{
        const col=getDeptColor(s.dept), chip=mk('div','month-shift-chip');
        chip.style.cssText=`background:${{hexToRgba(col,.25)}};color:${{col}};border-left:3px solid ${{col}}`;
        const st=parseD(s.start),et=parseD(s.end);
        chip.textContent=`${{s.staff}} ${{String(st.getHours()).padStart(2,'0')}}:${{String(st.getMinutes()).padStart(2,'0')}}-${{String(et.getHours()).padStart(2,'0')}}:${{String(et.getMinutes()).padStart(2,'0')}}`;
        chip.onclick=e=>{{e.stopPropagation();showDetail(s);}};
        mc.appendChild(chip);
      }});
      if(ds_shifts.length>3){{const m=mk('div','month-more');m.textContent=`+${{ds_shifts.length-3}}件`;mc.appendChild(m);}}
      mc.onclick=()=>openRegModal(ds);
      mr.appendChild(mc);
    }});
    mg.appendChild(mr);
  }});
  mv.appendChild(mg); root.appendChild(mv);
}}

// ===== WEEK =====
function getWeekStart(d) {{ const r=new Date(d); r.setDate(r.getDate()-r.getDay()); return r; }}
function renderWeek() {{
  const ws=getWeekStart(currentDate), we=new Date(ws); we.setDate(we.getDate()+6);
  const [y1,m1,d1]=[ws.getFullYear(),ws.getMonth()+1,ws.getDate()];
  const [y2,m2,d2]=[we.getFullYear(),we.getMonth()+1,we.getDate()];
  document.getElementById('period-label').textContent=y1===y2?`${{y1}}年${{m1}}/${{d1}} - ${{m2}}/${{d2}}`:`${{y1}}/${{m1}}/${{d1}} - ${{y2}}/${{m2}}/${{d2}}`;
  const today=todayStr(), fil=getFilteredShifts();
  const root=document.getElementById('calendar-root'); root.innerHTML='';
  const wv=mk('div','week-view');
  const wh=mk('div','week-header'); wh.appendChild(mk('div','week-header-corner'));
  for(let i=0;i<7;i++){{
    const d=new Date(ws); d.setDate(d.getDate()+i);
    const ds=fmt(d),dow=d.getDay();
    const hd=mk('div','week-header-day'+(ds===today?' today-col':'')+(dow===0?' sunday-col':dow===6?' saturday-col':''));
    hd.innerHTML=`<div class="week-dow">${{DAYS_JP[dow]}}</div><div class="week-date-num">${{d.getDate()}}</div>`;
    hd.onclick=()=>{{currentDate=new Date(d);setView('day');}};
    wh.appendChild(hd);
  }}
  wv.appendChild(wh);
  const wb=mk('div','week-body');
  const tc=mk('div','week-time-col');
  for(let h=0;h<24;h++){{const ts=mk('div','week-time-slot');ts.textContent=h>0?String(h).padStart(2,'0')+':00':'';tc.appendChild(ts);}}
  wb.appendChild(tc);
  const dc=mk('div','week-day-cols');
  for(let i=0;i<7;i++){{
    const d=new Date(ws); d.setDate(d.getDate()+i);
    const ds=fmt(d),dow=d.getDay();
    const col=mk('div','week-day-col'+(ds===today?' today-col':''));
    for(let h=0;h<24;h++) col.appendChild(mk('div','week-hour-slot'));
    setupDragWeek(col,ds,null);
    shiftsOn(ds,fil).forEach(s=>col.appendChild(makeBlock(s,true,false,0)));
    dc.appendChild(col);
  }}
  wb.appendChild(dc); wv.appendChild(wb); root.appendChild(wv);
}}

// ===== DAY VIEW（0:00〜翌6:00）=====
function renderDay() {{
  const y=currentDate.getFullYear(),mo=currentDate.getMonth()+1,d=currentDate.getDate(),dow=currentDate.getDay();
  document.getElementById('period-label').textContent=`${{y}}年${{mo}}月${{d}}日（${{DAYS_JP[dow]}}）`;
  const ds=fmt(currentDate);
  const nextDate=new Date(currentDate); nextDate.setDate(nextDate.getDate()+1);
  const dsNext=fmt(nextDate);
  const today=todayStr(), fil=getFilteredShifts();
  const fsVal=document.getElementById('filter-staff')?.value||'';
  const staffShow=fsVal?[fsVal]:STAFF_LIST;
  const root=document.getElementById('calendar-root'); root.innerHTML='';

  if(!staffShow.length){{root.innerHTML='<div style="display:flex;align-items:center;justify-content:center;height:200px;color:var(--text-muted)">スタッフを登録してください</div>';return;}}

  const dv=mk('div','day-view');
  const sh=mk('div','day-staff-header');
  const corn=mk('div','day-time-corner');
  corn.innerHTML=ds===today?'<span style="color:var(--accent);font-weight:700">今日</span>':'';
  sh.appendChild(corn);
  staffShow.forEach(st=>{{const h=mk('div','day-staff-col-header');h.textContent=st;sh.appendChild(h);}});
  dv.appendChild(sh);

  const db=mk('div','day-body');

  // 時間列（30時間分）
  const tc=mk('div','day-time-col');
  for(let h=DAY_START_H;h<DAY_END_H;h++){{
    const ts=mk('div','day-time-slot'+(h===MIDNIGHT_H?' day-boundary':''));
    if(h===0) ts.textContent='';
    else if(h===MIDNIGHT_H) ts.textContent='翌 00:00';
    else if(h>MIDNIGHT_H) ts.textContent=String(h-24).padStart(2,'0')+':00';
    else ts.textContent=String(h).padStart(2,'0')+':00';
    tc.appendChild(ts);
  }}
  db.appendChild(tc);

  const sc=mk('div','day-staff-cols');
  const midPx=MIDNIGHT_H*HOUR_PX;

  staffShow.forEach(staff=>{{
    const col=mk('div','day-staff-col');
    for(let h=0;h<DAY_HOURS;h++) col.appendChild(mk('div','day-hour-slot'));

    // 翌日ゾーン背景
    const nz=mk('div','next-day-zone');
    nz.style.top=midPx+'px'; nz.style.bottom='0';
    col.appendChild(nz);

    setupDragDay(col, ds, dsNext, staff);

    // 当日シフト
    fil.filter(s=>s.staff===staff&&s.start&&fmt(parseD(s.start))===ds)
       .forEach(s=>col.appendChild(makeBlock(s,false,false,0)));
    // 翌日シフト（0:00〜6:00）→ +1440分オフセット
    fil.filter(s=>s.staff===staff&&s.start&&fmt(parseD(s.start))===dsNext)
       .forEach(s=>{{
         const st=parseD(s.start), et=parseD(s.end);
         const sh=st.getHours(), eh=et.getHours();
         // 翌日6時以前のシフトだけ表示（夜勤帯）
         if(sh < (DAY_END_H - MIDNIGHT_H)) col.appendChild(makeBlock(s,false,true,1440));
       }});

    sc.appendChild(col);
  }});
  db.appendChild(sc); dv.appendChild(db); root.appendChild(dv);

  // 現在時刻ライン
  const now=new Date(), diffMins=(now-currentDate)/60000;
  if(diffMins>=0 && diffMins<DAY_HOURS*60) {{
    const line=mk('div','now-line');
    line.style.cssText=`position:absolute;left:64px;right:0;top:${{diffMins/60*HOUR_PX}}px;height:2px;background:#f87171;z-index:5;pointer-events:none;`;
    db.style.position='relative';
    db.appendChild(line);
  }}
}}

// ===== SHIFT BLOCK =====
function makeBlock(shift, showStaff, isNext, offsetMins) {{
  const st=parseD(shift.start), et=parseD(shift.end);
  let sm=st.getHours()*60+st.getMinutes()+offsetMins;
  let em=et.getHours()*60+et.getMinutes()+offsetMins;
  const top=(sm/60)*HOUR_PX;
  const h=Math.max(((em-sm)/60)*HOUR_PX, 16);
  const col=getDeptColor(shift.dept);
  const b=mk('div','shift-block');
  b.style.cssText=`top:${{top}}px;height:${{h}}px;background:${{hexToRgba(col,.3)}};border-left:3px solid ${{col}};color:${{col}};`;
  const nm=mk('div','sb-name'); nm.textContent=showStaff?shift.staff:shift.dept; b.appendChild(nm);
  if(h>28){{const tm=mk('div','sb-time');tm.textContent=`${{String(st.getHours()).padStart(2,'0')}}:${{String(st.getMinutes()).padStart(2,'0')}} - ${{String(et.getHours()).padStart(2,'0')}}:${{String(et.getMinutes()).padStart(2,'0')}}`;b.appendChild(tm);}}
  b.onclick=e=>{{e.stopPropagation();showDetail(shift);}};
  return b;
}}

// ===== DRAG =====
let dragState=null;
function yToMins(y) {{ return y/HOUR_PX*60; }}
function snap(m) {{ return Math.round(m/15)*15; }}

function setupDragWeek(col, dateStr, staff) {{
  let el=null;
  col.addEventListener('mousedown',e=>{{
    if(e.button||e.target.classList.contains('shift-block')) return; e.preventDefault();
    const y=e.clientY-col.getBoundingClientRect().top+col.scrollTop;
    const sm=snap(yToMins(y));
    el=mk('div','drag-selection'); el.style.top=sm/60*HOUR_PX+'px'; el.style.height='0'; col.appendChild(el);
    dragState={{col,dateStr,staff,sm,em:sm,el}};
  }});
  col.addEventListener('mousemove',e=>{{
    if(!dragState||dragState.col!==col) return;
    const em=snap(yToMins(e.clientY-col.getBoundingClientRect().top+col.scrollTop));
    el.style.top=Math.min(dragState.sm,em)/60*HOUR_PX+'px';
    el.style.height=Math.abs(em-dragState.sm)/60*HOUR_PX+'px';
    dragState.em=em;
  }});
  col.addEventListener('mouseup',()=>{{
    if(!dragState||dragState.col!==col) return;
    const s=Math.min(dragState.sm,dragState.em), en=Math.max(dragState.sm,dragState.em);
    el.remove(); dragState=null;
    openRegModal(dateStr,minsToTime(s),minsToTime(en-s<15?s+60:en),staff);
  }});
}}

function setupDragDay(col, ds, dsNext, staff) {{
  let el=null;
  col.addEventListener('mousedown',e=>{{
    if(e.button||e.target.classList.contains('shift-block')) return; e.preventDefault();
    const y=e.clientY-col.getBoundingClientRect().top+col.scrollTop;
    const sm=Math.min(snap(yToMins(y)), DAY_HOURS*60);
    el=mk('div','drag-selection'); el.style.top=sm/60*HOUR_PX+'px'; el.style.height='0'; col.appendChild(el);
    dragState={{col,ds,dsNext,staff,sm,em:sm,el,day:true}};
  }});
  col.addEventListener('mousemove',e=>{{
    if(!dragState||dragState.col!==col) return;
    const em=Math.min(snap(yToMins(e.clientY-col.getBoundingClientRect().top+col.scrollTop)),DAY_HOURS*60);
    el.style.top=Math.min(dragState.sm,em)/60*HOUR_PX+'px';
    el.style.height=Math.abs(em-dragState.sm)/60*HOUR_PX+'px';
    dragState.em=em;
  }});
  col.addEventListener('mouseup',()=>{{
    if(!dragState||dragState.col!==col) return;
    const s=Math.min(dragState.sm,dragState.em), en=Math.max(dragState.sm,dragState.em);
    el.remove();
    const isNext=s>=1440;
    const actualDate=isNext?dragState.dsNext:dragState.ds;
    dragState=null;
    openRegModal(actualDate,minsToTime(s),minsToTime(en-s<15?s+60:en),staff);
  }});
}}

document.addEventListener('mouseup',()=>{{ if(dragState?.el) dragState.el.remove(); dragState=null; }});

// ===== MODAL =====
function openRegModal(dateStr, s, e, staff) {{
  document.getElementById('m-date').value=dateStr||fmt(currentDate);
  document.getElementById('m-start').value=s||'09:00';
  document.getElementById('m-end').value=e||'18:00';
  if(staff){{ const sel=document.getElementById('m-staff'); for(let o of sel.options) if(o.value===staff){{sel.value=staff;break;}} }}
  document.getElementById('reg-modal').style.display='flex';
}}
function closeModal() {{ document.getElementById('reg-modal').style.display='none'; }}

async function saveShift() {{
  const staff=document.getElementById('m-staff').value, dept=document.getElementById('m-dept').value;
  const date=document.getElementById('m-date').value, s=document.getElementById('m-start').value, e=document.getElementById('m-end').value;
  if(!staff||!dept||!date||!s||!e){{alert('すべて入力してください');return;}}
  if(s>=e){{alert('終了は開始より後にしてください');return;}}
  closeModal(); showLoading('保存中...');
  try{{
    await fetch(`${{GAS_URL}}?`+new URLSearchParams({{action:'add_shift',name:staff,dept,start:`${{date}} ${{s}}`,end:`${{date}} ${{e}}`}}));
    SHIFTS.push({{rowIndex:-1,staff,dept,start:`${{date}}T${{s}}:00`,end:`${{date}}T${{e}}:00`}});
    hideLoading(); showToast('✅ シフトを保存しました'); renderView();
  }}catch(err){{hideLoading();showToast('❌ 保存に失敗しました',true);}}
}}

// ===== DETAIL + DELETE =====
let curShift=null, curIdx=-1;
function showDetail(shift) {{
  curShift=shift; curIdx=SHIFTS.indexOf(shift);
  const st=parseD(shift.start),et=parseD(shift.end),col=getDeptColor(shift.dept);
  document.getElementById('detail-content').innerHTML=`
    <span class="detail-chip" style="background:${{hexToRgba(col,.25)}};color:${{col}}">${{shift.dept}}</span>
    <div class="detail-row"><span class="detail-icon">👤</span><span>${{shift.staff}}</span></div>
    <div class="detail-row"><span class="detail-icon">📅</span><span>${{fmt(st)}}</span></div>
    <div class="detail-row"><span class="detail-icon">🕐</span><span>${{String(st.getHours()).padStart(2,'0')}}:${{String(st.getMinutes()).padStart(2,'0')}} → ${{String(et.getHours()).padStart(2,'0')}}:${{String(et.getMinutes()).padStart(2,'0')}}</span></div>
    <div class="detail-row"><span class="detail-icon">⏱️</span><span>${{Math.round((et-st)/60000)}}分</span></div>`;
  document.getElementById('detail-modal').style.display='flex';
}}
function closeDetail() {{ document.getElementById('detail-modal').style.display='none'; curShift=null; }}

async function deleteShift() {{
  if(!curShift) return;
  if(!confirm(`${{curShift.staff}} のシフトを削除しますか？`)) return;
  const s=curShift; closeDetail(); showLoading('削除中...');

  // ISO文字列を "YYYY-MM-DD HH:MM" に正規化
  const norm=iso=>iso.replace('T',' ').replace(/(\d{{4}}-\d{{2}}-\d{{2}} \d{{2}}:\d{{2}}).*$/,'$1');
  const startStr=norm(s.start), endStr=norm(s.end);

  let ok=false;
  try{{
    const res=await fetch(`${{GAS_URL}}?`+new URLSearchParams({{action:'del_shift',name:s.staff,dept:s.dept,start:startStr,end:endStr}}));
    const txt=await res.text();
    ok=res.ok && (txt.toLowerCase().includes('delet')||txt.toLowerCase().includes('ok')||txt.trim().length===0);
  }}catch(e){{ console.warn('GAS del_shift error:',e); }}

  // ローカルから除去（GAS結果に関係なく即反映）
  const i=curIdx>=0 ? curIdx : SHIFTS.findIndex(x=>x.staff===s.staff&&x.dept===s.dept&&x.start===s.start);
  if(i>=0) SHIFTS.splice(i,1);

  hideLoading();
  if(ok) showToast('🗑️ 削除しました');
  else   showToast('🗑️ 画面から削除しました\n（GASにdel_shiftが未設定の場合はシートも手動削除してください）','warn');
  renderView();
}}

// ===== HELPERS =====
function showToast(msg, type='', dur=4000) {{
  const t=mk('div','toast'+(type?' '+type:'')); t.textContent=msg;
  document.body.appendChild(t); setTimeout(()=>t.remove(),dur);
}}
function showLoading(msg='処理中...') {{
  const l=mk('div','loading'); l.id='loading-overlay';
  l.innerHTML=`<div class="spinner"></div><span>${{msg}}</span>`; document.body.appendChild(l);
}}
function hideLoading() {{ document.getElementById('loading-overlay')?.remove(); }}

document.addEventListener('keydown',e=>{{
  if(e.key==='Escape'){{closeModal();closeDetail();}}
  if(e.key==='ArrowLeft'&&!e.target.matches('input,select')) navigate(-1);
  if(e.key==='ArrowRight'&&!e.target.matches('input,select')) navigate(1);
}});
</script>
</body>
</html>
"""

    components.html(html_code, height=760, scrolling=False)
