# 课程：step_20e_checkpoint.md；访问范围：本地运行（无外部模型请求）。
"""20E：通过内存检查点按thread_id取回状态，无模型或网络请求。"""

from typing import Literal

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph

from learning.frameworks.step_20a_langgraph_state import query_order
from learning.frameworks.step_20c_langgraph_edge import ReplyState


class SessionState(ReplyState):
    """沿用订单与回答字段，request由入口明确指定，不由模型识别。"""

    request: Literal["status", "tracking"]


def reply_to_request(state: SessionState) -> dict[str, str]:
    """state由图传入；根据当前request读取查询结果，返回answer更新。

    request=status时回答状态，tracking时回答物流；不生成自然语言意图。
    """
    result = state["order_result"]
    if not result.get("found"):
        answer = "没有找到该订单。"
    elif state["request"] == "status":
        answer = f"订单{state['order_id']}状态：{result['status']}。"
    elif state["request"] == "tracking":
        tracking_number = result.get("tracking_number") or "暂无物流单号"
        answer = f"订单{state['order_id']}物流：{tracking_number}。"
    else:
        raise ValueError("本步仅支持status或tracking请求。")
    return {"answer": answer}


def build_graph():
    """无参数；为新图创建一个内存保存器，返回可执行图给main。

    同一图在进程内复用保存器；再次调用build_graph得到新保存器，不含旧状态。
    """
    builder = StateGraph(SessionState)
    builder.add_node("lookup", query_order)
    builder.add_node("reply", reply_to_request)
    builder.add_edge(START, "lookup")
    builder.add_edge("lookup", "reply")
    builder.add_edge("reply", END)
    checkpointer = InMemorySaver()
    return builder.compile(checkpointer=checkpointer)


def main() -> None:
    """无参数入口；用两个会话验证跨执行保留和本例隔离，返回None。"""
    graph = build_graph()
    config_c1 = {"configurable": {"thread_id": "c1"}}
    config_c2 = {"configurable": {"thread_id": "c2"}}

    first = graph.invoke(
        {"order_id": "10001", "order_result": {}, "answer": "", "request": "status"},
        config=config_c1,
    )
    print("c1第一次：", first["answer"])
    assert first["answer"] == "订单10001状态：已发货。"

    other = graph.invoke(
        {"order_id": "10002", "order_result": {}, "answer": "", "request": "status"},
        config=config_c2,
    )
    assert other["order_id"] == "10002"

    follow_up = {"request": "tracking"}
    print("c1第二次只传：", follow_up)
    second = graph.invoke(follow_up, config=config_c1)
    print("c1第二次恢复的order_id：", second["order_id"])
    print("c1第二次回答：", second["answer"])
    assert second["order_id"] == "10001"
    assert second["answer"] == "订单10001物流：SF1234567890。"
    assert graph.get_state(config_c2).values["order_id"] == "10002"
    assert graph.get_state(config_c2).values["request"] == "status"

    # 新图使用全新内存保存器，即使thread_id相同也没有旧记录。
    fresh_graph = build_graph()
    assert not fresh_graph.get_state(config_c1).values
    print("检查通过：c1取回旧订单，c2未被改写，新保存器没有旧状态。")


if __name__ == "__main__":
    main()
