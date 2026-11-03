# 课程：step_05_query_topk.md；访问范围：当前命令只读或预览；写入/生成选项见下文。
"""用户问题向量检索：学习者补写问题Embedding调用和余弦Top-K查询。"""

import argparse
import json

from app.services.embedding_service import EmbeddingService
from learning.pgvector.step_03_insert_one_chunk import VECTOR_DIMENSIONS
from learning.postgresql.step_03_python_order_lookup import connect_learning_db


EXPECTED_MODEL = "text-embedding-v4"
DEFAULT_QUERY = "星云机械键盘换轴需要焊接吗？"


def search_top_k(connection, query: str, top_k: int) -> list[dict[str, object]]:
    """生成一个问题向量，只读查询最接近的知识片段。"""
    embedding_service = EmbeddingService()
    if (
        embedding_service.model != EXPECTED_MODEL
        or embedding_service.dimensions != VECTOR_DIMENSIONS
    ):
        raise ValueError("问题与已入库文档必须沿用V4和1536维。")

    # 关键步骤 1：调用embed_query，参数为query；它直接返回一个完整向量。
    query_vector = embedding_service.embed_query(query)

    if len(query_vector) != VECTOR_DIMENSIONS or not any(query_vector):
        raise ValueError("问题向量必须是一个1536维非零向量，请检查向量生成步骤。")
    query_vector_text = json.dumps(query_vector, allow_nan=False)

    # 关键步骤 2：编写SELECT，返回chunk_id、source、content和计算出的distance。
    # 使用embedding与第一个%s计算余弦距离；升序排序，LIMIT使用第二个%s。
    sql = """
          SELECT chunk_id, 
                 source, 
                 content,
                 embedding <=> %s::vector(1536) AS distance
          FROM public.knowledge_chunks
          ORDER BY distance ASC
              LIMIT %s 
          """

    with connection.cursor() as cursor:
        cursor.execute(sql, (query_vector_text, top_k))
        return cursor.fetchall()


def main() -> None:
    parser = argparse.ArgumentParser(description="预览问题与数据库状态，或执行只读向量检索。")
    parser.add_argument("--query", default=DEFAULT_QUERY, help="要检索的用户问题。")
    parser.add_argument("--top-k", type=int, default=3, help="最多返回的片段数，默认3。")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--preview", action="store_true", help="只读展示计划；默认模式。")
    mode.add_argument("--search", action="store_true", help="确认配置后真实生成问题向量并检索。")
    args = parser.parse_args()
    if not args.query.strip() or args.top_k <= 0:
        raise ValueError("问题不能为空，top-k必须大于0。")

    with connect_learning_db() as connection:
        # 预览和真实检索都只读，不向知识表插入用户问题。
        connection.read_only = True
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT count(*) AS knowledge_rows, "
                "min(vector_dims(embedding)) AS dimensions, "
                "bool_and(vector_norm(embedding) > 0) AS all_nonzero "
                "FROM public.knowledge_chunks"
            )
            state = cursor.fetchone()
        print(json.dumps({
            "query": args.query,
            "top_k": args.top_k,
            "expected_model": EXPECTED_MODEL,
            "expected_dimensions": VECTOR_DIMENSIONS,
            "database_state": state,
        }, ensure_ascii=False, indent=2))

        if not args.search:
            print("只读预览结束：未生成问题向量，未执行语义匹配。")
            return
        if state["knowledge_rows"] == 0:
            raise ValueError("知识表为空，请先完成片段入库。")
        if state["dimensions"] != VECTOR_DIMENSIONS or not state["all_nonzero"]:
            raise ValueError("已保存向量的维度或非零状态不符合当前练习。")
        results = search_top_k(connection, args.query, args.top_k)

    distances = [row["distance"] for row in results]
    if len(results) > args.top_k or distances != sorted(distances):
        raise RuntimeError("请检查查询语句：限制Top-K数量，并按距离从小到大排序。")
    print(json.dumps({
        "query": args.query,
        "retrieved_count": len(results),
        "results": results,
    }, ensure_ascii=False, indent=2))
    print("以上是候选片段；请核对正文是否能支持回答。本步不调用聊天模型。")


if __name__ == "__main__":
    main()
