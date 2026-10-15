# 课程：step_03_document_loader.md；访问范围：本地运行（无外部模型请求）。
from app.rag.document_loader import load_markdown_documents


documents = load_markdown_documents()

print(f"共加载 {len(documents)} 个文档")

for document in documents:
    source = document.metadata["source"]
    preview = document.content[:60].replace("\n", " ")
    print(f"来源：{source}")
    print(f"内容预览：{preview}")
