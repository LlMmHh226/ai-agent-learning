# 上传到 GitHub

[返回首页](../README.md)

此目录可以作为独立仓库根目录。不要把它的父目录一起上传，也不要复制原学习项目的Git历史。

## 发布前

```console
python -m scripts.check_docs
python -m scripts.verify_offline --suite base
```

框架环境运行 `python -m scripts.verify_offline --suite framework`。核对 [验证记录](validation.md)，不要把未执行的平台测试写成通过。

`.gitignore` 排除 `.env`、虚拟环境和缓存。**忽略规则不能删除已提交的秘密**；若以后误提交密钥，需先撤销密钥，再处理历史。

## 创建空仓库后上传

在GitHub创建自己的空仓库，推荐名称 `ai-agent-learning`，描述可以用：

> 中文 AI Agent 自学教程：原生 Python、FastAPI、RAG、上下文工程与 LangGraph，包含分步代码、练习和离线检查。

在本目录执行以下命令。将 `<YOUR_REPOSITORY_URL>` 替换为GitHub显示的仓库地址；不要原样执行占位符。

```console
git init -b main
git add .
git diff --cached --stat
git diff --cached --name-only
git commit -m "Publish Chinese AI Agent learning tutorial"
git remote add origin <YOUR_REPOSITORY_URL>
git push -u origin main
```

在提交前的文件列表中确认没有 `.env`、`.venv`、缓存或个人记录；仅 `.env.example` 应纳入配置样例。推送后查看 Actions 的基础/框架检查结果，确认首页链接正常，再发布第一个Release。

仓库已提供MIT许可。尚未关联任何远程仓库，不包含GitHub账号信息，也没有执行上述上传操作。
