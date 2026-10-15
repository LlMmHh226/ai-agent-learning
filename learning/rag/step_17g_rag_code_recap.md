# 17g · RAG 代码复盘

[课程目录](../README.md) · [运行与排错](../../docs/setup.md)

## 学习目标

用三个输入追踪两条分支。完成后应能用本课输入解释参数来源、执行分支和返回值去向。

## 前置知识

先完成 [rag/17f RAG 阶段边界](step_17f_rag_stage_boundary.md)。
环境：基础环境 `.venv`。

## 文件职责

- [本课代码入口](step_17g_rag_branch_recap.py)：学习代码，关键定义：`main`。
- [正式调用链参照](../../app/services/rag_service.py)：比较学习脚本与应用入口的关系。
- [代码定位方法](../../docs/code-reading.md)：按函数名查找，不依赖旧行号。

## 具体输入与执行过程

```text
原话物流/同义物流/运费问题
→ retrieve
→ 空结果或生成分支
```

下面摘录当前入口的一段代码（省略部分文档字符串）；其余部分请打开完整文件。先找到输入变量，再标出传给下一个函数的参数，最后找到调用方接收返回值的位置。

```python
def main() -> None:
    for question in QUESTIONS:
        retrieval_results = retrieve(
            query=question,
            chunks=rag_service.chunks,
            top_k=rag_service.top_k,
            min_score=rag_service.min_score,
        )
        sources = [
            result.document.metadata["source"]
            for result in retrieval_results
        ]

        print(f"问题：{question}")
        print(f"检索来源：{sources}")
        if not retrieval_results:
            print(f"Python 分支：直接拒答“{RAG_INSUFFICIENT_CONTEXT_RESPONSE}”")
            print("后续：不会构建 Prompt，也不会调用聊天模型\n")
        else:
            print("Python 分支：结果非空，会继续构建 Prompt 和调用聊天模型")
            print("注意：本学习脚本只展示分支，不执行后续模型调用\n")
```

## 运行与预期结果

**访问范围：本地运行（无外部模型请求）。**
在仓库根目录、已激活上述环境后运行。Windows 与 macOS/Linux 使用同一条 Python 命令：

```console
python -m learning.rag.step_17g_rag_branch_recap
```


**应观察到：** 本地模拟展示分支与来源，能解释分数的局限。

结果以当前运行和代码为准，不要求真实模型逐字复现示例。只验证本地结构的课程不能证明模型的语义选择或生成质量。

## 常见错误

- 找不到 `app` 或 `learning`：回到仓库根目录，使用上面的模块运行命令，不直接双击脚本。
- 若出现外部请求或缺配置错误，先核对是否运行了本课命令以及是否填好占位配置；离线总检查会强制使用假配置。
- 空检索直接固定拒答；非空检索构建消息并请求生成，不能保证事实充足。

## 自测与参考答案

1. 两条 Python 分支是什么？
2. 用本课具体输入复述入口、处理步骤、结果；指出哪些动作发生在本地。

<details>
<summary>展开参考答案（先独立作答）</summary>

1. 空检索直接固定拒答；非空检索构建消息并请求生成，不能保证事实充足。
2. 原话物流/同义物流/运费问题 → retrieve → 空结果或生成分支。本课运行入口在本地完成；引用的正式服务可能有真实模型能力，不能据此判断本示例进行了网络请求。

</details>

## 完成标准

- 能解释“用三个输入追踪两条分支”，并指出代码中的依据。
- 能区分程序输出、模型输出与人工标注；遇到不一致先定位到具体步骤。
