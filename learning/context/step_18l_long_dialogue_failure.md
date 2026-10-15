# 18l · 有限退款偏好

[课程目录](../README.md) · [运行与排错](../../docs/setup.md)

## 学习目标

修复已知声明离开窗口后的丢失。完成后应能用本课输入解释参数来源、执行分支和返回值去向。

## 前置知识

先完成 [context/18k 上下文观测](step_18k_context_metrics.md)。
环境：基础环境 `.venv`。

## 文件职责

- [本课代码入口](step_18l_long_dialogue_failure.py)：学习代码，关键定义：`main`。
- [正式调用链参照](../../app/services/conversation_service.py)：比较学习脚本与应用入口的关系。
- [代码定位方法](../../docs/code-reading.md)：按函数名查找，不依赖旧行号。

## 具体输入与执行过程

```text
选10001
→ “暂不申请退款”
→ 闲聊挤出原文
→ facts恢复偏好
```

下面摘录当前入口的一段代码（省略部分文档字符串）；其余部分请打开完整文件。先找到输入变量，再标出传给下一个函数的参数，最后找到调用方接收返回值的位置。

```python
async def main() -> None:
    service = ConversationService()
    conversation_id = "refund-preference-demo"
    with patch.object(
        llm_service, "chat_with_messages", new=AsyncMock(return_value="模拟回答")
    ) as model_mock:
        await service.chat(conversation_id, "请查询订单10001")
        await service.chat(conversation_id, "暂不申请退款。")
        for turn in range(MAX_HISTORY_TURNS):
            await service.chat(conversation_id, f"闲聊问题{turn}")

        history = service.histories[conversation_id]
        print(f"保存历史条数：{len(history)}")
        print(f"原偏好仍在history：{any('暂不申请退款' in item['content'] for item in history)}")
        print(f"当前facts：{service.facts[conversation_id]}")

        question = "还是按我之前说的方式处理。"
        await service.chat(conversation_id, question)
        sent_messages = model_mock.await_args.args[0]
        print(f"下一轮输入含订单号：{'当前关注的订单编号是 10001' in sent_messages[0]['content']}")
        print(f"下一轮user副本含偏好：{'暂不申请退款' in sent_messages[-1]['content']}")
        print(f"偏好被放入system了吗：{'暂不申请退款' in sent_messages[0]['content']}")
        print(f"保存的本轮user仍是原问题：{history[-2]['content'] == question}")
        print("下一轮user副本正文：")
        print(sent_messages[-1]["content"])

    print("本步支持已有订单下两句独立声明；不是自动摘要，也没有执行退款或请求真实模型。")
```

## 运行与预期结果

**访问范围：本地运行（无外部模型请求）。**
在仓库根目录、已激活上述环境后运行。Windows 与 macOS/Linux 使用同一条 Python 命令：

```console
python -m learning.context.step_18l_long_dialogue_failure
```


**应观察到：** 支持两句独立声明；新订单/清会话时清理旧偏好，模型失败不更新。

结果以当前运行和代码为准，不要求真实模型逐字复现示例。只验证本地结构的课程不能证明模型的语义选择或生成质量。

## 常见错误

- 找不到 `app` 或 `learning`：回到仓库根目录，使用上面的模块运行命令，不直接双击脚本。
- 若出现外部请求或缺配置错误，先核对是否运行了本课命令以及是否填好占位配置；离线总检查会强制使用假配置。
- 没有；这是历史偏好数据，项目不据此执行真实退款动作。

## 自测与参考答案

1. 记录“现在申请退款”是否已经退款？
2. 用本课具体输入复述入口、处理步骤、结果；指出哪些动作发生在本地。

<details>
<summary>展开参考答案（先独立作答）</summary>

1. 没有；这是历史偏好数据，项目不据此执行真实退款动作。
2. 选10001 → “暂不申请退款” → 闲聊挤出原文 → facts恢复偏好。本课运行入口在本地完成；引用的正式服务可能有真实模型能力，不能据此判断本示例进行了网络请求。

</details>

## 完成标准

- 能解释“修复已知声明离开窗口后的丢失”，并指出代码中的依据。
- 能区分程序输出、模型输出与人工标注；遇到不一致先定位到具体步骤。
