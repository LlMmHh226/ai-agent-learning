# 20 · 结构化事实

[课程目录](../README.md) · [运行与排错](../../docs/setup.md)

## 学习目标

分开保存会话原文和重要字段。完成后应能用本课输入解释参数来源、执行分支和返回值去向。

## 前置知识

先完成 [steps_01_20/19 滑动窗口](step_19_memory_window.md)。
环境：基础环境 `.venv`。

## 文件职责

- [本课代码入口](../../app/services/conversation_service.py)：正式模块，关键定义：`extract_refund_preference`, `ConversationService`。
- [正式调用链参照](../../app/services/llm_service.py)：比较学习脚本与应用入口的关系。
- [代码定位方法](../../docs/code-reading.md)：按函数名查找，不依赖旧行号。

## 具体输入与执行过程

```text
10001出现
→ _remember_facts
→ 原文移出窗口
→ _build_model_messages读取编号
```

下面摘录当前入口的一段代码（省略部分文档字符串）；其余部分请打开完整文件。先找到输入变量，再标出传给下一个函数的参数，最后找到调用方接收返回值的位置。

```python
    def _remember_facts(
            self,
            conversation_id: str,
            message: str,
    ) -> None:
        order_ids = ORDER_ID_PATTERN.findall(message)
        if order_ids:
            conversation_facts = self.facts.setdefault(conversation_id, {})
            if conversation_facts.get("current_order_id") != order_ids[-1]:
                conversation_facts.pop("current_refund_preference", None)
            conversation_facts["current_order_id"] = order_ids[-1]

        refund_preference = extract_refund_preference(message)
        conversation_facts = self.facts.get(conversation_id, {})
        if refund_preference is not None and conversation_facts.get("current_order_id"):
            conversation_facts["current_refund_preference"] = refund_preference
```

## 运行与预期结果

**访问范围：本地运行（无外部模型请求）。**
在仓库根目录、已激活上述环境后运行。Windows 与 macOS/Linux 使用同一条 Python 命令：

```console
python -m unittest tests.test_structured_fact_retention -v
```


**应观察到：** 历史原文可消失，事实字典仍保存订单编号。

结果以当前运行和代码为准，不要求真实模型逐字复现示例。只验证本地结构的课程不能证明模型的语义选择或生成质量。

## 常见错误

- 找不到 `app` 或 `learning`：回到仓库根目录，使用上面的模块运行命令，不直接双击脚本。
- 若出现外部请求或缺配置错误，先核对是否运行了本课命令以及是否填好占位配置；离线总检查会强制使用假配置。
- Python 读取 facts 并组装进消息副本；模型不能直接读取本地字典。

## 自测与参考答案

1. 模型如何看到 facts？
2. 用本课具体输入复述入口、处理步骤、结果；指出哪些动作发生在本地。

<details>
<summary>展开参考答案（先独立作答）</summary>

1. Python 读取 facts 并组装进消息副本；模型不能直接读取本地字典。
2. 10001出现 → _remember_facts → 原文移出窗口 → _build_model_messages读取编号。本课运行入口在本地完成；引用的正式服务可能有真实模型能力，不能据此判断本示例进行了网络请求。

</details>

## 完成标准

- 能解释“分开保存会话原文和重要字段”，并指出代码中的依据。
- 能区分程序输出、模型输出与人工标注；遇到不一致先定位到具体步骤。
