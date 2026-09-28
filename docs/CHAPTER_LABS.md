# Eighteen chapter labs

These English sheets are original executable interpretations. The source book is not reproduced. Source hashes and anchors are in `neurogenesis/data/book_map.json`. Start with the named primary experiment, then inspect the alternative or failed case.

## Chapter 1. The problem of an actionable world

Question: When do equal disturbances produce different recoveries?

Book sections: 1.8, 1.16. Primary model: `loop`.

Run `python run.py run loop --out runs/chapter-01`.

Compare the same forcing and initial state. Increase feedback gain until the chosen discrete plant becomes less stable. The resource-free scalar state is a didactic abstraction, not a nervous system.

Research exercise: record the default result, choose one parameter inside its contract, predict how the result should change, then execute the modified model. Retain a case that contradicts the first prediction. Separate an algebraic consequence of the model from a claim about a biological system.

Provenance: source chapter SHA-256 `2d64a0c693e1ebb5bcec3831a7b81e5a09aea9b65e8121e02c4407e164b8567b`.

## Chapter 2. The physical prehistory of neural systems

Question: Why does an ion concentration ratio determine an equilibrium voltage?

Book sections: 2.7. Primary model: `nernst`.

Run `python run.py run nernst --out runs/chapter-02`.

Use Kelvin and signed valence. Equal concentrations give zero potential; reversing valence changes sign. An ideal equilibrium potential is not a measured resting voltage of a cell with many channels.

Research exercise: record the default result, choose one parameter inside its contract, predict how the result should change, then execute the modified model. Retain a case that contradicts the first prediction. Separate an algebraic consequence of the model from a claim about a biological system.

Provenance: source chapter SHA-256 `aed2e4f53ded2685826826342a05726616f118960661a7141be2239fd752eb0d`.

## Chapter 3. Communication before the first neural nets

Question: How do local diffusion and assigned propagation speed scale differently?

Book sections: 3.1, 3.18. Primary model: `delay`.

Run `python run.py run delay --out runs/chapter-03`.

Both routes depend on the selected geometry and mechanism. Change length while holding D and v constant. Similar scaling formulas do not demonstrate a historical single origin of neurons.

Research exercise: record the default result, choose one parameter inside its contract, predict how the result should change, then execute the modified model. Retain a case that contradicts the first prediction. Separate an algebraic consequence of the model from a claim about a biological system.

Provenance: source chapter SHA-256 `09a37c6a23c53f3374f4b15758e4d099aaa709c82589c9eec8a4cd8664a37f17`.

## Chapter 4. Evolutionary branches of centralization

Question: Can the same unsigned adjacency support different behavior?

Book sections: 4.10. Primary model: `network`.

Run `python run.py run network --out runs/chapter-04`.

The unsigned wiring is the same. Signs change eigenvalues and trajectories. Exact exponential/hyperbolic or trigonometric solutions isolate dynamical information missing from adjacency alone.

Research exercise: record the default result, choose one parameter inside its contract, predict how the result should change, then execute the modified model. Retain a case that contradicts the first prediction. Separate an algebraic consequence of the model from a claim about a biological system.

Provenance: source chapter SHA-256 `39728789be2b14fe6370483480b1419e730bb5e9bb616a1f044c27d889d5ff85`.

## Chapter 5. Development, connections and experience

Question: How can a fixed total connection budget be redistributed by experience?

Book sections: 5.11, 5.16. Primary model: `development`.

Run `python run.py run development --out runs/chapter-05`.

The normalization is a declared learning rule. It is not derived as a universal developmental mechanism. Compare experience ratios and test that the sum remains one.

Research exercise: record the default result, choose one parameter inside its contract, predict how the result should change, then execute the modified model. Retain a case that contradicts the first prediction. Separate an algebraic consequence of the model from a claim about a biological system.

Provenance: source chapter SHA-256 `46513691763a97ea118d97665fe2f043e044414e299fe4e127e133769a2503ce`.

## Chapter 6. Electrical neurons and propagation

Question: What changes when excitation is modeled rather than labeled?

Book sections: 6.4, 6.6, 6.7. Primary model: `hh`.

Run `python run.py run hh --out runs/chapter-06`.

Canonical 6.3 °C squid-axon kinetics, not mammalian calibration. V is in mV relative to an absolute rest convention near −65 mV; ENa=50, EK=−77, EL=−54.387 mV. RK4 steps end exactly on pulse boundaries. Integrating all signed currents with the same quadrature enables a charge residual; the method does not simulate axonal propagation.

Research exercise: record the default result, choose one parameter inside its contract, predict how the result should change, then execute the modified model. Retain a case that contradicts the first prediction. Separate an algebraic consequence of the model from a claim about a biological system.

Provenance: source chapter SHA-256 `5f362995dedd7263c4a97dd3070b6531369f9e8b18a4bc09102635ac7ac7848c`.

