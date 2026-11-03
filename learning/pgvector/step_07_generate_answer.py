# 课程：step_07_generate_answer.md；访问范围：当前命令只读或预览；写入/生成选项见下文。
"""复用第6步的消息构造；学习者填写一次异步模型调用。"""

import argparse
import asyncio
import json
from urllib.parse import urlsplit

from openai import APIConnectionError, APIStatusError, APITimeoutError, RateLimitError

from app.core.config import get_settings
from app.rag.prompt_builder import build_rag_messages
from learning.pgvector.step_06_build_messages import (
    QUERY,
    load_example_rows,
    rows_to_retrieval_results,
)


async def generate_answer(messages: list[dict[str, str]]) -> str:
    """将已经构造好的消息交给现有模型服务，返回回答正文。"""
    # 只在真实生成路径创建模型服务，默认预览不会进入这里。
    from app.services.llm_service import LLMService

    service = LLMService()
    # 只调整本练习新建的客户端：不自动重试，请求超时20秒。
    service.client = service.client.with_options(max_retries=0, timeout=20.0)
    try:
        # 关键步骤：调用service.complete_messages，参数messages=messages。
        # 用await等待调用结果，将返回的回答字符串赋给answer。
        answer = await service.complete_messages(messages)
        return answer
    finally:
        await service.client.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="预览已有RAG消息，或调用一次聊天模型生成答案。")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--preview", action="store_true", help="本地构造并展示待发送消息；默认模式。")
    mode.add_argument("--ask", action="store_true", help="确认配置后向现有聊天模型发送这些消息。")
    args = parser.parse_args()

    rows = load_example_rows()
    retrieval_results = rows_to_retrieval_results(rows)
    messages = build_rag_messages(query=QUERY, retrieval_results=retrieval_results)
    settings = get_settings()
    print(json.dumps({
        "input_origin": "沿用第6步本地示例；正文来自本地Markdown，不是本次数据库检索。",
        "query": QUERY,
        "chat_model": settings.llm_model,
        "chat_target_host": urlsplit(settings.llm_base_url).hostname,
        "automatic_retries": 0,
        "request_timeout_seconds": 20,
        "messages": messages,
    }, ensure_ascii=False, indent=2))

    if not args.ask:
        print("预览结束：未连接数据库，未调用Embedding或聊天模型。")
        return

    try:
        answer = asyncio.run(generate_answer(messages))
    except RateLimitError:
        print("聊天服务返回429限流，本次失败；没有自动重试。")
        raise SystemExit(1) from None
    except APITimeoutError:
        print("聊天请求超时，本次失败；没有自动重试。")
        raise SystemExit(1) from None
    except APIConnectionError:
        print("无法连接配置的聊天服务，本次失败；没有自动重试。")
        raise SystemExit(1) from None
    except APIStatusError as error:
        print(f"聊天服务返回HTTP {error.status_code}，本次失败；没有自动重试。")
        raise SystemExit(1) from None

    if not answer.strip():
        raise RuntimeError("没有取得回答正文，请检查生成调用；不要把空字符串当作生成成功。")
    print(json.dumps({"query": QUERY, "answer": answer}, ensure_ascii=False, indent=2))
    print("请对照片段正文审核回答。本步尚未返回结构化sources或切换正式检索后端。")


if __name__ == "__main__":
    main()
