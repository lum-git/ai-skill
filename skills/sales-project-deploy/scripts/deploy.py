#!/usr/bin/env python3
"""销售项目部署脚本
用法: python deploy.py <本地产物路径> <项目拼音首字母>
账号密码通过 Paperclip Secrets API 获取
"""

import os
import sys
import re
import urllib.request
import urllib.error
import json
import subprocess

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONF_FILE = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "references", "conf.md"))


def read_conf(key: str) -> str:
    """从 conf.md 表格中读取指定 key 的值"""
    try:
        with open(CONF_FILE, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        return ""
    pattern = rf"\|\s*`{re.escape(key)}`\s*\|\s*`([^`]*)`\s*\|"
    m = re.search(pattern, content)
    if m:
        return m.group(1).strip()
    return ""


def get_secret(key: str) -> str:
    """通过 Secrets API 获取值"""
    api_url = os.environ.get("PAPERCLIP_API_URL", "")
    api_key = os.environ.get("PAPERCLIP_API_KEY", "")
    if not api_url or not api_key:
        print("缺少 PAPERCLIP_API_URL 或 PAPERCLIP_API_KEY 环境变量")
        return ""

    url = f"{api_url}/api/agents/me/secrets/{key}/value"
    req = urllib.request.Request(url, method="POST")
    req.add_header("Authorization", f"Bearer {api_key}")
    req.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            return data.get("value", "")
    except urllib.error.URLError as e:
        print(f"获取 Secret {key} 失败: {e}")
        return ""


def main():
    if len(sys.argv) < 3:
        print("用法: python deploy.py <本地产物路径> <项目拼音首字母>")
        sys.exit(1)

    local_path = sys.argv[1]
    project_name = sys.argv[2]

    # 本地产物路径确保以 / 结尾
    if not local_path.endswith("/") and not local_path.endswith("\\"):
        local_path += "/"
    # 统一为正斜杠（rsync 兼容）
    local_path = local_path.replace("\\", "/")

    print("正在获取账号密码...")
    deploy_account = get_secret("deploy-deploy_account")
    deploy_password = get_secret("deploy-deploy_password")

    if not deploy_account:
        print("无法获取 Secret deploy-deploy_account")
        sys.exit(1)
    if not deploy_password:
        print("无法获取 Secret deploy-deploy_password")
        sys.exit(1)

    print(f"从 {CONF_FILE} 读取服务器配置...")
    deploy_ip = read_conf("DEPLOY_IP")
    deploy_port = read_conf("DEPLOY_PORT") or "22"
    deploy_remote_base = read_conf("DEPLOY_REMOTE_BASE")

    if not deploy_ip:
        print("conf.md 中缺少 DEPLOY_IP")
        sys.exit(1)
    if not deploy_remote_base:
        print("conf.md 中缺少 DEPLOY_REMOTE_BASE")
        sys.exit(1)

    remote = f"{deploy_account}@{deploy_ip}:{deploy_remote_base}/{project_name}/"

    print(f"正在部署到: {remote}")
    cmd = [
        "sshpass", "-p", deploy_password,
        "rsync", "-avz", "--delete", "--progress",
        "-e", f"ssh -p {deploy_port}",
        local_path, remote
    ]
    result = subprocess.run(cmd)
    if result.returncode == 0:
        print("部署完成!")
    else:
        print(f"部署失败，退出码: {result.returncode}")
        sys.exit(result.returncode)


if __name__ == "__main__":
    main()
