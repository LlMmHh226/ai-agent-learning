# 课程：step_20f_interrupt_resume.md；访问范围：本地运行（无外部模型请求）。
"""20F：暂停等待确认，再恢复图；只做本地模拟，不执行退款。"""

from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt


class ApprovalState(TypedDict):
    """入口提供订单号，确认节点写approved，结束节点写模拟结果。"""

    order_id: str
    approved: bool | None
    result: str


def confirm_refund(state: ApprovalState) -> dict[str, bool]:
    """state来自图；interrupt暂停，恢复后返回的布尔值写入approved。

    interrupt里的字典是给调用方展示的确认内容，不是同意结果。
    approved来自Command(resume=...)，本例只接受bool，不推断文字意愿。
    """
    print("进入confirm节点；首次和恢复时都会执行到这里。")
    approved = interrupt({
        "order_id": state["order_id"],
        "question": "是否同意继续本地退款演示？不会实际退款。",
    })
    if not isinstance(approved, bool):
        raise ValueError("本步确认值必须为True或False。")
    print("interrupt已取得恢复值：", approved)
    return {"approved": approved}


def record_demo_result(state: ApprovalState) -> dict[str, str]:
    """读取确认后的state，返回纯文本模拟结果；无外部业务操作。"""
    if state["approved"] is True:
        result = f"订单{state['order_id']}：模拟确认已同意，未执行真实退款。"
    elif state["approved"] is False:
        result = f"订单{state['order_id']}：确认已拒绝，未执行退款。"
    else:
        raise ValueError("尚未取得确认结果。")
    print("执行finish节点：", result)
    return {"result": result}


def build_graph():
    """无参数，创建内存检查点图；返回同一进程内可暂停/恢复的图。"""
    builder = StateGraph(ApprovalState)
    builder.add_node("confirm", confirm_refund)
    builder.add_node("finish", record_demo_result)
    builder.add_edge(START, "confirm")
    builder.add_edge("confirm", "finish")
    builder.add_edge("finish", END)
    return builder.compile(checkpointer=InMemorySaver())


def main() -> None:
    """演示同意与拒绝两个独立会话；恢复值为手写模拟值，不是真人审批。"""
    graph = build_graph()
    for thread_id, simulated_decision in (("approve-demo", True), ("reject-demo", False)):
        config = {"configurable": {"thread_id": thread_id}}
        paused = graph.invoke(
            {"order_id": "10001", "approved": None, "result": ""},
            config=config,
        )
        print("暂停提示：", paused["__interrupt__"][0].value)
        snapshot = graph.get_state(config)
        assert snapshot.values["approved"] is None
        assert snapshot.values["result"] == ""
        assert snapshot.next == ("confirm",)
        print("暂停时approved仍为None，finish未执行。")

        # 本地演示预先写好True/False；真实应用应收集用户决定后再恢复。
        final_state = graph.invoke(Command(resume=simulated_decision), config=config)
        assert final_state["approved"] is simulated_decision
        assert final_state["result"]
        assert not graph.get_state(config).next
        print("最终结果：", final_state["result"])


if __name__ == "__main__":
    main()
