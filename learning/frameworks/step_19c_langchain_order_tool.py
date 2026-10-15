# 课程：step_19c_langchain_order_tool.md；访问范围：真实外部请求（可能收费）。
"""19C：绑定一个订单工具，最多执行一轮工具调用，再生成回答。"""

import asyncio
import json

from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_openai import ChatOpenAI

from app.core.config import get_settings
from app.tools.order_tools import GET_ORDER_STATUS_TOOL, get_order_status


def execute_order_call(tool_call: dict) -> dict[str, object]:
    """校验LangChain调用请求并执行订单函数。

    tool_call：来自reply.tool_calls的一项字典，包含name、args、id。
    返回：订单结果或错误字典，交给ask_order构造ToolMessage。
    """
    if tool_call.get("name") != "get_order_status":
        return {"error": "不支持的工具"}
    arguments = tool_call.get("args")
    if not isinstance(arguments, dict) or set(arguments) != {"order_id"}:
        return {"error": "订单查询参数无效"}
    order_id = arguments["order_id"]
    if not isinstance(order_id, str):
        return {"error": "订单编号必须是字符串"}
    return get_order_status(order_id)


async def ask_order(question: str) -> str:
    """question来自main的用户问题；返回最终正文str给main的answer。

    第一轮提供订单工具定义，执行返回的工具请求；第二轮只生成文本。
    这是一次工具往返的学习流程，不是通用多轮Agent运行器。
    """
    settings = get_settings()
    model = ChatOpenAI(
        model=settings.llm_model,
        api_key=settings.llm_api_key,
        base_url=settings.llm_base_url,
        timeout=60,
        max_retries=0,
    )
    model_with_tools = model.bind_tools([GET_ORDER_STATUS_TOOL])
    messages = [
        SystemMessage(content="你是电商客服。查询订单必须调用订单工具，不要猜测。得到结果后用一句话回答；工具失败则说明无法查询。"),
        HumanMessage(content=question),
    ]
    print("第一次ainvoke：发送问题和工具说明。")
    reply = await model_with_tools.ainvoke(messages)
    if reply.invalid_tool_calls:
        raise ValueError("模型返回了无法解析的工具调用。")
    if not reply.tool_calls:
        raise ValueError("模型未提出工具调用，本步工具链尚未走通。")
    if any(not isinstance(call.get("id"), str) or not call["id"] for call in reply.tool_calls):
        raise ValueError("工具调用缺少有效关联ID。")
    messages.append(reply)
    for tool_call in reply.tool_calls:
        result = execute_order_call(tool_call)
        print("Python已处理工具请求，结果：", json.dumps(result, ensure_ascii=False))
        messages.append(ToolMessage(
            content=json.dumps(result, ensure_ascii=False),
            tool_call_id=tool_call["id"],
        ))
    print("第二次请求前的消息类型：", [type(item).__name__ for item in messages])
    # 使用未绑定工具的model：本步第二轮只根据已有结果生成文本。
    final_reply = await model.ainvoke(messages)
    if final_reply.tool_calls or final_reply.invalid_tool_calls:
        raise ValueError("第二轮仍请求工具，超出本步的一轮工具调用范围。")
    if not isinstance(final_reply.content, str) or not final_reply.content.strip():
        raise ValueError("未取得有效的文本回答。")
    return final_reply.content


async def main() -> None:
    """无参数学习入口，打印ask_order返回的answer；返回None。"""
    try:
        answer = await ask_order("请查询订单10001的物流单号。")
    except Exception as error:
        print("调用未完成，异常类型：", type(error).__name__)
        status_code = getattr(error, "status_code", None)
        if isinstance(status_code, int):
            print("HTTP状态码：", status_code)
        print_connection_diagnostics(error)
        print("已停止；不打印异常正文或密钥。")
        raise SystemExit(1) from None
    print("main里的answer：", answer)


def print_connection_diagnostics(error: BaseException) -> None:
    """读取main捕获的异常链，只打印类型和系统错误码；返回None。

    不打印异常正文、请求头、URL或配置，避免输出密钥。
    """
    pending = [error]
    seen = set()
    while pending:
        current = pending.pop()
        if id(current) in seen:
            continue
        seen.add(id(current))
        print("诊断异常类型：", type(current).__name__)
        for attribute in ("errno", "winerror", "verify_code"):
            value = getattr(current, attribute, None)
            if isinstance(value, int):
                print(f"  {attribute}：{value}")
        cause = current.__cause__ or current.__context__
        if cause is not None:
            pending.append(cause)
        if isinstance(current, BaseExceptionGroup):
            pending.extend(current.exceptions)


if __name__ == "__main__":
    asyncio.run(main())
