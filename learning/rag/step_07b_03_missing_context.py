# 课程：step_07b_03_missing_context.md；访问范围：本地运行（无外部模型请求）。
from app.rag.chunker import split_documents
from app.rag.document_loader import load_markdown_documents
from app.rag.prompt_builder import build_rag_messages
from app.rag.retriever import retrieve


query = "你们公司的董事长是谁？"

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

print(f"用户问题：{query}")
print(f"检索结果数：{len(retrieval_results)}")

for message in messages:
    print(f"\n===== {message['role']} =====")
    print(message["content"])
