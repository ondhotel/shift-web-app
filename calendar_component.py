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

    staff_json = json.dumps(staff_list,  ensure_ascii=False)
    dept_json  = json.dumps(dept_list,   ensure_ascii=False)
    shifts_json_str = json.dumps(shifts_json, ensure_ascii=False)
    color_palette = ["#4f86c6","#e07b5a","#5aad8f","#b07fc7","#e0b84a","#5abfcc","#e07bb0","#7ec45a","#c47e5a","#5a7ec4","#c4b05a","#5ac4a2","#c45a7e","#8fc45a","#c45ab0","#5a8fc4"]
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

#app{{display:flex;flex-direction:column;height:{H}px;}}
#topbar{{flex-shrink:0;display:flex;align-items:center;gap:8px;padding:8px 12px;background:var(--sf);border-bottom:1px solid var(--bd);flex-wrap:wrap;}}
#pbanner{{display:none;width:100%;align-items:center;gap:8px;padding:4px 0 2px;flex-wrap:wrap;}}
#pbanner.show{{display:flex;}}
.pbl{{font-size:11px;color:var(--cp);font-weight:700;}}
.pbb{{padding:3px 10px;border-radius:5px;border:1px solid var(--cp);background:rgba(240,160,91,.15);color:var(--cp);cursor:pointer;font-size:11px;font-weight:600;}}
#cal{{flex:1;overflow:hidden;display:flex;flex-direction:column;min-height:0;}}

