# 课程：step_07_prompt_context.md；访问范围：本地运行（无外部模型请求）。
from app.rag.chunker import split_documents
from app.rag.document_loader import load_markdown_documents
from app.rag.prompt_builder import build_rag_messages
from app.rag.retriever import retrieve


query = "物流轨迹超过 48 小时没有更新怎么办？"

documents = load_markdown_documents()
chunks = split_documents(
    documents=documents,
    chunk_size=10_000,
    overlap=0,
)
retrieval_results = retrieve(
    query=query,
    chunks=chunks,
    top_k=1,
)
messages = build_rag_messages(
    query=query,
    retrieval_results=retrieval_results,
)

print(f"原始文档数：{len(documents)}")
print(f"文档级 chunk 数：{len(chunks)}")
print(f"检索结果数：{len(retrieval_results)}")

for message in messages:
    print(f"\n===== {message['role']} =====")
    print(message["content"])
