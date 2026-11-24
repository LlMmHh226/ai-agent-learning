# 运行保障 04：启动检查与演示数据

## 学习目标

分别验证进程可响应、样例业务能跑、真实依赖可达，避免混用三种检查的结论。

## 前置知识

准备 [基础环境](../../docs/setup.md)，读过 [运行保障 01](step_01_request_tracing.md)。

## 文件职责

[教学应用](step_01_request_tracing.py) 提供 `/health` 与 `/demo/orders/query`；它的 CLI 用 `TestClient` 发起验证。正式 `main:app` 和模型配置不随本课改变。

## 具体输入与执行过程

`GET /health` → 应用返回 `{"status":"ok"}`。随后提交 `{"order_id":"10001"}` → 路由校验 → 虚构订单数据 → 带请求 ID 的 200 响应。健康端点没有访问模型或检查数据库。

## 运行与预期结果

首先用进程内检查，不需密钥、数据库或网络：

```console
python -m learning.runtime.step_01_request_tracing
```

也可以启动独立本机服务并用浏览器访问 `127.0.0.1:8001/health` 或 `127.0.0.1:8001/docs`：

```console
python -m uvicorn learning.runtime.step_01_request_tracing:app --host 127.0.0.1 --port 8001
```

在交互文档试订单查询，完成后按 `Ctrl+C`。这是本机回环访问，无外部模型。需要验证真实聊天时，另按 [首页快速开始](../../README.md) 配置并运行正式入口。

## 常见错误

- 打开了错的端口：教程演示用 `8001`，仓库的正式服务示例通常用 `8000`。
- 见到 `ok` 就说模型或数据库可用：此处健康检查只证明教学应用能响应。

## 自测与参考答案

教同学排查时，本课 200 响应可以排除什么？还有什么需要独立测试？

<details>
<summary>参考答案</summary>

说明演示进程可处理请求、样例路径能读到本地数据；还要分别验证正式应用配置、外部模型权限、网络、工具能力和按需开启的数据库。

</details>
