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
                    "staff": str(row.get("従業員", "")),
                    "dept": str(row.get("部門", "")),
                    "start": row["開始"].isoformat() if pd.notna(row["開始"]) else "",
                    "end": row["終了"].isoformat() if pd.notna(row["終了"]) else "",
                })
            except: pass

    shifts_json_str = json.dumps(shifts_json, ensure_ascii=False)
    staff_json = json.dumps(staff_list, ensure_ascii=False)
    dept_json = json.dumps(dept_list, ensure_ascii=False)
    
    H = 800

    # テンプレート方式で波括弧バグを回避
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
  --sel:rgba(240,160,91,.28);
  --fn:'Noto Sans JP',sans-serif;--mn:'JetBrains Mono',monospace;
}
* { margin:0; padding:0; box-sizing:border-box; }
body { width:100%; height:__H__px; overflow:hidden; background:var(--bg); color:var(--tx); font-family:var(--fn); font-size:13px; user-select:none; }
#app { display:flex; flex-direction:column; height:__H__px; }
#topbar { flex-shrink:0; display:flex; align-items:center; gap:8px; padding:8px 12px; background:var(--sf); border-bottom:1px solid var(--bd); flex-wrap:wrap; }
#cal { flex:1; overflow:hidden; display:flex; flex-direction:column; min-height:0; }