.vtab{{display:flex;background:var(--sf2);border-radius:7px;padding:3px;gap:2px;}}
.vt{{padding:4px 13px;border-radius:5px;cursor:pointer;font-size:12px;font-weight:500;color:var(--tx2);border:none;background:transparent;}}
.vt.on{{background:var(--ac);color:#fff;}}
.navg{{display:flex;align-items:center;gap:5px;}}
.nb{{width:28px;height:28px;border-radius:5px;border:1px solid var(--bd);background:var(--sf2);color:var(--tx);cursor:pointer;display:flex;align-items:center;justify-content:center;}}
#plbl{{font-size:14px;font-weight:700;min-width:160px;text-align:center;}}
.tdbtn{{padding:4px 11px;border-radius:5px;border:1px solid var(--bd);background:var(--sf2);color:var(--tx);cursor:pointer;font-size:12px;}}
.fgrp{{display:flex;gap:6px;margin-left:auto;align-items:center;}}
.fsel{{padding:4px 7px;border-radius:5px;border:1px solid var(--bd);background:var(--sf2);color:var(--tx);font-size:12px;}}

/* ビュー構造 */
.mv,.wv,.dv,.sv{{flex:1;display:flex;flex-direction:column;overflow:hidden;}}
.mgrid,.wbody,.dbody,.sbody{{flex:1;overflow-y:auto;position:relative;}}
.mrow,.whdr,.dshdr{{display:grid;border-bottom:1px solid var(--bd);}}
.mc{{border-right:1px solid var(--bd);padding:4px;cursor:pointer;min-height:75px;position:relative;}}
.mc.psel,.sw-day-cell.psel,.wdcol.psel{{background:var(--sel)!important;outline:2px solid var(--cp);outline-offset:-2px;}}
.dn{{font-size:11px;font-weight:600;width:20px;height:20px;display:flex;align-items:center;justify-content:center;border-radius:50%;font-family:var(--mn);}}
.tod .dn{{background:var(--ac);color:#fff;}}

/* 週（スタッフ）: スクショ用 */
.sw-grid {{ display: grid; grid-template-columns: 100px repeat(7, 1fr); min-width: 100%; }}
.sw-head {{ background: var(--sf); border-bottom: 2px solid var(--bd); padding: 8px; font-weight: 700; text-align: center; position: sticky; top: 0; z-index: 10; border-right: 1px solid var(--bd); }}
.sw-staff-cell {{ background: var(--sf); border-bottom: 1px solid var(--bd); border-right: 1px solid var(--bd); padding: 8px; font-weight: 600; position: sticky; left: 0; z-index: 5; display: flex; align-items: center; }}
.sw-day-cell {{ border-bottom: 1px solid var(--bd); border-right: 1px solid var(--bd); padding: 4px; min-height: 60px; cursor: pointer; }}

/* 時間軸ビュー */
.wdcol,.dscol{{position:relative;border-right:1px solid var(--bd);cursor:crosshair;}}
.sb{{position:absolute;border-radius:4px;padding:2px 4px;font-size:10px;font-weight:600;overflow:hidden;z-index:1;cursor:pointer;border:1px solid rgba(255,255,255,.1);}}
.dragsel{{position:absolute;left:2px;right:2px;background:var(--drag);border:2px dashed var(--ac);border-radius:4px;z-index:10;pointer-events:none;}}

/* モーダル */
.ov{{position:fixed;inset:0;background:rgba(0,0,0,.72);z-index:3000;display:flex;align-items:center;justify-content:center;backdrop-filter:blur(4px);}}
.modal{{background:var(--sf);border:1px solid var(--bd);border-radius:12px;padding:20px;width:390px;}}
.ma{{display:flex;gap:7px;margin-top:14px;}}
.btn{{flex:1;padding:8px;border-radius:6px;border:none;font-weight:600;cursor:pointer;}}
.bp{{background:var(--ac);color:#fff;}}.bs{{background:var(--sf2);color:var(--tx);}}.bd{{background:var(--ng);color:#fff;}}.be{{background:var(--wn);color:#000;}}.bc{{background:rgba(240,160,91,.2);color:var(--cp);border:1px solid var(--cp);}}
.ldg{{position:fixed;inset:0;background:rgba(0,0,0,.55);display:flex;align-items:center;justify-content:center;z-index:9998;gap:10px;color:var(--tx);}}
.spin{{width:17px;height:17px;border:2px solid var(--bd);border-top-color:var(--ac);border-radius:50%;animation:sp .7s linear infinite;}}
@keyframes sp{{to{{transform:rotate(360deg);}}}}
</style>
</head>
<body>
<div id="app">
  <div id="topbar">
    <div class="vtab">
      <button class="vt on" data-v="day">日</button>
      <button class="vt"    data-v="week">週</button>
      <button class="vt"    data-v="s-week">週(スタッフ)</button>
      <button class="vt"    data-v="month">月</button>
    </div>
    <div class="navg"><button class="nb" id="navP">&#8249;</button><div id="plbl"></div><button class="nb" id="navN">&#8250;</button></div>
    <button class="tdbtn" id="tdBtn">今日</button>
    <div id="pbanner"><span class="pbl">📋 ペースト</span> <span class="pbcnt" id="pcnt"></span><button class="pbb exec" id="pexec" style="display:none">実行</button><button class="pbb cancel" id="pcancel">✕</button></div>
    <div class="fgrp"><select class="fsel" id="fstaff"><option value="">全スタッフ</option></select><select class="fsel" id="fdept"><option value="">全部門</option></select></div>
  </div>
  <div id="cal"></div>
</div>

<div class="ov" id="regOv" style="display:none" onclick="if(event.target===this)closeReg()">
  <div class="modal">
    <div class="mt" id="mTitle" style="font-size:15px;font-weight:700;margin-bottom:14px;">📋 シフト登録</div>
    <input type="hidden" id="mEditMode" value="0">
    <div style="margin-bottom:11px;"><label class="fl">従業員</label><select class="fs2" id="mStaff" style="width:100%;padding:7px;"></select></div>
    <div style="margin-bottom:11px;"><label class="fl">部門</label><select class="fs2" id="mDept" style="width:100%;padding:7px;"></select></div>
    <div style="margin-bottom:11px;"><label class="fl">日付</label><input type="date" class="fi" id="mDate" style="width:100%;padding:7px;"></div>
    <div style="margin-bottom:11px;"><label class="fl">時間 (夜勤は25:00等も可)</label><div style="display:grid;grid-template-columns:1fr 20px 1fr;align-items:center;"><input type="text" class="fi" id="mS" value="09:00" style="padding:7px;"><span>→</span><input type="text" class="fi" id="mE" value="18:00" style="padding:7px;"></div></div>
    <div class="ma"><button class="btn bs" onclick="closeReg()">閉じる</button><button class="btn bp" onclick="saveShift()">保存</button></div>
  </div>
</div>

<div class="ov" id="detOv" style="display:none" onclick="if(event.target===this)closeDet()">
  <div class="modal"><div class="mt" style="font-size:15px;font-weight:700;margin-bottom:14px;">📌 詳細</div><div id="detBody"></div><div class="ma"><button class="btn bs" onclick="closeDet()">閉じる</button><button class="btn be" onclick="openEdit()">📝 修正</button><button class="btn bc" onclick="startCopy()">📋 コピー</button><button class="btn bd" onclick="delShift()">削除</button></div></div>
</div>

<script>
const GAS = "{gas_url}", STAFF = {staff_json}, DEPTS = {dept_json}, CLRS = {color_palette};
let SHIFTS = {shifts_json_str}, view = 'day', cur = new Date(); cur.setHours(0,0,0,0);
let clip = null, pasteDates = new Set(), curS = null;
const HPX = 48, DAY_H = 30, MID_H = 24;

const $$ = id => document.getElementById(id);
const mk = (t,c) => {{ const e=document.createElement(t); if(c)e.className=c; return e; }};
const fmt = d => `${{d.getFullYear()}}-${{p2(d.getMonth()+1)}}-${{p2(d.getDate())}}`;
const p2 = n => String(n).padStart(2,'0');
const tod = () => fmt(new Date());
const pd_ = s => new Date(s);
const m2t = m => `${{p2(Math.floor(m/60))}}:${{p2(m%60)}}`;

window.addEventListener('load', () => {{
  ['fstaff','mStaff'].forEach(id => STAFF.forEach(s => $$(id).appendChild(new Option(s,s))));
  ['fdept', 'mDept' ].forEach(id => DEPTS.forEach(d => $$(id).appendChild(new Option(d,d))));
  document.querySelector('.vtab').addEventListener('click', e => {{ if(e.target.dataset.v) setView(e.target.dataset.v); }});
  $$('navP').onclick = () => nav(-1); $$('navN').onclick = () => nav(1);
  $$('tdBtn').onclick = () => {{ cur=new Date(); cur.setHours(0,0,0,0); renderView(); }};
  $$('fstaff').onchange = renderView; $$('fdept').onchange = renderView;
  $$('pcancel').onclick = cancelCopy; $$('pexec').onclick = execPaste;
  $$('cal').addEventListener('click', onCalClick);
  renderView();
}});

function setView(v) {{ view = v; document.querySelectorAll('.vt').forEach(e => e.classList.toggle('on', e.dataset.v === v)); renderView(); }}
function nav(d) {{ if (view==='day') cur.setDate(cur.getDate()+d); else if (view.includes('week')) cur.setDate(cur.getDate()+d*7); else cur.setMonth(cur.getMonth()+d); renderView(); }}

function onCalClick(e) {{
  const chip = e.target.closest('.mmerge, .sb');
  if(chip) {{ const idx = parseInt(chip.dataset.idx); if(!isNaN(idx)) {{ if(clip) togglePasteDate(fmt(pd_(SHIFTS[idx].start))); else showDet(SHIFTS[idx]); return; }} }}
  const cell = e.target.closest('[data-date]');
  if(cell) {{ const ds = cell.dataset.date; if(clip) togglePasteDate(ds); else if(e.target===cell||cell.classList.contains('mc')) openReg(ds, "09:00", "18:00", cell.dataset.staff||""); }}
}}

function renderView() {{
  const cal = $$('cal'); cal.innerHTML = '';
  if(view==='day') renderDay(); else if(view==='week') renderWeek(); else if(view==='s-week') renderStaffWeek(); else renderMonth();
  updateBanner();
}}

// ── 週(スタッフ): 全表示 ──
function renderStaffWeek() {{
  const ws = new Date(cur); ws.setDate(cur.getDate() - cur.getDay()); $$('plbl').textContent = `${{fmt(ws)}} 〜`;
  const fil = getFil(), root = $$('cal'), container = mk('div', 'sbody');
  const sw = mk('div', 'sw-grid'); sw.appendChild(mk('div', 'sw-head'));
  for(let i=0; i<7; i++) {{
    const d = new Date(ws); d.setDate(ws.getDate()+i);
    const h = mk('div', 'sw-head'); h.textContent = `${{d.getDate()}}(${{['日','月','火','水','木','金','土'][i]}})`; sw.appendChild(h);
  }}
  const targetStaff = $$('fstaff').value ? [$$('fstaff').value] : STAFF;
  targetStaff.forEach(s => {{
    const sc = mk('div', 'sw-staff-cell'); sc.textContent = s; sw.appendChild(sc);
    for(let i=0; i<7; i++) {{
      const d = new Date(ws); d.setDate(ws.getDate()+i); const ds = fmt(d);
      const dc = mk('div', 'sw-day-cell'); dc.dataset.date = ds; dc.dataset.staff = s;
      if(pasteDates.has(ds)) dc.classList.add('psel');
      const dayS = fil.filter(x => x.staff === s && x.start.startsWith(ds));
      if(dayS.length) {{
        const m = mk('div', 'mmerge'); const col = deptClr(dayS[0].dept);
        m.style.cssText = `border-left:3px solid ${{col}}; background:${{rgba(col,.1)}}; color:${{col}};`;
        m.innerHTML = `<div class="mseg"><b>${{dayS[0].start.split('T')[1].slice(0,5)}}</b></div>`;
        m.dataset.idx = SHIFTS.indexOf(dayS[0]); dc.appendChild(m);
      }}
      sw.appendChild(dc);
    }}
  }});
  container.appendChild(sw); root.appendChild(container);
}}

// ── ドラッグ計算 (バグ修正) ──
function setupDrag(col, ds, dsN, s) {{
  col.onmousedown = (e) => {{
    if(clip || e.target.closest('.sb')) return;
    const rect = col.getBoundingClientRect();
    const scrollParent = col.closest('.dbody') || col.closest('.wbody');
    const getY = (me) => me.clientY - rect.top + scrollParent.scrollTop;
    const sm = Math.round((getY(e)/HPX)*4)/4*60;
    const el = mk('div', 'dragsel'); el.style.top = (sm/60*HPX)+'px'; col.appendChild(el);
    const onMove = (me) => {{
      const em = Math.round((getY(me)/HPX)*4)/4*60;
      el.style.top = Math.min(sm, em)/60*HPX + 'px'; el.style.height = Math.abs(em - sm)/60*HPX + 'px';
    }};
    const onUp = (ue) => {{
      window.removeEventListener('mousemove', onMove); window.removeEventListener('mouseup', onUp);
      const em = Math.round((getY(ue)/HPX)*4)/4*60; el.remove();
      if(Math.abs(em-sm) < 15) return;
      const sMin = Math.min(sm, em), eMin = Math.max(sm, em);
      openReg(sMin >= 1440 ? dsN : ds, m2t(sMin % 1440), m2t(eMin), s);
    }};
    window.addEventListener('mousemove', onMove); window.addEventListener('mouseup', onUp);
  }};
}}

// ── 保存・修正ロジック ──
async function saveShift() {{
  const name = $$('mStaff').value, dept = $$('mDept').value, d = $$('mDate').value, sT = $$('mS').value, eT = $$('mE').value;
  if(!name || !dept || !d || !sT || !eT) return; showLdg("保存中...");
  if($$('mEditMode').value === "1" && curS) {{
    await fetch(GAS+'?'+new URLSearchParams({{action:'del_shift', name:curS.staff, dept:curS.dept, start:curS.start.replace('T',' ').slice(0,16), end:curS.end.replace('T',' ').slice(0,16)}}));
    SHIFTS = SHIFTS.filter(x => x !== curS);
  }}
  const res = await fetch(GAS+'?'+new URLSearchParams({{action:'add_shift', name, dept, start: `${{d}} ${{sT}}`, end: `${{d}} ${{eT}}` }}));
  if(res.ok) {{
    SHIFTS.push({{ staff: name, dept: dept, start: `${{d}}T${{sT}}:00`, end: `${{d}}T${{eT}}:00` }});
    closeReg(); hideLdg(); renderView();
  }} else {{ hideLdg(); alert("失敗"); }}
}}

function openReg(ds, st, en, staff) {{
  $$('mTitle').textContent = "📋 シフト登録"; $$('mEditMode').value = "0";
  $$('mDate').value = ds; $$('mS').value = st; $$('mE').value = en;
  if(staff) $$('mStaff').value = staff; $$('regOv').style.display = 'flex';
}}
function openEdit() {{
  const s = curS; if(!s) return; closeDet(); $$('mTitle').textContent = "📝 修正"; $$('mEditMode').value = "1";
  $$('mStaff').value = s.staff; $$('mDept').value = s.dept; $$('mDate').value = s.start.split('T')[0];
  $$('mS').value = s.start.split('T')[1].slice(0,5);
  let et = s.end.split('T')[1].slice(0,5);
  if(new Date(s.end).getDate() !== new Date(s.start).getDate()) {{
    let [h, m] = et.split(':'); et = (parseInt(h)+24) + ':' + m;
  }}
  $$('mE').value = et; $$('regOv').style.display = 'flex';
}}

// ── 月別 (集約) ──
function renderMonth() {{
  const y=cur.getFullYear(), mo=cur.getMonth(); $$('plbl').textContent=`${{y}}年${{mo+1}}月`;
  const fil=getFil(), first=new Date(y,mo,1), sdow=first.getDay();
  const mg=mk('div','mgrid'), mv=mk('div','mv'), mh=mk('div','mrow mhdr');
  ['日','月','火','水','木','金','土'].forEach(d=>{{ const c=mk('div','mhc'); c.textContent=d; mh.appendChild(c); }});
  mv.appendChild(mh);
  let d=new Date(first); d.setDate(d.getDate()-sdow);
  for(let r=0;r<6;r++) {{
    const row=mk('div','mrow');
    for(let i=0;i<7;i++) {{
      const ds=fmt(d), mc=mk('div','mc'+(d.getMonth()!==mo?' other':'')+(ds===tod()?' tod':''));
      mc.dataset.date=ds; if(pasteDates.has(ds)) mc.classList.add('psel');
      mc.innerHTML=`<div class="dn">${{d.getDate()}}</div>`;
      const dayS = fil.filter(x=>x.start.startsWith(ds));
      const summary = {{}}; dayS.forEach(s => {{ if(!summary[s.staff]) summary[s.staff] = s; }});
      Object.values(summary).forEach(x=>{{
        const m=mk('div','mmerge'); const col=deptClr(x.dept);
        m.style.cssText=`border-left:3px solid ${{col}};background:${{rgba(col,0.1)}};color:${{col}};`;
        m.innerHTML=`<div class="mseg"><b>${{x.staff}}</b></div>`;
        m.dataset.idx=SHIFTS.indexOf(x); mc.appendChild(m);
      }});
      row.appendChild(mc); d.setDate(d.getDate()+1);
    }}
    mg.appendChild(row);
  }}
  mv.appendChild(mg); $$('cal').appendChild(mv);
}}

// ── 週別 (Lane復旧) ──
function renderWeek() {{
  const ws=new Date(cur); ws.setDate(cur.getDate()-cur.getDay()); $$('plbl').textContent=`${{fmt(ws)}} 〜`;
  const fil=getFil(), root=$$('cal'), wv=mk('div','wv'), wh=mk('div','whdr'); wh.appendChild(mk('div','wcrn'));
  for(let i=0;i<7;i++) {{
    const d=new Date(ws); d.setDate(ws.getDate()+i); const ds=fmt(d);
    const h=mk('div','whd'); h.dataset.date=ds; h.innerHTML=`<div class="wdow">${{['日','月','火','水','木','金','土'][i]}}</div><div class="wdn">${{d.getDate()}}</div>`;
    wh.appendChild(h);
  }}
  wv.appendChild(wh); const wb=mk('div','wbody'), tc=mk('div','wtc');
  for(let h=0;h<24;h++) {{ const t=mk('div','wts'); t.textContent=p2(h)+':00'; tc.appendChild(t); }}
  wb.appendChild(tc); const wdc=mk('div','wdc');
  for(let i=0;i<7;i++) {{
    const d=new Date(ws); d.setDate(ws.getDate()+i); const ds=fmt(d);
    const col=mk('div','wdcol'); for(let h=0;h<24;h++) col.appendChild(mk('div','whs'));
    col.dataset.date=ds; if(pasteDates.has(ds)) col.classList.add('psel');
    const dayS = fil.filter(x=>x.start.startsWith(ds)).map(x=>{{
      const st=pd_(x.start), et=pd_(x.end);
      return {{...x, sm:st.getHours()*60+st.getMinutes(), em:et.getHours()*60+et.getMinutes()+(et.getDate()!==st.getDate()?1440:0)}};
    }});
    const sorted = dayS.sort((a,b)=>a.sm-b.sm), lanes = [];
    sorted.forEach(s => {{
      let l=-1; for(let j=0;j<lanes.length;j++) if(lanes[j]<=s.sm){{l=j;lanes[j]=s.em;break;}}
      if(l===-1){{l=lanes.length;lanes.push(s.em);}}
      const b=mkBlock(s,0); const W=100/Math.max(lanes.length,1), L=l*W;
      b.style.width=W-2+'%'; b.style.left=L+1+'%'; col.appendChild(b);
    }});
    setupDrag(col, ds, ds, ""); wdc.appendChild(col);
  }}
  wb.appendChild(wdc); wv.appendChild(wb); root.appendChild(wv);
}}

// ── 日別 ──
function renderDay() {{
  const ds=fmt(cur), td=tod(), fil=getFil(); const nxt=new Date(cur); nxt.setDate(cur.getDate()+1); const dsN=fmt(nxt);
  $$('plbl').textContent=ds; const targetStaff = $$('fstaff').value ? [$$('fstaff').value] : STAFF;
  const dv=mk('div','dv'), sh=mk('div','dshdr'); sh.appendChild(mk('div','dcrn'));
  targetStaff.forEach(s=>{{ const h=mk('div','dsch'); h.textContent=s; sh.appendChild(h); }}); dv.appendChild(sh);
  const db=mk('div','dbody'), tc=mk('div','dtc');
  for(let h=0;h<DAY_H;h++) {{ const t=mk('div','dts'+(h===MID_H?' mid':'')); t.textContent=h>=24?p2(h-24)+':00':p2(h)+':00'; tc.appendChild(t); }}
  db.appendChild(tc); const sc=mk('div','dscs');
  targetStaff.forEach(s=>{{
    const col=mk('div','dscol'); for(let h=0;h<DAY_H;h++) col.appendChild(mk('div','dhs'));
    fil.filter(x=>x.staff===s && x.start.startsWith(ds)).forEach(x=>col.appendChild(mkBlock(x,0)));
    fil.filter(x=>x.staff===s && x.start.startsWith(dsN)).forEach(x=>{{ if(pd_(x.start).getHours()<6) col.appendChild(mkBlock(x,1440)); }});
    setupDrag(col, ds, dsN, s); sc.appendChild(col);
  }});
  db.appendChild(sc); dv.appendChild(db); $$('cal').appendChild(dv);
}}

function mkBlock(s, offset) {{
  const st=pd_(s.start), et=pd_(s.end);
  const sm=st.getHours()*60+st.getMinutes()+offset;
  let em=et.getHours()*60+et.getMinutes()+offset; if(et.getDate()!==st.getDate()) em+=1440;
  const b=mk('div','sb'); b.dataset.idx=SHIFTS.indexOf(s); const col=deptClr(s.dept);
  b.style.cssText=`top:${{sm/60*HPX}}px;height:${{Math.max((em-sm)/60*HPX,20)}}px;background:${{rgba(col,.2)}};border-left:3px solid ${{col}};color:${{col}};width:90%;left:5%;`;
  b.innerHTML=`<div class="sbn">${{s.dept}}</div><div class="sbt">${{st.getHours()}}:${{p2(st.getMinutes())}}-</div>`;
  return b;
}}

function showDet(s) {{
  curS = s; const col = deptClr(s.dept);
  $$('detBody').innerHTML = `<div style="padding:4px;border-radius:4px;background:${{rgba(col,.2)}};color:${{col}};margin-bottom:8px;">${{s.dept}}</div><div>👤 ${{s.staff}}</div><div>📅 ${{s.start.replace('T',' ').slice(5,16)}} 〜</div>`;
  $$('detOv').style.display = 'flex';
}}
function getFil() {{ const fs = $$('fstaff').value, fd = $$('fdept').value; return SHIFTS.filter(s => (!fs || s.staff === fs) && (!fd || s.dept === fd)); }}
function deptClr(d) {{ const i = DEPTS.indexOf(d); return CLRS[i % CLRS.length] || "#ccc"; }}
function rgba(h, a) {{ const r=parseInt(h.slice(1,3),16), g=parseInt(h.slice(3,5),16), b=parseInt(h.slice(5,7),16); return `rgba(${{r}},${{g}},${{b}},${{a}})`; }}
function closeReg() {{ $$('regOv').style.display='none'; }}
function closeDet() {{ $$('detOv').style.display='none'; curS=null; }}
function showLdg(m) {{ const l=mk('div','ldg'); l.id='_ldg'; l.innerHTML=`<div class="spin"></div><span>${{m}}</span>`; document.body.appendChild(l); }}
function hideLdg() {{ document.getElementById('_ldg')?.remove(); }}
function cancelCopy() {{ clip=null; pasteDates.clear(); renderView(); }}
function togglePasteDate(ds) {{ if(pasteDates.has(ds)) pasteDates.delete(ds); else pasteDates.add(ds); renderView(); }}
function updateBanner() {{ const b = $$('pbanner'); if(clip) {{ b.classList.add('show'); $$('pcnt').textContent=`${{clip.staff}} (${{pasteDates.size}}日)`; $$('pexec').style.display=pasteDates.size>0?'':'none'; }} else b.classList.remove('show'); }}
async function execPaste() {{
  if(!clip || pasteDates.size===0) return;
  const s=clip.start.split('T')[1].slice(0,5), e=clip.end.split('T')[1].slice(0,5);
  showLdg("貼り付け中...");
  for(const d of pasteDates) {{
    await fetch(GAS+'?'+new URLSearchParams({{action:'add_shift', name:clip.staff, dept:clip.dept, start:`${{d}} ${{s}}`, end:`${{d}} ${{e}}` }}));
    SHIFTS.push({{ staff:clip.staff, dept:clip.dept, start:`${{d}}T${{s}}:00`, end:`${{d}}T${{e}}:00` }});
  }}
  cancelCopy(); hideLdg(); renderView();
}}
async function delShift() {{
  if(!curS || !confirm("削除？")) return;
  const s = curS; closeDet(); showLdg("削除中...");
  await fetch(GAS+'?'+new URLSearchParams({{action:'del_shift', name:s.staff, dept:s.dept, start:s.start.replace('T',' ').slice(0,16), end:s.end.replace('T',' ').slice(0,16)}}));
  SHIFTS = SHIFTS.filter(x => x !== s); hideLdg(); renderView();
}}
</script>
</body>
</html>"""
    components.html(html, height=H, scrolling=False)
