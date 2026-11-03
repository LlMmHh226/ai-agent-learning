# 课程：step_04_batch_insert.md；访问范围：当前命令只读或预览；写入/生成选项见下文。
"""批量生成并保存待处理片段向量；学习者补写整批向量生成和逐项配对。"""

import argparse
import json

from app.rag.chunker import split_documents
from app.rag.document_loader import Document, load_markdown_documents
from app.services.embedding_service import EmbeddingService
from learning.pgvector.step_03_insert_one_chunk import INSERT_SQL, VECTOR_DIMENSIONS
from learning.postgresql.step_03_python_order_lookup import connect_learning_db


EXPECTED_MODEL = "text-embedding-v4"
MAX_BATCH_SIZE = 10


def select_pending_chunks(connection, chunks: list[Document]) -> list[Document]:
    """只读比较现有V4片段；正文、来源和向量状态一致时跳过。"""
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT chunk_id, source, content, vector_dims(embedding) AS dimensions, "
            "vector_norm(embedding) > 0 AS nonzero_embedding "
            "FROM public.knowledge_chunks"
        )
        saved_by_id = {row["chunk_id"]: row for row in cursor.fetchall()}

    pending_chunks = []
    for chunk in chunks:
        saved = saved_by_id.get(chunk.metadata["chunk_id"])
        unchanged = (
            saved is not None
            and saved["source"] == chunk.metadata["source"]
            and saved["content"] == chunk.content
            and saved["dimensions"] == VECTOR_DIMENSIONS
            and saved["nonzero_embedding"]
        )
        if not unchanged:
            pending_chunks.append(chunk)
    return pending_chunks


def save_pending_chunks(connection, pending_chunks: list[Document]) -> int:
    """一次生成整批向量，按对应关系逐行写入；返回本批写入数。"""
    embedding_service = EmbeddingService()
    if (
        embedding_service.model != EXPECTED_MODEL
        or embedding_service.dimensions != VECTOR_DIMENSIONS
    ):
        raise ValueError("本步沿用V4与1536维，已有片段也是这个模型生成的。")

    texts = [chunk.content for chunk in pending_chunks]

    # 关键步骤 1：生成texts中所有正文对应的向量列表；本次保留整个返回值。
    vectors = embedding_service.embed_documents(texts)

    if len(vectors) != len(pending_chunks):
        raise ValueError("每个待处理片段应对应一个向量，请检查向量生成步骤。")
    if any(len(vector) != VECTOR_DIMENSIONS for vector in vectors):
        raise ValueError("每个片段的向量都应为1536维。")

    # 关键步骤 2：用zip将pending_chunks和vectors按位置配对，替换空列表。
    pairs = zip(pending_chunks, vectors)

    written_count = 0
    with connection.cursor() as cursor:
        for chunk, vector in pairs:
            vector_text = json.dumps(vector, allow_nan=False)
            params = (
                chunk.metadata["chunk_id"],
                chunk.metadata["source"],
                chunk.content,
                vector_text,
            )
            cursor.execute(INSERT_SQL, params)
            written_count += 1
    return written_count


def main() -> None:
    parser = argparse.ArgumentParser(description="只读预览或批量写入剩余知识片段。")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--preview", action="store_true", help="只读比较数据库；默认模式。")
    mode.add_argument("--write", action="store_true", help="确认配置后真实生成并写入整批向量。")
    args = parser.parse_args()

    documents = load_markdown_documents()
    chunks = split_documents(documents)
    if not chunks:
        raise ValueError("没有可入库的知识片段。")

    with connect_learning_db() as connection:
        connection.read_only = not args.write
        pending_chunks = select_pending_chunks(connection, chunks)
        print(json.dumps({
            "document_count": len(documents),
            "total_chunk_count": len(chunks),
            "skip_unchanged_count": len(chunks) - len(pending_chunks),
            "pending_count": len(pending_chunks),
            "expected_model": EXPECTED_MODEL,
            "expected_dimensions": VECTOR_DIMENSIONS,
            "pending_chunks": [
                {"chunk_id": chunk.metadata["chunk_id"],
                 "source": chunk.metadata["source"],
                 "content": chunk.content}
                for chunk in pending_chunks
            ],
        }, ensure_ascii=False, indent=2))

        if not args.write:
            print("只读预览完成：未调用Embedding，未写入。")
            return
        if not pending_chunks:
            print("当前片段均已保存且内容未变，无需生成新向量。")
            return
        if len(pending_chunks) > MAX_BATCH_SIZE:
            raise ValueError("本练习只处理一批、最多10个片段；本次尚未请求Embedding。")

        written_count = save_pending_chunks(connection, pending_chunks)
        if select_pending_chunks(connection, chunks):
            raise RuntimeError("部分片段未正确保存，本次数据库修改将回滚。")

    # 上面的连接上下文成功退出后已提交；另开只读连接验证持久化结果。
    with connect_learning_db() as verification:
        verification.read_only = True
        if select_pending_chunks(verification, chunks):
            raise RuntimeError("独立连接未验证全部当前片段，请检查数据库状态。")
        with verification.cursor() as cursor:
            cursor.execute("SELECT count(*) AS count FROM public.knowledge_chunks")
            table_rows = cursor.fetchone()["count"]
    print(json.dumps({
        "written_count": written_count,
        "verified_current_chunks": len(chunks),
        "knowledge_table_rows": table_rows,
        "dimensions": VECTOR_DIMENSIONS,
        "independent_connection_verified": True,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
