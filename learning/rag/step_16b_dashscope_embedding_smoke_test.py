# 课程：step_16b_dashscope_embedding_smoke_test.md；访问范围：真实外部请求（可能收费）。
import math

from dashscope import TextEmbedding
from dotenv import dotenv_values


def cosine_similarity(
    vector_a: list[float],
    vector_b: list[float],
) -> float:
    """
    计算两个等长向量的余弦相似度。

    参数:
        vector_a:
            第一段文本的 Embedding 向量。

        vector_b:
            第二段文本的 Embedding 向量。

    返回:
        两个向量的余弦相似度浮点数。
    """
    dot_product = sum(
        value_a * value_b
        for value_a, value_b in zip(vector_a, vector_b)
    )
    magnitude_a = math.sqrt(sum(value * value for value in vector_a))
    magnitude_b = math.sqrt(sum(value * value for value in vector_b))
    return dot_product / (magnitude_a * magnitude_b)


config = dotenv_values(".env")
api_key = config.get("DASHSCOPE_API_KEY")
model_name = config.get("EMBEDDING_MODEL", "text-embedding-v2")
expected_dimensions = int(config.get("EMBEDDING_DIMENSIONS", "1536"))

if not api_key:
    raise RuntimeError(".env 中缺少 DASHSCOPE_API_KEY")

texts = [
    "物流轨迹没有更新",
    "快递两天没动静",
]

response = TextEmbedding.call(
    model=model_name,
    input=texts,
    api_key=api_key,
    text_type="document",
    request_timeout=20,
)

if response.status_code != 200:
    print(f"Embedding 调用失败，HTTP状态：{response.status_code}")
    print(f"错误码：{response.code}")
    print("已停止；不打印供应商异常正文，请根据状态码核对配置与额度。")
else:
    embedding_items = response.output["embeddings"]
    vectors = [
        item["embedding"]
        for item in embedding_items
    ]

    print(f"模型：{model_name}")
    print(f"输入数量：{len(texts)}")
    print(f"返回向量数量：{len(vectors)}")

    for index, vector in enumerate(vectors):
        print(
            f"文本{index + 1}维度：{len(vector)} "
            f"符合预期={len(vector) == expected_dimensions}"
        )
        print(f"前5个数值：{vector[:5]}")

    score = cosine_similarity(vectors[0], vectors[1])
    print(f"两句话的余弦相似度：{score:.4f}")
