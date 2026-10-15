# 课程：step_17g_rag_code_recap.md；访问范围：本地运行（无外部模型请求）。
from app.rag.prompt_builder import RAG_INSUFFICIENT_CONTEXT_RESPONSE
from app.rag.retriever import retrieve
from app.services.rag_service import rag_service


QUESTIONS = [
    "物流轨迹超过 48 小时没有更新怎么办？",
    "快递两天没动静怎么办？",
    "退货运费谁承担？",
]


def main() -> None:
    for question in QUESTIONS:
        retrieval_results = retrieve(
            query=question,
            chunks=rag_service.chunks,
            top_k=rag_service.top_k,
            min_score=rag_service.min_score,
        )
        sources = [
            result.document.metadata["source"]
            for result in retrieval_results
        ]

        print(f"问题：{question}")
        print(f"检索来源：{sources}")
        if not retrieval_results:
            print(f"Python 分支：直接拒答“{RAG_INSUFFICIENT_CONTEXT_RESPONSE}”")
            print("后续：不会构建 Prompt，也不会调用聊天模型\n")
        else:
            print("Python 分支：结果非空，会继续构建 Prompt 和调用聊天模型")
            print("注意：本学习脚本只展示分支，不执行后续模型调用\n")


if __name__ == "__main__":
    main()
