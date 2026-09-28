# Source-first publication and maintenance

**Publication update, 28 September 2026:** see [the GitHub publication record](PUBLICATION_2026-09-28.md). The original preparation notes below describe the pre-publication delivery.

This local package is ready to review and publish; the delivery has not created, pushed, changed or released a GitHub repository. Its identity does not imply institutional endorsement.

Maintain one canonical repository containing visible `neurogenesis/`, `tests/`, `docs/` and `tools/` paths. Do not replace the source tree with only a ZIP. Retain the release ZIP as a convenience artifact alongside the source and wheel, not as the only review surface.

From the source root, a maintainer can build a wheel with `python -m pip wheel --no-deps --no-build-isolation . --wheel-dir dist` after making sure setuptools and wheel are available. The dependency-free `run.py` route remains the simplest offline entry point. The supplied wheel is separately installation-tested.

Before tagging, run `python -m unittest discover -s tests -v`, `python tools/verify_release.py`, and `python run.py demo --out runs/release-candidate`. Recompute each saved run. Record Python/platform versions and model assumptions, including negative results. Refresh the release manifest only for an intentional new release; changing it is not a substitute for disclosing a changed source.

The supplied CI workflow covers Python 3.10 and 3.13 on Linux and Windows when executed by GitHub. It was prepared but not run on GitHub during this delivery. Action versions should be reviewed and pinned to reviewed commits by maintainers before a hardened production release. No branch rule, workflow run, DOI, artifact attestation or external timestamp is claimed here.

The next evidence milestones are scientific rather than calendar promises: an independent run outside the author's environment; a justified public passive-recording dataset with rights and acquisition metadata; null/alternative mechanisms that challenge the current kernels; and independently designed tasks for memory/mapping comparisons. Each should have a scoped acceptance criterion, not a blanket “validated brain” label.
