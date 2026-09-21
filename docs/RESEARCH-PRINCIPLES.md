# Research principles

## Objective

Reconstruct S.I.R. #39 and #36 in sufficient electrical detail that a reference solver can reproduce their candidate behavior and, eventually, a realtime implementation can be validated against that reference.

## Evidence classes

### Sourced
A value or connection is visible in a cited drawing, documented in a direct account, or obtained from an admitted measurement. “Sourced” means the source supports the statement; it does not automatically prove the source describes the original rental amplifier.

### Assumed
A deliberate engineering completion or reconstruction choice. Assumptions must be versioned and testable.

### Unresolved
A fact or parameter that has not been established. Unresolved values stay unresolved until evidence or a declared parameter-fit process changes their status.

## Historical versus predictive validity

Two different questions must remain separate:

1. **Historical:** was this component or topology actually present in the original amplifier?
2. **Predictive:** does this model reproduce measured electrical/audio behavior?

A model can become predictively strong while some historical details remain unresolved.

## Current architecture claims

### #39
Current working account:
- 1959T/Super Tremolo family foundation;
- tremolo function removed/disabled;
- existing tremolo valve circuitry repurposed into the audio gain path;
- exact section allocation, switching, and many values unresolved.

### #36
Current working account:
- non-tremolo Super Lead family foundation;
- additional gain stage required because no tremolo valve resource existed to repurpose;
- capacitor/value changes reported;
- exact added-stage implementation and capacitor changes unresolved.

These claims are research constraints, not authenticated schematics.

## Simulation admission gates

Before a candidate may be called simulation-ready:

- connectivity independently reviewed;
- all required device laws declared;
- DC operating point converges;
- output-valve dissipation checked;
- negative-feedback polarity verified;
- small-signal response checked;
- transient overload and blocking behavior tested;
- timestep/oversampling convergence demonstrated;
- unresolved transformer and supply assumptions documented.
