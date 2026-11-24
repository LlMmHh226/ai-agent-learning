"""23D：一次路由决定入口；模型候选以固定字典模拟，无模型调用。"""

import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, ValidationError


class Decision(BaseModel):
    model_config = ConfigDict(extra="forbid")
    route: Literal["order_only", "order_then_returns", "clarify"]
    order_id: str | None


def choose_route(question: str, proposal: dict[str, object]) -> Decision:
    clarify = Decision(route="clarify", order_id=None)
    try:
        candidate = Decision.model_validate(proposal)
    except ValidationError:
        return clarify
    mentioned = set(re.findall(r"(?<![0-9])[0-9]{5}(?![0-9])", question))
    if candidate.route == "clarify" or not candidate.order_id or mentioned != {candidate.order_id}:
        return clarify
    return candidate


def dispatch(decision: Decision) -> str:
    if decision.route == "order_only":
        return f"订单 {decision.order_id} → 结束"
    if decision.route == "order_then_returns":
        return f"订单 {decision.order_id} → 售后 → 结束"
    return "追问订单编号或诉求 → 结束"


def main() -> None:
    cases = (
        ("查订单10001的物流", {"route": "order_only", "order_id": "10001"}, "order_only"),
        ("看看订单10001能不能退", {"route": "order_then_returns", "order_id": "10001"}, "order_then_returns"),
        ("帮我查物流", {"route": "order_only", "order_id": "10001"}, "clarify"),
        ("订单10001和10002的物流", {"route": "order_only", "order_id": "10001"}, "clarify"),
        ("订单10001的状态", {"route": "退款", "order_id": "10001"}, "clarify"),
    )
    for question, proposal, expected in cases:
        decision = choose_route(question, proposal)
        assert decision.route == expected
        print(question, "| 候选：", proposal, "| 分派：", dispatch(decision))


if __name__ == "__main__":
    main()
