# 多 Agent 23C：用 LangGraph 状态交接

## 学习目标

运行两个独立的工具循环，并用外层图控制两个角色间的顺序与失败分支。

## 前置知识

完成 [23B](step_23b_order_agent.md) 和 [20I](../frameworks/step_20i_tool_loop_graph.md)，从仓库根目录使用框架环境。

## 文件职责

[协作图](step_23c_two_agents.py) 管理共享 `ServiceState`、两个角色节点和固定响应模型；[订单角色](step_23b_order_agent.py) 与 `lookup_policy` 各自只有一个工具。

## 具体输入与执行过程

`{"order_id":"10001"}` → 订单角色运行 `model → ToolNode → model` → 从 `ToolMessage` 提取字典 → 外层图确认结果属于 `10001` → 创建售后任务消息 → 售后子图执行 `lookup_policy` → 回收政策与需要补充的条件。`99999` 未找到时，条件边结束本轮，售后节点不执行。

## 运行与预期结果

```console
python -m learning.multi_agent.step_23c_two_agents
```

第一条结果中含订单事实、退货政策和追问；第二条没有 `policy_result`。可加 `--order-id 10001` 单独查看。LangGraph、ToolNode 与样例函数实际执行，模型返回的 Tool Call 和文本为固定样例；不调用真实模型或数据库。

## 常见错误

- 直接把订单角色的最终回答当成证据：要读取对应的工具结构化结果，并核对订单编号。
- 认为「图能跑」就是模型识别正确：实验只验证节点、参数、工具执行和分支。

## 自测与参考答案

外层图的状态和每个角色自己的 `messages` 有何区别？

<details>
<summary>参考答案</summary>

外层只保存跨角色要共享的任务与结果。局部 `messages` 用于一次角色执行，把其工具调用和 `ToolMessage` 关联起来；交接时提取所需事实即可。

</details>
