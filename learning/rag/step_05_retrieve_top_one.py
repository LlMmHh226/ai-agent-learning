# 课程：step_05_ngram_retriever.md；访问范围：本地运行（无外部模型请求）。
from app.rag.chunker import split_documents
from app.rag.document_loader import load_markdown_documents
from app.rag.retriever import build_char_ngrams, retrieve


query = "星云机械键盘支持热插拔吗？"
documents = load_markdown_documents()
chunks = split_documents(documents)
results = retrieve(
    query=query,
    chunks=chunks,
    top_k=1,
)

print(f"用户问题：{query}")
print(f"问题的二元字符组：{sorted(build_char_ngrams(query))}")

if results:
    top_result = results[0]
    print(f"第一名：{top_result.document.metadata['chunk_id']}")
    print(f"得分：{top_result.score:.3f}")
    print(top_result.document.content.replace("\n", " "))
else:
    print("没有找到包含相同字符组的 chunk")
