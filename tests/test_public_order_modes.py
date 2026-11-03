"""公开教程的入门数据模式与显式数据库模式边界。"""
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from app.repositories.order_repository import OrderRepositoryError, fetch_order_from_db


class PublicOrderModesTests(unittest.TestCase):
    @patch('app.repositories.order_repository.psycopg.connect')
    @patch('app.repositories.order_repository.get_settings', return_value=SimpleNamespace(order_storage_backend='demo'))
    def test_demo_is_offline_and_returns_a_copy(self, settings, connect):
        order = fetch_order_from_db('10001')
        self.assertEqual(order['tracking_number'], 'SF1234567890')
        order['status'] = 'changed'
        self.assertEqual(fetch_order_from_db('10001')['status'], '已发货')
        self.assertIsNone(fetch_order_from_db('99999'))
        connect.assert_not_called()

    @patch('app.repositories.order_repository.get_settings', return_value=SimpleNamespace(
        order_storage_backend='postgres', postgres_password=None))
    def test_database_configuration_failure_never_falls_back_to_demo(self, settings):
        with self.assertRaises(OrderRepositoryError):
            fetch_order_from_db('10001')