## Chapter 7. Synapses, glia and the cellular community

Question: Why does a probabilistic synapse have failures even at fixed parameters?

Book sections: 7.2, 7.3. Primary model: `release`.

Run `python run.py run release --out runs/chapter-07`.

The simulation uses independent fixed-probability release sites. Exact probabilities and finite-sample frequencies are reported side by side. No vesicle depletion, facilitation or correlated release is fitted.

Research exercise: record the default result, choose one parameter inside its contract, predict how the result should change, then execute the modified model. Retain a case that contradicts the first prediction. Separate an algebraic consequence of the model from a claim about a biological system.

Provenance: source chapter SHA-256 `3c07ec4bf674b81b5cf49759924be21c408923a0b2782edf1cbc6f5d070397a8`.

## Chapter 8. Sensation and active perception

Question: Can reports change without a change in sensory sensitivity?

Book sections: 8.15. Primary model: `detection`.

Run `python run.py run detection --out runs/chapter-08`.

Change criterion without changing d′ to isolate response policy from sensitivity. Balanced task accuracy is not perceptual consciousness, and d′ does not identify a neural circuit.

Research exercise: record the default result, choose one parameter inside its contract, predict how the result should change, then execute the modified model. Retain a case that contradicts the first prediction. Separate an algebraic consequence of the model from a claim about a biological system.

Provenance: source chapter SHA-256 `b242c2d9537703a7d447cd2a8fd5f6aad1ebc1fed8c7f5bd14335214a81e059c`.

## Chapter 9. Movement and feedback control

Question: How does delay change a simple tracking controller?

Book sections: 9.7, 9.15. Primary model: `motor`.

Run `python run.py run motor --out runs/chapter-09`.

Use the same disturbance and measurement-noise realizations in both arms. A delay can change stability and control error, but no universal physiological delay constant or best controller is inferred.

Research exercise: record the default result, choose one parameter inside its contract, predict how the result should change, then execute the modified model. Retain a case that contradicts the first prediction. Separate an algebraic consequence of the model from a claim about a biological system.

Provenance: source chapter SHA-256 `4f13230dd812c2cd56690c74131699d67fc6975d0294f808cfcfbccd5a310a94`.

## Chapter 10. Interoception and bodily regulation

Question: Can a delayed internal estimate maintain the same resource pool?

Book sections: 10.1, 10.15. Primary model: `body`.

Run `python run.py run body --out runs/chapter-10`.

The cumulative ledger distinguishes successful regulation from hidden resource depletion. The state and costs are dimensionless. Failure at exhaustion is reported, not clipped to a visually acceptable trace.

Research exercise: record the default result, choose one parameter inside its contract, predict how the result should change, then execute the modified model. Retain a case that contradicts the first prediction. Separate an algebraic consequence of the model from a claim about a biological system.

Provenance: source chapter SHA-256 `25f75045c06558da9f5d6dc01fc4b6d0ecf3f31d7119180409412ab509376fc4`.

## Chapter 11. Learning, reconstruction and forgetting

Question: When does pattern completion recover, distort or forget a cue?

Book sections: 11.9, 11.17. Primary model: `attractor`.

Run `python run.py run attractor --out runs/chapter-11`.

Asynchronous updates in a symmetric network should not increase this Lyapunov function. Its E is not measured metabolic energy. A recovered pattern demonstrates this constructed retrieval task, not human autobiographical memory.

Research exercise: record the default result, choose one parameter inside its contract, predict how the result should change, then execute the modified model. Retain a case that contradicts the first prediction. Separate an algebraic consequence of the model from a claim about a biological system.

Provenance: source chapter SHA-256 `39ebaf784b81a6e13334688b4295296412e1c7edfe61935210d987be881db09f`.

## Chapter 12. Value, affect and choice

Question: How does a learned expectation change when reward stops?

Book sections: 12.3, 12.5. Primary model: `td`.

Run `python run.py run td --out runs/chapter-12`.

The one-state reward expectation is a deliberately reduced prediction-error model. Changing outcomes produces adaptation, but the code does not identify dopamine, motivation or moral value from this scalar.

Research exercise: record the default result, choose one parameter inside its contract, predict how the result should change, then execute the modified model. Retain a case that contradicts the first prediction. Separate an algebraic consequence of the model from a claim about a biological system.

Provenance: source chapter SHA-256 `dbdf66208918a3c64601fea30c4bf984ff7c04f97d7ccb3c2e9601478cab6589`.

## Chapter 13. Sleep, rhythms and a lifetime

Question: How are a saturating pressure and an oscillating phase different?

Book sections: 13.2, 13.3. Primary model: `sleep`.

Run `python run.py run sleep --out runs/chapter-13`.

