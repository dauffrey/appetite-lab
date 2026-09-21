#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALLOWED = {"Sourced", "Assumed", "Unresolved"}

def load(path: Path):
    with path.open(encoding="utf-8") as f:
        return json.load(f)

def main() -> int:
    sources = load(ROOT / "research" / "sources.json")
    assert sources, "source registry is empty"

    manifests = [
        ROOT / "research" / "candidates" / "39" / "manifest.json",
        ROOT / "research" / "candidates" / "36" / "manifest.json",
    ]

    ids = set()
    for path in manifests:
        model = load(path)
        cid = model["candidate_id"]
        assert cid not in ids, f"duplicate candidate_id: {cid}"
        ids.add(cid)
        assert model["historically_verified"] is False
        assert model["electrically_validated"] is False
        assert model["simulation_ready"] is False

        foundation = model["foundation"]
        assert foundation["status"] in ALLOWED
        for sid in foundation.get("source_ids", []):
            assert sid in sources, f"{path}: unknown source {sid}"

        architecture = model["working_architecture"]
        assert architecture["status"] in ALLOWED
        for sid in architecture.get("support", []):
            assert sid in sources, f"{path}: unknown support source {sid}"

        for alt in model.get("known_alternatives", []):
            assert alt["status"] in ALLOWED

        assert len(model["candidate_signal_path"]) >= 6

    print(f"Validated {len(manifests)} candidate manifests and {len(sources)} source records.")
    print("Historical and electrical validation flags remain false, as required.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
