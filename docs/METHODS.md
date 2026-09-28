# Methods and parameter contracts

All equations below describe the delivered implementation. Book sections supply questions and framing; implementation choices and synthetic numbers are this companion’s additions. The registry is the executable input contract. Direct equations use declared units, not an inference that similarly named quantities are interchangeable.

## `loop` — A body maintains an actionable world

Book anchors: 1.8, 1.16. Sources: BOOK.

x[t+1]=a x[t]+u[t]+d[t]; u=-k x for feedback, u=0 for open loop.

Compare the same forcing and initial state. Increase feedback gain until the chosen discrete plant becomes less stable. The resource-free scalar state is a didactic abstraction, not a nervous system.

| Parameter | Default | Unit | Allowed interval |

|---|---:|---|---|

| `initial` | 0.5 | 1 | -2 to 2 |

| `gain` | 0.2 | 1 | 0 to 1 |

| `steps` | 120 | 1 | 20 to 1000 |

Run: `python run.py run loop --out runs/loop-01`. Every accepted result also includes the method and its explicit limitations.

## `nernst` — Electrochemical gradients

Book anchors: 2.7, 6.2. Sources: BOOK, HH1952.

E[mV]=1000 RT/(zF) ln(c_out/c_in).

Use Kelvin and signed valence. Equal concentrations give zero potential; reversing valence changes sign. An ideal equilibrium potential is not a measured resting voltage of a cell with many channels.

| Parameter | Default | Unit | Allowed interval |

|---|---:|---|---|

| `inside_mmol_L` | 140 | mmol/L | 0.001 to 1000 |

| `outside_mmol_L` | 5 | mmol/L | 0.001 to 1000 |

| `valence` | 1 | 1 | -3 to 3 |

| `temperature_K` | 310 | K | 250 to 350 |

Run: `python run.py run nernst --out runs/nernst-01`. Every accepted result also includes the method and its explicit limitations.

## `delay` — Communication before centralization

Book anchors: 3.1, 3.18. Sources: BOOK.

t_diff=L²/(2D), using one spatial dimension; t_signal=L/v+t_syn.

Both routes depend on the selected geometry and mechanism. Change length while holding D and v constant. Similar scaling formulas do not demonstrate a historical single origin of neurons.

| Parameter | Default | Unit | Allowed interval |

|---|---:|---|---|

| `distance_mm` | 1 | 1 | 0.001 to 100 |

| `diffusivity_m2_s` | 1e-09 | 1 | 1e-12 to 1e-06 |

| `velocity_m_s` | 1 | 1 | 0.001 to 200 |

| `synaptic_delay_ms` | 1 | ms | 0 to 100 |

Run: `python run.py run delay --out runs/delay-01`. Every accepted result also includes the method and its explicit limitations.

## `network` — One wiring diagram, two dynamics

Book anchors: 4.10, 17.4, 17.5. Sources: BOOK.

dx/dt=A x. A=[[-a,b],[b,-a]] for positive recurrence; A=[[-a,b],[-b,-a]] for opponent recurrence.

The unsigned wiring is the same. Signs change eigenvalues and trajectories. Exact exponential/hyperbolic or trigonometric solutions isolate dynamical information missing from adjacency alone.

| Parameter | Default | Unit | Allowed interval |

|---|---:|---|---|

| `gain` | 1.2 | 1 | 0 to 1.5 |

| `tau_ms` | 20 | ms | 5 to 100 |

| `duration_ms` | 100 | ms | 10 to 200 |

Run: `python run.py run network --out runs/network-01`. Every accepted result also includes the method and its explicit limitations.

## `development` — Experience-dependent competition

Book anchors: 5.11, 5.16. Sources: BOOK.

Two nonnegative weights receive seeded experience-dependent increments and are normalized to unit sum after each update.

The normalization is a declared learning rule. It is not derived as a universal developmental mechanism. Compare experience ratios and test that the sum remains one.

| Parameter | Default | Unit | Allowed interval |

|---|---:|---|---|

| `steps` | 250 | 1 | 20 to 2000 |

| `learning_rate` | 0.03 | 1 | 0 to 0.2 |

| `preference` | 0.75 | 1 | 0 to 1 |

| `seed` | 98 | 1 | 0 to 4294967295 |

Run: `python run.py run development --out runs/development-01`. Every accepted result also includes the method and its explicit limitations.

## `hh` — Excitable membrane and charge accounting

Book anchors: 6.4, 6.6, 6.7, 18.4. Sources: BOOK, HH1952, BRIAN_HH.

