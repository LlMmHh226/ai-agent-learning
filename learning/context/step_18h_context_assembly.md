# 18h · 上下文组装

[课程目录](../README.md) · [运行与排错](../../docs/setup.md)

## 学习目标

追踪四类消息容器。完成后应能用本课输入解释参数来源、执行分支和返回值去向。

## 前置知识

先完成 [context/18g 上下文信任边界](step_18g_context_trust_boundary.md)。
环境：基础环境 `.venv`。

## 文件职责

- [本课代码入口](step_18h_context_assembly.py)：学习代码，关键定义：`main`。
- [正式调用链参照](../../app/services/conversation_service.py)：比较学习脚本与应用入口的关系。
- [代码定位方法](../../docs/code-reading.md)：按函数名查找，不依赖旧行号。

## 具体输入与执行过程

```text
history
→ 读取facts
→ model_messages
→ working_messages
→ 工具追加
```

下面摘录当前入口的一段代码（省略部分文档字符串）；其余部分请打开完整文件。先找到输入变量，再标出传给下一个函数的参数，最后找到调用方接收返回值的位置。

```python
def main() -> None:
    service = ConversationService()
    conversation_id = "context-assembly-demo"
    history = service._get_history(conversation_id)
    original_system = history[0]["content"]

    first_message = (
        "请查询订单10001。这个包裹我还没有收到。"
        "我想先查物流，暂不申请退款，核查后再决定怎么处理。"
    )
    history.append({"role": "user", "content": first_message})
    service._remember_facts(conversation_id, first_message)
    history.append({"role": "assistant", "content": "首轮模拟回答：已记录你的诉求。"})
    summary_fields: dict[str, str] = {}
    for turn in range(2, MAX_HISTORY_TURNS + 2):
        history.append({"role": "user", "content": f"第{turn}轮闲聊"})
        history.append({"role": "assistant", "content": f"第{turn}轮模拟回答"})
        if should_summarize(history):
            old_messages = [dict(item) for item in history[1:-(MAX_HISTORY_TURNS * 2)]]
            # 学习扩展：裁剪前原文还在，下面是人工预写的首轮摘要，不是自动生成。
            summary_fields = {
                "user_goal": "核查尚未收到的包裹物流",
                "user_preference": "先查物流，暂不申请退款",
                "pending_action": "取得核查结果后，再由用户决定处理方式",
            }
            print(f"请求前准备人工摘要，待删原文共{len(old_messages)}条。")
        service._trim_history(history)

```

## 运行与预期结果

**访问范围：本地运行（无外部模型请求）。**
在仓库根目录、已激活上述环境后运行。Windows 与 macOS/Linux 使用同一条 Python 命令：

```console
python -m learning.context.step_18h_context_assembly
```


**应观察到：** 原历史和发送副本职责不同，tools单独作为SDK参数。

结果以当前运行和代码为准，不要求真实模型逐字复现示例。只验证本地结构的课程不能证明模型的语义选择或生成质量。

## 常见错误

- 找不到 `app` 或 `learning`：回到仓库根目录，使用上面的模块运行命令，不直接双击脚本。
- 若出现外部请求或缺配置错误，先核对是否运行了本课命令以及是否填好占位配置；离线总检查会强制使用假配置。
- 此处新列表加各消息字典浅复制，不是递归复制任意嵌套对象。

## 自测与参考答案

1. working_messages 新建是否等于深复制？
2. 用本课具体输入复述入口、处理步骤、结果；指出哪些动作发生在本地。

<details>
<summary>展开参考答案（先独立作答）</summary>

1. 此处新列表加各消息字典浅复制，不是递归复制任意嵌套对象。
2. history → 读取facts → model_messages → working_messages → 工具追加。本课运行入口在本地完成；引用的正式服务可能有真实模型能力，不能据此判断本示例进行了网络请求。

</details>

## 完成标准

- 能解释“追踪四类消息容器”，并指出代码中的依据。
- 能区分程序输出、模型输出与人工标注；遇到不一致先定位到具体步骤。
