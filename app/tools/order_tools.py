FAKE_ORDERS: dict[str, dict[str, str]] = {
    "10001": {
        "status": "已发货",
        "product": "机械键盘",
        "tracking_number": "SF1234567890",
    },
    "10002": {
        "status": "待发货",
        "product": "无线鼠标",
        "tracking_number": "",
    },
    "10003": {
        "status": "已完成",
        "product": "显示器",
        "tracking_number": "YT9876543210",
    },
}

GET_ORDER_STATUS_TOOL = {
    "type": "function",
    "function": {
        "name": "get_order_status",
        "description": "根据订单编号查询订单状态、商品名称和物流单号",
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "需要查询的订单编号，例如10001",
                }
            },
            "required": ["order_id"],
            "additionalProperties": False,
        },
    },
}

def get_order_status(order_id: str) -> dict[str, object]:
    order = FAKE_ORDERS.get(order_id)

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