C dV/dt=Iext−gNa m³h(V−ENa)−gK n⁴(V−EK)−gL(V−EL); dx/dt=alpha_x(1−x)−beta_x x.

Canonical 6.3 °C squid-axon kinetics, not mammalian calibration. V is in mV relative to an absolute rest convention near −65 mV; ENa=50, EK=−77, EL=−54.387 mV. RK4 steps end exactly on pulse boundaries. Integrating all signed currents with the same quadrature enables a charge residual; the method does not simulate axonal propagation.

| Parameter | Default | Unit | Allowed interval |

|---|---:|---|---|

| `current_uA_cm2` | 10 | 1 | 0 to 30 |

| `g_na_mS_cm2` | 120 | 1 | 0 to 200 |

| `g_k_mS_cm2` | 36 | 1 | 0 to 100 |

| `capacitance_uF_cm2` | 1 | 1 | 0.8 to 2 |

| `duration_ms` | 50 | ms | 5 to 200 |

| `dt_ms` | 0.025 | ms | 0.005 to 0.025 |

| `pulse_start_ms` | 5 | ms | 0 to 150 |

| `pulse_end_ms` | 30 | ms | 0.1 to 200 |

Run: `python run.py run hh --out runs/hh-01`. Every accepted result also includes the method and its explicit limitations.

## `release` — Stochastic synaptic release

Book anchors: 7.2, 7.3. Sources: BOOK.

K ~ Binomial(N,p). E[K]=Np; Var(K)=Np(1−p); P(K=0)=(1−p)^N.

The simulation uses independent fixed-probability release sites. Exact probabilities and finite-sample frequencies are reported side by side. No vesicle depletion, facilitation or correlated release is fitted.

| Parameter | Default | Unit | Allowed interval |

|---|---:|---|---|

| `sites` | 8 | 1 | 1 to 32 |

| `probability` | 0.25 | 1 | 0 to 1 |

| `trials` | 2000 | 1 | 100 to 10000 |

| `seed` | 98 | 1 | 0 to 4294967295 |

Run: `python run.py run release --out runs/release-01`. Every accepted result also includes the method and its explicit limitations.

## `detection` — Sensitivity is not criterion

Book anchors: 8.15, 16.3. Sources: BOOK.

For unit-variance normal evidence separated by d′, hit/false-alarm rates are upper-tail probabilities at the criterion.

Change criterion without changing d′ to isolate response policy from sensitivity. Balanced task accuracy is not perceptual consciousness, and d′ does not identify a neural circuit.

| Parameter | Default | Unit | Allowed interval |

|---|---:|---|---|

| `d_prime` | 1.5 | 1 | 0 to 5 |

| `criterion` | 0.3 | 1 | -3 to 3 |

Run: `python run.py run detection --out runs/detection-01`. Every accepted result also includes the method and its explicit limitations.

## `motor` — Feedback with shared measurement noise

Book anchors: 9.7, 9.15. Sources: BOOK.

A discrete linear plant receives feedback from either current or delayed noisy observations.

Use the same disturbance and measurement-noise realizations in both arms. A delay can change stability and control error, but no universal physiological delay constant or best controller is inferred.

| Parameter | Default | Unit | Allowed interval |

|---|---:|---|---|

| `steps` | 200 | 1 | 50 to 2000 |

| `gain` | 2 | 1 | 0 to 3 |

| `delay_steps` | 6 | 1 | 0 to 30 |

| `noise` | 0.02 | 1 | 0 to 0.3 |

| `seed` | 98 | 1 | 0 to 4294967295 |

Run: `python run.py run motor --out runs/motor-01`. Every accepted result also includes the method and its explicit limitations.

## `body` — Interoception and resource balance

Book anchors: 10.1, 10.15. Sources: BOOK.

resource[t+1]=resource[t]+input[t]−demand[t]. Acquisition is a bounded function of observed resource error.

The cumulative ledger distinguishes successful regulation from hidden resource depletion. The state and costs are dimensionless. Failure at exhaustion is reported, not clipped to a visually acceptable trace.

| Parameter | Default | Unit | Allowed interval |

|---|---:|---|---|

| `steps` | 160 | 1 | 40 to 1000 |

| `initial_resource` | 10 | 1 | 1 to 30 |

| `target` | 10 | 1 | 1 to 30 |

| `basal_cost` | 0.2 | 1 | 0 to 1 |

| `extra_cost` | 0.2 | 1 | 0 to 1 |

| `max_intake` | 0.8 | 1 | 0 to 2 |

| `gain` | 0.1 | 1 | 0 to 0.5 |

