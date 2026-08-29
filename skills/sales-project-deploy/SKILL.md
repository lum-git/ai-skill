---
name: "原型项目部署"
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
│   ├── conf.md           # 部署参数配置
│   └── deploy.py         # 部署执行脚本
└── scripts/              # 保留空目录占位
```

所有配置在 [conf.md](./references/conf.md) 中统一管理。账号密码通过 Secrets API 实时获取，不落盘。

## 执行流程

### 1. 读取配置

从 [conf.md](./references/conf.md) 中读取以下配置：

| 配置项 | 说明 |
|--------|------|
| `DEPLOY_IP` | 远程服务器 IP |
| `DEPLOY_PORT` | SSH 端口 |
| `DEPLOY_REMOTE_BASE` | 远程部署根路径 |

### 2. 获取账号密码

通过 Secrets API 获取部署凭据：

```
POST {PAPERCLIP_API_URL}/api/agents/me/secrets/{key}/value
Authorization: Bearer {PAPERCLIP_API_KEY}
```

需要获取的 Secret Key：

| Key | 用途 |
|-----|------|
| `deploy-deploy_account` | 服务器登录账号 |
| `deploy-deploy_password` | 服务器登录密码 |

### 3. 确认参数

向用户确认以下信息：
- 本地产物路径（打包后的 dist 目录等）

同时获取当前任务 id，作为部署子目录名。

### 4. 执行部署

运行部署脚本（纯 Python，仅需 `pip install paramiko`）：

```bash
python references/deploy.py <本地产物路径> <当前任务id>
# 示例: python references/deploy.py ./dist HYSQZC-971
```

脚本通过 paramiko SFTP 同步本地目录到远程：

- 自动创建远程目录结构
- 对比文件大小，跳过未变化的文件
- `--delete` 等效行为：删除远程多余文件和空目录

### 5. 验证结果

检查脚本退出码，确认部署成功或失败。

## 部署说明

将本地产物目录下的所有内容 rsync 到远程 `salesProject/{当前任务id}/` 子目录中。
