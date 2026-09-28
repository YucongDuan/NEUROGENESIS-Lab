"""Escaped, self-contained result reports. Full data are retained in JSON/CSV."""
from __future__ import annotations
import html
import json

def report_html(results:list[dict],title:str='NEUROGENESIS-Lab | Research results') -> str:
    h=html.escape
    parts=['<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">',
      '<title>'+h(title)+'</title><style>body{font:16px/1.6 system-ui,sans-serif;max-width:1120px;margin:40px auto;padding:0 24px;color:#1c2b3c;background:#f6f8fa}header,section{background:white;padding:24px;border:1px solid #dce4ec;border-radius:10px;margin:20px 0}h1,h2{line-height:1.2}small{color:#53657c}table{border-collapse:collapse;width:100%;font-size:13px}td,th{padding:8px;border-bottom:1px solid #dce4ec;text-align:left;overflow-wrap:anywhere}pre{overflow:auto;background:#f0f4f8;padding:12px}.scroll{overflow:auto}nav a{display:inline-block;margin:5px 12px 5px 0}a{color:#075a8c}</style></head><body>',
      '<header><small>YUCONG DUAN · BOOK COMPANION · 1.0.0</small><h1>'+h(title)+'</h1><p>This file contains precomputed research results. It does not execute Python or change model parameters. Run the local workbench for new computations.</p><p>Simulation output is not clinical evidence, a consciousness measurement, or proof of a new information field.</p><nav>']
    for j,r in enumerate(results): parts.append(f'<a href="#lab{j}">{h(r["experiment"])}</a>')
    parts.append('</nav></header>')
    for j,r in enumerate(results):
        parts.append(f'<section id="lab{j}"><small>BOOK SECTIONS {h(", ".join(r["book_sections"]))}</small><h2>{h(r["title"])}</h2><p>{h(r["question"])}</p><p>{h(r["method"])}</p><h3>Computed metrics</h3><table>')
        for k,v in r['metrics'].items():parts.append(f'<tr><th>{h(k)}</th><td>{h(str(v))}</td></tr>')
        parts.append('</table><h3>Conditions and limitations</h3>')
        for text in r['limitations']: parts.append('<p>'+h(text)+'</p>')
        for key in ['policies','models']:
            if key in r:parts.append('<pre>'+h(json.dumps(r[key],indent=2))+'</pre>')
        parts.append('<details><summary>Parameters</summary><pre>'+h(json.dumps(r['parameters'],indent=2))+'</pre></details>')
        rows=r.get('rows',[])[:30]
        if rows:
            fields=list(rows[0]);parts.append('<details><summary>First 30 rows (full data in JSON and CSV)</summary><div class="scroll"><table><tr>'+''.join('<th>'+h(x)+'</th>' for x in fields)+'</tr>')
            for row in rows:parts.append('<tr>'+''.join('<td>'+h(str(row.get(k,'')))+'</td>' for k in fields)+'</tr>')
            parts.append('</table></div></details>')
        parts.append('</section>')
    return ''.join(parts)+'</body></html>'