| `delay_steps` | 4 | 1 | 0 to 40 |

Run: `python run.py run body --out runs/body-01`. Every accepted result also includes the method and its explicit limitations.

## `attractor` — A reconstructive attractor

Book anchors: 11.9, 11.17. Sources: BOOK, HOPFIELD1982.

W_ij=(1/N) Σ_mu xi_i^mu xi_j^mu, W_ii=0; E=−(1/2)Σ_ij W_ij s_i s_j.

Asynchronous updates in a symmetric network should not increase this Lyapunov function. Its E is not measured metabolic energy. A recovered pattern demonstrates this constructed retrieval task, not human autobiographical memory.

| Parameter | Default | Unit | Allowed interval |

|---|---:|---|---|

| `neurons` | 24 | 1 | 8 to 48 |

| `patterns` | 3 | 1 | 1 to 12 |

| `corruption` | 0.15 | 1 | 0 to 0.8 |

| `updates` | 240 | 1 | 20 to 1000 |

| `seed` | 98 | 1 | 0 to 4294967295 |

Run: `python run.py run attractor --out runs/attractor-01`. Every accepted result also includes the method and its explicit limitations.

## `td` — Prediction error and changing outcomes

Book anchors: 12.3, 12.5. Sources: BOOK.

V[t+1]=V[t]+alpha(reward[t]−V[t]).

The one-state reward expectation is a deliberately reduced prediction-error model. Changing outcomes produces adaptation, but the code does not identify dopamine, motivation or moral value from this scalar.

| Parameter | Default | Unit | Allowed interval |

|---|---:|---|---|

| `learning_rate` | 0.08 | 1 | 0 to 1 |

| `trials` | 200 | 1 | 20 to 2000 |

Run: `python run.py run td --out runs/td-01`. Every accepted result also includes the method and its explicit limitations.

## `sleep` — Homeostatic and circadian time

Book anchors: 13.2, 13.3. Sources: BOOK.

During assigned wake: S′=(1−S)/tau_w; during assigned sleep: S′=−S/tau_s. Add an independent sinusoidal circadian signal.

Exact interval updates reduce numerical drift. The schedule is imposed, not predicted. It is not a sleep prescription or a full theory of sleep functions and disorders.

| Parameter | Default | Unit | Allowed interval |

|---|---:|---|---|

| `hours` | 72 | 1 | 24 to 240 |

| `initial_pressure` | 0.2 | 1 | 0 to 1 |

| `wake_tau_h` | 18 | 1 | 1 to 40 |

| `sleep_tau_h` | 4 | 1 | 1 to 20 |

Run: `python run.py run sleep --out runs/sleep-01`. Every accepted result also includes the method and its explicit limitations.

## `cable` — Distributed conduction and local loss

Book anchors: 6.12, 14.7. Sources: BOOK.

C_i dV_i/dt=I_i−gL V_i+gA Σ_neighbors(V_j−V_i). Sealed endpoints have only one neighbor.

Voltage is displacement from rest. Identical passive compartments conserve axial charge internally. The sum of input minus leak matches capacitive change. No active conduction velocity, myelin geometry or disease diagnosis is calculated.

| Parameter | Default | Unit | Allowed interval |

|---|---:|---|---|

| `compartments` | 9 | 1 | 2 to 24 |

| `capacitance_pF` | 200 | pF | 100 to 1000 |

| `leak_nS` | 10 | nS | 1 to 50 |

| `axial_nS` | 80 | nS | 0 to 300 |

| `current_pA` | 100 | pA | 0 to 1000 |

| `dt_ms` | 0.05 | ms | 0.01 to 0.1 |

| `duration_ms` | 100 | ms | 10 to 200 |

Run: `python run.py run cable --out runs/cable-01`. Every accepted result also includes the method and its explicit limitations.

## `social` — Many reports, one common source

Book anchors: 15.10, 15.14. Sources: BOOK.

For exchangeable correlation rho, n_eff=n/[1+(n−1)rho].

This is a variance-equivalence calculation under equal variance and pairwise correlation, not a universal measure of credibility. Thirty correlated reports need not equal thirty independent observations.

| Parameter | Default | Unit | Allowed interval |

|---|---:|---|---|

| `reports` | 30 | 1 | 2 to 500 |

| `shared_fraction` | 0.6 | 1 | 0 to 1 |

Run: `python run.py run social --out runs/social-01`. Every accepted result also includes the method and its explicit limitations.

## `access` — Task access and report dissociation

Book anchors: 16.3, 16.5, 16.17. Sources: BOOK.

