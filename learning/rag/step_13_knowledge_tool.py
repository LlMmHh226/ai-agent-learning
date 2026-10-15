# 课程：step_13_knowledge_tool.md；访问范围：本地运行（无外部模型请求）。
import json

from app.services.llm_service import AVAILABLE_TOOLS
from app.tools.knowledge_tools import search_knowledge_base


tool_names = [
    tool["function"]["name"]
    for tool in AVAILABLE_TOOLS
]
result = search_knowledge_base(
    query="星云机械键盘支持热插拔吗？"
)

print(f"已注册工具：{tool_names}")
print("知识库工具执行结果：")
print(json.dumps(result, ensure_ascii=False, indent=2))
