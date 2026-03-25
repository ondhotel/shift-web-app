import streamlit.components.v1 as components
import json
import pandas as pd

def render_calendar_component(df: pd.DataFrame, staff_list: list, dept_list: list, gas_url: str):
    """
    カレンダービューコンポーネント（フル版）
    - 日跨ぎシフトの分割表示対応
    - 日ビュー: 0時〜翌6時（30時間表示）
    - Python f-stringのエスケープ処理済み
    """

    # DataFrameをJSON化
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
            except: pass

    # JSON文字列化（JSに渡す用）
    staff_json = json.dumps(staff_list, ensure_ascii=False)
    dept_json = json.dumps(dept_list, ensure_ascii=False)
    shifts_json_str = json.dumps(shifts_json, ensure_ascii=False)
    
    color_palette = [
        "#4f86c6", "#e07b5a", "#5aad8f", "#b07fc7", "#e0b84a",
        "#5abfcc", "#e07bb0", "#7ec45a", "#c47e5a", "#5a7ec4"
    ]

    # HTML/JS/CSS (JSの波括弧は {{ }} でエスケープ)
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
  body{{font-family:var(--font);background:var(--bg);color:var(--text);font-size:13px;user-select:none;overflow:hidden;}}
  
  .topbar{{display:flex;align-items:center;gap:12px;padding:12px 16px;background:var(--surface);border-bottom:1px solid var(--border);}}
  .view-tabs{{display:flex;background:var(--surface2);border-radius:8px;padding:3px;gap:2px;}}
  .view-tab{{padding:6px 16px;border-radius:6px;cursor:pointer;font-size:12px;font-weight:500;color:var(--text-muted);transition:all .18s;border:none;background:transparent;}}
  .view-tab.active{{background:var(--accent);color:#fff;}}
  .nav-btn{{width:32px;height:32px;border-radius:6px;border:1px solid var(--border);background:var(--surface2);color:var(--text);cursor:pointer;}}
  .period-label{{font-size:15px;font-weight:700;min-width:180px;text-align:center;}}
  
  #calendar-root{{height:calc(100vh - 60px);display:flex;flex-direction:column;}}

  /* シフトブロック基本デザイン */
  .shift-block{{position:absolute;left:2px;right:2px;padding:3px 5px;font-size:10px;font-weight:600;z-index:1;cursor:pointer;border-left:3px solid;}}
  .sb-name{{white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}}
  .sb-time{{font-size:9px;opacity:0.8;font-family:var(--mono);}}

  /* ビュー共通 */
  .time-col{{width:64px;flex-shrink:0;border-right:1px solid var(--border);background:var(--surface);position:sticky;left:0;z-index:10;}}
  .time-slot{{height:48px;padding:4px 8px;border-bottom:1px solid var(--border);font-size:10px;color:var(--text-muted);text-align:right;}}
  .day-boundary{{border-top:2px solid var(--accent2);color:var(--accent2);font-weight:700;}}

  /* 月ビュー */
  .month-view{{display:flex;flex-direction:column;height:100%;}}
  .month-grid{{display:grid;grid-template-columns:repeat(7,1fr);flex:1;}}
  .month-cell{{border-right:1px solid var(--border);border-bottom:1px solid var(--border);padding:4px;min-height:80px;}}
  .month-shift-chip{{font-size:9px;padding:1px 4px;margin-bottom:1px;border-radius:2px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}}

  /* 週・日ビュー */
  .scroll-area{{flex:1;display:flex;overflow:auto;position:relative;}}
  .grid-container{{display:flex;flex:1;}}
  .header-row{{display:flex;background:var(--surface);border-bottom:2px solid var(--border);}}
  .col-header{{flex:1;min-width:100px;padding:10px;text-align:center;border-right:1px solid var(--border);font-weight:600;}}
  .data-col{{flex:1;min-width:100px;border-right:1px solid var(--border);position:relative;cursor:crosshair;}}
  .hour-slot{{height:48px;border-bottom:1px solid var(--border);}}

  /* モーダル */
  .modal-overlay{{position:fixed;inset:0;background:rgba(0,0,0,0.7);display:flex;align-items:center;justify-content:center;z-index:1000;}}
  .modal{{background:var(--surface);padding:20px;border-radius:12px;width:340px;border:1px solid var(--border);}}
  .form-group{{margin-bottom:12px;}}
  .form-input{{width:100%;padding:8px;background:var(--surface2);border:1px solid var(--border);color:#fff;border-radius:4px;}}
  .btn{{padding:8px 16px;border-radius:4px;border:none;cursor:pointer;font-weight:600;}}
  .btn-primary{{background:var(--accent);color:#fff;width:100%;}}

  /* Toast & Loading */
  .toast{{position:fixed;bottom:20px;right:20px;padding:12px 20px;border-radius:8px;background:var(--success);z-index:2000;animation:slideIn 0.3s;}}
  @keyframes slideIn{{from{{transform:translateX(100%);}}to{{transform:translateX(0);}}}}
</style>
</head>
<body>
<div class="topbar">
  <div class="view-tabs">
    <button class="view-tab" id="tab-day" onclick="setView('day')">日</button>
    <button class="view-tab" id="tab-week" onclick="setView('week')">週</button>
    <button class="view-tab" id="tab-month" onclick="setView('month')">月</button>
  </div>
  <div class="nav-group">
    <button class="nav-btn" onclick="navigate(-1)">◀</button>
    <span class="period-label" id="period-label"></span>
    <button class="nav-btn" onclick="navigate(1)">▶</button>
  </div>
  <div style="margin-left:auto; display:flex; gap:8px;">
    <select id="filter-staff" class="form-input" style="width:120px;" onchange="renderView()"><option value="">全スタッフ</option></select>
  </div>
</div>

<div id="calendar-root"></div>

<div id="modal-reg" class="modal-overlay" style="display:none;" onclick="if(event.target===this)this.style.display='none'">
  <div class="modal">
    <h3 style="margin-bottom:15px;">シフト登録</h3>
    <div class="form-group"><label>スタッフ</label><select id="m-staff" class="form-input"></select></div>
    <div class="form-group"><label>部門</label><select id="m-dept" class="form-input"></select></div>
    <div class="form-group"><label>日付</label><input type="date" id="m-date" class="form-input"></div>
    <div class="form-group"><label>開始 - 終了</label>
      <div style="display:flex; gap:5px;"><input type="time" id="m-start" class="form-input"><input type="time" id="m-end" class="form-input"></div>
    </div>
    <button class="btn btn-primary" onclick="saveShift()">保存する</button>
  </div>
</div>

<script>
// --- DATA ---
const GAS_URL = "{gas_url}";
const STAFF_LIST = {staff_json};
const DEPT_LIST = {dept_json};
let SHIFTS = {shifts_json_str};
const COLORS = {json.dumps(color_palette)};

let currentView = 'day';
let currentDate = new Date(); currentDate.setHours(0,0,0,0);
const HOUR_PX = 48;

// --- UTILS ---
function fmt(d) {{ return d.toISOString().split('T')[0]; }}
function parseD(s) {{ return new Date(s); }}
function mk(tag, cls) {{ const e=document.createElement(tag); if(cls)e.className=cls; return e; }}

function getDeptColor(dept) {{
    const i = DEPT_LIST.indexOf(dept);
    return COLORS[i >= 0 ? i % COLORS.length : 0];
}}

// シフトを特定の表示時間枠(mins)に合わせてカットして返す
function getShiftSegment(s, viewBaseDate, viewStartMins, viewEndMins) {{
    const st = parseD(s.start);
    const et = parseD(s.end);
    
    // viewBaseDate(表示中の基準日) 0:00 からの経過分を算出
    const shiftStartMins = (st - viewBaseDate) / 60000;
    const shiftEndMins = (et - viewBaseDate) / 60000;

    if (shiftEndMins <= viewStartMins || shiftStartMins >= viewEndMins) return null;

    return {{
        start: Math.max(shiftStartMins, viewStartMins),
        end: Math.min(shiftEndMins, viewEndMins),
        isContTop: shiftStartMins < viewStartMins,
        isContBottom: shiftEndMins > viewEndMins,
        original: s
    }};
}}

// --- COMPONENTS ---
function createShiftBlock(seg, showStaff) {{
    const col = getDeptColor(seg.original.dept);
    const b = mk('div', 'shift-block');
    const duration = seg.end - seg.start;
    
    b.style.top = (seg.start * HOUR_PX / 60) + 'px';
    b.style.height = Math.max(duration * HOUR_PX / 60, 18) + 'px';
    b.style.backgroundColor = col + '44'; // 透明度25%
    b.style.borderColor = col;
    b.style.color = col;
    
    if(seg.isContTop) {{ b.style.borderTopStyle = 'dashed'; b.style.borderTopLeftRadius = '0'; b.style.borderTopRightRadius = '0'; }}
    if(seg.isContBottom) {{ b.style.borderBottomStyle = 'dashed'; b.style.borderBottomLeftRadius = '0'; b.style.borderBottomRightRadius = '0'; }}

    const label = (seg.isContTop ? '▲ ' : '') + (showStaff ? seg.original.staff : seg.original.dept);
    b.innerHTML = `<div class="sb-name">${{label}}</div>`;
    b.onclick = () => alert(seg.original.staff + "\\n" + seg.original.dept + "\\n" + seg.original.start + " ～ " + seg.original.end);
    return b;
}}

// --- RENDERERS ---
function renderView() {{
    const root = document.getElementById('calendar-root');
    root.innerHTML = '';
    const staffFilter = document.getElementById('filter-staff').value;
    const filtered = SHIFTS.filter(s => !staffFilter || s.staff === staffFilter);
    
    document.querySelectorAll('.view-tab').forEach(t => t.classList.remove('active'));
    document.getElementById('tab-' + currentView).classList.add('active');

    if (currentView === 'day') renderDayView(root, filtered);
    else if (currentView === 'week') renderWeekView(root, filtered);
    else renderMonthView(root, filtered);
}}

function renderDayView(root, shifts) {{
    const ds = fmt(currentDate);
    document.getElementById('period-label').textContent = ds;
    
    const scroll = mk('div', 'scroll-area');
    const timeCol = mk('div', 'time-col');
    for(let h=0; h<31; h++) {{
        const ts = mk('div', 'time-slot' + (h===24 ? ' day-boundary' : ''));
        ts.textContent = h<24 ? `${{h}}:00` : `翌${{h-24}}:00`;
        timeCol.appendChild(ts);
    }
    scroll.appendChild(timeCol);

    const grid = mk('div', 'grid-container');
    const staffShow = STAFF_LIST.filter(s => !document.getElementById('filter-staff').value || s === document.getElementById('filter-staff').value);
    
    staffShow.forEach(staff => {{
        const col = mk('div', 'data-col');
        for(let h=0; h<30; h++) col.appendChild(mk('div', 'hour-slot'));
        
        // 0時〜30時(翌6時)の枠でセグメント化して描画
        shifts.filter(s => s.staff === staff).forEach(s => {{
            const seg = getShiftSegment(s, currentDate, 0, 30 * 60);
            if(seg) col.appendChild(createShiftBlock(seg, false));
        }});
        grid.appendChild(col);
    }});
    
    scroll.appendChild(grid);
    root.appendChild(scroll);
}}

function renderWeekView(root, shifts) {{
    const weekStart = new Date(currentDate);
    weekStart.setDate(currentDate.getDate() - currentDate.getDay());
    document.getElementById('period-label').textContent = fmt(weekStart) + " 週";

    const scroll = mk('div', 'scroll-area');
    const timeCol = mk('div', 'time-col');
    for(let h=0; h<25; h++) {{
        const ts = mk('div', 'time-slot');
        ts.textContent = `${{h}}:00`;
        timeCol.appendChild(ts);
    }}
    scroll.appendChild(timeCol);

    const grid = mk('div', 'grid-container');
    for(let i=0; i<7; i++) {{
        const d = new Date(weekStart); d.setDate(weekStart.getDate() + i);
        const col = mk('div', 'data-col');
        col.innerHTML = `<div style="position:sticky; top:0; background:var(--surface); text-align:center; padding:5px; border-bottom:1px solid var(--border); z-index:5;">${{d.getDate()}}(${{['日','月','火','水','木','金','土'][i]}})</div>`;
        for(let h=0; h<24; h++) col.appendChild(mk('div', 'hour-slot'));
        
        shifts.forEach(s => {{
            const seg = getShiftSegment(s, d, 0, 24 * 60);
            if(seg) col.appendChild(createShiftBlock(seg, true));
        }});
        grid.appendChild(col);
    }}
    scroll.appendChild(grid);
    root.appendChild(scroll);
}}

function renderMonthView(root, shifts) {{
    const y = currentDate.getFullYear(), m = currentDate.getMonth();
    document.getElementById('period-label').textContent = `${{y}}年 ${{m+1}}月`;
    const mv = mk('div', 'month-view');
    const grid = mk('div', 'month-grid');
    
    const first = new Date(y, m, 1);
    const start = new Date(first); start.setDate(first.getDate() - first.getDay());
    
    for(let i=0; i<35; i++) {{
        const d = new Date(start); d.setDate(start.getDate() + i);
        const cell = mk('div', 'month-cell');
        cell.innerHTML = `<div style="font-size:10px; opacity:0.5;">${{d.getDate()}}</div>`;
        
        shifts.forEach(s => {{
            const st = parseD(s.start);
            if(fmt(st) === fmt(d)) {{
                const chip = mk('div', 'month-shift-chip');
                const col = getDeptColor(s.dept);
                chip.style.backgroundColor = col + '33';
                chip.style.color = col;
                chip.textContent = s.staff;
                cell.appendChild(chip);
            }}
        }});
        grid.appendChild(cell);
    }}
    mv.appendChild(grid);
    root.appendChild(mv);
}}

// --- ACTIONS ---
function setView(v) {{ currentView = v; renderView(); }}
function navigate(dir) {{
    if(currentView==='day') currentDate.setDate(currentDate.getDate()+dir);
    else if(currentView==='week') currentDate.setDate(currentDate.getDate()+dir*7);
    else currentDate.setMonth(currentDate.getMonth()+dir);
    renderView();
}}

async function saveShift() {{
    const data = {{
        action: 'add_shift',
        name: document.getElementById('m-staff').value,
        dept: document.getElementById('m-dept').value,
        start: document.getElementById('m-date').value + ' ' + document.getElementById('m-start').value,
        end: document.getElementById('m-date').value + ' ' + document.getElementById('m-end').value
    }};
    showToast("保存中...");
    try {{
        await fetch(GAS_URL + "?" + new URLSearchParams(data));
        SHIFTS.push({{ staff: data.name, dept: data.dept, start: data.start.replace(' ','T'), end: data.end.replace(' ','T') }});
        document.getElementById('modal-reg').style.display='none';
        renderView();
        showToast("保存しました");
    }} catch(e) {{ showToast("エラーが発生しました", "danger"); }}
}}

function showToast(msg) {{
    const t = mk('div', 'toast'); t.textContent = msg;
    document.body.appendChild(t);
    setTimeout(() => t.remove(), 3000);
}}

// --- INIT ---
window.onload = () => {{
    const sSel = document.getElementById('filter-staff');
    const mStaff = document.getElementById('m-staff');
    STAFF_LIST.forEach(s => {{
        sSel.appendChild(new Option(s, s));
        mStaff.appendChild(new Option(s, s));
    }});
    const mDept = document.getElementById('m-dept');
    DEPT_LIST.forEach(d => mDept.appendChild(new Option(d, d)));
    renderView();
}};
</script>
</body>
</html>
"""
    # Streamlitにレンダリング
    components.html(html_code, height=800, scrolling=False)

# 利用例
# render_calendar_component(df, ["田中", "佐藤"], ["キッチン", "ホール"], "https://script.google.com/...")
