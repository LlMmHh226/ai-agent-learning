# 课程：step_15a_keyword_limit.md；访问范围：本地运行（无外部模型请求）。
from app.rag.chunker import split_documents
from app.rag.document_loader import load_markdown_documents
from app.rag.retriever import build_char_ngrams, retrieve


questions = [
    "物流轨迹超过 48 小时没有更新怎么办？",
    "快递两天没动静怎么办？",
]

chunks = split_documents(
    documents=load_markdown_documents(),
    chunk_size=10_000,
    overlap=0,
)

for question in questions:
    results = retrieve(
        query=question,
        chunks=chunks,
        top_k=1,
        min_score=0.0,
    )
    print(f"\n问题：{question}")
    print(f"二元字符组：{sorted(build_char_ngrams(question))}")
    if results:
        print(f"最高分来源：{results[0].document.metadata['source']}")
        print(f"最高分：{results[0].score:.3f}")
    else:
        print("没有任何共享二元字符组，检索结果为空。")
