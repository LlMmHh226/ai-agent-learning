# MCP 22B：订单网关的启动、复用与关闭

## 学习目标

理解进程级 MCP 连接何时建立、如何复用，以及为什么 native 模式不启动子进程。

## 前置知识

完成 [21H 生命周期](step_21h_fastapi_lifespan.md) 和 [22A 参数检查](step_22a_formal_boundary.md)，安装 [MCP 环境](../../docs/setup.md#mcp环境)。

## 文件职责

[订单网关应用](step_22b_order_lifecycle.py) 创建两种教学模式，管理 `app.state.order_client`，并映射协议错误。[stdio 服务端](managed_order_server.py) 注册并执行只读样例工具。

## 具体输入与执行过程

`create_app("mcp")` → lifespan 启动 stdio 子进程并确认有 `get_order_status` → 路由收到 `{"order_id":"10001"}` → 复用共享会话查询 → 返回工具字典。紧接着查询 `99999` 仍使用同一会话；退出后 SDK 管理子进程清理。`native` 直接使用本地函数。

## 运行与预期结果

```console
python -m learning.mcp.step_22b_order_lifecycle
```

`TestClient` 提供进程内 HTTP，MCP 走真实本机 stdio。预期 `10001` 的两条路径结果相同，`99999` 是 HTTP 200 且 `found:false`。无外部模型或数据库，不改正式入口。

## 常见错误

- 没用 `with TestClient(app)`：测试就未进入示例的 lifespan，连接没有准备好。
- 在服务端向 stdout 打普通日志：stdio 线路上应保留协议消息。
- 协议调用失败当成订单不存在：看 HTTP 502 与正常的 `found:false` 分支。

## 自测与参考答案

多个 Uvicorn worker 时，`app.state` 中是不是整个部署共用同一连接？

<details>
<summary>参考答案</summary>

不是。每个应用进程单独运行 lifespan；该进程内的请求复用自己的会话。进程之间不共享这个 Python 对象。

</details>
