# 课程：step_20c_langgraph_edge.md；访问范围：本地运行（无外部模型请求）。
"""20C：连接查询与整理回答两个节点，观察更新后的状态传递。"""

from langgraph.graph import END, START, StateGraph

from learning.frameworks.step_20a_langgraph_state import OrderState, query_order


class ReplyState(OrderState):
    """沿用order_id和order_result两个字段，再添加answer字符串。"""

    answer: str


def format_answer(state: ReplyState) -> dict[str, str]:
    """读取图传入的查询结果，用固定Python规则生成answer字段更新。

    state来自lookup节点更新后的状态；order_result是本地订单函数结果。
    返回值交给图更新answer，不调用模型，也不修改输入状态。
    """
    order_result = state["order_result"]
    print("整理回答节点读到的order_result：", order_result)
    if not order_result.get("found"):
        answer = "没有找到该订单。"
    elif order_result.get("tracking_number"):
        answer = f"订单{state['order_id']}的物流单号是{order_result['tracking_number']}。"
    else:
        answer = f"订单{state['order_id']}当前状态为{order_result['status']}，暂无物流单号。"
    return {"answer": answer}


def build_graph():
    """无参数；返回固定按lookup→reply执行的图，供main调用。"""
    builder = StateGraph(ReplyState)
    builder.add_node("lookup", query_order)
    builder.add_node("reply", format_answer)
    builder.add_edge(START, "lookup")
    builder.add_edge("lookup", "reply")
    builder.add_edge("reply", END)
    return builder.compile()


def main() -> None:
    """无参数本地入口，检查已发货/待发货/不存在的订单；返回None。"""
    graph = build_graph()
    expected_answers = {
        "10001": "订单10001的物流单号是SF1234567890。",
        "10002": "订单10002当前状态为待发货，暂无物流单号。",
        "99999": "没有找到该订单。",
    }
    for order_id, expected_answer in expected_answers.items():
        initial_state: ReplyState = {
            "order_id": order_id, "order_result": {}, "answer": "",
        }
        print("输入状态：", initial_state)
        final_state = graph.invoke(initial_state)
        print("最终answer：", final_state["answer"])
        assert final_state["answer"] == expected_answer
        assert final_state["order_id"] == order_id
        assert initial_state == {"order_id": order_id, "order_result": {}, "answer": ""}


if __name__ == "__main__":
    main()
