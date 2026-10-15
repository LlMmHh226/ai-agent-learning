# 课程：step_15d_precision_at_k.md；访问范围：本地运行（无外部模型请求）。
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


def calculate_precision_at_k(
    cases: list[tuple[str, str]],
    chunks: list[Document],
    k: int,
) -> float:
    """
    计算所有已返回资料中正确资料所占的比例。

    参数:
        cases:
            评测用例列表。每项包含用户问题和预期来源文件名。

        chunks:
            候选知识片段列表，来自 split_documents() 的返回值。

        k:
            每个问题最多返回几个检索结果。

    返回:
        当前评测集的微平均 Precision 浮点数。分子是返回的正确资料
        数量，分母是检索器实际返回的全部资料数量。
    """
    if not cases:
        raise ValueError("评测用例不能为空")
    if k <= 0:
        raise ValueError("k 必须大于 0")

    relevant_result_count = 0
    returned_result_count = 0

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
        relevant_sources = [
            source
            for source in returned_sources
            if source == expected_source
        ]

        returned_result_count += len(returned_sources)
        relevant_result_count += len(relevant_sources)

        print(
            f"K={k} 正确={len(relevant_sources)} "
            f"返回={len(returned_sources)} "
            f"预期={expected_source:14} "
            f"结果={returned_sources} "
            f"问题={question}"
        )

    if returned_result_count == 0:
        return 0.0

    return relevant_result_count / returned_result_count


knowledge_chunks = split_documents(
    documents=load_markdown_documents(),
    chunk_size=10_000,
    overlap=0,
)

precision_at_1 = calculate_precision_at_k(
    cases=evaluation_cases,
    chunks=knowledge_chunks,
    k=1,
)
print(f"\nPrecision@1 = {precision_at_1:.1%}\n")

precision_at_3 = calculate_precision_at_k(
    cases=evaluation_cases,
    chunks=knowledge_chunks,
    k=3,
)
print(f"\nPrecision@3 = {precision_at_3:.1%}")
