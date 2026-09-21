#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALLOWED = {"Sourced", "Assumed", "Unresolved"}
EXPECTED = {
    "36": {"elements": 116, "connections": 296, "nodes": 75},
    "39": {"elements": 114, "connections": 292, "nodes": 75},
}


def load_json(path: Path):
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def load_csv(path: Path):
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def source_ids(raw: str):
    return [x.strip() for x in raw.split(";") if x.strip()]


def validate_ledger(candidate: str, sources: dict) -> tuple[int, int]:
    base = ROOT / "research" / "candidates" / candidate
    ledger = load_csv(base / "ledger.csv")
    connections = load_csv(base / "connections.csv")
    expected = EXPECTED[candidate]

    assert len(ledger) == expected["elements"], (
        f"#{candidate}: expected {expected['elements']} elements, got {len(ledger)}"
    )
    assert len(connections) == expected["connections"], (
        f"#{candidate}: expected {expected['connections']} terminal connections, "
        f"got {len(connections)}"
    )

    elements = {}
    for row in ledger:
        eid = row["id"]
        assert eid and eid not in elements, f"#{candidate}: duplicate/blank element id {eid!r}"
        assert row["value_status"] in ALLOWED
        assert row["connection_status"] in ALLOWED
        assert row["historical_status"] in ALLOWED
        pins = json.loads(row["pins"])
        assert isinstance(pins, dict) and pins, f"#{candidate} {eid}: pins must be a non-empty object"
        elements[eid] = pins
        for sid in source_ids(row["source_ids"]):
            assert sid in sources, f"#{candidate} {eid}: unknown source {sid}"

    seen_terminals = set()
    nodes = set()
    for row in connections:
        eid, terminal, node = row["element"], row["terminal"], row["node"]
        assert eid in elements, f"#{candidate}: connection references unknown element {eid}"
        assert terminal in elements[eid], f"#{candidate} {eid}: unknown terminal {terminal}"
        assert elements[eid][terminal] == node, (
            f"#{candidate} {eid}.{terminal}: ledger node {elements[eid][terminal]!r} "
            f"!= connection node {node!r}"
        )
        key = (eid, terminal)
        assert key not in seen_terminals, f"#{candidate}: duplicate terminal connection {key}"
        seen_terminals.add(key)
        nodes.add(node)
        assert row["status"] in ALLOWED
        for sid in source_ids(row["source_ids"]):
            assert sid in sources, f"#{candidate} {eid}.{terminal}: unknown source {sid}"

    expected_terminals = {
        (eid, terminal) for eid, pins in elements.items() for terminal in pins
    }
    assert seen_terminals == expected_terminals, (
        f"#{candidate}: terminal coverage mismatch; "
        f"missing={sorted(expected_terminals-seen_terminals)[:10]}, "
        f"extra={sorted(seen_terminals-expected_terminals)[:10]}"
    )
    assert len(nodes) == expected["nodes"], (
        f"#{candidate}: expected {expected['nodes']} nodes, got {len(nodes)}"
    )

    return len(ledger), len(connections)


def main() -> int:
    sources = load_json(ROOT / "research" / "sources.json")
    assert sources, "source registry is empty"

    manifests = [
        ROOT / "research" / "candidates" / "39" / "manifest.json",
        ROOT / "research" / "candidates" / "36" / "manifest.json",
    ]

    ids = set()
    for path in manifests:
        model = load_json(path)
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

    totals = [validate_ledger(candidate, sources) for candidate in ("36", "39")]
    elements = sum(x[0] for x in totals)
    terminals = sum(x[1] for x in totals)
    assert elements == 230, f"expected 230 total elements, got {elements}"
    assert terminals == 588, f"expected 588 total terminal connections, got {terminals}"

    print(
        f"Validated {len(manifests)} manifests, {len(sources)} source records, "
        f"{elements} elements and {terminals} terminal connections."
    )
    print("Historical and electrical validation flags remain false, as required.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
