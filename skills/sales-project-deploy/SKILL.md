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
    └── deploy.py         # 部署执行脚本
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
- 项目名称拼音首字母，从用户的任务描述中提取

### 4. 执行部署

运行部署脚本（需 python3 + sshpass + rsync）：

```bash
python scripts/deploy.py <本地产物路径> <项目拼音首字母>
```

脚本内部通过 `sshpass` + `rsync` 执行同步：

- `-a`：归档模式，保留权限和时间戳
- `-v -z`：详细输出 + 传输压缩
- `--delete`：删除远程多余文件，确保完全一致
- `--progress`：显示进度
- `LOCAL_PATH` 自动追加 `/`，同步目录内容而非目录本身

### 5. 验证结果

检查 rsync 命令的退出码，确认部署成功或失败。

## 部署说明

将本地产物目录下的所有内容 rsync 到远程 `salesProject/{项目拼音首字母}/` 子目录中。
