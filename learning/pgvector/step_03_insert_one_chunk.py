# 课程：step_03_insert_one_chunk.md；访问范围：当前命令只读或预览；写入/生成选项见下文。
"""只将一个真实知识片段向量入库；生成向量和参数绑定学习演示。"""

import argparse
import json

from app.rag.chunker import split_documents
from app.rag.document_loader import Document, load_markdown_documents
from app.services.embedding_service import EmbeddingService
from learning.postgresql.step_03_python_order_lookup import connect_learning_db


VECTOR_DIMENSIONS = 1536

INSERT_SQL = """
INSERT INTO public.knowledge_chunks (chunk_id, source, content, embedding)
VALUES (%s, %s, %s, %s::vector(1536))
ON CONFLICT (chunk_id) DO UPDATE SET
    source = EXCLUDED.source,
    content = EXCLUDED.content,
    embedding = EXCLUDED.embedding
"""


def save_one_chunk(chunk: Document) -> dict[str, object]:
    """生成当前片段的真实向量，写入并回读一行；成功退出连接时提交。"""

    embedding_service = EmbeddingService()
    if embedding_service.model != 'text-embedding-v4' or embedding_service.dimensions != VECTOR_DIMENSIONS:
        raise ValueError("本练习要求V4/1536，避免把历史V2实验向量混入知识表。")

    with connect_learning_db() as connection:
        with connection.cursor() as cursor:
            # 先确认目标表可读，再请求真实Embedding；这里不读取或输出已有向量。
            cursor.execute(
                "SELECT chunk_id, source, content, vector_dims(embedding) "
                "FROM public.knowledge_chunks LIMIT 0"
            )

            # 关键步骤 1：将[]替换为生成当前片段document向量的调用。
            # embed_documents接收正文列表，返回向量列表；本次只取第0个向量。
            texts = [chunk.content]
            vectors = embedding_service.embed_documents(texts)
            vector = vectors[0]

            if len(vector) != VECTOR_DIMENSIONS:
                raise ValueError("vector应是当前片段对应的一个1536维向量，请检查向量生成步骤。")

            # 将Python浮点数列表转为字符串；SQL中的::vector(1536)负责转成向量类型。
            vector_text = json.dumps(vector, allow_nan=False)

            # 关键步骤 2：将()替换为四个入库值组成的元组，顺序对应INSERT_SQL的四列。
            # 编号和来源在chunk.metadata中，正文在chunk.content中，最后一项用vector_text。
            params = (
                chunk.metadata["chunk_id"],
                chunk.metadata["source"],
                chunk.content,
                vector_text,
            )
            cursor.execute(INSERT_SQL, params)

            cursor.execute(
                "SELECT chunk_id, source, content, vector_dims(embedding) AS dimensions "
                "FROM public.knowledge_chunks WHERE chunk_id = %s",
                (chunk.metadata["chunk_id"],),
            )
            saved = cursor.fetchone()
            if (
                saved is None
                or saved["source"] != chunk.metadata["source"]
                or saved["content"] != chunk.content
                or saved["dimensions"] != VECTOR_DIMENSIONS
            ):
                raise RuntimeError("入库后的编号、正文、来源或维度未通过回读检查。")

            return saved


def main() -> None:
    parser = argparse.ArgumentParser(description="预览或写入一个真实知识片段向量。")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--preview", action="store_true", help="只预览片段；默认模式。")
    mode.add_argument("--write", action="store_true", help="确认配置后调用真实Embedding并写入。")
    args = parser.parse_args()

    documents = load_markdown_documents()
    chunks = split_documents(documents)
    if not chunks:
        raise ValueError("知识文档中没有可入库的片段。")
    chunk = chunks[0]

    print(json.dumps({
        "document_count": len(documents),
        "total_chunk_count": len(chunks),
        "selected_chunk_id": chunk.metadata["chunk_id"],
        "source": chunk.metadata["source"],
        "content": chunk.content,
        "expected_dimensions": VECTOR_DIMENSIONS,
    }, ensure_ascii=False, indent=2))

    if not args.write:
        print("仅预览：未连接数据库，未调用Embedding，未写入。实际生成与入库请使用--write。")
        return

    saved = save_one_chunk(chunk)
    print("已提交并回读当前片段；不打印完整向量：")
    print(json.dumps(saved, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
