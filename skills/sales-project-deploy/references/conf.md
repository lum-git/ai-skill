# 销售项目部署配置

> 账号密码通过 Secrets API 实时获取，不在文件中存储。

| 配置项 | 值 | 说明 |
|--------|-----|------|
| `DEPLOY_IP` | `192.168.1.10` | 远程服务器 IP |
| `DEPLOY_PORT` | `22` | SSH 端口 |
| `DEPLOY_REMOTE_BASE` | `/volume1/nginx/nginx-www/salesProject` | 远程部署路径 |
| `URL_BASE` | `http://192.168.1.10/` | 访问地址前缀，部署后拼接 `{项目拼音}/` |

## 关联的 Secret

脚本通过 `POST /api/agents/me/secrets/{key}/value` 获取：

| Secret Key | 用途 |
|------------|------|
| `deploy-deploy_account` | 服务器登录账号 |
| `deploy-deploy_password` | 服务器登录密码 |
