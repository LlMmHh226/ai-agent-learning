import logging

from app.repositories.order_repository import OrderRepositoryError, fetch_order_from_db


logger = logging.getLogger(__name__)

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
    try:
        order = fetch_order_from_db(order_id)
    except OrderRepositoryError:
        logger.exception("订单数据库不可用")
        return {"error": "订单查询服务暂时不可用，请稍后重试"}

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
