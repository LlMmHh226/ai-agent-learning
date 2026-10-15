# 课程：step_18f_tool_result_compression.md；访问范围：本地运行（无外部模型请求）。
"""第18F步：针对状态/物流问题筛选订单工具字段，仅使用项目本地模拟数据。"""

import json

from app.tools.order_tools import get_order_status


def compress_order_result(result: dict[str, object]) -> dict[str, object]:
    """为只问订单状态和物流单号的问题准备较短的工具结果。

    参数：
        result：main调用正式get_order_status(order_id)取得的字典；键为字符串，
            值可为bool或字符串等对象。成功结果提供found、order_id、status、
            product和tracking_number，本函数只筛选本问题所需字段。
    返回：
        新字典，赋给main中的compact_result，随后转为tool消息的JSON正文。
        成功时保留found、order_id、status、tracking_number；失败或错误时复制
        原结果，保留原因。不修改输入、不生成订单事实，也不调用模型。
    适用范围：
        仅用于只问状态/物流的问题；若问题需要商品信息，应保留product。
    """
    if not result.get("found"):
        return dict(result)

    return {
        "found": result["found"],
        "order_id": result["order_id"],
        "status": result["status"],
        "tracking_number": result["tracking_number"],
    }


def main() -> None:
    """无参数；验证三个本地订单结果的筛选与消息格式，打印后返回None给模块入口。"""
    for order_id in ("10001", "10002", "99999"):
        user_question = f"订单{order_id}现在是什么状态，物流单号是什么？"
        # 调用正式函数，但它的数据源是项目FAKE_ORDERS，并非外部订单API。
        result = get_order_status(order_id)
        original_result = dict(result)
        compact_result = compress_order_result(result)

        raw_content = json.dumps(result, ensure_ascii=False)
        compact_content = json.dumps(compact_result, ensure_ascii=False)
        tool_message = {
            "role": "tool",
            # 仅模拟消息格式；正式Tool Loop从模型返回的tool_call.id取得这个值。
            "tool_call_id": f"demo-order-{order_id}",
            "content": compact_content,
        }

        if result.get("found"):
            preserved = all(
                compact_result[field] == result[field]
                for field in ("found", "order_id", "status", "tracking_number")
            )
        else:
            preserved = compact_result == result

        print(f"问题：{user_question}")
        print(f"正式函数原结果：{raw_content}")
        print(f"学习压缩结果：{compact_content}")
        print(f"JSON正文字符数：{len(raw_content)} → {len(compact_content)}")
        print(f"关键字段或失败信息保留：{preserved}")
        print(f"原result没有被修改：{result == original_result}")
        print(f"学习模拟的tool消息：{json.dumps(tool_message, ensure_ascii=False)}")
        # 本地检查数据保留与复制行为；不验证模型最终回答。
        assert preserved, "压缩丢失或改写了必要信息"
        assert result == original_result, "压缩修改了原工具结果"
        print()

    print("现有结果只有几个字段，压缩收益很小；字符数不是精确Token数。")
    print("只执行本地函数和消息组装，正式Tool Loop未接入压缩，没有请求模型。")


if __name__ == "__main__":
    main()
