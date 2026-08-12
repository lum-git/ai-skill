#!/bin/bash

# 销售项目部署脚本
# 用法: ./deploy.sh <本地产物路径> <项目拼音首字母>
# 账号密码通过 Paperclip Secrets API 获取

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CONF_FILE="${SCRIPT_DIR}/../references/conf.md"

# 从 conf.md 表格中读取指定 key 的值
read_conf() {
    local key="$1"
    grep "|\s*\`${key}\`\s*|" "$CONF_FILE" 2>/dev/null | \
        sed -E 's/.*\|\s*`[^`]*`\s*\|\s*`([^`]*)`\s*\|.*/\1/' | \
        sed 's/^[[:space:]]*//;s/[[:space:]]*$//'
}

# 通过 Secrets API 获取值
get_secret() {
    local key="$1"
    curl -sSf -X POST "${PAPERCLIP_API_URL}/api/agents/me/secrets/${key}/value" \
        -H "Authorization: Bearer ${PAPERCLIP_API_KEY}" \
        -H "Content-Type: application/json" | grep -o '"value":"[^"]*"' | sed 's/"value":"//;s/"//'
}

echo "正在获取账号密码..."
DEPLOY_ACCOUNT=$(get_secret "deploy-deploy_account")
DEPLOY_PASSWORD=$(get_secret "deploy-deploy_password")

[ -z "$DEPLOY_ACCOUNT" ] && { echo "无法获取 Secret deploy-deploy_account"; exit 1; }
[ -z "$DEPLOY_PASSWORD" ] && { echo "无法获取 Secret deploy-deploy_password"; exit 1; }

# 其余配置从 conf.md 读取
echo "从 $CONF_FILE 读取服务器配置..."
DEPLOY_IP=$(read_conf DEPLOY_IP)
DEPLOY_PORT=$(read_conf DEPLOY_PORT)
DEPLOY_REMOTE_BASE=$(read_conf DEPLOY_REMOTE_BASE)

[ -z "$DEPLOY_IP" ] && { echo "conf.md 中缺少 DEPLOY_IP"; exit 1; }
[ -z "$DEPLOY_PORT" ] && DEPLOY_PORT="22"
[ -z "$DEPLOY_REMOTE_BASE" ] && { echo "conf.md 中缺少 DEPLOY_REMOTE_BASE"; exit 1; }

LOCAL_PATH="$1"
PROJECT_NAME="$2"

if [ -z "$LOCAL_PATH" ] || [ -z "$PROJECT_NAME" ]; then
    echo "用法: ./deploy.sh <本地产物路径> <项目拼音首字母>"
    exit 1
fi

# 确保本地产物路径以 / 结尾
[[ "$LOCAL_PATH" != */ ]] && LOCAL_PATH="${LOCAL_PATH}/"

REMOTE="${DEPLOY_ACCOUNT}@${DEPLOY_IP}:${DEPLOY_REMOTE_BASE}/${PROJECT_NAME}/"

echo "正在部署到: ${REMOTE}"
sshpass -p "${DEPLOY_PASSWORD}" rsync -avz --delete --progress -e "ssh -p ${DEPLOY_PORT}" "${LOCAL_PATH}" "${REMOTE}"

echo "部署完成!"
