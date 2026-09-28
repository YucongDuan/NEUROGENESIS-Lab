# Contributing a falsifiable extension

Start with a bounded question and identify what the existing release cannot distinguish. A larger model is not automatically better. Keep the following in one reviewed change: explicit variables and units, mechanism/algorithm, normalized input contract, failure conditions, source status, and regression tests.

Register a new experiment in `neurogenesis/data/experiments.json`; implement its function or dispatch in `experiments.py` or a focused module. Return JSON-compatible finite results, a metric dictionary, rows, assumptions and limitations. Add source/book anchors, but do not put the full copyrighted book or third-party papers into the repository. New schema fields require strict validation and test coverage.

Use seeded randomness local to the experiment. Do not alter global random state. For continuous dynamics, add an analytic limit or independent solver comparison, dt sensitivity, domain tests and a conservation ledger where applicable. Do not repair an unstable model by silently clipping invalid states.

For statistical models, specify which data fit parameters, choose models and evaluate final generalization. Preserve null/negative scenarios and report parameter count and observation assumptions. Do not tune to a holdout and keep calling it untouched.

For evidence memory, preserve source records. Revise interpretations through new operations; do not backdate goals. An internally valid graph cannot certify the truth of a paper or an observation. Keep source, formal, synthetic and hypothesis roles distinguishable.

Before a release, run the stdlib tests, optional coverage and solver checks, actual HTTP tests, browser UI checks, wheel install outside the repository, and clean-extraction verification. Record what was not tested. Remote CI should be enabled only after maintainers review the workflow and permissions.

A change to scientific meaning should update the model/software version and its documented compatibility. Publication claims, clinical claims and claims of artificial consciousness require evidence beyond software tests.
