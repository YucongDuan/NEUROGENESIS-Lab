# Validation record and precise scope

## Executed checks

The release suite contains **235 unittest cases**, with 0 failures and 0 errors in the recorded Linux/Python 3.13.5 execution. The generated per-experiment contract cases are counted as tests, not as independent biological experiments. Logs are in `validation/tests.txt`; the machine-readable summary is in `validation/test_summary.json`.

Core imported Python modules reached **96.12% statement coverage** and **87.10% branch coverage**. Coverage concerns the process instrumented by coverage.py; CLI commands are exercised in subprocesses but excluded from those coverage totals. The record does not claim complete execution coverage or proof of correctness.

Tests include finite/unit validation, JSON duplicate keys, unknown fields, equilibrium limits, HH zero-current and sodium-block cases, gate singularities, timestep refinement, capacitor/current accounting, passive-cable charge balance, resource conservation and exhaustion, exact binomial distributions, criterion/sensitivity distinctions, attractor Lyapunov behavior, report/task separation, observational non-identifiability, paired mapping costs, train/test isolation, source retraction, goal history, tampering, symlinks, HTML/CSV escaping, actual HTTP routes, and the CLI.

## Separate HH solver

`tools/reference_checks.py` implements relative-to-rest rates independently of `membrane.rates`, and integrates them with SciPy 1.17.0 DOP853 at rtol 1e-10/atol 1e-12. It compares them to the release's absolute-voltage RK4 output at the same sampled times. Brian2's official example was read to check equation/voltage conventions; Brian2 itself was not executed.

| RK4 step (ms) | Maximum voltage difference (mV) | Charge residual (nC/cm²) |
|---:|---:|---:|
| 0.025 | 0.00599964 | 5.8522e-12 |
| 0.0125 | 0.000305194 | 8.9102e-12 |
| 0.00625 | 0.0000171732 | 1.1710e-11 |

The voltage error decreases under step refinement. Charge residual is near round-off and need not decrease monotonically with more steps. All three runs produce two default spikes. This is an algorithm/equation cross-check, not a fit to squid recordings or human validation. The full record is `validation/reference_solver.json`.

## Browser and HTTP checks

The real Python loopback HTTP server was tested with standard-library HTTP requests, including all 24 experiment endpoints, the fit endpoint, Host/Origin checks, token rejection, bad content types and invalid input. Direct Chromium navigation to loopback (and the attempted test host) was blocked by environment policy.

To test the user interface without claiming that blocked path worked, the original HTML/JS was run in Chromium 144.0.7559.96 with an explicit injected fetch-to-Python-HTTP harness. All 24 experiments displayed metrics without JavaScript errors; 18 chapter buttons, chapter-to-experiment navigation, JSON download, CSV fitting, invalid-form handling and a 390-pixel mobile layout were checked. No horizontal document overflow was observed at that mobile width. Header behavior was checked separately; CSP enforcement in the injected browser harness is not claimed. See `validation/browser.json` and `tools/browser_ui_check.py`.

## Source baseline

The supplied NEPHROGENESIS 1.0.0 test suite actually ran with 198 passing tests. Five local core files match the current GitHub blob identifiers. Those results are not added to the new system's 235 tests and do not establish superiority. Other upstream ZIP internals were not executed. Review details and source-match records are retained separately.

## Reproduction gates

All 24 default experiments are saved and recomputed under the final engine identity. The passive CSV fit is also retained and recomputed. The final distribution is re-extracted into a new directory for manifest, unittest and execution checks. A wheel is installed into a separate virtual environment and run outside the source root. Machine-readable results are included in the delivery audit; do not assume a gate passed from this paragraph alone.

## Not established

There is no independent biological validation dataset, clinical trial, hardware test, full 3D brain model, definitive consciousness detector, experimentally confirmed independent information field, or demonstrated universal DIKWP advantage. No remote GitHub CI run, Windows/macOS execution or public repository deployment occurred during this delivery. Default numerical gains are properties of specified synthetic tasks, not claims about populations or all possible alternative architectures.
