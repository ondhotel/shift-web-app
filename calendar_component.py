import streamlit.components.v1 as components
import json
import pandas as pd

def render_calendar_component(df: pd.DataFrame, staff_list: list, dept_list: list, gas_url: str):
    shifts_json = []
    if not df.empty:
        for idx, row in df.iterrows():
            try:
                shifts_json.append({
                    "staff": str(row.get("従業員", "")),
                    "dept":  str(row.get("部門", "")),
                    "start": row["開始"].isoformat() if pd.notna(row["開始"]) else "",
                    "end":   row["終了"].isoformat() if pd.notna(row["終了"]) else "",
                })
            except: pass

    staff_json = json.dumps(staff_list, ensure_ascii=False)
    dept_json = json.dumps(dept_list, ensure_ascii=False)
    shifts_json_str = json.dumps(shifts_json, ensure_ascii=False)
    
    color_palette = ["#4f86c6","#e07b5a","#5aad8f","#b07fc7","#e0b84a","#5abfcc","#e07bb0","#7ec45a"]
    H = 800

    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700&family=JetBrains+Mono:wght@400;600&display=swap');
:root{{
  --bg:#0f1117;--sf:#1a1d27;--sf2:#22263a;--bd:#2d3148;
  --tx:#e8eaf2;--tx2:#6b7094;--ac:#5b8af0;--ac2:#8b5cf6;
  --ok:#34d399;--ng:#f87171;--wn:#f59e0b;--cp:#f0a05b;
  --tod:rgba(91,138,240,.12);--hv:rgba(91,138,240,.08);
  --sel:rgba(240,160,91,.28);
  --fn:'Noto Sans JP',sans-serif;--mn:'JetBrains Mono',monospace;
}}
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{height:{H}px;background:var(--bg);color:var(--tx);font-family:var(--fn);font-size:13px;overflow:hidden;}}
#app{{display:flex;flex-direction:column;height:100%;}}
#topbar{{flex-shrink:0;display:flex;align-items:center;gap:8px;padding:8px 12px;background:var(--sf);border-bottom:1px solid var(--bd);flex-wrap:wrap;}}
#pbanner{{display:none;width:100%;gap:8px;padding:4px 0;}}
#pbanner.show{{display:flex;}}
.vtab{{display:flex;background:var(--sf2);border-radius:7px;padding:3px;gap:2px;}}
.vt{{padding:4px 10px;border-radius:5px;cursor:pointer;font-size:12px;color:var(--tx2);border:none;background:transparent;}}
.vt.on{{background:var(--ac);color:#fff;}}
#cal{{flex:1;overflow:hidden;display:flex;flex-direction:column;}}

/* スタッフ週表示用 */
.sw-grid {{ display: grid; grid-template-columns: 120px repeat(7, 1fr); height: 100%; overflow-y: auto; }}
.sw-cell {{ border-right: 1px solid var(--bd); border-bottom: 1px solid var(--bd); padding: 4px; min-height: 60px; }}
.sw-head {{ background: var(--sf); font-weight: bold; position: sticky; top: 0; z-index: 10; text-align: center; }}
.sw-staff-name {{ background: var(--sf); position: sticky; left: 0; z-index: 9; font-weight: 600; padding: 10px 5px; }}

/* 共通パーツ */
.mc{{border-right:1px solid var(--bd);border-bottom:1px solid var(--bd);padding:4px;min-height:80px;position:relative;}}
.dn{{font-size:11px;font-weight:600;margin-bottom:4px;}}
.mmerge{{border-radius:3px;margin-bottom:2px;cursor:pointer;font-size:10px;overflow:hidden;}}
.mseg{{padding:1px 4px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}}
.sb{{position:absolute;border-radius:4px;padding:2px 4px;font-size:10px;font-weight:600;z-index:1;cursor:pointer;border:1px solid rgba(255,255,255,.1);}}
.dragsel{{position:absolute;left:2px;right:2px;background:rgba(91,138,240,0.3);border:1px dashed var(--ac);pointer-events:none;z-index:10;}}

/* モーダル */
.ov{{position:fixed;inset:0;background:rgba(0,0,0,.7);z-index:3000;display:flex;align-items:center;justify-content:center;}}
.modal{{background:var(--sf);border-radius:12px;padding:20px;width:380px;border:1px solid var(--bd);}}
.ma{{display:flex;gap:7px;margin-top:15px;}}
.btn{{flex:1;padding:8px;border-radius:6px;border:none;cursor:pointer;font-weight:600;}}
.bp{{background:var(--ac);color:#fff;}}
.bd{{background:var(--ng);color:#fff;}}
.be{{background:var(--wn);color:#000;}}
.fi,.fs2{{width:100%;padding:7px;background:var(--sf2);color:#fff;border:1px solid var(--bd);border-radius:6px;margin-top:4px;}}
</style>
</head>
<body>
<div id="app">
  <div id="topbar">
    <div class="vtab">
      <button class="vt on" data-v="day">日</button>
      <button class="vt"    data-v="week">週(時間)</button>
      <button class="vt"    data-v="staff-week">週(スタッフ)</button>
      <button class="vt"    data-v="month">月</button>
    </div>
    <div style="display:flex;align-items:center;gap:10px;">
      <button onclick="nav(-1)" class="vt">◀</button>
      <div id="plbl" style="font-weight:700;min-width:120px;text-align:center;"></div>
      <button onclick="nav(1)" class="vt">▶</button>
      <button onclick="goToday()" class="vt">今日</button>
    </div>
    <div id="pbanner">
      <span id="pcnt" style="color:var(--cp);font-size:11px;"></span>
      <button class="vt" id="pexec" style="background:var(--cp);color:#000;">貼り付け実行</button>
      <button class="vt" id="pcancel">キャンセル</button>
    </div>
    <div style="margin-left:auto;display:flex;gap:5px;">
      <select id="fstaff" class="fs2" style="margin:0;"><option value="">全スタッフ</option></select>
      <select id="fdept" class="fs2" style="margin:0;"><option value="">全部門</option></select>
    </div>
  </div>
  <div id="cal"></div>
</div>

<div class="ov" id="regOv" style="display:none;">
  <div class="modal">
    <h3 id="regTitle">シフト登録</h3>
    <input type="hidden" id="editIdx" value="-1">
    <div style="margin-top:10px;">
      <label style="font-size:10px;color:var(--tx2);">スタッフ / 部門</label>
      <div style="display:flex;gap:5px;">
        <select id="mStaff" class="fs2"></select>
        <select id="mDept" class="fs2"></select>
      </div>
    </div>
    <div style="margin-top:10px;">
      <label style="font-size:10px;color:var(--tx2);">日付</label>
      <input type="date" id="mDate" class="fi">
    </div>
    <div style="margin-top:10px;">
      <label style="font-size:10px;color:var(--tx2);">時間 (夜勤は25:00等で入力可)</label>
      <div style="display:flex;align-items:center;gap:5px;">
        <input type="text" id="mS" class="fi" placeholder="09:00">
        <span>→</span>
        <input type="text" id="mE" class="fi" placeholder="18:00">
      </div>
    </div>
    <div class="ma">
      <button class="btn" onclick="closeReg()" style="background:var(--sf2);color:var(--tx);">閉じる</button>
      <button class="btn bp" onclick="saveShift()">保存</button>
    </div>
  </div>
</div>

<div class="ov" id="detOv" style="display:none;">
  <div class="modal">
    <h3>シフト詳細</h3>
    <div id="detBody" style="margin:15px 0;line-height:1.6;"></div>
    <div class="ma">
      <button class="btn" onclick="closeDet()" style="background:var(--sf2);color:var(--tx);">閉じる</button>
      <button class="btn" onclick="startCopy()" style="background:var(--cp);color:#000;">コピー</button>
      <button class="btn be" onclick="openEdit()">編集</button>
      <button class="btn bd" onclick="delShift()">削除</button>
    </div>
  </div>
</div>

<script>
const GAS = "{gas_url}";
const STAFF = {staff_json};
const DEPTS = {dept_json};
let SHIFTS = {shifts_json_str};
const CLRS = {color_palette};

let view = 'day';
let cur = new Date(); cur.setHours(0,0,0,0);
let clip = null;
let pasteDates = new Set();
let curS = null;

const $$ = id => document.getElementById(id);
const fmt = d => d.toISOString().split('T')[0];
const p2 = n => String(n).padStart(2,'0');

window.onload = () => {{
  STAFF.forEach(s => {{ $$('fstaff').add(new Option(s,s)); $$('mStaff').add(new Option(s,s)); }});
  DEPTS.forEach(d => {{ $$('fdept').add(new Option(d,d)); $$('mDept').add(new Option(d,d)); }});
  
  document.querySelectorAll('.vt[data-v]').forEach(btn => {{
    btn.onclick = () => {{
      view = btn.dataset.v;
      document.querySelectorAll('.vt[data-v]').forEach(b => b.classList.toggle('on', b.dataset.v === view));
      render();
    }};
  }});
  $$('pcancel').onclick = () => {{ clip=null; pasteDates.clear(); render(); }};
  $$('pexec').onclick = execPaste;
  $$('fstaff').onchange = render;
  $$('fdept').onchange = render;
  render();
}};

function nav(d) {{
  if(view==='day') cur.setDate(cur.getDate()+d);
  else if(view.includes('week')) cur.setDate(cur.getDate()+d*7);
  else cur.setMonth(cur.getMonth()+d);
  render();
}}
function goToday() {{ cur = new Date(); cur.setHours(0,0,0,0); render(); }}

function getFiltered() {{
  const s = $$('fstaff').value, d = $$('fdept').value;
  return SHIFTS.filter(x => (!s || x.staff===s) && (!d || x.dept===d));
}}

function render() {{
  const cal = $$('cal'); cal.innerHTML = '';
  $$('pbanner').classList.toggle('show', !!clip);
  if(clip) $$('pcnt').textContent = `${{clip.staff}} (${{clip.start.split('T')[1].slice(0,5)}}-) をコピー中: ${{pasteDates.size}}日選択`;

  if(view === 'day') renderDay();
  else if(view === 'week') renderWeek();
  else if(view === 'staff-week') renderStaffWeek();
  else renderMonth();
}}

// --- 月表示 ---
function renderMonth() {{
  const y=cur.getFullYear(), m=cur.getMonth();
  $$('plbl').textContent = `${{y}}年${{m+1}}月`;
  const first = new Date(y,m,1), last = new Date(y,m+1,0);
  const start = new Date(first); start.setDate(first.getDate() - first.getDay());
  
  const grid = document.createElement('div');
  grid.style.display='grid'; grid.style.gridTemplateColumns='repeat(7,1fr)'; grid.style.height='100%';
  
  for(let i=0; i<42; i++) {{
    const d = new Date(start); d.setDate(start.getDate()+i);
    const ds = fmt(d);
    const cell = document.createElement('div');
    cell.className = 'mc' + (d.getMonth()!==m ? ' other':'');
    if(pasteDates.has(ds)) cell.style.background = 'var(--sel)';
    cell.innerHTML = `<div class="dn">${{d.getDate()}}</div>`;
    
    cell.onclick = () => {{
      if(clip) {{
        if(pasteDates.has(ds)) pasteDates.delete(ds); else pasteDates.add(ds);
        render();
      }} else {{
        openReg(ds);
      }}
    }};

    getFiltered().filter(s => s.start.startsWith(ds)).forEach(s => {{
      const div = document.createElement('div');
      div.className = 'mmerge';
      div.style.borderLeft = `3px solid ${{getClr(s.dept)}}`;
      div.style.background = 'rgba(255,255,255,0.05)';
      div.innerHTML = `<div class="mseg"><b>${{s.staff}}</b> ${{s.start.split('T')[1].slice(0,5)}}</div>`;
      div.onclick = (e) => {{ e.stopPropagation(); showDet(s); }};
      cell.appendChild(div);
    }});
    grid.appendChild(cell);
  }}
  $$('cal').appendChild(grid);
}}

// --- スタッフ別週表示 (NEW) ---
function renderStaffWeek() {{
  const ws = new Date(cur); ws.setDate(cur.getDate() - cur.getDay());
  $$('plbl').textContent = `${{ws.getMonth()+1}}/${{ws.getDate()}}の週`;
  const grid = document.createElement('div'); grid.className = 'sw-grid';
  
  // ヘッダ
  grid.appendChild(document.createElement('div'));
  for(let i=0; i<7; i++) {{
    const d = new Date(ws); d.setDate(ws.getDate()+i);
    const h = document.createElement('div'); h.className = 'sw-cell sw-head';
    h.textContent = `${{d.getDate()}}(${{['日','月','火','水','木','金','土'][i]}})`;
    grid.appendChild(h);
  }}

  const targetStaff = $$('fstaff').value ? [$$('fstaff').value] : STAFF;
  targetStaff.forEach(name => {{
    const nameCell = document.createElement('div'); nameCell.className = 'sw-cell sw-staff-name';
    nameCell.textContent = name; grid.appendChild(nameCell);
    for(let i=0; i<7; i++) {{
      const d = new Date(ws); d.setDate(ws.getDate()+i);
      const ds = fmt(d);
      const cell = document.createElement('div'); cell.className = 'sw-cell';
      if(pasteDates.has(ds)) cell.style.background = 'var(--sel)';
      
      cell.onclick = () => {{
        if(clip) {{ if(pasteDates.has(ds)) pasteDates.delete(ds); else pasteDates.add(ds); render(); }}
        else openReg(ds, "09:00", "18:00", name);
      }};

      getFiltered().filter(x => x.staff===name && x.start.startsWith(ds)).forEach(s => {{
        const div = document.createElement('div'); div.className = 'mmerge';
        div.style.borderLeft = `3px solid ${{getClr(s.dept)}}`;
        div.style.background = 'rgba(255,255,255,0.1)';
        div.textContent = `${{s.start.split('T')[1].slice(0,5)}}-${{s.end.split('T')[1].slice(0,5)}}`;
        div.onclick = (e) => {{ e.stopPropagation(); showDet(s); }};
        cell.appendChild(div);
      }});
      grid.appendChild(cell);
    }}
  }});
  $$('cal').appendChild(grid);
}}

// --- 日表示 ---
function renderDay() {{
  const ds = fmt(cur);
  $$('plbl').textContent = ds;
  const targetStaff = $$('fstaff').value ? [$$('fstaff').value] : STAFF;
  const container = document.createElement('div');
  container.style.display='flex'; container.style.height='100%'; container.style.overflowX='auto';

  // 時間軸
  const timeCol = document.createElement('div'); timeCol.style.width='50px'; timeCol.style.flexShrink='0';
  for(let i=0; i<25; i++) {{
    const t = document.createElement('div'); t.style.height='40px'; t.style.fontSize='10px';
    t.textContent = i+':00'; timeCol.appendChild(t);
  }}
  container.appendChild(timeCol);

  targetStaff.forEach(name => {{
    const col = document.createElement('div');
    col.style.flex='1'; col.style.minWidth='100px'; col.style.borderLeft='1px solid var(--bd)';
    col.style.position='relative'; col.style.height='1000px';
    col.innerHTML = `<div style="text-align:center;padding:5px;background:var(--sf2);position:sticky;top:0;z-index:5;">${{name}}</div>`;
    
    // ドラッグ登録イベント
    setupDrag(col, ds, name);

    getFiltered().filter(x => x.staff===name && x.start.startsWith(ds)).forEach(s => {{
      const b = createShiftBlock(s);
      col.appendChild(b);
    }});
    container.appendChild(col);
  }});
  $$('cal').appendChild(container);
}}

// --- ドラッグ登録ロジック ---
function setupDrag(col, ds, staffName) {{
  let startY, dragEl;
  col.onmousedown = (e) => {{
    if(clip || e.target.classList.contains('sb')) return;
    startY = e.offsetY;
    dragEl = document.createElement('div'); dragEl.className = 'dragsel';
    dragEl.style.top = startY + 'px';
    col.appendChild(dragEl);
    
    col.onmousemove = (me) => {{
      const h = me.offsetY - startY;
      dragEl.style.height = Math.max(0, h) + 'px';
    }};
    
    window.onmouseup = (ue) => {{
      const endY = ue.pageY - col.getBoundingClientRect().top - window.scrollY;
      col.onmousemove = null; window.onmouseup = null;
      if(!dragEl) return;
      const sMins = Math.floor(startY / 40) * 60 + (Math.floor((startY%40)/10)*15);
      const eMins = Math.floor(endY / 40) * 60 + (Math.floor((endY%40)/10)*15);
      dragEl.remove();
      if(eMins - sMins > 10) {{
        openReg(ds, minsToTs(sMins), minsToTs(eMins), staffName);
      }}
    }};
  }};
}}

function minsToTs(m) {{ return `${{p2(Math.floor(m/60))}}:${{p2(m%60)}}`; }}

function createShiftBlock(s) {{
  const st = new Date(s.start), et = new Date(s.end);
  const sMins = st.getHours()*60 + st.getMinutes();
  let eMins = et.getHours()*60 + et.getMinutes();
  if(et.getDate() !== st.getDate()) eMins += 1440; // 日跨ぎ対応

  const div = document.createElement('div'); div.className = 'sb';
  div.style.top = (sMins / 60 * 40 + 30) + 'px';
  div.style.height = ((eMins - sMins) / 60 * 40) + 'px';
  div.style.background = 'rgba(91,138,240,0.2)';
  div.style.borderLeft = `4px solid ${{getClr(s.dept)}}`;
  div.innerHTML = `<div>${{s.dept}}</div><div>${{s.start.split('T')[1].slice(0,5)}}-${{s.end.split('T')[1].slice(0,5)}}</div>`;
  div.onclick = (e) => {{ e.stopPropagation(); showDet(s); }};
  return div;
}}

function getClr(d) {{
  const idx = DEPTS.indexOf(d);
  return idx >= 0 ? CLRS[idx % CLRS.length] : '#ccc';
}}

// --- モーダル制御 ---
function openReg(ds, s="09:00", e="18:00", staff="", dept="", idx="-1") {{
  $$('mDate').value = ds; $$('mS').value = s; $$('mE').value = e;
  if(staff) $$('mStaff').value = staff;
  if(dept) $$('mDept').value = dept;
  $$('editIdx').value = idx;
  $$('regTitle').textContent = idx === "-1" ? "シフト登録" : "シフト編集";
  $$('regOv').style.display = 'flex';
}}
function closeReg() {{ $$('regOv').style.display = 'none'; }}

function showDet(s) {{
  curS = s;
  $$('detBody').innerHTML = `
    <b>スタッフ:</b> ${{s.staff}}<br>
    <b>部門:</b> ${{s.dept}}<br>
    <b>日時:</b> ${{s.start.replace('T',' ')}}${{s.end.includes('T') ? ' 〜 ' + s.end.split('T')[1] : ''}}
  `;
  $$('detOv').style.display = 'flex';
}}
function closeDet() {{ $$('detOv').style.display = 'none'; }}

function openEdit() {{
  const s = curS;
  const ds = s.start.split('T')[0];
  const st = s.start.split('T')[1].slice(0,5);
  const et = s.end.split('T')[1].slice(0,5);
  const idx = SHIFTS.indexOf(s);
  closeDet();
  openReg(ds, st, et, s.staff, s.dept, idx);
}}

async function saveShift() {{
  const staff = $$('mStaff').value, dept = $$('mDept').value, ds = $$('mDate').value, s = $$('mS').value, e = $$('mE').value;
  const idx = parseInt($$('editIdx').value);
  
  // 編集の場合は一旦削除
  if(idx !== -1) {{
    const old = SHIFTS[idx];
    await fetch(GAS+'?'+new URLSearchParams({{action:'del_shift', name:old.staff, dept:old.dept, start:old.start.replace('T',' '), end:old.end.replace('T',' ')}}));
    SHIFTS.splice(idx, 1);
  }}

  const res = await fetch(GAS+'?'+new URLSearchParams({{action:'add_shift', name:staff, dept:dept, start:`${{ds}} ${{s}}`, end:`${{ds}} ${{e}}` }}));
  if(res.ok) {{
    SHIFTS.push({{ staff, dept, start: `${{ds}}T${{s}}:00`, end: `${{ds}}T${{e}}:00` }});
    closeReg(); render();
  }}
}}

async function delShift() {{
  if(!confirm('削除しますか？')) return;
  const s = curS;
  await fetch(GAS+'?'+new URLSearchParams({{action:'del_shift', name:s.staff, dept:s.dept, start:s.start.replace('T',' '), end:s.end.replace('T',' ')}}));
  SHIFTS = SHIFTS.filter(x => x !== s);
  closeDet(); render();
}}

function startCopy() {{
  clip = curS;
  pasteDates.clear();
  closeDet();
  render();
}}

async function execPaste() {{
  if(!clip || pasteDates.size === 0) return;
  const st = clip.start.split('T')[1].slice(0,5);
  const et = clip.end.split('T')[1].slice(0,5);
  for(const d of pasteDates) {{
    await fetch(GAS+'?'+new URLSearchParams({{action:'add_shift', name:clip.staff, dept:clip.dept, start:`${{d}} ${{st}}`, end:`${{d}} ${{et}}` }}));
    SHIFTS.push({{ staff:clip.staff, dept:clip.dept, start:`${{d}}T${{st}}:00`, end:`${{d}}T${{et}}:00` }});
  }}
  clip = null; pasteDates.clear(); render();
}}
</script>
</body>
</html>"""

    components.html(html, height=H, scrolling=False)
