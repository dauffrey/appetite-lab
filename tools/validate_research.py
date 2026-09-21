#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALLOWED = {"Sourced", "Assumed", "Unresolved"}
ALLOWED_SELECTION_STATUSES = {"Sourced", "Assumed"}
ALLOWED_SOURCE_STATUSES = {
    "reference-stock",
    "adjacent-period-reference",
    "candidate-only",
    "architecture-history",
    "qualified",
    "discovery-lead-only",
    "user-evidence",
    "assumption-only",
}
EVIDENTIARY_SOURCE_STATUSES = {
    "reference-stock",
    "adjacent-period-reference",
    "candidate-only",
    "architecture-history",
    "qualified",
    "user-evidence",
}
ALLOWED_SOURCE_SCOPES = {"shared", "36", "39"}
ALLOWED_FINGERPRINT_STATES = {"verified", "pending", "not-applicable"}
EXPECTED = {
    "36": {"elements": 116, "connections": 296, "nodes": 75},
    "39": {"elements": 114, "connections": 292, "nodes": 75},
}
SOURCE_LOCATOR_ALIASES = {
    "T70": "T70",
    "L70": "L70",
    "P78": "P78",
    "W78": "W78",
    "Cerberus": "CER",
    "ENG36": "ENG36",
    "ENG39": "ENG39",
}


def load_json(path: Path):
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def load_csv(path: Path):
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def source_ids(raw: str):
    return [x.strip() for x in raw.split(";") if x.strip()]


def validate_source_registry(sources: dict) -> None:
    assert sources, "source registry is empty"
    for sid, record in sources.items():
        status = record.get("status")
        scope = record.get("scope")
        fingerprint_status = record.get("fingerprint_status")
        assert status in ALLOWED_SOURCE_STATUSES, (
            f"{sid}: unknown source status {status!r}; provenance classes are fail-closed"
        )
        assert scope in ALLOWED_SOURCE_SCOPES, f"{sid}: invalid source scope {scope!r}"
        assert fingerprint_status in ALLOWED_FINGERPRINT_STATES, (
            f"{sid}: invalid fingerprint_status {fingerprint_status!r}"
        )
        if record.get("url"):
            assert record.get("accessed_at"), f"{sid}: URL source requires accessed_at"
            assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", record["accessed_at"]), (
                f"{sid}: accessed_at must use YYYY-MM-DD"
            )
            assert fingerprint_status in {"verified", "pending"}, (
                f"{sid}: URL source fingerprint must be verified or explicitly pending"
            )
        if fingerprint_status == "verified":
            fingerprint = record.get("fingerprint", "")
            assert fingerprint, f"{sid}: verified fingerprint requires fingerprint value"


def ensure_source_ids(ids: list[str], sources: dict, context: str) -> None:
    for sid in ids:
        assert sid in sources, f"{context}: unknown source {sid}"


def validate_source_boundary(
    candidate: str, ids: list[str], sources: dict, context: str
) -> None:
    crossed = sorted(
        sid
        for sid in ids
        if sources[sid].get("scope") not in {"shared", candidate}
    )
    assert not crossed, (
        f"{context}: candidate #{candidate} references source(s) outside its scope: {crossed}"
    )


def validate_sourced_claim(ids: list[str], sources: dict, context: str) -> None:
    assert ids, f"{context}: Sourced claim requires source_ids"
    admissible = [
        sid
        for sid in ids
        if sources[sid].get("status") in EVIDENTIARY_SOURCE_STATUSES
    ]
    assert admissible, (
        f"{context}: Sourced claim has no evidentiary source class: {ids}"
    )


def validate_claim_sources(
    statuses: list[str] | tuple[str, ...],
    ids: list[str],
    sources: dict,
    context: str,
) -> None:
    if "Sourced" in statuses:
        validate_sourced_claim(ids, sources, context)


