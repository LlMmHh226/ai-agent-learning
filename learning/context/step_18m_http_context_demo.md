# 18m · HTTP 上下文演示

[课程目录](../README.md) · [运行与排错](../../docs/setup.md)

## 学习目标

从请求验证到响应回溯。完成后应能用本课输入解释参数来源、执行分支和返回值去向。

## 前置知识

先完成 [context/18l 有限退款偏好](step_18l_long_dialogue_failure.md)。
环境：基础环境 `.venv`。

## 文件职责

- [本课代码入口](step_18m_http_context_demo.py)：学习代码，关键定义：`main`。
- [正式调用链参照](../../app/services/conversation_service.py)：比较学习脚本与应用入口的关系。
- [代码定位方法](../../docs/code-reading.md)：按函数名查找，不依赖旧行号。

## 具体输入与执行过程

```text
进程内HTTP
→ Schema/API
→ 会话
→ 原生循环
→ 模拟SDK
→ 响应
```

下面摘录当前入口的一段代码（省略部分文档字符串）；其余部分请打开完整文件。先找到输入变量，再标出传给下一个函数的参数，最后找到调用方接收返回值的位置。

```python
def main() -> None:
    conversation_id = "http-context-demo"
    state = {"phase": "", "request_no": 0}
    snapshots = []
    conversation_service.clear(conversation_id)

    async def simulate_create(**request_parameters: Any) -> SimpleNamespace:
        """在SDK入口复制实际参数，再给正式Tool Loop返回本地模拟对象。

        参数：request_parameters收集正式create传入的关键字参数；仅读取messages。
        返回：包含choices[0].message的模拟响应。订单查询与最后追问的首次请求
            预设Tool Call，后续读取正式工具结果拼接模拟答复，不做真实模型推理。
        """
        state["request_no"] += 1
        messages = request_parameters["messages"]
        snapshots.append(
            {
                "phase": state["phase"],
                "request_no": state["request_no"],
                "messages": deepcopy(messages),
            }
        )
        if state["phase"] in ("order", "follow_up") and state["request_no"] == 1:
            message = ChatCompletionMessage(
                role="assistant",
                content=None,
                tool_calls=[
                    {
```

## 运行与预期结果

**访问范围：本地运行（无外部模型请求）。**
在仓库根目录、已激活上述环境后运行。Windows 与 macOS/Linux 使用同一条 Python 命令：

```console
python -m learning.context.step_18m_http_context_demo
```


**应观察到：** 业务层实际运行，SDK响应模拟；多轮后历史仍受窗口限制。

结果以当前运行和代码为准，不要求真实模型逐字复现示例。只验证本地结构的课程不能证明模型的语义选择或生成质量。

## 常见错误

- 找不到 `app` 或 `learning`：回到仓库根目录，使用上面的模块运行命令，不直接双击脚本。
- 若出现外部请求或缺配置错误，先核对是否运行了本课命令以及是否填好占位配置；离线总检查会强制使用假配置。
- HTTP路由、会话和本地工具真实执行，只有模型生成响应由模拟提供。

## 自测与参考答案

1. 这个演示真实与模拟的边界在哪？
2. 用本课具体输入复述入口、处理步骤、结果；指出哪些动作发生在本地。

<details>
<summary>展开参考答案（先独立作答）</summary>

1. HTTP路由、会话和本地工具真实执行，只有模型生成响应由模拟提供。
2. 进程内HTTP → Schema/API → 会话 → 原生循环 → 模拟SDK → 响应。本课运行入口在本地完成；引用的正式服务可能有真实模型能力，不能据此判断本示例进行了网络请求。

</details>

## 完成标准

- 能解释“从请求验证到响应回溯”，并指出代码中的依据。
- 能区分程序输出、模型输出与人工标注；遇到不一致先定位到具体步骤。
