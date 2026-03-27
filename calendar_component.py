import streamlit.components.v1 as components
import json
import pandas as pd

def render_calendar_component(df: pd.DataFrame, staff_list: list, dept_list: list, gas_url: str):
    # シフトデータの整理（JSON化）
    shifts_json = []
    if not df.empty:
        for idx, row in df.iterrows():
            try:
                shifts_json.append({
                    "id": int(idx),
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
    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<style>
:root {{
  --bg:#0f1117; --sf:#1a1d27; --bd:#2d3148; --tx:#e8eaf2; --tx2:#94a3b8;
  --ac:#5b8af0; --tod:rgba(91,138,240,.15); --fn:'Noto Sans JP',sans-serif;
}}
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ background:var(--bg); color:var(--tx); font-family:var(--fn); font-size:13px; height:{H}px; overflow:hidden; }}
#app {{ display:flex; flex-direction:column; height:100%; }}
#top {{ padding:10px; border-bottom:1px solid var(--bd); display:flex; align-items:center; gap:15px; }}
#nav {{ display:flex; align-items:center; gap:10px; font-weight:bold; font-size:16px; }}
.btn {{ padding:5px 12px; background:var(--sf); border:1px solid var(--bd); color:var(--tx); cursor:pointer; border-radius:4px; }}

.mv {{ flex:1; display:flex; flex-direction:column; overflow:hidden; }}
.mhdr {{ display:grid; grid-template-columns:repeat(7, 1fr); border-bottom:1px solid var(--bd); }}
.mhc {{ padding:8px; text-align:center; color:var(--tx2); font-size:11px; }}
.mgrid {{ flex:1; display:grid; grid-template-rows:repeat(6, 1fr); }}
.mrow {{ display:grid; grid-template-columns:repeat(7, 1fr); border-bottom:1px solid var(--bd); }}
.mc {{ border-right:1px solid var(--bd); padding:5px; position:relative; overflow-y:auto; }}
.mc.tod {{ background:var(--tod); }}
.dn {{ font-size:11px; margin-bottom:4px; font-weight:bold; }}

/* 合計時間表示のスタイル */
.summary-box {{
    background: rgba(91, 138, 240, 0.2);
    border: 1px solid var(--ac);
    color: #fff;
    padding: 4px;
    border-radius: 4px;
    margin-bottom: 6px;
    text-align: center;
}}
.sum-time {{ font-size: 13px; font-weight: 800; display: block; }}
.sum-label {{ font-size: 9px; opacity: 0.8; }}

.chip {{
    font-size: 10px; padding: 2px 4px; border-radius: 3px; margin-bottom: 2px;
    background: var(--sf); border-left: 3px solid var(--ac); white-space: nowrap; overflow: hidden;
}}
</style>
</head>
<body>
<div id="app">
  <div id="top">
    <div id="nav">
      <button class="btn" onclick="nav(-1)">◀</button>
      <span id="lbl"></span>
      <button class="btn" onclick="nav(1)">▶</button>
    </div>
    <button class="btn" onclick="goToday()">今日</button>
  </div>
  <div id="cal"></div>
</div>

<script>
const SHIFTS = {shifts_json_str};
let cur = new Date(); cur.setHours(0,0,0,0);

function render() {{
  const y=cur.getFullYear(), m=cur.getMonth();
  document.getElementById('lbl').textContent = `${{y}}年 ${{m+1}}月`;
  
  const root = document.getElementById('cal');
  root.innerHTML = '';
  const mv = document.createElement('div'); mv.className='mv';
  const mh = document.createElement('div'); mh.className='mhdr';
  ['日','月','火','水','木','金','土'].forEach(d=>{{
    const c=document.createElement('div'); c.className='mhc'; c.textContent=d; mh.appendChild(c);
  }});
  mv.appendChild(mh);

  const mg = document.createElement('div'); mg.className='mgrid';
  let d = new Date(y, m, 1);
  d.setDate(d.getDate() - d.getDay());

  for(let r=0; r<6; r++) {{
    const row = document.createElement('div'); row.className='mrow';
    for(let i=0; i<7; i++) {{
      const ds = d.toISOString().split('T')[0];
      const mc = document.createElement('div');
      mc.className = `mc ${{d.getMonth()!==m?'other':''}} ${{ds===new Date().toISOString().split('T')[0]?'tod':''}}`;
      mc.innerHTML = `<div class="dn">${{d.getDate()}}</div>`;
      
      const dayShifts = SHIFTS.filter(s => s.start.startsWith(ds));
      
      if(dayShifts.length > 0) {{
        // 開始時間と終了時間の最小・最大を求めて「合計時間」を作る
        const starts = dayShifts.map(s => new Date(s.start));
        const ends = dayShifts.map(s => new Date(s.end));
        const minS = new Date(Math.min(...starts));
        const maxE = new Date(Math.max(...ends));
        
        const timeStr = `${{String(minS.getHours()).padStart(2,'0')}}:${{String(minS.getMinutes()).padStart(2,'0')}} 〜 ${{String(maxE.getHours()).padStart(2,'0')}}:${{String(maxE.getMinutes()).padStart(2,'0')}}`;
        
        // まとまった時間を上に表示
        const sumBox = document.createElement('div');
        sumBox.className = 'summary-box';
        sumBox.innerHTML = `<span class="sum-label">TOTAL</span><span class="sum-time">${{timeStr}}</span>`;
        mc.appendChild(sumBox);

        // 各部門の内訳を下に並べる
        dayShifts.forEach(s => {{
          const ch = document.createElement('div');
          ch.className = 'chip';
          ch.textContent = `${{s.dept}} (${{s.start.split('T')[1].slice(0,5)}}-)`;
          mc.appendChild(ch);
        }});
      }}

      row.appendChild(mc);
      d.setDate(d.getDate() + 1);
    }
    mg.appendChild(row);
  }
  mv.appendChild(mg); root.appendChild(mv);
}}

function nav(v) {{ cur.setMonth(cur.getMonth()+v); render(); }}
function goToday() {{ cur=new Date(); render(); }}
window.onload = render;
</script>
</body>
</html>"""

    components.html(html, height=H)
