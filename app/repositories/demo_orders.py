"""入门课程的虚构订单；与数据库示例种子一致，不代表电商平台数据。"""
DEMO_ORDERS = {
    "10001": {"order_id": "10001", "status": "已发货", "product": "机械键盘", "tracking_number": "SF1234567890"},
    "10002": {"order_id": "10002", "status": "待发货", "product": "无线鼠标", "tracking_number": ""},
    "10003": {"order_id": "10003", "status": "已完成", "product": "显示器", "tracking_number": "YT9876543210"},
}


def get_demo_order_status(order_id: str) -> dict[str, object]:
    """独立协议演示的纯业务函数，不读取聊天密钥或数据库配置。"""
    order = DEMO_ORDERS.get(order_id)
    if order is None:
        return {'found': False, 'message': '没有找到该订单'}
    return {'found': True, **order}
