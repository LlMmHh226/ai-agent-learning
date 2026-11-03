from app.rag.knowledge_retriever import KnowledgeRetrievalError, retrieve_knowledge


SEARCH_KNOWLEDGE_BASE_TOOL = {
    "type": "function",
    "function": {
        "name": "search_knowledge_base",
        "description": (
            "搜索客服知识库中的商品规格、使用说明和知识文档。"
            "实时订单状态应使用 get_order_status；退货、换货或退款规则"
            "应使用 get_after_sales_policy。"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "minLength": 1,
                    "description": "需要在知识库中检索的完整用户问题",
                }
            },
            "required": ["query"],
            "additionalProperties": False,
        },
    },
}


def search_knowledge_base(query: str) -> dict[str, object]:
    """
    与正式RAG共用检索后端，搜索与问题相关的资料。

    参数:
        query:
            需要检索的完整用户问题。Agent 从用户消息中提取并通过
            Tool Call 参数传入，例如“星云机械键盘支持热插拔吗？”。

    返回:
        包含 found 和 results 的字典。找到资料时，results 中包含
        source、chunk_id、snippet 和 score；否则返回明确的未找到消息。
    """
    normalized_query = query.strip()
    if not normalized_query:
        return {
            "found": False,
            "message": "知识库查询内容不能为空",
        }

    try:
        retrieval_results = retrieve_knowledge(query=normalized_query)
    except KnowledgeRetrievalError:
        return {"error": "知识库检索服务暂时不可用，请稍后重试"}

    if not retrieval_results:
        return {
            "found": False,
            "message": "知识库中没有找到足够相关的资料",
        }

    return {
        "found": True,
        "results": [
            {
                "source": result.document.metadata["source"],
                "chunk_id": result.document.metadata["chunk_id"],
                "snippet": result.document.content,
                "score": round(result.score, 3),
            }
            for result in retrieval_results
        ],
    }
