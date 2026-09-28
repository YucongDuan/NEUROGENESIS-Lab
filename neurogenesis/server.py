"""Loopback-only workbench. No uploads to third parties or hardware interfaces.

This is a local research UI, not a hardened multi-user web deployment.
"""
from __future__ import annotations
import hmac
import secrets
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from .core import ValidationError, loads, canonical, keys
from .experiments import catalog, run
from .calibration import fit_csv

class LabServer(ThreadingHTTPServer):
    daemon_threads=True
    def __init__(self, port:int=8766):
        self.token=secrets.token_urlsafe(32)
        super().__init__(('127.0.0.1',port), Handler)

class Handler(BaseHTTPRequestHandler):
    server_version='NEUROGENESIS/1.0'
    def log_message(self,*args):pass # do not retain research inputs in an access log
    def _origin_ok(self):
        port=self.server.server_address[1]
        hosts={f'127.0.0.1:{port}',f'localhost:{port}'}
        host=self.headers.get('Host','')
        origin=self.headers.get('Origin')
        return host in hosts and (origin is None or origin in {f'http://{h}' for h in hosts})
    def _send(self,code,body:bytes,mime='application/json; charset=utf-8'):
        self.send_response(code);self.send_header('Content-Type',mime);self.send_header('Content-Length',str(len(body)))
        self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Referrer-Policy','no-referrer');self.send_header('X-Frame-Options','DENY')
        self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'")
        self.end_headers();self.wfile.write(body)
    def _json(self,code,obj):self._send(code,canonical(obj).encode())
    def do_GET(self):
        if not self._origin_ok():return self._json(403,{'error':'Host or Origin rejected'})
        if self.path=='/api/catalog':return self._json(200,catalog())
        if self.path=='/api/book':
            from .core import load_json
            return self._json(200,load_json(Path(__file__).parent/'data/book_map.json'))
        if self.path=='/api/health':return self._json(200,{'status':'ok','version':'1.0.0'})
        routes={'/':('index.html','text/html; charset=utf-8'),'/app.js':('app.js','text/javascript; charset=utf-8'),'/style.css':('style.css','text/css; charset=utf-8')}
        if self.path not in routes:return self._json(404,{'error':'Unknown route'})
        name,mime=routes[self.path];text=(Path(__file__).parent/'web'/name).read_text()
        if name=='index.html':text=text.replace('__TOKEN__',self.server.token)
        self._send(200,text.encode(),mime)
    def do_POST(self):
        if not self._origin_ok():return self._json(403,{'error':'Host or Origin rejected'})
        token=self.headers.get('X-Lab-Token','')
        if not hmac.compare_digest(token,self.server.token):return self._json(403,{'error':'Session token rejected'})
        if self.path not in {'/api/run','/api/fit'}:return self._json(404,{'error':'Unknown route'})
        if self.headers.get_content_type()!='application/json':return self._json(415,{'error':'Expected application/json'})
        try:
            length=int(self.headers.get('Content-Length','0'))
            if not 0<length<=750000:raise ValidationError('Request must be non-empty and at most 750 kB')
            body=loads(self.rfile.read(length).decode('utf-8'))
            if self.path=='/api/run':
                keys(body,{'experiment','parameters'},{'experiment'})
                result=run(body['experiment'],body.get('parameters',{}))
            else:
                keys(body,{'csv','metadata'},{'csv','metadata'});result=fit_csv(body['csv'],body['metadata'])
            self._json(200,result)
        except (ValidationError,UnicodeError,ValueError,TypeError,KeyError) as exc:self._json(400,{'error':str(exc)})
        except Exception:self._json(500,{'error':'Unexpected internal failure; no result was accepted'})


def serve(port:int=8766):
    server=LabServer(port)
    print(f'NEUROGENESIS-Lab: http://127.0.0.1:{server.server_address[1]}',flush=True)
    print('Local research only. Press Ctrl+C to stop. No device or cloud connections.',flush=True)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()
