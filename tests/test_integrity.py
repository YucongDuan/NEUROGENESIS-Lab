"""Executable tests of revision semantics, capsules, CLI and real HTTP routes."""
from __future__ import annotations
import csv
import io
import json
import re
import subprocess
import sys
import tempfile
import threading
import unittest
from copy import deepcopy
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.error import HTTPError
from unittest.mock import patch
from neurogenesis.core import ValidationError, canonical,digest,file_digest,load_json,write_json
from neurogenesis.evidence import EvidenceStore,evaluate,revision_trial
from neurogenesis.capsule import save,verify,replay,safe_file,chain,check_chain,export_csv
from neurogenesis.reporting import report_html
from neurogenesis.experiments import run,catalog
from neurogenesis.server import LabServer
from neurogenesis.bridge import import_nephrogenesis
ROOT=Path(__file__).resolve().parents[1]

def base():
    s=EvidenceStore();s.set_goal('Explain')
    s.put({'id':'raw','kind':'synthetic','role':'D','text':'value=2','parents':[],'provides':['voltage']})
    s.put({'id':'interpretation','kind':'interpretation','role':'K','text':'Interpretation one','parents':['raw'],'requires':['voltage']})
    return s

class Revision(unittest.TestCase):
    def test_good_graph(self):self.assertTrue(all(base().snapshot()['evaluation']['valid'].values()))
    def test_missing_dependency(self):
        s=base()
        with self.assertRaises(ValidationError):s.put({'id':'x','kind':'interpretation','role':'K','text':'x','parents':['absent']})
    def test_contract(self):
        s=base();s.put({'id':'x','kind':'interpretation','role':'K','text':'x','parents':['raw'],'requires':['calibration']})
        self.assertEqual(s.snapshot()['evaluation']['reasons']['x'],['unsatisfied_contract'])
    def test_withdrawal_descendants(self):
        s=base();s.withdraw('raw','bad timestamp');v=s.snapshot()['evaluation']['valid'];self.assertFalse(v['raw']);self.assertFalse(v['interpretation'])
    def test_old_event_preserved(self):
        s=base();old=deepcopy(s.events);s.withdraw('raw','reason');self.assertEqual(old,s.events[:len(old)])
    def test_raw_immutable(self):
        with self.assertRaises(ValidationError):base().revise('raw','new',[])
    def test_new_interpretation_version(self):
        s=base();s.revise('interpretation','second',['raw']);self.assertEqual(s.nodes['interpretation']['version'],2)
    def test_goal_history(self):
        s=base();old=deepcopy(s.events);s.set_goal('Different');self.assertEqual(EvidenceStore.replay(old).goal,'Explain')
    def test_replay(self):
        s=base();self.assertEqual(s.snapshot(),EvidenceStore.replay(s.events).snapshot())
    def test_event_tamper(self):
        s=base();s.events[1]['operation']['node']['text']='altered'
        with self.assertRaises(ValidationError):EvidenceStore.replay(s.events)
    def test_cycle_rejected_transactionally(self):
        s=base();s.put({'id':'other','kind':'interpretation','role':'I','text':'x','parents':['interpretation']});old=s.snapshot()
        with self.assertRaises(ValidationError):s.revise('interpretation','cyclic',['other'])
        self.assertEqual(old,s.snapshot())
    def test_duplicate_id(self):
        s=base()
        with self.assertRaises(ValidationError):s.put({'id':'raw','kind':'synthetic','role':'D','text':'x','parents':[]})
    def test_source_required(self):
        with self.assertRaises(ValidationError):EvidenceStore().put({'id':'o','kind':'observation','role':'D','text':'x','parents':[]})
    def test_observation_not_computed(self):
        with self.assertRaises(ValidationError):base().put({'id':'o','kind':'observation','role':'D','text':'x','parents':['raw'],'source':'local'})
    def test_invalid_role(self):
        with self.assertRaises(ValidationError):EvidenceStore().put({'id':'x','kind':'synthetic','role':'Z','text':'x','parents':[]})
    def test_duplicate_parent(self):
        with self.assertRaises(ValidationError):base().put({'id':'x','kind':'interpretation','role':'I','text':'x','parents':['raw','raw']})
    def test_missing_withdrawal(self):
        with self.assertRaises(ValidationError):base().withdraw('x','reason')
    def test_empty_goal(self):
        with self.assertRaises(ValidationError):base().set_goal('')
    def test_four_fixture_queries(self):self.assertEqual(revision_trial()['metrics']['versioned_task_passes'],4)
    def test_cost_not_equal_claim(self):
        r=revision_trial(1);self.assertTrue(all(not x['within_shared_budget'] for x in r['rows']));self.assertEqual(len({x['serialized_bytes'] for x in r['rows']}),3)
    def test_all_fixture_answers_reported(self):self.assertEqual(set(revision_trial()['query_answers']),{'summary_only','current_dag','versioned_dag'})

