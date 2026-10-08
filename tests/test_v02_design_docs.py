"""Contract checks for the v0.2 design milestone documentation."""

from __future__ import annotations

from pathlib import Path
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


class DurableExecutionDesignTests(unittest.TestCase):
    def test_architecture_defines_durable_record_and_recovery_contract(self) -> None:
        architecture = (REPOSITORY_ROOT / "docs/ARCHITECTURE.md").read_text()
        design = architecture.split("## v0.2 durable execution design", 1)[1]

        for required_decision in (
            "Persist a workflow definition separately from each run.",
            "It does not\nstore Python callables.",
            "JSON-compatible task inputs and results are durable",
            "A task left `running` is\nchanged to `failed`",
            "Pending tasks in that execution become `blocked`",
            "already terminal\ntask records remain unchanged",
            "Recovery applies only to nonterminal runs and is safe to repeat",
            "does not resume tasks,\nretry failures",
        ):
            with self.subTest(decision=required_decision):
                self.assertIn(required_decision, design)

    def test_current_state_tracks_v02_milestone_progress(self) -> None:
        current = (REPOSITORY_ROOT / "CURRENT.md").read_text()

        self.assertIn("**Current Version:** v0.2", current)
        self.assertIn("Milestone 1 — Define durable records and restart behavior. COMPLETE.", current)
        self.assertIn("Milestone 2 — Build the PostgreSQL schema and persistence layer.", current)


if __name__ == "__main__":
    unittest.main()