/* タブ・ボタン */
.vtab { display:flex; background:var(--sf2); border-radius:7px; padding:3px; gap:2px; }
.vt { padding:4px 13px; border-radius:5px; cursor:pointer; font-size:12px; font-weight:500; color:var(--tx2); border:none; background:transparent; transition:all .15s; }
.vt.on { background:var(--ac); color:#fff; }
#plbl { font-size:14px; font-weight:700; min-width:160px; text-align:center; }
.fsel { padding:4px 7px; border-radius:5px; border:1px solid var(--bd); background:var(--sf2); color:var(--tx); font-size:12px; }

/* ── 月表示（変更箇所） ── */
.mv { flex:1; display:flex; flex-direction:column; overflow:hidden; }
.mhdr { display:grid; grid-template-columns:repeat(7,1fr); border-bottom:1px solid var(--bd); }
.mhc { padding:6px 0; text-align:center; font-size:11px; color:var(--tx2); }
.mgrid { flex:1; display:grid; grid-template-rows:repeat(6,1fr); overflow-y:auto; }
.mrow { display:grid; grid-template-columns:repeat(7,1fr); border-bottom:1px solid var(--bd); min-height:110px; }
.mc { border-right:1px solid var(--bd); padding:4px; cursor:pointer; overflow-y:auto; position:relative; scrollbar-width:none; }
.mc::-webkit-scrollbar { display:none; }
.mc.other { opacity:.3; } .mc.tod { background:var(--tod); }
.dn { font-size:11px; font-weight:600; width:20px; height:20px; display:flex; align-items:center; justify-content:center; position:sticky; top:0; background:inherit; z-index:5; }
.m-group { background:rgba(255,255,255,0.03); border:1px solid var(--bd); border-radius:4px; margin-bottom:4px; overflow:hidden; }
.m-total { background:var(--ac); color:#000; font-weight:800; font-size:10px; padding:1px 4px; display:flex; justify-content:space-between; }
.m-depts { font-size:9px; padding:1px 4px; color:var(--tx2); }

/* ── 週・日表示（以前の構造を維持） ── */
.wv { flex:1; display:flex; flex-direction:column; overflow:hidden; }
.whdr { display:grid; grid-template-columns:50px repeat(7,1fr); border-bottom:2px solid var(--bd); background:var(--sf); }
.wbody { flex:1; display:flex; overflow-y:auto; }
.wdc { flex:1; display:grid; grid-template-columns:repeat(7,1fr); }
.dv { flex:1; display:flex; flex-direction:column; overflow:hidden; }
.dshdr { display:flex; border-bottom:2px solid var(--bd); background:var(--sf); }
.dbody { flex:1; display:flex; overflow-y:auto; }
.dscs { flex:1; display:flex; overflow-x:auto; }
.wtc, .dtc { width:50px; flex-shrink:0; border-right:1px solid var(--bd); background:var(--sf); }
.wts, .dts { height:48px; border-bottom:1px solid var(--bd); font-size:10px; color:var(--tx2); text-align:right; padding:2px 5px; font-family:var(--mn); }
.wdcol, .dscol { flex:1; border-right:1px solid var(--bd); position:relative; min-width:90px; }
.whs, .dhs { height:48px; border-bottom:1px solid var(--bd); }
.sb { position:absolute; border-radius:4px; padding:2px; font-size:10px; font-weight:600; border:1px solid rgba(255,255,255,0.1); width:94%; left:3%; }
</style>
</head>
<body>
<div id="app">
  <div id="topbar">
    <div class="vtab"><button class="vt on" data-v="day">日</button><button class="vt" data-v="week">週</button><button class="vt" data-v="month">月</button></div>
    <div class="navg"><button class="nb" id="navP">‹</button><div id="plbl"></div><button class="nb" id="navN">›</button></div>
    <div style="margin-left:auto; display:flex; gap:5px;"><select class="fsel" id="fstaff"><option value="">全スタッフ</option></select></div>
  </div>
  <div id="cal"></div>
</div>

<script>
const SHIFTS = __SHIFTS__;
const STAFF = __STAFF__;
const CLRS = ["#4f86c6","#e07b5a","#5aad8f","#b07fc7","#e0b84a","#5abfcc","#e07bb0","#7ec45a"];

const $$ = id => document.getElementById(id);
const mk = (t,c) => { const e=document.createElement(t); if(c)e.className=c; return e; };
const fmt = d => d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0');

let view = 'day', cur = new Date(); cur.setHours(0,0,0,0);

window.onload = () => {
  STAFF.forEach(s => $$('fstaff').appendChild(new Option(s,s)));
  document.querySelector('.vtab').onclick = e => { if(e.target.dataset.v) setView(e.target.dataset.v); };
  $$('navP').onclick = () => nav(-1); $$('navN').onclick = () => nav(1);
  renderView();
};

function setView(v) { view=v; document.querySelectorAll('.vt').forEach(e=>e.classList.toggle('on',e.dataset.v===v)); renderView(); }
function nav(d) { if(view==='month') cur.setMonth(cur.getMonth()+d); else cur.setDate(cur.getDate()+(view==='week'?d*7:d)); renderView(); }

function renderView() { if(view==='month') renderMonth(); else if(view==='week') renderWeek(); else renderDay(); }

/* ── 月表示（ここだけロジック変更） ── */
function renderMonth() {
  const y=cur.getFullYear(), m=cur.getMonth();
  $$('plbl').textContent = y+'年 '+(m+1)+'月';
  const root=$$('cal'); root.innerHTML='';
  const mv=mk('div','mv'), mh=mk('div','mhdr'), mg=mk('div','mgrid');
  ['日','月','火','水','木','金','土'].forEach(d=>{ const c=mk('div','mhc'); c.textContent=d; mh.appendChild(c); });
  mv.appendChild(mh);

  let d = new Date(y, m, 1); d.setDate(d.getDate()-d.getDay());
  for(let r=0; r<6; r++) {
    const row=mk('div','mrow');
    for(let i=0; i<7; i++) {
      const ds = fmt(d);
      const mc = mk('div', 'mc '+(d.getMonth()!==m?'other':'')+(ds===fmt(new Date())?' tod':''));
      mc.innerHTML = '<div class="dn">'+d.getDate()+'</div>';
      
      const dayShifts = SHIFTS.filter(s => s.start.startsWith(ds));
      const summary = {};
      dayShifts.forEach(s => {
        if(!summary[s.staff]) summary[s.staff] = { depts:[], starts:[], ends:[] };
        summary[s.staff].depts.push(s.dept);
        summary[s.staff].starts.push(new Date(s.start));
        summary[s.staff].ends.push(new Date(s.end));
      });

      for(const staff in summary) {
        const info = summary[staff];
        const minS = new Date(Math.min(...info.starts)), maxE = new Date(Math.max(...info.ends));
        const tStr = minS.getHours()+':'+String(minS.getMinutes()).padStart(2,'0')+'-'+maxE.getHours()+':'+String(maxE.getMinutes()).padStart(2,'0');
        const box = mk('div','m-group');
        box.innerHTML = `<div class="m-total"><span>${staff}</span><span>${tStr}</span></div><div class="m-depts">${info.depts.join(' / ')}</div>`;
        mc.appendChild(box);
      }
      row.appendChild(mc); d.setDate(d.getDate()+1);
    }
    mg.appendChild(row);
  }
  mv.appendChild(mg); root.appendChild(mv);
}

function renderWeek() {
  const ws = new Date(cur); ws.setDate(ws.getDate()-ws.getDay());
  const root=$$('cal'); root.innerHTML='';
  const wv=mk('div','wv'), wh=mk('div','whdr'); wh.appendChild(mk('div','wcrn'));
  for(let i=0;i<7;i++){
    const d=new Date(ws); d.setDate(d.getDate()+i);
    const h=mk('div','whd'); h.innerHTML=`<div class="wdow">${['日','月','火','水','木','金','土'][d.getDay()]}</div><div class="wdn">${d.getDate()}</div>`;
    wh.appendChild(h);
  }
  wv.appendChild(wh);
  const wb=mk('div','wbody'), tc=mk('div','wtc'), dc=mk('div','wdc');
  for(let h=0;h<24;h++){ const t=mk('div','wts'); t.textContent=h+':00'; tc.appendChild(t); }
  for(let i=0;i<7;i++){
    const ds=fmt(new Date(ws.getFullYear(), ws.getMonth(), ws.getDate()+i));
    const col=mk('div','wdcol'); for(let h=0;h<24;h++) col.appendChild(mk('div','whs'));
    SHIFTS.filter(s=>s.start.startsWith(ds)).forEach(s=>col.appendChild(mkBlock(s, true)));
    dc.appendChild(col);
  }
  wb.appendChild(tc); wb.appendChild(dc); wv.appendChild(wb); root.appendChild(wv);
}

function renderDay() {
  const ds=fmt(cur); $$('plbl').textContent = ds;
  const root=$$('cal'); root.innerHTML='';
  const dv=mk('div','dv'), sh=mk('div','dshdr'); sh.appendChild(mk('div','dcrn'));
  STAFF.forEach(s=>{ const h=mk('div','dsch'); h.textContent=s; sh.appendChild(h); });
  dv.appendChild(sh);
  const db=mk('div','dbody'), tc=mk('div','dtc'), sc=mk('div','dscs');
  for(let h=0;h<30;h++){ const t=mk('div','dts'); t.textContent=(h<24?h:h-24)+':00'; tc.appendChild(t); }
  STAFF.forEach(s=>{
    const col=mk('div','dscol'); for(let h=0;h<30;h++) col.appendChild(mk('div','dhs'));
    SHIFTS.filter(x=>x.staff===s && x.start.startsWith(ds)).forEach(x=>col.appendChild(mkBlock(x, false)));
    sc.appendChild(col);
  });
  db.appendChild(tc); db.appendChild(sc); dv.appendChild(db); root.appendChild(dv);
}

function mkBlock(s, showStaff) {
  const st=new Date(s.start), et=new Date(s.end);
  const top=(st.getHours()*60+st.getMinutes())/60*48, ht=(et-st)/3600000*48;
  const b=mk('div','sb'); b.style.cssText=`top:${top}px;height:${ht}px;background:rgba(91,138,240,0.2);color:#5b8af0;border-left:3px solid #5b8af0;`;
  b.innerHTML=`<div>${showStaff?s.staff:s.dept}</div>`;
  return b;
}
</script>
</body>
</html>"""

    final_html = html_template.replace("__H__", str(H)).replace("__SHIFTS__", shifts_json_str).replace("__STAFF__", staff_json)
    components.html(final_html, height=H)
