"""
カレンダービューコンポーネント
"""
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
            except Exception:
                pass

    staff_json      = json.dumps(staff_list, ensure_ascii=False)
    dept_json       = json.dumps(dept_list, ensure_ascii=False)
    shifts_json_str = json.dumps(shifts_json, ensure_ascii=False)

    color_palette = [
        "#4f86c6","#e07b5a","#5aad8f","#b07fc7","#e0b84a",
        "#5abfcc","#e07bb0","#7ec45a","#c47e5a","#5a7ec4",
        "#c4b05a","#5ac4a2","#c45a7e","#8fc45a","#c45ab0","#5a8fc4"
    ]

    COMPONENT_HEIGHT = 780

    html_code = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@300;400;500;700&family=JetBrains+Mono:wght@400;600&display=swap');
:root{{
  --bg:#0f1117;--surface:#1a1d27;--surface2:#22263a;--border:#2d3148;
  --text:#e8eaf2;--text-muted:#6b7094;--accent:#5b8af0;--accent2:#8b5cf6;
  --success:#34d399;--danger:#f87171;--warn:#f59e0b;--copy:#f0a05b;
  --today:rgba(91,138,240,.12);--hover:rgba(91,138,240,.08);
  --drag:rgba(91,138,240,.25);--nextday:rgba(139,92,246,.06);
  --paste-hover:rgba(240,160,91,.18);
  --font:'Noto Sans JP',sans-serif;--mono:'JetBrains Mono',monospace;
}}
*{{margin:0;padding:0;box-sizing:border-box;}}
html,body{{width:100%;height:{COMPONENT_HEIGHT}px;overflow:hidden;font-family:var(--font);background:var(--bg);color:var(--text);font-size:13px;user-select:none;}}
#app{{display:flex;flex-direction:column;height:{COMPONENT_HEIGHT}px;}}
#topbar{{flex-shrink:0;display:flex;align-items:center;gap:10px;padding:10px 14px;background:var(--surface);border-bottom:1px solid var(--border);flex-wrap:wrap;height:52px;}}
#cal{{flex:1;overflow:hidden;display:flex;flex-direction:column;min-height:0;}}

