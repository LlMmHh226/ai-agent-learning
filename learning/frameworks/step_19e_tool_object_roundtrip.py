# 课程：step_19e_tool_object_roundtrip.md；访问范围：真实外部请求（可能收费）。
"""19E：把19D的工具对象接入19C的一轮模型/工具往返。"""

import asyncio
import json

from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_openai import ChatOpenAI
from pydantic import ValidationError

from app.core.config import get_settings
from learning.frameworks.step_19c_langchain_order_tool import print_connection_diagnostics
from learning.frameworks.step_19d_langchain_tool_object import lookup_order


def execute_tool_object(tool_call: dict) -> dict[str, object]:
    """接收reply.tool_calls的一项；校验名称，交工具对象执行，返回结果字典。

    name用于允许列表判断；args是模型提供的参数字典，交给invoke。
    返回值交给ask_order里的result，再序列化为ToolMessage正文。
    """
    if tool_call.get("name") != lookup_order.name:
        return {"error": "不支持的工具"}
    arguments = tool_call.get("args")
    # 保留19C只接受order_id字段的约束；@tool默认不等于禁止额外字段。
    if not isinstance(arguments, dict) or set(arguments) != {"order_id"}:
        return {"error": "订单查询参数无效"}
    try:
        return lookup_order.invoke(arguments)
    except ValidationError:
        return {"error": "订单查询参数类型无效"}


async def ask_order(question: str) -> str:
    """question是main传入的用户字符串；成功返回正文str给main的answer。

    仅一轮工具调用；第二次模型请求不再提供工具，保持19C的学习范围。
    """
    settings = get_settings()
    model = ChatOpenAI(
        model=settings.llm_model,
        api_key=settings.llm_api_key,
        base_url=settings.llm_base_url,
        timeout=60,
        max_retries=0,
    )
    model_with_tools = model.bind_tools([lookup_order])
    messages = [
        SystemMessage(content="你是电商客服。查询订单必须调用订单工具，不要猜测。得到结果后用一句话回答；工具失败则说明无法查询。"),
        HumanMessage(content=question),
    ]
    print("第一次ainvoke：发送问题和lookup_order工具说明。")
    reply = await model_with_tools.ainvoke(messages)
    if reply.invalid_tool_calls or not reply.tool_calls:
        raise ValueError("模型未返回可用工具调用。")
    if any(not isinstance(call.get("id"), str) or not call["id"] for call in reply.tool_calls):
        raise ValueError("工具调用缺少有效关联ID。")
    messages.append(reply)
    for tool_call in reply.tool_calls:
        result = execute_tool_object(tool_call)
        print("工具处理结果：", json.dumps(result, ensure_ascii=False))
        messages.append(ToolMessage(
            content=json.dumps(result, ensure_ascii=False),
            tool_call_id=tool_call["id"],
        ))
    print("第二次请求前的消息类型：", [type(item).__name__ for item in messages])
    final_reply = await model.ainvoke(messages)
    if final_reply.tool_calls or final_reply.invalid_tool_calls:
        raise ValueError("第二轮仍请求工具，超出本步范围。")
    if not isinstance(final_reply.content, str) or not final_reply.content.strip():
        raise ValueError("未取得有效文本回答。")
    return final_reply.content


async def main() -> None:
    """无参数入口，打印最终回答或脱敏异常；返回None。"""
    try:
        answer = await ask_order("请查询订单10001的物流单号。")
    except Exception as error:
        print("调用未完成，异常类型：", type(error).__name__)
        status_code = getattr(error, "status_code", None)
        if isinstance(status_code, int):
            print("HTTP状态码：", status_code)
        print_connection_diagnostics(error)
        raise SystemExit(1) from None
    print("main里的answer：", answer)


if __name__ == "__main__":
    asyncio.run(main())
