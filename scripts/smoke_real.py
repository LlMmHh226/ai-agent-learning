"""真实验收：一次聊天加一次订单工具往返，最多三次请求，不自动重试。"""
import asyncio
import json
from openai import AsyncOpenAI
from app.core.config import get_settings
from app.tools.order_tools import GET_ORDER_STATUS_TOOL, get_order_status
from scripts.check_config import main as check_config


async def main() -> None:
    check_config()
    settings = get_settings()
    async with AsyncOpenAI(api_key=settings.llm_api_key, base_url=settings.llm_base_url,
                           timeout=30, max_retries=0) as client:
        try:
            greeting = await client.chat.completions.create(
                model=settings.llm_model, messages=[{'role': 'user', 'content': '请用一句中文打招呼。'}])
            if not greeting.choices[0].message.content:
                raise ValueError('empty_greeting')
            print('CHAT_OK')
            messages = [
                {'role': 'system', 'content': '你是客服。订单问题必须调用工具，再根据工具数据回答，不得编造。'},
                {'role': 'user', 'content': '查询订单10001的物流单号。'},
            ]
            response = await client.chat.completions.create(
                model=settings.llm_model, messages=messages, tools=[GET_ORDER_STATUS_TOOL], tool_choice='auto')
            reply = response.choices[0].message
            if not reply.tool_calls or len(reply.tool_calls) != 1:
                raise ValueError('expected_one_tool_call')
            call = reply.tool_calls[0]
            if call.function.name != 'get_order_status' or json.loads(call.function.arguments) != {'order_id': '10001'}:
                raise ValueError('unexpected_tool_or_arguments')
            result = get_order_status('10001')
            messages.extend([
                reply.model_dump(exclude_none=True),
                {'role': 'tool', 'tool_call_id': call.id, 'content': json.dumps(result, ensure_ascii=False)},
            ])
            final = await client.chat.completions.create(model=settings.llm_model, messages=messages)
            answer = final.choices[0].message.content or ''
            if result['tracking_number'] not in answer:
                raise ValueError('answer_does_not_include_tracking_number')
            print('TOOL_ROUNDTRIP_OK')
        except Exception as error:
            # No exception body, request headers, model/provider names or credentials.
            status = getattr(error, 'status_code', None)
            print(f'REAL_CHECK_STOPPED type={type(error).__name__} status={status}')
            print('已停止；429请等待额度恢复，401/403检查权限，连接错误检查地址和网络。')
            raise SystemExit(1) from None


if __name__ == '__main__':
    asyncio.run(main())