Generate a task decision with fixed sensory reliability and an independent report gate with probability q.

The output distinguishes task correctness, report availability and correctness conditional on report. Nothing in the generator creates an experience variable. The experiment cannot infer awareness from failure to report.

| Parameter | Default | Unit | Allowed interval |

|---|---:|---|---|

| `trials` | 1000 | 1 | 50 to 10000 |

| `sensitivity` | 0.8 | 1 | 0.5 to 1 |

| `report_gate` | 0.25 | 1 | 0 to 1 |

| `seed` | 98 | 1 | 0 to 4294967295 |

Run: `python run.py run access --out runs/access-01`. Every accepted result also includes the method and its explicit limitations.

## `identify` — Hidden state is not identified by a fit

Book anchors: 17.7, 17.8, 17.9. Sources: BOOK.

Two hidden states share decay rate a: x1′=−a x1, x2′=−a x2. The sensor y=x1+x2 cannot distinguish initial splits with the same sum.

Adding selective observation increases rank. A perfect fit to y is compatible with different hidden mechanisms. This exact counterexample concerns observability, not every practical parameter-identification problem.

| Parameter | Default | Unit | Allowed interval |

|---|---:|---|---|

| `tau_ms` | 20 | ms | 1 to 200 |

| `duration_ms` | 100 | ms | 10 to 500 |

| `split_a` | 0.2 | 1 | 0 to 1 |

| `split_b` | 0.8 | 1 | 0 to 1 |

Run: `python run.py run identify --out runs/identify-01`. Every accepted result also includes the method and its explicit limitations.

## `energy` — Energy, information and dimensional bridges

Book anchors: 18.4, 18.8, 18.11. Sources: BOOK, LANDAUER1961.

Per-event energy=(molar energy)/NA. Erasure scale=k_B T ln 2. Ratio=(delta_mu)/(RT ln2). Capacitor energy=(1/2)C V².

Match J/mol to J/event before forming a dimensionless ratio. Landauer supplies a conditional erasure scale, not actual brain computation cost. Capacitive energy, channel dissipation and restoration budgets must not be simply summed as total metabolism.

| Parameter | Default | Unit | Allowed interval |

|---|---:|---|---|

| `molar_energy_J_mol` | 50000 | J/mol | 1 to 100000 |

| `temperature_K` | 310 | K | 250 to 350 |

| `capacitance_pF` | 200 | pF | 1 to 1000 |

| `voltage_mV` | 65 | mV | 0 to 150 |

Run: `python run.py run energy --out runs/energy-01`. Every accepted result also includes the method and its explicit limitations.

## `clamp` — Voltage-dependent gating

Book anchors: 6.5, 6.6. Sources: BOOK, HH1952, BRIAN_HH.

x_inf(V)=alpha_x/[alpha_x+beta_x]; tau_x(V)=1/[alpha_x+beta_x].

Voltage-dependent gating uses the same canonical kinetics as HH, including stable evaluation of removable singularities at −40 and −55 mV. It is a calculation under a clamp assumption, not an experimental protocol.

| Parameter | Default | Unit | Allowed interval |

|---|---:|---|---|

| `voltage_mV` | -40 | mV | -100 to 50 |

Run: `python run.py run clamp --out runs/clamp-01`. Every accepted result also includes the method and its explicit limitations.

## `alias` — A sampling window can hide a mechanism

Book anchors: 17.2, 17.3. Sources: BOOK.

cos(2π f k/fs)=cos(2π f_alias k/fs) for an appropriate aliased frequency within [0,fs/2].

The default 90 Hz cosine sampled at 100 Hz equals a 10 Hz sampled cosine. Samples alone cannot decide which original source produced them. Anti-alias filtering is not implemented here.

| Parameter | Default | Unit | Allowed interval |

|---|---:|---|---|

| `frequency_Hz` | 90 | Hz | 0.1 to 500 |

| `sample_Hz` | 100 | Hz | 1 to 1000 |

| `samples` | 150 | 1 | 10 to 1000 |

Run: `python run.py run alias --out runs/alias-01`. Every accepted result also includes the method and its explicit limitations.

## `mapping` — Programme I: matched cues and remapping

Book anchors: 18.7, 18.9, 18.16. Sources: BOOK.

Adaptive mapping score q[t+1]=(1−alpha)q[t]+alpha cue[t] truth[t], updated only after action.

A hidden cue reversal halfway through the synthetic task tests frozen versus delayed versus offline-permuted versus learned mappings. All policies receive identical current cues and post-action outcomes. The adaptive action uses the preceding score. Report paired seed differences and separate additional update energy; do not call equal action count equal total energy.

