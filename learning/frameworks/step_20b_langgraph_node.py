# 课程：step_20b_langgraph_node.md；访问范围：本地运行（无外部模型请求）。
"""20B：登记一个现有函数为节点，观察何时执行及参数从哪里来。"""

from langgraph.graph import END, START, StateGraph

from learning.frameworks.step_20a_langgraph_state import OrderState, query_order


def main() -> None:
    """无参数入口；复用query_order，打印节点登记和执行顺序，返回None。"""
    builder = StateGraph(OrderState)
    print("1. 准备登记节点，尚未查询订单。")

    # 字符串是图里的步骤名，query_order是不带括号的函数对象。
    builder.add_node("lookup", query_order)
    print("2. 已登记lookup节点，query_order尚未执行。")

    # 连接使用节点名lookup，不使用Python函数名query_order。
    builder.add_edge(START, "lookup")
    builder.add_edge("lookup", END)
    graph = builder.compile()
    print("3. 已创建可执行图，仍未查询订单。")

    initial_state: OrderState = {"order_id": "10002", "order_result": {}}
    print("4. 开始graph.invoke，输入状态：", initial_state)
    final_state = graph.invoke(initial_state)
    print("5. 图执行完成，最终状态：", final_state)

    assert final_state["order_id"] == "10002"
    assert final_state["order_result"]["status"] == "待发货"
    assert final_state["order_result"]["tracking_number"] == ""
    assert initial_state == {"order_id": "10002", "order_result": {}}


if __name__ == "__main__":
    main()