.view-tabs{{display:flex;background:var(--surface2);border-radius:8px;padding:3px;gap:2px;}}
.vt{{padding:5px 14px;border-radius:6px;cursor:pointer;font-size:12px;font-weight:500;color:var(--text-muted);border:none;background:transparent;transition:all .15s;font-family:var(--font);}}
.vt.on{{background:var(--accent);color:#fff;box-shadow:0 2px 8px rgba(91,138,240,.4);}}
.vt:hover:not(.on){{background:var(--hover);color:var(--text);}}
.nav-grp{{display:flex;align-items:center;gap:6px;}}
.nb{{width:30px;height:30px;border-radius:6px;border:1px solid var(--border);background:var(--surface2);color:var(--text);cursor:pointer;font-size:15px;display:flex;align-items:center;justify-content:center;transition:all .15s;}}
.nb:hover{{border-color:var(--accent);background:var(--hover);}}
#plabel{{font-size:14px;font-weight:700;min-width:170px;text-align:center;}}
.today-btn{{padding:5px 12px;border-radius:6px;border:1px solid var(--border);background:var(--surface2);color:var(--text);cursor:pointer;font-size:12px;font-family:var(--font);font-weight:500;}}
.today-btn:hover{{border-color:var(--accent);color:var(--accent);}}
.fgrp{{display:flex;gap:8px;margin-left:auto;align-items:center;}}
.fsel{{padding:5px 8px;border-radius:6px;border:1px solid var(--border);background:var(--surface2);color:var(--text);font-size:12px;font-family:var(--font);cursor:pointer;}}

#paste-banner{{display:none;background:rgba(240,160,91,.25);border:1px solid var(--copy);border-radius:8px;padding:6px 16px;font-size:12px;color:var(--copy);font-weight:600;align-items:center;gap:12px;box-shadow:0 4px 12px rgba(0,0,0,0.3);}}
#paste-banner button{{background:var(--surface2);border:1px solid var(--copy);color:var(--copy);border-radius:4px;padding:4px 10px;cursor:pointer;font-size:11px;font-family:var(--font);font-weight:700;}}

.month-view{{flex:1;display:flex;flex-direction:column;overflow:hidden;min-height:0;}}
.mhdr{{display:grid;grid-template-columns:repeat(7,1fr);border-bottom:1px solid var(--border);flex-shrink:0;}}
.mhc{{padding:7px 0;text-align:center;font-size:11px;font-weight:600;color:var(--text-muted);letter-spacing:.08em;}}
.mgrid{{flex:1;display:grid;grid-template-rows:repeat(6,1fr);overflow-y:auto;}}
.mrow{{display:grid;grid-template-columns:repeat(7,1fr);border-bottom:1px solid var(--border);}}
.mcell{{border-right:1px solid var(--border);padding:5px;cursor:pointer;transition:background .12s;overflow:hidden;min-height:80px;position:relative;}}
.mcell:hover{{background:var(--hover);}}
.mcell.paste-target:hover{{background:var(--paste-hover)!important;outline:2px dashed var(--copy);outline-offset:-2px;}}
.dnum{{font-size:12px;font-weight:600;width:22px;height:22px;display:flex;align-items:center;justify-content:center;border-radius:50%;font-family:var(--mono);margin-bottom:3px;}}
.tod .dnum{{background:var(--accent);color:#fff;}}

.mchip{{font-size:10px;padding:2px 5px;border-radius:3px;margin-bottom:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-weight:500;cursor:pointer;position:relative;}}
.mchip.copied{{outline:2px solid var(--copy);}}

.wbody, .dbody {{flex:1;display:flex;overflow-y:auto;min-height:0;position:relative;}}
.whdr, .dshdr {{display:grid;grid-template-columns:52px repeat(7,1fr);border-bottom:2px solid var(--border);background:var(--surface);flex-shrink:0;}}
.whday, .dsch {{padding:7px 4px;text-align:center;border-left:1px solid var(--border);cursor:pointer;font-weight:600;}}
.wdcol, .dscol {{border-right:1px solid var(--border);position:relative;cursor:crosshair;min-height:1152px;}}
.wdcol.paste-col, .dscol.paste-col {{cursor:copy;}}

.sb{{position:absolute;border-radius:4px;padding:3px 5px;font-size:10px;font-weight:600;overflow:hidden;z-index:1;cursor:pointer;transition:filter .12s;border:1px solid rgba(255,255,255,.1);}}
.sb:hover{{filter:brightness(1.25);z-index:4;}}

.ov{{position:fixed;inset:0;background:rgba(0,0,0,.7);z-index:2000;display:flex;align-items:center;justify-content:center;backdrop-filter:blur(4px);}}
.modal{{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:22px;width:400px;max-width:96vw;box-shadow:0 24px 64px rgba(0,0,0,.6);}}
.mtitle{{font-size:15px;font-weight:700;margin-bottom:16px;display:flex;align-items:center;gap:8px;}}
.fg{{margin-bottom:12px;}}
.fl{{display:block;font-size:10px;font-weight:700;color:var(--text-muted);text-transform:uppercase;letter-spacing:.08em;margin-bottom:5px;}}
.fi,.fsel2{{width:100%;padding:8px 10px;border-radius:6px;border:1px solid var(--border);background:var(--surface2);color:var(--text);font-size:13px;font-family:var(--font);}}
.mact{{display:flex;gap:8px;margin-top:16px;flex-wrap:wrap;}}
.btn{{flex:1;padding:9px;border-radius:6px;border:none;font-size:13px;font-family:var(--font);font-weight:600;cursor:pointer;transition:all .15s;min-width:80px;}}
.btn-p{{background:var(--accent);color:#fff;}}
.btn-s{{background:var(--surface2);color:var(--text);border:1px solid var(--border);}}
.btn-c{{background:rgba(240,160,91,.2);color:var(--copy);border:1px solid var(--copy);}}

.toast{{position:fixed;bottom:18px;right:18px;padding:11px 18px;border-radius:8px;font-weight:600;font-size:12px;z-index:9999;color:#fff;}}
.toast.ok{{background:var(--success);}}
.ldg{{position:fixed;inset:0;background:rgba(0,0,0,.55);display:flex;align-items:center;justify-content:center;z-index:9998;gap:10px;color:var(--text);}}
.spin{{width:18px;height:18px;border:2px solid var(--border);border-top-color:var(--accent);border-radius:50%;animation:sp .7s linear infinite;}}
@keyframes sp{{to{{transform:rotate(360deg);}}}}
</style>
</head>
<body>
<div id="app">
  <div id="topbar">
    <div class="view-tabs">
      <button class="vt on"  onclick="setView('day')">日</button>
      <button class="vt"     onclick="setView('week')">週</button>
      <button class="vt"     onclick="setView('month')">月</button>
    </div>
    <div class="nav-grp">
      <button class="nb" onclick="nav(-1)">&#8249;</button>
      <div id="plabel"></div>
      <button class="nb" onclick="nav(1)">&#8250;</button>
    </div>
    <button class="today-btn" onclick="goToday()">今日</button>
    <div id="paste-banner"></div>
    <div class="fgrp">
      <select class="fsel" id="fstaff" onchange="renderView()"><option value="">全スタッフ</option></select>
      <select class="fsel" id="fdept"  onchange="renderView()"><option value="">全部門</option></select>
    </div>
  </div>
  <div id="cal"></div>
</div>

<div class="ov" id="reg-ov" style="display:none" onclick="if(event.target===this)closeReg()">
  <div class="modal">
    <div class="mtitle">📋 シフト登録</div>
    <div class="fg"><label class="fl">従業員</label><select class="fsel2" id="m-staff"></select></div>
    <div class="fg"><label class="fl">部門</label><select class="fsel2" id="m-dept"></select></div>
    <div class="fg"><label class="fl">日付</label><input type="date" class="fi" id="m-date"></div>
    <div class="fg">
      <label class="fl">時間</label>
      <div class="trow" style="display:grid; grid-template-columns:1fr 20px 1fr; align-items:center;">
        <input type="time" class="fi" id="m-start" value="09:00">
        <div style="text-align:center;color:var(--text-muted)">→</div>
        <input type="time" class="fi" id="m-end" value="18:00">
      </div>
    </div>
    <div class="mact">
      <button class="btn btn-s" onclick="closeReg()">閉じる</button>
      <button class="btn btn-p" onclick="saveAll()">保存</button>
    </div>
  </div>
</div>

<div class="ov" id="det-ov" style="display:none" onclick="if(event.target===this)closeDet()">
  <div class="modal">
    <div class="mtitle">📌 シフト詳細</div>
    <div id="det-body"></div>
    <div class="mact" style="margin-top:14px">
      <button class="btn btn-s" onclick="closeDet()">閉じる</button>
      <button class="btn btn-c" onclick="copyShift()">📋 コピー</button>
      <button class="btn btn-d" onclick="delShift()" style="background:var(--danger);color:#fff">削除</button>
    </div>
  </div>
</div>

<script>
const GAS   = "{gas_url}";
const STAFF = {staff_json};
const DEPTS = {dept_json};
let   SHIFTS = {shifts_json_str};
const CLRS = {json.dumps(color_palette)};

function deptColor(d){{
  const i=DEPTS.indexOf(d);
  if(i>=0) return CLRS[i%CLRS.length];
  let h=0; for(const c of d) h=(h*31+c.charCodeAt(0))&0x7fffffff;
  return CLRS[h%CLRS.length];
}}
function rgba(hex,a){{
  return `rgba(${{parseInt(hex.slice(1,3),16)}},${{parseInt(hex.slice(3,5),16)}},${{parseInt(hex.slice(5,7),16)}},${{a}})`;
}}

const DAYS=['日','月','火','水','木','金','土'];
const MONS=['1月','2月','3月','4月','5月','6月','7月','8月','9月','10月','11月','12月'];
const HPX=48, DAY_H=30, MID_H=24;

let view='day';
let cur=new Date(); cur.setHours(0,0,0,0);
let batchQueue=[];
let clipShift=null;

window.onload=()=>{{
  ['fstaff','m-staff'].forEach(id=>STAFF.forEach(s=>$$(id).appendChild(new Option(s,s))));
  ['fdept', 'm-dept' ].forEach(id=>DEPTS.forEach(d=>$$(id).appendChild(new Option(d,d))));
  renderView();
}};

function $$(id){{return document.getElementById(id);}}
function mk(t,c){{const e=document.createElement(t);if(c)e.className=c;return e;}}
function fmt(d){{return`${{d.getFullYear()}}-${{p2(d.getMonth()+1)}}-${{p2(d.getDate())}}`;}}
function p2(n){{return String(n).padStart(2,'0');}}
function today(){{return fmt(new Date());}}
function pd(s){{return new Date(s);}}

function setView(v){{
  view=v;
  document.querySelectorAll('.vt').forEach((e,i)=>e.classList.toggle('on',['day','week','month'][i]===v));
  renderView();
}}
function nav(d){{
  if(view==='day')       cur.setDate(cur.getDate()+d);
  else if(view==='week') cur.setDate(cur.getDate()+d*7);
  else                   cur.setMonth(cur.getMonth()+d);
  renderView();
}}
function goToday(){{cur=new Date();cur.setHours(0,0,0,0);renderView();}}

function renderView(){{
  if(view==='day') renderDay();
  else if(view==='week') renderWeek();
  else renderMonth();
  updatePasteBanner();
}}

function copyShift(){{
  closeDet();
  clipShift={{...curS}};
  updatePasteBanner();
  showToast('📋 コピーモード：日付をクリックして選択してください');
  renderView();
}}

function cancelCopy(){{
  clipShift=null; batchQueue=[]; updatePasteBanner(); renderView();
}}

function updatePasteBanner(){{
  const b=$$('paste-banner');
  if(clipShift){{
    b.style.display='flex';
    const count = batchQueue.length;
    b.innerHTML = `
      <span style="flex:1">📋 ${{clipShift.staff}} / ${{clipShift.dept}} (${{count}}件選択中)</span>
      <div style="display:flex; gap:8px;">
        <button onclick="saveAll()" style="background:var(--success); color:#fff; border:none; padding:4px 12px; border-radius:4px;">
          ${{count > 0 ? '✅ '+count+'件分を保存確定' : '選択を完了'}}
        </button>
        <button onclick="cancelCopy()">中止</button>
      </div>
    `;
  }} else {{
    b.style.display='none';
  }}
}}

function pasteToDate(dateStr){{
  if(!clipShift) return;
  const s=pd(clipShift.start),et=pd(clipShift.end);
  const startT = `${{p2(s.getHours())}}:${{p2(s.getMinutes())}}`;
  const endT = `${{p2(et.getHours())}}:${{p2(et.getMinutes())}}`;
  batchQueue.push({{ staff: clipShift.staff, dept: clipShift.dept, date: dateStr, start: startT, end: endT }});
  updatePasteBanner();
  showToast(`➕ ${{dateStr}} を追加`,'ok',1000);
}}

function renderMonth(){{
  const y=cur.getFullYear(),mo=cur.getMonth();
  $$('plabel').textContent=`${{y}}年 ${{MONS[mo]}}`;
  const td=today(), fil=filtered();
  const first=new Date(y,mo,1),sdow=first.getDay(),dim=new Date(y,mo+1,0).getDate(),prev=new Date(y,mo,0).getDate();
  let cells=[];
  for(let i=sdow-1;i>=0;i--) cells.push({{d:prev-i,m:mo-1,y,o:true}});
  for(let d=1;d<=dim;d++) cells.push({{d,m:mo,y,o:false}});
  while(cells.length<42) cells.push({{d:cells.length-dim-sdow+1,m:mo+1,y,o:true}});

  const root=$$('cal'); root.innerHTML='';
  const mv=mk('div','month-view');
  const mh=mk('div','mhdr');
  DAYS.forEach(d=>{{const c=mk('div','mhc');c.textContent=d;mh.appendChild(c);}});
  mv.appendChild(mh);
  const mg=mk('div','mgrid');
  for(let r=0;r<6;r++){{
    const row=mk('div','mrow');
    cells.slice(r*7,r*7+7).forEach(cell=>{{
      const cd=new Date(cell.y,cell.m,cell.d),ds=fmt(cd);
      const mc=mk('div',`mcell${{cell.o?' other':''}}${{ds===td?' tod':''}}${{clipShift?' paste-target':''}}`);
      const dn=mk('div','dnum'); dn.textContent=cell.d; mc.appendChild(dn);
      
      mc.onclick=(e)=>{{
        e.stopPropagation();
        if(clipShift) pasteToDate(ds);
        else if(!e.target.classList.contains('mchip')) openReg(ds);
      }};

      shOn(ds,fil).forEach(s=>{{
          const col=deptColor(s.dept);
          const ch=mk('div','mchip');
          ch.style.cssText=`background:${{rgba(col,.25)}};color:${{col}};border-left:3px solid ${{col}}`;
          const st=pd(s.start),et=pd(s.end);
          ch.textContent=`${{s.staff}} ${{p2(st.getHours())}}:${{p2(st.getMinutes())}}-${{p2(et.getHours())}}:${{p2(et.getMinutes())}}`;
          ch.onclick=e=>{{e.stopPropagation(); if(clipShift) pasteToDate(ds); else showDet(s); }};
          mc.appendChild(ch);
      }});
      row.appendChild(mc);
    }});
    mg.appendChild(row);
  }}
  mv.appendChild(mg); root.appendChild(mv);
}}

function renderWeek(){{
  const ws=new Date(cur); ws.setDate(ws.getDate()-ws.getDay());
  $$('plabel').textContent=`${{ws.getMonth()+1}}月 ${{ws.getDate()}}日の週`;
  const td=today(),fil=filtered();
  const root=$$('cal'); root.innerHTML='';
  const wv=mk('div','week-view');
  const wb=mk('div','wbody');
  const dc=mk('div','wdaycols');
  dc.style.display='grid'; dc.style.gridTemplateColumns='repeat(7,1fr)'; dc.style.flex='1';

  for(let i=0;i<7;i++){{
    const d=new Date(ws); d.setDate(d.getDate()+i);
    const ds=fmt(d);
    const col=mk('div',`wdcol${{ds===td?' tod':''}}${{clipShift?' paste-col':''}}`);
    col.innerHTML=`<div style="text-align:center;padding:5px;border-bottom:1px solid var(--border);font-weight:700;">${{d.getDate()}}(${{DAYS[i]}})</div>`;
    for(let h=0;h<24;h++) col.appendChild(mk('div','whs'));
    col.onclick=()=>{{ if(clipShift) pasteToDate(ds); else openReg(ds); }};
    shOn(ds,fil).forEach(s=>{{
       const st=pd(s.start), et=pd(s.end);
       const sm=st.getHours()*60+st.getMinutes(), em=et.getHours()*60+et.getMinutes();
       const top=sm/60*HPX+30, ht=Math.max((em-sm)/60*HPX,20);
       const colr=deptColor(s.dept);
       const b=mk('div','sb');
       b.style.cssText=`top:${{top}}px;height:${{ht}}px;background:${{rgba(colr,.3)}};border-left:3px solid ${{colr}};color:${{colr}};width:95%;left:2.5%;`;
       b.innerHTML=`<div class="sbname">${{s.staff}}</div>`;
       b.onclick=e=>{{ e.stopPropagation(); if(clipShift) pasteToDate(ds); else showDet(s); }};
       col.appendChild(b);
    }});
    dc.appendChild(col);
  }}
  wb.appendChild(dc); wv.appendChild(wb); root.appendChild(wv);
}}

function renderDay(){{
  const ds=fmt(cur),fil=filtered();
  $$('plabel').textContent=ds;
  const root=$$('cal'); root.innerHTML='';
  const dv=mk('div','day-view');
  const db=mk('div','dbody');
  const sc=mk('div','dscols');
  sc.style.display='flex'; sc.style.flex='1';
  const staff=STAFF.length?STAFF:['スタッフ未登録'];
  staff.forEach(s=>{{
    const col=mk('div',`dscol${{clipShift?' paste-col':''}}`);
    col.style.flex='1';
    col.innerHTML=`<div style="text-align:center;padding:5px;border-bottom:1px solid var(--border);font-weight:700;">${{s}}</div>`;
    for(let h=0;h<24;h++) col.appendChild(mk('div','dhs'));
    col.onclick=()=>{{ if(clipShift) pasteToDate(ds); else openReg(ds, '09:00', '18:00', s); }};
    fil.filter(x=>x.staff===s && fmt(pd(x.start))===ds).forEach(x=>{{
       const st=pd(x.start), et=pd(x.end);
       const sm=st.getHours()*60+st.getMinutes(), em=et.getHours()*60+et.getMinutes();
       const top=sm/60*HPX+30, ht=Math.max((em-sm)/60*HPX,20);
       const colr=deptColor(x.dept);
       const b=mk('div','sb');
       b.style.cssText=`top:${{top}}px;height:${{ht}}px;background:${{rgba(colr,.3)}};border-left:3px solid ${{colr}};color:${{colr}};width:95%;left:2.5%;`;
       b.innerHTML=`<div class="sbname">${{x.dept}}</div>`;
       b.onclick=e=>{{ e.stopPropagation(); if(clipShift) pasteToDate(ds); else showDet(x); }};
       col.appendChild(b);
    }});
    sc.appendChild(col);
  }});
  db.appendChild(sc); dv.appendChild(db); root.appendChild(dv);
}}

function openReg(dateStr,startT,endT,staffName){{
  $$('m-date').value=dateStr||today();
  $$('m-start').value=startT||'09:00';
  $$('m-end').value=endT||'18:00';
  if(staffName) $$('m-staff').value=staffName;
  $$('reg-ov').style.display='flex';
}}
function closeReg(){{ $$('reg-ov').style.display='none'; }}

async function saveAll(){{
  let items = batchQueue.length > 0 ? [...batchQueue] : [{{
    staff:$$('m-staff').value, dept:$$('m-dept').value, date:$$('m-date').value, start:$$('m-start').value, end:$$('m-end').value
  }}];
  if(!items[0].staff || items[0].start >= items[0].end) return;
  closeReg(); showLdg(`${{items.length}}件 保存中...`);
  let ok=0;
  for(const item of items){{
    try{{
      await fetch(GAS+'?'+new URLSearchParams({{action:'add_shift',name:item.staff,dept:item.dept,start:`${{item.date}} ${{item.start}}`,end:`${{item.date}} ${{item.end}}`}}));
      SHIFTS.push({{rowIndex:-1,staff:item.staff,dept:item.dept,start:`${{item.date}}T${{item.start}}:00`,end:`${{item.date}}T${{item.end}}:00`}});
      ok++;
    }}catch{{}}
  }}
  clipShift = null; batchQueue = []; hideLdg(); showToast(`✅ ${{ok}}件 保存完了`); renderView();
}}

let curS=null;
function showDet(s){{
  curS=s; const st=pd(s.start),et=pd(s.end),col=deptColor(s.dept);
  $$('det-body').innerHTML=`<div style="font-weight:700;color:${{col}}">${{s.staff}} (${{s.dept}})</div><div>📅 ${{fmt(st)}}</div><div>🕐 ${{p2(st.getHours())}}:${{p2(st.getMinutes())}} - ${{p2(et.getHours())}}:${{p2(et.getMinutes())}}</div>`;
  $$('det-ov').style.display='flex';
}}
function closeDet(){{ $$('det-ov').style.display='none'; }}

async function delShift(){{
  if(!curS || !confirm('削除しますか？')) return;
  const s=curS; closeDet(); showLdg('削除中...');
  try{{
    const norm=iso=>iso.replace('T',' ').split('.')[0].substring(0,16);
    await fetch(GAS+'?'+new URLSearchParams({{action:'del_shift',name:s.staff,dept:s.dept,start:norm(s.start)}}));
    SHIFTS = SHIFTS.filter(x=>!(x.staff===s.staff && x.start===s.start));
  }}catch(e){{}}
  hideLdg(); renderView();
}}

function showToast(msg,type='ok',dur=2000){{
  const t=mk('div',`toast ${{type}}`); t.textContent=msg;
  document.body.appendChild(t); setTimeout(()=>t.remove(),dur);
}}
function showLdg(msg){{
  const l=mk('div','ldg'); l.id='ldg';
  l.innerHTML=`<div class="spin"></div><span>${{msg}}</span>`;
  document.body.appendChild(l);
}}
function hideLdg(){{ $$('ldg')?.remove(); }}
</script>
</body>
</html>"""

    components.html(html_code, height=COMPONENT_HEIGHT, scrolling=False)
