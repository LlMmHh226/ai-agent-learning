# 课程：step_15e_rerank.md；访问范围：本地运行（无外部模型请求）。
from app.rag.chunker import split_documents
from app.rag.document_loader import load_markdown_documents
from app.rag.retriever import RetrievalResult, retrieve


def toy_rerank_score(
    query: str,
    result: RetrievalResult,
) -> float:
    """
    使用一条教学规则为候选资料重新评分。

    参数:
        query:
            用户问题。本例检查其中是否出现“寄出”。

        result:
            第一阶段 retrieve() 返回的一个候选结果。

    返回:
        教学重排分数。命中“寄出”和“发出/发货”的语义映射时加 1，
        再加上第一阶段原始分数用于同分排序。
    """
    semantic_bonus = 0.0
    document_text = result.document.content

    if "寄出" in query and (
        "发出" in document_text
        or "发货" in document_text
    ):
        semantic_bonus = 1.0

    return semantic_bonus + result.score


query = "购买商品什么时候寄出？"

chunks = split_documents(
    documents=load_markdown_documents(),
    chunk_size=10_000,
    overlap=0,
)

first_stage_results = retrieve(
    query=query,
    chunks=chunks,
    top_k=3,
    min_score=0.0,
)

print("第一阶段召回结果：")
for result in first_stage_results:
    print(
        f"{result.document.metadata['source']:14} "
        f"score={result.score:.3f}"
    )

reranked_results = sorted(
    first_stage_results,
    key=lambda result: toy_rerank_score(query, result),
    reverse=True,
)

print("\n第二阶段重排结果：")
for result in reranked_results:
    print(
        f"{result.document.metadata['source']:14} "
        f"rerank_score={toy_rerank_score(query, result):.3f}"
    )

final_results = reranked_results[:1]
print("\n最终 Top-1：")
print(final_results[0].document.metadata["source"])
