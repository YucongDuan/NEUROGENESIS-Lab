# NEUROGENESIS-Lab 1.0.0

[Online report and project home](https://yucongduan.github.io/NEUROGENESIS-Lab/) · [Download v1.0.0](https://github.com/YucongDuan/NEUROGENESIS-Lab/releases/tag/v1.0.0) · [中文入口](README.zh-CN.md) · [Quick start](GETTING_STARTED.md) · [Publication record](PUBLICATION_2026-09-28.md)

## Energy, Information and Reconstructive Neural Science

**An English executable companion for Yucong Duan's _A Brief History of the Nervous System: From Life Sensing to Consciousness and Civilization_.**

Turn a book question into a mechanism that another researcher can challenge:

`chapter → explicit variables and units → experiment → alternative model → result → revision → recomputation`

This release is a complete, runnable reference workbench, not a whole-brain simulator. It provides **24 registered experiments, an 18-chapter reading path, a passive-recording CSV fitter, an append-only evidence memory, replayable run capsules, and a narrow cross-organ record adapter**. It does not provide a consciousness score, clinical recommendations, hardware control, or proof of an independent information field.

## Start without installation

Python 3.10 or later; no third-party runtime packages, API keys or model downloads.

```bash
python run.py list
python -m unittest discover -s tests -v
python run.py serve --port 8766
```

Open `http://127.0.0.1:8766`. On Windows use `launch.bat`; on macOS/Linux use `sh launch.sh`. The launcher does not install software, contact a cloud service or modify system settings. Stop the server with Ctrl+C.

## Run, retain and actually recompute

```bash
python run.py run hh --out runs/hh-01
python run.py verify-run runs/hh-01
python run.py replay runs/hh-01
```

A capsule contains the normalized input, result, numerical table, event chain, source identity and an integrity receipt. `verify-run` checks the stored artifacts. `replay` **executes the model again**, rather than simply checking a hash. Keep the printed `receipt_digest` independently to detect a coherently rewritten receipt and its files.

```bash
python run.py run hh --params examples/hh_blocked_sodium.json --out runs/no-sodium
python run.py run mapping --out runs/mapping
python run.py run revision --out runs/revision
python run.py run tournament --out runs/tournament
python run.py run candidate --params examples/null_candidate.json --out runs/null-candidate
python run.py demo --out runs/all-24
```

Every output path must be new. Failed results are not accepted as valid capsules. A capsule is a local research artifact, not a cryptographic signature or a registration with an independent timestamp.

## Three research programmes from the book

**Matched cues and remapping.** Frozen, delayed, permuted-control and adaptive policies see the same cue stream. Correct outcomes become available only after action. Paired seeds expose variation; sensing, action and additional updating costs are separated. The permuted arm is an offline negative control, not a causal online sensor.

**Reconstructive memory.** The same event stream is applied to summary-only, current dependency-graph and versioned-graph representations. Public queries test whether raw events, retractions, revised interpretations and past goals can be recovered. Storage bytes and a shared cap are reported, not concealed behind a composite superiority claim.

**Do more scales improve prediction?** Activity-only, structure-augmented and history-augmented linear models are fitted to the same synthetic table. Model choice uses validation data, not the final test set. A null-history scenario is supplied. These are controlled software experiments, not independent biological findings.

## Neural mechanisms, not a renamed kidney model

The new implementation contains a space-clamped Hodgkin–Huxley membrane, passive cable compartments, binomial synaptic release, a symmetric associative-memory network, feedback/decision experiments and observation-map tests. It retains useful reproducibility ideas already present in NEPHROGENESIS-Lab. See [the upstream review](docs/UPSTREAM_REVIEW.md) for actual inspection scope, source hashes and limitations of the comparison.

## Import a passive-membrane recording

```bash
python run.py fit --data examples/passive_step.csv --metadata examples/passive_source.json --out runs/passive-fit
```

CSV columns must be `time,voltage,split`; split is `train` or `test`. Metadata declares source, licensing and measurement units. Only a known-rest, known-current passive step model is fitted. Public-research input is accepted, but user declarations are not automatically verified. Do not load identifiable clinical data into this local prototype.

## Cross-organ record bridge

```bash
python run.py bridge --input examples/nephrogenesis_transport_result.json --out runs/kidney-record.json
```

This tested adapter preserves an actual NEPHROGENESIS result envelope and its file digest for side-by-side inspection. It does **not** create neural–renal co-simulation, shared state units or a clinical conclusion.

## Documentation and verification

- [User guide](docs/USER_GUIDE.md): commands, file formats, browser workflow and failure handling.
- [Methods](docs/METHODS.md): equations, numerical conventions and all experiment parameter contracts.
- [Chapter labs](docs/CHAPTER_LABS.md): all 18 chapter links and executable research tasks.
- [Architecture](docs/ARCHITECTURE.md): scientific kernel, evidence memory, capsules and API.
- [Validation](docs/VALIDATION.md): tests, solver comparisons and exact boundaries of verification.
- [English handbook](docs/NEUROGENESIS_Lab_English_Handbook.docx): integrated user/research/developer manual.
- [Security](SECURITY.md), [contributing](CONTRIBUTING.md), and [publication guide](PUBLICATION.md).

The runtime uses the Python standard library only. SciPy, coverage.py, python-docx and browser automation were used for optional release validation or documentation, not as runtime requirements. Configured CI is not evidence that remote CI or all platforms have already run.

## License and attribution

Apache-2.0 for original code and original English companion documentation. Synthetic passive-step data is additionally CC0-1.0. The full book, third-party papers, and fonts are not redistributed or relicensed. See LICENSE, NOTICE and CITATION.cff. Public source, release downloads and the online report are linked above; the original delivery record is preserved in the publication notes.
