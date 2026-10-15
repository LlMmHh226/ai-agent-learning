# 18c · 跨窗口事实

[课程目录](../README.md) · [运行与排错](../../docs/setup.md)

## 学习目标

让重要订单号独立于原文。完成后应能用本课输入解释参数来源、执行分支和返回值去向。

## 前置知识

先完成 [context/18b 裁剪切片](step_18b_trim_history_slice.md)。
环境：基础环境 `.venv`。

## 文件职责

- [本课代码入口](step_18c_structured_fact_retention.py)：学习代码，关键定义：`main`。
- [正式调用链参照](../../app/services/conversation_service.py)：比较学习脚本与应用入口的关系。
- [代码定位方法](../../docs/code-reading.md)：按函数名查找，不依赖旧行号。

## 具体输入与执行过程

```text
10001原话被裁剪
→ facts保留
→ system副本注入
```

下面摘录当前入口的一段代码（省略部分文档字符串）；其余部分请打开完整文件。先找到输入变量，再标出传给下一个函数的参数，最后找到调用方接收返回值的位置。

```python
def main() -> None:
    service = ConversationService()
    conversation_id = "order-memory-demo"
    history = service._get_history(conversation_id)

    message = "请查询订单10001"
    history.append({"role": "user", "content": message})
    # 模拟一次成功回复后的正式顺序，不调用聊天模型或订单工具。
    service._remember_facts(conversation_id, message)
    history.append({"role": "assistant", "content": "模拟回答：已查询订单10001"})
    service._trim_history(history)
    print(f"首轮记录事实：{service.facts[conversation_id]}")

    # 累计十一轮，使含订单号的第一轮离开十轮窗口。
    for turn in range(2, MAX_HISTORY_TURNS + 2):
        message = f"第{turn}轮闲聊"
        history.append({"role": "user", "content": message})
        service._remember_facts(conversation_id, message)
        history.append({"role": "assistant", "content": f"第{turn}轮模拟回答"})
        service._trim_history(history)

    print(f"裁剪后历史条数：{len(history)}")
    print(f"原订单正文仍在历史中：{any('10001' in item['content'] for item in history)}")
    print(f"裁剪后事实仍在：{service.facts[conversation_id]}")

    history.append({"role": "user", "content": "它的物流单号是什么？"})
    model_messages = service._build_model_messages(conversation_id, history)
    print(f"下一轮user：{model_messages[-1]['content']}")
```

## 运行与预期结果

**访问范围：本地运行（无外部模型请求）。**
在仓库根目录、已激活上述环境后运行。Windows 与 macOS/Linux 使用同一条 Python 命令：

```console
python -m learning.context.step_18c_structured_fact_retention
```


**应观察到：** 保存的原 system 不变，模型输入副本含编号。

结果以当前运行和代码为准，不要求真实模型逐字复现示例。只验证本地结构的课程不能证明模型的语义选择或生成质量。

## 常见错误

- 找不到 `app` 或 `learning`：回到仓库根目录，使用上面的模块运行命令，不直接双击脚本。
- 若出现外部请求或缺配置错误，先核对是否运行了本课命令以及是否填好占位配置；离线总检查会强制使用假配置。
- 不会；必须由 _build_model_messages 读取并写入本次输入。

## 自测与参考答案

1. facts 保存以后模型会自动看见吗？
2. 用本课具体输入复述入口、处理步骤、结果；指出哪些动作发生在本地。

<details>
<summary>展开参考答案（先独立作答）</summary>

1. 不会；必须由 _build_model_messages 读取并写入本次输入。
2. 10001原话被裁剪 → facts保留 → system副本注入。本课运行入口在本地完成；引用的正式服务可能有真实模型能力，不能据此判断本示例进行了网络请求。

</details>

## 完成标准

- 能解释“让重要订单号独立于原文”，并指出代码中的依据。
- 能区分程序输出、模型输出与人工标注；遇到不一致先定位到具体步骤。
