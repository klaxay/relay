"""Tests for applying and reverting the initial schema migration."""

from __future__ import annotations

import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


class MigrationTests(unittest.TestCase):
    def test_initial_migration_creates_and_drops_durable_tables(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            database_path = Path(directory) / "relay.db"
            database_url = f"sqlite+pysqlite:///{database_path}"
            config = Config(str(REPOSITORY_ROOT / "alembic.ini"))

            with patch.dict(os.environ, {"RELAY_DATABASE_URL": database_url}):
                command.upgrade(config, "head")
                command.check(config)
                engine = create_engine(database_url)
                try:
                    self.assertEqual(
                        set(inspect(engine).get_table_names()),
                        {
                            "alembic_version",
                            "workflow_definitions",
                            "workflow_executions",
                            "task_executions",
                        },
                    )
                finally:
                    engine.dispose()

                command.downgrade(config, "base")
                engine = create_engine(database_url)
                try:
                    self.assertEqual(
                        inspect(engine).get_table_names(), ["alembic_version"]
                    )
                finally:
                    engine.dispose()


if __name__ == "__main__":
    unittest.main()
