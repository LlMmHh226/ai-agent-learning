from types import SimpleNamespace
import unittest
from unittest.mock import patch

import psycopg
from pydantic import SecretStr

from app.repositories.order_repository import OrderRepositoryError, fetch_order_from_db


class OrderRepositoryTests(unittest.TestCase):
    @patch("app.repositories.order_repository.psycopg.connect")
    @patch("app.repositories.order_repository.get_settings")
    def test_missing_password_fails_without_attempting_database_connection(
        self, settings, connect
    ) -> None:
        settings.return_value = SimpleNamespace(order_storage_backend="postgres", postgres_password=None)

        with self.assertRaisesRegex(OrderRepositoryError, "POSTGRES_PASSWORD"):
            fetch_order_from_db("10001")

        connect.assert_not_called()

    @patch("app.repositories.order_repository.psycopg.connect")
    @patch("app.repositories.order_repository.get_settings")
    def test_driver_failure_is_distinct_from_no_matching_record(
        self, settings, connect
    ) -> None:
        settings.return_value = SimpleNamespace(
            order_storage_backend="postgres",
            postgres_host="localhost",
            postgres_port=15432,
            postgres_db="agent_learning",
            postgres_user="root",
            postgres_password=SecretStr("unit-test-only"),
        )
        connect.side_effect = psycopg.OperationalError("database unavailable")

        with self.assertRaises(OrderRepositoryError) as raised:
            fetch_order_from_db("10001")

        self.assertIsInstance(raised.exception.__cause__, psycopg.OperationalError)
        self.assertNotIn("unit-test-only", str(raised.exception))


if __name__ == "__main__":
    unittest.main()
