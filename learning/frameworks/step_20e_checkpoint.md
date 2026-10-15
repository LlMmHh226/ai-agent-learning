# 20e · Checkpoint

[课程目录](../README.md) · [运行与排错](../../docs/setup.md)

## 学习目标

按 thread_id 恢复状态。完成后应能用本课输入解释参数来源、执行分支和返回值去向。

## 前置知识

先完成 [frameworks/20d 条件边](step_20d_conditional_route.md)。
环境：独立框架环境 `.venv-langchain`。

## 文件职责

- [本课代码入口](step_20e_checkpoint.py)：学习代码，关键定义：`SessionState`, `reply_to_request`, `build_graph`, `main`。
- [正式调用链参照](step_20i_tool_loop_graph.py)：比较学习脚本与应用入口的关系。
- [代码定位方法](../../docs/code-reading.md)：按函数名查找，不依赖旧行号。

## 具体输入与执行过程

```text
同一内存保存器+c1
→ 保存10001
→ 再次输入request
→ 恢复编号
```

下面摘录当前入口的一段代码（省略部分文档字符串）；其余部分请打开完整文件。先找到输入变量，再标出传给下一个函数的参数，最后找到调用方接收返回值的位置。

```python
def reply_to_request(state: SessionState) -> dict[str, str]:
    result = state["order_result"]
    if not result.get("found"):
        answer = "没有找到该订单。"
    elif state["request"] == "status":
        answer = f"订单{state['order_id']}状态：{result['status']}。"
    elif state["request"] == "tracking":
        tracking_number = result.get("tracking_number") or "暂无物流单号"
        answer = f"订单{state['order_id']}物流：{tracking_number}。"
    else:
        raise ValueError("本步仅支持status或tracking请求。")
    return {"answer": answer}
```

## 运行与预期结果

**访问范围：本地运行（无外部模型请求）。**
在仓库根目录、已激活上述环境后运行。Windows 与 macOS/Linux 使用同一条 Python 命令：

```console
python -m learning.frameworks.step_20e_checkpoint
```


**应观察到：** c1延续、c2隔离；新保存器没有旧记录。

结果以当前运行和代码为准，不要求真实模型逐字复现示例。只验证本地结构的课程不能证明模型的语义选择或生成质量。

## 常见错误

- 找不到 `app` 或 `learning`：回到仓库根目录，使用上面的模块运行命令，不直接双击脚本。
- 若出现外部请求或缺配置错误，先核对是否运行了本课命令以及是否填好占位配置；离线总检查会强制使用假配置。
- 不在；跨进程持久化需要数据库等持久保存器。

## 自测与参考答案

1. 进程重启后内存Checkpoint还在吗？
2. 用本课具体输入复述入口、处理步骤、结果；指出哪些动作发生在本地。

<details>
<summary>展开参考答案（先独立作答）</summary>

1. 不在；跨进程持久化需要数据库等持久保存器。
2. 同一内存保存器+c1 → 保存10001 → 再次输入request → 恢复编号。本课运行入口在本地完成；引用的正式服务可能有真实模型能力，不能据此判断本示例进行了网络请求。

</details>

## 完成标准

- 能解释“按 thread_id 恢复状态”，并指出代码中的依据。
- 能区分程序输出、模型输出与人工标注；遇到不一致先定位到具体步骤。