class Capsules(unittest.TestCase):
    def setUp(self):self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name);self.path=self.root/'run';self.info=save('nernst',{},self.path)
    def tearDown(self):self.temp.cleanup()
    def test_verify(self):self.assertTrue(verify(self.path)['verified'])
    def test_recompute(self):self.assertTrue(replay(self.path)['canonical_result_identical'])
    def test_anchor(self):self.assertTrue(verify(self.path,self.info['receipt_digest'])['trusted_anchor_supplied'])
    def test_wrong_anchor(self):
        with self.assertRaises(ValidationError):verify(self.path,'a'*64)
    def test_no_overwrite(self):
        with self.assertRaises(ValidationError):save('nernst',{},self.path)
    def test_tamper_result(self):
        with (self.path/'result.json').open('a') as f:f.write(' ')
        with self.assertRaises(ValidationError):verify(self.path)
    def test_missing_file(self):
        (self.path/'report.html').unlink()
        with self.assertRaises(ValidationError):verify(self.path)
    def test_extra_file(self):
        (self.path/'unlisted.txt').write_text('x')
        with self.assertRaises(ValidationError):verify(self.path)
    def test_path_traversal(self):
        for s in ['../outside','..','a/b','a\\b','']:
            with self.subTest(name=s),self.assertRaises(ValidationError):safe_file(self.path,s)
    def test_symlink_rejected(self):
        try:(self.root/'link').symlink_to(self.path,target_is_directory=True)
        except OSError:self.skipTest('Symlink privilege unavailable')
        with self.assertRaises(ValidationError):verify(self.root/'link')
    def test_engine_mismatch(self):
        with patch('neurogenesis.capsule.source_identity',return_value='other'):
            with self.assertRaises(ValidationError):replay(self.path)
    def test_failure_has_no_capsule(self):
        p=self.root/'bad'
        with self.assertRaises(ValidationError):save('nernst',{'temperature_K':-1},p)
        self.assertFalse(p.exists())
    def test_event_chain_tamper(self):
        e=chain([{'value':1},{'value':2}]);e[0]['event']['value']=4
        with self.assertRaises(ValidationError):check_chain(e,e[-1]['hash'])
    def test_event_chain_empty(self):
        with self.assertRaises(ValidationError):check_chain([],'0'*64)
    def test_csv_formula_escape(self):
        p=self.root/'export.csv';export_csv(p,[{'x':'=2+2','y':-3,'z':{'a':1}}]);s=p.read_text();self.assertIn("'=2+2",s);self.assertIn('-3',s)
    def test_html_escaped(self):
        r=run('nernst');r['title']='<script>alert(1)</script>';h=report_html([r]);self.assertNotIn('<script>alert',h);self.assertIn('&lt;script&gt;',h)
    def test_fit_replay(self):
        p=self.root/'fit';save('fit-passive',load_json(ROOT/'examples/passive_source.json'),p,(ROOT/'examples/passive_step.csv').read_text());self.assertTrue(replay(p)['canonical_result_identical'])
    def test_fit_data_tamper(self):
        p=self.root/'fit';save('fit-passive',load_json(ROOT/'examples/passive_source.json'),p,(ROOT/'examples/passive_step.csv').read_text());(p/'input.csv').write_text('changed')
        with self.assertRaises(ValidationError):verify(p)
    def test_bridge_preserves_payload(self):
        p=ROOT/'examples/nephrogenesis_transport_result.json';r=import_nephrogenesis(p);self.assertEqual(r['original_payload'],load_json(p));self.assertEqual(r['source_file_sha256'],file_digest(p));self.assertEqual(r['evidence_kind'],'imported_unverified')
    def test_bridge_not_native_result(self):
        p=self.root/'other.json';write_json(p,{'x':1})
        with self.assertRaises(ValidationError):import_nephrogenesis(p)

