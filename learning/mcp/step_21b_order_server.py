# 课程：step_21b_local_order.md；访问范围：本地演示，不请求外部模型。
"""21B：独立MCP服务端，只暴露本地样例订单查询，不调用模型。"""

from mcp.server.mcpserver import MCPServer

from app.repositories.demo_orders import get_demo_order_status as get_order_status


server = MCPServer("order-learning-server", log_level="WARNING")


@server.tool()
def query_order(order_id: str) -> dict[str, object]:
    """根据订单编号查询本地样例订单，返回状态、商品和物流单号。

    参数order_id由MCP客户端提交；字符串，例如10001。
    返回业务结果字典给MCP SDK，由SDK包装成协议结果发回客户端。
    """
    return get_order_status(order_id)


if __name__ == "__main__":
    # stdout承载协议消息，不在服务端使用print输出普通说明。
    server.run(transport="stdio")
