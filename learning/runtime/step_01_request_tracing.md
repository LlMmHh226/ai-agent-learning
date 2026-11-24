# 运行保障 01：请求 ID 与分段日志

## 学习目标

通过响应头定位本次请求经过的阶段，区分「一次 HTTP 请求」和「一个会话」。

## 前置知识

了解 [FastAPI 生命周期与应用状态](../web_basics/README.md) 中的请求处理；会看 HTTP 状态码和响应头。

## 文件职责

[教学应用](step_01_request_tracing.py) 生成请求 ID、设置 `ContextVar`、记录阶段和耗时。[样例订单函数](../../app/repositories/demo_orders.py) 提供本地结果。

## 具体输入与执行过程

提交 `{"order_id":"10001"}` 到 `/demo/orders/query` → 中间件生成 ID → `order.lookup` 读取样例 → `order.result` → 响应返回 `X-Request-ID`。`finally` 恢复当前上下文，其他请求创建新 ID。

## 运行与预期结果

```console
python -m learning.runtime.step_01_request_tracing
```

`TestClient` 在进程内请求，无外部模型、数据库或网络依赖。订单 `10001` 和 `99999` 都是 HTTP 200，业务字段 `found` 不同，请求 ID 也不同。用任一订单响应的 ID 找到 `request.start`、`order.lookup`、`order.result` 和 `request.end`。

## 常见错误

- 用 `conversation_id` 查某次报错：同一会话包含多次 HTTP 请求，应用故障先按本次 `X-Request-ID` 找日志。
- 整包打印请求：通常只记阶段、时间、状态和关联 ID；不要把密钥或完整对话放进日志。

## 自测与参考答案

为什么本例在中间件生成 ID，并用 `finally` 恢复上下文？

<details>
<summary>参考答案</summary>

凡经中间件的请求都用同一个日志入口，路由不必重复生成。用 `ContextVar` 把标识限定到本次执行上下文，`finally` 保证处理失败时也恢复此前的值。

</details>
