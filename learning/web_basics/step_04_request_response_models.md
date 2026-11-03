# 04 · 请求与响应模型

[本组目录](README.md) · [课程总目录](../README.md)

## 学习目标

区分输入对象和输出过滤。对照具体输入解释每个参数从哪里来、返回值交给谁以及失败发生在哪一层。

## 前置知识

先阅读 [路径参数](step_03_path_parameter.md)。 使用环境：.venv。所有Python命令在仓库根目录运行；安装见 [运行说明](../../docs/setup.md)。

## 文件职责

- [核心文件](step_01_hello.py)：按本课数据流查找对应定义。
- [同一Web学习应用](step_01_hello.py)：本组课逐步阅读同一应用，不替代正式客服接口。

## 具体输入与执行过程

```text
POST /greetings，name=小明
→ GreetingRequest
→ dict
→ GreetingResponse
```

先找到入口，再标出关键函数的参数与返回点。学习脚本是分步实现；`app`中的整合版可能同时支持演示与数据库后端，观察时记下当前配置，避免混用结果。

## 运行与预期结果

**访问范围：本地演示，不请求外部模型。**

```console
python -m uvicorn learning.web_basics.step_01_hello:app --reload --port 8001
```

应观察到：内部演示字段被response_model过滤。



在 `/docs` 展开 `POST /greetings`，提交 `{"name":"小明"}`，观察输出不包含internal_note。

## 常见错误

- 导入失败：确认位于仓库根目录，并使用本课对应的独立环境。
- 运行结果与预期不同：先检查后端配置、前置服务及当前代码版本，再判断是否属于模型行为差异。
- 不是；通过校验后是GreetingRequest实例，用body.name取字段。

## 自测与参考答案

1. body是原始JSON字符串吗？
2. 对照上面的具体输入，指出本地处理、协议通信、数据库访问与外部模型请求分别发生在哪里。

<details>
<summary>展开参考答案</summary>

1. 不是；通过校验后是GreetingRequest实例，用body.name取字段。
2. POST /greetings，name=小明 → GreetingRequest → dict → GreetingResponse。本课的访问范围已在运行段说明；预览、本地模拟、真实协议和真实模型是不同层次的证据，不能互相替代。

</details>

## 完成标准

能独立说明“区分输入对象和输出过滤”，指出核心调用、至少一个失败分支，并解释本课实验能证明的范围。
