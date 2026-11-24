# MCP 22C：发现工具与限定开放范围

## 学习目标

从 MCP 服务端发现工具说明，并让同一份授权范围约束候选描述和实际分派。

## 前置知识

完成 [22B 连接生命周期](step_22b_order_lifecycle.md)，理解 [21C 的 Tool Message](step_21c_tool_adapter.md)。

## 文件职责

- [发现练习](step_22c_tool_discovery.py)：调用 `list_tools`，拒绝重复或缺少必需名称，从 `orders` 或 `all` 提取允许集合。
- [工具适配](step_21c_tool_adapter.py)：把输入 schema 转成模型工具声明，依据允许集合校验调用，回传相同 `tool_call_id`。
- [本机只读服务](managed_order_server.py)：提供样例订单、售后政策和本地资料匹配三个工具。

## 具体输入与执行过程

发现三个工具 → `orders` 仅开放订单、`all` 开放这三个指定工具 → 交给分派层一个固定的 `get_after_sales_policy` Tool Call → 前者拒绝，后者经 stdio 读取「退货」规则 → 打包为对应的 Tool Message。

## 运行与预期结果

```console
python -m learning.mcp.step_22c_tool_discovery
```

输出两个允许集合以及同一个调用被拒绝和被执行的结果。这里的候选是手写样例；只运行本机 MCP，不向外部模型发送工具说明或回复。

## 常见错误

- 认为 `list_tools` 的所有返回项都自动授权：发现只提供元数据，Host 决定业务范围。
- 只在发给模型前过滤：分派时也要校验实际工具名和参数，不能信任模型生成。

## 自测与参考答案

服务端明天新增 `create_ticket`，`all` 会自动允许这个工具吗？

<details>
<summary>参考答案</summary>

不会。`all` 是本例显式定义的三个只读名称。新增业务工具要先设计参数、权限和风险边界，再审阅允许范围。

</details>