def validate_locator(locator: str, ids: list[str], candidate: str, context: str) -> None:
    other_marker = "#39" if candidate == "36" else "#36"
    assert other_marker not in locator, (
        f"{context}: source_locator contains cross-candidate marker {other_marker}"
    )
    for token, sid in SOURCE_LOCATOR_ALIASES.items():
        if token in locator:
            assert sid in ids, (
                f"{context}: source_locator mentions {token!r} but source_ids "
                f"does not contain {sid}"
            )


def parse_ledger_value(raw: str):
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw


def validate_model_binding(
    binding: dict, ledger_by_id: dict[str, dict], context: str
) -> None:
    kind = binding.get("kind")
    element = binding.get("element")
    assert kind in {"element_exists", "element_absent", "element_value", "pin_node"}, (
        f"{context}: unknown model binding kind {kind!r}"
    )
    assert element, f"{context}: model binding requires element"

    if kind == "element_absent":
        assert element not in ledger_by_id, (
            f"{context}: expected element {element!r} to be absent"
        )
        return

    assert element in ledger_by_id, (
        f"{context}: model binding references missing element {element!r}"
    )
    row = ledger_by_id[element]

    if kind == "element_exists":
        return

    if kind == "element_value":
        expected = binding.get("expected")
        actual = parse_ledger_value(row["value"])
        assert actual == expected, (
            f"{context}: {element} value drift; expected {expected!r}, got {actual!r}"
        )
        if "unit" in binding:
            assert row["unit"] == binding["unit"], (
                f"{context}: {element} unit drift; expected {binding['unit']!r}, "
                f"got {row['unit']!r}"
            )
        return

    pins = json.loads(row["pins"])
    pin = binding.get("pin")
    node = binding.get("node")
    assert pin in pins, f"{context}: {element} has no pin {pin!r}"
    assert pins[pin] == node, (
        f"{context}: {element}.{pin} drift; expected node {node!r}, "
        f"got {pins[pin]!r}"
    )


def validate_alternative(
    alt: dict,
    candidate: str,
    sources: dict,
    ledger_by_id: dict[str, dict],
    context: str,
) -> None:
    status = alt["status"]
    assert status in ALLOWED, f"{context}: invalid alternative status {status!r}"

    alt_sources = alt.get("source_ids", [])
    ensure_source_ids(alt_sources, sources, context)
    validate_source_boundary(candidate, alt_sources, sources, context)
    validate_claim_sources([status], alt_sources, sources, context)

    candidates = alt.get("candidates")
    selected = alt.get("selected_in_candidate")
    if candidates is not None:
        assert isinstance(candidates, list) and candidates, (
            f"{context}: candidates must be a non-empty list"
        )
        assert selected is not None, (
            f"{context}: alternatives with candidates require selected_in_candidate "
            "so the instantiated model is explicit"
        )
        assert selected in candidates, (
            f"{context}: selected_in_candidate {selected!r} is not one of {candidates!r}"
        )

    if selected is not None:
        selection_status = alt.get("selection_status")
        selection_sources = alt.get("selection_source_ids", [])
        assert selection_status in ALLOWED_SELECTION_STATUSES, (
            f"{context}: selected_in_candidate requires selection_status "
            "Sourced or Assumed"
        )
        ensure_source_ids(selection_sources, sources, context)
        validate_source_boundary(candidate, selection_sources, sources, context)
        validate_claim_sources(
            [selection_status], selection_sources, sources, f"{context} selection"
        )

        bindings = alt.get("model_bindings", [])
        assert isinstance(bindings, list) and bindings, (
            f"{context}: selected_in_candidate requires non-empty model_bindings"
        )
        for index, binding in enumerate(bindings, start=1):
            validate_model_binding(
                binding, ledger_by_id, f"{context} binding[{index}]"
            )