| Parameter | Default | Unit | Allowed interval |

|---|---:|---|---|

| `trials` | 500 | 1 | 100 to 1500 |

| `seeds` | 24 | 1 | 4 to 64 |

| `noise` | 0.15 | 1 | 0 to 0.49 |

| `learning_rate` | 0.08 | 1 | 0.01 to 0.5 |

| `delay_trials` | 5 | 1 | 0 to 40 |

| `sensor_nJ` | 0.2 | nJ | 0 to 10 |

| `action_nJ` | 0.8 | nJ | 0 to 10 |

| `update_nJ` | 0.05 | nJ | 0 to 10 |

| `seed` | 98 | 1 | 0 to 4294967295 |

Run: `python run.py run mapping --out runs/mapping-01`. Every accepted result also includes the method and its explicit limitations.

## `revision` — Programme II: reconstructive evidence memory

Book anchors: 11.16, 18.15, 18.16. Sources: BOOK.

Representations: final summary, current dependency graph, and event-versioned dependency graph; all process the same eight-operation correction stream.

Four explicitly published queries are evaluated by extracting retained values, not assigning a winner by name. The byte cap is a shared reporting threshold. Retractions and past-goal recovery are software properties, not demonstrations of phenomenal identity or universal DIKWP superiority.

| Parameter | Default | Unit | Allowed interval |

|---|---:|---|---|

| `budget_bytes` | 16000 | 1 | 100 to 100000 |

Run: `python run.py run revision --out runs/revision-01`. Every accepted result also includes the method and its explicit limitations.

## `tournament` — Programme III: does another scale help prediction?

Book anchors: 17.10, 17.12, 18.16. Sources: BOOK.

Nested OLS: y~1+x; y~1+x+structure; y~1+x+structure+history. Ordered splits: 60% training,20% validation,20% final test.

Fit coefficients on training; select using validation; report test only. The synthetic history feature is observed; obtaining it in a real recording requires an estimator and independent evidence. A zero-history scenario checks that more structure is not asserted beneficial a priori.

| Parameter | Default | Unit | Allowed interval |

|---|---:|---|---|

| `samples` | 400 | 1 | 100 to 1500 |

| `history_gain` | 1.5 | 1 | 0 to 3 |

| `noise` | 0.1 | 1 | 0 to 1 |

| `seed` | 98 | 1 | 0 to 4294967295 |

Run: `python run.py run tournament --out runs/tournament-01`. Every accepted result also includes the method and its explicit limitations.

## `candidate` — A falsifiable energy-information candidate

Book anchors: 18.10, 18.11, 18.16. Sources: BOOK, RG_LIST.

E_nJ=intercept+beta_s spike_feature+beta_t duration_feature+Psi_nJ/bit (I_bit C A)+noise.

This is an additive extension of a conventional resource model, not a claim that the book’s E=Psi I C A represents all neural energy. Compression C and coupling A are dimensionless scenario variables. I is not automatically Shannon information measured from recordings. Fit on training70%, compare final30%; a null-Psi example is included.

| Parameter | Default | Unit | Allowed interval |

|---|---:|---|---|

| `samples` | 300 | 1 | 100 to 1000 |

| `psi_nJ_bit` | 0.7 | 1 | 0 to 3 |

| `noise_nJ` | 0.1 | nJ | 0 to 1 |

| `seed` | 98 | 1 | 0 to 4294967295 |

Run: `python run.py run candidate --out runs/candidate-01`. Every accepted result also includes the method and its explicit limitations.

## Numerical assumptions and independent checks

All registered experiments are either conditional calculations or synthetic models. No runtime accesses a participant, clinic or neural device. The membrane solver is checked against a separately written relative-voltage RHS integrated by SciPy DOP853; the published Brian2 example was used to check equation conventions, not executed as a second software benchmark. The SciPy check is numerical, not biological validation.

Continuous and discrete models have different contracts. A one-step discrete process does not gain a continuous-time convergence guarantee merely because another experiment uses RK4. In the membrane and cable models, charge ledgers share the same quadrature as the state dynamics. Domain rejection and solver sensitivity must be examined before interpreting a curve.

Statistical results are scoped to their generator, seed schedule, noise model and chosen data partitions. The normal-approximation interval in the mapping task spans paired random-seed outcomes, not biological populations. The fixed CSV tau profile is not a confidence interval. Repeated tuning after observing a holdout defeats its independence even if the fitting function never reads those rows.