Exact interval updates reduce numerical drift. The schedule is imposed, not predicted. It is not a sleep prescription or a full theory of sleep functions and disorders.

Research exercise: record the default result, choose one parameter inside its contract, predict how the result should change, then execute the modified model. Retain a case that contradicts the first prediction. Separate an algebraic consequence of the model from a claim about a biological system.

Provenance: source chapter SHA-256 `b89ae1332116f058a4efb506f1d4f22e48a5f930a1e5c14c5c7ce9341a5830ca`.

## Chapter 14. Damage and functional repair

Question: Does a local voltage report the state of a distributed cable?

Book sections: 14.7. Primary model: `cable`.

Run `python run.py run cable --out runs/chapter-14`.

Voltage is displacement from rest. Identical passive compartments conserve axial charge internally. The sum of input minus leak matches capacitive change. No active conduction velocity, myelin geometry or disease diagnosis is calculated.

Research exercise: record the default result, choose one parameter inside its contract, predict how the result should change, then execute the modified model. Retain a case that contradicts the first prediction. Separate an algebraic consequence of the model from a claim about a biological system.

Provenance: source chapter SHA-256 `9088881caa5015c74eb469b0e839d6f40e04792c0c95a8e13382fd58a284fdb9`.

## Chapter 15. Language, other people and culture

Question: How much evidence is added by another correlated report?

Book sections: 15.10, 15.14. Primary model: `social`.

Run `python run.py run social --out runs/chapter-15`.

This is a variance-equivalence calculation under equal variance and pairwise correlation, not a universal measure of credibility. Thirty correlated reports need not equal thirty independent observations.

Research exercise: record the default result, choose one parameter inside its contract, predict how the result should change, then execute the modified model. Retain a case that contradicts the first prediction. Separate an algebraic consequence of the model from a claim about a biological system.

Provenance: source chapter SHA-256 `43936df8bac76fbc3cf106441216763e114936815c0f77e040c6d51f1128271c`.

## Chapter 16. Consciousness, self and testable distinctions

Question: Can a system discriminate while its report channel is unavailable?

Book sections: 16.3, 16.5, 16.17. Primary model: `access`.

Run `python run.py run access --out runs/chapter-16`.

The output distinguishes task correctness, report availability and correctness conditional on report. Nothing in the generator creates an experience variable. The experiment cannot infer awareness from failure to report.

Research exercise: record the default result, choose one parameter inside its contract, predict how the result should change, then execute the modified model. Retain a case that contradicts the first prediction. Separate an algebraic consequence of the model from a claim about a biological system.

Provenance: source chapter SHA-256 `9dfdb61cc0053cd08e85939efee25381aa2840964f024a0814b61233adc44cde`.

## Chapter 17. Connectomes, causal models and neural engineering

Question: Which measurement distinguishes two output-equivalent systems?

Book sections: 17.7, 17.8, 17.9. Primary model: `identify`.

Run `python run.py run identify --out runs/chapter-17`.

Adding selective observation increases rank. A perfect fit to y is compatible with different hidden mechanisms. This exact counterexample concerns observability, not every practical parameter-identification problem.

Research exercise: record the default result, choose one parameter inside its contract, predict how the result should change, then execute the modified model. Retain a case that contradicts the first prediction. Separate an algebraic consequence of the model from a claim about a biological system.

Provenance: source chapter SHA-256 `03e14e1469ae14cf69668874c5640c07331ff40ebf8f00a5efb6aa0e759d0623`.

## Chapter 18. Energy, information and possible minds

Question: When is an energy-to-information comparison dimensionally valid?

Book sections: 18.4, 18.8, 18.11. Primary model: `energy`.

Run `python run.py run energy --out runs/chapter-18`.

Match J/mol to J/event before forming a dimensionless ratio. Landauer supplies a conditional erasure scale, not actual brain computation cost. Capacitive energy, channel dissipation and restoration budgets must not be simply summed as total metabolism.

Research exercise: record the default result, choose one parameter inside its contract, predict how the result should change, then execute the modified model. Retain a case that contradicts the first prediction. Separate an algebraic consequence of the model from a claim about a biological system.

Provenance: source chapter SHA-256 `938afa6711a394f00f3f0efb0c590a50d7c3669689afa261e5213f4be6daa431`.

## Cross-chapter programmes

Programme I (`mapping`) primarily operationalizes section 18.16 and connects sensation, action, feedback and learning. Programme II (`revision`) connects sections 11.9–11.17, 17.17 and 18.15–18.16 without equating software event history with neuronal memory. Programme III (`tournament`) connects model identifiability and explicit scale bridges in chapters 17–18.

The `candidate` experiment retains a declared, falsifiable energy-information feature. It does not silently replace it with an established law, and it does not establish an independent physical field. The `fit` command connects the membrane chapter to actual acquisition metadata and held-out prediction.
