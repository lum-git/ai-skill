---
name: "sales-project-deploy"
description: "将构建产物通过 rsync 部署到公司内网 Nginx 服务器。当用户需要部署项目、同步产物到远程预览机、发布到 Nginx 时调用此技能。"
---

# 销售项目部署

将前端构建产物通过 rsync 同步部署到远程服务器。

## 文件结构

```
sales-project-deploy/
├── SKILL.md
├── assets/               # 静态资源（暂无）
├── references/
│   └── conf.md           # 部署参数配置
└── scripts/
    └── deploy.sh         # 部署执行脚本
```

所有配置在 [conf.md](./references/conf.md) 中统一管理。账号密码通过 Secrets API 实时获取，不落盘。

## 执行流程

1. **读取配置**：[deploy.sh](./scripts/deploy.sh) 通过 Secrets API 获取账号密码，从 [conf.md](./references/conf.md) 读取服务器配置。

2. **确认参数**：向用户确认以下信息：
   - 本地产物路径（打包后的 dist 目录等）
   - 项目名称拼音首字母，从用户的任务描述中提取

3. **执行部署**：

   ```bash
   bash ./scripts/deploy.sh <本地产物路径> <项目拼音首字母>
   ```

   > 注意：
   > - 需要提前安装 `sshpass`（Windows 可通过 WSL/Git Bash 使用）
   > - `--delete` 会删除远程多余文件，确保完全一致

4. **验证结果**：检查脚本退出码，确认部署成功或失败。

## 部署说明

将本地产物目录下的所有内容 rsync 到远程 `salesProject/{项目拼音首字母}/` 子目录中。
