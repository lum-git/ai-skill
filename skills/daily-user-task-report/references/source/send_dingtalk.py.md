#!/usr/bin/env python3
"""钉钉自定义机器人群消息推送脚本（daily-user-task-report 技能专用）

用法:
  python send_dingtalk.py.md --access_token TOKEN --msgtype markdown --title "ai日报｜用户任务创建 2026-09-05" --text "消息正文..."
  python send_dingtalk.py.md --access_token TOKEN --msgtype markdown --title "..." --text-file 用户任务创建日报-2026-09-05.md
  python send_dingtalk.py.md --access_token TOKEN --secret SECxxx --msgtype markdown --title "..." --text "..."   # 加签模式

参数:
  --access_token  必填，机器人 Webhook 的 access_token
  --secret        可选，加签密钥（机器人安全设置为"加签"时必传；自定义关键词模式不传，
                  脚本自动按官方算法计算 timestamp 与 sign 并追加到 Webhook）
  --msgtype       text 或 markdown，默认 text
  --title         markdown 消息必填，会话列表展示的标题（建议包含安全关键词）
  --text          消息正文（与 --text-file 二选一，--text 优先）
  --text-file     从文件读取消息正文（长内容推荐，避免命令行转义与长度限制）
  --msg           --text 的别名
  --userid        待 @ 的钉钉用户ID，多个用逗号分隔
  --at_mobiles    待 @ 的手机号，多个用逗号分隔
  --is_at_all     @所有人
  --msg-uuid      消息幂等 key（官方 msgUuid：重试时复用同一个值，避免重复发消息）

说明: 本文件以 .md 后缀存放。
     Python 解释器不检查扩展名，可直接执行，无需重命名（技能仓库不允许 .py 文件入库，
     保持 markdown_only 信任级别）。

依赖: pip install requests

退出码: 0 成功；1 参数或文件错误；2 钉钉请求失败或 errcode != 0
"""

import argparse
import base64
import hashlib
import hmac
import sys
import time
import urllib.parse

import requests


def parse_args():
    parser = argparse.ArgumentParser(description="钉钉自定义机器人群消息推送")
    parser.add_argument("--access_token", dest="access_token", required=True,
                        help="机器人 Webhook 的 access_token")
    parser.add_argument("--secret", dest="secret", default=None,
                        help="加签密钥（机器人安全设置为加签时必传；关键词模式不传）")
    parser.add_argument("--msgtype", dest="msgtype", choices=["text", "markdown"], default="text",
                        help="消息类型：text 或 markdown，默认 text")
    parser.add_argument("--title", dest="title", default=None,
                        help="markdown 消息的标题（会话列表展示，建议包含安全关键词）")
    parser.add_argument("--text", "--msg", dest="text", default=None,
                        help="消息正文")
    parser.add_argument("--text-file", dest="text_file", default=None,
                        help="从文件读取消息正文（与 --text 二选一，--text 优先）")
    parser.add_argument("--userid", dest="userid", default=None,
                        help="待 @ 的钉钉用户ID，多个用逗号分隔")
    parser.add_argument("--at_mobiles", dest="at_mobiles", default=None,
                        help="待 @ 的手机号，多个用逗号分隔")
    parser.add_argument("--is_at_all", dest="is_at_all", action="store_true",
                        help="是否 @ 所有人")
    parser.add_argument("--msg-uuid", dest="msg_uuid", default=None,
                        help="消息幂等 key，重试时复用同一个值")
    return parser.parse_args()


def build_webhook(access_token, secret=None):
    """构造 Webhook URL；secret 存在时按官方算法追加 timestamp 与 sign。"""
    url = "https://oapi.dingtalk.com/robot/send?access_token=%s" % access_token
    if secret:
        timestamp = str(round(time.time() * 1000))
        string_to_sign = "%s\n%s" % (timestamp, secret)
        hmac_code = hmac.new(secret.encode("utf-8"),
                             string_to_sign.encode("utf-8"),
                             digestmod=hashlib.sha256).digest()
        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
        url += "&timestamp=%s&sign=%s" % (timestamp, sign)
    return url


def main():
    args = parse_args()

    # 正文：--text 优先，其次 --text-file
    text = args.text
    if text is None and args.text_file is not None:
        try:
            with open(args.text_file, "r", encoding="utf-8") as f:
                text = f.read()
        except OSError as e:
            print("读取正文文件失败：%s" % e, file=sys.stderr)
            sys.exit(1)
    if not text:
        print("缺少消息正文：请用 --text 或 --text-file 指定", file=sys.stderr)
        sys.exit(1)

    at = {
        "isAtAll": bool(args.is_at_all),
        "atUserIds": [u.strip() for u in (args.userid or "").split(",") if u.strip()],
        "atMobiles": [m.strip() for m in (args.at_mobiles or "").split(",") if m.strip()],
    }

    if args.msgtype == "markdown":
        if not args.title:
            print("markdown 消息需要 --title", file=sys.stderr)
            sys.exit(1)
        body = {
            "msgtype": "markdown",
            "markdown": {"title": args.title, "text": text},
            "at": at,
        }
    else:
        body = {
            "msgtype": "text",
            "text": {"content": text},
            "at": at,
        }
    if args.msg_uuid:
        body["msgUuid"] = args.msg_uuid

    url = build_webhook(args.access_token, args.secret)
    try:
        resp = requests.post(url, json=body,
                             headers={"Content-Type": "application/json"}, timeout=15)
    except requests.RequestException as e:
        print("钉钉请求失败：%s" % e, file=sys.stderr)
        sys.exit(2)

    print(resp.text)
    try:
        result = resp.json()
    except ValueError:
        print("钉钉返回非 JSON 响应（HTTP %s）" % resp.status_code, file=sys.stderr)
        sys.exit(2)
    if resp.status_code != 200 or result.get("errcode") != 0:
        print("钉钉推送失败：HTTP %s errcode=%s errmsg=%s"
              % (resp.status_code, result.get("errcode"), result.get("errmsg")),
              file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
