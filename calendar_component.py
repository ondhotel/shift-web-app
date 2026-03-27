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
            except Exception:
                pass

    staff_json       = json.dumps(staff_list,  ensure_ascii=False)
    dept_json        = json.dumps(dept_list,   ensure_ascii=False)
    shifts_json_str  = json.dumps(shifts_json, ensure_ascii=False)

    color_palette = [
        "#4f86c6","#e07b5a","#5aad8f","#b07fc7","#e0b84a",
        "#5abfcc","#e07bb0","#7ec45a","#c47e5a","#5a7ec4",
        "#c4b05a","#5ac4a2","#c45a7e","#8fc45a","#c45ab0","#5a8fc4"
    ]

    H = 800

    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@300;400;500;700&family=JetBrains+Mono:wght@400;600&display=swap');
:root {{
  --bg:#0f1117;--sf:#1a1d27;--sf2:#22263a;--bd:#2d3148;
  --tx:#e8eaf2;--tx2:#6b7094;--ac:#5b8af0;--ac2:#8b5cf6;
  --ok:#34d399;--ng:#f87171;--wn:#f59e0b;--cp:#f0a05b;
  --tod:rgba(91,138,240,.12);--hv:rgba(91,138,240,.08);
  --drag:rgba(91,138,240,.25);--nday:rgba(139,92,246,.06);
  --sel:rgba(240,160,91,.28);
  --fn:'Noto Sans JP',sans-serif;--mn:'JetBrains Mono',monospace;
}}
* {{margin:0;padding:0;box-sizing:border-box;}}
html,body {{width:100%;height:{H}px;overflow:hidden;background:var(--bg);color:var(--tx);font-family:var(--fn);font-size:13px;user-select:none;}}

