# 课程：step_08_sources.md；访问范围：本地资料演示，无数据库和模型请求。
"""第8步独立练习：完整实现候选检索结果到来源字典列表的转换。"""

import argparse
from dataclasses import asdict
import json

from app.rag.retriever import RetrievalResult
from learning.pgvector.step_06_build_messages import (
    QUERY,
    load_example_rows,
    rows_to_retrieval_results,
)


# 用户在2026-10-30提供的第7步回答；本步不重新调用模型生成答案。
RECORDED_ANSWER = "不需要。星云机械键盘支持五脚轴热插拔，更换轴体时不需要焊接。"


def build_source_records(
    retrieval_results: list[RetrievalResult],
) -> list[dict[str, str]]:
    """独立实现来源转换：每条输入对应一条含source、chunk_id、snippet的字典。

    要求：保持输入顺序与同文件的不同片段；空输入返回[]；不修改输入对象。
    本练习请自行完成遍历、取值与返回，不调用现有build_sources代替实现。
    """
    sources = []

    for result in retrieval_results:
        record = {
            "source": result.document.metadata["source"],
            # 在这里补上 chunk_id 和 snippet
            "chunk_id": result.document.metadata["chunk_id"],
            "snippet": result.document.content
        }
        sources.append(record)

    return sources




def build_response(
    answer: str,
    retrieval_results: list[RetrievalResult],
) -> dict[str, object]:
    """对照实现的复用版，保留供对照；当前--build使用上面的独立练习。"""

    # 只复用正式的类型与纯数据转换函数，不调用RAGService.chat。
    from app.services.rag_service import RAGResult, build_sources

    # 对照实现：复用正式函数构造来源。
    sources = build_sources(retrieval_results)

    result = RAGResult(answer=answer, sources=sources)
    # 把数据类对象（包括嵌套的来源对象）转换成可打印JSON的普通字典。
    return asdict(result)


def main() -> None:
    parser = argparse.ArgumentParser(description="本地练习：独立实现完整的候选来源转换函数。")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--preview", action="store_true", help="展示输入；默认模式，不执行转换函数。")
    mode.add_argument("--build", action="store_true", help="执行build_source_records，打印answer与sources。")
    args = parser.parse_args()

    rows = load_example_rows()
    retrieval_results = rows_to_retrieval_results(rows)
    print(json.dumps({
        "input_origin": "沿用第6步本地示例，不是本次数据库检索。",
        "answer_origin": "复用用户10月30日提供的第7步回答，不是本次模型生成。",
        "sources_meaning": "交给模型的候选资料，不是模型实际使用片段的审计结论。",
        "query": QUERY,
        "recorded_answer": RECORDED_ANSWER,
        "retrieval_results": [asdict(result) for result in retrieval_results],
    }, ensure_ascii=False, indent=2))

    if not args.build:
        print("预览结束。运行--build，才会执行你的来源转换函数。")
        return

    sources = build_source_records(retrieval_results)
    response = {"answer": RECORDED_ANSWER, "sources": sources}
    print("\n使用来源转换函数组合后的结果：")
    print(json.dumps(response, ensure_ascii=False, indent=2))
    print("本步只组合已有答案与来源；未请求模型、未连接数据库、未切换正式接口。")


if __name__ == "__main__":
    main()
