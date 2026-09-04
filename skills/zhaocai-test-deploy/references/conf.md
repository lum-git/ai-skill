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

> 工作区代码通过 **GitLab 拉取**维护，统一存放在宿主机 `/home/data/jenkins-slave/workspace/zhaocai/{PROJ}/`（构建容器内视角为 `/jenkins-slave/workspace/zhaocai/{PROJ}/`）。本脚本只负责"构建 + 制镜像 + 启动容器"，**不执行 git pull**；部署前请先确保代码已拉取到目标版本。

## 配置替换对（application.properties，构建环境 → 测试环境）

| 配置项 | 值 | 说明 |
|--------|-----|------|
| `REDIS_FROM` | `10.22.50.200` | 原配置 Redis 地址 |
| `REDIS_TO` | `192.168.1.40` | 测试环境 Redis 地址 |
| `DB_HOST_FROM` | `10.50.84.187` | 原配置数据库地址 |
| `DB_HOST_TO` | `192.168.1.215` | 测试环境数据库地址 |
| `DB_PORT_FROM` | `3306` | 原配置数据库端口 |
| `DB_PORT_TO` | `13306` | 测试环境数据库端口 |
| `DB_NAME_FROM` | `bg-zhaocai` | 原配置数据库名 |
| `DB_NAME_TO` | `jt20260820` | 测试环境数据库名 |

## 关联的 Secret

脚本通过 `POST /api/agents/me/secrets/{key}/value` 获取（也可用环境变量直接传入）：

| Secret Key | 环境变量覆盖 | 用途 |
|------------|------------|------|
| `zhaocai-db_password_from` | `DB_PWD_FROM` | 原配置数据库密码（sed 匹配源） |
| `zhaocai-db_password_to` | `DB_PWD_TO` | 测试环境数据库密码（sed 替换值） |
