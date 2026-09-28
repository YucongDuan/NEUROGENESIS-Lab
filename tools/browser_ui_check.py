import sys,json,threading,re
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.error import HTTPError
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from neurogenesis.server import LabServer
from neurogenesis.experiments import catalog
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1];qa=root/'validation'/'ui_local';qa.mkdir(exist_ok=True);server=LabServer(0);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();base=f'http://127.0.0.1:{server.server_address[1]}'
report={'mode':'Original application JS/DOM with injected fetch-to-Python-HTTP test harness','direct_browser_network':'blocked_by_environment_policy','real_http':'Separately tested; harness also calls the actual server from Python','csp_in_browser':'Not tested in injected harness; headers checked in HTTP tests','experiments':[],'errors':[]}
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(headless=True,executable_path=__import__('os').environ.get('NEUROGENESIS_CHROMIUM','/usr/bin/chromium'),args=['--no-sandbox']);report['browser']=browser.version
  page=browser.new_page(viewport={'width':1440,'height':1000})
  page.on('pageerror',lambda error:report['errors'].append(str(error)))
  page.on('console',lambda message:report['errors'].append(message.text) if message.type=='error' else None)
  def bridge(source,path,options):
   headers=(options or {}).get('headers',{});headers['X-Lab-Token']=server.token
   data=(options or {}).get('body');data=data.encode() if data else None
   req=Request(base+path,data=data,headers=headers,method=(options or {}).get('method','GET'))
   try:
    with urlopen(req,timeout=20) as response:return {'status':response.status,'body':response.read().decode()}
   except HTTPError as e:return {'status':e.code,'body':e.read().decode()}
  page.expose_binding('testBridge',bridge)
  html=(root/'neurogenesis/web/index.html').read_text().replace('__TOKEN__',server.token)
  html=re.sub(r'<link[^>]+>','',html);html=re.sub(r'<script[^>]+></script>','',html)
  page.set_content(html);page.add_style_tag(content=(root/'neurogenesis/web/style.css').read_text())
  page.evaluate("() => { window.fetch=async (path,options)=>{const r=await window.testBridge(path,options||{});return {ok:r.status>=200&&r.status<300,status:r.status,json:async()=>JSON.parse(r.body)}}; }")
  page.add_script_tag(content=(root/'neurogenesis/web/app.js').read_text());page.wait_for_selector('button[data-lab="hh"]')
  for key in catalog():
   page.locator(f'button[data-lab="{key}"]').click();page.locator('#run').click();page.wait_for_function("document.getElementById('status').textContent.includes('Computed')")
   report['experiments'].append({'experiment':key,'metrics_visible':page.locator('#metrics').is_visible(),'error':page.locator('#error').inner_text()})
  page.locator('#book-tab').click();page.wait_for_selector('button[data-chapter="18"]');report['chapter_buttons']=page.locator('button[data-chapter]').count();page.locator('button[data-chapter="6"]').click();report['chapter_route_correct']='Excitable' in page.locator('#title').inner_text();page.locator('button[data-lab="hh"]').click();page.locator('#run').click();page.wait_for_function("document.getElementById('status').textContent.includes('Computed')")
  page.screenshot(path=str(qa/'desktop.png'),full_page=True)
  with page.expect_download() as download:page.locator('#download').click()
  download.value.save_as(str(qa/'browser_download.json'));report['download_ok']=json.loads((qa/'browser_download.json').read_text())['experiment']=='hh'
  page.locator('#fit-tab').click();page.locator('#csv-file').set_input_files(str(root/'examples/passive_step.csv'));page.locator('#fit-run').click();page.wait_for_selector('#result:not([hidden])')
  report['fit_metrics']=page.locator('#metrics').inner_text();report['fit_download_visible']=page.locator('#download').is_visible();page.screenshot(path=str(qa/'fit.png'),full_page=True)
  page.locator('button[data-lab="nernst"]').click();page.locator('#p-temperature_K').fill('-1');page.locator('#run').click();report['invalid_html_form_blocked']=not page.locator('#p-temperature_K').evaluate('(e)=>e.checkValidity()')
  page.set_viewport_size({'width':390,'height':844});page.locator('#reset').click();page.locator('#run').click();page.wait_for_function("document.getElementById('status').textContent.includes('Computed')")
  page.screenshot(path=str(qa/'mobile.png'),full_page=True);report['mobile_document_width']=page.evaluate('document.documentElement.scrollWidth');report['mobile_viewport_width']=390
  browser.close()
except Exception as e:report['execution_failure']=repr(e)
finally:server.shutdown();server.server_close();thread.join(timeout=3)
(root/'validation/browser.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
