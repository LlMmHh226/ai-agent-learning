# 课程：step_07b_05_answer_and_sources.md；访问范围：本地运行（无外部模型请求）。
import json

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

# 当前尚未调用模型，先用预期正文展示未来响应结构。
model_answer = "物流轨迹超过 48 小时没有更新时，可以联系人工客服核查。"
sources: list[dict[str, str]] = []

for result in retrieval_results:
    sources.append(
        {
            "source": result.document.metadata["source"],
            "chunk_id": result.document.metadata["chunk_id"],
            "snippet": result.document.content,
        }
    )

response_preview = {
    "answer": model_answer,
    "sources": sources,
}

print("模型将收到的 System 输出要求：")
print(messages[0]["content"])
print("\n未来 API 响应结构预览：")
print(json.dumps(response_preview, ensure_ascii=False, indent=2))
