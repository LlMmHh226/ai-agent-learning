# 请求运行保障

使用 [基础环境](../../docs/setup.md)，在独立教学应用中观察日志、请求预算和重试。所有默认命令都无需模型密钥、Docker 或真实订单。

| 课次 | 追踪的问题 | 入口 |
| --- | --- | --- |
| 01 | 怎样把一个 HTTP 响应和多条阶段日志关联起来？ | [请求 ID 与分段日志](step_01_request_tracing.md) |
| 02 | 两段异步处理怎样共用一个预算？ | [请求级超时](step_02_request_timeout.md) |
| 03 | 什么错误可以重试一次，什么错误应直接返回？ | [模型调用的有限重试](step_03_model_retry.md) |
| 04 | 如何区分「进程能响应」和「业务能跑」？ | [启动与演示模式](step_04_start_and_demo.md) |

读完尝试说清 `request_id`、`conversation_id` 和 `revision` 分别标识什么，再到 [MCP 生命周期](../mcp/step_22b_order_lifecycle.md) 对照启动和关闭的边界。
