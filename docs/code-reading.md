# 如何顺着代码学习

[返回课程目录](../learning/README.md)

## 从一个输入开始

不要同时打开所有文件。以“请查询订单10001”为例，先找到 HTTP 路由，再跟到调用方传参、服务返回和响应包装。使用编辑器全局搜索 `conversation_chat`、`chat_with_messages`、`get_order_status`，比记住某个版本的行号更可靠。

阅读每次调用时回答四件事：传入值从哪里来；参数是什么类型；函数做了什么；返回值由谁接收。遇到框架或 patch 动态调用时，先看 [完整调用链](architecture.md)，再跳到具体文件。

## Python 术语与 Java 经验

| 写法 | 称呼 | 例子 |
| --- | --- | --- |
| 一个 `.py` 文件 | 模块 | `conversation_service.py` |
| `class ConversationService` | 类 | 定义状态与方法 |
| `ConversationService()` | 对象/实例 | 构造一份服务对象 |
| 模块顶层 `def` | 函数 | `get_order_status` |
| 类内 `def` | 方法 | `ConversationService.chat` |
| `await coroutine(...)` | 等待异步操作结果 | 等模型请求完成，再处理响应 |

## 三个容易混淆的地方

```python
history = saved
messages = [dict(item) for item in history]
history.append({"role": "user", "content": "新问题"})
```

history 和 saved 引用同一列表，追加会影响二者看到的内容。messages 是另一个列表，里面的消息字典也被浅复制；它不是通用的深复制。列表追加只是本地操作，并未发出请求。

```python
result = service._trim_history(history)
```

裁剪原地修改 history，返回值为 None。不要写 `history = service._trim_history(history)`，否则局部 history 会被赋为 None。

```python
facts = {"c1": {"current_order_id": "10001"}}
order_id = facts.get("c1", {}).get("current_order_id")
```

c1 是会话键，current_order_id 是字段名，10001 是值。模型不会自行读取 facts，Python 必须把需要的信息放入 messages。

## 用职责概括代码

按照“动作＋处理对象＋用途”表达：`working_messages.append(tool_message)` 是“把工具结果加入本次消息，让下一次模型调用能读取结果”。不要把变量用途“工作列表”当作整段代码的动作。

原生工具 `arguments` 是 JSON 字符串，解析后才能取字段；LangChain 的 `tool_calls[i]['args']` 通常已经是字典。函数返回的订单字典、JSON 字符串、SDK 响应对象和最终 answer 字符串必须分清。

## 独立练习

在 [正式会话服务](../app/services/conversation_service.py)中标出“读 facts”“请求模型”“写 facts”“保存 assistant”“裁剪”五个位置，然后不用看代码复述顺序。

<details>
<summary>参考顺序</summary>

取历史并追加本次 user → `_build_model_messages` 读取旧 facts 并组成输入副本 → `chat_with_messages` 返回最终正文 → `_remember_facts` 保存本次事实 → history 追加最终 assistant → `_trim_history` → 返回 answer。异常分支在保存事实前回滚本次 user。

</details>
