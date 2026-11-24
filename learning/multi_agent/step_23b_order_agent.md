# 多 Agent 23B：订单角色与工具范围

## 学习目标

给一个专业 Agent 组装独立消息，并用相同的工具名单约束模型和执行节点。

## 前置知识

完成 [23A 角色分工](step_23a_roles_and_handoff.md)，知道 [19D 的工具包装](../frameworks/step_19d_langchain_tool_object.md) 如何声明业务参数。

## 文件职责

[订单角色](step_23b_order_agent.py) 的 `build_order_input()` 生成当前子任务的消息；`build_order_agent()` 把 `lookup_order` 交给 [20I 的工具循环](../frameworks/step_20i_tool_loop_graph.py)。

## 具体输入与执行过程

`请核实订单10001的物流。` → 去除首尾空格并验证非空 → 生成 `SystemMessage` 与 `HumanMessage` → 在图构建时绑定唯一工具 `lookup_order`。系统指令说明角色边界，执行节点的实际名单负责约束权限。

## 运行与预期结果

```console
python -m learning.multi_agent.step_23b_order_agent
```

在框架环境输出两条消息和工具名。传入 `--task "   "` 会报告任务为空。预览不调用任何模型或工具；真正运行局部工具循环见下一课。

## 常见错误

- 把空格消息当成合法任务：需要先 `strip()` 再判空。
- Prompt 写「只查订单」就认为售后工具不可用：检查运行时工具是不是也只绑定 `lookup_order`。

## 自测与参考答案

为什么不直接把原始用户的混合诉求当作订单角色的子任务？

<details>
<summary>参考答案</summary>

路由应把需要这个角色处理的内容说清楚，例如核实 `10001` 的物流。把所有诉求透传会增加角色越界回答的机会，还让其他子任务的进度不清楚。

</details>
