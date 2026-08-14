#!/usr/bin/env python3
"""销售项目部署脚本（纯 Python，等同于 rsync -avz --delete --progress）
用法:
  python deploy.py <本地产物路径> <当前任务id>
  示例: python deploy.py ./dist HYSQZC-971

依赖: pip install paramiko
账号密码通过 Paperclip Secrets API 获取
"""

import os
import sys
import re
import stat as stat_module
import tarfile
import io
import urllib.request
import urllib.error
import json
import time
from pathlib import Path

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


def format_size(size_bytes: int) -> str:
    for unit in ["B", "KB", "MB", "GB"]:
        if abs(size_bytes) < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def walk_local(local_root: str):
    """遍历本地目录，返回 (相对路径, 本地绝对路径, 文件大小) 列表"""
    result = []
    for dirpath, dirnames, filenames in os.walk(local_root):
        rel_dir = os.path.relpath(dirpath, local_root)
        if rel_dir == ".":
            rel_dir = ""
        for fname in filenames:
            rel = os.path.join(rel_dir, fname).replace("\\", "/")
            local = os.path.join(dirpath, fname)
            result.append((rel, local, os.path.getsize(local)))
    return result


# ========================== SFTP 方式 ==========================

def ensure_remote_dir_sftp(sftp, remote_dir: str):
    """递归创建远程目录 (SFTP)"""
    parts = remote_dir.replace("\\", "/").strip("/").split("/")
    current = ""
    for part in parts:
        current += "/" + part
        try:
            sftp.stat(current)
        except FileNotFoundError:
            sftp.mkdir(current)


def walk_remote_sftp(sftp, remote_root: str):
    """遍历远程目录 (SFTP)，返回 {相对路径: SFTPAttributes}"""
    files = {}
    try:
        items = sftp.listdir_attr(remote_root)
    except FileNotFoundError:
        return files

    for item in items:
        item_path = f"{remote_root.rstrip('/')}/{item.filename}"
        if stat_module.S_ISDIR(item.st_mode):
            files.update(walk_remote_sftp(sftp, item_path))
        else:
            rel = item_path[len(remote_root.rstrip("/")) + 1:]
            files[rel.replace("\\", "/")] = item
    return files


def collect_remote_dirs_sftp(sftp, remote_root: str) -> set:
    """遍历远程子目录 (SFTP)"""
    dirs = set()
    try:
        items = sftp.listdir_attr(remote_root)
    except FileNotFoundError:
        return dirs

    for item in items:
        item_path = f"{remote_root.rstrip('/')}/{item.filename}"
        if stat_module.S_ISDIR(item.st_mode):
            dirs.add(item_path)
            dirs.update(collect_remote_dirs_sftp(sftp, item_path))
    return dirs


def sftp_upload(sftp, local_path: str, remote_path: str, callback=None):
    """上传单个文件 (SFTP)，保留时间戳和权限"""
    sftp.put(local_path, remote_path, confirm=True, callback=callback)
    local_stat = os.stat(local_path)
    try:
        sftp.utime(remote_path, (local_stat.st_atime, local_stat.st_mtime))
    except Exception:
        pass
    try:
        sftp.chmod(remote_path, local_stat.st_mode & 0o777)
    except Exception:
        pass


# ========================== SSH TAR 方式（SFTP 不可用时的回退） ==========================

def ssh_exec(ssh, cmd: str) -> tuple:
    """通过 SSH 执行命令，返回 (stdout, stderr)"""
    stdin, stdout, stderr = ssh.exec_command(cmd)
    return stdout.read().decode(errors="replace"), stderr.read().decode(errors="replace")


def walk_remote_ssh(ssh, remote_root: str):
    """遍历远程目录 (SSH + find)，返回 {相对路径: 文件大小}"""
    files = {}
    remote_root = remote_root.rstrip("/")
    cmd = (
        "find '" + remote_root + "' -type f -printf '%s %P\\n' 2>/dev/null || "
        "find '" + remote_root + "' -type f | while read f; do "
        "  size=$(stat -c%s \"$f\" 2>/dev/null || stat -f%z \"$f\" 2>/dev/null); "
        "  echo \"$size ${f#" + remote_root + "/}\"; "
        "done"
    )
    out, err = ssh_exec(ssh, cmd)
    for line in out.strip().split("\n"):
        line = line.strip()
        if not line:
            continue
        parts = line.split(" ", 1)
        if len(parts) == 2:
            try:
                size = int(parts[0])
                rel = parts[1]
                files[rel] = size
            except ValueError:
                pass
    return files


def ssh_ensure_remote_dir(ssh, remote_dir: str):
    """通过 SSH 创建远程目录"""
    ssh_exec(ssh, f"mkdir -p '{remote_dir}'")


def ssh_remove_file(ssh, remote_file: str):
    ssh_exec(ssh, f"rm -f '{remote_file}'")


