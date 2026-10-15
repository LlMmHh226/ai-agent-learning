# 课程：step_15f_hallucination.md；访问范围：本地运行（无外部模型请求）。
cases = [
    {
        "name": "正确回答",
        "context": "退款通常在1至3个工作日内原路退回。",
        "answer": "退款通常会在1至3个工作日内原路退回。",
        "result": "正确：回答受到资料支持",
    },
    {
        "name": "生成幻觉",
        "context": "退款通常在1至3个工作日内原路退回。",
        "answer": "退款当天到账，并额外补偿10元优惠券。",
        "result": "生成错误：模型添加了资料中不存在的事实",
    },
    {
        "name": "检索失败后猜测",
        "context": "机械键盘支持五脚轴热插拔。",
        "answer": "退款会在当天到账。",
        "result": "检索错误：上下文无关；模型又进行了猜测",
    },
    {
        "name": "知识库错误",
        "context": "退款需要90个工作日。",
        "answer": "退款需要90个工作日。",
        "result": "来源错误：模型忠实引用，但知识库事实错误",
    },
    {
        "name": "引用不一致",
        "context": "退款通常在1至3个工作日内原路退回。",
        "answer": "退款通常在1至3个工作日到账，来源：products.md。",
        "result": "引用错误：答案事实正确，但来源文件不支持该事实",
    },
]


for case in cases:
    print(f"\n场景：{case['name']}")
    print(f"上下文：{case['context']}")
    print(f"回答：{case['answer']}")
    print(f"判断：{case['result']}")
