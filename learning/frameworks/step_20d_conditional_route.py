# 课程：step_20d_conditional_route.md；访问范围：本地运行（无外部模型请求）。
"""20D：根据订单查询结果选择后续节点，无模型或网络请求。"""

from typing import Literal

from langgraph.graph import END, START, StateGraph

from learning.frameworks.step_20a_langgraph_state import query_order
from learning.frameworks.step_20c_langgraph_edge import ReplyState, format_answer


def route_after_lookup(state: ReplyState) -> Literal["found", "missing"]:
    """读取图传入的查询后状态，返回路线标签给条件边，不返回状态更新。

    state['order_result']来自query_order；found=True选found，否则选missing。
    Literal描述返回字符串只应为这两个值，不是运行时自动判断逻辑。
    """
    route = "found" if state["order_result"].get("found") else "missing"
    print("路由选择：", route)
    return route


def answer_missing(state: ReplyState) -> dict[str, str]:
    """state由图传入；读取订单号，返回answer字段更新给图。"""
    print("执行missing_reply节点。")
    return {"answer": f"没有找到订单{state['order_id']}，请核对订单编号。"}


def build_graph():
    """无参数；登记查询节点、两个回复节点和条件边，返回可执行图。"""
    builder = StateGraph(ReplyState)
    builder.add_node("lookup", query_order)
    builder.add_node("reply", format_answer)
    builder.add_node("missing_reply", answer_missing)
    builder.add_edge(START, "lookup")
    builder.add_conditional_edges(
        "lookup",
        route_after_lookup,
        {"found": "reply", "missing": "missing_reply"},
    )
    builder.add_edge("reply", END)
    builder.add_edge("missing_reply", END)
    return builder.compile()


def main() -> None:
    """无参数本地入口，验证三个订单的路径及输出，返回None。"""
    graph = build_graph()
    cases = [
        ("10001", "reply", "订单10001的物流单号是SF1234567890。"),
        ("10002", "reply", "订单10002当前状态为待发货，暂无物流单号。"),
        ("99999", "missing_reply", "没有找到订单99999，请核对订单编号。"),
    ]
    for order_id, expected_node, expected_answer in cases:
        initial_state: ReplyState = {"order_id": order_id, "order_result": {}, "answer": ""}
        print("本次订单：", order_id)
        # stream输出每个实际执行节点的更新，供本地验证路径；不是模型流式回答。
        updates = list(graph.stream(initial_state, stream_mode="updates"))
        executed_nodes = [name for update in updates for name in update]
        assert executed_nodes == ["lookup", expected_node], executed_nodes
        assert updates[-1][expected_node]["answer"] == expected_answer
        assert initial_state == {"order_id": order_id, "order_result": {}, "answer": ""}
        print("实际执行路径：", " → ".join(executed_nodes))
        print("最终answer：", updates[-1][expected_node]["answer"])


if __name__ == "__main__":
    main()
