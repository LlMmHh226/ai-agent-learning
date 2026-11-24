"""22A：校验工具参数，并在本地函数和注入的网关之间选择执行路径。"""

import asyncio
from collections.abc import Awaitable, Callable
import json
import re

from app.repositories.demo_orders import get_demo_order_status


def parse_order_arguments(arguments: str) -> str:
    try:
        data = json.loads(arguments)
    except json.JSONDecodeError:
        raise ValueError("工具参数不是合法 JSON") from None
    if not isinstance(data, dict) or set(data) != {"order_id"}:
        raise ValueError("工具参数只接受 order_id 字段")
    order_id = data["order_id"]
    if not isinstance(order_id, str) or not re.fullmatch(r"[0-9]{5}", order_id):
        raise ValueError("order_id 必须是五位数字字符串")
    return order_id


async def dispatch_order(
    arguments: str, gateway: Callable[[str], Awaitable[dict[str, object]]] | None = None,
) -> dict[str, object]:
    order_id = parse_order_arguments(arguments)
    if gateway is None:
        return get_demo_order_status(order_id)
    return await gateway(order_id)


async def main() -> None:
    calls: list[str] = []

    async def fake_gateway(order_id: str) -> dict[str, object]:
        calls.append(order_id)
        return get_demo_order_status(order_id)

    good = '{"order_id":"10001"}'
    native = await dispatch_order(good)
    through_gateway = await dispatch_order(good, fake_gateway)
    assert native == through_gateway and native["found"] is True
    for invalid in ('{"order_id":10001}', '["10001"]', '{"order_id":"10001","extra":true}', '{'):
        try:
            await dispatch_order(invalid, fake_gateway)
        except ValueError as error:
            print("参数已拦截：", error)
        else:
            raise AssertionError("无效参数不能进入业务网关")
    assert calls == ["10001"]
    print("两条路径使用同一个业务数据契约：", native)
    print("本课网关是固定的本地函数；下一课改成真实 stdio。")


if __name__ == "__main__":
    asyncio.run(main())