def validate_manifest(
    model: dict,
    candidate: str,
    sources: dict,
    ledger_by_id: dict[str, dict],
    context: str,
) -> None:
    assert model["historically_verified"] is False
    assert model["electrically_validated"] is False
    assert model["simulation_ready"] is False

    foundation = model["foundation"]
    assert foundation["status"] in ALLOWED
    assert foundation.get("specimen_match") in ALLOWED
    foundation_sources = foundation.get("source_ids", [])
    ensure_source_ids(foundation_sources, sources, context)
    validate_source_boundary(candidate, foundation_sources, sources, context)
    validate_claim_sources(
        [foundation["status"]], foundation_sources, sources, f"{context} foundation"
    )

    architecture = model["working_architecture"]
    assert architecture["status"] in ALLOWED
    architecture_sources = architecture.get("support", [])
    ensure_source_ids(architecture_sources, sources, context)
    validate_source_boundary(candidate, architecture_sources, sources, context)
    validate_claim_sources(
        [architecture["status"]],
        architecture_sources,
        sources,
        f"{context} working_architecture",
    )

    for index, alt in enumerate(model.get("known_alternatives", []), start=1):
        validate_alternative(
            alt,
            candidate,
            sources,
            ledger_by_id,
            f"{context} alternative[{index}] {alt.get('item')!r}",
        )

    assert len(model["candidate_signal_path"]) >= 6


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
        context = f"#{candidate} {eid}"
        assert eid and eid not in elements, f"#{candidate}: duplicate/blank element id {eid!r}"
        assert row["value_status"] in ALLOWED
        assert row["connection_status"] in ALLOWED
        assert row["historical_status"] in ALLOWED
        pins = json.loads(row["pins"])
        assert isinstance(pins, dict) and pins, f"{context}: pins must be a non-empty object"
        elements[eid] = pins

        row_sources = source_ids(row["source_ids"])
        ensure_source_ids(row_sources, sources, context)
        validate_source_boundary(candidate, row_sources, sources, context)
        validate_locator(row["source_locator"], row_sources, candidate, context)
        validate_claim_sources(
            [
                row["value_status"],
                row["connection_status"],
                row["historical_status"],
            ],
            row_sources,
            sources,
            context,
        )

    seen_terminals = set()
    nodes = set()
    for row in connections:
        eid, terminal, node = row["element"], row["terminal"], row["node"]
        context = f"#{candidate} {eid}.{terminal}"
        assert eid in elements, f"#{candidate}: connection references unknown element {eid}"
        assert terminal in elements[eid], f"#{candidate} {eid}: unknown terminal {terminal}"
        assert elements[eid][terminal] == node, (
            f"{context}: ledger node {elements[eid][terminal]!r} "
            f"!= connection node {node!r}"
        )
        key = (eid, terminal)
        assert key not in seen_terminals, f"#{candidate}: duplicate terminal connection {key}"
        seen_terminals.add(key)
        nodes.add(node)
        assert row["status"] in ALLOWED

        connection_sources = source_ids(row["source_ids"])
        ensure_source_ids(connection_sources, sources, context)
        validate_source_boundary(candidate, connection_sources, sources, context)
        validate_locator(row["locator"], connection_sources, candidate, context)
        validate_claim_sources(
            [row["status"]], connection_sources, sources, context
        )

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
    validate_source_registry(sources)

    manifests = {
        "39": ROOT / "research" / "candidates" / "39" / "manifest.json",
        "36": ROOT / "research" / "candidates" / "36" / "manifest.json",
    }

    ids = set()
    for candidate, path in manifests.items():
        model = load_json(path)
        cid = model["candidate_id"]
        assert cid not in ids, f"duplicate candidate_id: {cid}"
        ids.add(cid)
        ledger_rows = load_csv(
            ROOT / "research" / "candidates" / candidate / "ledger.csv"
        )
        ledger_by_id = {row["id"]: row for row in ledger_rows}
        validate_manifest(
            model, candidate, sources, ledger_by_id, str(path)
        )

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
