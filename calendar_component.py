import streamlit.components.v1 as components
import json
import pandas as pd

def render_calendar_component(df: pd.DataFrame, staff_list: list, dept_list: list, gas_url: str):
    # --- 1. データの準備 ---
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

    shifts_json_str = json.dumps(shifts_json, ensure_ascii=False)
    staff_json = json.dumps(staff_list, ensure_ascii=False)
    dept_json = json.dumps(dept_list, ensure_ascii=False)
    color_palette_json = json.dumps([
        "#4f86c6","#e07b5a","#5aad8f","#b07fc7","#e0b84a",
        "#5abfcc","#e07bb0","#7ec45a","#c47e5a","#5a7ec4",
        "#c4b05a","#5ac4a2","#c45a7e","#8fc45a","#c45ab0","#5a8fc4"
    ])

    H = 800

    # --- 2. HTML テンプレート (Pythonの波括弧エラーを避けるため replace 方式) ---
    html_template = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@300;400;500;700&family=JetBrains+Mono:wght@400;600&display=swap');
:root {
  --bg:#0f1117;--sf:#1a1d27;--sf2:#22263a;--bd:#2d3148;
  --tx:#e8eaf2;--tx2:#6b7094;--ac:#5b8af0;--ac2:#8b5cf6;
  --ok:#34d399;--ng:#f87171;--wn:#f59e0b;--cp:#f0a05b;
  --tod:rgba(91,138,240,.12);--hv:rgba(91,138,240,.08);
  --drag:rgba(91,138,240,.25);--nday:rgba(139,92,246,.06);
  --sel:rgba(240,160,91,.28);
  --fn:'Noto Sans JP',sans-serif;--mn:'JetBrains Mono',monospace;
}
* { margin:0; padding:0; box-sizing:border-box; }
html,body { width:100%; height:__H__px; overflow:hidden; background:var(--bg); color:var(--tx); font-family:var(--fn); font-size:13px; user-select:none; }

/* レイアウト */
#app { display:flex; flex-direction:column; height:__H__px; }
#topbar { flex-shrink:0; display:flex; align-items:center; gap:8px; padding:8px 12px; background:var(--sf); border-bottom:1px solid var(--bd); flex-wrap:wrap; }
#pbanner { display:none; width:100%; align-items:center; gap:8px; padding:4px 0 2px; flex-wrap:wrap; }
#pbanner.show { display:flex; }
#cal { flex:1; overflow:hidden; display:flex; flex-direction:column; min-height:0; }

