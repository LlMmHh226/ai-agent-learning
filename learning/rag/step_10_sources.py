# 课程：step_10_sources.md；访问范围：本地运行（无外部模型请求）。
import json
from dataclasses import asdict

from app.rag.retriever import retrieve
from app.services.rag_service import RAGResult, build_sources, rag_service


query = "物流轨迹超过 48 小时没有更新怎么办？"

retrieval_results = retrieve(
    query=query,
    chunks=rag_service.chunks,
    top_k=rag_service.top_k,
    min_score=rag_service.min_score,
)
sources = build_sources(retrieval_results=retrieval_results)

# 本脚本不调用模型，用预期正文专注观察正式返回类型和 sources。
result = RAGResult(
    answer="物流轨迹超过 48 小时没有更新时，可以联系人工客服核查。",
    sources=sources,
)

print(json.dumps(asdict(result), ensure_ascii=False, indent=2))
