# MCP 22D：规格、价格与库存查询练习

## 学习目标

先写可独立测试的业务函数，区分「商品有多种规格」「某规格零库存」和「查无这个规格」。

## 前置知识

会用字典和函数；理解 [22A 参数边界](step_22a_formal_boundary.md)。这里不依赖上一课的 MCP 会话。

## 文件职责

[SKU 练习](step_22d_sku_lookup.py) 包含两条虚构规格，以 SKU 作字典键；还提供一份可运行参考实现。尝试先按下述输入输出自己写，再对照函数。

## 具体输入与执行过程

`KB-BLACK-BROWN` → 按完整键查字典 → 得到黑色茶轴 → 返回 `found:true`、`available_stock:0` 和以分为单位的 `price_cents`。`UNKNOWN` 查无记录，返回 `found:false`。一个商品 ID 可以关联多个规格，不能拿商品 ID 代替 SKU。

## 运行与预期结果

```console
python -m learning.mcp.step_22d_sku_lookup
python -m learning.mcp.step_22d_sku_lookup --sku-id KB-BLACK-BROWN
```

第一条检查有库存、零库存、无此规格三种情况；第二条只打印黑色茶轴样例。均无模型、外部服务或 MCP 协议调用，SKU 未注册到服务器。

## 常见错误

- 用 `if available_stock` 判定是否存在：零库存是正常查询结果。
- 把 `31900` 当作 31900 元：字段名 `price_cents` 明确表示分；显示给读者时才换算。

## 自测与参考答案

如果规格存在但没有库存，返回什么？为什么不直接返回一个布尔值？

<details>
<summary>参考答案</summary>

返回 `found:true` 和 `available_stock:0`，同时保留具体规格与价格。调用方才能区分「找到但缺货」和「编号错误或不存在」。

</details>
