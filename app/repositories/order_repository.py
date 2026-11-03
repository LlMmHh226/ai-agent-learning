"""按配置读取演示或PostgreSQL订单；返回字典或None，数据库失败显式报错。"""

import psycopg
from psycopg.rows import dict_row

from app.core.config import get_settings
from app.repositories.demo_orders import DEMO_ORDERS


class OrderRepositoryError(RuntimeError):
    """订单数据库配置或查询失败，与没有匹配记录区分。"""


def fetch_order_from_db(order_id: str) -> dict[str, object] | None:
    settings = get_settings()
    if settings.order_storage_backend == "demo":
        order = DEMO_ORDERS.get(order_id)
        return dict(order) if order is not None else None
    password = settings.postgres_password
    if password is None or not password.get_secret_value():
        raise OrderRepositoryError("项目根目录.env中未配置POSTGRES_PASSWORD。")

    try:
        with psycopg.connect(
            host=settings.postgres_host,
            port=settings.postgres_port,
            dbname=settings.postgres_db,
            user=settings.postgres_user,
            password=password.get_secret_value(),
            row_factory=dict_row,
            connect_timeout=5,
        ) as connection:
            with connection.cursor() as cursor:
                sql = (
                    "SELECT order_id, status, product, tracking_number "
                    "FROM public.orders WHERE order_id = %s"
                )
                cursor.execute(sql, (order_id,))
                return cursor.fetchone()
    except psycopg.Error as exc:
        raise OrderRepositoryError("订单数据库查询失败。") from exc
