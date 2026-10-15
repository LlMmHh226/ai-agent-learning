# 课程：step_20g_node_failure.md；访问范围：本地运行（无外部模型请求）。
"""20G：把预期查询超时转换为状态更新，按错误路线结束；无网络。"""

from typing import Literal
from unittest.mock import patch

from langgraph.graph import END, START, StateGraph

from app.tools.order_tools import get_order_status
from learning.frameworks.step_20c_langgraph_edge import ReplyState, format_answer
from learning.frameworks.step_20d_conditional_route import answer_missing


class FailureState(ReplyState):
    """沿用订单与回答字段；error为None或本例定义的错误代码。"""

    error: str | None


def query_order_safely(state: FailureState) -> dict[str, object]:
    """state由图传入；查询当前订单，返回order_result/error/answer更新。

    只捕获本例约定的TimeoutError，其他异常仍抛出。超时清空旧结果，
    成功清除旧错误；均清空旧回答，避免重复使用之前的数据。
    """
    try:
        order_result = get_order_status(state["order_id"])
    except TimeoutError:
        return {"order_result": {}, "error": "order_query_timeout", "answer": ""}
    return {"order_result": order_result, "error": None, "answer": ""}


def route_after_lookup(state: FailureState) -> Literal["error", "found", "missing"]:
    """读取图应用查询更新后的状态；返回路线标签，不更新State。"""
    if state["error"] is not None:
        return "error"
    if state["order_result"].get("found"):
        return "found"
    return "missing"


def answer_error(state: FailureState) -> dict[str, str]:
    """读取state中的错误代码，返回面向用户的answer更新，不暴露异常原文。"""
    if state["error"] == "order_query_timeout":
        return {"answer": "订单查询超时，暂时无法确认订单信息，请稍后再试。"}
    return {"answer": "订单查询失败，暂时无法确认订单信息。"}


def build_graph():
    """无参数；返回查询后可走成功/未找到/错误三条路线的可执行图。"""
    builder = StateGraph(FailureState)
    builder.add_node("lookup", query_order_safely)
    builder.add_node("reply", format_answer)
    builder.add_node("missing_reply", answer_missing)
    builder.add_node("error_reply", answer_error)
    builder.add_edge(START, "lookup")
    builder.add_conditional_edges(
        "lookup", route_after_lookup,
        {"found": "reply", "missing": "missing_reply", "error": "error_reply"},
    )
    builder.add_edge("reply", END)
    builder.add_edge("missing_reply", END)
    builder.add_edge("error_reply", END)
    return builder.compile()


def main() -> None:
    """无参数入口；检查三条实际路径、旧字段清理及非预期异常传播。"""
    graph = build_graph()
    cases = [
        ("10001", False, "reply", "订单10001的物流单号是SF1234567890。"),
        ("99999", False, "missing_reply", "没有找到订单99999，请核对订单编号。"),
        ("10001", True, "error_reply", "订单查询超时，暂时无法确认订单信息，请稍后再试。"),
    ]
    for order_id, simulate_timeout, expected_node, expected_answer in cases:
        # 故意传旧字段，核对成功会清错、失败会清结果，不能沿用旧答案。
        initial_state: FailureState = {
            "order_id": order_id,
            "order_result": {"found": True, "tracking_number": "OLD"},
            "answer": "旧回答",
            "error": "old_error",
        }
        print("订单：", order_id, "；模拟超时：", simulate_timeout)
        # 只替换本学习模块的调用引用；不修改正式函数或FAKE_ORDERS。
        with patch(__name__ + ".get_order_status", wraps=get_order_status) as query:
            if simulate_timeout:
                query.side_effect = TimeoutError("本地教学模拟超时")
            updates = list(graph.stream(initial_state, stream_mode="updates"))
            query.assert_called_once_with(order_id)
        path = [name for update in updates for name in update]
        assert path == ["lookup", expected_node], path
        assert updates[-1][expected_node]["answer"] == expected_answer
        lookup_update = updates[0]["lookup"]
        assert lookup_update["answer"] == ""
        if simulate_timeout:
            assert lookup_update["order_result"] == {}
            assert lookup_update["error"] == "order_query_timeout"
        else:
            assert lookup_update["error"] is None
        print("查询节点返回的更新：", lookup_update)
        print("实际路径：", " → ".join(path))
        print("最终回答：", updates[-1][expected_node]["answer"])

    # 不把程序错误误报成“查询超时”。
    with patch(__name__ + ".get_order_status", side_effect=ValueError("模拟非预期错误")):
        try:
            graph.invoke({"order_id": "10001", "order_result": {}, "answer": "", "error": None})
        except ValueError:
            print("检查通过：非预期ValueError仍向调用方抛出。")
        else:
            raise AssertionError("非预期错误不应被吞掉。")


if __name__ == "__main__":
    main()
