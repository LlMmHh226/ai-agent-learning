# 09 · 程序级拒答

[课程目录](../README.md) · [运行与排错](../../docs/setup.md)

## 学习目标

用空结果分支阻止无依据生成。完成后应能用本课输入解释参数来源、执行分支和返回值去向。

## 前置知识

先完成 [rag/08 RAGService](step_08_rag_service.md)。
环境：基础环境 `.venv`。

## 文件职责

- [本课代码入口](step_09_reliable_refusal.py)：学习代码，关键定义：模块顶层按顺序执行的变量与调用。
- [正式调用链参照](../../app/services/rag_service.py)：比较学习脚本与应用入口的关系。
- [代码定位方法](../../docs/code-reading.md)：按函数名查找，不依赖旧行号。

## 具体输入与执行过程

```text
“商品有优惠券吗”
→ 分数过滤
→ []
→ 固定拒答
```

下面摘录当前入口的一段代码（省略部分文档字符串）；其余部分请打开完整文件。先找到输入变量，再标出传给下一个函数的参数，最后找到调用方接收返回值的位置。

```python
query = "商品有优惠券吗？"

raw_results = retrieve(
    query=query,
    chunks=rag_service.chunks,
    top_k=1,
    min_score=0.0,
)
raw_score = raw_results[0].score if raw_results else 0.0

result = asyncio.run(rag_service.chat(query=query))

print(f"用户问题：{query}")
print(f"过滤前最高分：{raw_score:.3f}")
print(f"RAGService 最低分：{rag_service.min_score:.3f}")
print(f"最终回答：{result.answer}")
print(f"来源数量：{len(result.sources)}")
```

## 运行与预期结果

**访问范围：当前固定无资料示例不请求模型；更改问题或知识库后可能进入真实生成分支。**
在仓库根目录、已激活上述环境后运行。Windows 与 macOS/Linux 使用同一条 Python 命令：

```console
python -m learning.rag.step_09_reliable_refusal
```


**应观察到：** 当前知识库下 sources=[]，不发聊天请求。

结果以当前运行和代码为准，不要求真实模型逐字复现示例。只验证本地结构的课程不能证明模型的语义选择或生成质量。

## 常见错误

- 找不到 `app` 或 `learning`：回到仓库根目录，使用上面的模块运行命令，不直接双击脚本。
- 若出现外部请求或缺配置错误，先核对是否运行了本课命令以及是否填好占位配置；离线总检查会强制使用假配置。
- 不能；相关文档仍可能缺少答案，分数不是事实充分性的证明。

## 自测与参考答案

1. 最低分数能覆盖所有无答案问题吗？
2. 用本课具体输入复述入口、处理步骤、结果；指出哪些动作发生在本地。

<details>
<summary>展开参考答案（先独立作答）</summary>

1. 不能；相关文档仍可能缺少答案，分数不是事实充分性的证明。
2. “商品有优惠券吗” → 分数过滤 → [] → 固定拒答。本课运行入口在本地完成；引用的正式服务可能有真实模型能力，不能据此判断本示例进行了网络请求。

</details>

## 完成标准

- 能解释“用空结果分支阻止无依据生成”，并指出代码中的依据。
- 能区分程序输出、模型输出与人工标注；遇到不一致先定位到具体步骤。
