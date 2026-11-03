# 课程：step_03_python_order_lookup.md；访问范围：访问自己启动的教学数据库；不请求模型（正式聊天请求除外）。
"""Python连接PostgreSQL：学习演示执行查询和取回一行的核心代码。"""

import argparse
import json

import psycopg
from psycopg.rows import dict_row


def connect_learning_db():
    """读取学习目录的配置，连接已有的agent_learning数据库。"""
    from app.core.config import get_settings
    settings = get_settings()
    if settings.postgres_password is None or not settings.postgres_password.get_secret_value():
        raise RuntimeError("请在项目根目录.env中填写POSTGRES_PASSWORD。")
    return psycopg.connect(
        host=settings.postgres_host, port=settings.postgres_port,
        dbname=settings.postgres_db, user=settings.postgres_user,
        password=settings.postgres_password.get_secret_value(),
        row_factory=dict_row, connect_timeout=5,
    )


def fetch_order_from_db(order_id: str) -> dict[str, object] | None:
    """按订单号读一行；找到时返回字典，找不到时返回None。"""
    with connect_learning_db() as connection:
        with connection.cursor() as cursor:
            # 关键步骤 1：定义sql，查public.orders的四列，订单号位置使用%s占位符。
            sql = "SELECT order_id, status, product, tracking_number FROM public.orders WHERE order_id = %s"
            # 关键步骤 2：调用cursor.execute，第二个参数传包含order_id的单元素元组。
            cursor.execute(sql, (order_id,))
            # 关键步骤 3：调用cursor.fetchone，把返回值交给本函数的调用者。
            return cursor.fetchone()


def main() -> None:
    parser = argparse.ArgumentParser(description="从PostgreSQL学习库查询一条订单。")
    parser.add_argument("--order-id", default="10001", help="要查询的订单号，默认10001。")
    args = parser.parse_args()

    order = fetch_order_from_db(args.order_id)
    print(json.dumps(order, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
