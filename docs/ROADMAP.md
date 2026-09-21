# Roadmap

## Phase 0 — Research baseline
- [x] Establish separate #39 and #36 project identities.
- [x] Define provenance vocabulary.
- [x] Register primary/reference/community sources.
- [x] Record current architecture hypotheses.
- [x] Import full component and connection ledgers.
- [ ] Add screenshot evidence inventory and hashes.

## Phase 1 — Stock reference circuits
- [ ] Independently transcribe 1959T reference for #39.
- [ ] Independently transcribe non-tremolo 1959 reference for #36.
- [ ] Resolve drawing-era differences relevant to claimed 1973/1977 hardware.
- [ ] Add switch/contact states and supply networks.
- [ ] Run structural netlist checks.

## Phase 2 — Modification candidates
- [ ] #39: enumerate tremolo removal and every repurposed valve connection.
- [ ] #39: preserve published alternatives for treble/cathode networks.
- [ ] #36: enumerate extra-stage insertion alternatives.
- [ ] #36: enumerate capacitor-change hypotheses without attributing them to Levi.
- [ ] Define falsification tests for each alternative.

## Phase 3 — Reference electrical solver
- [ ] ECC83 model with provenance and tests.
- [ ] EL34 model with provenance and tests.
- [ ] Rectifier, capacitor ESR/leakage, choke and supply sag models.
- [ ] Output-transformer model: winding R/L, leakage, magnetizing branch, parasitics, saturation.
- [ ] DC, AC and transient regression tests.

## Phase 4 — Audio validation
- [ ] Calibrated guitar input level convention.
- [ ] Reactive speaker/load model.
- [ ] Reference clips and re-amping protocol.
- [ ] Compare gain envelope, harmonic spectra, frequency response and dynamics.
- [ ] Keep parameter fits separate from historical claims.

## Phase 5 — Realtime engine
- [ ] C++ circuit engine.
- [ ] Reference-vs-realtime equivalence tests.
- [ ] Oversampling/aliasing tests.
- [ ] ASIO/WASAPI low-latency audio.
- [ ] Standalone Windows application.
- [ ] VST3 wrapper.

## Phase 6 — Interactive workbench
- [ ] Live schematic view.
- [ ] Node probes and oscilloscope.
- [ ] Operating-point visualization.
- [ ] Component editing and A/B variants.
- [ ] Provenance overlay directly on the circuit.
