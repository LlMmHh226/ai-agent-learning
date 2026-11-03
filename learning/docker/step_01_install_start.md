# 01 · 准备Docker

[本组目录](README.md) · [课程总目录](../README.md)

## 学习目标

理解Client、Engine与容器环境。对照具体输入解释每个参数从哪里来、返回值交给谁以及失败发生在哪一层。

## 前置知识

按 [Docker官方安装入口](https://docs.docker.com/get-started/get-docker/)选择系统。Windows使用Docker Desktop并启动引擎，必要时按官方提示启用WSL2；安装结束后重新打开终端。Linux也可以使用已安装的Docker Engine与Compose插件。

先按首页安装基础环境，并完成原生工具循环与相关阶段复盘。 使用环境：Docker Engine。所有Python命令在仓库根目录运行；安装见 [运行说明](../../docs/setup.md)。

## 文件职责

- [核心文件](../postgresql/compose.yaml)：按本课数据流查找对应定义。

## 具体输入与执行过程

```text
安装并启动Docker Desktop
→ docker version
→ Client/Server
```

先找到入口，再标出关键函数的参数与返回点。学习脚本是分步实现；`app`中的整合版可能同时支持演示与数据库后端，观察时记下当前配置，避免混用结果。

## 运行与预期结果

**访问范围：首次下载镜像需要联网；不请求模型。**

```console
docker version
```

应观察到：两端信息都有才说明Engine可用。





## 常见错误

- 导入失败：确认位于仓库根目录，并使用本课对应的独立环境。
- 运行结果与预期不同：先检查后端配置、前置服务及当前代码版本，再判断是否属于模型行为差异。
- 不能；Client是命令工具，Server部分来自实际Docker Engine。

## 自测与参考答案

1. 只看到Client版本能说明引擎已启动吗？
2. 对照上面的具体输入，指出本地处理、协议通信、数据库访问与外部模型请求分别发生在哪里。

<details>
<summary>展开参考答案</summary>

1. 不能；Client是命令工具，Server部分来自实际Docker Engine。
2. 安装并启动Docker Desktop → docker version → Client/Server。本课的访问范围已在运行段说明；预览、本地模拟、真实协议和真实模型是不同层次的证据，不能互相替代。

</details>

## 完成标准

能独立说明“理解Client、Engine与容器环境”，指出核心调用、至少一个失败分支，并解释本课实验能证明的范围。
