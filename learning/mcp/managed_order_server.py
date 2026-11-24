"""22B/22C 共用的本机 stdio 服务器；只读公开样例，不加载模型配置。"""

from typing import Literal

from mcp.server.mcpserver import MCPServer

from app.rag.document_loader import load_markdown_documents
from app.rag.retriever import retrieve
from app.repositories.demo_orders import get_demo_order_status
from app.tools.policy_tools import get_after_sales_policy as lookup_policy


server = MCPServer("customer-service-learning", log_level="WARNING")


@server.tool()
def get_order_status(order_id: str) -> dict[str, object]:
    """根据编号查询一条虚构订单。"""
    return get_demo_order_status(order_id)


@server.tool()
def get_after_sales_policy(topic: Literal["退货", "换货", "退款"]) -> dict[str, object]:
    """查询教学售后政策。"""
    return lookup_policy(topic)


@server.tool()
def search_knowledge_base(query: str) -> dict[str, object]:
    """按 n-gram 匹配本地教学资料，只报告最相关的文件与分数。"""
    matches = retrieve(query, load_markdown_documents(), top_k=1, min_score=0.3)
    if not matches:
        return {"found": False}
    match = matches[0]
    return {"found": True, "source": match.document.metadata["source"], "score": round(match.score, 3)}


if __name__ == "__main__":
    server.run(transport="stdio")
