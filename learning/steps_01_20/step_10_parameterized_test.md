# 10 · 参数化测试

[课程目录](../README.md) · [运行与排错](../../docs/setup.md)

## 学习目标

用同一规则覆盖多组输入。完成后应能用本课输入解释参数来源、执行分支和返回值去向。

## 前置知识

先完成 [steps_01_20/09 首个单元测试](step_09_first_test.md)。
环境：基础环境 `.venv`。

## 文件职责

- [本课代码入口](step_10_parameterized_test.py)：学习代码，关键定义：`OrderToolParameterizedTests`。
- [正式调用链参照](../../app/services/llm_service.py)：比较学习脚本与应用入口的关系。
- [代码定位方法](../../docs/code-reading.md)：按函数名查找，不依赖旧行号。

## 具体输入与执行过程

```text
多个订单编号
→ subTest
→ 相同断言
```

下面摘录当前入口的一段代码（省略部分文档字符串）；其余部分请打开完整文件。先找到输入变量，再标出传给下一个函数的参数，最后找到调用方接收返回值的位置。

```python
    def test_existing_orders(self) -> None:
        # 每个元组是一组输入和预期结果。
        cases = [
            ("10001", "已发货", "机械键盘", "SF1234567890"),
            ("10002", "待发货", "无线鼠标", ""),
            ("10003", "已完成", "显示器", "YT9876543210"),
        ]

        for order_id, expected_status, expected_product, expected_tracking in cases:
            # 如果某一组失败，测试报告会显示具体是哪个 order_id。
            with self.subTest(order_id=order_id):
                result = get_order_status(order_id)

                self.assertTrue(result["found"])
                self.assertEqual(result["order_id"], order_id)
                self.assertEqual(result["status"], expected_status)
                self.assertEqual(result["product"], expected_product)
                self.assertEqual(
                    result["tracking_number"],
                    expected_tracking,
                )
```

## 运行与预期结果

**访问范围：本地运行（无外部模型请求）。**
在仓库根目录、已激活上述环境后运行。Windows 与 macOS/Linux 使用同一条 Python 命令：

```console
python -m learning.steps_01_20.step_10_parameterized_test
```


**应观察到：** 各案例独立报告失败，避免复制多份测试。

结果以当前运行和代码为准，不要求真实模型逐字复现示例。只验证本地结构的课程不能证明模型的语义选择或生成质量。

## 常见错误

- 找不到 `app` 或 `learning`：回到仓库根目录，使用上面的模块运行命令，不直接双击脚本。
- 若出现外部请求或缺配置错误，先核对是否运行了本课命令以及是否填好占位配置；离线总检查会强制使用假配置。
- 不能，只覆盖给定样本；应根据边界和失败模式选择案例。

## 自测与参考答案

1. 参数化测试能证明所有输入都正确吗？
2. 用本课具体输入复述入口、处理步骤、结果；指出哪些动作发生在本地。

<details>
<summary>展开参考答案（先独立作答）</summary>

1. 不能，只覆盖给定样本；应根据边界和失败模式选择案例。
2. 多个订单编号 → subTest → 相同断言。本课运行入口在本地完成；引用的正式服务可能有真实模型能力，不能据此判断本示例进行了网络请求。

</details>

## 完成标准

- 能解释“用同一规则覆盖多组输入”，并指出代码中的依据。
- 能区分程序输出、模型输出与人工标注；遇到不一致先定位到具体步骤。
