# 课程：step_14_agent_knowledge_loop.md；访问范围：本地运行（无外部模型请求）。
import json

from app.services.llm_service import llm_service


query = "星云机械键盘支持热插拔吗？"
tool_call_id = "call-knowledge-1"
tool_name = "search_knowledge_base"
tool_arguments = json.dumps(
    {"query": query},
    ensure_ascii=False,
)

tool_result = llm_service._execute_tool(
    name=tool_name,
    arguments=tool_arguments,
)

first_result = tool_result["results"][0]
final_answer = (
    "支持。星云机械键盘支持五脚轴热插拔。"
    f"来源：{first_result['source']}，{first_result['chunk_id']}。"
)

messages = [
    {
        "role": "user",
        "content": query,
    },
    {
        "role": "assistant",
        "tool_calls": [
            {
                "id": tool_call_id,
                "type": "function",
                "function": {
                    "name": tool_name,
                    "arguments": tool_arguments,
                },
            }
        ],
    },
    {
        "role": "tool",
        "tool_call_id": tool_call_id,
        "content": json.dumps(tool_result, ensure_ascii=False),
    },
    {
        "role": "assistant",
        "content": final_answer,
    },
]

for index, message in enumerate(messages):
    print(f"\nmessages[{index}] role={message['role']}")
    print(json.dumps(message, ensure_ascii=False, indent=2))
