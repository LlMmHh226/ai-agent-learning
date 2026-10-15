# 18k · 上下文观测

[课程目录](../README.md) · [运行与排错](../../docs/setup.md)

## 学习目标

记录长度和裁剪事件。完成后应能用本课输入解释参数来源、执行分支和返回值去向。

## 前置知识

先完成 [context/18j 上下文复盘](step_18j_context_stage_recap.md)。
环境：基础环境 `.venv`。

## 文件职责

- [本课代码入口](step_18k_context_metrics.py)：学习代码，关键定义：`measure_request`, `main`。
- [正式调用链参照](../../app/services/conversation_service.py)：比较学习脚本与应用入口的关系。
- [代码定位方法](../../docs/code-reading.md)：按函数名查找，不依赖旧行号。

## 具体输入与执行过程

```text
请求副本
→ 计数/字符数
→ 模拟响应
→ 保存后裁剪
```

下面摘录当前入口的一段代码（省略部分文档字符串）；其余部分请打开完整文件。先找到输入变量，再标出传给下一个函数的参数，最后找到调用方接收返回值的位置。

```python
def measure_request(
    messages: list[dict[str, Any]],
    tools: list[dict[str, Any]],
) -> dict[str, int]:
    content_chars = sum(len(item.get("content") or "") for item in messages)
    messages_json_chars = len(json.dumps(messages, ensure_ascii=False, separators=(",", ":")))
    tools_json_chars = len(json.dumps(tools, ensure_ascii=False, separators=(",", ":")))
    return {
        "message_count": len(messages),
        "content_chars": content_chars,
        "messages_json_chars": messages_json_chars,
        "tools_json_chars": tools_json_chars,
        "context_json_chars": messages_json_chars + tools_json_chars,
    }
```

## 运行与预期结果

**访问范围：本地运行（无外部模型请求）。**
在仓库根目录、已激活上述环境后运行。Windows 与 macOS/Linux 使用同一条 Python 命令：

```console
python -m learning.context.step_18k_context_metrics
```


**应观察到：** 指标解释消息与裁剪，不冒充真实计费统计。

结果以当前运行和代码为准，不要求真实模型逐字复现示例。只验证本地结构的课程不能证明模型的语义选择或生成质量。

## 常见错误

- 找不到 `app` 或 `learning`：回到仓库根目录，使用上面的模块运行命令，不直接双击脚本。
- 若出现外部请求或缺配置错误，先核对是否运行了本课命令以及是否填好占位配置；离线总检查会强制使用假配置。
- 不能；Tokenizer、模型和计费规则不同，需供应商 usage 或匹配的分词器。

## 自测与参考答案

1. 字符数能直接当 Token 费用吗？
2. 用本课具体输入复述入口、处理步骤、结果；指出哪些动作发生在本地。

<details>
<summary>展开参考答案（先独立作答）</summary>

1. 不能；Tokenizer、模型和计费规则不同，需供应商 usage 或匹配的分词器。
2. 请求副本 → 计数/字符数 → 模拟响应 → 保存后裁剪。本课运行入口在本地完成；引用的正式服务可能有真实模型能力，不能据此判断本示例进行了网络请求。

</details>

## 完成标准

- 能解释“记录长度和裁剪事件”，并指出代码中的依据。
- 能区分程序输出、模型输出与人工标注；遇到不一致先定位到具体步骤。
