"""Experiment capsules with exclusive-path writes and cleanup: artifact integrity, event binding and actual replay."""
from __future__ import annotations
import csv
import hashlib
import json
import os
import platform
from pathlib import Path
import shutil
import tempfile
from . import __version__
from .core import ValidationError, canonical, digest, file_digest, load_json, write_json, source_identity, numerical_equal, keys
from .experiments import run
from .calibration import fit_csv
from .reporting import report_html


def safe_file(root:Path,name:str)->Path:
    if not isinstance(name,str) or not name or name in {'.','..'} or '/' in name or '\\' in name:
        raise ValidationError('Unsafe capsule filename')
    p=root/name
    if p.is_symlink() or p.resolve().parent!=root.resolve(): raise ValidationError('Symlinks and path escapes are not accepted')
    return p


def chain(events:list[dict])->list[dict]:
    out=[]; previous='0'*64
    for idx,event in enumerate(events):
        row={'sequence':idx,'previous':previous,'event':event}; previous=digest(row)
        out.append({**row,'hash':previous})
    return out


def check_chain(events:list[dict],head:str)->None:
    previous='0'*64
    for idx,row in enumerate(events):
        keys(row,{'sequence','previous','event','hash'},{'sequence','previous','event','hash'})
        body={k:row[k] for k in ['sequence','previous','event']}
        if row['sequence']!=idx or row['previous']!=previous or digest(body)!=row['hash']:
            raise ValidationError('Broken event chain')
        previous=row['hash']
    if not events or previous!=head:raise ValidationError('Incorrect event head')


def export_csv(path:Path,rows:list[dict])->None:
    if not rows:return
    fields=list(dict.fromkeys(k for r in rows for k in r))
    def safe(v):
        if isinstance(v,(dict,list)):return canonical(v)
        if isinstance(v,str) and v.startswith(('=','+','-','@','\t','\r')):return "'"+v
        return v
    with path.open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader()
        for row in rows:writer.writerow({k:safe(v) for k,v in row.items()})


def save(name:str,parameters:dict,out:Path|str,csv_text:str|None=None)->dict:
    out=Path(out)
    if out.exists() or out.is_symlink():raise ValidationError('Capsules never overwrite an existing path; choose a new directory')
    result=fit_csv(csv_text,parameters) if name=='fit-passive' and csv_text is not None else run(name,parameters)
    protocol={'format':'neurogenesis-protocol-v1','experiment':name,'parameters':result['parameters'],
          'engine_digest':source_identity(),'software_version':__version__,'python':platform.python_version(),'platform':platform.platform()}
    if csv_text is not None: protocol['data_sha256']=hashlib.sha256(csv_text.encode()).hexdigest()
    events=chain([{'role':'P','action':'declare_question','question':result['question']},
           {'role':'D','action':'bind_input','protocol_digest':digest(protocol),'source_kind':result['source_kind']},
           {'role':'I','action':'bind_units_and_sections','sections':result['book_sections']},
           {'role':'K','action':'execute','result_digest':digest(result)},
           {'role':'W','action':'retain_omissions','limitations':result['limitations']},
           {'role':'P','action':'invite_disconfirmation','next':'Change an assumption, add independent evidence or replace the model.'}])
    out.parent.mkdir(parents=True,exist_ok=True)
    temp=Path(tempfile.mkdtemp(prefix='.neuro-capsule-',dir=out.parent))
    try:
        write_json(temp/'protocol.json',protocol);write_json(temp/'result.json',result)
        (temp/'events.jsonl').write_text(''.join(canonical(e)+'\n' for e in events),encoding='utf-8')
        (temp/'report.html').write_text(report_html([result]),encoding='utf-8')
        export_csv(temp/'data.csv',result['rows'])
        # Preserve the exact UTF-8 bytes used for the protocol digest on every
        # platform.  ``Path.write_text`` applies newline translation on
        # Windows, which would otherwise make a valid recording fail its own
        # integrity check after checkout.
        if csv_text is not None:(temp/'input.csv').write_bytes(csv_text.encode('utf-8'))
        receipt={'format':'neurogenesis-capsule-v1','engine_digest':protocol['engine_digest'],'event_head':events[-1]['hash'],
          'files':{p.name:file_digest(p) for p in sorted(temp.iterdir())},
          'trust_model':'Unkeyed hashes. Preserve receipt_digest independently; no signature or external timestamp is supplied.'}
        write_json(temp/'receipt.json',receipt)
        # mkdir is the exclusive publication reservation; copy is followed by an integrity check.
        out.mkdir()
        try:
            for p in temp.iterdir():shutil.move(str(p),str(out/p.name))
            verify(out)
        except Exception:
            shutil.rmtree(out);raise
    finally:shutil.rmtree(temp,ignore_errors=True)
    return {'path':str(out),'receipt_digest':digest(receipt),'result_digest':digest(result)}


def verify(root:Path|str,trusted_digest:str|None=None)->dict:
    root=Path(root)
    if root.is_symlink() or not root.is_dir():raise ValidationError('Capsule must be a real directory')
    receipt=load_json(safe_file(root,'receipt.json'));keys(receipt,{'format','engine_digest','event_head','files','trust_model'},{'format','engine_digest','event_head','files','trust_model'})
    if receipt['format']!='neurogenesis-capsule-v1':raise ValidationError('Unknown capsule format')
    if trusted_digest is not None and digest(receipt)!=trusted_digest:raise ValidationError('External receipt anchor does not match')
    files=receipt['files'];required={'protocol.json','result.json','events.jsonl','report.html'}
    if not isinstance(files,dict) or not required<=set(files) or set(files)-required-{'data.csv','input.csv'}:
        raise ValidationError('Invalid capsule inventory')
    if {p.name for p in root.iterdir()} != set(files)|{'receipt.json'}:raise ValidationError('Unlisted or missing capsule artifact')
    for name,expected in files.items():
        p=safe_file(root,name)
        if not p.is_file() or file_digest(p)!=expected:raise ValidationError(f'File changed: {name}')
    from .core import loads
    events=[loads(s) for s in safe_file(root,'events.jsonl').read_text().splitlines()]
    check_chain(events,receipt['event_head'])
    protocol=load_json(root/'protocol.json');result=load_json(root/'result.json')
    if len(events)!=6 or events[1]['event'].get('protocol_digest')!=digest(protocol) or events[3]['event'].get('result_digest')!=digest(result):
        raise ValidationError('Events do not bind this protocol and result')
    if protocol['engine_digest']!=receipt['engine_digest']:raise ValidationError('Engine identity mismatch')
    if protocol['experiment']=='fit-passive':
        if 'input.csv' not in files or file_digest(root/'input.csv')!=protocol.get('data_sha256'):raise ValidationError('Input recording is not bound')
    return {'verified':True,'receipt_digest':digest(receipt),'trusted_anchor_supplied':trusted_digest is not None,
            'engine_matches':source_identity()==receipt['engine_digest']}


def replay(root:Path|str,trusted_digest:str|None=None)->dict:
    root=Path(root);checked=verify(root,trusted_digest)
    if not checked['engine_matches']:raise ValidationError('Engine or catalogue changed; retain the original release or create a new run')
    p=load_json(root/'protocol.json');old=load_json(root/'result.json')
    new=fit_csv((root/'input.csv').read_text(),p['parameters']) if p['experiment']=='fit-passive' else run(p['experiment'],p['parameters'])
    return {**checked,'recomputed':True,'numerically_equal':numerical_equal(old,new),
            'canonical_result_identical':digest(old)==digest(new),'rtol':1e-9,'atol':1e-12}
