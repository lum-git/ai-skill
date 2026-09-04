---
name: "zhaocai-test-deploy"
description: "将集团招采系统后端部署到测试环境：Gradle 容器构建 WAR → Dockerfile 制作镜像（自动替换 Redis/数据库配置）→ 启动容器。部署目标项目由 conf.md 的 PROJ 配置决定（当前 jt12302），更换项目只需改 conf.md。当用户需要部署或更新集团招采测试环境、重新构建招采后端项目、重启招采后端服务时调用。不用于前端静态产物部署（那是 sales-project-deploy 技能），也不用于其他系统部署。"
---

# 集团招采测试环境部署

在招采测试服务器上完成招采后端项目的完整部署：**Gradle 容器构建 WAR → Docker 制作镜像（内置测试环境配置替换）→ 启动容器**。

> 本文中 `{PROJ}`、`{PORT}` 为占位符，实际值以 [conf.md](./references/conf.md) 为准（当前 `PROJ=jt12302`、`PORT=12302`）。

## 文件结构

```
zhaocai-test-deploy/
├── SKILL.md
└── references/
    ├── conf.md               # 部署参数配置（项目名/端口/路径/镜像/配置替换对）
    └── source/
        └── deploy.sh.md      # 部署脚本（.md 后缀，直接用 bash 执行）
```

所有配置在 [conf.md](./references/conf.md) 中统一管理。数据库密码通过 Secrets API 实时获取，不落盘。

## 执行流程

### 1. 读取配置

从 [conf.md](./references/conf.md) 读取项目名 `PROJ`、端口 `PORT` 及路径、镜像、配置替换对。更换部署项目时只需修改 conf.md，脚本无需改动。

### 2. 获取数据库密码

脚本自动通过 Secrets API 获取（需 `PAPERCLIP_API_URL` / `PAPERCLIP_API_KEY` 环境变量，也可用环境变量直接传入）：

| Secret Key | 环境变量覆盖 | 用途 |
|-----|-----|------|
| `zhaocai-db_password_from` | `DB_PWD_FROM` | 原配置数据库密码（sed 匹配源） |
| `zhaocai-db_password_to` | `DB_PWD_TO` | 测试环境数据库密码（sed 替换值） |

### 3. 确认部署方式

向用户确认：
- **全量部署**（默认）：重新 Gradle 构建，耗时较长
- **跳过构建**（`--skip-build`）：复用最近一次 WAR，只重做镜像和容器

### 4. 执行部署

脚本源码以 `.md` 后缀存放在 `references/source/deploy.sh.md`（技能仓库不允许 `.sh` 文件）。bash 不检查文件扩展名，**直接执行即可，无需复制或重命名**：

```bash
# 全量部署
bash <技能目录>/references/source/deploy.sh.md
# 跳过构建（复用已有 WAR）
bash <技能目录>/references/source/deploy.sh.md --skip-build
```

脚本自动完成：
1. Gradle 容器构建 WAR（`gradle clean build --parallel -PskipTests`，跳过测试）
2. WAR 校验：构建失败立即中止，**不影响正在运行的旧容器**
3. 停旧容器 → 删当日旧镜像 → 清理历史镜像（只保留最近 2 个版本）
4. 生成 Dockerfile：tomcat 基础镜像 + 解压 WAR + **替换配置**（Redis 地址、数据库地址/端口/库名/密码，构建环境 → 测试环境）+ 清理冲突 jar
5. 制作镜像 `{PROJ}:YYYYMMDD` 并启动容器（端口 `{PORT} → 8080`，挂载附件与日志目录）

### 5. 验证结果

脚本末尾自动检查容器运行状态。失败时执行 `docker logs {PROJ}` 查看日志。

## 关键约束

| 约束 | 说明 |
|------|------|
| 代码来源 | 工作区代码通过 **GitLab 拉取**维护，存放在宿主机 `/home/data/jenkins-slave/workspace/zhaocai/{PROJ}/`；脚本不执行 git pull，部署前需确认已拉取到目标版本 |
| 执行位置 | 必须在**有 docker 权限的招采测试服务器**上执行（脚本直接操作本机 docker） |
| 镜像版本 | 以当天日期（YYYYMMDD）为版本号；同日重复部署会先删当日旧镜像再重建 |
| 镜像保留 | 只保留最近 2 个版本，更早版本自动清理 |
| 数据持久化 | 附件（`s/upload`）与日志挂载宿主机 `/data/zhaocai/webapps/`，重建容器不丢失 |
| 密码安全 | 数据库密码运行时从 Secrets API 获取，不写入仓库任何文件 |

## 常见问题

| 问题 | 处理 |
|------|------|
| WAR 不存在而中止 | 构建失败，或 GitLab 拉取的代码不在 `WAR_DIR` 下（检查 `/home/data/jenkins-slave/workspace/zhaocai/{PROJ}/build/libs/` 是否有 WAR） |
| 容器启动后异常退出 | `docker logs {PROJ}` 查看原因，常见为测试环境数据库/Redis 不可达 |
| 需要回滚 | 历史镜像仅保留 2 个版本：`docker stop/rm {PROJ}` 后用旧日期 tag 重新 `docker run`（挂载参数见脚本） |
