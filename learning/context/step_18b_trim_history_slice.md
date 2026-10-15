# 18b · 裁剪切片

[课程目录](../README.md) · [运行与排错](../../docs/setup.md)

## 学习目标

推导负索引和原地删除。完成后应能用本课输入解释参数来源、执行分支和返回值去向。

## 前置知识

先完成 [context/18a 轮数与 Token](step_18a_turn_window_vs_token_budget.md)。
环境：基础环境 `.venv`。

## 文件职责

- [本课代码入口](step_18b_trim_history_slice.py)：学习代码，关键定义：`main`。
- [正式调用链参照](../../app/services/conversation_service.py)：比较学习脚本与应用入口的关系。
- [代码定位方法](../../docs/code-reading.md)：按函数名查找，不依赖旧行号。

## 具体输入与执行过程

```text
history23条
→ del history[1:-20]
→ 21条
```

下面摘录当前入口的一段代码（省略部分文档字符串）；其余部分请打开完整文件。先找到输入变量，再标出传给下一个函数的参数，最后找到调用方接收返回值的位置。

```python
def main() -> None:
    service = ConversationService()
    conversation_id = "trim-demo"
    history = service._get_history(conversation_id)

    for turn in range(1, MAX_HISTORY_TURNS + 1):
        history.append({"role": "user", "content": f"U{turn}"})
        history.append({"role": "assistant", "content": f"A{turn}"})

    # 恰好十轮，正式方法不会删除消息。
    service._trim_history(history)
    print(f"已有十轮：{len(history)} 条，首轮={history[1]['content']}、{history[2]['content']}")

    # 按正式 chat() 的顺序模拟本轮过程，省略真实模型请求。
    history.append({"role": "user", "content": "订单到哪了？"})
    model_messages = service._build_model_messages(conversation_id, history)
    print(f"追加本轮 user、送模型前：history={len(history)} 条，model_messages={len(model_messages)} 条")

    answer = "模拟回答：订单正在运输。"
    history.append({"role": "assistant", "content": answer})
    print(f"追加本轮 assistant 后：history={len(history)} 条")

    max_regular_messages = MAX_HISTORY_TURNS * 2
    stop_index = len(history) - max_regular_messages
    removed_contents = [
        item["content"] for item in history[1:-max_regular_messages]
    ]
    print(f"切片 history[1:-{max_regular_messages}] 等价于 history[1:{stop_index}]")
```

## 运行与预期结果

**访问范围：本地运行（无外部模型请求）。**
在仓库根目录、已激活上述环境后运行。Windows 与 macOS/Linux 使用同一条 Python 命令：

```console
python -m learning.context.step_18b_trim_history_slice
```


**应观察到：** system保留、最早一轮被删除；返回值是 None。

结果以当前运行和代码为准，不要求真实模型逐字复现示例。只验证本地结构的课程不能证明模型的语义选择或生成质量。

## 常见错误

- 找不到 `app` 或 `learning`：回到仓库根目录，使用上面的模块运行命令，不直接双击脚本。
- 若出现外部请求或缺配置错误，先核对是否运行了本课命令以及是否填好占位配置；离线总检查会强制使用假配置。
- 方法原地改列表后返回 None，赋值会把局部 history 变成 None。

## 自测与参考答案

1. 把 history=_trim_history(history) 会怎样？
2. 用本课具体输入复述入口、处理步骤、结果；指出哪些动作发生在本地。

<details>
<summary>展开参考答案（先独立作答）</summary>

1. 方法原地改列表后返回 None，赋值会把局部 history 变成 None。
2. history23条 → del history[1:-20] → 21条。本课运行入口在本地完成；引用的正式服务可能有真实模型能力，不能据此判断本示例进行了网络请求。

</details>

## 完成标准

- 能解释“推导负索引和原地删除”，并指出代码中的依据。
- 能区分程序输出、模型输出与人工标注；遇到不一致先定位到具体步骤。
