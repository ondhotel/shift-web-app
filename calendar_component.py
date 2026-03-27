import streamlit.components.v1 as components
import json
import pandas as pd

def render_calendar_component(df: pd.DataFrame, staff_list: list, dept_list: list, gas_url: str):
    shifts_json = []
    if not df.empty:
        for idx, row in df.iterrows():
            try:
                shifts_json.append({
                    "rowIndex": int(idx),
                    "staff":    str(row.get("従業員", "")),
                    "dept":     str(row.get("部門", "")),
                    "start":    row["開始"].isoformat() if pd.notna(row["開始"]) else "",
                    "end":      row["終了"].isoformat() if pd.notna(row["終了"]) else "",
                })
            except Exception: pass

    staff_json       = json.dumps(staff_list,  ensure_ascii=False)
    dept_json        = json.dumps(dept_list,   ensure_ascii=False)
    shifts_json_str  = json.dumps(shifts_json, ensure_ascii=False)

    color_palette = ["#4f86c6","#e07b5a","#5aad8f","#b07fc7","#e0b84a","#5abfcc","#e07bb0","#7ec45a"]
    H = 800

    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@300;400;500;700&family=JetBrains+Mono:wght@400;600&display=swap');
:root{{
  --bg:#0f1117;--sf:#1a1d27;--sf2:#22263a;--bd:#2d3148;
  --tx:#e8eaf2;--tx2:#6b7094;--ac:#5b8af0;--ac2:#8b5cf6;
  --ok:#34d399;--ng:#f87171;--wn:#f59e0b;--cp:#f0a05b;
  --tod:rgba(91,138,240,.12);--hv:rgba(91,138,240,.08);
  --drag:rgba(91,138,240,.25);--nday:rgba(139,92,246,.06);
  --sel:rgba(240,160,91,.28);
  --fn:'Noto Sans JP',sans-serif;--mn:'JetBrains Mono',monospace;
}}
*{{margin:0;padding:0;box-sizing:border-box;}}
html,body{{width:100%;height:{H}px;overflow:hidden;background:var(--bg);color:var(--tx);font-family:var(--fn);font-size:13px;user-select:none;}}

/* レイアウト */
#app{{display:flex;flex-direction:column;height:100%;}}
#topbar{{flex-shrink:0;display:flex;align-items:center;gap:8px;padding:8px 12px;background:var(--sf);border-bottom:1px solid var(--bd);flex-wrap:wrap;}}
#pbanner{{display:none;width:100%;align-items:center;gap:8px;padding:4px 0 2px;flex-wrap:wrap;}}
#pbanner.show{{display:flex;}}
#cal{{flex:1;overflow:hidden;display:flex;flex-direction:column;min-height:0;}}

