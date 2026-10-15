# 课程：step_15d_recall_at_k.md；访问范围：本地运行（无外部模型请求）。
from app.rag.chunker import split_documents
from app.rag.document_loader import Document, load_markdown_documents
from app.rag.retriever import retrieve


evaluation_cases: list[tuple[str, str]] = [
    ("键盘支持蓝牙吗？", "products.md"),
    ("鼠标续航多久？", "products.md"),
    ("物流超过48小时没更新怎么办？", "shipping.md"),
    ("质量问题换货运费谁承担？", "after_sales.md"),
    ("退款多久？", "after_sales.md"),
    ("购买商品什么时候寄出？", "shipping.md"),
    ("快递两天没动静怎么办？", "shipping.md"),
]


def calculate_recall_at_k(
    cases: list[tuple[str, str]],
    chunks: list[Document],
    k: int,
) -> float:
    """
    计算正确来源进入前 K 个检索结果的问题比例。

    参数:
        cases:
            评测用例列表。每项包含用户问题和预期来源文件名。

        chunks:
            候选知识片段列表，来自 split_documents() 的返回值。

        k:
            每个问题最多检查前几个检索结果。

    返回:
        Recall@K 浮点数，即命中问题数除以全部评测问题数。
    """
    if not cases:
        raise ValueError("评测用例不能为空")
    if k <= 0:
        raise ValueError("k 必须大于 0")

    hit_count = 0

    for question, expected_source in cases:
        results = retrieve(
            query=question,
            chunks=chunks,
            top_k=k,
            min_score=0.0,
        )
        returned_sources = [
            result.document.metadata["source"]
            for result in results
        ]
        hit = expected_source in returned_sources
        if hit:
            hit_count += 1

        print(
            f"K={k} 命中={hit!s:5} "
            f"预期={expected_source:14} "
            f"返回={returned_sources} "
            f"问题={question}"
        )

    return hit_count / len(cases)


knowledge_chunks = split_documents(
    documents=load_markdown_documents(),
    chunk_size=10_000,
    overlap=0,
)

recall_at_1 = calculate_recall_at_k(
    cases=evaluation_cases,
    chunks=knowledge_chunks,
    k=1,
)
print(f"\nRecall@1 = {recall_at_1:.1%}\n")

recall_at_3 = calculate_recall_at_k(
    cases=evaluation_cases,
    chunks=knowledge_chunks,
    k=3,
)
print(f"\nRecall@3 = {recall_at_3:.1%}")
