#!/usr/bin/env bash
# =====================================================================
# 集团招采测试环境部署脚本
# 流程: Gradle 容器构建 WAR → Dockerfile 制作镜像(替换测试环境配置) → 启动容器
#
# 用法:
#   bash deploy.sh.md               # 全量部署（构建 + 制镜像 + 启动）
#   bash deploy.sh.md --skip-build  # 跳过构建，复用最近一次的 WAR
#
# 说明: 本文件以 .md 后缀存放（技能仓库不允许 .sh 文件）。
#      bash 不检查文件扩展名，直接执行，无需重命名。
#
# 依赖: 招采测试服务器上的 docker。数据库密码通过 Paperclip Secrets API
#      获取（需 PAPERCLIP_API_URL / PAPERCLIP_API_KEY 环境变量，
#      也可用 DB_PWD_FROM / DB_PWD_TO 环境变量直接传入）。
#      conf.md 中 {env:VAR} 形式的值在运行时解析同名环境变量
#      （用户在对话中指定的值也以环境变量方式传入，优先级最高）
# =====================================================================

set -o pipefail

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
CONF_FILE="$SCRIPT_DIR/../conf.md"

# ---------------- 工具函数 ----------------

die() { echo "错误: $*" >&2; exit 1; }
log()  { echo; echo "==> $*"; }

# 从 conf.md 表格中读取 `KEY` | `value` 形式的配置值。
# 值支持 Paperclip {env:VAR} 引用: 运行时解析同名环境变量；
# 用户在对话中指定的值由 Agent 以环境变量方式传入（优先级最高）。
read_conf() {
  local key="$1" val
  [ -f "$CONF_FILE" ] || die "配置文件不存在: $CONF_FILE"
  val=$(sed -n 's/^| *`'"$key"'` *| *`\([^`]*\)`.*$/\1/p' "$CONF_FILE" | head -n 1)
  # 解析 {env:VAR} 引用（支持整值引用，也支持嵌在字符串中）
  while [[ "$val" =~ \{env:([A-Za-z_][A-Za-z0-9_]*)\} ]]; do
    local var="${BASH_REMATCH[1]}"
    local env_val="${!var:-}"
    [ -n "$env_val" ] || die "配置 $key 引用的环境变量 $var 未设置（用户未提供时需在运行环境配置同名环境变量）"
    val="${val/\{env:$var\}/$env_val}"
  done
  printf '%s' "$val"
}

# 转义 sed 特殊字符（/ & \ . * $），密码含特殊字符时保证替换正确
sed_escape() {
  printf '%s' "$1" | sed 's/[\/&\\.*$]/\\&/g'
}

# 通过 Secrets API 获取值（支持环境变量直接覆盖）
get_secret() {
  local key="$1" env_name="$2"
  local val="${!env_name:-}"
  if [ -z "$val" ]; then
    local api_url="${PAPERCLIP_API_URL:-}" api_key="${PAPERCLIP_API_KEY:-}"
    api_url="${api_url%/}"
    [ -n "$api_url" ] && [ -n "$api_key" ] || \
      die "缺少 PAPERCLIP_API_URL / PAPERCLIP_API_KEY 环境变量（或设置 $env_name 直接传入）"
    val=$(curl -sS -X POST "$api_url/api/agents/me/secrets/$key/value" \
      -H "Authorization: Bearer $api_key" \
      -H "Content-Type: application/json" 2>/dev/null \
      | sed -n 's/.*"value"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')
    [ -n "$val" ] || die "获取 Secret $key 失败（检查 Secret 是否已配置）"
  fi
  printf '%s' "$val"
}

# ---------------- 参数与配置 ----------------

SKIP_BUILD=0
[ "${1:-}" = "--skip-build" ] && SKIP_BUILD=1

PROJ=$(read_conf PROJ)
PORT=$(read_conf PORT)
GRADLE_CONTAINER=$(read_conf GRADLE_CONTAINER)
GRADLE_IMAGE=$(read_conf GRADLE_IMAGE)
TOMCAT_IMAGE=$(read_conf TOMCAT_IMAGE)
JAVA_OPTS=$(read_conf JAVA_OPTS)
IMAGE_KEEP=$(read_conf IMAGE_KEEP)
BUILD_ROOT=$(read_conf BUILD_ROOT)
WORKSPACE_HOST=$(read_conf WORKSPACE_HOST)
WORKSPACE_MOUNT=$(read_conf WORKSPACE_MOUNT)
GRADLE_CD_DIR=$(read_conf GRADLE_CD_DIR)
WAR_DIR=$(read_conf WAR_DIR)
GRADLE_REP=$(read_conf GRADLE_REP)
WEBAPPS_ROOT=$(read_conf WEBAPPS_ROOT)
REDIS_FROM=$(read_conf REDIS_FROM); TEST_REDIS_HOST=$(read_conf TEST_REDIS_HOST)
DB_HOST_FROM=$(read_conf DB_HOST_FROM); TEST_DB_HOST=$(read_conf TEST_DB_HOST)
DB_PORT_FROM=$(read_conf DB_PORT_FROM); TEST_DB_PORT=$(read_conf TEST_DB_PORT)
DB_NAME_FROM=$(read_conf DB_NAME_FROM); TEST_DB_NAME=$(read_conf TEST_DB_NAME)

