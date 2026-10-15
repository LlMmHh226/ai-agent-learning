# 课程：step_16c_query_document_retrieval.md；访问范围：真实外部请求（可能收费）。
import math

from dashscope import TextEmbedding
from dotenv import dotenv_values

from app.rag.document_loader import load_markdown_documents


QUERY = "快递两天没动静怎么办？"


def cosine_similarity(
    vector_a: list[float],
    vector_b: list[float],
) -> float:
    """使用两个完整向量计算余弦相似度。"""
    if len(vector_a) != len(vector_b):
        raise ValueError("两个向量的维度必须相同")

    dot_product = sum(
        value_a * value_b
        for value_a, value_b in zip(vector_a, vector_b)
    )
    magnitude_a = math.sqrt(sum(value * value for value in vector_a))
    magnitude_b = math.sqrt(sum(value * value for value in vector_b))

    if magnitude_a == 0 or magnitude_b == 0:
        raise ValueError("不能计算零向量的余弦相似度")

    return dot_product / (magnitude_a * magnitude_b)


def request_embeddings(
    texts: list[str],
    text_type: str,
    api_key: str,
    model_name: str,
) -> list[list[float]]:
    """
    发起一次 Embedding 请求，并按输入顺序返回向量。

    本函数不重试：调用失败或返回数量异常时，交给主流程停止实验。
    """
    try:
        response = TextEmbedding.call(
            model=model_name,
            input=texts,
            api_key=api_key,
            text_type=text_type,
            request_timeout=20,
        )
    except Exception as error:
        raise RuntimeError(
            f"{text_type} 请求异常（{type(error).__name__}），已停止且不重试"
        ) from error

    if response.status_code != 200:
        raise RuntimeError(
            f"{text_type} 请求失败：HTTP {response.status_code}，"
            f"错误码 {response.code}；已停止且不重试，不打印供应商异常正文"
        )

    embedding_items = sorted(
        response.output["embeddings"],
        key=lambda item: item.get("text_index", 0),
    )
    vectors = [item["embedding"] for item in embedding_items]

    if len(vectors) != len(texts):
        raise RuntimeError(
            f"{text_type} 返回数量异常：输入 {len(texts)}，返回 {len(vectors)}"
        )

    return vectors


config = dotenv_values(".env")
api_key = config.get("DASHSCOPE_API_KEY")
model_name = config.get("EMBEDDING_MODEL", "text-embedding-v2")
expected_dimensions = int(config.get("EMBEDDING_DIMENSIONS", "1536"))

if not api_key:
    raise RuntimeError(".env 中缺少 DASHSCOPE_API_KEY")

documents = load_markdown_documents()
document_texts = [document.content for document in documents]

try:
    document_vectors = request_embeddings(
        texts=document_texts,
        text_type="document",
        api_key=api_key,
        model_name=model_name,
    )
    query_vector = request_embeddings(
        texts=[QUERY],
        text_type="query",
        api_key=api_key,
        model_name=model_name,
    )[0]
except RuntimeError as error:
    print(error)
    raise SystemExit(1) from error

for document, vector in zip(documents, document_vectors):
    source = document.metadata["source"]
    print(f"来源：{source}，维度：{len(vector)}")

print(f"来源：用户问题，维度：{len(query_vector)}")

all_vectors = [*document_vectors, query_vector]
if any(len(vector) != expected_dimensions for vector in all_vectors):
    raise RuntimeError(f"存在维度不等于预期值 {expected_dimensions} 的向量")

ranked_results = sorted(
    (
        (
            document.metadata["source"],
            cosine_similarity(query_vector, document_vector),
        )
        for document, document_vector in zip(documents, document_vectors)
    ),
    key=lambda item: item[1],
    reverse=True,
)

for rank, (source, score) in enumerate(ranked_results, start=1):
    print(f"排名：{rank}，来源：{source}，分数：{score:.4f}")