/* UIパーツ */
.vtab{{display:flex;background:var(--sf2);border-radius:7px;padding:3px;gap:2px;}}
.vt{{padding:4px 13px;border-radius:5px;cursor:pointer;font-size:12px;font-weight:500;color:var(--tx2);border:none;background:transparent;}}
.vt.on{{background:var(--ac);color:#fff;}}
.fsel{{padding:4px 7px;border-radius:5px;border:1px solid var(--bd);background:var(--sf2);color:var(--tx);font-size:12px;}}

/* 月・スタッフ週ビュー共通 */
.mv{{flex:1;display:flex;flex-direction:column;overflow:hidden;}}
.mgrid{{flex:1;display:grid;overflow-y:auto;}}
.mc{{border-right:1px solid var(--bd);border-bottom:1px solid var(--bd);padding:4px;cursor:pointer;min-height:75px;position:relative;}}
.mc.psel{{background:var(--sel)!important;outline:2px solid var(--cp);outline-offset:-2px;}}
.mmerge{{border-radius:3px;margin-bottom:2px;overflow:hidden;cursor:pointer;font-size:10px;font-weight:500;}}
.mseg{{padding:1px 4px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}}

/* スタッフ週表示専用 */
.sw-grid {{ display: grid; grid-template-columns: 100px repeat(7, 1fr); }}
.sw-head {{ background: var(--sf); font-weight: bold; position: sticky; top: 0; z-index: 10; text-align: center; padding: 5px; border-bottom: 2px solid var(--bd); }}
.sw-staff-name {{ background: var(--sf); position: sticky; left: 0; z-index: 9; font-weight: 600; padding: 10px 5px; border-right: 2px solid var(--bd); }}

/* 日ビュー・シフトブロック */
.sb{{position:absolute;border-radius:4px;padding:2px 4px;font-size:10px;font-weight:600;overflow:hidden;z-index:1;cursor:pointer;border:1px solid rgba(255,255,255,.1);}}
.dragsel{{position:absolute;left:2px;right:2px;background:var(--drag);border:2px dashed var(--ac);border-radius:4px;z-index:10;pointer-events:none;}}

/* モーダル */
.ov{{position:fixed;inset:0;background:rgba(0,0,0,.7);z-index:3000;display:flex;align-items:center;justify-content:center;backdrop-filter:blur(4px);}}
.modal{{background:var(--sf);border:1px solid var(--bd);border-radius:12px;padding:20px;width:390px;}}
.ma{{display:flex;gap:7px;margin-top:14px;}}
.btn{{flex:1;padding:8px;border-radius:6px;border:none;font-weight:600;cursor:pointer;}}
.bp{{background:var(--ac);color:#fff;}}
.bs{{background:var(--sf2);color:var(--tx);border:1px solid var(--bd);}}
.bd{{background:var(--ng);color:#fff;}}
.be{{background:var(--wn);color:#000;}}
.fi,.fs2{{width:100%;padding:7px 10px;border-radius:6px;border:1px solid var(--bd);background:var(--sf2);color:var(--tx);}}

/* トースト・ローディング */
.toast{{position:fixed;bottom:16px;right:16px;padding:10px 16px;border-radius:8px;font-weight:600;z-index:9999;color:#fff;}}
.ldg{{position:fixed;inset:0;background:rgba(0,0,0,.5);display:flex;align-items:center;justify-content:center;z-index:9998;color:#tx;}}
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
    <div style="display:flex;align-items:center;gap:5px;">
      <button id="navP" class="vt">◀</button>
      <div id="plbl" style="font-weight:700;min-width:140px;text-align:center;"></div>
      <button id="navN" class="vt">▶</button>
    </div>
    <button id="tdBtn" class="vt">今日</button>
    <div id="pbanner">
      <span style="color:var(--cp);font-size:11px;font-weight:700;">📋 コピー中:</span>
      <span id="pcnt" style="font-size:11px;"></span>
      <button id="pexec" class="vt" style="background:var(--cp);color:#000;">貼り付け</button>
      <button id="pcancel" class="vt">✕</button>
    </div>
    <div style="margin-left:auto;display:flex;gap:5px;">
      <select id="fstaff" class="fsel"><option value="">全スタッフ</option></select>
      <select id="fdept" class="fsel"><option value="">全部門</option></select>
    </div>
  </div>
  <div id="cal"></div>
</div>

<div class="ov" id="regOv" style="display:none" onclick="if(event.target===this)closeReg()">
  <div class="modal">
    <div class="mt" style="font-size:15px;font-weight:700;margin-bottom:15px;">📋 シフト登録/修正</div>
    <input type="hidden" id="editIdx" value="-1">
    <div class="fg"><label class="fl">従業員</label><select class="fs2" id="mStaff"></select></div>
    <div class="fg" style="margin-top:10px;"><label class="fl">部門</label><select class="fs2" id="mDept"></select></div>
    <div class="fg" style="margin-top:10px;"><label class="fl">日付</label><input type="date" class="fi" id="mDate"></div>
    <div class="fg" style="margin-top:10px;">
      <label class="fl">時間 (夜勤は25:00等で入力可)</label>
      <div style="display:grid;grid-template-columns:1fr 20px 1fr;align-items:center;">
        <input type="text" class="fi" id="mS" value="09:00">
        <div style="text-align:center;">→</div>
        <input type="text" class="fi" id="mE" value="18:00">
      </div>
    </div>
    <div class="ma">
      <button class="btn bs" onclick="closeReg()">閉じる</button>
      <button class="btn bp" onclick="saveShift()">保存</button>
    </div>
  </div>
</div>

<div class="ov" id="detOv" style="display:none" onclick="if(event.target===this)closeDet()">
  <div class="modal">
    <div class="mt" style="font-size:15px;font-weight:700;margin-bottom:15px;">📌 シフト詳細</div>
    <div id="detBody" style="line-height:1.6;"></div>
    <div class="ma">
      <button class="btn bs" onclick="closeDet()">閉じる</button>
      <button class="btn bc" onclick="startCopy()">コピー</button>
      <button class="btn be" onclick="openEdit()">修正</button>
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
const HPX = 48;

const $$ = id => document.getElementById(id);
const mk = (t,c) => {{ const e=document.createElement(t); if(c)e.className=c; return e; }};
const fmt = d => `${{d.getFullYear()}}-${{p2(d.getMonth()+1)}}-${{p2(d.getDate())}}`;
const p2 = n => String(n).padStart(2,'0');
const tod = () => fmt(new Date());
const pd_ = s => new Date(s.includes('T') ? s : s.replace(' ','T'));
const m2t = m => `${{p2(Math.floor(m/60))}}:${{p2(m%60)}}`;
const getClr = d => CLRS[DEPTS.indexOf(d) % CLRS.length] || "#ccc";
const rgba = (h,a) => {{ const r=parseInt(h.slice(1,3),16),g=parseInt(h.slice(3,5),16),b=parseInt(h.slice(5,7),16); return `rgba(${{r}},${{g}},${{b}},${{a}})`; }};

window.onload = () => {{
  ['fstaff','mStaff'].forEach(id => STAFF.forEach(s => $$(id).appendChild(new Option(s,s))));
  ['fdept', 'mDept' ].forEach(id => DEPTS.forEach(d => $$(id).appendChild(new Option(d,d))));
  document.querySelector('.vtab').onclick = e => {{ if(e.target.dataset.v) setView(e.target.dataset.v); }};
  $$('navP').onclick = () => nav(-1);
  $$('navN').onclick = () => nav(1);
  $$('tdBtn').onclick = () => {{ cur=new Date(); cur.setHours(0,0,0,0); renderView(); }};
  $$('pcancel').onclick = () => {{ clip=null; pasteDates.clear(); renderView(); }};
  $$('pexec').onclick = execPaste;
  $$('fstaff').onchange = renderView;
  $$('fdept').onchange = renderView;
  $$('cal').onclick = onCalClick;
  renderView();
}};

function setView(v) {{
  view = v;
  document.querySelectorAll('.vt').forEach(e => e.classList.toggle('on', e.dataset.v === v));
  renderView();
}}

function nav(d) {{
  if(view==='day') cur.setDate(cur.getDate()+d);
  else if(view.includes('week')) cur.setDate(cur.getDate()+d*7);
  else cur.setMonth(cur.getMonth()+d);
  renderView();
}}

function renderView() {{
  const cal = $$('cal'); cal.innerHTML = '';
  $$('pbanner').classList.toggle('show', !!clip);
  if(clip) $$('pcnt').textContent = `${{clip.staff}} (${{clip.start.split('T')[1].slice(0,5)}}-)`;

  if(view === 'day') renderDay();
  else if(view === 'week') renderWeek();
  else if(view === 'staff-week') renderStaffWeek();
  else renderMonth();
}}

function onCalClick(e) {{
  const sb = e.target.closest('.sb, .mmerge');
  if(sb) {{
    const idx = parseInt(sb.dataset.idx);
    if(!isNaN(idx)) {{ showDet(SHIFTS[idx]); return; }}
  }}
  const cell = e.target.closest('[data-date]');
  if(cell) {{
    const ds = cell.dataset.date;
    if(clip) {{
      if(pasteDates.has(ds)) pasteDates.delete(ds); else pasteDates.add(ds);
      renderView();
    }} else {{
      openReg(ds, "09:00", "18:00", cell.dataset.staff || "");
    }}
  }}
}}

// ── 日ビュー描画 & ドラッグ修正 ──
function renderDay() {{
  const ds=fmt(cur), fil=getFil();
  $$('plbl').textContent = ds;
  const staff = $$('fstaff').value ? [$$('fstaff').value] : STAFF;
  const dv=mk('div','mv'); // 構造は月ビューに合わせる
  const body=mk('div','dv'); body.style.display='flex'; body.style.height='100%';
  
  // 時間軸
  const tc=mk('div','dtc'); tc.style.width='50px'; tc.style.flexShrink='0';
  for(let h=0; h<30; h++) {{ 
    const ts=mk('div','dts'); ts.style.height=HPX+'px'; ts.textContent=h>23?p2(h-24)+':00':p2(h)+':00';
    tc.appendChild(ts);
  }}
  body.appendChild(tc);

  const scs=mk('div','dscs'); scs.style.display='flex'; scs.style.flex='1'; scs.style.overflowX='auto';
  staff.forEach(s => {{
    const col=mk('div','dscol'); col.style.minWidth='120px'; col.style.flex='1'; col.style.position='relative'; col.style.borderLeft='1px solid var(--bd)';
    col.innerHTML=`<div style="text-align:center;padding:5px;background:var(--sf2);position:sticky;top:0;z-index:5;border-bottom:1px solid var(--bd);">${{s}}</div>`;
    
    // ドラッグ登録の実装
    setupDrag(col, ds, s);

    fil.filter(x => x.staff===s && x.start.startsWith(ds)).forEach(x => {{
      const b = createBlock(x); col.appendChild(b);
    }});
    scs.appendChild(col);
  }});
  body.appendChild(scs); cal.appendChild(body);
}}

function setupDrag(col, ds, staff) {{
  col.onmousedown = e => {{
    if(clip || e.target.closest('.sb')) return;
    const rect = col.getBoundingClientRect();
    const startY = e.clientY - rect.top;
    const sm = Math.round((startY - 30) / (HPX/4)) * 15; // 15分刻み
    const el = mk('div','dragsel'); el.style.top = (sm/60*HPX + 30) + 'px'; col.appendChild(el);

    const onMove = me => {{
      const curY = me.clientY - rect.top;
      const em = Math.round((curY - 30) / (HPX/4)) * 15;
      el.style.top = (Math.min(sm, em)/60*HPX + 30) + 'px';
      el.style.height = (Math.abs(em - sm)/60*HPX) + 'px';
    }};
    const onUp = ue => {{
      window.removeEventListener('mousemove', onMove); window.removeEventListener('mouseup', onUp);
      const curY = ue.clientY - rect.top;
      const em = Math.round((curY - 30) / (HPX/4)) * 15;
      el.remove();
      if(Math.abs(em-sm) >= 15) openReg(ds, m2t(Math.min(sm,em)), m2t(Math.max(sm,em)), staff);
    }};
    window.addEventListener('mousemove', onMove); window.addEventListener('mouseup', onUp);
  }};
}}

function createBlock(s) {{
  const st=pd_(s.start), et=pd_(s.end);
  const sm = st.getHours()*60+st.getMinutes();
  let em = et.getHours()*60+et.getMinutes();
  if(et.getDate() !== st.getDate()) em += 1440; // 日またぎ
  
  const b=mk('div','sb'); b.dataset.idx = SHIFTS.indexOf(s);
  const c=getClr(s.dept);
  b.style.cssText=`top:${{sm/60*HPX+30}}px;height:${{Math.max((em-sm)/60*HPX,20)}}px;background:${{rgba(c,0.2)}};border-left:4px solid ${{c}};color:${{c}};width:90%;left:5%;`;
  b.innerHTML=`<div class="sbn">${{s.dept}}</div><div class="sbt">${{p2(st.getHours())}}:${{p2(st.getMinutes())}}-</div>`;
  return b;
}}

// ── スタッフ別週表示 (NEW) ──
function renderStaffWeek() {{
  const ws = new Date(cur); ws.setDate(cur.getDate() - cur.getDay());
  $$('plbl').textContent = `${{ws.getMonth()+1}}/${{ws.getDate()}}の週`;
  const root = $$('cal');
  const grid = mk('div','mgrid sw-grid');
  
  grid.appendChild(mk('div','sw-head'));
  for(let i=0; i<7; i++) {{
    const d = new Date(ws); d.setDate(ws.getDate()+i);
    const h = mk('div','sw-head'); h.textContent = `${{d.getDate()}}(${{['日','月','火','水','木','金','土'][i]}})`;
    grid.appendChild(h);
  }}

  const staff = $$('fstaff').value ? [$$('fstaff').value] : STAFF;
  staff.forEach(name => {{
    const nameCell = mk('div','sw-staff-name'); nameCell.textContent = name; grid.appendChild(nameCell);
    for(let i=0; i<7; i++) {{
      const d = new Date(ws); d.setDate(ws.getDate()+i);
      const ds = fmt(d);
      const cell = mk('div','mc'); cell.dataset.date = ds; cell.dataset.staff = name;
      if(pasteDates.has(ds)) cell.classList.add('psel');
      
      getFil().filter(x => x.staff===name && x.start.startsWith(ds)).forEach(s => {{
        const div = mk('div','mmerge'); const c=getClr(s.dept);
        div.style.cssText = `border-left:3px solid ${{c}}; background:${{rgba(c,0.1)}};`;
        div.textContent = `${{s.start.split('T')[1].slice(0,5)}}-${{s.end.split('T')[1].slice(0,5)}}`;
        div.dataset.idx = SHIFTS.indexOf(s);
        cell.appendChild(div);
      }});
      grid.appendChild(cell);
    }}
  }});
  root.appendChild(grid);
}}

// ── 月表示 ──
function renderMonth() {{
  const y=cur.getFullYear(), m=cur.getMonth(); $$('plbl').textContent = `${{y}}年${{m+1}}月`;
  const first=new Date(y,m,1), start=new Date(first); start.setDate(first.getDate()-first.getDay());
  const grid = mk('div','mgrid'); grid.style.gridTemplateColumns = 'repeat(7,1fr)';
  for(let i=0; i<42; i++) {{
    const d=new Date(start); d.setDate(start.getDate()+i); const ds=fmt(d);
    const cell=mk('div','mc'); cell.dataset.date = ds;
    if(pasteDates.has(ds)) cell.classList.add('psel');
    cell.innerHTML=`<div style="font-size:10px;font-weight:700;">${{d.getDate()}}</div>`;
    getFil().filter(x=>x.start.startsWith(ds)).forEach(x=>{{
      const div=mk('div','mmerge'); const c=getClr(x.dept);
      div.style.cssText=`border-left:3px solid ${{c}};background:${{rgba(c,0.1)}};`;
      div.innerHTML=`<div class="mseg"><b>${{x.staff}}</b> ${{x.start.split('T')[1].slice(0,5)}}</div>`;
      div.dataset.idx = SHIFTS.indexOf(x);
      cell.appendChild(div);
    }});
    grid.appendChild(cell);
  }}
  cal.appendChild(grid);
}}

// ── 登録・修正・削除 ──
function openReg(ds, st="09:00", en="18:00", staff="", idx="-1") {{
  $$('mDate').value=ds; $$('mS').value=st; $$('mE').value=en;
  if(staff) $$('mStaff').value=staff;
  $$('editIdx').value=idx;
  $$('regOv').style.display='flex';
}}

function openEdit() {{
  const s = curS; closeDet();
  const ds = s.start.split('T')[0];
  const st = s.start.split('T')[1].slice(0,5);
  const et = s.end.split('T')[1].slice(0,5);
  openReg(ds, st, et, s.staff, SHIFTS.indexOf(s));
}}

async function saveShift() {{
  const name=$$('mStaff').value, dept=$$('mDept').value, ds=$$('mDate').value, sT=$$('mS').value, eT=$$('mE').value;
  const idx = parseInt($$('editIdx').value);
  showLdg("保存中...");
  
  if(idx !== -1) {{ // 修正時は一度消す
    const o = SHIFTS[idx];
    await fetch(GAS+'?'+new URLSearchParams({{action:'del_shift', name:o.staff, dept:o.dept, start:o.start.replace('T',' ').slice(0,16), end:o.end.replace('T',' ').slice(0,16)}}));
    SHIFTS.splice(idx, 1);
  }}

  const res = await fetch(GAS+'?'+new URLSearchParams({{action:'add_shift', name, dept, start:`${{ds}} ${{sT}}`, end:`${{ds}} ${{eT}}` }}));
  if(res.ok) {{
    SHIFTS.push({{ staff:name, dept, start:`${{ds}}T${{sT}}:00`, end:`${{ds}}T${{eT}}:00` }});
    closeReg(); hideLdg(); renderView();
  }}
}}

async function delShift() {{
  if(!confirm("削除しますか？")) return;
  const s = curS; closeDet(); showLdg("削除中...");
  await fetch(GAS+'?'+new URLSearchParams({{action:'del_shift', name:s.staff, dept:s.dept, start:s.start.replace('T',' ').slice(0,16), end:s.end.replace('T',' ').slice(0,16)}}));
  SHIFTS = SHIFTS.filter(x => x !== s);
  hideLdg(); renderView();
}}

// ── ユーティリティ ──
function showDet(s) {{
  curS = s;
  $$('detBody').innerHTML = `<b>${{s.staff}}</b> (${{s.dept}})<br>${{s.start.replace('T',' ')}} → ${{s.end.replace('T',' ')}}`;
  $$('detOv').style.display='flex';
}}
function closeReg() {{ $$('regOv').style.display='none'; }}
function closeDet() {{ $$('detOv').style.display='none'; }}
function startCopy() {{ clip={{...curS}}; pasteDates.clear(); closeDet(); renderView(); }}
async function execPaste() {{
  if(!clip || pasteDates.size===0) return;
  const s=clip.start.split('T')[1].slice(0,5), e=clip.end.split('T')[1].slice(0,5);
  showLdg("貼り付け中...");
  for(const d of pasteDates) {{
    await fetch(GAS+'?'+new URLSearchParams({{action:'add_shift', name:clip.staff, dept:clip.dept, start:`${{d}} ${{s}}`, end:`${{d}} ${{e}}` }}));
    SHIFTS.push({{ staff:clip.staff, dept:clip.dept, start:`${{d}}T${{s}}:00`, end:`${{d}}T${{e}}:00` }});
  }}
  clip=null; pasteDates.clear(); hideLdg(); renderView();
}}
function getFil() {{
  const s=$$('fstaff').value, d=$$('fdept').value;
  return SHIFTS.filter(x => (!s || x.staff===s) && (!d || x.dept===d));
}}
function showLdg(m) {{ const l=mk('div','ldg'); l.id='_ldg'; l.innerHTML=`<span>${{m}}</span>`; document.body.appendChild(l); }}
function hideLdg() {{ document.getElementById('_ldg')?.remove(); }}
function renderWeek() {{ setView('week'); }} // 互換性のため
</script>
</body>
</html>"""

    components.html(html, height=H, scrolling=False)
