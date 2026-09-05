# 集团招采测试环境部署配置

> 数据库密码通过 Secrets API 实时获取，不在文件中存储。

## 基础配置

| 配置项 | 值 | 说明 |
|--------|-----|------|
| `PROJ` | `jt12302` | 项目名（同时也是容器名 / 镜像名 / WAR 文件名） |
| `PORT` | `12302` | 宿主机端口（容器内固定 8080） |
| `GRADLE_CONTAINER` | `gradle-12302` | 构建用临时容器名（用完即删，惯例 `gradle-{PORT}`） |
| `GRADLE_IMAGE` | `swr.cn-south-1.myhuaweicloud.com/hylc/gradle:6.5.1` | 构建镜像（Gradle 6.5.1） |
| `TOMCAT_IMAGE` | `swr.cn-south-1.myhuaweicloud.com/hylc/tomcat:8.5.71` | 运行基础镜像（tomcat 8.5 + jdk8，预装 vim/unzip） |
| `JAVA_OPTS` | `-Djava.security.egd=file:/dev/./urandom` | 容器 JVM 参数 |
| `IMAGE_KEEP` | `3` | 镜像清理阈值（tail -n +3 = 只保留最近 2 个版本） |

## 测试环境服务器与构建参数（TEST_ 前缀）

取值优先级：**用户在对话中指定 > 环境变量（Paperclip `{env:...}` 引用，运行时解析）> 向用户询问**。

| 配置项 | 值 | 说明 |
|--------|-----|------|
| `TEST_SERVER_HOST` | `{env:TEST_SERVER_HOST}` | 执行构建与部署的服务器地址 |
| `TEST_SERVER_PORT` | `{env:TEST_SERVER_PORT}` | 构建服务器 SSH 端口（环境变量未设置时默认 22，区别于服务端口 `PORT`） |
| `TEST_SERVER_ACCOUNT` | `{env:TEST_SERVER_ACCOUNT}` | 构建服务器 SSH 账号 |
| `TEST_SERVER_PASSWORD` | `{env:TEST_SERVER_PASSWORD}` | 构建服务器 SSH 密码 |
| `TEST_GIT_BRANCH` | `{env:TEST_GIT_BRANCH}` | 构建分支（环境变量未设置时默认 master） |

> 实际值在 Paperclip 运行环境中通过同名环境变量（`TEST_*`）提供，不在本文件中存储。用户在对话中指定的值优先：Agent 直接使用指定值；环境变量与用户指定均缺时向用户询问。

## 路径配置

| 配置项 | 值 | 说明 |
|--------|-----|------|
| `BUILD_ROOT` | `/buildCenter/zhaocai/dockerBuildFile` | Dockerfile 与 WAR 的工作目录（其下按 `$PROJ` 分子目录） |
| `WORKSPACE_HOST` | `/home/data/jenkins-slave` | 代码仓库宿主机根路径（docker 挂载源，GitLab 拉取的代码存放于此） |
| `WORKSPACE_MOUNT` | `/jenkins-slave` | 构建容器内的挂载点（固定） |
| `GRADLE_CD_DIR` | `/jenkins-slave/workspace/zhaocai` | Gradle 构建容器内的代码路径（容器视角 = 挂载点 + `/workspace/zhaocai`，固定不变） |
| `WAR_DIR` | `/home/data/jenkins-slave/workspace/zhaocai` | 脚本（宿主机）视角的代码路径（查找 WAR 用），与 `GRADLE_CD_DIR` 是同一目录的两种视角 |
| `GRADLE_REP` | `/data/zhaocai/gradle-rep` | Gradle 仓库缓存（宿主机路径，挂载提速） |
| `WEBAPPS_ROOT` | `/data/zhaocai/webapps` | 附件与日志的挂载根目录 |

> 工作区代码通过 **GitLab 拉取**维护，统一存放在宿主机 `/home/data/jenkins-slave/workspace/zhaocai/{PROJ}/`（构建容器内视角为 `/jenkins-slave/workspace/zhaocai/{PROJ}/`）。本脚本只负责"构建 + 制镜像 + 启动容器"，**不执行 git pull**；部署前请先确保代码已切换到目标分支（默认 `TEST_GIT_BRANCH`）并拉取到最新。

## 配置替换对（application.properties，构建环境 → 测试环境）

替换目标值为测试环境专属参数，**配置项名 = 环境变量名**（与其他 `TEST_` 参数一致）：`TEST_REDIS_HOST` 替换 `REDIS_FROM`、`TEST_DB_HOST` 替换 `DB_HOST_FROM`、`TEST_DB_PORT` 替换 `DB_PORT_FROM`、`TEST_DB_NAME` 替换 `DB_NAME_FROM`。取值规则与「测试环境服务器与构建参数」小节相同，优先级：**用户指定 > `{env:...}` 环境变量（Paperclip 运行环境配置，脚本运行时解析）> 脚本报错提示**。**脚本读取 `{env:...}` 环境变量的前提是用户未特意指定值**：用户指定时由 Agent 以命令行同名环境变量传入（如 `TEST_DB_HOST=192.168.1.99 bash deploy.sh.md`，命令行赋值会遮蔽运行环境的同名变量，用户值因此优先生效）；用户未指定时才读取 Paperclip 运行环境的同名环境变量；两者皆无则脚本报错提示。

| 配置项 | 值 | 说明 |
|--------|-----|------|
| `REDIS_FROM` | `10.22.50.200` | 原配置 Redis 地址（源码常量，sed 匹配源） |
| `TEST_REDIS_HOST` | `{env:TEST_REDIS_HOST}` | 测试环境 Redis 地址（替换 `REDIS_FROM`） |
| `DB_HOST_FROM` | `10.50.84.187` | 原配置数据库地址（源码常量，sed 匹配源） |
| `TEST_DB_HOST` | `{env:TEST_DB_HOST}` | 测试环境数据库地址（替换 `DB_HOST_FROM`） |
| `DB_PORT_FROM` | `3306` | 原配置数据库端口（源码常量，sed 匹配源） |
| `TEST_DB_PORT` | `{env:TEST_DB_PORT}` | 测试环境数据库端口（替换 `DB_PORT_FROM`） |
| `DB_NAME_FROM` | `bg-zhaocai` | 原配置数据库名（源码常量，sed 匹配源） |
| `TEST_DB_NAME` | `{env:TEST_DB_NAME}` | 测试环境数据库名（替换 `DB_NAME_FROM`） |

## 关联的 Secret

脚本通过 `POST /api/agents/me/secrets/{key}/value` 获取（也可用环境变量直接传入）：

| Secret Key | 环境变量覆盖 | 用途 |
|------------|------------|------|
| `zhaocai-db_password_from` | `DB_PWD_FROM` | 原配置数据库密码（sed 匹配源） |
| `zhaocai-db_password_to` | `DB_PWD_TO` | 测试环境数据库密码（sed 替换值） |