[ -n "$PROJ" ] || die "conf.md 缺少 PROJ"
[ -n "$PORT" ] || die "conf.md 缺少 PORT"
[ -n "$WAR_DIR" ] || die "conf.md 缺少 WAR_DIR"
command -v docker >/dev/null 2>&1 || die "当前环境没有 docker 命令（必须在招采测试服务器上执行）"

DATE=$(date +%Y%m%d)
CONF_DIR="$BUILD_ROOT/$PROJ"
WAR_SRC="$WAR_DIR/$PROJ/build/libs/$PROJ.war"
WAR_DST="$CONF_DIR/$PROJ.war"

echo "===================================================="
echo " 集团招采测试环境部署"
echo "   项目: $PROJ    镜像版本: $DATE"
echo "   模式: $([ "$SKIP_BUILD" = "1" ] && echo "跳过构建(复用已有 WAR)" || echo "全量部署(Gradle 构建)")"
echo "===================================================="

# ---------------- 1. 获取数据库密码（Secrets） ----------------

log "获取数据库密码（Secrets API）"
PWD_FROM=$(get_secret zhaocai-db_password_from DB_PWD_FROM)
PWD_TO=$(get_secret zhaocai-db_password_to DB_PWD_TO)
# 密码含 sed 特殊字符时转义，保证替换正确
PWD_FROM_ESC=$(sed_escape "$PWD_FROM")
PWD_TO_ESC=$(sed_escape "$PWD_TO")

# ---------------- 2. 构建 WAR ----------------

mkdir -p "$CONF_DIR"

if [ "$SKIP_BUILD" = "1" ]; then
  [ -f "$WAR_DST" ] || die "跳过构建，但未找到已有 WAR: $WAR_DST（请先执行一次全量部署）"
  log "跳过构建，复用 WAR: $WAR_DST"
else
  log "Gradle 容器构建 WAR（跳过测试，耗时较长）"
  docker rm -f "$GRADLE_CONTAINER" >/dev/null 2>&1 || true
  docker run --name "$GRADLE_CONTAINER" \
    -v "$WORKSPACE_HOST:$WORKSPACE_MOUNT" \
    -v /etc/localtime:/etc/localtime \
    -v "$GRADLE_REP:/root/.gradle" \
    "$GRADLE_IMAGE" \
    bash -c "cd $GRADLE_CD_DIR/$PROJ && gradle clean build --parallel --profile -PskipTests -Dorg.gradle.jvmargs=-Xmx4048m --no-daemon" || true
  docker rm -f "$GRADLE_CONTAINER" >/dev/null 2>&1 || true

  # WAR 校验: 构建失败时立即中止，不影响正在运行的旧容器
  [ -f "$WAR_SRC" ] || die "WAR 不存在: $WAR_SRC（构建失败，或 GitLab 拉取的代码不在 WAR_DIR 下，见 conf.md 路径配置说明）"

  log "移动 WAR 至 Dockerfile 工作目录"
  mv "$WAR_SRC" "$WAR_DST" || die "移动 WAR 失败: $WAR_SRC → $WAR_DST"
fi

# ---------------- 3. 清理旧容器与镜像 ----------------

log "停止并删除旧容器 $PROJ"
docker stop "$PROJ" >/dev/null 2>&1 || true
docker rm "$PROJ" >/dev/null 2>&1 || true

log "删除当日版本镜像（避免重复创建），并清理历史版本（保留最近 2 个）"
docker rmi "$PROJ:$DATE" >/dev/null 2>&1 || true
docker images "$PROJ" | awk 'NR>1 {print $1, $2}' | sort -k2,2r | tail -n +"$IMAGE_KEEP" | awk '{print $1":"$2}' | xargs docker rmi >/dev/null 2>&1 || true

# ---------------- 4. 生成 Dockerfile ----------------

log "生成 Dockerfile: $CONF_DIR/Dockerfile"
rm -rf "$CONF_DIR/Dockerfile" || true
cat > "$CONF_DIR/Dockerfile" <<EOF

# 基础镜像是 tomcat8.5.71-jdk8 环境，预装了 vim、unzip 命令
FROM $TOMCAT_IMAGE
MAINTAINER lxm
COPY $PROJ.war /usr/local/tomcat/webapps/ROOT/

