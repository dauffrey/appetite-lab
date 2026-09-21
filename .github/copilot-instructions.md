# GitHub Copilot instructions — Appetite Lab

This repository is a provenance-first circuit reconstruction project.

## Non-negotiable rules

1. Never present an engineering assumption as a recovered S.I.R. fact.
2. Keep #39 and #36 separate. Do not copy values or topology between them without an explicit source or an explicit Assumed label.
3. Every added component, parameter, switch state, node connection, and historical claim must carry provenance.
4. Allowed evidence statuses are exactly: `Sourced`, `Assumed`, `Unresolved`.
5. An `Unresolved` field must not receive a conventional Marshall value merely to make a simulation run.
6. Community reconstructions are candidate evidence, not authentication of the original amplifiers.
7. Tone matching may fit model parameters, but a fitted parameter is not historical proof.
8. Preserve contradictory evidence and alternatives rather than averaging them into a single “best guess”.
9. Do not redistribute third-party schematic files unless their redistribution rights are clear. Prefer links, citations, hashes, and our own normalized data.
10. Circuit-model code must distinguish physical device models, solver numerics, and real-time approximations.

## Pull requests

A circuit-changing PR must state:

- target: #39, #36, shared stock reference, or simulator;
- what changed electrically;
- source or assumption for each change;
- which uncertainties remain;
- validation performed;
- whether historical confidence changed.

No PR may claim “exact”, “verified”, or “authentic” solely from tonal similarity.