def ssh_remove_dir(ssh, remote_dir: str):
    ssh_exec(ssh, f"rmdir '{remote_dir}' 2>/dev/null")


def ssh_tar_upload(ssh, local_files: list, local_root: str, remote_root: str,
                   progress_cb=None):
    """通过 tar + SSH pipe 批量上传文件（等同 rsync --delete 后的全量同步）"""
    start = time.time()
    total_bytes = sum(size for _, _, size in local_files)

    # 清除远程旧内容
    ssh_exec(ssh, f"rm -rf '{remote_root}'/*")
    ssh_exec(ssh, f"mkdir -p '{remote_root}'")

    # 创建 tar 流并通过 SSH pipe 解压
    tar_buf = io.BytesIO()
    with tarfile.open(fileobj=tar_buf, mode="w:gz") as tar:
        for rel, local_file, _ in local_files:
            arcname = rel.replace("\\", "/")
            tar.add(local_file, arcname=arcname)

    tar_data = tar_buf.getvalue()
    compressed_size = len(tar_data)

    print(f"  tar 包: {format_size(compressed_size)} (原始 {format_size(total_bytes)})")
    print(f"  正在通过 SSH pipe 传输...")

    transport = ssh.get_transport()
    channel = transport.open_session()
    channel.exec_command(f"tar xzf - -C '{remote_root}'")

    # 分块写入并显示进度
    chunk_size = 65536
    sent = 0
    last_pct = -1
    for offset in range(0, len(tar_data), chunk_size):
        chunk = tar_data[offset:offset + chunk_size]
        channel.send(chunk)
        sent += len(chunk)
        pct = int(sent * 100 / len(tar_data))
        if pct - last_pct >= 5 or pct == 100:
            bar = "█" * (pct // 5) + "░" * (20 - pct // 5)
            print(f"\r  {bar} {pct:3d}%  {format_size(sent)}/{format_size(compressed_size)}", end="")
            last_pct = pct

    channel.shutdown_write()
    channel.recv_exit_status()
    channel.close()
    print()

    elapsed = time.time() - start
    print(f"  总耗时: {elapsed:.1f}s, 平均: {format_size(int(total_bytes / elapsed))}/s")


# ========================== 统一部署入口 ==========================

def deploy_sync(host: str, port: int, user: str, password: str,
                local_path: str, remote_path: str):
    """部署，自动选择 SFTP 或 tar+SSH pipe"""
    import paramiko

    print(f"正在连接 {user}@{host}:{port} ...")

    transport = paramiko.Transport((host, port))
    transport.use_compression(True)
    transport.connect(username=user, password=password)
    ssh = paramiko.SSHClient()
    ssh._transport = transport

    # 尝试 SFTP
    sftp = None
    use_sftp = False
    try:
        sftp = paramiko.SFTPClient.from_transport(transport)
        sftp.listdir("/")  # 快速验证 SFTP 是否可用
        use_sftp = True
        print("  传输方式: SFTP")
    except Exception as e:
        print(f"  SFTP 不可用 ({e})，回退到 tar+SSH pipe 方式")

    local_root = local_path.rstrip("/").rstrip("\\")
    remote_root = remote_path.rstrip("/")
    local_files = walk_local(local_root)

    # --- 获取远程文件列表 ---
    if use_sftp:
        print(f"确保远程目录存在: {remote_path}")
        ensure_remote_dir_sftp(sftp, remote_path)
        remote_files = walk_remote_sftp(sftp, remote_root)
        remote_map = {rel: (item.st_size if hasattr(item, 'st_size') else 0)
                      for rel, item in remote_files.items()}
    else:
        # 用 SSH 先创建目录
        ssh_ensure_remote_dir(ssh, remote_path)
        remote_map = walk_remote_ssh(ssh, remote_root)

    # --- 对比分析 ---
    local_set = {f[0] for f in local_files}
    remote_set = set(remote_map.keys())

    to_delete = remote_set - local_set
    to_upload = []
    to_skip = []
    for rel, local_file, size in local_files:
        if rel in remote_map and remote_map[rel] == size:
            to_skip.append((rel, size))
        else:
            to_upload.append((rel, local_file, size))

    # --- 差异输出 ---
    print()
    if to_delete:
        print(f"删除远程多余文件 ({len(to_delete)}):")
        for rel in sorted(to_delete):
            ds = format_size(remote_map[rel])
            print(f"    - {rel}  ({ds})")
    if to_upload:
        total_up = sum(f[2] for f in to_upload)
        print(f"上传/更新文件 ({len(to_upload)}, {format_size(total_up)}):")
        for rel, local_file, size in to_upload:
            marker = "U" if rel in remote_map else "+"
            print(f"    {marker} {rel}  ({format_size(size)})")
    if to_skip:
        total_skip = sum(f[1] for f in to_skip)
        print(f"跳过 (未变化): {len(to_skip)} 个文件, {format_size(total_skip)}")
    if not to_delete and not to_upload:
        print(f"所有文件已是最新，无需操作。")
        if sftp:
            sftp.close()
        transport.close()
        return

    # --- 实际执行 ---
    if use_sftp:
        # 删除远程多余文件
        for rel in sorted(to_delete):
            rf = f"{remote_root}/{rel}"
            print(f"  删除: {rel}")
            sftp.remove(rf)

        # 清理空目录
        remote_dirs = collect_remote_dirs_sftp(sftp, remote_root)
        for d in sorted(remote_dirs, key=lambda x: x.count("/"), reverse=True):
            d_rel = d[len(remote_root) + 1:]
            if not any(f.startswith(d_rel + "/") for f in local_set):
                try:
                    sftp.rmdir(d)
                except OSError:
                    pass

        # 上传
        if to_upload:
            print(f"\n正在上传 {len(to_upload)} 个文件...")
            start = time.time()
            total_bytes = 0
            for i, (rel, local_file, size) in enumerate(to_upload, 1):
                remote_file = f"{remote_root}/{rel}".replace("\\", "/")
                ensure_remote_dir_sftp(sftp, os.path.dirname(remote_file))

                transferred = [0]
                last_pct = [-1]

                def progress_cb(tb, total_inner):
                    transferred[0] = tb
                    if total_inner:
                        pct = int(tb * 100 / total_inner)
                        if pct - last_pct[0] >= 10 or pct == 100:
                            bar = "█" * (pct // 5) + "░" * (20 - pct // 5)
                            print(f"\r  [{i}/{len(to_upload)}] {rel[:50]}  {bar} {pct:3d}%  {format_size(tb)}/{format_size(total_inner)}", end="")
                            last_pct[0] = pct

                if size > 0:
                    sftp_upload(sftp, local_file, remote_file, callback=progress_cb)
                    print()
                else:
                    sftp_upload(sftp, local_file, remote_file)
                    print(f"  [{i}/{len(to_upload)}] {rel[:50]}  (空文件)")
                total_bytes += size

            elapsed = time.time() - start
            print(f"  总耗时: {elapsed:.1f}s, 平均: {format_size(int(total_bytes / elapsed))}/s")
    else:
        # --- SSH tar pipe 方式 ---
        # 删除远程多余文件
        for rel in sorted(to_delete):
            rf = f"{remote_root}/{rel}"
            print(f"  删除: {rel}")
            ssh_remove_file(ssh, rf)

        # 全量上传（tar pipe 一次性搞定所有文件）
        if to_upload:
            print(f"\n正在通过 tar+SSH pipe 传输 {len(to_upload)} 个文件...")
            # 先删除旧内容（等同于 --delete）
            ssh_exec(ssh, f"rm -rf '{remote_root}'/*")
            ssh_exec(ssh, f"mkdir -p '{remote_root}'")
            ssh_tar_upload(ssh, to_upload, local_root, remote_root)

    # 汇总
    total_up = sum(f[2] for f in to_upload)
    total_del = sum(remote_map[r] for r in to_delete)
    print(f"\n{'='*50}")
    print(f"部署完成!")
    print(f"  上传: {len(to_upload)} 个文件 ({format_size(total_up)})")
    print(f"  删除: {len(to_delete)} 个远程文件 ({format_size(total_del)})")
    print(f"  跳过: {len(to_skip)} 个文件(未变化)")
    print(f"{'='*50}")

    if sftp:
        sftp.close()
    transport.close()


# ========================== 入口 ==========================

def main():
    if len(sys.argv) < 3:
        print("用法: python deploy.py <本地产物路径> <当前任务id>")
        sys.exit(1)

    local_path = sys.argv[1]
    task_id = sys.argv[2]

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
    deploy_port = int(read_conf("DEPLOY_PORT") or "22")
    deploy_remote_base = read_conf("DEPLOY_REMOTE_BASE")

    if not deploy_ip:
        print("conf.md 中缺少 DEPLOY_IP")
        sys.exit(1)
    if not deploy_remote_base:
        print("conf.md 中缺少 DEPLOY_REMOTE_BASE")
        sys.exit(1)

    remote_path = f"{deploy_remote_base.rstrip('/')}/{task_id}"
    print(f"目标: {deploy_account}@{deploy_ip}:{deploy_port} → {remote_path}")

    deploy_sync(
        host=deploy_ip,
        port=deploy_port,
        user=deploy_account,
        password=deploy_password,
        local_path=local_path,
        remote_path=remote_path,
    )

    # 输出访问地址
    url_base = read_conf("URL_BASE") or f"http://{deploy_ip}/"
    url = f"{url_base.rstrip('/')}/{task_id}/"
    print(f"\n访问地址: {url}")


if __name__ == "__main__":
    main()
