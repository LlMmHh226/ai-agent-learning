"""23C：两个实际运行的 LangGraph 工具循环，用结构化订单事实交接。"""

import argparse
import asyncio
import json
import re
from typing import Literal, TypedDict

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.graph import END, START, StateGraph

from app.tools.policy_tools import get_after_sales_policy
from learning.frameworks.step_20i_tool_loop_graph import AgentState, build_graph
from learning.multi_agent.step_23b_order_agent import build_order_agent, build_order_input


AFTER_SALES_PROMPT = (
    "你是售后 Agent。使用 lookup_policy 查退货规则。收到的 JSON 是订单证据。"
    "缺少签收时间、商品完好情况时追问，不根据已发货推断可以退货。"
    "只核对政策，不发起申请或退款。"
)


@tool
def lookup_policy(topic: Literal["退货", "换货", "退款"]) -> dict[str, object]:
    """按主题读取本地售后政策。"""
    return get_after_sales_policy(topic)


class ServiceState(TypedDict, total=False):
    order_id: str
    order_result: dict[str, object]
    policy_result: dict[str, object]
    answer: str


def build_after_sales_input(order_id: str, order_result: dict[str, object]) -> AgentState:
    task = f"核对订单{order_id}的退货条件。订单证据：{json.dumps(order_result, ensure_ascii=False)}"
    return {"messages": [SystemMessage(content=AFTER_SALES_PROMPT), HumanMessage(content=task)]}


def read_tool_result(messages, tool_name: str) -> dict[str, object]:
    for message in reversed(messages):
        if isinstance(message, ToolMessage) and message.name == tool_name and isinstance(message.content, str):
            result = json.loads(message.content)
            if isinstance(result, dict):
                return result
    raise ValueError(f"没有得到 {tool_name} 的结构化事实")


def build_service_graph(model):
    order_agent = build_order_agent(model)
    after_sales_agent = build_graph(model, tools=[lookup_policy])

    async def order_node(state: ServiceState) -> ServiceState:
        result = await order_agent.ainvoke(
            build_order_input(f"请查询订单{state['order_id']}。"), config={"recursion_limit": 6},
        )
        evidence = read_tool_result(result["messages"], "lookup_order")
        if evidence.get("found") is not True or evidence.get("order_id") != state["order_id"]:
            return {"order_result": evidence, "answer": "未核实这笔订单，未运行售后角色。"}
        return {"order_result": evidence}

    def next_after_order(state: ServiceState) -> Literal["after_sales", "stop"]:
        evidence = state["order_result"]
        return "after_sales" if evidence.get("found") is True and evidence.get("order_id") == state["order_id"] else "stop"

    async def after_sales_node(state: ServiceState) -> ServiceState:
        result = await after_sales_agent.ainvoke(
            build_after_sales_input(state["order_id"], state["order_result"]), config={"recursion_limit": 6},
        )
        return {"policy_result": read_tool_result(result["messages"], "lookup_policy"),
                "answer": str(result["messages"][-1].content)}

    graph = StateGraph(ServiceState)
    graph.add_node("order", order_node)
    graph.add_node("after_sales", after_sales_node)
    graph.add_edge(START, "order")
    graph.add_conditional_edges("order", next_after_order, {"after_sales": "after_sales", "stop": END})
    graph.add_edge("after_sales", END)
    return graph.compile()


class ScriptedModel:
    """模拟模型固定输出 Tool Call 与最终文本；ToolNode 与业务工具真实运行。"""

    def __init__(self, tool_name: str = "") -> None:
        self.tool_name = tool_name

    def bind_tools(self, tools):
        selected, = tools
        return ScriptedModel(selected.name)

    async def ainvoke(self, messages) -> AIMessage:
        latest = messages[-1]
        if isinstance(latest, ToolMessage):
            if self.tool_name == "lookup_order":
                return AIMessage(content="订单查询结束，以工具结果为准。")
            return AIMessage(content="请补充签收时间，并确认商品完好且不影响二次销售。")
        if self.tool_name == "lookup_order":
            matched = re.search(r"[0-9]{5}", str(latest.content))
            if matched is None:
                raise ValueError("教学输入需要一个五位的订单号")
            arguments = {"order_id": matched.group()}
        else:
            arguments = {"topic": "退货"}
        return AIMessage(content="", tool_calls=[{"name": self.tool_name, "args": arguments,
                                                   "id": f"demo-{self.tool_name}"}])


async def demo(order_ids: tuple[str, ...]) -> None:
    graph = build_service_graph(ScriptedModel())
    for order_id in order_ids:
        outcome = await graph.ainvoke({"order_id": order_id})
        if order_id == "10001":
            assert outcome["policy_result"]["topic"] == "退货"
        if order_id == "99999":
            assert outcome["order_result"]["found"] is False and "policy_result" not in outcome
        print(json.dumps(outcome, ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--order-id")
    args = parser.parse_args()
    if args.order_id is not None and not re.fullmatch(r"[0-9]{5}", args.order_id):
        parser.error("订单号须为五位数字字符串")
    asyncio.run(demo((args.order_id,) if args.order_id else ("10001", "99999")))


if __name__ == "__main__":
    main()
