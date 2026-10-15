# 课程：step_18l_long_dialogue_failure.md；访问范围：本地运行（无外部模型请求）。
"""第18L步：运行正式会话，展示独立退款偏好在原文被裁剪后的保留。"""

import asyncio
from unittest.mock import AsyncMock, patch

from app.services.conversation_service import MAX_HISTORY_TURNS, ConversationService, llm_service


async def main() -> None:
    """无参数；用模拟模型响应走正式chat，打印事实与下轮消息，返回None给入口。"""
    service = ConversationService()
    conversation_id = "refund-preference-demo"
    with patch.object(
        llm_service, "chat_with_messages", new=AsyncMock(return_value="模拟回答")
    ) as model_mock:
        await service.chat(conversation_id, "请查询订单10001")
        await service.chat(conversation_id, "暂不申请退款。")
        for turn in range(MAX_HISTORY_TURNS):
            await service.chat(conversation_id, f"闲聊问题{turn}")

        history = service.histories[conversation_id]
        print(f"保存历史条数：{len(history)}")
        print(f"原偏好仍在history：{any('暂不申请退款' in item['content'] for item in history)}")
        print(f"当前facts：{service.facts[conversation_id]}")

        question = "还是按我之前说的方式处理。"
        await service.chat(conversation_id, question)
        sent_messages = model_mock.await_args.args[0]
        print(f"下一轮输入含订单号：{'当前关注的订单编号是 10001' in sent_messages[0]['content']}")
        print(f"下一轮user副本含偏好：{'暂不申请退款' in sent_messages[-1]['content']}")
        print(f"偏好被放入system了吗：{'暂不申请退款' in sent_messages[0]['content']}")
        print(f"保存的本轮user仍是原问题：{history[-2]['content'] == question}")
        print("下一轮user副本正文：")
        print(sent_messages[-1]["content"])

    print("本步支持已有订单下两句独立声明；不是自动摘要，也没有执行退款或请求真实模型。")


if __name__ == "__main__":
    asyncio.run(main())
