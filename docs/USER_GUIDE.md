# User guide

## 1. Choose your entry point

For an immediate overview, open `SHOWCASE.html`. It is a static, precomputed report, not a live simulator. For parameter changes start `python run.py serve` and use the local workbench at `http://127.0.0.1:8766`. The interface, parameters, errors and documentation are in English.

Python 3.10+ is required. The core has zero third-party runtime dependencies. A virtual environment is useful but optional for running `run.py` from the source root. For a separately supplied wheel, use `python -m pip install --no-deps neurogenesis_lab-1.0.0-py3-none-any.whl`, then `neurogenesis list` or `python -m neurogenesis list`.

## 2. Browser workflow

The experiment atlas lists all 24 questions. Search by title or identifier. The chapter-reading button presents 18 book chapters, each linked to a primary experiment. A chapter card is a selective learning bridge, not a promise that a single simulation covers the entire chapter.

Each experiment displays its question, method, unit/range-constrained parameters, computed metrics, explicit limitations and the first 100 data rows. All numerical rows remain in downloaded JSON. Graphs may display at most about 600 sampled points per series for responsiveness; this affects only drawing. It does not resample the underlying run or the metrics.

Select **Run experiment** to call the local Python engine. Invalid forms are blocked in the browser, and the engine independently checks input. Reset returns to the registered defaults. Download saves the latest result as JSON. The browser result alone is not the full integrity/replay capsule; use the displayed CLI command to create one.

The application does not send data to external sites. CSV files are transmitted from the page to your local Python process only, then used in memory. The server does not write them into an access log or a persistent patient store.

## 3. Command-line experiments

```bash
python run.py list
python run.py run nernst
python run.py run hh --out runs/hh-01
python run.py run mapping --params examples/mapping_low_update_cost.json --out runs/mapping-01
python run.py demo --out runs/all-24
```

A parameter file is a JSON object of overrides. Omitted entries use defaults. Unknown keys are errors. A number may be supplied directly in its declared unit, or as `{ "value": 0.01, "unit": "s" }` for a time parameter whose native unit is ms. Only the documented conversion whitelist is accepted; this is not a symbolic computer-algebra system.

An output directory must not already exist. This prevents accidental loss of a previous run. Use a new name after changing an assumption. A failed experiment returns a nonzero process status with an error, not a simulated successful result.

## 4. Capsules, verification and replay

```bash
python run.py verify-run runs/hh-01
python run.py replay runs/hh-01
python run.py replay runs/hh-01 --trusted-digest YOUR_INDEPENDENTLY_RETAINED_RECEIPT_DIGEST
```

Files include `protocol.json`, `result.json`, `events.jsonl`, `report.html`, `data.csv` when rows are present, and `receipt.json`. A fit additionally retains `input.csv`. Verify checks exact inventory, bytes, event ordering and protocol/result bindings. Replay compares freshly computed results with both floating-point tolerances (rtol 1e-9, atol 1e-12) and exact canonical JSON equality. Both outcomes are reported; they are not interchangeable.

Changing a source file or registry invalidates engine identity. Keep the original software release alongside the run, or create a new run under the changed model. Python and platform metadata are recorded; bitwise equality across every platform is not guaranteed by passing locally.

## 5. Passive-recording CSV

Example:

```text
time,voltage,split
0,-65.0,train
1,-64.51,train
...
90,-55.11,test
```

Do not include literal ellipsis rows. Use the complete example in `examples/passive_step.csv`. Times must increase strictly; at least 8 training rows and 4 test rows are required. Allowed metadata fields are shown in `examples/passive_source.json`: source_kind (`synthetic` or `public_research`), source_locator, license, time_unit, voltage_unit, current_pA, rest_mV and onset_ms.

```bash
python run.py fit --data examples/passive_step.csv --metadata examples/passive_source.json --out runs/passive-fit
python run.py replay runs/passive-fit
```

The model is V(t)=Vrest + 0.001 I[pA] R[MOhm] (1-exp(-(t-onset)/tau[ms])). Tau is profiled over 1–200 ms at 1 ms spacing; R is fitted analytically from training rows at each tau and must be positive. The selected tau minimizes training RMSE. Test rows are not used for fitting. C[pF]=1000 tau[ms]/R[MOhm] is a conditional derived quantity. The profile is not a confidence interval.

Do not interpret a fit outside its known-step, known-rest assumptions as membrane identification. Spikes, drift, time-varying current and unknown baseline can invalidate the model. Boundary solutions are flagged. This importer does not parse NWB, ABF or equipment-native files and does not establish licensing or de-identification from a checkbox.

## 6. Evidence-memory experiment

```bash
python run.py run revision --out runs/revision
```

The four public regression questions concern raw-event retention, invalidation after a calibration retraction, updated present interpretation and recovery of a past goal. The three stored representations process the same event sequence, but have different capacities by construction. The printed serialized-byte count and common cap prevent hiding that difference. The cap is a reporting threshold, not an enforced memory allocator. Passing more of these constructed queries does not establish a universal advantage over other memory systems or human participants.

## 7. Read-only kidney bridge

```bash
python run.py bridge --input examples/nephrogenesis_transport_result.json --out runs/kidney-record.json
```

The output preserves the original payload and file digest, labels it `imported_unverified` and records mapping loss. It does not assert that the source computation is correct or that its units translate into neural ones. Only the documented result envelope has been exercised. No FHIR, NOESISCOPE, NeuroBody, electrode or cloud integration is claimed.

## 8. Troubleshooting

**Port occupied:** choose a different port, e.g. `--port 8877`.

**Host/Origin rejected:** use the displayed localhost URL; do not expose this server through an unreviewed public reverse proxy.

**Session token rejected:** reload the page after restarting the server. Each process has a fresh token.

**Engine changed on replay:** preserve the original source/wheel. Do not edit a receipt to conceal the difference.

**Gate or state error:** inspect the input, units and allowed range. A model-domain rejection is not an experimental discovery.

**Download does not represent the full study:** JSON contains one result. A reproducible capsule also needs its protocol, source identity and inputs.

**Test data influenced tuning:** changing feature sets or parameters after seeing the test set invalidates its role as a final holdout, even if the code itself never uses test rows in fitting. Create a new independent evaluation and disclose the change.
