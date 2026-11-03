# 课程：step_06_build_messages.md；访问范围：本地资料演示，无数据库和模型请求。
"""把pgvector结果行交给已有的RAG消息构造函数；学习者填写正文与元数据。"""

import argparse
import json

from app.rag.chunker import split_documents
from app.rag.document_loader import Document, load_markdown_documents
from app.rag.prompt_builder import build_rag_messages
from app.rag.retriever import RetrievalResult


QUERY = "星云机械键盘换轴需要焊接吗？"

# 固定教学排序与距离，不是本次重新检索的结果。
RECORDED_RANKING = [
    ("products.md#chunk-0", 0.35175721070255905),
    ("products.md#chunk-1", 0.6032595994031127),
    ("after_sales.md#chunk-0", 0.7200650155641151),
]


def rows_to_retrieval_results(
    rows: list[dict[str, object]],
) -> list[RetrievalResult]:
    """保留每行的正文、来源和编号，转换成build_rag_messages接收的类型。"""
    results: list[RetrievalResult] = []
    for row in rows:
        # 关键步骤 1：content接收这一行的正文。
        # 关键步骤 2：metadata保存source和chunk_id两个键，值分别取自这一行。
        document = Document(
            content=row["content"],
            metadata={
                "source": row["source"],
                "chunk_id": row["chunk_id"],
            },
        )
        results.append(
            RetrievalResult(
                document=document,
                # 余弦相似度=1-余弦距离；本步Prompt不读取score，也不套用n-gram阈值。
                score=1.0 - float(row["distance"]),
            )
        )
    return results


def load_example_rows() -> list[dict[str, object]]:
    """从当前本地原文取得正文，构造与第5步fetchall同形状的演示输入。"""
    chunks = split_documents(load_markdown_documents())
    chunks_by_id = {chunk.metadata["chunk_id"]: chunk for chunk in chunks}
    rows = []
    for chunk_id, distance in RECORDED_RANKING:
        chunk = chunks_by_id[chunk_id]
        rows.append({
            "chunk_id": chunk_id,
            "source": chunk.metadata["source"],
            "content": chunk.content,
            "distance": distance,
        })
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="本地练习：将检索结果行转换为RAG模型消息。")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--preview", action="store_true", help="展示本地示例行；默认模式。")
    mode.add_argument("--build", action="store_true", help="确认配置后构造并打印模型消息。")
    args = parser.parse_args()

    rows = load_example_rows()
    print(json.dumps({
        "input_origin": "本地Markdown正文配合固定教学排序和距离；不是本次数据库查询。",
        "query": QUERY,
        "rows": rows,
    }, ensure_ascii=False, indent=2))

    if not args.build:
        print("预览完成。转换代码已补齐，可用--build查看模型消息。")
        return

    retrieval_results = rows_to_retrieval_results(rows)
    messages = build_rag_messages(
        query=QUERY,
        retrieval_results=retrieval_results,
    )
    print("\n构造出的模型消息：")
    print(json.dumps(messages, ensure_ascii=False, indent=2))
    print("本步只构造消息；未连接数据库、未请求Embedding或聊天模型。")


if __name__ == "__main__":
    main()
