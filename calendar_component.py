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

/* 月ビュー構造 */
.mv {{ flex:1; display:flex; flex-direction:column; overflow:hidden; }}
.mhdr {{ display:grid; grid-template-columns:repeat(7, 1fr); background:var(--sf); border-bottom:1px solid var(--bd); }}
.mhc {{ padding:8px; text-align:center; color:var(--tx2); font-weight:bold; }}
.mgrid {{ flex:1; display:grid; grid-template-rows:repeat(6, 1fr); }}
.mrow {{ display:grid; grid-template-columns:repeat(7, 1fr); border-bottom:1px solid var(--bd); }}
.mc {{ border-right:1px solid var(--bd); padding:4px; overflow-y:auto; scrollbar-width:none; position:relative; }}
.mc::-webkit-scrollbar {{ display:none; }}
.mc.tod {{ background:var(--tod); }}
.dn {{ font-size:11px; font-weight:bold; margin-bottom:5px; position:sticky; top:0; background:inherit; z-index:10; }}

/* スタッフごとのまとめ枠 */
.staff-group {{
    background: rgba(255,255,255,0.03);
    border: 1px solid var(--bd);
    border-radius: 4px;
    margin-bottom: 8px;
    padding: 2px;
}}
.total-bar {{
    background: var(--ac);
    color: #000;
    font-weight: 800;
    font-size: 11px;
    padding: 2px 5px;
    border-radius: 3px;
    display: flex;
    justify-content: space-between;
    margin-bottom: 2px;
}}
.dept-chip {{
    font-size: 10px;
    padding: 1px 4px;
    color: var(--tx2);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}}
</style>
</head>
<body>
<div id="app">
  <div id="top">
    <button class="nav-btn" onclick="nav(-1)">◀</button>
    <div id="lbl" style="font-weight:bold; min-width:120px; text-align:center;"></div>
    <button class="nav-btn" onclick="nav(1)">▶</button>
    <button class="nav-btn" onclick="location.reload()" style="margin-left:auto;">更新</button>
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
      const ds = d.toISOString().split('T')[0];
      const mc = document.createElement('div');
      mc.className = `mc ${{d.getMonth()!==m?'other':''}} ${{ds===new Date().toISOString().split('T')[0]?'tod':''}}`;
      mc.innerHTML = `<div class="dn">${{d.getDate()}}</div>`;
      
      // その日のシフトをスタッフごとにグループ化
      const dayShifts = SHIFTS.filter(s => s.start.startsWith(ds));
      const groups = {{}};
      dayShifts.forEach(s => {{
        if(!groups[s.staff]) groups[s.staff] = [];
        groups[s.staff].push(s);
      }});

      // スタッフごとに表示生成
      for(const staff in groups) {{
        const sArr = groups[staff];
        const groupDiv = document.createElement('div');
        groupDiv.className = 'staff-group';

        // 開始・終了の最小最大を計算
        const times = sArr.flatMap(s => [new Date(s.start), new Date(s.end)]);
        const minS = new Date(Math.min(...times));
        const maxE = new Date(Math.max(...times));
        const tStr = `${{minS.getHours()}}:${{String(minS.getMinutes()).padStart(2,'0')}}-${{maxE.getHours()}}:${{String(maxE.getMinutes()).padStart(2,'0')}}`;

        // 合計時間バー（一番上に太く）
        const bar = document.createElement('div');
        bar.className = 'total-bar';
        bar.innerHTML = `<span>${{staff}}</span><span>${{tStr}}</span>`;
        groupDiv.appendChild(bar);

        // 各部門の内訳（小さく並べる）
        sArr.forEach(s => {{
          const chip = document.createElement('div');
          chip.className = 'dept-chip';
          chip.textContent = `・${{s.dept}}`;
          groupDiv.appendChild(chip);
        }});

        mc.appendChild(groupDiv);
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
