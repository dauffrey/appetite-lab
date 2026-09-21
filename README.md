# Appetite Lab

**Appetite Lab** is a research and engineering project to reconstruct S.I.R. **#39** and **#36** as historically disciplined, component-level virtual guitar amplifiers that can ultimately be played in real time from a Windows PC.

The project deliberately separates **evidence** from **engineering assumptions**. A circuit value, connection, or historical claim is never promoted to fact merely because it sounds plausible or produces the desired tone.

## Targets

### S.I.R. #39
Working reconstruction target: a Marshall 1959T/Super Tremolo lineage amplifier associated with Tim Caswell. The current research hypothesis treats the tremolo circuitry as the resource repurposed into additional preamp gain. Exact original wiring and component values remain partly unresolved.

### S.I.R. #36
Working reconstruction target: a non-tremolo Marshall Super Lead lineage amplifier associated with Frank Levi. The current research hypothesis requires an additional gain stage plus capacitor/value changes. The exact Levi modification has not been recovered and must remain explicitly hypothetical until supported.

## Research rules

Every model element and connection must be one of:

- **Sourced** — supported by an identified source.
- **Assumed** — explicit engineering hypothesis.
- **Unresolved** — unknown; never silently defaulted.

Observed screenshot captions and user-supplied historical accounts are recorded separately from independently sourced technical evidence.

## Repository structure

```
.github/                    CI and Copilot instructions
docs/                       research method, roadmap, source boundaries
research/
  sources.json              source registry
  candidates/
    39/manifest.json        #39 candidate architecture
    36/manifest.json        #36 candidate architecture
tools/                      structural validation
```

## Current status

**Research baseline only.** The v0.2 ledgers are now imported in full: **230 circuit elements and 588 terminal connections** across the independent #36 and #39 candidates. Neither candidate is historically authenticated, electrically validated, or ready for real-time audio simulation.

Immediate work:

1. independently review the imported v0.2 ledgers against stock 1959T and 1959 reference transcriptions;
2. enumerate candidate modification deltas;
3. validate DC operating points and feedback polarity;
4. add reviewed ECC83/EL34/rectifier and transformer models;
5. build a reference circuit solver;
6. only then optimize toward real-time Windows guitar playback.

## Goal

The end state is not a generic “Appetite-style” amp sim. It is an auditable virtual reconstruction in which the sound, circuit measurements, uncertainty, and provenance all derive from the same explicit electrical model.
