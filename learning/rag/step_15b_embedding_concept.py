# 课程：step_15b_embedding_concept.md；访问范围：本地运行（无外部模型请求）。
toy_embeddings: dict[str, list[float]] = {
    "物流轨迹没有更新": [0.90, 0.85, 0.10],
    "快递两天没动静": [0.88, 0.82, 0.12],
    "机械键盘支持热插拔": [0.10, 0.15, 0.92],
}


print("以下是手工构造的教学向量，不是真实 Embedding 模型输出：")

for text, vector in toy_embeddings.items():
    print(f"文本：{text}")
    print(f"向量：{vector}")
    print(f"维度：{len(vector)}\n")