/* UIパーツ */
.vtab { display:flex; background:var(--sf2); border-radius:7px; padding:3px; gap:2px; }
.vt { padding:4px 13px; border-radius:5px; cursor:pointer; font-size:12px; font-weight:500; color:var(--tx2); border:none; background:transparent; transition:all .15s; font-family:var(--fn); }
.vt.on { background:var(--ac); color:#fff; box-shadow:0 2px 8px rgba(91,138,240,.4); }
.navg { display:flex; align-items:center; gap:5px; }
.nb { width:28px; height:28px; border-radius:5px; border:1px solid var(--bd); background:var(--sf2); color:var(--tx); cursor:pointer; display:flex; align-items:center; justify-content:center; }
#plbl { font-size:14px; font-weight:700; min-width:160px; text-align:center; }
.fsel { padding:4px 7px; border-radius:5px; border:1px solid var(--bd); background:var(--sf2); color:var(--tx); font-size:12px; cursor:pointer; }

/* ── 月ビュー (ガッチャンコ版) ── */
.mv { flex:1; display:flex; flex-direction:column; overflow:hidden; }
.mhdr { display:grid; grid-template-columns:repeat(7,1fr); border-bottom:1px solid var(--bd); flex-shrink:0; }
.mgrid { flex:1; display:grid; grid-template-rows:repeat(6,1fr); overflow-y:auto; }
.mrow { display:grid; grid-template-columns:repeat(7,1fr); border-bottom:1px solid var(--bd); }
.mc { border-right:1px solid var(--bd); padding:4px; cursor:pointer; overflow-y:auto; min-height:100px; position:relative; scrollbar-width:none; }
.mc::-webkit-scrollbar { display:none; }
.mc.other { opacity:.3; } .mc.tod { background:var(--tod); }
.dn { font-size:11px; font-weight:600; width:20px; height:20px; display:flex; align-items:center; justify-content:center; position:sticky; top:0; background:inherit; z-index:5; }

/* 月ビュー専用：スタッフまとめ枠 */
.m-group { background:rgba(255,255,255,0.03); border:1px solid var(--bd); border-radius:4px; margin-bottom:4px; overflow:hidden; }
.m-total { background:var(--ac); color:#000; font-weight:800; font-size:10px; padding:1px 4px; display:flex; justify-content:space-between; }
.m-depts { font-size:9px; padding:1px 4px; color:var(--tx2); line-height:1.2; }

/* ── 週・日ビュー用 ── */
.wv,.dv { flex:1; display:flex; flex-direction:column; overflow:hidden; }
.whdr,.dshdr { display:grid; border-bottom:2px solid var(--bd); background:var(--sf); flex-shrink:0; }
.wbody,.dbody { flex:1; display:flex; overflow-y:auto; position:relative; }
.wtc,.dtc { width:50px; flex-shrink:0; border-right:1px solid var(--bd); background:var(--sf); }
.wts,.dts { height:48px; padding:3px 5px; border-bottom:1px solid var(--bd); font-size:10px; color:var(--tx2); text-align:right; font-family:var(--mn); }
.wdc,.dscs { flex:1; display:flex; }
.wdcol,.dscol { flex:1; border-right:1px solid var(--bd); position:relative; cursor:crosshair; min-width:80px; }
.whs,.dhs { height:48px; border-bottom:1px solid var(--bd); }
.sb { position:absolute; border-radius:4px; padding:2px; font-size:10px; font-weight:600; cursor:pointer; border:1px solid rgba(255,255,255,.1); z-index:1; }
.dragsel { position:absolute; background:var(--drag); border:2px dashed var(--ac); border-radius:4px; pointer-events:none; z-index:10; }

/* モーダル・トースト */
.ov { position:fixed; inset:0; background:rgba(0,0,0,.7); z-index:3000; display:flex; align-items:center; justify-content:center; backdrop-filter:blur(4px); }
.modal { background:var(--sf); border:1px solid var(--bd); border-radius:12px; padding:20px; width:380px; }
.btn { padding:8px 12px; border-radius:6px; border:none; font-weight:600; cursor:pointer; }
.bp { background:var(--ac); color:#fff; } .bs { background:var(--sf2); color:var(--tx); } .bd { background:var(--ng); color:#fff; }
.toast { position:fixed; bottom:16px; right:16px; padding:10px 16px; border-radius:8px; color:#fff; z-index:9999; }
.ldg { position:fixed; inset:0; background:rgba(0,0,0,0.5); display:flex; align-items:center; justify-content:center; color:#fff; z-index:9998; }
</style>
</head>
<body>
<div id="app">
  <div id="topbar">
    <div class="vtab">
      <button class="vt on" data-v="day">日</button>
      <button class="vt" data-v="week">週</button>
      <button class="vt" data-v="month">月</button>
    </div>
    <div class="navg">
      <button class="nb" id="navP">‹</button>
      <div id="plbl"></div>
      <button class="nb" id="navN">›</button>
    </div>
    <button class="nb" id="tdBtn" style="width:auto; padding:0 10px; font-size:12px;">今日</button>
    <div id="pbanner">
      <span style="color:var(--cp); font-weight:700;">📋 ペースト中: </span><span id="pcnt"></span>
      <button class="nb exec" id="pexec" style="background:var(--cp); color:#000; display:none; padding:0 8px;">貼付実行</button>
      <button class="nb" id="pcancel" style="padding:0 8px;">✕</button>
    </div>
    <div style="margin-left:auto; display:flex; gap:5px;">
      <select class="fsel" id="fstaff"><option value="">全スタッフ</option></select>
      <select class="fsel" id="fdept"><option value="">全部門</option></select>
    </div>
  </div>
  <div id="cal"></div>
</div>

<div class="ov" id="regOv" style="display:none" onclick="if(event.target===this)closeReg()">
  <div class="modal">
    <div style="font-weight:700; margin-bottom:15px;">📋 シフト登録</div>
    <div style="margin-bottom:10px;"><label style="font-size:10px; color:var(--tx2);">従業員</label><select id="mStaff" class="fsel" style="width:100%"></select></div>
    <div style="margin-bottom:10px;"><label style="font-size:10px; color:var(--tx2);">部門</label><select id="mDept" class="fsel" style="width:100%"></select></div>
    <div style="margin-bottom:10px;"><label style="font-size:10px; color:var(--tx2);">日付</label><input type="date" id="mDate" class="fsel" style="width:100%"></div>
    <div style="display:flex; gap:5px; margin-bottom:15px;">
      <div style="flex:1;"><label style="font-size:10px; color:var(--tx2);">開始</label><input type="time" id="mS" class="fsel" style="width:100%"></div>
      <div style="flex:1;"><label style="font-size:10px; color:var(--tx2);">終了</label><input type="time" id="mE" class="fsel" style="width:100%"></div>
    </div>
    <div style="display:flex; gap:10px;">
      <button class="btn bs" onclick="closeReg()">閉じる</button>
      <button class="btn bp" style="flex:1;" onclick="saveAll()">保存</button>
    </div>
  </div>
</div>

<div class="ov" id="detOv" style="display:none" onclick="if(event.target===this)closeDet()">
  <div class="modal">
    <div style="font-weight:700; margin-bottom:15px;">📌 シフト詳細</div>
    <div id="detBody" style="margin-bottom:20px;"></div>
    <div style="display:flex; gap:10px;">
      <button class="btn bs" onclick="closeDet()">閉じる</button>
      <button class="btn bp" onclick="startCopy()">コピー</button>
      <button class="btn bd" onclick="delShift()">削除</button>
    </div>
  </div>
</div>

<script>
const GAS = "__GAS__";
const STAFF = __STAFF__;
const DEPTS = __DEPTS__;
let SHIFTS = __SHIFTS__;
const CLRS = __CLRS__;

const $$ = id => document.getElementById(id);
const mk = (t,c) => { const e=document.createElement(t); if(c)e.className=c; return e; };
const fmt = d => d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0');
const p2 = n => String(n).padStart(2,'0');
const pd_ = s => new Date(s);
const sMins = s => { const d=pd_(s.start); return d.getHours()*60+d.getMinutes(); };
const eMins = s => { const d=pd_(s.end); return d.getHours()*60+d.getMinutes()||1440; };
const deptClr = d => { const i=DEPTS.indexOf(d); return CLRS[i >= 0 ? i % CLRS.length : 0]; };
const rgba = (hex, a) => { const r=parseInt(hex.slice(1,3),16),g=parseInt(hex.slice(3,5),16),b=parseInt(hex.slice(5,7),16); return `rgba(${r},${g},${b},${a})`; };

let view = 'day', cur = new Date(); cur.setHours(0,0,0,0);
let clip = null, pasteDates = new Set(), curS = null;

window.onload = () => {
  STAFF.forEach(s => { $$('fstaff').appendChild(new Option(s,s)); $$('mStaff').appendChild(new Option(s,s)); });
  DEPTS.forEach(d => { $$('fdept').appendChild(new Option(d,d)); $$('mDept').appendChild(new Option(d,d)); });
  document.querySelector('.vtab').onclick = e => { if(e.target.dataset.v) setView(e.target.dataset.v); };
  $$('navP').onclick = () => nav(-1); $$('navN').onclick = () => nav(1); $$('tdBtn').onclick = goToday;
  $$('fstaff').onchange = $$('fdept').onchange = () => renderView();
  $$('pcancel').onclick = cancelCopy; $$('pexec').onclick = execPaste;
  $$('cal').onclick = onCalClick;
  renderView();
};

function setView(v) { view=v; document.querySelectorAll('.vt').forEach(e=>e.classList.toggle('on',e.dataset.v===v)); renderView(); }
function nav(d) {
  if(view==='month') cur.setMonth(cur.getMonth()+d);
  else cur.setDate(cur.getDate() + (view==='week' ? d*7 : d));
  renderView();
}
function goToday() { cur=new Date(); cur.setHours(0,0,0,0); renderView(); }

function renderView() {
  if(view==='month') renderMonth(); else if(view==='week') renderWeek(); else renderDay();
  updateBanner();
}

function getFil() {
  const s=$$('fstaff').value, d=$$('fdept').value;
  return SHIFTS.filter(x => (!s || x.staff===s) && (!d || x.dept===d));
}

// ── 月ビュー (スタッフごとに合計時間を表示) ──
function renderMonth() {
  const y=cur.getFullYear(), m=cur.getMonth();
  $$('plbl').textContent = y+'年 '+(m+1)+'月';
  const root=$$('cal'); root.innerHTML='';
  const mv=mk('div','mv'), mh=mk('div','mhdr'), mg=mk('div','mgrid');
  ['日','月','火','水','木','金','土'].forEach(d=>{ const c=mk('div','mhc'); c.textContent=d; mh.appendChild(c); });
  mv.appendChild(mh);

  let d = new Date(y, m, 1); d.setDate(d.getDate()-d.getDay());
  const fil = getFil();

  for(let r=0; r<6; r++) {
    const row=mk('div','mrow');
    for(let i=0; i<7; i++) {
      const ds = fmt(d);
      const mc = mk('div', 'mc '+(d.getMonth()!==m?'other':'')+(ds===fmt(new Date())?' tod':'')+(pasteDates.has(ds)?' psel':''));
      mc.dataset.date = ds; if(!clip) mc.dataset.openreg = ds;
      mc.innerHTML = '<div class="dn">'+d.getDate()+'</div>';
      
      const dayShifts = fil.filter(s => s.start.startsWith(ds));
      const summary = {};
      dayShifts.forEach(s => {
        if(!summary[s.staff]) summary[s.staff] = { depts:[], starts:[], ends:[], raw:[] };
        summary[s.staff].depts.push(s.dept);
        summary[s.staff].starts.push(new Date(s.start));
        summary[s.staff].ends.push(new Date(s.end));
        summary[s.staff].raw.push(s);
      });

      for(const staff in summary) {
        const info = summary[staff];
        const minS = new Date(Math.min(...info.starts)), maxE = new Date(Math.max(...info.ends));
        const tStr = minS.getHours()+':'+p2(minS.getMinutes())+'-'+maxE.getHours()+':'+p2(maxE.getMinutes());
        const box = mk('div','m-group');
        box.onclick = (e) => { e.stopPropagation(); if(clip) togglePasteDate(ds); else showDet(info.raw[0]); };
        box.innerHTML = `<div class="m-total"><span>${staff}</span><span>${tStr}</span></div><div class="m-depts">${info.depts.join(' / ')}</div>`;
        mc.appendChild(box);
      }
      row.appendChild(mc); d.setDate(d.getDate()+1);
    }
    mg.appendChild(row);
  }
  mv.appendChild(mg); root.appendChild(mv);
}

// ── 週・日ビュー用 ──
function renderWeek() {
  const ws = new Date(cur); ws.setDate(ws.getDate()-ws.getDay());
  const we = new Date(ws); we.setDate(we.getDate()+6);
  $$('plbl').textContent = fmt(ws)+' - '+fmt(we);
  const root=$$('cal'); root.innerHTML='';
  const wv=mk('div','wv'), wh=mk('div','whdr'); wh.appendChild(mk('div','wcrn'));
  for(let i=0;i<7;i++){
    const d=new Date(ws); d.setDate(d.getDate()+i); const ds=fmt(d);
    const h=mk('div','whd '+(ds===fmt(new Date())?'tod':'')+(pasteDates.has(ds)?' psel':''));
    h.dataset.date=ds; h.innerHTML=`<div class="wdow">${['日','月','火','水','木','金','土'][d.getDay()]}</div><div class="wdn">${d.getDate()}</div>`;
    wh.appendChild(h);
  }
  wv.appendChild(wh);
  const wb=mk('div','wbody'), tc=mk('div','wtc'), dc=mk('div','wdc');
  for(let h=0;h<24;h++){ const t=mk('div','wts'); t.textContent=h+':00'; tc.appendChild(t); }
  const fil = getFil();
  for(let i=0;i<7;i++){
    const d=new Date(ws); d.setDate(d.getDate()+i); const ds=fmt(d);
    const col=mk('div','wdcol '+(ds===fmt(new Date())?'tod':'')+(pasteDates.has(ds)?' psel':''));
    col.dataset.date=ds; if(!clip) { col.dataset.openreg=ds; setupDrag(col, ds); }
    for(let h=0;h<24;h++) col.appendChild(mk('div','whs'));
    fil.filter(s=>s.start.startsWith(ds)).forEach(s=>col.appendChild(mkBlock(s, true)));
    dc.appendChild(col);
  }
  wb.appendChild(tc); wb.appendChild(dc); wv.appendChild(wb); root.appendChild(wv);
}

function renderDay() {
  const ds=fmt(cur); $$('plbl').textContent = ds;
  const root=$$('cal'); root.innerHTML='';
  const dv=mk('div','dv'), sh=mk('div','dshdr'); sh.appendChild(mk('div','dcrn'));
  const staff = $$('fstaff').value ? [$$('fstaff').value] : STAFF;
  staff.forEach(s=>{ const h=mk('div','dsch'); h.textContent=s; sh.appendChild(h); });
  dv.appendChild(sh);
  const db=mk('div','dbody'), tc=mk('div','dtc'), sc=mk('div','dscs');
  for(let h=0;h<30;h++){ const t=mk('div','dts'); t.textContent=(h<24?h:h-24)+':00'; tc.appendChild(t); }
  const fil = getFil();
  staff.forEach(s=>{
    const col=mk('div','dscol'); if(!clip) { col.dataset.openreg=ds; col.dataset.staff=s; setupDrag(col, ds, s); }
    for(let h=0;h<30;h++) col.appendChild(mk('div','dhs'));
    fil.filter(x=>x.staff===s && x.start.startsWith(ds)).forEach(x=>col.appendChild(mkBlock(x, false)));
    sc.appendChild(col);
  });
  db.appendChild(tc); db.appendChild(sc); dv.appendChild(db); root.appendChild(dv);
}

function mkBlock(s, showStaff) {
  const st=pd_(s.start), et=pd_(s.end);
  const sm=st.getHours()*60+st.getMinutes(), em=et.getHours()*60+et.getMinutes()||1440;
  const top=(sm/60)*48, ht=((em-sm)/60)*48, c=deptClr(s.dept);
  const b=mk('div','sb'); b.dataset.idx=SHIFTS.indexOf(s);
  b.style.cssText=`top:${top}px;height:${ht}px;background:${rgba(c,0.3)};border-left:3px solid ${c};color:${c};width:95%;left:2.5%;`;
  b.innerHTML=`<div style="overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">${showStaff?s.staff:s.dept}</div><div style="font-size:9px;opacity:0.8;">${st.getHours()}:${p2(st.getMinutes())}</div>`;
  b.onclick=(e)=>{e.stopPropagation(); showDet(s);};
  return b;
}

// ── イベント・共通 ──
function onCalClick(e) {
  const ds = e.target.closest('[data-date]')?.dataset.date;
  if(ds && clip) { togglePasteDate(ds); return; }
  const reg = e.target.closest('[data-openreg]');
  if(reg && !clip) openReg(reg.dataset.openreg, '09:00', '18:00', reg.dataset.staff||'');
}

function togglePasteDate(ds) {
  if(pasteDates.has(ds)) pasteDates.delete(ds); else pasteDates.add(ds);
  updateBanner(); renderView();
}

function startCopy() { clip=curS; pasteDates.clear(); closeDet(); updateBanner(); renderView(); }
function cancelCopy() { clip=null; pasteDates.clear(); updateBanner(); renderView(); }
async function execPaste() {
  if(!clip || !pasteDates.size) return;
  const st=pd_(clip.start), et=pd_(clip.end), sT=p2(st.getHours())+':'+p2(st.getMinutes()), eT=p2(et.getHours())+':'+p2(et.getMinutes());
  const dates = [...pasteDates]; cancelCopy(); showLdg('貼付中...');
  for(const ds of dates){
    await fetch(GAS+'?'+new URLSearchParams({action:'add_shift',name:clip.staff,dept:clip.dept,start:ds+' '+sT,end:ds+' '+eT}));
    SHIFTS.push({staff:clip.staff,dept:clip.dept,start:ds+'T'+sT+':00',end:ds+'T'+eT+':00'});
  }
  hideLdg(); renderView();
}

function updateBanner() {
  const b=$$('pbanner'); if(clip){ b.classList.add('show'); $$('pcnt').textContent=clip.staff+' / '+pasteDates.size+'日選択'; $$('pexec').style.display=pasteDates.size?'block':'none'; } else b.classList.remove('show');
}

function openReg(ds,s,e,stf) { $$('mDate').value=ds; $$('mS').value=s; $$('mE').value=e; if(stf)$$('mStaff').value=stf; $$('regOv').style.display='flex'; }
function closeReg() { $$('regOv').style.display='none'; }
async function saveAll() {
  const s=$$('mStaff').value, d=$$('mDept').value, dt=$$('mDate').value, st=$$('mS').value, et=$$('mE').value;
  closeReg(); showLdg('保存中...');
  await fetch(GAS+'?'+new URLSearchParams({action:'add_shift',name:s,dept:d,start:dt+' '+st,end:dt+' '+et}));
  SHIFTS.push({staff:s,dept:d,start:dt+'T'+st+':00',end:dt+'T'+et+':00'});
  hideLdg(); renderView();
}

function showDet(s) {
  curS=s; const st=pd_(s.start), et=pd_(s.end);
  $$('detBody').innerHTML=`<div style="font-size:16px; font-weight:700;">${s.staff}</div><div style="color:var(--tx2);">${s.dept}</div><div style="margin-top:10px;">${fmt(st)}</div><div>${st.getHours()}:${p2(st.getMinutes())} - ${et.getHours()}:${p2(et.getMinutes())}</div>`;
  $$('detOv').style.display='flex';
}
function closeDet() { $$('detOv').style.display='none'; }
async function delShift() {
  if(!confirm('削除しますか？')) return; const s=curS; closeDet(); showLdg('削除中...');
  await fetch(GAS+'?'+new URLSearchParams({action:'del_shift',name:s.staff,dept:s.dept,start:s.start.replace('T',' '),end:s.end.replace('T',' ')}));
  SHIFTS = SHIFTS.filter(x=>x!==s); hideLdg(); renderView();
}

function setupDrag(col, ds, stf) {
  let startM = 0, el = null;
  col.onmousedown = e => {
    if(e.target !== col) return;
    const rect = col.getBoundingClientRect();
    startM = Math.round((e.clientY - rect.top) / 48 * 4) * 15;
    el = mk('div','dragsel'); el.style.top = (startM/60*48)+'px'; col.appendChild(el);
    window.onmousemove = me => {
      const curM = Math.round((me.clientY - rect.top) / 48 * 4) * 15;
      const top = Math.min(startM, curM), h = Math.abs(curM - startM);
      el.style.top = (top/60*48)+'px'; el.style.height = (h/60*48)+'px';
    };
    window.onmouseup = me => {
      const curM = Math.round((me.clientY - rect.top) / 48 * 4) * 15;
      const s = Math.min(startM, curM), e = Math.max(startM, curM);
      el.remove(); window.onmousemove = window.onmouseup = null;
      if(e-s >= 15) openReg(ds, p2(Math.floor(s/60))+':'+p2(s%60), p2(Math.floor(e/60))+':'+p2(e%60), stf||'');
    };
  };
}

function showLdg(m) { const l=mk('div','ldg'); l.id='_ldg'; l.innerHTML='<div style="margin-right:10px;">🌀</div>'+m; document.body.appendChild(l); }
function hideLdg() { document.getElementById('_ldg')?.remove(); }
</script>
</body>
</html>"""

    # --- 3. データの埋め込み (replace方式で波括弧エラーを回避) ---
    final_html = (html_template
        .replace("__H__", str(H))
        .replace("__GAS__", gas_url)
        .replace("__STAFF__", staff_json)
        .replace("__DEPTS__", dept_json)
        .replace("__SHIFTS__", shifts_json_str)
        .replace("__CLRS__", color_palette_json)
    )

    components.html(final_html, height=H, scrolling=False)
