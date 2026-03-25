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

    # ★ 修正: heightを固定px値で渡し、内部はそのpx-topbarで flex表示
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
  --success:#34d399;--danger:#f87171;--warn:#f59e0b;
  --today:rgba(91,138,240,.12);--hover:rgba(91,138,240,.08);
  --drag:rgba(91,138,240,.25);--nextday:rgba(139,92,246,.06);
  --font:'Noto Sans JP',sans-serif;--mono:'JetBrains Mono',monospace;
}}
*{{margin:0;padding:0;box-sizing:border-box;}}
html,body{{width:100%;height:{COMPONENT_HEIGHT}px;overflow:hidden;font-family:var(--font);background:var(--bg);color:var(--text);font-size:13px;user-select:none;}}

/* ── layout ── */
#app{{display:flex;flex-direction:column;height:{COMPONENT_HEIGHT}px;}}
#topbar{{flex-shrink:0;display:flex;align-items:center;gap:10px;padding:10px 14px;background:var(--surface);border-bottom:1px solid var(--border);flex-wrap:wrap;height:52px;}}
#cal{{flex:1;overflow:hidden;display:flex;flex-direction:column;min-height:0;}}

/* ── topbar widgets ── */
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

/* ── month ── */
.month-view{{flex:1;display:flex;flex-direction:column;overflow:hidden;min-height:0;}}
.mhdr{{display:grid;grid-template-columns:repeat(7,1fr);border-bottom:1px solid var(--border);flex-shrink:0;}}
.mhc{{padding:7px 0;text-align:center;font-size:11px;font-weight:600;color:var(--text-muted);letter-spacing:.08em;}}
.mhc:first-child{{color:#f87171;}}.mhc:last-child{{color:#60a5fa;}}
.mgrid{{flex:1;display:grid;grid-template-rows:repeat(6,1fr);overflow-y:auto;}}
.mrow{{display:grid;grid-template-columns:repeat(7,1fr);border-bottom:1px solid var(--border);}}
.mcell{{border-right:1px solid var(--border);padding:5px;cursor:pointer;transition:background .12s;overflow:hidden;min-height:80px;}}
.mcell:hover{{background:var(--hover);}}
.mcell.other{{opacity:.35;}}.mcell.tod{{background:var(--today);}}
.mcell.sun .dnum{{color:#f87171;}}.mcell.sat .dnum{{color:#60a5fa;}}
.dnum{{font-size:12px;font-weight:600;width:22px;height:22px;display:flex;align-items:center;justify-content:center;border-radius:50%;font-family:var(--mono);margin-bottom:3px;}}
.tod .dnum{{background:var(--accent);color:#fff;}}
.mchip{{font-size:10px;padding:2px 5px;border-radius:3px;margin-bottom:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-weight:500;cursor:pointer;}}
.mmore{{font-size:10px;color:var(--text-muted);cursor:pointer;padding:1px 4px;}}
.mmore:hover{{color:var(--accent);}}

/* ── week ── */
.week-view{{flex:1;display:flex;flex-direction:column;overflow:hidden;min-height:0;}}
.whdr{{display:grid;grid-template-columns:52px repeat(7,1fr);border-bottom:2px solid var(--border);background:var(--surface);flex-shrink:0;}}
.whcorner{{padding:8px 0;}}
.whday{{padding:7px 4px;text-align:center;border-left:1px solid var(--border);cursor:pointer;}}
.whday:hover{{background:var(--hover);}}
.wdow{{font-size:10px;font-weight:600;letter-spacing:.1em;text-transform:uppercase;color:var(--text-muted);}}
.wdnum{{font-size:18px;font-weight:700;font-family:var(--mono);line-height:1.2;}}
.whday.tod .wdnum{{color:var(--accent);}}
.whday.sun .wdow,.whday.sun .wdnum{{color:#f87171;}}
.whday.sat .wdow,.whday.sat .wdnum{{color:#60a5fa;}}
.wbody{{flex:1;display:flex;overflow-y:auto;min-height:0;}}
.wtimecol{{width:52px;flex-shrink:0;border-right:1px solid var(--border);background:var(--surface);}}
.wts{{height:48px;padding:4px 5px 0;border-bottom:1px solid var(--border);font-size:10px;color:var(--text-muted);font-family:var(--mono);text-align:right;}}
.wdaycols{{flex:1;display:grid;grid-template-columns:repeat(7,1fr);}}
.wdcol{{border-right:1px solid var(--border);position:relative;cursor:crosshair;}}
.wdcol.tod{{background:var(--today);}}
.whs{{height:48px;border-bottom:1px solid var(--border);}}

/* ── day ── */
.day-view{{flex:1;display:flex;flex-direction:column;overflow:hidden;min-height:0;}}
.dshdr{{display:flex;border-bottom:2px solid var(--border);background:var(--surface);flex-shrink:0;}}
.dtcorner{{width:60px;min-width:60px;flex-shrink:0;padding:8px 4px;font-size:10px;color:var(--text-muted);text-align:center;border-right:1px solid var(--border);}}
.dsch{{flex:1;min-width:90px;padding:7px 5px;text-align:center;border-right:1px solid var(--border);font-weight:600;font-size:12px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}}
.dbody{{flex:1;display:flex;overflow-y:auto;min-height:0;position:relative;}}
.dtcol{{width:60px;min-width:60px;flex-shrink:0;border-right:1px solid var(--border);background:var(--surface);}}
.dts{{height:48px;padding:4px 6px 0;border-bottom:1px solid var(--border);font-size:10px;color:var(--text-muted);font-family:var(--mono);text-align:right;}}
.dts.midnight{{border-top:2px solid var(--accent2);color:var(--accent2);font-weight:700;}}
.dscols{{flex:1;display:flex;overflow-x:auto;}}
.dscol{{flex:1;min-width:90px;border-right:1px solid var(--border);position:relative;cursor:crosshair;}}
.dhs{{height:48px;border-bottom:1px solid var(--border);}}
.nextzone{{position:absolute;left:0;right:0;background:var(--nextday);border-top:1px dashed var(--accent2);pointer-events:none;z-index:0;}}
.nowline{{position:absolute;left:0;right:0;height:2px;background:#f87171;z-index:6;pointer-events:none;}}
.nowline::before{{content:'';position:absolute;left:-3px;top:-3px;width:8px;height:8px;border-radius:50%;background:#f87171;}}

/* ── shift block ── */
.sb{{position:absolute;left:2px;right:2px;border-radius:4px;padding:3px 5px;font-size:10px;font-weight:600;overflow:hidden;z-index:1;cursor:pointer;transition:filter .12s;border:1px solid rgba(255,255,255,.1);}}
.sb:hover{{filter:brightness(1.25);z-index:4;}}
.sbname{{white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}}
.sbtime{{font-size:9px;opacity:.8;font-family:var(--mono);}}
.drag-sel{{position:absolute;left:2px;right:2px;background:var(--drag);border:2px dashed var(--accent);border-radius:4px;z-index:10;pointer-events:none;}}

/* ── modal ── */
.ov{{position:fixed;inset:0;background:rgba(0,0,0,.7);z-index:2000;display:flex;align-items:center;justify-content:center;backdrop-filter:blur(4px);}}
.modal{{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:22px;width:400px;max-width:96vw;box-shadow:0 24px 64px rgba(0,0,0,.6);animation:mIn .18s ease;}}
@keyframes mIn{{from{{transform:scale(.93);opacity:0;}}to{{transform:scale(1);opacity:1;}}}}
.mtitle{{font-size:15px;font-weight:700;margin-bottom:16px;display:flex;align-items:center;gap:8px;}}
.fg{{margin-bottom:12px;}}
.fl{{display:block;font-size:10px;font-weight:700;color:var(--text-muted);text-transform:uppercase;letter-spacing:.08em;margin-bottom:5px;}}
.fi,.fsel2{{width:100%;padding:8px 10px;border-radius:6px;border:1px solid var(--border);background:var(--surface2);color:var(--text);font-size:13px;font-family:var(--font);transition:border-color .15s;}}
.fi:focus,.fsel2:focus{{outline:none;border-color:var(--accent);box-shadow:0 0 0 3px rgba(91,138,240,.15);}}
.trow{{display:grid;grid-template-columns:1fr 20px 1fr;align-items:center;gap:6px;}}
.tsep{{color:var(--text-muted);text-align:center;}}
.mact{{display:flex;gap:8px;margin-top:16px;flex-wrap:wrap;}}
.btn{{flex:1;padding:9px;border-radius:6px;border:none;font-size:13px;font-family:var(--font);font-weight:600;cursor:pointer;transition:all .15s;min-width:80px;}}
.btn-p{{background:var(--accent);color:#fff;}}.btn-p:hover{{background:#4272d8;}}
.btn-s{{background:var(--surface2);color:var(--text);border:1px solid var(--border);}}.btn-s:hover{{border-color:var(--accent);color:var(--accent);}}
.btn-d{{background:var(--danger);color:#fff;flex:0;padding:9px 14px;}}.btn-d:hover{{background:#ef4444;}}
.btn-add{{background:var(--success);color:#fff;flex:0;padding:9px 14px;white-space:nowrap;}}.btn-add:hover{{background:#22c37e;}}

/* batch list */
.batch-list{{max-height:180px;overflow-y:auto;margin-bottom:10px;}}
.batch-item{{display:flex;align-items:center;justify-content:space-between;padding:6px 8px;background:var(--surface2);border-radius:6px;margin-bottom:4px;font-size:12px;border:1px solid var(--border);}}
.batch-item .bi-label{{flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}}
.batch-item .bi-del{{color:var(--danger);cursor:pointer;padding:2px 6px;border-radius:4px;font-size:11px;border:none;background:transparent;}}
.batch-item .bi-del:hover{{background:rgba(248,113,113,.15);}}
.batch-count{{font-size:11px;color:var(--text-muted);margin-bottom:8px;}}

/* detail */
.dchip{{display:inline-block;padding:3px 10px;border-radius:20px;font-size:12px;font-weight:600;margin-bottom:12px;}}
.drow{{display:flex;align-items:center;gap:10px;padding:7px 0;border-bottom:1px solid var(--border);font-size:13px;}}
.drow:last-child{{border-bottom:none;}}.dicon{{font-size:15px;width:22px;text-align:center;}}

/* toast / loading */
.toast{{position:fixed;bottom:18px;right:18px;padding:11px 18px;border-radius:8px;font-weight:600;font-size:12px;z-index:9999;animation:tIn .25s ease;max-width:300px;color:#fff;}}
.toast.ok{{background:var(--success);box-shadow:0 6px 20px rgba(52,211,153,.4);}}
.toast.err{{background:var(--danger);box-shadow:0 6px 20px rgba(248,113,113,.4);}}
.toast.warn{{background:var(--warn);box-shadow:0 6px 20px rgba(245,158,11,.4);}}
@keyframes tIn{{from{{transform:translateY(16px);opacity:0;}}to{{transform:translateY(0);opacity:1;}}}}
.ldg{{position:fixed;inset:0;background:rgba(0,0,0,.55);display:flex;align-items:center;justify-content:center;z-index:9998;gap:10px;font-size:13px;color:var(--text);}}
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
    <div class="fgrp">
      <select class="fsel" id="fstaff" onchange="renderView()"><option value="">全スタッフ</option></select>
      <select class="fsel" id="fdept"  onchange="renderView()"><option value="">全部門</option></select>
    </div>
  </div>
  <div id="cal"></div>
</div>

<!-- 登録モーダル（複数シフト対応） -->
<div class="ov" id="reg-ov" style="display:none" onclick="if(event.target===this)closeReg()">
  <div class="modal">
    <div class="mtitle">📋 シフト登録
      <span id="reg-mode-label" style="font-size:11px;color:var(--text-muted);font-weight:400;margin-left:4px;"></span>
    </div>

    <!-- 入力フォーム -->
    <div class="fg"><label class="fl">従業員</label><select class="fsel2" id="m-staff"></select></div>
    <div class="fg"><label class="fl">部門</label><select class="fsel2" id="m-dept"></select></div>
    <div class="fg"><label class="fl">日付</label><input type="date" class="fi" id="m-date"></div>
    <div class="fg">
      <label class="fl">時間</label>
      <div class="trow">
        <input type="time" class="fi" id="m-start" value="09:00">
        <div class="tsep">→</div>
        <input type="time" class="fi" id="m-end" value="18:00">
      </div>
    </div>

    <!-- キューリスト -->
    <div id="batch-section" style="display:none">
      <div class="batch-count" id="batch-count"></div>
      <div class="batch-list" id="batch-list"></div>
    </div>

    <div class="mact">
      <button class="btn btn-s" onclick="closeReg()">閉じる</button>
      <button class="btn btn-add" onclick="addToBatch()" title="フォームの内容をリストに追加">＋ リストに追加</button>
      <button class="btn btn-p"  onclick="saveAll()">保存</button>
    </div>
    <div style="font-size:10px;color:var(--text-muted);margin-top:8px;line-height:1.5;">
      💡「リストに追加」で複数件まとめて登録できます。「保存」でリスト全件を一括保存します。
    </div>
  </div>
</div>

<!-- 詳細モーダル -->
<div class="ov" id="det-ov" style="display:none" onclick="if(event.target===this)closeDet()">
  <div class="modal">
    <div class="mtitle">📌 シフト詳細</div>
    <div id="det-body"></div>
    <div class="mact" style="margin-top:14px">
      <button class="btn btn-s" onclick="closeDet()">閉じる</button>
      <button class="btn btn-d" onclick="delShift()">削除</button>
    </div>
  </div>
</div>

<script>
// ═══ DATA ═══════════════════════════════
const GAS   = "{gas_url}";
const STAFF = {staff_json};
const DEPTS = {dept_json};
let   SHIFTS = {shifts_json_str};
const CLRS = {color_palette};

function deptColor(d){{
  const i=DEPTS.indexOf(d);
  if(i>=0) return CLRS[i%CLRS.length];
  let h=0; for(const c of d) h=(h*31+c.charCodeAt(0))&0x7fffffff;
  return CLRS[h%CLRS.length];
}}
function rgba(hex,a){{
  return `rgba(${{parseInt(hex.slice(1,3),16)}},${{parseInt(hex.slice(3,5),16)}},${{parseInt(hex.slice(5,7),16)}},${{a}})`;
}}

// ═══ CONSTANTS ═══════════════════════════
const DAYS=['日','月','火','水','木','金','土'];
const MONS=['1月','2月','3月','4月','5月','6月','7月','8月','9月','10月','11月','12月'];
const HPX=48, DAY_H=30, MID_H=24; // 日ビュー: 30h, 深夜境界=24

// ═══ STATE ════════════════════════════════
let view='day';
let cur=new Date(); cur.setHours(0,0,0,0);
let batchQueue=[]; // 複数シフト登録キュー

// ═══ INIT ════════════════════════════════
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
function m2t(m){{const mm=m%1440;return`${{p2(Math.floor(mm/60))}}:${{p2(mm%60)}}`;}}
function shOn(ds,arr){{return arr.filter(s=>s.start&&fmt(pd(s.start))===ds);}}
function filtered(){{
  const fs=$$('fstaff')?.value||'',fd=$$('fdept')?.value||'';
  return SHIFTS.filter(s=>(!fs||s.staff===fs)&&(!fd||s.dept===fd));
}}

// ═══ VIEW ════════════════════════════════
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
}}

// ═══ MONTH ═══════════════════════════════
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
      const cd=new Date(cell.y,cell.m,cell.d),ds=fmt(cd),dow=cd.getDay();
      const mc=mk('div',`mcell${{cell.o?' other':''}}${{ds===td?' tod':''}}${{dow===0?' sun':dow===6?' sat':''}}`);
      const dn=mk('div','dnum'); dn.textContent=cell.d; mc.appendChild(dn);
      const ss=shOn(ds,fil);
      ss.slice(0,3).forEach(s=>{{
        const col=deptColor(s.dept),ch=mk('div','mchip');
        ch.style.cssText=`background:${{rgba(col,.25)}};color:${{col}};border-left:3px solid ${{col}}`;
        const st=pd(s.start),et=pd(s.end);
        ch.textContent=`${{s.staff}} ${{p2(st.getHours())}}:${{p2(st.getMinutes())}}-${{p2(et.getHours())}}:${{p2(et.getMinutes())}}`;
        ch.onclick=e=>{{e.stopPropagation();showDet(s);}};
        mc.appendChild(ch);
      }});
      if(ss.length>3){{const mm=mk('div','mmore');mm.textContent=`+${{ss.length-3}}件`;mc.appendChild(mm);}}
      mc.onclick=()=>openReg(ds);
      row.appendChild(mc);
    }});
    mg.appendChild(row);
  }}
  mv.appendChild(mg); root.appendChild(mv);
}}

// ═══ WEEK ════════════════════════════════
function wkStart(d){{const r=new Date(d);r.setDate(r.getDate()-r.getDay());return r;}}
function renderWeek(){{
  const ws=wkStart(cur),we=new Date(ws);we.setDate(we.getDate()+6);
  const [y1,m1,d1]=[ws.getFullYear(),ws.getMonth()+1,ws.getDate()];
  const [y2,m2,d2]=[we.getFullYear(),we.getMonth()+1,we.getDate()];
  $$('plabel').textContent=y1===y2?`${{y1}}年${{m1}}/${{d1}}-${{m2}}/${{d2}}`:`${{y1}}/${{m1}}/${{d1}}-${{y2}}/${{m2}}/${{d2}}`;
  const td=today(),fil=filtered();
  const root=$$('cal'); root.innerHTML='';
  const wv=mk('div','week-view');
  const wh=mk('div','whdr'); wh.appendChild(mk('div','whcorner'));
  for(let i=0;i<7;i++){{
    const d=new Date(ws);d.setDate(d.getDate()+i);
    const ds=fmt(d),dow=d.getDay();
    const hd=mk('div',`whday${{ds===td?' tod':''}}${{dow===0?' sun':dow===6?' sat':''}}`);
    hd.innerHTML=`<div class="wdow">${{DAYS[dow]}}</div><div class="wdnum">${{d.getDate()}}</div>`;
    hd.onclick=()=>{{cur=new Date(d);setView('day');}};
    wh.appendChild(hd);
  }}
  wv.appendChild(wh);
  const wb=mk('div','wbody');
  const tc=mk('div','wtimecol');
  for(let h=0;h<24;h++){{const ts=mk('div','wts');ts.textContent=h?p2(h)+':00':'';tc.appendChild(ts);}}
  wb.appendChild(tc);
  const dc=mk('div','wdaycols');
  for(let i=0;i<7;i++){{
    const d=new Date(ws);d.setDate(d.getDate()+i);
    const ds=fmt(d),dow=d.getDay();
    const col=mk('div',`wdcol${{ds===td?' tod':''}}`);
    for(let h=0;h<24;h++) col.appendChild(mk('div','whs'));
    dragWeek(col,ds);
    shOn(ds,fil).forEach(s=>col.appendChild(block(s,true,0)));
    dc.appendChild(col);
  }}
  wb.appendChild(dc);wv.appendChild(wb);root.appendChild(wv);
}}

// ═══ DAY ═════════════════════════════════
function renderDay(){{
  const y=cur.getFullYear(),mo=cur.getMonth()+1,d=cur.getDate(),dow=cur.getDay();
  $$('plabel').textContent=`${{y}}年${{mo}}月${{d}}日（${{DAYS[dow]}}）`;
  const ds=fmt(cur),td=today(),fil=filtered();
  const nxt=new Date(cur);nxt.setDate(nxt.getDate()+1);const dsN=fmt(nxt);
  const fsv=$$('fstaff')?.value||'';
  const staff=fsv?[fsv]:STAFF;
  const root=$$('cal'); root.innerHTML='';

  // スタッフ未登録でも「クリックで登録」できるメッセージ表示
  if(!staff.length){{
    root.innerHTML='<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;color:var(--text-muted);gap:12px;"><div style="font-size:32px">👥</div><div>スタッフを登録してください</div></div>';
    return;
  }}

  const dv=mk('div','day-view');
  // ヘッダー
  const sh=mk('div','dshdr');
  const corn=mk('div','dtcorner');
  corn.innerHTML=ds===td?'<span style="color:var(--accent);font-weight:700;font-size:11px">今日</span>':'';
  sh.appendChild(corn);
  staff.forEach(s=>{{const h=mk('div','dsch');h.textContent=s;sh.appendChild(h);}});
  dv.appendChild(sh);

  // ボディ
  const db=mk('div','dbody');
  const tc=mk('div','dtcol');
  for(let h=0;h<DAY_H;h++){{
    const ts=mk('div','dts'+(h===MID_H?' midnight':''));
    if(h===0) ts.textContent='';
    else if(h===MID_H) ts.textContent='翌0:00';
    else if(h>MID_H) ts.textContent=p2(h-24)+':00';
    else ts.textContent=p2(h)+':00';
    tc.appendChild(ts);
  }}
  db.appendChild(tc);

  const sc=mk('div','dscols');
  staff.forEach(s=>{{
    const col=mk('div','dscol');
    for(let h=0;h<DAY_H;h++) col.appendChild(mk('div','dhs'));
    // 翌日ゾーン背景
    const nz=mk('div','nextzone');
    nz.style.top=MID_H*HPX+'px';nz.style.bottom='0';
    col.appendChild(nz);
    dragDay(col,ds,dsN,s);
    // 当日シフト
    fil.filter(x=>x.staff===s&&x.start&&fmt(pd(x.start))===ds)
       .forEach(x=>col.appendChild(block(x,false,0)));
    // 翌日0-6時シフト
    fil.filter(x=>x.staff===s&&x.start&&fmt(pd(x.start))===dsN)
       .forEach(x=>{{
         const h=pd(x.start).getHours();
         if(h<(DAY_H-MID_H)) col.appendChild(block(x,false,1440));
       }});
    sc.appendChild(col);
  }});
  db.appendChild(sc);dv.appendChild(db);root.appendChild(dv);

  // 現在時刻ライン
  const now=new Date(),diff=(now-cur)/60000;
  if(diff>=0&&diff<DAY_H*60){{
    const nl=mk('div','nowline');
    nl.style.cssText=`top:${{diff/60*HPX}}px;left:60px;right:0;`;
    db.appendChild(nl);
  }}
}}

// ═══ SHIFT BLOCK ═════════════════════════
function block(s,showStaff,offsetMins){{
  const st=pd(s.start),et=pd(s.end);
  const sm=st.getHours()*60+st.getMinutes()+offsetMins;
  const em=et.getHours()*60+et.getMinutes()+offsetMins;
  const top=sm/60*HPX, ht=Math.max((em-sm)/60*HPX,16);
  const col=deptColor(s.dept);
  const b=mk('div','sb');
  b.style.cssText=`top:${{top}}px;height:${{ht}}px;background:${{rgba(col,.3)}};border-left:3px solid ${{col}};color:${{col}};`;
  const nm=mk('div','sbname');nm.textContent=showStaff?s.staff:s.dept;b.appendChild(nm);
  if(ht>28){{const tm=mk('div','sbtime');tm.textContent=`${{p2(st.getHours())}}:${{p2(st.getMinutes())}}-${{p2(et.getHours())}}:${{p2(et.getMinutes())}}`;b.appendChild(tm);}}
  b.onclick=e=>{{e.stopPropagation();showDet(s);}};
  return b;
}}

// ═══ DRAG ════════════════════════════════
let ds=null;
function y2m(y){{return y/HPX*60;}}
function snap(m){{return Math.round(m/15)*15;}}
function dragWeek(col,dateStr){{
  let el=null;
  col.addEventListener('mousedown',e=>{{
    if(e.button||e.target.classList.contains('sb')) return; e.preventDefault();
    const y=e.clientY-col.getBoundingClientRect().top+(col.closest('.wbody')?.scrollTop||0);
    const sm=snap(y2m(y));
    el=mk('div','drag-sel');el.style.top=sm/60*HPX+'px';el.style.height='0';col.appendChild(el);
    ds={{col,date:dateStr,staff:null,sm,em:sm,el}};
  }});
  col.addEventListener('mousemove',e=>{{
    if(!ds||ds.col!==col)return;
    const y=e.clientY-col.getBoundingClientRect().top+(col.closest('.wbody')?.scrollTop||0);
    const em=snap(y2m(y));
    el.style.top=Math.min(ds.sm,em)/60*HPX+'px';el.style.height=Math.abs(em-ds.sm)/60*HPX+'px';
    ds.em=em;
  }});
  col.addEventListener('mouseup',()=>{{
    if(!ds||ds.col!==col)return;
    const s=Math.min(ds.sm,ds.em),en=Math.max(ds.sm,ds.em);
    el.remove();const d=ds.date;ds=null;
    openReg(d,m2t(s),m2t(en-s<15?s+60:en));
  }});
}}
function dragDay(col,dateStr,dateStrN,staffName){{
  let el=null;
  col.addEventListener('mousedown',e=>{{
    if(e.button||e.target.classList.contains('sb')) return; e.preventDefault();
    const y=e.clientY-col.getBoundingClientRect().top+(col.closest('.dbody')?.scrollTop||0);
    const sm=Math.min(snap(y2m(y)),DAY_H*60);
    el=mk('div','drag-sel');el.style.top=sm/60*HPX+'px';el.style.height='0';col.appendChild(el);
    ds={{col,date:dateStr,dateN:dateStrN,staff:staffName,sm,em:sm,el}};
  }});
  col.addEventListener('mousemove',e=>{{
    if(!ds||ds.col!==col)return;
    const y=e.clientY-col.getBoundingClientRect().top+(col.closest('.dbody')?.scrollTop||0);
    const em=Math.min(snap(y2m(y)),DAY_H*60);
    el.style.top=Math.min(ds.sm,em)/60*HPX+'px';el.style.height=Math.abs(em-ds.sm)/60*HPX+'px';
    ds.em=em;
  }});
  col.addEventListener('mouseup',()=>{{
    if(!ds||ds.col!==col)return;
    const s=Math.min(ds.sm,ds.em),en=Math.max(ds.sm,ds.em);
    const isN=s>=1440,actualDate=isN?ds.dateN:ds.date,stf=ds.staff;
    el.remove();ds=null;
    openReg(actualDate,m2t(s),m2t(en-s<15?s+60:en),stf);
  }});
}}
document.addEventListener('mouseup',()=>{{if(ds?.el)ds.el.remove();ds=null;}});

// ═══ REGISTER MODAL（複数シフト対応）═════
function openReg(dateStr,startT,endT,staffName){{
  $$('m-date').value=dateStr||fmt(cur);
  $$('m-start').value=startT||'09:00';
  $$('m-end').value=endT||'18:00';
  if(staffName){{
    const sel=$$('m-staff');
    for(const o of sel.options) if(o.value===staffName){{sel.value=staffName;break;}}
  }}
  renderBatchUI();
  $$('reg-ov').style.display='flex';
}}
function closeReg(){{
  $$('reg-ov').style.display='none';
  batchQueue=[];
  renderBatchUI();
}}

// バッチキューにフォームの内容を追加
function addToBatch(){{
  const staff=$$('m-staff').value,dept=$$('m-dept').value;
  const date=$$('m-date').value,s=$$('m-start').value,e=$$('m-end').value;
  if(!staff||!dept||!date||!s||!e){{alert('すべて入力してください');return;}}
  if(s>=e){{alert('終了は開始より後にしてください');return;}}
  batchQueue.push({{staff,dept,date,start:s,end:e}});
  renderBatchUI();
  // フォームのスタッフ・時間はそのまま（次の人を連続入力しやすくする）
  // 日付だけ維持、スタッフ選択を次の人に進める
  showToast(`➕ リストに追加: ${{staff}} ${{s}}-${{e}}`,'ok',2000);
}}

function renderBatchUI(){{
  const sec=$$('batch-section'),list=$$('batch-list'),cnt=$$('batch-count');
  const lbl=$$('reg-mode-label');
  if(batchQueue.length===0){{
    sec.style.display='none';
    lbl.textContent='';
    return;
  }}
  sec.style.display='block';
  lbl.textContent=`（キュー: ${{batchQueue.length}}件）`;
  cnt.textContent=`登録予定: ${{batchQueue.length}} 件`;
  list.innerHTML='';
  batchQueue.forEach((item,i)=>{{
    const row=mk('div','batch-item');
    const lbl2=mk('div','bi-label');
    lbl2.textContent=`${{item.staff}} / ${{item.dept}} / ${{item.date}} ${{item.start}}-${{item.end}}`;
    const del=mk('button','bi-del');
    del.textContent='✕';del.onclick=()=>{{batchQueue.splice(i,1);renderBatchUI();}};
    row.appendChild(lbl2);row.appendChild(del);
    list.appendChild(row);
  }});
}}

// 保存: キューがあればキュー全件、なければフォーム単体
async function saveAll(){{
  let items=[];
  if(batchQueue.length>0){{
    items=[...batchQueue];
  }} else {{
    const staff=$$('m-staff').value,dept=$$('m-dept').value;
    const date=$$('m-date').value,s=$$('m-start').value,e=$$('m-end').value;
    if(!staff||!dept||!date||!s||!e){{alert('すべて入力してください');return;}}
    if(s>=e){{alert('終了は開始より後にしてください');return;}}
    items=[{{staff,dept,date,start:s,end:e}}];
  }}

  closeReg();
  showLdg(`${{items.length}}件 保存中...`);

  let ok=0,fail=0;
  for(const item of items){{
    try{{
      await fetch(GAS+'?'+new URLSearchParams({{action:'add_shift',name:item.staff,dept:item.dept,start:`${{item.date}} ${{item.start}}`,end:`${{item.date}} ${{item.end}}`}}));
      SHIFTS.push({{rowIndex:-1,staff:item.staff,dept:item.dept,start:`${{item.date}}T${{item.start}}:00`,end:`${{item.date}}T${{item.end}}:00`}});
      ok++;
    }}catch{{fail++;}}
  }}

  hideLdg();
  if(fail===0) showToast(`✅ ${{ok}}件 保存しました`,'ok');
  else showToast(`⚠️ ${{ok}}件成功 / ${{fail}}件失敗`,'warn');
  renderView();
}}

// ═══ DETAIL + DELETE ════════════════════
let curS=null,curI=-1;
function showDet(s){{
  curS=s;curI=SHIFTS.indexOf(s);
  const st=pd(s.start),et=pd(s.end),col=deptColor(s.dept);
  $$('det-body').innerHTML=`
    <span class="dchip" style="background:${{rgba(col,.25)}};color:${{col}}">${{s.dept}}</span>
    <div class="drow"><span class="dicon">👤</span><span>${{s.staff}}</span></div>
    <div class="drow"><span class="dicon">📅</span><span>${{fmt(st)}}</span></div>
    <div class="drow"><span class="dicon">🕐</span><span>${{p2(st.getHours())}}:${{p2(st.getMinutes())}} → ${{p2(et.getHours())}}:${{p2(et.getMinutes())}}</span></div>
    <div class="drow"><span class="dicon">⏱️</span><span>${{Math.round((et-st)/60000)}}分</span></div>`;
  $$('det-ov').style.display='flex';
}}
function closeDet(){{$$('det-ov').style.display='none';curS=null;}}
async function delShift(){{
  if(!curS||!confirm(`${{curS.staff}} のシフトを削除しますか？`))return;
  const s=curS;closeDet();showLdg('削除中...');
  const norm=iso=>iso.replace('T',' ').replace(/(\d{{4}}-\d{{2}}-\d{{2}} \d{{2}}:\d{{2}}).*$/,'$1');
  let ok=false;
  try{{
    const r=await fetch(GAS+'?'+new URLSearchParams({{action:'del_shift',name:s.staff,dept:s.dept,start:norm(s.start),end:norm(s.end)}}));
    const t=await r.text();
    ok=r.ok&&(t.toLowerCase().includes('delet')||t.toLowerCase().includes('ok')||t.trim().length===0);
  }}catch(e){{console.warn(e);}}
  const i=curI>=0?curI:SHIFTS.findIndex(x=>x.staff===s.staff&&x.dept===s.dept&&x.start===s.start);
  if(i>=0)SHIFTS.splice(i,1);
  hideLdg();
  ok?showToast('🗑️ 削除しました','ok'):showToast('🗑️ 画面から削除（シートはGAS del_shift設定後に連携）','warn');
  renderView();
}}

// ═══ HELPERS ═════════════════════════════
function showToast(msg,type='ok',dur=3500){{
  const t=mk('div',`toast ${{type}}`);t.textContent=msg;
  document.body.appendChild(t);setTimeout(()=>t.remove(),dur);
}}
function showLdg(msg='処理中...'){{
  const l=mk('div','ldg');l.id='ldg';
  l.innerHTML=`<div class="spin"></div><span>${{msg}}</span>`;
  document.body.appendChild(l);
}}
function hideLdg(){{$$('ldg')?.remove();}}
document.addEventListener('keydown',e=>{{
  if(e.key==='Escape'){{closeReg();closeDet();}}
  if(!e.target.matches('input,select,textarea')){{
    if(e.key==='ArrowLeft') nav(-1);
    if(e.key==='ArrowRight') nav(1);
  }}
}});
</script>
</body>
</html>"""

    components.html(html_code, height=COMPONENT_HEIGHT, scrolling=False)
