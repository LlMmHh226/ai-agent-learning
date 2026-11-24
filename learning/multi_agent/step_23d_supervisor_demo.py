"""23D 延伸：检查任务依赖，按会话和订单续接待办；只读教学演示。"""

from dataclasses import dataclass, replace
from typing import Literal

from app.repositories.demo_orders import get_demo_order_status
from app.tools.policy_tools import get_after_sales_policy


Action = Literal["order", "policy", "report"]


@dataclass(frozen=True)
class ReturnCase:
    task_id: str
    order_id: str
    order_found: bool | None = None
    policy: str | None = None
    within_window: bool | None = None
    intact_and_resellable: bool | None = None


def ready_actions(case: ReturnCase) -> tuple[Action, ...]:
    if case.order_found is None:
        return ("order",)
    if case.order_found and case.policy is None:
        return ("policy",)
    return ("report",)


def accept_proposal(case: ReturnCase, proposed: Action) -> Action:
    eligible = ready_actions(case)
    return proposed if proposed in eligible else eligible[0]


def review(case: ReturnCase) -> tuple[ReturnCase, list[Action], str]:
    trace: list[Action] = []
    for proposed in ("policy", "policy", "report"):
        action = accept_proposal(case, proposed)
        trace.append(action)
        if action == "order":
            order = get_demo_order_status(case.order_id)
            found = order.get("found") is True and order.get("order_id") == case.order_id
            case = replace(case, order_found=found)
        elif action == "policy":
            result = get_after_sales_policy("退货")
            case = replace(case, policy=str(result["policy"]))
        else:
            if case.order_found is False:
                return case, trace, "未核实订单，不能判断退货条件。"
            missing = [label for label, value in (
                ("是否在签收期限内", case.within_window),
                ("商品是否完好且不影响二次销售", case.intact_and_resellable),
            ) if value is None]
            if missing:
                return case, trace, "等待补充：" + "、".join(missing)
            if case.within_window and case.intact_and_resellable:
                return case, trace, "按提供的信息初步符合样例条件，实际以验收为准。"
            return case, trace, "按提供的信息不满足至少一项样例条件。"
    raise RuntimeError("演示应在有界步骤内汇总")


def main() -> None:
    pending: dict[tuple[str, str], ReturnCase] = {}
    first, trace, answer = review(ReturnCase("return-1", "10001"))
    assert trace == ["order", "policy", "report"] and answer.startswith("等待补充")
    pending[("lesson-session", first.order_id)] = first
    print(first.task_id, trace, answer)

    snapshot = pending[("lesson-session", "10001")]
    assert pending.get(("lesson-session", "10002")) is None
    partial, trace, answer = review(replace(snapshot, within_window=True))
    assert trace == ["report"] and "商品是否完好" in answer
    print(partial.task_id, trace, "已补充期限；只有‘未拆封’时仍然", answer)

    complete, trace, answer = review(replace(partial, intact_and_resellable=True))
    assert trace == ["report"] and complete.task_id == first.task_id and "初步符合" in answer
    pending.pop(("lesson-session", complete.order_id))
    print(complete.task_id, trace, answer)

    _, trace, answer = review(ReturnCase("return-2", "99999"))
    assert trace == ["order", "report"] and "未核实订单" in answer
    print("不存在的订单：", trace, answer)


if __name__ == "__main__":
    main()
