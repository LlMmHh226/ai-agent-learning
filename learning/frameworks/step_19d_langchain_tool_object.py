# 课程：step_19d_langchain_tool_object.md；访问范围：本地运行（无外部模型请求）。
"""19D：用@tool包装已有业务函数，本地执行，不请求模型。"""

from langchain_core.tools import tool
from pydantic import ValidationError

from app.tools.order_tools import get_order_status


@tool
def lookup_order(order_id: str) -> dict[str, object]:
    """根据订单编号查询订单状态、商品名称和物流单号。

    Args:
        order_id: 订单编号字符串，例如10001；来自invoke传入的参数字典。
    """
    # 保留正式业务函数，包装层不复制订单查询逻辑。
    return get_order_status(order_id)


def main() -> None:
    """无参数学习入口；打印工具说明与本地结果，返回None。"""
    print("lookup_order现在的类型：", type(lookup_order).__name__)
    print("工具名称：", lookup_order.name)
    print("参数说明：", lookup_order.args)

    arguments = {"order_id": "10001"}
    result = lookup_order.invoke(arguments)
    print("invoke返回类型：", type(result).__name__)
    print("invoke返回结果：", result)
    assert result == get_order_status("10001")

    # 缺少必填字段时，工具对象先拒绝输入，业务函数不会执行。
    try:
        lookup_order.invoke({})
    except ValidationError:
        print("缺少order_id：工具参数校验失败。")
    else:
        raise AssertionError("预期缺少必填参数被拒绝。")


if __name__ == "__main__":
    main()
