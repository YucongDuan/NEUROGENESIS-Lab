# Python and local HTTP API

## Python

```python
from neurogenesis.experiments import run, catalog
from neurogenesis.capsule import save, verify, replay
from neurogenesis.evidence import EvidenceStore

result = run("hh", {"dt_ms": 0.0125})
print(result["metrics"])
receipt = save("hh", {"dt_ms": 0.0125}, "runs/independent-hh")
assert verify("runs/independent-hh")["verified"]
assert replay("runs/independent-hh")["numerically_equal"]
```

`run` normalizes and validates catalogue inputs before executing a model. Low-level kernel helpers are intended for developers who preserve those contracts. Results contain experiment, model_version, title, question, method, source_kind, parameters, book_sections, references, metrics, rows and limitations. Some add comparison models, policies, spike times or series metadata.

```python
s = EvidenceStore()
s.set_goal("Explain a recording")
s.put({"id": "raw", "kind": "synthetic", "role": "D", "text": "amplitude=2 mV",
       "parents": [], "provides": ["voltage"]})
s.put({"id": "claim", "kind": "interpretation", "role": "K", "text": "Initial explanation",
       "parents": ["raw"], "requires": ["voltage"]})
s.withdraw("raw", "Acquisition record found invalid")
assert not s.snapshot()["evaluation"]["valid"]["claim"]
restored = EvidenceStore.replay(s.events)
```

`put`, `withdraw`, `revise` and `set_goal` append events. Observations and source records cannot be rewritten using revise; create a new source and invalidate the old one. A snapshot is a copy, not mutable access to internal state. Do not treat graph validity as verification of source truth.

## HTTP

GET `/api/catalog`, `/api/book`, `/api/health`; page `/`, script `/app.js`, stylesheet `/style.css`. The local root inserts a fresh session token in a meta element. POST endpoints require that token in `X-Lab-Token`, acceptable Host/Origin headers and `Content-Type: application/json`.

POST `/api/run` body:

```json
{"experiment":"nernst","parameters":{"temperature_K":310}}
```

POST `/api/fit` body has exactly `csv` (UTF-8 text) and `metadata` (the source/acquisition object). Inputs are not persisted by the HTTP service. Responses are finite JSON or an explicit error. No arbitrary filesystem endpoint is provided. To retain full run custody, use the CLI capsule interface.

The server is for one trusted local research context. There is no patient database, authentication across users, OAuth, external model API or device adapter. Header tests were executed against the real Python HTTP server. Browser UI testing used an injected fetch bridge because environment policy blocked direct browser navigation to localhost; no direct browser-to-server network pass is claimed.
