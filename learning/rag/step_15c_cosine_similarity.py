# 课程：step_15c_cosine_similarity.md；访问范围：本地运行（无外部模型请求）。
import math


def cosine_similarity(
    vector_a: list[float],
    vector_b: list[float],
) -> float:
    """
    计算两个等长向量的余弦相似度。

    参数:
        vector_a:
            第一个文本的向量，例如用户问题向量。

        vector_b:
            第二个文本的向量，例如一个知识库 chunk 向量。

    返回:
        两个向量的余弦相似度浮点数。越接近 1，方向越相近。
    """
    if len(vector_a) != len(vector_b):
        raise ValueError("两个向量的维度必须相同")
    if not vector_a:
        raise ValueError("向量不能为空")

    dot_product = sum(
        value_a * value_b
        for value_a, value_b in zip(vector_a, vector_b)
    )
    magnitude_a = math.sqrt(sum(value * value for value in vector_a))
    magnitude_b = math.sqrt(sum(value * value for value in vector_b))

    if magnitude_a == 0 or magnitude_b == 0:
        raise ValueError("零向量不能计算余弦相似度")

    return dot_product / (magnitude_a * magnitude_b)


query_vector = [0.90, 0.85, 0.10]
similar_logistics_vector = [0.88, 0.82, 0.12]
keyboard_vector = [0.10, 0.15, 0.92]

logistics_score = cosine_similarity(
    vector_a=query_vector,
    vector_b=similar_logistics_vector,
)
keyboard_score = cosine_similarity(
    vector_a=query_vector,
    vector_b=keyboard_vector,
)

print(f"物流同义表达相似度：{logistics_score:.4f}")
print(f"键盘文本相似度：{keyboard_score:.4f}")
