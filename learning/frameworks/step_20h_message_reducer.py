# 课程：step_20h_message_reducer.md；访问范围：本地运行（无外部模型请求）。
"""20H：对照消息字段的默认替换与add_messages合并，不调用模型。"""

from copy import deepcopy
from typing import Annotated, TypedDict

from langchain_core.messages import AIMessage, AnyMessage, HumanMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages


class ReplaceState(TypedDict):
    """未指定合并规则，节点返回messages会替换该字段。"""

    messages: list[AnyMessage]


class MergeState(TypedDict):
    """Annotated附带add_messages，告诉图如何合并messages字段。"""

    messages: Annotated[list[AnyMessage], add_messages]


def reply_node(state: ReplaceState) -> dict[str, list[AIMessage]]:
    """图传入含当前用户问题的state；返回仅一条新消息，交给图处理。

    本步输入保证最后一条是文本用户消息。正文由Python拼接，不请求模型。
    返回字段相同；使用替换还是合并由各自图的状态结构决定。
    """
    question = state["messages"][-1].content
    reply = AIMessage(content=f"模拟回答：收到你的问题“{question}”。", id="a2")
    return {"messages": [reply]}


def build_graph(state_schema):
    """state_schema由main传入ReplaceState或MergeState；返回单节点图。

    两种结构都含messages，节点只按相同结构读取；不更改回复函数。
    """
    builder = StateGraph(state_schema)
    # 显式采用当前图的输入结构，避免节点注解被推断为另一种字段规则。
    builder.add_node("reply", reply_node, input_schema=state_schema)
    builder.add_edge(START, "reply")
    builder.add_edge("reply", END)
    return builder.compile()


def main() -> None:
    """无参数；比较同一输入在两图中的输出，并检查同ID消息更新规则。"""
    original_messages = [
        HumanMessage(content="查询订单10001。", id="u1"),
        AIMessage(content="模拟旧回答：订单10001已发货。", id="a1"),
        HumanMessage(content="它的物流单号是什么？", id="u2"),
    ]
    print("两图输入均为3条消息；节点均只返回1条新消息。")
    replaced = build_graph(ReplaceState).invoke({"messages": deepcopy(original_messages)})
    merged = build_graph(MergeState).invoke({"messages": deepcopy(original_messages)})
    print("默认替换后：", len(replaced["messages"]), "条")
    print("add_messages合并后：", len(merged["messages"]), "条")
    for message in merged["messages"]:
        print(type(message).__name__, message.id, message.content)
    assert [m.id for m in replaced["messages"]] == ["a2"]
    assert [m.id for m in merged["messages"]] == ["u1", "a1", "u2", "a2"]
    assert len(original_messages) == 3

    # add_messages按ID合并：相同ID是更新，不会再追加一条重复消息。
    revised = add_messages(
        merged["messages"], [AIMessage(content="模拟修订回答。", id="a2")],
    )
    assert len(revised) == 4
    assert revised[-1].content == "模拟修订回答。"
    assert merged["messages"][-1].content != "模拟修订回答。"
    print("相同ID修订后仍为4条，最后一条内容已更新。")


if __name__ == "__main__":
    main()
