"""Integration coverage for Relay's documented local entry point."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


class LocalEntryPointTests(unittest.TestCase):
    def test_bundled_example_exits_successfully_and_reports_outcome(self) -> None:
        completed = subprocess.run(
            [sys.executable, "main.py"],
            cwd=REPOSITORY_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(
            completed.stdout,
            "Workflow example: succeeded\n"
            "- format: succeeded result='RELAY' error=None\n"
            "- publish: succeeded result='done!' error=None\n",
        )
        self.assertEqual(completed.stderr, "")


if __name__ == "__main__":
    unittest.main()
