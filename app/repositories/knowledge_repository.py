"""只读查询知识向量表；不在用户提问时重建知识库。"""

import json
import math

import psycopg
from psycopg.rows import dict_row

from app.core.config import get_settings


VECTOR_DIMENSIONS = 1536
SEARCH_SQL = """
SELECT chunk_id, source, content,
       embedding <=> %s::vector(1536) AS distance
FROM public.knowledge_chunks
WHERE vector_norm(embedding) > 0
ORDER BY distance ASC, chunk_id ASC
LIMIT %s
"""


class KnowledgeRepositoryError(RuntimeError):
    """知识库不可用，与查询成功但没有资料区分。"""


def search_knowledge_chunks(
    query_vector: list[float], top_k: int,
) -> list[dict[str, object]]:
    if not 1 <= top_k <= 20:
        raise ValueError("top_k 必须在1到20之间")
    if len(query_vector) != VECTOR_DIMENSIONS or any(
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(value)
        for value in query_vector
    ) or not any(query_vector):
        raise ValueError("问题向量必须是有效的1536维非零数值向量")

    settings = get_settings()
    password = settings.postgres_password
    if password is None or not password.get_secret_value():
        raise KnowledgeRepositoryError("项目根目录.env中未配置POSTGRES_PASSWORD。")

    try:
        with psycopg.connect(
            host=settings.postgres_host,
            port=settings.postgres_port,
            dbname=settings.postgres_db,
            user=settings.postgres_user,
            password=password.get_secret_value(),
            row_factory=dict_row,
            connect_timeout=5,
        ) as connection:
            connection.read_only = True
            with connection.cursor() as cursor:
                cursor.execute("SET LOCAL statement_timeout = '5s'")
                cursor.execute(
                    SEARCH_SQL,
                    (json.dumps(query_vector, allow_nan=False), top_k),
                )
                return cursor.fetchall()
    except psycopg.Error as error:
        raise KnowledgeRepositoryError("知识库数据库查询失败。") from error