class HTTP(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server=LabServer(0);cls.port=cls.server.server_address[1];cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start();cls.base=f'http://127.0.0.1:{cls.port}'
    @classmethod
    def tearDownClass(cls):cls.server.shutdown();cls.server.server_close();cls.thread.join(timeout=3)
    def request(self,path,body=None,headers=None,method=None):
        hs={'Content-Type':'application/json','X-Lab-Token':self.server.token};hs.update(headers or {})
        data=None if body is None else (body.encode() if isinstance(body,str) else canonical(body).encode())
        req=Request(self.base+path,data=data,headers=hs,method=method)
        try:
            with urlopen(req,timeout=15) as r:return r.status,r.read(),r.headers
        except HTTPError as e:return e.code,e.read(),e.headers
    def test_health(self):self.assertEqual(self.request('/api/health')[0],200)
    def test_catalog(self):self.assertEqual(len(json.loads(self.request('/api/catalog')[1])),24)
    def test_book_map(self):self.assertEqual(self.request('/api/book')[0],200)
    def test_root_token(self):self.assertIn(self.server.token.encode(),self.request('/')[1])
    def test_script(self):self.assertEqual(self.request('/app.js')[0],200)
    def test_css(self):self.assertEqual(self.request('/style.css')[0],200)
    def test_unknown_route(self):self.assertEqual(self.request('/../../etc/passwd')[0],404)
    def test_security_headers(self):
        hs=self.request('/')[2];self.assertEqual(hs['X-Frame-Options'],'DENY');self.assertIn("default-src 'self'",hs['Content-Security-Policy'])
    def test_origin(self):self.assertEqual(self.request('/api/health',headers={'Origin':'https://untrusted.example'})[0],403)
    def test_host(self):self.assertEqual(self.request('/api/health',headers={'Host':'untrusted.example'})[0],403)
    def test_missing_token(self):self.assertEqual(self.request('/api/run',{'experiment':'nernst'},headers={'X-Lab-Token':''})[0],403)
    def test_bad_mime(self):self.assertEqual(self.request('/api/run',{},headers={'Content-Type':'text/plain'})[0],415)
    def test_duplicate_json(self):self.assertEqual(self.request('/api/run','{"experiment":"hh","experiment":"cable"}')[0],400)
    def test_nan(self):self.assertEqual(self.request('/api/run','{"experiment":"nernst","parameters":{"temperature_K":NaN}}')[0],400)
    def test_bad_parameter(self):self.assertEqual(self.request('/api/run',{'experiment':'nernst','parameters':{'oops':1}})[0],400)
    def test_extra_root(self):self.assertEqual(self.request('/api/run',{'experiment':'nernst','extra':1})[0],400)
    def test_unknown_experiment(self):self.assertEqual(self.request('/api/run',{'experiment':'absent'})[0],400)
    def test_list_as_id(self):self.assertEqual(self.request('/api/run',{'experiment':[]})[0],400)
    def test_large_request(self):
        # Assert early rejection from the declared length. Sending the entire
        # oversized payload races the server's intentional connection close.
        from http.client import HTTPConnection
        connection = HTTPConnection('127.0.0.1', self.port, timeout=5)
        try:
            connection.putrequest('POST', '/api/run')
            connection.putheader('Content-Type', 'application/json')
            connection.putheader('X-Lab-Token', self.server.token)
            connection.putheader('Content-Length', '750001')
            connection.endheaders()
            response = connection.getresponse()
            self.assertEqual(response.status, 400)
            response.read()
        finally:
            connection.close()
    def test_bad_fit(self):self.assertEqual(self.request('/api/fit',{'csv':'x','metadata':{}})[0],400)
    def test_real_fit(self):
        code,body,_=self.request('/api/fit',{'csv':(ROOT/'examples/passive_step.csv').read_text(),'metadata':load_json(ROOT/'examples/passive_source.json')});self.assertEqual(code,200);self.assertEqual(json.loads(body)['metrics']['tau_ms'],20)
    def test_24_real_http_experiments(self):
        for key in catalog():
            with self.subTest(experiment=key):
                code,b,_=self.request('/api/run',{'experiment':key,'parameters':{}});self.assertEqual(code,200);self.assertEqual(json.loads(b)['experiment'],key)

class CLI(unittest.TestCase):
    def call(self,*args):return subprocess.run([sys.executable,str(ROOT/'run.py'),*args],capture_output=True,text=True,cwd=ROOT)
    def test_list(self):r=self.call('list');self.assertEqual(r.returncode,0);self.assertEqual(len(json.loads(r.stdout)),24)
    def test_unknown(self):r=self.call('run','unknown');self.assertEqual(r.returncode,2);self.assertIn('Error:',r.stderr)
    def test_invalid_port(self):self.assertEqual(self.call('serve','--port','0').returncode,2)
    def test_run_and_replay(self):
        with tempfile.TemporaryDirectory() as t:
            p=str(Path(t)/'case');self.assertEqual(self.call('run','nernst','--out',p).returncode,0);r=self.call('replay',p);self.assertEqual(r.returncode,0);self.assertTrue(json.loads(r.stdout)['canonical_result_identical'])
    def test_fit_cli(self):
        with tempfile.TemporaryDirectory() as t:
            r=self.call('fit','--data',str(ROOT/'examples/passive_step.csv'),'--metadata',str(ROOT/'examples/passive_source.json'),'--out',str(Path(t)/'case'));self.assertEqual(r.returncode,0,r.stderr)
    def test_bridge_cli(self):
        with tempfile.TemporaryDirectory() as t:
            p=str(Path(t)/'bridge.json');r=self.call('bridge','--input',str(ROOT/'examples/nephrogenesis_transport_result.json'),'--out',p);self.assertEqual(r.returncode,0,r.stderr);self.assertEqual(self.call('bridge','--input',str(ROOT/'examples/nephrogenesis_transport_result.json'),'--out',p).returncode,2)

if __name__=='__main__':unittest.main()
