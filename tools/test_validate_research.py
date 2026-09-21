#!/usr/bin/env python3
import copy
import unittest

from tools import validate_research as vr


class ProvenanceValidationTests(unittest.TestCase):
    def setUp(self):
        self.sources = {
            "REF39": {
                "title": "reference",
                "kind": "manufacturer drawing",
                "status": "reference-stock",
                "scope": "39",
                "fingerprint_status": "not-applicable",
            },
            "ENG39": {
                "title": "assumption",
                "kind": "engineering assumption",
                "status": "assumption-only",
                "scope": "39",
                "fingerprint_status": "not-applicable",
            },
            "ENG36": {
                "title": "assumption",
                "kind": "engineering assumption",
                "status": "assumption-only",
                "scope": "36",
                "fingerprint_status": "not-applicable",
            },
        }
        self.ledger = {
            "E1": {
                "id": "E1",
                "value": "2.0",
                "unit": "ohm",
                "pins": '{"a": "N1", "b": "0"}',
            }
        }

    def base_manifest(self):
        return {
            "candidate_id": "test",
            "historically_verified": False,
            "electrically_validated": False,
            "simulation_ready": False,
            "foundation": {
                "family": "test",
                "status": "Sourced",
                "source_ids": ["REF39"],
                "specimen_match": "Unresolved",
            },
            "working_architecture": {
                "status": "Assumed",
                "support": ["ENG39"],
            },
            "candidate_signal_path": [
                "a", "b", "c", "d", "e", "f"
            ],
            "known_alternatives": [],
        }

    def valid_alt(self):
        return {
            "item": "test alternative",
            "candidates": ["A", "B"],
            "status": "Unresolved",
            "selected_in_candidate": "B",
            "selection_status": "Sourced",
            "selection_source_ids": ["REF39"],
            "model_bindings": [
                {
                    "kind": "element_value",
                    "element": "E1",
                    "expected": 2.0,
                    "unit": "ohm",
                }
            ],
        }

    def test_unknown_source_status_is_rejected(self):
        sources = copy.deepcopy(self.sources)
        sources["REF39"]["status"] = "refernece-stock"
        with self.assertRaises(AssertionError):
            vr.validate_source_registry(sources)

    def test_cross_candidate_source_is_rejected(self):
        with self.assertRaises(AssertionError):
            vr.validate_source_boundary(
                "36", ["ENG39"], self.sources, "cross-scope"
            )

    def test_sourced_claim_cannot_use_assumption_only_source(self):
        with self.assertRaises(AssertionError):
            vr.validate_claim_sources(
                ["Sourced"], ["ENG39"], self.sources, "assumption-as-evidence"
            )

    def test_historical_sourced_status_is_evidence_gated(self):
        with self.assertRaises(AssertionError):
            vr.validate_claim_sources(
                ["Unresolved", "Unresolved", "Sourced"],
                ["ENG39"],
                self.sources,
                "historical claim",
            )

    def test_sourced_architecture_requires_evidence(self):
        model = self.base_manifest()
        model["working_architecture"] = {
            "status": "Sourced",
            "support": [],
        }
        with self.assertRaises(AssertionError):
            vr.validate_manifest(
                model, "39", self.sources, self.ledger, "manifest"
            )

    def test_architecture_obeys_candidate_scope(self):
        model = self.base_manifest()
        model["working_architecture"] = {
            "status": "Assumed",
            "support": ["ENG36"],
        }
        with self.assertRaises(AssertionError):
            vr.validate_manifest(
                model, "39", self.sources, self.ledger, "manifest"
            )

    def test_selected_alternative_must_be_declared_candidate(self):
        alt = self.valid_alt()
        alt["selected_in_candidate"] = "C"
        with self.assertRaises(AssertionError):
            vr.validate_alternative(
                alt, "39", self.sources, self.ledger, "alternative"
            )

    def test_selection_status_cannot_be_unresolved(self):
        alt = self.valid_alt()
        alt["selection_status"] = "Unresolved"
        with self.assertRaises(AssertionError):
            vr.validate_alternative(
                alt, "39", self.sources, self.ledger, "alternative"
            )

    def test_selected_alternative_requires_model_binding(self):
        alt = self.valid_alt()
        alt["model_bindings"] = []
        with self.assertRaises(AssertionError):
            vr.validate_alternative(
                alt, "39", self.sources, self.ledger, "alternative"
            )

    def test_element_value_binding_detects_drift(self):
        alt = self.valid_alt()
        alt["model_bindings"][0]["expected"] = 3.0
        with self.assertRaises(AssertionError):
            vr.validate_alternative(
                alt, "39", self.sources, self.ledger, "alternative"
            )

    def test_pin_node_binding_detects_drift(self):
        alt = self.valid_alt()
        alt["model_bindings"] = [
            {
                "kind": "pin_node",
                "element": "E1",
                "pin": "a",
                "node": "WRONG",
            }
        ]
        with self.assertRaises(AssertionError):
            vr.validate_alternative(
                alt, "39", self.sources, self.ledger, "alternative"
            )

    def test_element_absent_binding_detects_presence(self):
        alt = self.valid_alt()
        alt["model_bindings"] = [
            {"kind": "element_absent", "element": "E1"}
        ]
        with self.assertRaises(AssertionError):
            vr.validate_alternative(
                alt, "39", self.sources, self.ledger, "alternative"
            )

    def test_valid_selected_alternative_is_accepted(self):
        alt = self.valid_alt()
        vr.validate_alternative(
            alt, "39", self.sources, self.ledger, "alternative"
        )


if __name__ == "__main__":
    unittest.main()
