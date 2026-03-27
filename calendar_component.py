import streamlit.components.v1 as components
import json
import pandas as pd

def render_calendar_component(df: pd.DataFrame, staff_list: list, dept_list: list, gas_url: str):
    shifts_json = []
    if not df.empty:
        for idx, row in df.iterrows():
            try:
                shifts_json.append({
                    "idx": int(idx),
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
    # Pythonのf-string内では、CSSやJSの { } は {{ }} と書かないとSyntaxErrorになります
    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
:root {{
  --bg:#0f1117; --sf:#1a1d27; --bd:#2d3148; --tx:#e8eaf2; --tx2:#94a3b8;
  --ac:#5b8af0; --tod:rgba(91,138,240,.12); --fn:'Noto Sans JP',sans-serif;
}}
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ background:var(--bg); color:var(--tx); font-family:var(--fn); font-size:12px; height:{H}px; overflow:hidden; }}
#app {{ display:flex; flex-direction:column; height:100%; }}
#top {{ padding:10px; border-bottom:1px solid var(--bd); display:flex; align-items:center; gap:10px; background:var(--sf); }}
.nav-btn {{ padding:4px 10px; background:var(--bd); border:none; color:#fff; cursor:pointer; border-radius:4px; }}

.mv {{ flex:1; display:flex; flex-direction:column; overflow:hidden; }}
.mhdr {{ display:grid; grid-template-columns:repeat(7, 1fr); background:var(--sf); border-bottom:1px solid var(--bd); }}
.mhc {{ padding:8px; text-align:center; color:var(--tx2); font-weight:bold; }}
.mgrid {{ flex:1; display:grid; grid-template-rows:repeat(6, 1fr); }}
.mrow {{ display:grid; grid-template-columns:repeat(7, 1fr); border-bottom:1px solid var(--bd); }}
.mc {{ border-right:1px solid var(--bd); padding:4px; overflow-y:auto; scrollbar-width:none; position:relative; min-height:100px; }}
.mc::-webkit-scrollbar {{ display:none; }}
.mc.tod {{ background:var(--tod); }}
.dn {{ font-size:11px; font-weight:bold; margin-bottom:5px; position:sticky; top:0; background:inherit; z-index:10; }}

/* 合計表示のスタイル */
.staff-summary {{
    background: rgba(91, 138, 240, 0.1);
    border: 1px solid rgba(91, 138, 240, 0.3);
    border-radius: 4px;
    margin-bottom: 6px;
    overflow: hidden;
}}
.total-time-bar {{
    background: var(--ac);
    color: #000;
    padding: 2px 4px;
    font-weight: 800;
    font-size: 10px;
    display: flex;
    justify-content: space-between;
}}
.dept-list {{
    padding: 2px 4px;
    font-size: 9px;
    color: var(--tx2);
    line-height: 1.2;
}}
.other {{ opacity: 0.3; }}
</style>
</head>
<body>
<div id="app">
  <div id="top">
    <button class="nav-btn" onclick="nav(-1)">◀</button>
    <div id="lbl" style="font-weight:bold; min-width:120px; text-align:center;"></div>
    <button class="nav-btn" onclick="nav(1)">▶</button>
  </div>
  <div id="cal"></div>
</div>

<script>
const SHIFTS = {shifts_json_str};
let cur = new Date(); cur.setHours(0,0,0,0);

function render() {{
  const y=cur.getFullYear(), m=cur.getMonth();
  document.getElementById('lbl').textContent = `${{y}}年 ${{m+1}}月`;
  const root = document.getElementById('cal'); root.innerHTML = '';
  
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
      const ds = d.getFullYear() + '-' + String(d.getMonth()+1).padStart(2,'0') + '-' + String(d.getDate()).padStart(2,'0');
      const mc = document.createElement('div');
      mc.className = `mc ${{d.getMonth()!==m?'other':''}} ${{ds===(new Date().toISOString().split('T')[0])?'tod':''}}`;
      mc.innerHTML = `<div class="dn">${{d.getDate()}}</div>`;
      
      const dayShifts = SHIFTS.filter(s => s.start.startsWith(ds));
      
      // スタッフごとに集計
      const summary = {{}};
      dayShifts.forEach(s => {{
        if(!summary[s.staff]) summary[s.staff] = {{ depts: [], starts: [], ends: [] }};
        summary[s.staff].depts.push(s.dept);
        summary[s.staff].starts.push(new Date(s.start));
        summary[s.staff].ends.push(new Date(s.end));
      }});

      for(const staff in summary) {{
        const info = summary[staff];
        const minS = new Date(Math.min(...info.starts));
        const maxE = new Date(Math.max(...info.ends));
        const timeStr = minS.getHours() + ':' + String(minS.getMinutes()).padStart(2,'0') + '-' + maxE.getHours() + ':' + String(maxE.getMinutes()).padStart(2,'0');

        const box = document.createElement('div');
        box.className = 'staff-summary';
        box.innerHTML = `
          <div class="total-time-bar">
            <span>${{staff}}</span>
            <span>${{timeStr}}</span>
          </div>
          <div class="dept-list">${{info.depts.join(' / ')}}</div>
        `;
        mc.appendChild(box);
      }}

      row.appendChild(mc);
      d.setDate(d.getDate() + 1);
    }
    mg.appendChild(row);
  }
  mv.appendChild(mg); root.appendChild(mv);
}}

function nav(v) {{ cur.setMonth(cur.getMonth()+v); render(); }}
window.onload = render;
</script>
</body>
</html>"""

    components.html(html, height=H)
