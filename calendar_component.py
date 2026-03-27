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

    H = 800   # コンポーネント全体の高さ(px)

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

/* ── 共通ビューパーツ ── */
.dn{{font-size:11px;font-weight:600;width:20px;height:20px;display:flex;align-items:center;justify-content:center;border-radius:50%;font-family:var(--mn);margin-bottom:2px;}}
.tod .dn{{background:var(--ac);color:#fff;}}
.mc.psel{{background:var(--sel)!important;outline:2px solid var(--cp);outline-offset:-2px;}}

/* ── 月ビュー / スタッフ週ビュー ── */
.mv{{flex:1;display:flex;flex-direction:column;overflow:hidden;min-height:0;}}
.mhdr{{display:grid;grid-template-columns:repeat(7,1fr);border-bottom:1px solid var(--bd);flex-shrink:0;}}
.mhc{{padding:6px 0;text-align:center;font-size:11px;font-weight:600;color:var(--tx2);}}
.mhc:first-child{{color:#f87171;}}.mhc:last-child{{color:#60a5fa;}}
.mgrid{{flex:1;display:grid;grid-template-rows:repeat(6,1fr);overflow-y:auto;}}
.mrow{{display:grid;grid-template-columns:repeat(7,1fr);border-bottom:1px solid var(--bd);}}
.mc{{border-right:1px solid var(--bd);padding:4px;cursor:pointer;overflow:hidden;min-height:75px;transition:background .1s;position:relative;}}
.mc:hover{{background:var(--hv);}}
.mc.other{{opacity:.3;}}.mc.tod{{background:var(--tod);}}
.mc.sun .dn{{color:#f87171;}}.mc.sat .dn{{color:#60a5fa;}}
.mmerge{{border-radius:3px;margin-bottom:2px;overflow:hidden;cursor:pointer;font-size:10px;font-weight:500;}}
.mseg{{padding:1px 4px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}}

/* スタッフ週ビュー専用 */
.sw-grid {{ display: grid; grid-template-columns: 100px repeat(7, 1fr); overflow-y: auto; flex: 1; }}
.sw-row {{ display: contents; }}
.sw-head {{ background: var(--sf); border-bottom: 1px solid var(--bd); border-right: 1px solid var(--bd); padding: 8px; font-weight: 700; text-align: center; position: sticky; top: 0; z-index: 10; }}
.sw-staff-cell {{ background: var(--sf); border-bottom: 1px solid var(--bd); border-right: 1px solid var(--bd); padding: 8px; font-weight: 600; display: flex; align-items: center; position: sticky; left: 0; z-index: 5; }}
.sw-day-cell {{ border-bottom: 1px solid var(--bd); border-right: 1px solid var(--bd); padding: 4px; min-height: 50px; cursor: pointer; }}
.sw-day-cell:hover {{ background: var(--hv); }}

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

/* ── シフトブロック ── */
.sb{{position:absolute;border-radius:4px;padding:2px 4px;font-size:10px;font-weight:600;overflow:hidden;z-index:1;cursor:pointer;transition:filter .12s;border:1px solid rgba(255,255,255,.1);}}
.sb:hover{{filter:brightness(1.25);z-index:4;}}
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
.fi,.fs2{{width:100%;padding:7px 10px;border-radius:6px;border:1px solid var(--bd);background:var(--sf2);color:var(--tx);font-size:13px;font-family:var(--fn);}}
.tr{{display:grid;grid-template-columns:1fr 18px 1fr;align-items:center;gap:5px;}}
.tsep{{color:var(--tx2);text-align:center;}}
.ma{{display:flex;gap:7px;margin-top:14px;flex-wrap:wrap;}}
.btn{{flex:1;padding:8px;border-radius:6px;border:none;font-size:13px;font-family:var(--fn);font-weight:600;cursor:pointer;transition:all .15s;min-width:72px;}}
.bp{{background:var(--ac);color:#fff;}}.bp:hover{{background:#4272d8;}}
.bs{{background:var(--sf2);color:var(--tx);border:1px solid var(--bd);}}.bs:hover{{border-color:var(--ac);color:var(--ac);}}
.be{{background:var(--wn);color:#000;flex:0;padding:8px 13px;}}.be:hover{{background:#fbbf24;}}
.bd{{background:var(--ng);color:#fff;flex:0;padding:8px 13px;}}.bd:hover{{background:#ef4444;}}
.bc{{background:rgba(240,160,91,.2);color:var(--cp);border:1px solid var(--cp);flex:0;padding:8px 13px;}}.bc:hover{{background:var(--cp);color:#000;}}

.toast{{position:fixed;bottom:16px;right:16px;padding:10px 16px;border-radius:8px;font-weight:600;font-size:12px;z-index:9999;animation:tIn .22s ease;max-width:300px;color:#fff;}}
.toast.ok{{background:var(--ok);}}.toast.err{{background:var(--ng);}}.toast.wn{{background:var(--wn);}}
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
      <button class="vt"    data-v="s-week">週(スタッフ)</button>
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
      <button class="pbb exec" id="pexec" style="display:none">実行</button>
      <button class="pbb cancel" id="pcancel">✕ キャンセル</button>
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
    <div class="mt" id="mTitle">📋 シフト登録</div>
    <input type="hidden" id="mRowIdx" value="-1">
    <input type="hidden" id="mEditMode" value="0">
    <div class="fg"><label class="fl">従業員</label><select class="fs2" id="mStaff"></select></div>
    <div class="fg"><label class="fl">部門</label><select class="fs2" id="mDept"></select></div>
    <div class="fg"><label class="fl">日付</label><input type="date" class="fi" id="mDate"></div>
    <div class="fg">
      <label class="fl">時間 (夜勤は25:00等も可)</label>
      <div class="tr">
        <input type="text" class="fi" id="mS" value="09:00">
        <div class="tsep">→</div>
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
    <div class="mt">📌 シフト詳細</div>
    <div id="detBody"></div>
    <div class="ma" style="margin-top:12px">
      <button class="btn bs" onclick="closeDet()">閉じる</button>
      <button class="btn be" onclick="openEdit()">📝 修正</button>
      <button class="btn bc" onclick="startCopy()">📋 コピー</button>
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
let clip = null, pasteDates = new Set(), curS = null;
const HPX = 48;

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
  $$('navP').onclick = () => nav(-1);
  $$('navN').onclick = () => nav(1);
  $$('tdBtn').onclick = () => {{ cur=new Date(); cur.setHours(0,0,0,0); renderView(); }};
  $$('fstaff').onchange = renderView;
  $$('fdept').onchange = renderView;
  $$('pcancel').onclick = cancelCopy;
  $$('pexec').onclick = execPaste;
  $$('cal').addEventListener('click', onCalClick);
  renderView();
}});

function setView(v) {{
  view = v;
  document.querySelectorAll('.vt').forEach(e => e.classList.toggle('on', e.dataset.v === v));
  renderView();
}}

function nav(d) {{
  if (view==='day') cur.setDate(cur.getDate()+d);
  else if (view.includes('week')) cur.setDate(cur.getDate()+d*7);
  else cur.setMonth(cur.getMonth()+d);
  renderView();
}}

function onCalClick(e) {{
  const chip = e.target.closest('.mmerge, .sb');
  if(chip) {{
    const idx = parseInt(chip.dataset.idx);
    if(!isNaN(idx)) {{ 
      if(clip) togglePasteDate(fmt(pd_(SHIFTS[idx].start)));
      else showDet(SHIFTS[idx]);
      return;
    }}
  }}
  const cell = e.target.closest('[data-date]');
  if(cell) {{
    const ds = cell.dataset.date;
    if(clip) togglePasteDate(ds);
    else openReg(ds, "09:00", "18:00", cell.dataset.staff||"");
  }}
}}

function renderView() {{
  const cal = $$('cal'); cal.innerHTML = '';
  if(view==='day') renderDay();
  else if(view==='week') renderWeek();
  else if(view==='s-week') renderStaffWeek();
  else renderMonth();
  updateBanner();
}}

// ── スタッフベース週ビュー ──
function renderStaffWeek() {{
  const ws = new Date(cur); ws.setDate(cur.getDate() - cur.getDay());
  const we = new Date(ws); we.setDate(ws.getDate()+6);
  $$('plbl').textContent = `${{fmt(ws)}} 〜`;
  const fil = getFil();
  const root = $$('cal');
  const sw = mk('div', 'sw-grid');
  sw.appendChild(mk('div', 'sw-head'));
  for(let i=0; i<7; i++) {{
    const d = new Date(ws); d.setDate(ws.getDate()+i);
    const h = mk('div', 'sw-head'); h.textContent = `${{d.getDate()}}(${{['日','月','火','水','木','金','土'][i]}})`;
    sw.appendChild(h);
  }}
  const targetStaff = $$('fstaff').value ? [$$('fstaff').value] : STAFF;
  targetStaff.forEach(s => {{
    const sc = mk('div', 'sw-staff-cell'); sc.textContent = s; sw.appendChild(sc);
    for(let i=0; i<7; i++) {{
      const d = new Date(ws); d.setDate(ws.getDate()+i); const ds = fmt(d);
      const dc = mk('div', 'sw-day-cell'); dc.dataset.date = ds; dc.dataset.staff = s;
      if(pasteDates.has(ds)) dc.classList.add('psel');
      fil.filter(x => x.staff === s && x.start.startsWith(ds)).forEach(x => {{
        const m = mk('div', 'mmerge'); const col = deptClr(x.dept);
        m.style.cssText = `border-left:3px solid ${{col}}; background:${{rgba(col,.1)}}; color:${{col}};`;
        m.innerHTML = `<div class="mseg"><b>${{x.start.split('T')[1].slice(0,5)}}</b></div>`;
        m.dataset.idx = SHIFTS.indexOf(x);
        dc.appendChild(m);
      }});
      sw.appendChild(dc);
    }}
  }});
  root.appendChild(sw);
}}

// ── ドラッグ計算用 ──
function setupDrag(col, ds, dsN, s) {{
  col.onmousedown = (e) => {{
    if(clip || e.target.closest('.sb')) return;
    const rect = col.getBoundingClientRect();
    const sy = e.clientY - rect.top + col.closest('.dbody').scrollTop;
    const sm = Math.round((sy/HPX)*4)/4*60;
    const el = mk('div', 'dragsel'); el.style.top = (sm/60*HPX)+'px'; col.appendChild(el);
    const onMove = (me) => {{
      const cy = me.clientY - rect.top + col.closest('.dbody').scrollTop;
      const em = Math.round((cy/HPX)*4)/4*60;
      el.style.top = Math.min(sm, em)/60*HPX + 'px';
      el.style.height = Math.abs(em - sm)/60*HPX + 'px';
    }};
    const onUp = (ue) => {{
      window.removeEventListener('mousemove', onMove); window.removeEventListener('mouseup', onUp);
      const cy = ue.clientY - rect.top + col.closest('.dbody').scrollTop;
      const em = Math.round((cy/HPX)*4)/4*60;
      el.remove();
      if(Math.abs(em-sm) < 15) return;
      const sMin = Math.min(sm, em), eMin = Math.max(sm, em);
      openReg(sMin >= 1440 ? dsN : ds, m2t(sMin % 1440), m2t(eMin % 1440 === 0 && eMin > 0 ? eMin : eMin % 1440), s);
    }};
    window.addEventListener('mousemove', onMove); window.addEventListener('mouseup', onUp);
  }};
}}

// ── 日跨ぎ対応保存 ──
async function saveShift() {{
  const name = $$('mStaff').value, dept = $$('mDept').value, d = $$('mDate').value;
  let sT = $$('mS').value, eT = $$('mE').value;
  const isEdit = $$('mEditMode').value === "1";
  if(!name || !dept || !d || !sT || !eT) return alert("入力不備");
  showLdg("保存中...");
  if(isEdit && curS) {{
    await fetch(GAS+'?'+new URLSearchParams({{action:'del_shift', name:curS.staff, dept:curS.dept, start:curS.start.replace('T',' ').slice(0,16), end:curS.end.replace('T',' ').slice(0,16)}}));
    SHIFTS = SHIFTS.filter(x => x !== curS);
  }}
  const res = await fetch(GAS+'?'+new URLSearchParams({{action:'add_shift', name, dept, start: `${{d}} ${{sT}}`, end: `${{d}} ${{eT}}` }}));
  if(res.ok) {{
    const data = await res.json();
    SHIFTS.push({{ rowIndex: -1, staff: name, dept: dept, start: `${{d}}T${{sT}}:00`, end: `${{d}}T${{eT}}:00` }});
    closeReg(); hideLdg(); renderView();
  }} else {{ hideLdg(); alert("保存失敗"); }}
}}

// ── ユーティリティ ──
function openReg(ds, st, en, staff) {{
  $$('mTitle').textContent = "📋 シフト登録"; $$('mEditMode').value = "0";
  $$('mDate').value = ds; $$('mS').value = st; $$('mE').value = en;
  if(staff) $$('mStaff').value = staff;
  $$('regOv').style.display = 'flex';
}}
function openEdit() {{
  const s = curS; if(!s) return; closeDet();
  $$('mTitle').textContent = "📝 シフト修正"; $$('mEditMode').value = "1";
  $$('mStaff').value = s.staff; $$('mDept').value = s.dept;
  $$('mDate').value = s.start.split('T')[0];
  $$('mS').value = s.start.split('T')[1].slice(0,5);
  $$('mE').value = s.end.split('T')[1].slice(0,5);
  $$('regOv').style.display = 'flex';
}}
function showDet(s) {{
  curS = s; const col = deptClr(s.dept);
  $$('detBody').innerHTML = `<div class="dchip" style="background:${{rgba(col,.2)}};color:${{col}}">${{s.dept}}</div><div class="dr">👤 ${{s.staff}}</div><div class="dr">🕐 ${{s.start.replace('T',' ').slice(5,16)}} 〜 ${{s.end.replace('T',' ').slice(5,16)}}</div>`;
  $$('detOv').style.display = 'flex';
}}
function getFil() {{
  const fs = $$('fstaff').value, fd = $$('fdept').value;
  return SHIFTS.filter(s => (!fs || s.staff === fs) && (!fd || s.dept === fd));
}}
function deptClr(d) {{ const i = DEPTS.indexOf(d); return CLRS[i % CLRS.length] || "#ccc"; }}
function rgba(h, a) {{ const r=parseInt(h.slice(1,3),16), g=parseInt(h.slice(3,5),16), b=parseInt(h.slice(5,7),16); return `rgba(${{r}},${{g}},${{b}},${{a}})`; }}
function closeReg() {{ $$('regOv').style.display='none'; }}
function closeDet() {{ $$('detOv').style.display='none'; curS=null; }}
function showLdg(m) {{ const l=mk('div','ldg'); l.id='_ldg'; l.innerHTML=`<div class="spin"></div><span>${{m}}</span>`; document.body.appendChild(l); }}
function hideLdg() {{ document.getElementById('_ldg')?.remove(); }}
function showToast(m, t) {{ const e=mk('div', `toast ${{t}}`); e.textContent=m; document.body.appendChild(e); setTimeout(()=>e.remove(), 3000); }}
function cancelCopy() {{ clip=null; pasteDates.clear(); renderView(); }}
function togglePasteDate(ds) {{ if(pasteDates.has(ds)) pasteDates.delete(ds); else pasteDates.add(ds); renderView(); }}
function updateBanner() {{ 
  const b = $$('pbanner'); if(clip) {{ b.classList.add('show'); $$('pcnt').textContent=`${{clip.staff}} (${{pasteDates.size}}日)`; $$('pexec').style.display=pasteDates.size>0?'':'none'; }} else b.classList.remove('show');
}}
async function execPaste() {{
  if(!clip || pasteDates.size===0) return;
  const s=clip.start.split('T')[1].slice(0,5), e=clip.end.split('T')[1].slice(0,5);
  showLdg("貼り付け中...");
  for(const d of pasteDates) {{
    await fetch(GAS+'?'+new URLSearchParams({{action:'add_shift', name:clip.staff, dept:clip.dept, start:`${{d}} ${{s}}`, end:`${{d}} ${{e}}` }}));
    SHIFTS.push({{rowIndex:-1, staff:clip.staff, dept:clip.dept, start:`${{d}}T${{s}}:00`, end:`${{d}}T${{e}}:00` }});
  }}
  cancelCopy(); hideLdg(); renderView();
}}
async function delShift() {{
  if(!curS || !confirm("削除しますか？")) return;
  const s = curS; closeDet(); showLdg("削除中...");
  await fetch(GAS+'?'+new URLSearchParams({{action:'del_shift', name:s.staff, dept:s.dept, start:s.start.replace('T',' ').slice(0,16), end:s.end.replace('T',' ').slice(0,16)}}));
  SHIFTS = SHIFTS.filter(x => x !== s); hideLdg(); renderView();
}}

// ── 各種描画 ──
function renderDay() {{
  const ds=fmt(cur), td=tod(), fil=getFil(); const nxt=new Date(cur); nxt.setDate(cur.getDate()+1); const dsN=fmt(nxt);
  $$('plbl').textContent=ds; const targetStaff = $$('fstaff').value ? [$$('fstaff').value] : STAFF;
  const dv=mk('div','dv'); const sh=mk('div','dshdr'); sh.appendChild(mk('div','dcrn'));
  targetStaff.forEach(s=>{{ const h=mk('div','dsch'); h.textContent=s; sh.appendChild(h); }}); dv.appendChild(sh);
  const db=mk('div','dbody'); const tc=mk('div','dtc');
  for(let h=0;h<30;h++) {{ const t=mk('div','dts'+(h===24?' mid':'')); t.textContent=h>=24?p2(h-24)+':00':p2(h)+':00'; tc.appendChild(t); }}
  db.appendChild(tc); const sc=mk('div','dscs');
  targetStaff.forEach(s=>{{
    const col=mk('div','dscol'); for(let h=0;h<30;h++) col.appendChild(mk('div','dhs'));
    fil.filter(x=>x.staff===s && x.start.startsWith(ds)).forEach(x=>col.appendChild(mkBlock(x,0)));
    fil.filter(x=>x.staff===s && x.start.startsWith(dsN)).forEach(x=>{{ if(pd_(x.start).getHours()<6) col.appendChild(mkBlock(x,1440)); }});
    setupDrag(col, ds, dsN, s); sc.appendChild(col);
  }});
  db.appendChild(sc); dv.appendChild(db); $$('cal').appendChild(dv);
}}

function mkBlock(s, offset) {{
  const st=pd_(s.start), et=pd_(s.end);
  const sm=st.getHours()*60+st.getMinutes()+offset;
  let em=et.getHours()*60+et.getMinutes()+offset;
  if(et.getDate()!==st.getDate()) em+=1440;
  const b=mk('div','sb'); b.dataset.idx=SHIFTS.indexOf(s); const col=deptClr(s.dept);
  b.style.cssText=`top:${{sm/60*HPX}}px;height:${{Math.max((em-sm)/60*HPX,20)}}px;background:${{rgba(col,.2)}};border-left:3px solid ${{col}};color:${{col}};width:90%;left:5%;`;
  b.innerHTML=`<div class="sbn">${{s.dept}}</div><div class="sbt">${{st.getHours()}}:${{p2(st.getMinutes())}}-</div>`;
  return b;
}}

function renderMonth() {{
  const y=cur.getFullYear(), mo=cur.getMonth(); $$('plbl').textContent=`${{y}}年${{mo+1}}月`;
  const fil=getFil(); const first=new Date(y,mo,1), sdow=first.getDay();
  const mg=mk('div','mgrid'); const mv=mk('div','mv'); const mh=mk('div','mhdr');
  ['日','月','火','水','木','金','土'].forEach(d=>{{ const c=mk('div','mhc'); c.textContent=d; mh.appendChild(c); }});
  mv.appendChild(mh);
  let d=new Date(first); d.setDate(d.getDate()-sdow);
  for(let r=0;r<6;r++) {{
    const row=mk('div','mrow');
    for(let i=0;i<7;i++) {{
      const ds=fmt(d); const mc=mk('div','mc'+(d.getMonth()!==mo?' other':'')+(ds===tod()?' tod':''));
      mc.dataset.date=ds; if(pasteDates.has(ds)) mc.classList.add('psel');
      mc.innerHTML=`<div class="dn">${{d.getDate()}}</div>`;
      fil.filter(x=>x.start.startsWith(ds)).forEach(x=>{{
        const m=mk('div','mmerge'); const col=deptClr(x.dept);
        m.style.cssText=`border-left:3px solid ${{col}};background:${{rgba(col,.1)}};color:${{col}};`;
        m.innerHTML=`<div class="mseg"><b>${{x.staff}}</b> ${{x.start.split('T')[1].slice(0,5)}}</div>`;
        m.dataset.idx=SHIFTS.indexOf(x); mc.appendChild(m);
      }});
      row.appendChild(mc); d.setDate(d.getDate()+1);
    }}
    mg.appendChild(row);
  }}
  mv.appendChild(mg); $$('cal').appendChild(mv);
}}

function renderWeek() {{
  const ws=new Date(cur); ws.setDate(cur.getDate()-cur.getDay()); $$('plbl').textContent=`${{fmt(ws)}} 〜`;
  const fil=getFil(); const root=$$('cal'); const wv=mk('div','wv'); const wh=mk('div','whdr'); wh.appendChild(mk('div','wcrn'));
  for(let i=0;i<7;i++) {{
    const d=new Date(ws); d.setDate(ws.getDate()+i); const ds=fmt(d);
    const h=mk('div','whd'); h.dataset.date=ds; h.innerHTML=`<div class="wdow">${{['日','月','火','水','木','金','土'][i]}}</div><div class="wdn">${{d.getDate()}}</div>`;
    wh.appendChild(h);
  }}
  wv.appendChild(wh); const wb=mk('div','wbody'); const tc=mk('div','wtc');
  for(let h=0;h<24;h++) {{ const t=mk('div','wts'); t.textContent=p2(h)+':00'; tc.appendChild(t); }}
  wb.appendChild(tc); const wdc=mk('div','wdc');
  for(let i=0;i<7;i++) {{
    const d=new Date(ws); d.setDate(ws.getDate()+i); const ds=fmt(d);
    const col=mk('div','wdcol'); for(let h=0;h<24;h++) col.appendChild(mk('div','whs'));
    col.dataset.date=ds; if(pasteDates.has(ds)) col.classList.add('psel');
    fil.filter(x=>x.start.startsWith(ds)).forEach(x=>col.appendChild(mkBlock(x,0)));
    wdc.appendChild(col);
  }}
  wb.appendChild(wdc); wv.appendChild(wb); root.appendChild(wv);
}}
</script>
</body>
</html>"""
    components.html(html, height=H, scrolling=False)

# Would you like me to test the Staff-based week view performance or add more filtering options?
