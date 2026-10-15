# 课程：step_06_scores_and_top_k.md；访问范围：本地运行（无外部模型请求）。
from app.rag.chunker import split_documents
from app.rag.document_loader import load_markdown_documents
from app.rag.retriever import (
    RetrievalResult,
    build_char_ngrams,
    calculate_ngram_similarity,
    retrieve,
)


query = "物流轨迹超过 48 小时没有更新怎么办？"
top_k = 2

documents = load_markdown_documents()
chunks = split_documents(documents)
query_ngrams = build_char_ngrams(query)
all_results: list[RetrievalResult] = []

for chunk in chunks:
    score = calculate_ngram_similarity(
        query=query,
        chunk_text=chunk.content,
    )
    all_results.append(
        RetrievalResult(
            document=chunk,
            score=score,
        )
    )

all_results.sort(
    key=lambda result: result.score,
    reverse=True,
)

print(f"用户问题：{query}")
print(f"问题字符组总数：{len(query_ngrams)}")
print("\n全部 chunk 得分（从高到低）：")

for rank, result in enumerate(all_results, start=1):
    chunk_ngrams = build_char_ngrams(result.document.content)
    matched_ngrams = sorted(query_ngrams & chunk_ngrams)
    print(
        f"{rank}. {result.document.metadata['chunk_id']} "
        f"score={result.score:.3f} "
        f"命中={matched_ngrams}"
    )

top_results = retrieve(
    query=query,
    chunks=chunks,
    top_k=top_k,
)

print(f"\nTop-K 选择：K={top_k}")
for result in top_results:
    print(
        f"- {result.document.metadata['chunk_id']} "
        f"score={result.score:.3f}"
    )

print("\n最终检索结果正文：")
for result in top_results:
    print(f"\n[{result.document.metadata['chunk_id']}]")
    print(result.document.content.replace("\n", " "))
