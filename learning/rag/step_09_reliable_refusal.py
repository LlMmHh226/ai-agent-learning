# 课程：step_09_reliable_refusal.md；访问范围：当前固定无资料示例不请求模型；更改问题或知识库后可能进入真实生成分支。
import asyncio

from app.rag.retriever import retrieve
from app.services.rag_service import rag_service


query = "商品有优惠券吗？"

raw_results = retrieve(
    query=query,
    chunks=rag_service.chunks,
    top_k=1,
    min_score=0.0,
)
raw_score = raw_results[0].score if raw_results else 0.0

result = asyncio.run(rag_service.chat(query=query))

print(f"用户问题：{query}")
print(f"过滤前最高分：{raw_score:.3f}")
print(f"RAGService 最低分：{rag_service.min_score:.3f}")
print(f"最终回答：{result.answer}")
print(f"来源数量：{len(result.sources)}")
