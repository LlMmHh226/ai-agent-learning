# 课程：step_04_order_tool_result.md；访问范围：访问自己启动的教学数据库；不请求模型（正式聊天请求除外）。
"""把数据库查询结果转换成订单工具的返回格式；取值调用由学习演示。"""

import argparse
import json

from learning.postgresql.step_03_python_order_lookup import fetch_order_from_db


def get_order_status(order_id: str) -> dict[str, object]:
    # 关键步骤：把下面的None替换为调用查库函数的结果，参数使用当前收到的order_id。
    # 完成后删除raise这一行；下面的判断和返回代码沿用现有订单工具。
    order=fetch_order_from_db(order_id)

    if order is None:
        return {
            "found": False,
            "message": "没有找到该订单",
        }

    return {
        "found": True,
        "order_id": order_id,
        "status": order["status"],
        "product": order["product"],
        "tracking_number": order["tracking_number"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="用数据库结果生成订单工具响应。")
    parser.add_argument("--order-id", default="10001", help="要查询的订单号，默认10001。")
    args = parser.parse_args()

    result = get_order_status(args.order_id)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