# 解压 WAR 包
RUN unzip -q -a -o /usr/local/tomcat/webapps/ROOT/$PROJ.war -d /usr/local/tomcat/webapps/ROOT || true
# 清理解压后的 WAR 文件
RUN rm -rf /usr/local/tomcat/webapps/ROOT/$PROJ.war

# redis 地址（构建环境 → 测试环境）
RUN sed -i "s/$REDIS_FROM/$TEST_REDIS_HOST/g" \$(grep $REDIS_FROM -rl /usr/local/tomcat/webapps/ROOT/WEB-INF/classes/application.properties) || true
# 数据库地址
RUN sed -i "s/$DB_HOST_FROM/$TEST_DB_HOST/g" \$(grep $DB_HOST_FROM -rl /usr/local/tomcat/webapps/ROOT/WEB-INF/classes/application.properties) || true
# 数据库端口
RUN sed -i "s/$DB_PORT_FROM/$TEST_DB_PORT/g" \$(grep $DB_PORT_FROM -rl /usr/local/tomcat/webapps/ROOT/WEB-INF/classes/application.properties) || true
# 数据库名称
RUN sed -i "s/$DB_NAME_FROM/$TEST_DB_NAME/g" \$(grep $DB_NAME_FROM -rl /usr/local/tomcat/webapps/ROOT/WEB-INF/classes/application.properties) || true
# 数据库密码
RUN sed -i "s/$PWD_FROM_ESC/$PWD_TO_ESC/g" \$(grep "$PWD_FROM_ESC" -rl /usr/local/tomcat/webapps/ROOT/WEB-INF/classes/application.properties) || true
# 数据库账号（默认相同，无需替换）
#RUN sed -i "s/root/root/g" \$(grep root -rl /usr/local/tomcat/webapps/ROOT/WEB-INF/classes/application.properties) || true
# 定时任务（默认关闭，需要时取消注释）
#RUN sed -i "s/schedule.job.enable=false/schedule.job.enable=true/g" \$(grep schedule.job.enable=false -rl /usr/local/tomcat/webapps/ROOT/WEB-INF/classes/application.properties) || true

# 日志 jar 包冲突，导致日志无法打印
RUN rm -rf /usr/local/tomcat/webapps/ROOT/WEB-INF/lib/slf4j-jdk14-1.5.6.jar || true
RUN rm -rf /usr/local/tomcat/webapps/ROOT/WEB-INF/classes/com/gxhylc/gbds/jpush/api/device/package-info.class || true
RUN rm -rf /usr/local/tomcat/webapps/ROOT/WEB-INF/classes/com/gxhylc/gbds/jpush/api/examples/package-info.class || true
RUN rm -rf /usr/local/tomcat/webapps/ROOT/WEB-INF/classes/com/gxhylc/gbds/jpush/api/push/package-info.class || true
RUN rm -rf /usr/local/tomcat/webapps/ROOT/WEB-INF/classes/com/gxhylc/gbds/jpush/api/report/package-info.class || true
RUN rm -rf /usr/local/tomcat/webapps/ROOT/WEB-INF/classes/com/gxhylc/gbds/jpush/api/schedule/package-info.class || true
RUN rm -rf /usr/local/tomcat/webapps/ROOT/WEB-INF/lib/xalan-2.6.0.jar || true

CMD ["catalina.sh", "run"]

EOF

# ---------------- 5. 制作镜像 ----------------

log "制作镜像 $PROJ:$DATE"
docker build -t "$PROJ:$DATE" "$CONF_DIR" || die "镜像构建失败（Dockerfile 见 $CONF_DIR/Dockerfile）"

# ---------------- 6. 启动容器 ----------------

log "启动容器（端口 $PORT → 8080，挂载附件与日志目录）"
mkdir -p "$WEBAPPS_ROOT/$PROJ/" "$WEBAPPS_ROOT/logs/$PROJ/" || true
docker run --name "$PROJ" -it -p "$PORT:8080" --restart=always --privileged=true \
  -v "$WEBAPPS_ROOT/$PROJ/s/upload:/usr/local/tomcat/webapps/ROOT/s/upload" \
  -v "$WEBAPPS_ROOT/logs/$PROJ:/usr/local/tomcat/logs" \
  -e JAVA_OPTS="$JAVA_OPTS" \
  -d "$PROJ:$DATE" >/dev/null || die "容器启动失败"

# ---------------- 7. 验证 ----------------

log "验证容器状态"
sleep 3
if docker ps --filter "name=$PROJ" --format '{{.Names}}' | grep -qx "$PROJ"; then
  echo "===================================================="
  echo " 部署成功"
  echo "   镜像: $PROJ:$DATE"
  echo "   容器: $PROJ（端口 $PORT → 8080）"
  echo "   日志: docker logs -f $PROJ"
  echo "===================================================="
else
  die "容器未处于运行状态，查看日志: docker logs $PROJ"
fi
