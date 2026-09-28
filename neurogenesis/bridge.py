"""Narrow read-only import of actual NEPHROGENESIS-Lab v1 result envelopes."""
from __future__ import annotations
from pathlib import Path
from .core import load_json, file_digest, ValidationError


def import_nephrogenesis(path:Path|str)->dict:
    path=Path(path);r=load_json(path)
    if not isinstance(r,dict) or not {'experiment','parameters','book_sections'}<=set(r):
        raise ValidationError('Expected a NEPHROGENESIS result envelope')
    # This is an interoperability adapter, not execution of a foreign package.
    if not isinstance(r['parameters'],dict) or not isinstance(r['book_sections'],list):raise ValidationError('Malformed source result')
    return {'format':'neurogenesis-cross-organ-record-v1','source_system':'NEPHROGENESIS-Lab',
      'source_file_sha256':file_digest(path),'source_experiment':r['experiment'],
      'source_book_sections':r['book_sections'],'original_payload':r,
      'evidence_kind':'imported_unverified','compatible_for':'side-by-side research-record inspection',
      'not_claimed':['Neural-kidney co-simulation','Shared state variables','Source run integrity','Biological or clinical validity'],
      'mapping_loss':'No automatic translation of kidney state units, controls or outcome semantics into neural variables.'}
