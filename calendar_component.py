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

/* ── 月ビュー ── */
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
.mc.psel{{background:var(--sel)!important;outline:2px solid var(--cp);outline-offset:-2px;}}
.mc.pmode{{cursor:copy;}}
.mc.pmode:hover:not(.psel){{background:rgba(240,160,91,.1)!important;}}
.dn{{font-size:11px;font-weight:600;width:20px;height:20px;display:flex;align-items:center;justify-content:center;border-radius:50%;font-family:var(--mn);margin-bottom:2px;}}
.tod .dn{{background:var(--ac);color:#fff;}}

/* 月ビュー専用: スタッフまとめ表示 */
.m-group {{ background:rgba(255,255,255,0.03); border:1px solid var(--bd); border-radius:4px; margin-bottom:4px; overflow:hidden; }}
.m-total {{ background:var(--ac); color:#000; font-weight:800; font-size:10px; padding:1px 4px; display:flex; justify-content:space-between; }}
.m-depts {{ font-size:9px; padding:1px 4px; color:var(--tx2); line-height:1.2; }}

/* シフトチップ */
.chip{{font-size:10px;padding:1px 4px;border-radius:3px;margin-bottom:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-weight:500;cursor:pointer;}}
.chip.copied{{outline:2px solid var(--cp);}}
.mmerge{{border-radius:3px;margin-bottom:2px;overflow:hidden;cursor:pointer;font-size:10px;font-weight:500;}}
.mseg{{padding:1px 4px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}}
.mmore{{font-size:10px;color:var(--tx2);cursor:pointer;padding:1px 3px;}}
.mmore:hover{{color:var(--ac);}}

/* ── 週ビュー（時間軸） ── */
.wv{{flex:1;display:flex;flex-direction:column;overflow:hidden;min-height:0;}}
.whdr{{display:grid;grid-template-columns:50px repeat(7,1fr);border-bottom:2px solid var(--bd);background:var(--sf);flex-shrink:0;}}
.wcrn{{padding:8px 0;}}
.whd{{padding:6px 3px;text-align:center;border-left:1px solid var(--bd);cursor:pointer;transition:background .1s;}}
.whd:hover{{background:var(--hv);}}
.whd.pmode{{cursor:copy;}}
.whd.pmode:hover{{background:rgba(240,160,91,.12)!important;}}
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
.wdcol.pmode:hover{{background:rgba(240,160,91,.08)!important;}}
.wdcol.psel{{background:var(--sel)!important;}}
.whs{{height:48px;border-bottom:1px solid var(--bd);}}

/* ── スタッフ週ビュー ── */
.swv{{flex:1;display:flex;flex-direction:column;overflow:hidden;min-height:0;}}
.swhdr{{display:grid;border-bottom:2px solid var(--bd);background:var(--sf);flex-shrink:0;}}
.swcrn{{padding:8px 6px;font-size:10px;color:var(--tx2);font-weight:600;text-align:center;border-right:1px solid var(--bd);}}
.swhd{{padding:5px 3px;text-align:center;border-right:1px solid var(--bd);}}
.swhd.tod .swdn{{color:var(--ac);}}
.swhd.sun .swdow,.swhd.sun .swdn{{color:#f87171;}}
.swhd.sat .swdow,.swhd.sat .swdn{{color:#60a5fa;}}
.swdow{{font-size:9px;font-weight:600;color:var(--tx2);letter-spacing:.05em;}}
.swdn{{font-size:15px;font-weight:700;font-family:var(--mn);}}
.swgrid{{flex:1;overflow-y:auto;display:flex;flex-direction:column;}}
.swrow{{display:grid;border-bottom:1px solid var(--bd);min-height:48px;}}
.swstaff{{padding:6px 6px;font-size:11px;font-weight:600;display:flex;align-items:flex-start;border-right:1px solid var(--bd);background:var(--sf);overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}}
.swcell{{border-right:1px solid var(--bd);padding:3px;cursor:pointer;transition:background .1s;min-height:48px;overflow:hidden;}}
.swcell:hover{{background:var(--hv);}}
.swcell.tod{{background:var(--tod);}}
.swcell.pmode{{cursor:copy;}}
.swcell.pmode:hover:not(.psel){{background:rgba(240,160,91,.1)!important;}}
.swcell.psel{{background:var(--sel)!important;outline:2px solid var(--cp);outline-offset:-2px;}}
.swchip{{font-size:10px;padding:1px 4px;border-radius:3px;margin-bottom:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-weight:500;cursor:pointer;display:block;}}
.swchip:hover{{filter:brightness(1.2);}}

/* ── 日ビュー ── */
.dv{{flex:1;display:flex;flex-direction:column;overflow:hidden;min-height:0;}}
.dscroll{{flex:1;overflow:auto;min-height:0;}}
.dshdr{{display:flex;position:sticky;top:0;z-index:3;background:var(--sf);border-bottom:2px solid var(--bd);}}
.dcrn{{position:sticky;left:0;z-index:4;width:58px;min-width:58px;flex-shrink:0;padding:7px 4px;font-size:10px;color:var(--tx2);text-align:center;border-right:1px solid var(--bd);background:var(--sf);}}
.dsch{{min-width:120px;padding:6px 4px;text-align:center;border-right:1px solid var(--bd);font-weight:600;font-size:12px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}}
.dbody{{display:flex;position:relative;}}
.dtc{{position:sticky;left:0;z-index:2;width:58px;min-width:58px;flex-shrink:0;border-right:1px solid var(--bd);background:var(--sf);}}
.dts{{height:48px;padding:3px 6px 0;border-bottom:1px solid var(--bd);font-size:10px;color:var(--tx2);font-family:var(--mn);text-align:right;}}
.dts.mid{{border-top:2px solid var(--ac2);color:var(--ac2);font-weight:700;}}
.dscs{{display:flex;}}
.dscol{{min-width:120px;border-right:1px solid var(--bd);position:relative;cursor:crosshair;}}
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
.tr{{display:grid;grid-template-columns:1fr 18px 1fr 90px;align-items:center;gap:5px;}}
.tsep{{color:var(--tx2);text-align:center;}}
.ma{{display:flex;gap:7px;margin-top:14px;flex-wrap:wrap;}}
.btn{{flex:1;padding:8px;border-radius:6px;border:none;font-size:13px;font-family:var(--fn);font-weight:600;cursor:pointer;transition:all .15s;min-width:72px;}}
.bp{{background:var(--ac);color:#fff;}}.bp:hover{{background:#4272d8;}}
.bs{{background:var(--sf2);color:var(--tx);border:1px solid var(--bd);}}.bs:hover{{border-color:var(--ac);color:var(--ac);}}
.bd{{background:var(--ng);color:#fff;flex:0;padding:8px 13px;}}.bd:hover{{background:#ef4444;}}
.bc{{background:rgba(240,160,91,.2);color:var(--cp);border:1px solid var(--cp);flex:0;padding:8px 13px;}}.bc:hover{{background:var(--cp);color:#000;}}
.badd{{background:var(--ok);color:#fff;flex:0;padding:8px 13px;white-space:nowrap;}}.badd:hover{{background:#22c37e;}}
.bedit{{background:rgba(91,138,240,.2);color:var(--ac);border:1px solid var(--ac);flex:0;padding:8px 13px;}}.bedit:hover{{background:var(--ac);color:#fff;}}
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
/* 36時間表記ヒント */
.time-hint{{font-size:10px;color:var(--tx2);margin-top:3px;}}
</style>
</head>
<body>
<div id="app">

  <div id="topbar">
    <div class="vtab">
      <button class="vt on" data-v="day">日</button>
      <button class="vt"    data-v="week">週</button>
      <button class="vt"    data-v="staffweek">週/人</button>
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

<!-- 登録 / 編集モーダル -->
<div class="ov" id="regOv" style="display:none" onclick="if(event.target===this)closeReg()">
  <div class="modal">
    <div class="mt">📋 <span id="regTitle">シフト登録</span> <span id="regLbl" style="font-size:11px;color:var(--tx2);font-weight:400;"></span></div>
    <div class="fg"><label class="fl">従業員</label><select class="fs2" id="mStaff"></select></div>
    <div class="fg"><label class="fl">部門</label><select class="fs2" id="mDept"></select></div>
    <div class="fg"><label class="fl">日付</label><input type="date" class="fi" id="mDate"></div>
    <div class="fg">
      <label class="fl">時間 <span style="font-weight:400;font-size:9px;color:var(--tx2);">（日跨ぎ: 終了を25〜36時で入力）</span></label>
      <div class="tr">
        <input type="number" class="fi" id="mSH" min="0" max="23" placeholder="開始h" style="text-align:center;">
        <div class="tsep" style="font-size:9px;">:</div>
        <input type="number" class="fi" id="mSM" min="0" max="59" placeholder="分" style="text-align:center;">
        <div></div>
      </div>
      <div class="tr" style="margin-top:5px;">
        <input type="number" class="fi" id="mEH" min="0" max="36" placeholder="終了h" style="text-align:center;">
        <div class="tsep" style="font-size:9px;">:</div>
        <input type="number" class="fi" id="mEM" min="0" max="59" placeholder="分" style="text-align:center;">
        <div style="font-size:10px;color:var(--ac2);padding-left:4px;" id="nextDayLbl"></div>
      </div>
    </div>
    <div id="batchSec" style="display:none">
      <div class="dcl" id="batchCnt"></div>
      <div class="blist" id="batchList"></div>
    </div>
    <div class="ma" id="regBtns">
      <button class="btn bs" onclick="closeReg()">閉じる</button>
      <button class="btn badd" id="addBatchBtn" onclick="addBatch()">＋ リストに追加</button>
      <button class="btn bp"  onclick="saveAll()">保存</button>
    </div>
    <div style="font-size:10px;color:var(--tx2);margin-top:7px;" id="regHint">💡「リストに追加」で複数件まとめて登録できます。</div>
  </div>
</div>

<!-- 詳細モーダル -->
<div class="ov" id="detOv" style="display:none" onclick="if(event.target===this)closeDet()">
  <div class="modal">
    <div class="mt">📌 シフト詳細</div>
    <div id="detBody"></div>
    <div class="ma" style="margin-top:12px">
      <button class="btn bs" onclick="closeDet()">閉じる</button>
      <button class="btn bedit" onclick="editShift()">✏️ 編集</button>
      <button class="btn bc" onclick="startCopy()">📋 コピー</button>
      <button class="btn bd" onclick="delShift()">削除</button>
    </div>
  </div>
</div>

<script>
// ══════════════════════════════════════
// データ
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

// ══════════════════════════════════════
// 定数
// ══════════════════════════════════════
const DAYS  = ['日','月','火','水','木','金','土'];
const MONS  = ['1月','2月','3月','4月','5月','6月','7月','8月','9月','10月','11月','12月'];
const HPX   = 48;   // 1時間の高さ(px)
const DAY_H = 30;   // 日ビュー: 0〜翌6時 = 30時間
const MID_H = 24;   // 深夜境界
const MERGE_GAP = 5;

// ══════════════════════════════════════
// 状態
// ══════════════════════════════════════
let view = 'day';
let cur  = new Date(); cur.setHours(0,0,0,0);
let batch = [];
let clip  = null;
let pasteDates = new Set();
let curS = null, curI = -1;
let dragSt = null;
let editMode = false;   // 編集モードフラグ
let editOrig = null;    // 編集対象の元データ
let dragJustHappened = false;  // ドラッグ直後のクリック誤発火防止

// ══════════════════════════════════════
// 初期化
// ══════════════════════════════════════
const $$ = id => document.getElementById(id);

window.addEventListener('load', () => {{
  ['fstaff','mStaff'].forEach(id => STAFF.forEach(s => $$(id).appendChild(new Option(s,s))));
  ['fdept', 'mDept' ].forEach(id => DEPTS.forEach(d => $$(id).appendChild(new Option(d,d))));

  document.querySelector('.vtab').addEventListener('click', e => {{
    const v = e.target.dataset.v;
    if (v) setView(v);
  }});
  $$('navP').onclick = () => nav(-1);
  $$('navN').onclick = () => nav(1);
  $$('tdBtn').onclick = goToday;
  $$('fstaff').onchange = renderView;
  $$('fdept').onchange  = renderView;
  $$('pcancel').onclick = cancelCopy;
  $$('pexec').onclick   = execPaste;

  // 終了時間が24以上なら「翌日」ラベル表示
  $$('mEH').addEventListener('input', updateNextDayLabel);

  $$('cal').addEventListener('click', onCalClick);

  renderView();
}});

function updateNextDayLabel() {{
  const eh = parseInt($$('mEH').value)||0;
  $$('nextDayLbl').textContent = eh >= 24 ? `翌${{eh-24}}時` : '';
}}

// ══════════════════════════════════════
// ユーティリティ
// ══════════════════════════════════════
const mk  = (t,c) => {{ const e=document.createElement(t); if(c)e.className=c; return e; }};
const fmt = d => `${{d.getFullYear()}}-${{p2(d.getMonth()+1)}}-${{p2(d.getDate())}}`;
const p2  = n => String(n).padStart(2,'0');
const tod = () => fmt(new Date());
const pd_ = s => new Date(s);
const shOn = (ds,arr) => arr.filter(s => s.start && fmt(pd_(s.start)) === ds);
const getFil = () => {{
  const fs = $$('fstaff').value||'', fd = $$('fdept').value||'';
  return SHIFTS.filter(s => (!fs||s.staff===fs)&&(!fd||s.dept===fd));
}};
const sMins = s => {{ const d=pd_(s.start); return d.getHours()*60+d.getMinutes(); }};
const eMins = s => {{ const d=pd_(s.end);   return d.getHours()*60+d.getMinutes()||1440; }};

// 開始分から "HH:MM" を返す（36時間対応）
function m2t(m) {{
  const mm = ((m % 1440) + 1440) % 1440;
  return `${{p2(Math.floor(mm/60))}}:${{p2(mm%60)}}`;
}}

// ══════════════════════════════════════
// ビュー制御
// ══════════════════════════════════════
function setView(v) {{
  view = v;
  document.querySelectorAll('.vt').forEach(e => e.classList.toggle('on', e.dataset.v === v));
  renderView();
}}
function nav(d) {{
  if (view==='day')                    cur.setDate(cur.getDate()+d);
  else if (view==='week'||view==='staffweek') cur.setDate(cur.getDate()+d*7);
  else                                 cur.setMonth(cur.getMonth()+d);
  renderView();
}}
function goToday() {{ cur=new Date(); cur.setHours(0,0,0,0); renderView(); }}
function renderView() {{
  if (view==='day')            renderDay();
  else if (view==='week')      renderWeek();
  else if (view==='staffweek') renderStaffWeek();
  else                         renderMonth();
  updateBanner();
}}

// ══════════════════════════════════════
// イベント委任: カレンダー全体のクリック
// ══════════════════════════════════════
function onCalClick(e) {{
  const sbEl = e.target.closest('.sb');
  if (sbEl) {{
    const idx = parseInt(sbEl.dataset.idx, 10);
    if (!isNaN(idx)) {{ showDet(SHIFTS[idx]); return; }}
  }}

  // 月チップ / スタッフ週チップ クリック
  const chipEl = e.target.closest('.chip,.mseg,.swchip');
  if (chipEl) {{
    const idx = parseInt(chipEl.dataset.idx, 10);
    if (!isNaN(idx)) {{
      if (clip) {{
        // ペーストモード中は日付セル選択
        const dateEl = chipEl.closest('[data-date]');
        if (dateEl) togglePasteDate(dateEl.dataset.date);
      }} else {{
        showDet(SHIFTS[idx]);
      }}
      return;
    }}
  }}

  // ペーストモード中: data-dateを持つ要素をクリック
  if (clip) {{
    const dateEl = e.target.closest('[data-date]');
    if (dateEl) {{
      togglePasteDate(dateEl.dataset.date);
      return;
    }}
  }}

  // 通常クリック: data-openreg
  // ★ ドラッグ直後はクリックイベントを無視（時間の上書き防止）
  if (dragJustHappened) {{ dragJustHappened = false; return; }}
  const regEl = e.target.closest('[data-openreg]');
  if (regEl && !clip) {{
    const ds = regEl.dataset.openreg;
    const st = regEl.dataset.staff || '';
    openReg(ds, '', '', st, '');
    return;
  }}

  // 週ヘッダ日付クリック → 日ビューへ
  const whdEl = e.target.closest('.whd[data-date]');
  if (whdEl && !clip) {{
    cur = new Date(whdEl.dataset.date + 'T00:00:00');
    setView('day');
  }}
}}

// ══════════════════════════════════════
// コピー / ペースト
// ══════════════════════════════════════
function startCopy() {{
  clip = {{...curS}};
  pasteDates.clear();
  closeDet();
  updateBanner();
  renderView();
  showToast('📋 コピーしました。日付をクリックして選択 → 貼り付け実行', 'ok', 4000);
}}
function cancelCopy() {{
  clip = null;
  pasteDates.clear();
  updateBanner();
  renderView();
}}
function togglePasteDate(ds) {{
  if (pasteDates.has(ds)) pasteDates.delete(ds);
  else                    pasteDates.add(ds);
  updateBanner();
  document.querySelectorAll(`[data-date]`).forEach(el => {{
    el.classList.toggle('psel', pasteDates.has(el.dataset.date));
  }});
}}
async function execPaste() {{
  if (!clip || pasteDates.size === 0) return;
  const st = pd_(clip.start), et = pd_(clip.end);
  const sTime = `${{p2(st.getHours())}}:${{p2(st.getMinutes())}}`;
  const eTime = `${{p2(et.getHours())}}:${{p2(et.getMinutes())}}`;
  const dates = [...pasteDates].sort();
  const prev = clip;
  cancelCopy();
  showLdg(`${{dates.length}}日分 貼り付け中...`);
  let ok=0, fail=0;
  for (const ds of dates) {{
    try {{
      await fetch(GAS+'?'+new URLSearchParams({{
        action:'add_shift', name:prev.staff, dept:prev.dept,
        start:`${{ds}} ${{sTime}}`, end:`${{ds}} ${{eTime}}`
      }}));
      SHIFTS.push({{rowIndex:-1, staff:prev.staff, dept:prev.dept,
        start:`${{ds}}T${{sTime}}:00`, end:`${{ds}}T${{eTime}}:00`}});
      ok++;
    }} catch {{ fail++; }}
  }}
  hideLdg();
  showToast(fail===0 ? `✅ ${{ok}}日分 貼り付け完了` : `⚠️ ${{ok}}件成功/${{fail}}件失敗`, fail===0?'ok':'wn');
  renderView();
}}
function updateBanner() {{
  const b = $$('pbanner');
  if (clip) {{
    b.classList.add('show');
    const st=pd_(clip.start), et=pd_(clip.end);
    $$('pcnt').textContent =
      `${{clip.staff}} ${{p2(st.getHours())}}:${{p2(st.getMinutes())}}-${{p2(et.getHours())}}:${{p2(et.getMinutes())}} ／ ${{pasteDates.size}}日選択中`;
    const exec = $$('pexec');
    exec.style.display = pasteDates.size > 0 ? '' : 'none';
    exec.textContent = `選択した${{pasteDates.size}}日に貼り付け`;
  }} else {{
    b.classList.remove('show');
  }}
}}

// ══════════════════════════════════════
// 月ビュー
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
      const isPsel = pasteDates.has(ds);
      let cls = `mc${{cell.o?' other':''}}${{ds===td?' tod':''}}${{dow===0?' sun':dow===6?' sat':''}}`;
      if (clip) cls += ' pmode';
      if (isPsel) cls += ' psel';
      const mc = mk('div', cls);
      mc.dataset.date = ds;
      if (!clip) mc.dataset.openreg = ds;

      const dn=mk('div','dn'); dn.textContent=cell.d; mc.appendChild(dn);

      const dayS = shOn(ds, fil);
      const summary = {{}};
      dayS.forEach(s => {{
        if(!summary[s.staff]) summary[s.staff] = {{ depts: [], starts: [], ends: [], raw: [] }};
        summary[s.staff].depts.push(s.dept);
        summary[s.staff].starts.push(new Date(s.start));
        summary[s.staff].ends.push(new Date(s.end));
        summary[s.staff].raw.push(s);
      }});

      for(const staff in summary) {{
        const info = summary[staff];
        const minS = new Date(Math.min(...info.starts));
        const maxE = new Date(Math.max(...info.ends));
        const timeStr = minS.getHours() + ':' + String(minS.getMinutes()).padStart(2,'0') + '-' + maxE.getHours() + ':' + String(maxE.getMinutes()).padStart(2,'0');
        const isCopied = clip && staff === clip.staff && info.raw.some(s => s.start === clip.start);

        const groupDiv = mk('div','mmerge' + (isCopied?' copied':''));
        const col = deptClr(info.raw[0].dept);
        groupDiv.style.cssText = `border-left:3px solid ${{col}}; background:${{rgba(col,.12)}}; color:${{col}};`;
        groupDiv.dataset.date = ds;

        const hdr = mk('div','mseg');
        hdr.style.cssText = `background:${{rgba(col,.3)}}; font-weight:700;`;
        hdr.innerHTML = `<span>${{staff}}</span> <span style="float:right; font-size:9px;">${{timeStr}}</span>`;
        hdr.dataset.idx = SHIFTS.indexOf(info.raw[0]);
        groupDiv.appendChild(hdr);

        const dlst = mk('div','mseg');
        dlst.style.cssText = `font-size:9px; color:var(--tx2);`;
        dlst.textContent = info.depts.join(' / ');
        dlst.dataset.idx = SHIFTS.indexOf(info.raw[0]);
        groupDiv.appendChild(dlst);

        groupDiv.dataset.idx = SHIFTS.indexOf(info.raw[0]);
        mc.appendChild(groupDiv);
      }}

      row.appendChild(mc);
    }});
    mg.appendChild(row);
  }}
  mv.appendChild(mg); root.appendChild(mv);
}}

// ══════════════════════════════════════
// スタッフ週ビュー（新規）
// ══════════════════════════════════════
function wkStart(d) {{ const r=new Date(d); r.setDate(r.getDate()-r.getDay()); return r; }}

function renderStaffWeek() {{
  const ws=wkStart(cur), we=new Date(ws); we.setDate(we.getDate()+6);
  const [y1,m1,d1]=[ws.getFullYear(),ws.getMonth()+1,ws.getDate()];
  const [y2,m2,d2]=[we.getFullYear(),we.getMonth()+1,we.getDate()];
  $$('plbl').textContent = y1===y2
    ? `${{y1}}年${{m1}}/${{d1}}-${{m2}}/${{d2}}`
    : `${{y1}}/${{m1}}/${{d1}}-${{y2}}/${{m2}}/${{d2}}`;

  const td=tod(), fil=getFil();
  const fsv = $$('fstaff').value||'';
  const staffList = fsv ? [fsv] : STAFF;

  const root=$$('cal'); root.innerHTML='';
  const swv=mk('div','swv');

  // 列数 = 1(スタッフ名列) + 7(曜日)
  const cols = 7;
  const STAFF_COL_W = 80; // px

  // ヘッダー
  const swhdr=mk('div','swhdr');
  swhdr.style.gridTemplateColumns = `${{STAFF_COL_W}}px repeat(${{cols}},1fr)`;
  const crn=mk('div','swcrn'); crn.textContent='スタッフ'; swhdr.appendChild(crn);

  const weekDates = [];
  for(let i=0;i<7;i++) {{
    const d=new Date(ws); d.setDate(d.getDate()+i);
    weekDates.push(d);
    const ds=fmt(d), dow=d.getDay();
    const isPsel=pasteDates.has(ds);
    let cls=`swhd${{ds===td?' tod':''}}${{dow===0?' sun':dow===6?' sat':''}}${{clip?' pmode':''}}${{isPsel?' psel':''}}`;
    const hd=mk('div',cls);
    hd.dataset.date=ds;
    hd.innerHTML=`<div class="swdow">${{DAYS[dow]}}</div><div class="swdn">${{d.getDate()}}</div>`;
    swhdr.appendChild(hd);
  }}
  swv.appendChild(swhdr);

  // グリッド本体
  const swgrid=mk('div','swgrid');

  staffList.forEach(staff => {{
    const row=mk('div','swrow');
    row.style.gridTemplateColumns = `${{STAFF_COL_W}}px repeat(${{cols}},1fr)`;

    // スタッフ名列
    const nameCell=mk('div','swstaff'); nameCell.textContent=staff; row.appendChild(nameCell);

    // 各曜日セル
    weekDates.forEach(d => {{
      const ds=fmt(d), dow=d.getDay();
      const isPsel=pasteDates.has(ds);
      let cls=`swcell${{ds===td?' tod':''}}${{clip?' pmode':''}}${{isPsel?' psel':''}}`;
      const cell=mk('div',cls);
      cell.dataset.date=ds;
      if(!clip) cell.dataset.openreg=ds;
      cell.dataset.staff=staff;

      // シフト表示（月表示と同じ最小情報）
      const dayS = shOn(ds, fil).filter(s => s.staff===staff);
      dayS.forEach(s => {{
        const st=pd_(s.start), et=pd_(s.end);
        const timeStr = p2(st.getHours())+':'+p2(st.getMinutes())+'-'+p2(et.getHours())+':'+p2(et.getMinutes());
        const col=deptClr(s.dept);
        const isCopied=clip&&s.staff===clip.staff&&s.start===clip.start;
        const chip=mk('span','swchip'+(isCopied?' copied':''));
        chip.style.cssText=`background:${{rgba(col,.25)}};border-left:3px solid ${{col}};color:${{col}};`;
        chip.textContent=`${{s.dept}} ${{timeStr}}`;
        chip.dataset.idx=SHIFTS.indexOf(s);
        cell.appendChild(chip);
      }});

      row.appendChild(cell);
    }});

    swgrid.appendChild(row);
  }});

  swv.appendChild(swgrid);
  root.appendChild(swv);
}}

// ══════════════════════════════════════
// 週ビュー（時間軸）
// ══════════════════════════════════════
function calcLanes(shifts) {{
  const sorted = [...shifts].sort((a,b)=>a.sm-b.sm);
  const lanes = [];
  sorted.forEach(s => {{
    let lane=-1;
    for(let i=0;i<lanes.length;i++) {{ if(lanes[i]<=s.sm){{lane=i;lanes[i]=s.em;break;}} }}
    if(lane===-1) {{ lane=lanes.length; lanes.push(s.em); }}
    s.lane=lane;
  }});
  sorted.forEach(s=>s.total=lanes.length);
  return sorted;
}}

function renderWeek() {{
  const ws=wkStart(cur), we=new Date(ws); we.setDate(we.getDate()+6);
  const [y1,m1,d1]=[ws.getFullYear(),ws.getMonth()+1,ws.getDate()];
  const [y2,m2,d2]=[we.getFullYear(),we.getMonth()+1,we.getDate()];
  $$('plbl').textContent = y1===y2
    ? `${{y1}}年${{m1}}/${{d1}}-${{m2}}/${{d2}}`
    : `${{y1}}/${{m1}}/${{d1}}-${{y2}}/${{m2}}/${{d2}}`;
  const td=tod(), fil=getFil();
  const root=$$('cal'); root.innerHTML='';
  const wv=mk('div','wv');
  const whdr=mk('div','whdr'); whdr.appendChild(mk('div','wcrn'));

  for(let i=0;i<7;i++) {{
    const d=new Date(ws); d.setDate(d.getDate()+i);
    const ds=fmt(d), dow=d.getDay();
    const isPsel=pasteDates.has(ds);
    let cls=`whd${{ds===td?' tod':''}}${{dow===0?' sun':dow===6?' sat':''}}${{clip?' pmode':''}}${{isPsel?' psel':''}}`;
    const hd=mk('div',cls);
    hd.dataset.date=ds;
    hd.innerHTML=`<div class="wdow">${{DAYS[dow]}}</div><div class="wdn">${{d.getDate()}}</div>`;
    whdr.appendChild(hd);
  }}
  wv.appendChild(whdr);

  const wb=mk('div','wbody');
  const tc=mk('div','wtc');
  for(let h=0;h<24;h++) {{ const ts=mk('div','wts'); ts.textContent=h?p2(h)+':00':''; tc.appendChild(ts); }}
  wb.appendChild(tc);

  const wdc=mk('div','wdc');
  for(let i=0;i<7;i++) {{
    const d=new Date(ws); d.setDate(d.getDate()+i);
    const ds=fmt(d), dow=d.getDay();
    const isPsel=pasteDates.has(ds);
    let cls=`wdcol${{ds===td?' tod':''}}${{clip?' pmode':''}}${{isPsel?' psel':''}}`;
    const col=mk('div',cls);
    col.dataset.date=ds;
    if(!clip) col.dataset.openreg=ds;
    for(let h=0;h<24;h++) col.appendChild(mk('div','whs'));

    const dayS=shOn(ds,fil).map(s=>{{return{{...s,sm:sMins(s),em:eMins(s)}}}});
    calcLanes(dayS).forEach(s=>col.appendChild(mkBlock(s,true,0,s.lane,s.total)));

    if(!clip) setupDragWeek(col, ds);
    wdc.appendChild(col);
  }}
  wb.appendChild(wdc); wv.appendChild(wb); root.appendChild(wv);
}}

// ══════════════════════════════════════
// 日ビュー
// ══════════════════════════════════════
function renderDay() {{
  const y=cur.getFullYear(),mo=cur.getMonth()+1,d=cur.getDate(),dow=cur.getDay();
  $$('plbl').textContent=`${{y}}年${{mo}}月${{d}}日（${{DAYS[dow]}}）`;
  const ds=fmt(cur), td=tod(), fil=getFil();
  const nxt=new Date(cur); nxt.setDate(nxt.getDate()+1); const dsN=fmt(nxt);
  const fsv=$$('fstaff').value||'';
  const staff=fsv?[fsv]:STAFF;
  const root=$$('cal'); root.innerHTML='';

  if(!staff.length) {{
    root.innerHTML='<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;color:var(--tx2);gap:12px;"><div style="font-size:32px">👥</div><div>スタッフを登録してください</div></div>';
    return;
  }}

  const dv=mk('div','dv');
  // ── 単一スクロールコンテナ（sticky対応） ──
  const dscroll=mk('div','dscroll');

  // sticky top: スタッフ名ヘッダー
  const sh=mk('div','dshdr');
  const crn=mk('div','dcrn');
  crn.innerHTML=ds===td?'<span style="color:var(--ac);font-weight:700;font-size:11px">今日</span>':'';
  sh.appendChild(crn);
  staff.forEach(s=>{{ const h=mk('div','dsch'); h.textContent=s; sh.appendChild(h); }});
  dscroll.appendChild(sh);

  // ボディ（時間列＋スタッフ列）
  const db=mk('div','dbody');

  // sticky left: 時間列
  const tc=mk('div','dtc');
  for(let h=0;h<DAY_H;h++) {{
    const ts=mk('div','dts'+(h===MID_H?' mid':''));
    if(h===0)          ts.textContent='';
    else if(h===MID_H) ts.textContent='翌0:00';
    else if(h>MID_H)   ts.textContent=p2(h-24)+':00';
    else               ts.textContent=p2(h)+':00';
    tc.appendChild(ts);
  }}
  db.appendChild(tc);

  const sc=mk('div','dscs');
  staff.forEach(s=>{{
    const col=mk('div','dscol');
    for(let h=0;h<DAY_H;h++) col.appendChild(mk('div','dhs'));
    const nz=mk('div','nzone'); nz.style.top=MID_H*HPX+'px'; nz.style.bottom='0'; col.appendChild(nz);

    col.dataset.openreg=ds;
    col.dataset.staff=s;

    if(!clip) setupDragDay(col, ds, dsN, s);

    fil.filter(x=>x.staff===s&&x.start&&fmt(pd_(x.start))===ds)
       .forEach(x=>col.appendChild(mkBlock(x,false,0,0,1)));
    fil.filter(x=>x.staff===s&&x.start&&fmt(pd_(x.start))===dsN)
       .forEach(x=>{{ if(pd_(x.start).getHours()<(DAY_H-MID_H)) col.appendChild(mkBlock(x,false,1440,0,1)); }});
    sc.appendChild(col);
  }});
  db.appendChild(sc);

  // 現在時刻ライン（dbody基準・sticky-left分58pxオフセット）
  const now=new Date(), diff=(now-cur)/60000;
  if(diff>=0&&diff<DAY_H*60) {{
    const nl=mk('div','nowl'); nl.style.cssText=`top:${{diff/60*HPX}}px;left:58px;right:0;position:absolute;`; db.appendChild(nl);
  }}

  dscroll.appendChild(db);
  dv.appendChild(dscroll);
  root.appendChild(dv);
}}

// ══════════════════════════════════════
// シフトブロック生成
// ══════════════════════════════════════
function mkBlock(s, showStaff, offsetMins, lane, total) {{
  const st=pd_(s.start), et=pd_(s.end);
  const sm=st.getHours()*60+st.getMinutes()+offsetMins;
  const em=et.getHours()*60+et.getMinutes()+offsetMins;
  const top=sm/60*HPX, ht=Math.max((em-sm)/60*HPX,16);
  const col=deptClr(s.dept);
  const isCopied=clip&&s.staff===clip.staff&&s.start===clip.start;
  const b=mk('div','sb'+(isCopied?' copied':''));
  const W=100/total, L=lane*W;
  b.style.cssText=`top:${{top}}px;height:${{ht}}px;background:${{rgba(col,.3)}};border-left:3px solid ${{col}};color:${{col}};left:${{L+0.4}}%;width:${{W-0.8}}%;`;

  b.onclick = (e) => {{
    e.stopPropagation();
    if (clip) {{
      togglePasteDate(fmt(pd_(s.start)));
    }} else {{
      showDet(s);
    }}
  }};

  const nm=mk('div','sbn'); nm.textContent=showStaff?s.staff:s.dept; b.appendChild(nm);
  if(ht>26) {{ const tm=mk('div','sbt'); tm.textContent=`${{p2(st.getHours())}}:${{p2(st.getMinutes())}}-${{p2(et.getHours())}}:${{p2(et.getMinutes())}}`; b.appendChild(tm); }}
  // dataset.idxをセット（イベント委任用）
  b.dataset.idx = SHIFTS.indexOf(s);
  return b;
}}

// ══════════════════════════════════════
// ドラッグ
// ══════════════════════════════════════
function y2m(y) {{ return y/HPX*60; }}
function snap(m) {{ return Math.round(m/15)*15; }}

function setupDragWeek(col, dateStr) {{
  let el=null;
  col.addEventListener('mousedown', e => {{
    if(e.button||e.target.classList.contains('sb')) return;
    e.preventDefault();
    const rect=col.getBoundingClientRect();
    // ★ getBoundingClientRect()はスクロール済み位置を返すのでscrollTop加算不要
    const relY=e.clientY-rect.top;
    const sm=Math.max(0,snap(y2m(relY)));
    el=mk('div','dragsel'); el.style.top=sm/60*HPX+'px'; el.style.height='0'; col.appendChild(el);
    dragSt={{col,date:dateStr,sm,em:sm,el}};
  }});
  col.addEventListener('mousemove', e => {{
    if(!dragSt||dragSt.col!==col) return;
    const rect=col.getBoundingClientRect();
    const relY=e.clientY-rect.top;
    const em=Math.max(0,snap(y2m(relY)));
    dragSt.em=em;
    el.style.top=Math.min(dragSt.sm,em)/60*HPX+'px';
    el.style.height=Math.abs(em-dragSt.sm)/60*HPX+'px';
  }});
  col.addEventListener('mouseup', () => {{
    if(!dragSt||dragSt.col!==col) return;
    const s=Math.min(dragSt.sm,dragSt.em), en=Math.max(dragSt.sm,dragSt.em);
    el.remove(); const dt=dragSt.date; dragSt=null;
    if(en-s<5)return; // 誤クリック防止
    dragJustHappened = true;  // ★ 後続clickイベントをブロック
    openReg(dt, null, null, '', '', s, en<s+15?s+60:en);
  }});
}}

function setupDragDay(col, ds, dsN, staff) {{
  let el=null;
  col.addEventListener('mousedown', e => {{
    if(e.button||e.target.classList.contains('sb')) return;
    e.preventDefault();
    const rect=col.getBoundingClientRect();
    // ★ getBoundingClientRect()はスクロール済み位置を返すのでscrollTop加算不要
    const relY=e.clientY-rect.top;
    const sm=Math.min(Math.max(0,snap(y2m(relY))), DAY_H*60);
    el=mk('div','dragsel'); el.style.top=sm/60*HPX+'px'; el.style.height='0'; col.appendChild(el);
    dragSt={{col,ds,dsN,staff,sm,em:sm,el}};
  }});
  col.addEventListener('mousemove', e => {{
    if(!dragSt||dragSt.col!==col) return;
    const rect=col.getBoundingClientRect();
    const relY=e.clientY-rect.top;
    const em=Math.min(Math.max(0,snap(y2m(relY))), DAY_H*60);
    dragSt.em=em;
    el.style.top=Math.min(dragSt.sm,em)/60*HPX+'px';
    el.style.height=Math.abs(em-dragSt.sm)/60*HPX+'px';
  }});
  col.addEventListener('mouseup', () => {{
    if(!dragSt||dragSt.col!==col) return;
    const s=Math.min(dragSt.sm,dragSt.em), en=Math.max(dragSt.sm,dragSt.em);
    const isN=s>=1440, actualDs=isN?dragSt.dsN:dragSt.ds, stf=dragSt.staff;
    el.remove(); dragSt=null;
    if(en-s<5)return; // 誤クリック防止
    dragJustHappened = true;  // ★ 後続clickイベントをブロック
    openReg(actualDs, null, null, stf, '', s%1440, en<s+15?s+60:en);
  }});
}}
document.addEventListener('mouseup', () => {{ if(dragSt?.el) dragSt.el.remove(); dragSt=null; }});

// ══════════════════════════════════════
// 登録モーダル
// ══════════════════════════════════════
// smMins / emMins: 分単位（オプション。ドラッグ時に渡す）
function openReg(ds, stStr, enStr, staff='', dept='', smMins=null, emMins=null) {{
  editMode = false;
  editOrig = null;
  $$('regTitle').textContent = 'シフト登録';
  $$('addBatchBtn').style.display = '';
  $$('regHint').style.display = '';

  $$('mDate').value = ds || fmt(cur);

  if(smMins !== null) {{
    // ドラッグ時: 分単位から時・分を設定（36時間対応）
    $$('mSH').value = Math.floor(smMins / 60);
    $$('mSM').value = smMins % 60;
    // emMinsが1440以上なら翌日
    const totalEH = Math.floor(emMins / 60);
    $$('mEH').value = totalEH;
    $$('mEM').value = emMins % 60;
  }} else if(stStr) {{
    // 文字列 "HH:MM" から設定
    const [sh,sm2] = stStr.split(':').map(Number);
    $$('mSH').value = sh; $$('mSM').value = sm2;
    const [eh,em2] = (enStr||'18:00').split(':').map(Number);
    $$('mEH').value = eh; $$('mEM').value = em2;
  }} else {{
    $$('mSH').value=9; $$('mSM').value=0;
    $$('mEH').value=18; $$('mEM').value=0;
  }}

  updateNextDayLabel();

  if(staff) {{ const sel=$$('mStaff'); for(const o of sel.options) if(o.value===staff){{sel.value=staff;break;}} }}
  if(dept)  {{ const sel=$$('mDept');  for(const o of sel.options) if(o.value===dept) {{sel.value=dept; break;}} }}
  renderBatchUI();
  $$('regOv').style.display='flex';
}}

function closeReg() {{ $$('regOv').style.display='none'; batch=[]; editMode=false; editOrig=null; renderBatchUI(); }}

// 時・分フィールドから "YYYY-MM-DD HH:MM" を生成（日跨ぎ対応）
function getStartEnd() {{
  const ds = $$('mDate').value;
  const sh = parseInt($$('mSH').value)||0;
  const sm = parseInt($$('mSM').value)||0;
  const eh = parseInt($$('mEH').value)||0;
  const em = parseInt($$('mEM').value)||0;

  const startDt = `${{ds}} ${{p2(sh)}}:${{p2(sm)}}`;

  // 終了が24時以上なら翌日
  if(eh>=24) {{
    const nextDate = new Date(ds+'T00:00:00'); nextDate.setDate(nextDate.getDate()+1);
    const nextDs = fmt(nextDate);
    const realEH = eh-24;
    const endDt = `${{nextDs}} ${{p2(realEH)}}:${{p2(em)}}`;
    return {{startDt, endDt, valid: sh<24 && em<=59 && sm<=59}};
  }}
  const endDt = `${{ds}} ${{p2(eh)}}:${{p2(em)}}`;
  return {{startDt, endDt, valid: sh<24 && em<=59 && sm<=59 && (eh*60+em) > (sh*60+sm)}};
}}

function addBatch() {{
  const staff=$$('mStaff').value, dept=$$('mDept').value;
  const {{startDt, endDt, valid}} = getStartEnd();
  if(!staff||!dept||!$$('mDate').value){{alert('すべて入力してください');return;}}
  if(!valid){{alert('時間が不正です。終了は開始より後にしてください');return;}}
  batch.push({{staff,dept,start:startDt,end:endDt}});
  renderBatchUI();
  showToast(`➕ ${{staff}} ${{startDt.slice(11)}}-${{endDt.slice(11)}}`,'ok',1800);
}}

function renderBatchUI() {{
  const sec=$$('batchSec'), lst=$$('batchList'), cnt=$$('batchCnt'), lbl=$$('regLbl');
  if(!batch.length){{sec.style.display='none';lbl.textContent='';return;}}
  sec.style.display='block';
  lbl.textContent=`（キュー: ${{batch.length}}件）`;
  cnt.textContent=`登録予定: ${{batch.length}} 件`;
  lst.innerHTML='';
  batch.forEach((item,i)=>{{
    const row=mk('div','bi');
    const lb=mk('div','bilbl'); lb.textContent=`${{item.staff}} / ${{item.dept}} / ${{item.start}}-${{item.end.slice(11)}}`;
    const dl=mk('button','bidel'); dl.textContent='✕'; dl.onclick=()=>{{batch.splice(i,1);renderBatchUI();}};
    row.appendChild(lb); row.appendChild(dl); lst.appendChild(row);
  }});
}}

async function saveAll() {{
  // 編集モード
  if(editMode && editOrig) {{
    const staff=$$('mStaff').value, dept=$$('mDept').value;
    const {{startDt, endDt, valid}} = getStartEnd();
    if(!staff||!dept||!$$('mDate').value){{alert('すべて入力してください');return;}}
    if(!valid){{alert('時間が不正です');return;}}
   // 変更後
showLdg('更新中...'); // ← closeReg()をここから外す
const norm = iso => (iso.replace('T', ' ') + '').slice(0, 16);
const savedOrig = {...editOrig}; // ← 先にコピーを保存
let ok = false;
try {
  await fetch(...del_shift...);
  await fetch(...add_shift...);
  ok = true;
} catch(ex) { console.warn(ex); }
closeReg(); // ← awaitが全部終わった後に移動
const idx = SHIFTS.findIndex(x => x.staff === savedOrig.staff && x.dept === savedOrig.dept && x.start === savedOrig.start);
if(idx >= 0) {
  SHIFTS[idx] = {...SHIFTS[idx], staff, dept,
    start: startDt.replace(' ', 'T') + ':00',
    end:   endDt.replace(' ', 'T') + ':00'};
}
hideLdg();
    if(idx>=0) {{
      SHIFTS[idx]={{...SHIFTS[idx], staff, dept,
        start:startDt.replace(' ','T')+':00',
        end:endDt.replace(' ','T')+':00'}};
    }}
    hideLdg();
    showToast(ok?'✅ 更新しました':'⚠️ 画面更新済み（GAS側も確認してください）', ok?'ok':'wn');
    renderView();
    return;
  }}

  // 通常登録
  let items=[];
  if(batch.length>0) {{
    items=[...batch];
  }} else {{
    const staff=$$('mStaff').value, dept=$$('mDept').value;
    const {{startDt, endDt, valid}} = getStartEnd();
    if(!staff||!dept||!$$('mDate').value){{alert('すべて入力してください');return;}}
    if(!valid){{alert('時間が不正です');return;}}
    items=[{{staff,dept,start:startDt,end:endDt}}];
  }}
  closeReg(); showLdg(`${{items.length}}件 保存中...`);
  let ok=0,fail=0;
  for(const item of items) {{
    try {{
      await fetch(GAS+'?'+new URLSearchParams({{action:'add_shift',name:item.staff,dept:item.dept,
        start:item.start,end:item.end}}));
      SHIFTS.push({{rowIndex:-1,staff:item.staff,dept:item.dept,
        start:item.start.replace(' ','T')+':00',
        end:item.end.replace(' ','T')+':00'}});
      ok++;
    }} catch{{fail++;}}
  }}
  hideLdg();
  showToast(fail===0?`✅ ${{ok}}件 保存しました`:`⚠️ ${{ok}}件成功/${{fail}}件失敗`, fail===0?'ok':'wn');
  renderView();
}}

// ══════════════════════════════════════
// 詳細 / 削除 / 編集
// ══════════════════════════════════════
function showDet(s) {{
  curS=s; curI=SHIFTS.indexOf(s);
  const st=pd_(s.start), et=pd_(s.end), col=deptClr(s.dept);
  $$('detBody').innerHTML=`
    <span class="dchip" style="background:${{rgba(col,.25)}};color:${{col}}">${{s.dept}}</span>
    <div class="dr"><span class="di">👤</span><span>${{s.staff}}</span></div>
    <div class="dr"><span class="di">📅</span><span>${{fmt(st)}}</span></div>
    <div class="dr"><span class="di">🕐</span><span>${{p2(st.getHours())}}:${{p2(st.getMinutes())}} → ${{p2(et.getHours())}}:${{p2(et.getMinutes())}}</span></div>
    <div class="dr"><span class="di">⏱️</span><span>${{Math.round((et-st)/60000)}}分</span></div>`;
  $$('detOv').style.display='flex';
}}
function closeDet() {{ $$('detOv').style.display='none'; curS=null; }}

function editShift() {{
  if(!curS) return;
  // ★ closeDet()がcurS=nullにするので先にデータを保存
  const staffName = curS.staff;
  const deptName  = curS.dept;
  editMode=true; editOrig={{...curS}};
  const st=pd_(curS.start), et=pd_(curS.end);
  closeDet(); // ← ここでcurS=nullになる

  $$('regTitle').textContent = 'シフト編集';
  $$('addBatchBtn').style.display='none';
  $$('regHint').style.display='none';

  $$('mDate').value = fmt(st);
  $$('mSH').value = st.getHours();
  $$('mSM').value = st.getMinutes();
  // 終了が翌日なら36時間表記に（DAY_H=30時間対応）
  const diffMins = (et - st) / 60000;
  if(diffMins > 23*60) {{
    $$('mEH').value = et.getHours() + 24;
  }} else {{
    $$('mEH').value = et.getHours();
  }}
  $$('mEM').value = et.getMinutes();
  updateNextDayLabel();

  // ★ curSではなく事前保存したstaffName/deptNameを使用
  const sel1=$$('mStaff'); for(const o of sel1.options) if(o.value===staffName){{sel1.value=staffName;break;}}
  const sel2=$$('mDept');  for(const o of sel2.options) if(o.value===deptName) {{sel2.value=deptName; break;}}

  renderBatchUI();
  $$('regOv').style.display='flex';
}}

async function delShift() {{
  if(!curS||!confirm(`${{curS.staff}} のシフトを削除しますか？`)) return;
  const s=curS; closeDet(); showLdg('削除中...');
  const norm=iso=>(iso.replace('T',' ')+'').slice(0,16);
  let ok=false;
  try {{
    const r=await fetch(GAS+'?'+new URLSearchParams({{action:'del_shift',name:s.staff,dept:s.dept,
      start:norm(s.start),end:norm(s.end)}}));
    const t=await r.text();
    ok=r.ok&&(t.includes('delet')||t.includes('ok')||t.trim().length===0);
  }} catch(ex){{console.warn(ex);}}
  const i=curI>=0?curI:SHIFTS.findIndex(x=>x.staff===s.staff&&x.dept===s.dept&&x.start===s.start);
  if(i>=0) SHIFTS.splice(i,1);
  hideLdg();
  showToast(ok?'🗑️ 削除しました':'🗑️ 画面から削除（GAS側も確認してください）', ok?'ok':'wn');
  renderView();
}}

// ══════════════════════════════════════
// ヘルパー
// ══════════════════════════════════════
function showToast(msg,type='ok',dur=3200) {{
  const t=mk('div',`toast ${{type}}`); t.textContent=msg;
  document.body.appendChild(t); setTimeout(()=>t.remove(),dur);
}}
function showLdg(msg='処理中...') {{
  const l=mk('div','ldg'); l.id='_ldg';
  l.innerHTML=`<div class="spin"></div><span>${{msg}}</span>`;
  document.body.appendChild(l);
}}
function hideLdg() {{ document.getElementById('_ldg')?.remove(); }}

document.addEventListener('keydown', e => {{
  if(e.key==='Escape') {{
    if(clip) {{ cancelCopy(); return; }}
    closeReg(); closeDet();
  }}
  if(!e.target.matches('input,select,textarea')) {{
    if(e.key==='ArrowLeft')  nav(-1);
    if(e.key==='ArrowRight') nav(1);
  }}
}});
</script>
</body>
</html>"""

    components.html(html, height=H, scrolling=False)
