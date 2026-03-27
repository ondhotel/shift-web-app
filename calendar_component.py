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

/* ── レイアウト ── */
#app{{display:flex;flex-direction:column;height:{H}px;}}
#topbar{{flex-shrink:0;display:flex;align-items:center;gap:8px;padding:8px 12px;background:var(--sf);border-bottom:1px solid var(--bd);flex-wrap:wrap;}}
#pbanner{{display:none;width:100%;align-items:center;gap:8px;padding:4px 0 2px;flex-wrap:wrap;}}
#pbanner.show{{display:flex;}}
.pbl{{font-size:11px;color:var(--cp);font-weight:700;}}
.pbcnt{{font-size:11px;color:var(--tx2);}}
.pbb{{padding:3px 10px;border-radius:5px;border:1px solid var(--cp);background:rgba(240,160,91,.15);color:var(--cp);cursor:pointer;font-size:11px;font-family:var(--fn);font-weight:600;transition:all .15s;}}
.pbb:hover{{background:var(--cp);color:#000;}}
.pbb.exec{{background:var(--cp);color:#000;}}
.pbb.cancel{{border-color:var(--tx2);color:var(--tx2);background:transparent;}}
.pbb.cancel:hover{{background:var(--tx2);color:#000;}}
#cal{{flex:1;overflow:hidden;display:flex;flex-direction:column;min-height:0;}}

/* ── トップバーUI ── */
.vtab{{display:flex;background:var(--sf2);border-radius:7px;padding:3px;gap:2px;}}
.vt{{padding:4px 13px;border-radius:5px;cursor:pointer;font-size:12px;font-weight:500;color:var(--tx2);border:none;background:transparent;transition:all .15s;font-family:var(--fn);}}
.vt.on{{background:var(--ac);color:#fff;box-shadow:0 2px 8px rgba(91,138,240,.4);}}
.vt:hover:not(.on){{background:var(--hv);color:var(--tx);}}
.navg{{display:flex;align-items:center;gap:5px;}}
.nb{{width:28px;height:28px;border-radius:5px;border:1px solid var(--bd);background:var(--sf2);color:var(--tx);cursor:pointer;font-size:14px;display:flex;align-items:center;justify-content:center;transition:all .15s;}}
.nb:hover{{border-color:var(--ac);background:var(--hv);}}
#plbl{{font-size:14px;font-weight:700;min-width:160px;text-align:center;}}
.tdbtn{{padding:4px 11px;border-radius:5px;border:1px solid var(--bd);background:var(--sf2);color:var(--tx);cursor:pointer;font-size:12px;font-family:var(--fn);font-weight:500;transition:all .15s;}}
.tdbtn:hover{{border-color:var(--ac);color:var(--ac);}}
.fgrp{{display:flex;gap:6px;margin-left:auto;align-items:center;}}
.fsel{{padding:4px 7px;border-radius:5px;border:1px solid var(--bd);background:var(--sf2);color:var(--tx);font-size:12px;font-family:var(--fn);cursor:pointer;}}

/* ── 月ビュー ── */
.mv{{flex:1;display:flex;flex-direction:column;overflow:hidden;min-height:0;}}
.mhdr{{display:grid;grid-template-columns:repeat(7,1fr);border-bottom:1px solid var(--bd);flex-shrink:0;}}
.mhc{{padding:6px 0;text-align:center;font-size:11px;font-weight:600;color:var(--tx2);}}
.mhc:first-child{{color:#f87171;}}.mhc:last-child{{color:#60a5fa;}}
.mgrid{{flex:1;display:grid;grid-template-rows:repeat(6,1fr);overflow:hidden;}}
.mrow{{display:grid;grid-template-columns:repeat(7,1fr);border-bottom:1px solid var(--bd);}}
.mc{{border-right:1px solid var(--bd);padding:4px;cursor:pointer;overflow-y:auto;min-height:0;transition:background .1s;position:relative;scrollbar-width:none;}}
.mc::-webkit-scrollbar {{display:none;}}
.mc:hover{{background:var(--hv);}}
.mc.other{{opacity:.3;}}.mc.tod{{background:var(--tod);}}
.mc.sun .dn{{color:#f87171;}}.mc.sat .dn{{color:#60a5fa;}}
.mc.psel{{background:var(--sel)!important;outline:2px solid var(--cp);outline-offset:-2px;}}
.mc.pmode{{cursor:copy;}}
.dn{{font-size:11px;font-weight:600;width:20px;height:20px;display:flex;align-items:center;justify-content:center;border-radius:50%;font-family:var(--mn);margin-bottom:4px;position:sticky;top:0;background:inherit;z-index:2;}}
.tod .dn{{background:var(--ac);color:#fff;}}
/* 月ビュー用チップ（シンプル化） */
.chip{{font-size:10px;padding:2px 4px;border-radius:3px;margin-bottom:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-weight:500;cursor:pointer;border-left:3px solid transparent;}}
.chip.copied{{outline:2px solid var(--cp);}}

/* ── 週ビュー ── */
.wv{{flex:1;display:flex;flex-direction:column;overflow:hidden;min-height:0;}}
.whdr{{display:grid;grid-template-columns:50px repeat(7,1fr);border-bottom:2px solid var(--bd);background:var(--sf);flex-shrink:0;}}
.wcrn{{padding:8px 0;}}
.whd{{padding:6px 3px;text-align:center;border-left:1px solid var(--bd);cursor:pointer;transition:background .1s;}}
.whd:hover{{background:var(--hv);}}
.whd.pmode{{cursor:copy;}}
.whd.psel{{background:var(--sel)!important;outline:2px solid var(--cp);outline-offset:-2px;}}
.wdow{{font-size:10px;font-weight:600;letter-spacing:.1em;text-transform:uppercase;color:var(--tx2);}}
.wdn{{font-size:17px;font-weight:700;font-family:var(--mn);line-height:1.2;}}
.whd.tod .wdn{{color:var(--ac);}}
.whd.sun .wdow,.whd.sun .wdn{{color:#f87171;}}
.whd.sat .wdow,.whd.sat .wdn{{color:#60a5fa;}}
.wbody{{flex:1;display:flex;overflow-y:auto;min-height:0;}}
.wtc{{width:50px;flex-shrink:0;border-right:1px solid var(--bd);background:var(--sf);}}
.wts{{height:48px;padding:3px 5px 0;border-bottom:1px solid var(--bd);font-size:10px;color:var(--tx2);font-family:var(--mn);text-align:right;}}
.wdc{{flex:1;display:grid;grid-template-columns:repeat(7,1fr);}}
.wdcol{{border-right:1px solid var(--bd);position:relative;cursor:crosshair;}}
.wdcol.tod{{background:var(--tod);}}
.wdcol.pmode{{cursor:copy;}}
.wdcol.psel{{background:var(--sel)!important;}}
.whs{{height:48px;border-bottom:1px solid var(--bd);}}

/* ── 日ビュー ── */
.dv{{flex:1;display:flex;flex-direction:column;overflow:hidden;min-height:0;}}
.dshdr{{display:flex;border-bottom:2px solid var(--bd);background:var(--sf);flex-shrink:0;}}
.dcrn{{width:58px;min-width:58px;flex-shrink:0;padding:7px 4px;font-size:10px;color:var(--tx2);text-align:center;border-right:1px solid var(--bd);}}
.dsch{{flex:1;min-width:88px;padding:6px 4px;text-align:center;border-right:1px solid var(--bd);font-weight:600;font-size:12px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}}
.dbody{{flex:1;display:flex;overflow-y:auto;min-height:0;position:relative;}}
.dtc{{width:58px;min-width:58px;flex-shrink:0;border-right:1px solid var(--bd);background:var(--sf);}}
.dts{{height:48px;padding:3px 6px 0;border-bottom:1px solid var(--bd);font-size:10px;color:var(--tx2);font-family:var(--mn);text-align:right;}}
.dts.mid{{border-top:2px solid var(--ac2);color:var(--ac2);font-weight:700;}}
.dscs{{flex:1;display:flex;overflow-x:auto;}}
.dscol{{flex:1;min-width:88px;border-right:1px solid var(--bd);position:relative;cursor:crosshair;}}
.dhs{{height:48px;border-bottom:1px solid var(--bd);}}
.nzone{{position:absolute;left:0;right:0;background:var(--nday);border-top:1px dashed var(--ac2);pointer-events:none;z-index:0;}}
.nowl{{position:absolute;left:0;right:0;height:2px;background:#f87171;z-index:6;pointer-events:none;}}
.nowl::before{{content:'';position:absolute;left:-3px;top:-3px;width:8px;height:8px;border-radius:50%;background:#f87171;}}

/* ── シフトブロック ── */
.sb{{position:absolute;border-radius:4px;padding:2px 4px;font-size:10px;font-weight:600;overflow:hidden;z-index:1;cursor:pointer;transition:filter .12s;border:1px solid rgba(255,255,255,.1);}}
.sb:hover{{filter:brightness(1.25);z-index:4;}}
.sb.copied{{outline:2px solid var(--cp);box-shadow:0 0 0 3px rgba(240,160,91,.3);z-index:2;}}
.sbn{{white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}}
.sbt{{font-size:9px;opacity:.8;font-family:var(--mn);}}
.dragsel{{position:absolute;left:2px;right:2px;background:var(--drag);border:2px dashed var(--ac);border-radius:4px;z-index:10;pointer-events:none;}}

/* ── モーダル ── */
.ov{{position:fixed;inset:0;background:rgba(0,0,0,.72);z-index:3000;display:flex;align-items:center;justify-content:center;backdrop-filter:blur(4px);}}
.modal{{background:var(--sf);border:1px solid var(--bd);border-radius:12px;padding:20px;width:390px;max-width:95vw;box-shadow:0 24px 64px rgba(0,0,0,.6);animation:mIn .18s ease;}}
@keyframes mIn{{from{{transform:scale(.93);opacity:0;}}to{{transform:scale(1);opacity:1;}}}}
.mt{{font-size:15px;font-weight:700;margin-bottom:14px;display:flex;align-items:center;gap:8px;}}
.fg{{margin-bottom:11px;}}
.fl{{display:block;font-size:10px;font-weight:700;color:var(--tx2);text-transform:uppercase;letter-spacing:.08em;margin-bottom:4px;}}
.fi,.fs2{{width:100%;padding:7px 10px;border-radius:6px;border:1px solid var(--bd);background:var(--sf2);color:var(--tx);font-size:13px;font-family:var(--fn);transition:border-color .15s;}}
.fi:focus,.fs2:focus{{outline:none;border-color:var(--ac);box-shadow:0 0 0 3px rgba(91,138,240,.15);}}
.tr{{display:grid;grid-template-columns:1fr 18px 1fr;align-items:center;gap:5px;}}
.tsep{{color:var(--tx2);text-align:center;}}
.ma{{display:flex;gap:7px;margin-top:14px;flex-wrap:wrap;}}
.btn{{flex:1;padding:8px;border-radius:6px;border:none;font-size:13px;font-family:var(--fn);font-weight:600;cursor:pointer;transition:all .15s;min-width:72px;}}
.bp{{background:var(--ac);color:#fff;}}.bp:hover{{background:#4272d8;}}
.bs{{background:var(--sf2);color:var(--tx);border:1px solid var(--bd);}}.bs:hover{{border-color:var(--ac);color:var(--ac);}}
.bd{{background:var(--ng);color:#fff;flex:0;padding:8px 13px;}}.bd:hover{{background:#ef4444;}}
.bc{{background:rgba(240,160,91,.2);color:var(--cp);border:1px solid var(--cp);flex:0;padding:8px 13px;}}.bc:hover{{background:var(--cp);color:#000;}}
.badd{{background:var(--ok);color:#fff;flex:0;padding:8px 13px;white-space:nowrap;}}.badd:hover{{background:#22c37e;}}
.blist{{max-height:140px;overflow-y:auto;margin-bottom:7px;}}
.bi{{display:flex;align-items:center;justify-content:space-between;padding:5px 7px;background:var(--sf2);border-radius:5px;margin-bottom:3px;font-size:11px;border:1px solid var(--bd);}}
.bilbl{{flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}}
.bidel{{color:var(--ng);cursor:pointer;padding:1px 5px;border-radius:3px;font-size:11px;border:none;background:transparent;}}
.bidel:hover{{background:rgba(248,113,113,.15);}}
.dcl{{font-size:11px;color:var(--tx2);margin-bottom:7px;}}
.dchip{{display:inline-block;padding:3px 10px;border-radius:20px;font-size:12px;font-weight:600;margin-bottom:11px;}}
.dr{{display:flex;align-items:center;gap:9px;padding:6px 0;border-bottom:1px solid var(--bd);font-size:13px;}}
.dr:last-child{{border-bottom:none;}}.di{{font-size:14px;width:20px;text-align:center;}}
.toast{{position:fixed;bottom:16px;right:16px;padding:10px 16px;border-radius:8px;font-weight:600;font-size:12px;z-index:9999;animation:tIn .22s ease;max-width:300px;color:#fff;}}
.toast.ok{{background:var(--ok);}}.toast.err{{background:var(--ng);}}.toast.wn{{background:var(--wn);}}
@keyframes tIn{{from{{transform:translateY(14px);opacity:0;}}to{{transform:translateY(0);opacity:1;}}}}
.ldg{{position:fixed;inset:0;background:rgba(0,0,0,.55);display:flex;align-items:center;justify-content:center;z-index:9998;gap:10px;font-size:13px;color:var(--tx);}}
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
      <button class="pbb exec" id="pexec" style="display:none">選択した日に貼り付け</button>
      <button class="pbb cancel" id="pcancel">✕ キャンセル (Esc)</button>
    </div>

    <div class="fgrp">
      <select class="fsel" id="fstaff"><option value="">全スタッフ</option></select>
      <select class="fsel" id="fdept"><option value="">全部門</option></select>
    </div>
  </div>
  <div id="cal"></div>
</div>

<div class="ov" id="regOv" style="display:none" onclick="if(event.target===this)closeReg()">
  <div class="modal">
    <div class="mt">📋 シフト登録 <span id="regLbl" style="font-size:11px;color:var(--tx2);font-weight:400;"></span></div>
    <div class="fg"><label class="fl">従業員</label><select class="fs2" id="mStaff"></select></div>
    <div class="fg"><label class="fl">部門</label><select class="fs2" id="mDept"></select></div>
    <div class="fg"><label class="fl">日付</label><input type="date" class="fi" id="mDate"></div>
    <div class="fg">
      <label class="fl">時間</label>
      <div class="tr">
        <input type="time" class="fi" id="mS" value="09:00">
        <div class="tsep">→</div>
        <input type="time" class="fi" id="mE" value="18:00">
      </div>
    </div>
    <div id="batchSec" style="display:none">
      <div class="dcl" id="batchCnt"></div>
      <div class="blist" id="batchList"></div>
    </div>
    <div class="ma">
      <button class="btn bs" onclick="closeReg()">閉じる</button>
      <button class="btn badd" onclick="addBatch()">＋ リストに追加</button>
      <button class="btn bp"  onclick="saveAll()">保存</button>
    </div>
  </div>
</div>

<div class="ov" id="detOv" style="display:none" onclick="if(event.target===this)closeDet()">
  <div class="modal">
    <div class="mt">📌 シフト詳細</div>
    <div id="detBody"></div>
    <div class="ma" style="margin-top:12px">
      <button class="btn bs" onclick="closeDet()">閉じる</button>
      <button class="btn bc" onclick="startCopy()">📋 コピー</button>
      <button class="btn bd" onclick="delShift()">削除</button>
    </div>
  </div>
</div>

<script>
// ══════════════════════════════════════
// データ & ユーティリティ
// ══════════════════════════════════════
const GAS    = "{gas_url}";
const STAFF  = {staff_json};
const DEPTS  = {dept_json};
let   SHIFTS = {shifts_json_str};
const CLRS   = {color_palette};

function deptClr(d) {{
  const i = DEPTS.indexOf(d);
  if (i >= 0) return CLRS[i % CLRS.length];
  let h = 0; for (const c of d) h = (h * 31 + c.charCodeAt(0)) & 0x7fffffff;
  return CLRS[h % CLRS.length];
}}
function rgba(hex, a) {{
  return `rgba(${{parseInt(hex.slice(1,3),16)}},${{parseInt(hex.slice(3,5),16)}},${{parseInt(hex.slice(5,7),16)}},${{a}})`;
}}

const DAYS  = ['日','月','火','水','木','金','土'];
const MONS  = ['1月','2月','3月','4月','5月','6月','7月','8月','9月','10月','11月','12月'];
const HPX   = 48;
const DAY_H = 30;
const MID_H = 24;

let view = 'day';
let cur  = new Date(); cur.setHours(0,0,0,0);
let batch = [];
let clip  = null;
let pasteDates = new Set();
let curS = null, curI = -1;
let dragSt = null;

const $$ = id => document.getElementById(id);
const mk  = (t,c) => {{ const e=document.createElement(t); if(c)e.className=c; return e; }};
const fmt = d => `${{d.getFullYear()}}-${{p2(d.getMonth()+1)}}-${{p2(d.getDate())}}`;
const p2  = n => String(n).padStart(2,'0');
const tod = () => fmt(new Date());
const pd_ = s => new Date(s);
const m2t = m => {{ const mm=m%1440; return `${{p2(Math.floor(mm/60))}}:${{p2(mm%60)}}`; }};
const shOn = (ds,arr) => arr.filter(s => s.start && fmt(pd_(s.start)) === ds);
const getFil = () => {{
  const fs = $$('fstaff').value||'', fd = $$('fdept').value||'';
  return SHIFTS.filter(s => (!fs||s.staff===fs)&&(!fd||s.dept===fd));
}};
const sMins = s => {{ const d=pd_(s.start); return d.getHours()*60+d.getMinutes(); }};
const eMins = s => {{ const d=pd_(s.end);   return d.getHours()*60+d.getMinutes()||1440; }};

window.addEventListener('load', () => {{
  ['fstaff','mStaff'].forEach(id => STAFF.forEach(s => $$(id).appendChild(new Option(s,s))));
  ['fdept', 'mDept' ].forEach(id => DEPTS.forEach(d => $$(id).appendChild(new Option(d,d))));
  document.querySelector('.vtab').addEventListener('click', e => {{ const v=e.target.dataset.v; if(v)setView(v); }});
  $$('navP').onclick = () => nav(-1);
  $$('navN').onclick = () => nav(1);
  $$('tdBtn').onclick = goToday;
  $$('fstaff').onchange = renderView;
  $$('fdept').onchange  = renderView;
  $$('pcancel').onclick = cancelCopy;
  $$('pexec').onclick   = execPaste;
  $$('cal').addEventListener('click', onCalClick);
  renderView();
}});

function setView(v) {{ view=v; document.querySelectorAll('.vt').forEach(e=>e.classList.toggle('on',e.dataset.v===v)); renderView(); }}
function nav(d) {{
  if(view==='day') cur.setDate(cur.getDate()+d);
  else if(view==='week') cur.setDate(cur.getDate()+d*7);
  else cur.setMonth(cur.getMonth()+d);
  renderView();
}}
function goToday() {{ cur=new Date(); cur.setHours(0,0,0,0); renderView(); }}
function renderView() {{
  if(view==='day') renderDay(); else if(view==='week') renderWeek(); else renderMonth();
  updateBanner();
}}

// ══════════════════════════════════════
// 月ビュー (修正版: シンプル1行チップ & 全表示)
// ══════════════════════════════════════
function renderMonth() {{
  const y=cur.getFullYear(), mo=cur.getMonth();
  $$('plbl').textContent = `${{y}}年 ${{MONS[mo]}}`;
  const td=tod(), fil=getFil();
  const first=new Date(y,mo,1), sdow=first.getDay(), dim=new Date(y,mo+1,0).getDate(), prev=new Date(y,mo,0).getDate();
  let cells=[];
  for(let i=sdow-1;i>=0;i--) cells.push({{d:prev-i,m:mo-1,y,o:true}});
  for(let d=1;d<=dim;d++)    cells.push({{d,m:mo,y,o:false}});
  while(cells.length<42)     cells.push({{d:cells.length-dim-sdow+1,m:mo+1,y,o:true}});

  const root=$$('cal'); root.innerHTML='';
  const mv=mk('div','mv');
  const mh=mk('div','mhdr');
  DAYS.forEach(d=>{{ const c=mk('div','mhc'); c.textContent=d; mh.appendChild(c); }});
  mv.appendChild(mh);
  const mg=mk('div','mgrid');

  for(let r=0;r<6;r++) {{
    const row=mk('div','mrow');
    cells.slice(r*7,r*7+7).forEach(cell => {{
      const cd=new Date(cell.y,cell.m,cell.d), ds=fmt(cd), dow=cd.getDay();
      const mc = mk('div', `mc${{cell.o?' other':''}}${{ds===td?' tod':''}}${{dow===0?' sun':dow===6?' sat':''}}${{clip?' pmode':''}}${{pasteDates.has(ds)?' psel':''}}`);
      mc.dataset.date = ds;
      if (!clip) mc.dataset.openreg = ds;

      const dn=mk('div','dn'); dn.textContent=cell.d; mc.appendChild(dn);

      // シフト表示：1行のシンプルなチップに変更し、全件表示
      const dayS = shOn(ds, fil).sort((a,b)=>sMins(a)-sMins(b));
      dayS.forEach(s => {{
        const col=deptClr(s.dept);
        const st=pd_(s.start), et=pd_(s.end);
        const ch=mk('div','chip');
        ch.style.cssText=`background:${{rgba(col,.15)}};color:${{col}};border-left-color:${{col}}`;
        ch.textContent=`${{s.staff}} ${{st.getHours()}}:${{p2(st.getMinutes())}}`;
        ch.dataset.idx = SHIFTS.indexOf(s);
        mc.appendChild(ch);
      }});
      row.appendChild(mc);
    }});
    mg.appendChild(row);
  }}
  mv.appendChild(mg); root.appendChild(mv);
}}

// ══════════════════════════════════════
// 週・日ビュー (既存)
// ══════════════════════════════════════
function renderWeek() {{
  const ws=new Date(cur); ws.setDate(ws.getDate()-ws.getDay());
  const we=new Date(ws); we.setDate(we.getDate()+6);
  $$('plbl').textContent = `${{ws.getFullYear()}}年${{ws.getMonth()+1}}/${{ws.getDate()}} - ${{we.getMonth()+1}}/${{we.getDate()}}`;
  const td=tod(), fil=getFil();
  const root=$$('cal'); root.innerHTML='';
  const wv=mk('div','wv');
  const whdr=mk('div','whdr'); whdr.appendChild(mk('div','wcrn'));
  for(let i=0;i<7;i++){{
    const d=new Date(ws); d.setDate(d.getDate()+i); const ds=fmt(d), dow=d.getDay();
    const hd=mk('div',`whd${{ds===td?' tod':''}}${{dow===0?' sun':dow===6?' sat':''}}${{clip?' pmode':''}}${{pasteDates.has(ds)?' psel':''}}`);
    hd.dataset.date=ds; hd.innerHTML=`<div class="wdow">${{DAYS[dow]}}</div><div class="wdn">${{d.getDate()}}</div>`;
    whdr.appendChild(hd);
  }}
  wv.appendChild(whdr);
  const wb=mk('div','wbody'); const tc=mk('div','wtc');
  for(let h=0;h<24;h++){{ const ts=mk('div','wts'); ts.textContent=h?p2(h)+':00':''; tc.appendChild(ts); }}
  wb.appendChild(tc);
  const wdc=mk('div','wdc');
  for(let i=0;i<7;i++){{
    const d=new Date(ws); d.setDate(d.getDate()+i); const ds=fmt(d);
    const col=mk('div',`wdcol${{ds===td?' tod':''}}${{clip?' pmode':''}}${{pasteDates.has(ds)?' psel':''}}`);
    col.dataset.date=ds; if(!clip) col.dataset.openreg=ds;
    for(let h=0;h<24;h++) col.appendChild(mk('div','whs'));
    const dayS=shOn(ds,fil).map(s=>({{...s,sm:sMins(s),em:eMins(s)}}));
    calcLanes(dayS).forEach(s=>col.appendChild(mkBlock(s,true,0,s.lane,s.total)));
    if(!clip) setupDragWeek(col, ds);
    wdc.appendChild(col);
  }
  wb.appendChild(wdc); wv.appendChild(wb); root.appendChild(wv);
}}

function renderDay() {{
  const ds=fmt(cur), td=tod(), fil=getFil(), y=cur.getFullYear(), mo=cur.getMonth()+1, d=cur.getDate(), dow=cur.getDay();
  $$('plbl').textContent=`${{y}}年${{mo}}月${{d}}日（${{DAYS[dow]}}）`;
  const staff=$$('fstaff').value?[$$('fstaff').value]:STAFF;
  const root=$$('cal'); root.innerHTML='';
  const dv=mk('div','dv'); const sh=mk('div','dshdr');
  const crn=mk('div','dcrn'); crn.innerHTML=ds===td?'<span style="color:var(--ac);font-weight:700">今日</span>':'';
  sh.appendChild(crn); staff.forEach(s=>{{ const h=mk('div','dsch'); h.textContent=s; sh.appendChild(h); }});
  dv.appendChild(sh);
  const db=mk('div','dbody'); const tc=mk('div','dtc');
  for(let h=0;h<DAY_H;h++){{ const ts=mk('div','dts'+(h===MID_H?' mid':'')); ts.textContent=h===MID_H?'翌0:00':(h>MID_H?p2(h-24)+':00':(h?p2(h)+':00':'')); tc.appendChild(ts); }}
  db.appendChild(tc);
  const sc=mk('div','dscs');
  staff.forEach(s=>{{
    const col=mk('div','dscol'); for(let h=0;h<DAY_H;h++) col.appendChild(mk('div','dhs'));
    const nz=mk('div','nzone'); nz.style.top=MID_H*HPX+'px'; nz.style.bottom='0'; col.appendChild(nz);
    col.dataset.openreg=ds; col.dataset.staff=s; if(!clip) setupDragDay(col, ds, s);
    fil.filter(x=>x.staff===s&&fmt(pd_(x.start))===ds).forEach(x=>col.appendChild(mkBlock(x,false,0,0,1)));
    sc.appendChild(col);
  }});
  db.appendChild(sc); dv.appendChild(db); root.appendChild(dv);
}}

// ══════════════════════════════════════
// 共通処理 (コピー/ペースト/イベント/他)
// ══════════════════════════════════════
function onCalClick(e) {{
  const chipEl = e.target.closest('.chip, .sb');
  if (chipEl) {{
    const idx = parseInt(chipEl.dataset.idx);
    if (!isNaN(idx)) {{ showDet(SHIFTS[idx]); return; }}
  }}
  if (clip) {{
    const dateEl = e.target.closest('[data-date]');
    if (dateEl) {{ togglePasteDate(dateEl.dataset.date); return; }}
  }}
  const regEl = e.target.closest('[data-openreg]');
  if (regEl && !clip) {{
    openReg(regEl.dataset.openreg, '', '', regEl.dataset.staff || '');
    return;
  }}
  const whdEl = e.target.closest('.whd[data-date]');
  if (whdEl && !clip) {{ cur = new Date(whdEl.dataset.date + 'T00:00:00'); setView('day'); }}
}}

function mkBlock(s, showStaff, offsetMins, lane, total) {{
  const st=pd_(s.start), et=pd_(s.end);
  const sm=st.getHours()*60+st.getMinutes()+offsetMins, em=et.getHours()*60+et.getMinutes()+offsetMins;
  const top=sm/60*HPX, ht=Math.max((em-sm)/60*HPX,16), col=deptClr(s.dept);
  const b=mk('div','sb'+(clip&&s.staff===clip.staff&&s.start===clip.start?' copied':''));
  b.style.cssText=`top:${{top}}px;height:${{ht}}px;background:${{rgba(col,.3)}};border-left:3px solid ${{col}};color:${{col}};left:${{lane*(100/total)+0.4}}%;width:${{(100/total)-0.8}}%;`;
  b.dataset.idx = SHIFTS.indexOf(s);
  b.innerHTML = `<div class="sbn">${{showStaff?s.staff:s.dept}}</div>` + (ht>26?`<div class="sbt">${{st.getHours()}}:${{p2(st.getMinutes())}}-${{et.getHours()}}:${{p2(et.getMinutes())}}</div>`:'');
  return b;
}}

function calcLanes(shifts) {{
  const sorted = [...shifts].sort((a,b)=>a.sm-b.sm); const lanes = [];
  sorted.forEach(s => {{
    let l=-1; for(let i=0;i<lanes.length;i++) if(lanes[i]<=s.sm){{l=i;lanes[i]=s.em;break;}}
    if(l===-1){{l=lanes.length;lanes.push(s.em);}} s.lane=l;
  }});
  sorted.forEach(s=>s.total=lanes.length); return sorted;
}}

function startCopy() {{ clip={{...curS}}; pasteDates.clear(); closeDet(); updateBanner(); renderView(); showToast('📋 コピーしました。日付を選択して貼り付け','ok'); }}
function cancelCopy() {{ clip=null; pasteDates.clear(); updateBanner(); renderView(); }}
function togglePasteDate(ds) {{
  if(pasteDates.has(ds)) pasteDates.delete(ds); else pasteDates.add(ds);
  updateBanner();
  document.querySelectorAll(`[data-date="${{ds}}"]`).forEach(el=>el.classList.toggle('psel', pasteDates.has(ds)));
}}
async function execPaste() {{
  if(!clip||!pasteDates.size)return;
  const st=pd_(clip.start), et=pd_(clip.end), sT=`${{p2(st.getHours())}}:${{p2(st.getMinutes())}}`, eT=`${{p2(et.getHours())}}:${{p2(et.getMinutes())}}`;
  const dates=[...pasteDates]; cancelCopy(); showLdg('貼り付け中...');
  for(const ds of dates){{
    await fetch(GAS+'?'+new URLSearchParams({{action:'add_shift',name:clip.staff,dept:clip.dept,start:`${{ds}} ${{sT}}`,end:`${{ds}} ${{eT}}` }}));
    SHIFTS.push({{staff:clip.staff,dept:clip.dept,start:`${{ds}}T${{sT}}:00`,end:`${{ds}}T${{eT}}:00`}});
  }}
  hideLdg(); renderView();
}}
function updateBanner() {{
  const b=$$('pbanner'); if(clip){{ b.classList.add('show'); $$('pcnt').textContent=`${{clip.staff}} / ${{pasteDates.size}}日選択`; $$('pexec').style.display=pasteDates.size?'':'none'; }} else b.classList.remove('show');
}}

function openReg(ds, st, en, staff) {{
  $$('mDate').value=ds; $$('mS').value=st||'09:00'; $$('mE').value=en||'18:00';
  if(staff) $$('mStaff').value=staff;
  $$('regOv').style.display='flex';
}}
function closeReg() {{ $$('regOv').style.display='none'; batch=[]; }}
function addBatch() {{
  const s=$$('mStaff').value, d=$$('mDept').value, dt=$$('mDate').value, st=$$('mS').value, et=$$('mE').value;
  if(!s||!d||!dt||!st||!et)return; batch.push({{staff:s,dept:d,date:dt,start:st,end:et}});
  $$('batchSec').style.display='block'; const row=mk('div','bi'); row.textContent=`${{s}} ${{dt}}`; $$('batchList').appendChild(row);
}}
async function saveAll() {{
  const items=batch.length?batch:[{{staff:$$('mStaff').value,dept:$$('mDept').value,date:$$('mDate').value,start:$$('mS').value,end:$$('mE').value}}];
  closeReg(); showLdg('保存中...');
  for(const i of items){{
    await fetch(GAS+'?'+new URLSearchParams({{action:'add_shift',name:i.staff,dept:i.dept,start:`${{i.date}} ${{i.start}}`,end:`${{i.date}} ${{i.end}}` }}));
    SHIFTS.push({{staff:i.staff,dept:i.dept,start:`${{i.date}}T${{i.start}}:00`,end:`${{i.date}}T${{i.end}}:00`}});
  }}
  hideLdg(); renderView();
}}

function showDet(s) {{
  curS=s; const st=pd_(s.start), et=pd_(s.end), col=deptClr(s.dept);
  $$('detBody').innerHTML=`<span class="dchip" style="background:${{rgba(col,.2)}};color:${{col}}">${{s.dept}}</span><div class="dr">👤 ${{s.staff}}</div><div class="dr">📅 ${{fmt(st)}}</div><div class="dr">🕐 ${{st.getHours()}}:${{p2(st.getMinutes())}} - ${{et.getHours()}}:${{p2(et.getMinutes())}}</div>`;
  $$('detOv').style.display='flex';
}}
function closeDet() {{ $$('detOv').style.display='none'; }}
async function delShift() {{
  if(!confirm('削除しますか？'))return; const s=curS; closeDet(); showLdg('削除...');
  await fetch(GAS+'?'+new URLSearchParams({{action:'del_shift',name:s.staff,dept:s.dept,start:s.start.replace('T',' '),end:s.end.replace('T',' ')}}));
  SHIFTS=SHIFTS.filter(x=>x!==s); hideLdg(); renderView();
}}

function setupDragWeek(col, ds) {{ /* ドラッグ処理 */ }}
function setupDragDay(col, ds, s) {{ /* ドラッグ処理 */ }}
function showToast(m,t){{ const o=mk('div',`toast ${{t}}`); o.textContent=m; document.body.appendChild(o); setTimeout(()=>o.remove(),3000); }}
function showLdg(m){{ const l=mk('div','ldg'); l.id='_ldg'; l.innerHTML=`<div class="spin"></div>${{m}}`; document.body.appendChild(l); }}
function hideLdg(){{ $$('_ldg')?.remove(); }}
</script>
</body>
</html>"""

    components.html(html, height=H, scrolling=False)
