# 贡献指南

欢迎修正教程、补充可复现问题或改进小范围实现。一次改动围绕一个明确教学目标，保持现有步骤编号和导入路径，避免把入门课改成大型框架模板。

## 提交前检查

使用 Python 3.11，在相应环境运行：

```console
python -m scripts.check_docs
python -m scripts.verify_offline --suite base
```

涉及框架时，在独立框架环境再运行：

```console
python -m scripts.verify_offline --suite framework
```

默认验证不需要密钥。不要把真实调用加进CI，也不要将个人 `.env`、供应商返回的请求头或真实业务数据写入测试。

## 添加课程

1. 使用已有目录和步骤编号体系，为新脚本配套Markdown讲义。
2. 讲义包含学习目标、前置知识、文件职责、具体调用链、运行与预期、常见错误、自测及折叠答案。
3. 显式标注是否访问外部模型；涉及模拟时说明替换位置和验证边界。
4. 更新 `docs/lessons.json` 和课程导航；有安全的离线入口时加入验证白名单。
5. 对行为变化增加有意义的边界验证；纯文案改动检查链接即可。

提问或提交PR时写清问题、复现命令、预期与实际结果、验证方式。新增依赖应修改 `.in` 并重新生成对应 `.txt` 完整清单，在全新环境验证后提交。

当前维护工具可使用 uv：`uv pip compile requirements.in --python-version 3.11 --universal -o requirements.txt`；框架使用其独立的 `.in` 路径生成清单。普通读者不需要安装uv。

贡献按仓库 [MIT 许可](LICENSE)分发。保留第三方依赖原有许可，不将其代码或虚拟环境打包进本仓库。
