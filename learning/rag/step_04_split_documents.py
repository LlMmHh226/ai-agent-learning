# 课程：step_04_chunker.md；访问范围：本地运行（无外部模型请求）。
from app.rag.chunker import split_documents
from app.rag.document_loader import load_markdown_documents


documents = load_markdown_documents()
chunks = split_documents(
    documents=documents,
    chunk_size=120,
    overlap=20,
)

print(f"原始文档数：{len(documents)}")
print(f"切分后的 chunk 数：{len(chunks)}")

for chunk in chunks:
    print(
        f"{chunk.metadata['chunk_id']} "
        f"长度={len(chunk.content)} "
        f"来源={chunk.metadata['source']}"
    )
    print(chunk.content.replace("\n", " "))
