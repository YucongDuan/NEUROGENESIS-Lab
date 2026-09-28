"""Verify a clean release inventory, source contracts and local integrity.

A manifest is not an externally authenticated signature. Independently retain
its digest, or the supplied archive digest, when stronger custody is needed.
"""
from __future__ import annotations
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from neurogenesis.core import ValidationError,load_json,source_identity
from neurogenesis.experiments import catalog

def ignore(p):
    return any(x in {'.git','__pycache__','.venv','runs','build'} or x.endswith('.egg-info') for x in p.parts) or p.name in {'.coverage','RELEASE_MANIFEST.json'}

def inventory(root):
    paths=[]
    for p in root.rglob('*'):
        rel=p.relative_to(root)
        if ignore(rel):continue
        if p.is_symlink():raise ValidationError(f'Symlink not accepted: {rel}')
        if p.is_file():paths.append(p)
    return {p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}

def verify(root=ROOT):
    manifest=load_json(root/'RELEASE_MANIFEST.json');actual=inventory(root)
    if manifest.get('files')!=actual:
        wanted=manifest.get('files',{})
        raise ValidationError('Release manifest mismatch: '+str({'missing':sorted(set(wanted)-set(actual)),'extra':sorted(set(actual)-set(wanted)),'changed':sorted(k for k in set(actual)&set(wanted) if actual[k]!=wanted[k])}))
    cats=catalog();book=load_json(root/'neurogenesis/data/book_map.json');refs=load_json(root/'neurogenesis/data/references.json');refids={r['id'] for r in refs}
    assert len(book['chapters'])==18 and {x['chapter'] for x in book['chapters']}==set(range(1,19))
    assert len(cats)==24
    assert all(ch['primary_experiment'] in cats for ch in book['chapters'])
    assert all(set(spec['references'])<=refids for spec in cats.values())
    return {'verified':True,'files_hashed':len(actual),'chapter_links':18,'registered_experiments':24,'engine_digest':source_identity(),'scope':'Local byte inventory and declared contracts; not source truth or external signature'}

if __name__=='__main__':
    try:print(json.dumps(verify(),indent=2))
    except (OSError,ValidationError,AssertionError) as e:print(f'FAILED: {e}',file=sys.stderr);raise SystemExit(1)
