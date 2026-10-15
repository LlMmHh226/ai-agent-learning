# 18a · 轮数与 Token

[课程目录](../README.md) · [运行与排错](../../docs/setup.md)

## 学习目标

区分数量上限和长度预算。完成后应能用本课输入解释参数来源、执行分支和返回值去向。

## 前置知识

先完成 [rag/17g RAG 代码复盘](../rag/step_17g_rag_code_recap.md)。
环境：基础环境 `.venv`。

## 文件职责

- [本课代码入口](step_18a_turn_window_vs_token_budget.py)：学习代码，关键定义：`main`。
- [正式调用链参照](../../app/services/conversation_service.py)：比较学习脚本与应用入口的关系。
- [代码定位方法](../../docs/code-reading.md)：按函数名查找，不依赖旧行号。

## 具体输入与执行过程

```text
同样十轮短文本/长文本
→ 统计字符数
→ 比较
```

下面摘录当前入口的一段代码（省略部分文档字符串）；其余部分请打开完整文件。先找到输入变量，再标出传给下一个函数的参数，最后找到调用方接收返回值的位置。

```python
def main() -> None:
    examples = [
        ("短消息", "物流没动静"),
        ("长消息", "物流" * 900),
    ]

    for label, message_text in examples:
        service = ConversationService()
        history = [{"role": "system", "content": DEFAULT_SYSTEM_PROMPT}]
        for _ in range(MAX_HISTORY_TURNS):
            history.append({"role": "user", "content": message_text})
            history.append({"role": "assistant", "content": message_text})

        service._trim_history(history)
        stored_message_count = len(history)
        stored_characters = sum(len(item["content"]) for item in history)

        # 正式 chat() 也是先追加本轮 user，再组装消息并调用模型；
        # 模型返回 assistant 消息之后才裁剪 history。
        history.append({"role": "user", "content": "订单到哪了？"})
        model_messages = service._build_model_messages("演示会话", history)
        request_characters = sum(
            len(item["content"]) for item in model_messages
        )

        print(f"{label}：每条示例消息 {len(message_text)} 个字符")
        print(
            f"裁剪后保存：{MAX_HISTORY_TURNS} 轮，"
```

## 运行与预期结果

**访问范围：本地运行（无外部模型请求）。**
在仓库根目录、已激活上述环境后运行。Windows 与 macOS/Linux 使用同一条 Python 命令：

```console
python -m learning.context.step_18a_turn_window_vs_token_budget
```


**应观察到：** 轮数一样但字符差异很大；字符不是精确 Token。

结果以当前运行和代码为准，不要求真实模型逐字复现示例。只验证本地结构的课程不能证明模型的语义选择或生成质量。

## 常见错误

- 找不到 `app` 或 `learning`：回到仓库根目录，使用上面的模块运行命令，不直接双击脚本。
- 若出现外部请求或缺配置错误，先核对是否运行了本课命令以及是否填好占位配置；离线总检查会强制使用假配置。
- 需按模型分词统计输入并在请求前分配与裁剪预算，本例尚未实现。

## 自测与参考答案

1. 如何实现真正 Token 预算？
2. 用本课具体输入复述入口、处理步骤、结果；指出哪些动作发生在本地。

<details>
<summary>展开参考答案（先独立作答）</summary>

1. 需按模型分词统计输入并在请求前分配与裁剪预算，本例尚未实现。
2. 同样十轮短文本/长文本 → 统计字符数 → 比较。本课运行入口在本地完成；引用的正式服务可能有真实模型能力，不能据此判断本示例进行了网络请求。

</details>

## 完成标准

- 能解释“区分数量上限和长度预算”，并指出代码中的依据。
- 能区分程序输出、模型输出与人工标注；遇到不一致先定位到具体步骤。
