# Upstream review: observed assets, actual limits, and new implementation

Review date: 2026-09-27. This is a scoped engineering comparison, not an exhaustive audit of Yucong Duan's portfolio or a ranking of biological accuracy. Observed repositories were read with the connected GitHub API. Root-tree identities below are **tree SHA values, not commit SHA values**. Individual source-file identities use Git blob SHA-1.

## 1. NEPHROGENESIS-Lab: executable source review and baseline run

Repository: https://github.com/YucongDuan/NEPHROGENESIS-Lab

Observed root tree: `3cdf751cccae39315d631a2ec621bdbf8ce2f83b`.

The supplied 1.0.0 archive was extracted. Five local core files were compared byte-for-byte through their Git-blob hash construction with the current GitHub Contents API identifiers: `dynamics.py`, `evidence.py`, `ledger.py`, `calibration.py`, and `experiments.py`. All five matched; the entire archive is **not** thereby asserted identical to current GitHub. The supplied upstream test suite was actually run: 198 tests passed. Logs and all five hashes are retained in `validation/upstream_tests.txt` and `validation/upstream_source_match.json`.

The reviewed implementation already contains an explicitly bounded renal compartment model, RK4-integrated water/sodium/urea ledgers, typed evidence dependencies, withdrawal propagation, result recomputation and a train/holdout scalar fitter. These capabilities are genuine prior assets; the new work does not claim to invent them.

The domain boundary is concrete. The renal dynamics states are water, sodium, urea and cumulative fluxes. Its source explicitly excludes vascular, glomerular and medullary geometry. It does not implement neuronal channel gates, cable voltage propagation, synaptic release or associative neural dynamics in that reviewed module. Its evidence graph offers present-state dependency auditing; the new system adds explicit append-only interpretation versions and past-goal replay, with a constructed multi-representation query experiment. Its curve fitter motivates, but is not substituted for, the new passive-membrane acquisition contract.

NEUROGENESIS-Lab is a new domain implementation rather than a fork containing renamed renal state variables. The only bundled upstream-generated example is the renal transport result used by the narrow, read-only record adapter. No untested native integration with other repositories is advertised.

## 2. NeuroBody SemanticOS: public design and distribution inspection

Repository: https://github.com/YucongDuan/DIKWP-NeuroBody-SemanticOS-Platform-Package

Observed root tree: `cc303795892906a331f7bad2d4f4055898b67dd3`.

The public README describes brain/body-machine semantic interaction, a browser prototype, a blueprint, a policy matrix, schemas, an API draft and a replay-bundle demo. It expressly treats the package as a research/product-design prototype rather than a medical device or invasive control protocol. The observed root distributes the application as a ZIP alongside README and LICENSE.

The connector rejects binary raw downloads; the ZIP's internal implementation was not recovered or executed in this review. Consequently, no claim is made that it lacks every mechanism, test or integration discussed here. The defensible extension is a separately delivered, visibly source-first neural numerical workbench with tested model outputs, not a supposed refutation of unseen source.

## 3. NeuroSentinel: care-oriented scope, not a neural simulation baseline

Repository: https://github.com/YucongDuan/NeuroSentinel-OS-v1.0.0

Observed root tree: `73385c38f40df03a30b5925bc4ee75fef7428277`.

Its README describes evidence-bound neurological clinical decision-support and safeguarding, competing hypotheses, human approval and outcome calibration, with alpha/reference status and explicit limitations. The observed root again contains a ZIP, README and LICENSE. Only the README and root inventory were reviewed; internal ZIP source and clinical effectiveness were not tested.

NEUROGENESIS does not supersede care workflows. It addresses a different need: explaining how a specified mechanism generates a curve and how alternative mechanisms can be distinguished. There is no prescribing, capacity adjudication, risk prediction about individuals or device actuation in the companion.

## 4. C-NOESISCOPE: distinctions worth preserving

Repository: https://github.com/YucongDuan/C-NOESISCOPE

Observed root tree: `86103f5f480e1b63b4fe333d7d972821027cc7c9`.

The README distinguishes functional signatures, subjecthood candidates, welfare precautions and phenomenal consciousness, and declines an uncalibrated consciousness probability. That restraint is not a limitation to remove. The observed ZIP internals were not executed. Our `access` experiment instead provides a small task/report dissociation, keeping those distinctions visible without issuing an awareness score.

## 5. NEGENESIS-OMEGA: root inventory only in this review

Repository: https://github.com/YucongDuan/NEGENESIS-OMEGA

Observed root tree: `440cf568f6dc08882752cf1e8446cd6b6a43c06f`.

The current root inventory was inspected, not the binary package or its full scientific implementation. Its presence is a context pointer only. No comparative performance or internal-feature claim is made from a root listing.

## What “advancement” means in this delivery

It means new executable neural mechanisms, explicit dimensional bridges, three source-derived research programmes, a usable passive-recording import path, versioned interpretation history, and recomputable neural capsules. It does not mean verified superiority over all upstream projects, novel discovery of the HH equations, proof of consciousness, or empirical validation of a new field. Those stronger claims require additional evidence and independent comparators.

Source-first delivery is already present in current NEPHROGENESIS; it is not attributed as a new invention. ZIP-only root layouts in three other observed repositories make public browsing and review less direct, but do not prove their archives lack code or tests.
