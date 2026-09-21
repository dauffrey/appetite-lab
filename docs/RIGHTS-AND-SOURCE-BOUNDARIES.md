# Rights and source boundaries

Appetite Lab should contain our original research structure, normalized facts, code, tests, hashes, and links.

Do not assume a schematic found online is licensed for republication. Where redistribution rights are unclear:

- store the source URL and access date;
- store a cryptographic fingerprint when we have lawfully accessed the source;
- record only the facts needed for our research with appropriate attribution;
- do not commit the third-party image/PDF itself.

Marshall and other product/artist names may be trademarks of their respective owners. This repository is an independent research project and should not imply endorsement or affiliation.

Source provenance and copyright permission are separate questions: a source can be technically useful but unsuitable for redistribution.

## Machine-readable source metadata

Each source registry entry declares a provenance `status` and a `scope` of `36`, `39`, or `shared`. Candidate-scoped sources must not be used by the other reconstruction unless the source record itself is deliberately reclassified after review.

URL-backed sources record an `accessed_at` date. The `fingerprint_status` field is explicit:

- `verified` — a stable artifact fingerprint has been captured and recorded;
- `pending` — the source was accessed but a stable artifact fingerprint has not yet been captured;
- `not-applicable` — the source is an internal assumption/evidence record rather than an externally retrieved artifact.

A `pending` fingerprint is not equivalent to a verified hash. Resolving pending fingerprints remains part of the Phase 0 evidence-inventory work.

