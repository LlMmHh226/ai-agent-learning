AFTER_SALES_POLICIES: dict[str, str] = {
    "退货": "商品签收后7天内，商品完好且不影响二次销售时可以申请退货。",
    "换货": "商品签收后15天内，如存在质量问题，可以提交凭证申请换货。",
    "退款": "退货验收通过后，退款通常会在1至3个工作日内原路退回。",
}


GET_AFTER_SALES_POLICY_TOOL = {
    "type": "function",
    "function": {
        "name": "get_after_sales_policy",
        "description": "查询商城的退货、换货或退款政策",
        "parameters": {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "enum": ["退货", "换货", "退款"],
                    "description": "用户想了解的售后政策主题",
                }
            },
            "required": ["topic"],
            "additionalProperties": False,
        },
    },
}


def get_after_sales_policy(topic: str) -> dict[str, object]:
    policy = AFTER_SALES_POLICIES.get(topic)

    if policy is None:
        return {
            "found": False,
            "message": "没有找到该售后政策",
        }

    return {
        "found": True,
        "topic": topic,
        "policy": policy,
    }
