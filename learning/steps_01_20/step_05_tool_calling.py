# 课程：step_05_tool_calling.md；访问范围：真实外部请求（可能收费）；启动后提交有效问题才调用模型。
"""
第 5 步：让大模型通过工具查询订单。

启动方式（在项目根目录下）：
    python -m uvicorn learning.steps_01_20.step_05_tool_calling:app --reload
"""

import json

from fastapi import FastAPI
from openai import AsyncOpenAI
from pydantic import BaseModel, Field, field_validator

from app.core.config import get_settings
from app.tools.order_tools import GET_ORDER_STATUS_TOOL, get_order_status


SYSTEM_PROMPT = (
    "你是一名电商客服。"
    "当用户查询订单时，必须使用 get_order_status 工具，"
    "不能自己猜测订单信息。"
)


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)

    @field_validator("message")
    @classmethod
    def validate_message(cls, value: str) -> str:
        cleaned_value = value.strip()
        if not cleaned_value:
            raise ValueError("消息不能为空")
        return cleaned_value


class ChatResponse(BaseModel):
    answer: str
    used_tool: bool


app = FastAPI(title="第 5 步：订单工具调用")
settings = get_settings()
client = AsyncOpenAI(
    max_retries=0,
    timeout=30,
    api_key=settings.llm_api_key,
    base_url=settings.llm_base_url,
)


def execute_tool(name: str, arguments: str) -> dict[str, object]:
    """把模型生成的工具请求，转换为真正的 Python 函数调用。"""
    if name != "get_order_status":
        return {"error": f"不支持的工具：{name}"}

    try:
        parsed_arguments = json.loads(arguments)
        order_id = parsed_arguments["order_id"]
    except (json.JSONDecodeError, KeyError, TypeError):
        return {"error": "订单查询参数无效"}

    if not isinstance(order_id, str):
        return {"error": "订单编号必须是字符串"}

    return get_order_status(order_id)


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": request.message,
        },
    ]

    # 第一次调用：模型可以直接回答，也可以申请使用工具。
    first_response = await client.chat.completions.create(
        model=settings.llm_model,
        messages=messages,
        tools=[GET_ORDER_STATUS_TOOL],
        tool_choice="auto",
    )
    assistant_message = first_response.choices[0].message

    # 普通问题不需要工具，直接返回模型答案。
    if not assistant_message.tool_calls:
        return ChatResponse(
            answer=assistant_message.content or "模型没有返回内容",
            used_tool=False,
        )

    # 先把模型的工具申请加入消息列表。
    messages.append(assistant_message.model_dump(exclude_none=True))

    # 模型只生成调用请求；真正的 Python 函数在这里执行。
    for tool_call in assistant_message.tool_calls:
        result = execute_tool(
            name=tool_call.function.name,
            arguments=tool_call.function.arguments,
        )
        messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result, ensure_ascii=False),
            }
        )

    # 第二次调用：模型读取 Python 的查询结果，组织成自然语言。
    final_response = await client.chat.completions.create(
        model=settings.llm_model,
        messages=messages,
    )
    answer = final_response.choices[0].message.content

    return ChatResponse(
        answer=answer or "模型没有返回内容",
        used_tool=True,
    )