#app {{display:flex;flex-direction:column;height:{H}px;}}
#topbar {{flex-shrink:0;display:flex;align-items:center;gap:8px;padding:8px 12px;background:var(--sf);border-bottom:1px solid var(--bd);flex-wrap:wrap;}}
#pbanner {{display:none;width:100%;align-items:center;gap:8px;padding:4px 0 2px;flex-wrap:wrap;}}
#pbanner.show {{display:flex;}}
.pbl {{font-size:11px;color:var(--cp);font-weight:700;}}
.pbcnt {{font-size:11px;color:var(--tx2);}}
.pbb {{padding:3px 10px;border-radius:5px;border:1px solid var(--cp);background:rgba(240,160,91,.15);color:var(--cp);cursor:pointer;font-size:11px;font-family:var(--fn);font-weight:600;transition:all .15s;}}
.pbb:hover {{background:var(--cp);color:#000;}}
.pbb.exec {{background:var(--cp);color:#000;}}
.pbb.cancel {{border-color:var(--tx2);color:var(--tx2);background:transparent;}}
.pbb.cancel:hover {{background:var(--tx2);color:#000;}}
#cal {{flex:1;overflow:hidden;display:flex;flex-direction:column;min-height:0;}}

.vtab {{display:flex;background:var(--sf2);border-radius:7px;padding:3px;gap:2px;}}
.vt {{padding:4px 13px;border-radius:5px;cursor:pointer;font-size:12px;font-weight:500;color:var(--tx2);border:none;background:transparent;transition:all .15s;font-family:var(--fn);}}
.vt.on {{background:var(--ac);color:#fff;box-shadow:0 2px 8px rgba(91,138,240,.4);}}
.vt:hover:not(.on) {{background:var(--hv);color:var(--tx);}}
.navg {{display:flex;align-items:center;gap:5px;}}
.nb {{width:28px;height:28px;border-radius:5px;border:1px solid var(--bd);background:var(--sf2);color:var(--tx);cursor:pointer;font-size:14px;display:flex;align-items:center;justify-content:center;transition:all .15s;}}
.nb:hover {{border-color:var(--ac);background:var(--hv);}}
#plbl {{font-size:14px;font-weight:700;min-width:160px;text-align:center;}}
.tdbtn {{padding:4px 11px;border-radius:5px;border:1px solid var(--bd);background:var(--sf2);color:var(--tx);cursor:pointer;font-size:12px;font-family:var(--fn);font-weight:500;transition:all .15s;}}
.tdbtn:hover {{border-color:var(--ac);color:var(--ac);}}
.fgrp {{display:flex;gap:6px;margin-left:auto;align-items:center;}}
.fsel {{padding:4px 7px;border-radius:5px;border:1px solid var(--bd);background:var(--sf2);color:var(--tx);font-size:12px;font-family:var(--fn);cursor:pointer;}}

/* ── 月ビュー ── */
.mv {{flex:1;display:flex;flex-direction:column;overflow:hidden;min-height:0;}}
.mhdr {{display:grid;grid-template-columns:repeat(7,1fr);border-bottom:1px solid var(--bd);flex-shrink:0;}}
.mhc {{padding:6px 0;text-align:center;font-size:11px;font-weight:600;color:var(--tx2);}}
.mhc:first-child {{color:#f87171;}}
.mhc:last-child {{color:#60a5fa;}}
.mgrid {{flex:1;display:grid;grid-template-rows:repeat(6,1fr);overflow:hidden;}}
.mrow {{display:grid;grid-template-columns:repeat(7,1fr);border-bottom:1px solid var(--bd);}}
.mc {{border-right:1px solid var(--bd);padding:4px;cursor:pointer;overflow-y:auto;min-height:0;transition:background .1s;position:relative;scrollbar-width:none;}}
.mc::-webkit-scrollbar {{display:none;}}
.mc:hover {{background:var(--hv);}}
.mc.other {{opacity:.3;}}
.mc.tod {{background:var(--tod);}}
.mc.sun .dn {{color:#f87171;}}
.mc.sat .dn {{color:#60a5fa;}}
.mc.psel {{background:var(--sel)!important;outline:2px solid var(--cp);outline-offset:-2px;}}
.mc.pmode {{cursor:copy;}}
.dn {{font-size:11px;font-weight:600;width:20px;height:20px;display:flex;align-items:center;justify-content:center;border-radius:50%;font-family:var(--mn);margin-bottom:4px;position:sticky;top:0;background:inherit;z-index:2;}}
.tod .dn {{background:var(--ac);color:#fff;}}
.chip {{font-size:10px;padding:2px 4px;border-radius:3px;margin-bottom:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-weight:500;cursor:pointer;border-left:3px solid transparent;}}
.chip.copied {{outline:2px solid var(--cp);}}

/* ── 他ビュー & モーダル ── */
.wv, .dv {{flex:1;display:flex;flex-direction:column;overflow:hidden;min-height:0;}}
.whdr, .dshdr {{display:grid;background:var(--sf);border-bottom:2px solid var(--bd);flex-shrink:0;}}
.wbody, .dbody {{flex:1;display:flex;overflow-y:auto;min-height:0;position:relative;}}
.wtc, .dtc {{width:50px;flex-shrink:0;border-right:1px solid var(--bd);background:var(--sf);}}
.wts, .dts {{height:48px;padding:3px 5px 0;border-bottom:1px solid var(--bd);font-size:10px;color:var(--tx2);font-family:var(--mn);text-align:right;}}
.wdc, .dscs {{flex:1;display:flex;}}
.wdcol, .dscol {{flex:1;border-right:1px solid var(--bd);position:relative;}}
.whs, .dhs {{height:48px;border-bottom:1px solid var(--bd);}}

.sb {{position:absolute;border-radius:4px;padding:2px 4px;font-size:10px;font-weight:600;overflow:hidden;z-index:1;cursor:pointer;border:1px solid rgba(255,255,255,.1);}}
.ov {{position:fixed;inset:0;background:rgba(0,0,0,.72);z-index:3000;display:flex;align-items:center;justify-content:center;backdrop-filter:blur(4px);}}
.modal {{background:var(--sf);border:1px solid var(--bd);border-radius:12px;padding:20px;width:390px;max-width:95vw;}}
.btn {{padding:8px;border-radius:6px;font-weight:600;cursor:pointer;border:none;}}
.bp {{background:var(--ac);color:#fff;}}
.bs {{background:var(--sf2);color:var(--tx);border:1px solid var(--bd);}}
.toast {{position:fixed;bottom:16px;right:16px;padding:10px 16px;border-radius:8px;color:#fff;z-index:9999;}}
.toast.ok {{background:var(--ok);}}
.ldg {{position:fixed;inset:0;background:rgba(0,0,0,.55);display:flex;align-items:center;justify-content:center;color:#fff;z-index:9998;gap:10px;}}
.spin {{width:17px;height:17px;border:2px solid #fff;border-top-color:var(--ac);border-radius:50%;animation:sp .7s linear infinite;}}
@keyframes sp {{to {{transform:rotate(360deg);}} }}
</style>
</head>
<body>
<div id="app">
  <div id="topbar">
    <div class="vtab">
      <button class="vt on" data-v="day">日</button>
      <button class="vt"    data-v="week">週</button>
      <button class="vt"    data-v="month">月</button>
    </div>
    <div class="navg">
      <button class="nb" id="navP">&#8249;</button>
      <div id="plbl"></div>
      <button class="nb" id="navN">&#8250;</button>
    </div>
    <button class="tdbtn" id="tdBtn">今日</button>
    <div id="pbanner">
      <span class="pbl">📋 ペーストモード</span>
      <span class="pbcnt" id="pcnt"></span>
      <button class="pbb exec" id="pexec" style="display:none">貼り付け</button>
      <button class="pbb cancel" id="pcancel">✕ キャンセル</button>
    </div>
    <div class="fgrp">
      <select class="fsel" id="fstaff"><option value="">全スタッフ</option></select>
    </div>
  </div>
  <div id="cal"></div>
</div>

<div class="ov" id="detOv" style="display:none">
  <div class="modal">
    <div id="detBody"></div>
    <div style="margin-top:12px;display:flex;gap:8px;">
      <button class="btn bs" onclick="closeDet()">閉じる</button>
      <button class="btn bp" onclick="startCopy()">コピー</button>
      <button class="btn bs" style="background:var(--ng);color:#fff" onclick="delShift()">削除</button>
    </div>
  </div>
</div>

<script>
const GAS    = "{gas_url}";
const STAFF  = {staff_json};
const DEPTS  = {dept_json};
let   SHIFTS = {shifts_json_str};
const CLRS   = {color_palette};

function deptClr(d) {{
  const i = DEPTS.indexOf(d);
  if (i >= 0) return CLRS[i % CLRS.length];
  return CLRS[0];
}}
function rgba(hex, a) {{
  const r = parseInt(hex.slice(1,3),16), g = parseInt(hex.slice(3,5),16), b = parseInt(hex.slice(5,7),16);
  return `rgba(${{r}},${{g}},${{b}},${{a}})`;
}}

const DAYS = ['日','月','火','水','木','金','土'];
let view = 'day', cur = new Date(); cur.setHours(0,0,0,0);
let clip = null, pasteDates = new Set(), curS = null;

const $$ = id => document.getElementById(id);
const mk = (t,c) => {{ const e=document.createElement(t); if(c)e.className=c; return e; }};
const fmt = d => `${{d.getFullYear()}}-${{String(d.getMonth()+1).padStart(2,'0')}}-${{String(d.getDate()).padStart(2,'0')}}`;

window.addEventListener('load', () => {{
  STAFF.forEach(s => $$('fstaff').appendChild(new Option(s,s)));
  document.querySelector('.vtab').addEventListener('click', e => {{ if(e.target.dataset.v) setView(e.target.dataset.v); }});
  $$('navP').onclick = () => nav(-1);
  $$('navN').onclick = () => nav(1);
  $$('tdBtn').onclick = goToday;
  $$('cal').addEventListener('click', onCalClick);
  renderView();
}});

function setView(v) {{ view=v; document.querySelectorAll('.vt').forEach(e=>e.classList.toggle('on',e.dataset.v===v)); renderView(); }}
function nav(d) {{
  if(view==='month') cur.setMonth(cur.getMonth()+d);
  else cur.setDate(cur.getDate() + (view==='week' ? d*7 : d));
  renderView();
}}
function goToday() {{ cur=new Date(); cur.setHours(0,0,0,0); renderView(); }}

function renderView() {{
  if(view==='month') renderMonth();
  else $$('cal').innerHTML = '<div style="padding:20px;color:#fff">日・週ビューは簡易版です。月ビューをメインに表示しています。</div>';
  $$('plbl').textContent = `${{cur.getFullYear()}}年 ${{cur.getMonth()+1}}月`;
}}

function renderMonth() {{
  const y=cur.getFullYear(), mo=cur.getMonth();
  const first=new Date(y,mo,1), sdow=first.getDay(), dim=new Date(y,mo+1,0).getDate();
  const root=$$('cal'); root.innerHTML='';
  const mv=mk('div','mv'), mh=mk('div','mhdr'), mg=mk('div','mgrid');
  
  DAYS.forEach(d=>{{ const c=mk('div','mhc'); c.textContent=d; mh.appendChild(c); }});
  mv.appendChild(mh);

  let dCnt = 1 - sdow;
  for(let r=0; r<6; r++) {{
    const row=mk('div','mrow');
    for(let i=0; i<7; i++) {{
      const cd=new Date(y,mo,dCnt), ds=fmt(cd);
      const mc=mk('div', `mc ${{cd.getMonth()!==mo?'other':''}} ${{ds===fmt(new Date())?'tod':''}} ${{pasteDates.has(ds)?'psel':''}}`);
      mc.dataset.date = ds;
      mc.innerHTML = `<div class="dn">${{cd.getDate()}}</div>`;
      
      SHIFTS.filter(s => s.start.startsWith(ds)).forEach(s => {{
        const c=deptClr(s.dept), ch=mk('div','chip');
        ch.style.cssText = `background:${{rgba(c,0.15)}}; color:${{c}}; border-left-color:${{c}}`;
        ch.textContent = `${{s.staff}} ${{s.start.split('T')[1].slice(0,5)}}`;
        ch.onclick = (e) => {{ e.stopPropagation(); showDet(s); }};
        mc.appendChild(ch);
      }});
      row.appendChild(mc);
      dCnt++;
    }}
    mg.appendChild(row);
  }}
  mv.appendChild(mg); root.appendChild(mv);
}}

function showDet(s) {{
  curS=s; $$('detBody').innerHTML = `<h3 style="color:#fff">${{s.staff}}</h3><p>${{s.dept}}</p><p>${{s.start}}</p>`;
  $$('detOv').style.display='flex';
}}
function closeDet() {{ $$('detOv').style.display='none'; }}
function startCopy() {{ clip=curS; pasteDates.clear(); closeDet(); $$('pbanner').classList.add('show'); }}
function onCalClick(e) {{
  const ds = e.target.closest('[data-date]')?.dataset.date;
  if(ds && clip) {{
    if(pasteDates.has(ds)) pasteDates.delete(ds); else pasteDates.add(ds);
    $$('pcnt').textContent = `${{pasteDates.size}}日選択中`;
    $$('pexec').style.display = pasteDates.size?'block':'none';
    renderMonth();
  }}
}}
</script>
</body>
</html>"""

    components.html(html, height=H, scrolling=False)
