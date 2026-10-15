# 课程：step_20a_langgraph_state.md；访问范围：本地运行（无外部模型请求）。
"""20A：一个固定步骤读取State，并返回部分字段更新；不调用模型。"""

from copy import deepcopy
from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from app.tools.order_tools import get_order_status


class OrderState(TypedDict):
    """描述本步状态字典：订单号由入口提供，订单结果由查询步骤补充。"""

    order_id: str
    order_result: dict[str, object]


def query_order(state: OrderState) -> dict[str, object]:
    """读取图传入的状态，返回order_result字段的更新，不原地修改state。

    state来自本次graph.invoke输入及图内已应用的更新；本步含order_id。
    返回值交给LangGraph更新本次状态，不是直接返回给main的完整状态。
    """
    order_id = state["order_id"]
    order_result = get_order_status(order_id)
    update = {"order_result": order_result}
    print("查询步骤返回的更新：", update)
    return update


def build_graph():
    """无参数；创建只有查询步骤的可执行图，返回给main中的graph。"""
    builder = StateGraph(OrderState)
    builder.add_node("query_order", query_order)
    builder.add_edge(START, "query_order")
    builder.add_edge("query_order", END)
    return builder.compile()


def main() -> None:
    """构造输入状态并执行图，打印最终状态；无参数，返回None。"""
    graph = build_graph()
    initial_state: OrderState = {
        "order_id": "10001",
        "order_result": {},
    }
    snapshot = deepcopy(initial_state)
    print("输入状态：", initial_state)
    final_state = graph.invoke(initial_state)
    print("最终状态：", final_state)
    print("原输入字典：", initial_state)
    assert final_state["order_id"] == "10001"
    assert final_state["order_result"]["tracking_number"] == "SF1234567890"
    assert initial_state == snapshot

    # 第二次独立执行，检查结果来自本次输入，不自动沿用前次订单。
    missing_state = graph.invoke({"order_id": "99999", "order_result": {}})
    assert missing_state["order_id"] == "99999"
    assert missing_state["order_result"]["found"] is False
    print("另一输入99999的结果：", missing_state)


if __name__ == "__main__":
    main()
