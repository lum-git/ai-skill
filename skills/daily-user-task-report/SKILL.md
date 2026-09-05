---
name: daily-user-task-report
description: >
  每日用户任务创建汇报。Use when asked to generate 每日用户任务创建汇报 / 用户任务创建日报 /
  统计今天用户创建的任务 / daily user task creation report. 统计今天所有真人用户（全部角色，仅排除
  系统账号）通过 Paperclip Web UI 人工创建的任务，覆盖 board 凭证可访问的全部公司，按创建人分组、
  组内按公司分组，生成 Markdown 日报（创建/完成/堵塞/评审中/完成率 + 任务明细），保存为任务评论 +
  Markdown 附件，并推送钉钉机器人（自定义 Webhook，关键词 ai）。
  Don't use for agent-created task statistics, routine execution issues, weekly summaries,
  or when asked to create/modify tasks.
---

# 每日用户任务创建汇报

## 目标

统计今天（Asia/Shanghai 时区 00:00:00 至当前时刻）由所有真人用户（全部角色，仅排除系统账号）通过 Paperclip Web UI 人工创建的任务，覆盖 board 凭证可访问的全部公司，按创建人分组、组内按公司分组，生成 Markdown 日报，保存为当前任务的评论 + Markdown 附件，并推送到钉钉机器人。

## 前置条件

1. 环境变量（由调用本技能的例程 Secrets 或 agent 环境变量提供；缺失时在当前任务评论中说明缺少哪个变量，然后停止执行）：
   - `BOARD_API_KEY`：Paperclip Board API Token（用于列出全部公司并跨公司查询数据；实例为本地免认证模式时可缺省，见"准备"第 3 条）；
   - `ACCESS_TOKEN`：钉钉机器人 access_token（自定义 Webhook 接入；安全设置为自定义关键词 `ai`，推送消息必须包含该关键词）。
2. API 基地址 `PAPERCLIP_API_URL`：你运行环境中的 Paperclip 实例地址（如 `http://localhost:3100`；Paperclip 运行时自动注入，缺失时在评论中说明后停止执行）。
3. 工具：curl 与 jq（环境缺失时用等价方式实现 HTTP 请求与 JSON 处理）。
4. 通用错误处理：调用 `GET /api/companies` 返回非 2xx（如 401/403）时，在当前任务评论中说明端点与 HTTP 状态码后停止执行；进入逐公司统计后，某公司的用户目录或任务列表获取失败时不要静默跳过——在报告与最终评论中明确标注该公司获取失败（公司名、端点、状态码），继续处理其余公司，不要用空数据伪装完整报告。

## 准备

1. 计算统计窗口（转为 UTC ISO 8601，API 的 `createdAt` 为 UTC）：

```bash
START_TIME=$(TZ=Asia/Shanghai date -d "today 00:00:00" -u +%Y-%m-%dT%H:%M:%SZ)   # 今天 00:00（上海）对应的 UTC
END_TIME=$(date -u +%Y-%m-%dT%H:%M:%SZ)                                          # 当前时刻
TODAY=$(TZ=Asia/Shanghai date +%F)                                               # 报告用日期 YYYY-MM-DD
```

2. 确定当前任务（你正在执行、调用本技能的 issue，可能是例程执行任务或手动分派的任务）的 `ISSUE_ID` 与其所属公司 `ISSUE_COMPANY_ID`（从你的运行上下文获取）。
3. 构造统一的请求凭证 `AUTH`，后续所有 Paperclip API 调用统一携带 `"${AUTH[@]}"`（已配置 `BOARD_API_KEY` 时携带 Bearer 头；未配置时不带 Authorization 头，适用于本地免认证实例。不要在 curl 命令中硬编码 `-H "Authorization: ..."`，否则变量为空时会发出空的 Bearer 头）：

```bash
if [ -n "${BOARD_API_KEY}" ]; then
  AUTH=(-H "Authorization: Bearer ${BOARD_API_KEY}")
else
  AUTH=()
fi
```

## 第 1 步：列出所有公司

```bash
curl -s "${AUTH[@]}" "${PAPERCLIP_API_URL}/api/companies"
```

从响应数组提取每个公司的 `id`、`name`，作为待遍历公司清单（若响应被 `{companies:[...]}` 包裹则先取 `.companies`；排除 `status = 'archived'` 的公司）。统计范围即该 board 凭证可访问的所有公司。

## 第 2 步：筛选应统计的用户（逐公司）

```bash
curl -s "${AUTH[@]}" \
  "${PAPERCLIP_API_URL}/api/companies/${COMPANY_ID}/user-directory"
```

处理规则：
- 统计所有真人用户，不再按角色过滤（角色规则 v5，2026-09-05：全部角色 owner/viewer/operator/admin 纳入统计，取代 v4/PAP-6827 的仅 Operator/Admin 口径）；
- 排除系统账号：`slug = 'local-board'` 或 `email = 'local@paperclip.local'`；
- 无需逐个调用 profile 查角色；若目录响应缺少姓名字段，再调 `GET /api/companies/${COMPANY_ID}/users/${SLUG}/profile` 补全（同样使用 `"${AUTH[@]}"`）；
- 产出数据：`USER_IDS`（该公司全部真人 userId JSON 数组，形如 `["usr_xxx","usr_yyy"]`）、`USER_NAMES`（userId → 真实姓名/email 映射，email 供第 4 步跨公司合并同一真人使用）。

## 第 3 步：查询今天人工创建的任务（逐公司）

```bash
curl -s "${AUTH[@]}" \
  "${PAPERCLIP_API_URL}/api/companies/${COMPANY_ID}/issues?limit=200"
```

返回条数等于 `limit` 时，追加 `&offset=200`（每次递增 200）继续拉取，直至取全。

对结果按以下条件过滤（jq 参考实现）：

```bash
curl -s "${AUTH[@]}" \
  "${PAPERCLIP_API_URL}/api/companies/${COMPANY_ID}/issues?limit=200" \
| jq --arg start "$START_TIME" --arg end "$END_TIME" --argjson users "$USER_IDS" '
    [.[] | select(
        .createdByUserId != null
        and .createdByAgentId == null
        and .originKind != "routine_execution"
        and .createdAt >= $start
        and .createdAt <= $end
        and (.createdByUserId | IN($users[]))
      )]'
```

铁律：
- 绝对不要把 agent 创建的任务（routine execution、recovery 子任务、子 agent 自动 issue）混进报告；
- 绝对不要把系统账号（local-board）创建的任务混进报告；owner / viewer / operator / admin 等所有真人角色创建的任务均正常统计。

## 第 4 步：统计并生成报告

数据组织：按创建人分组，同一用户的任务再按公司分组。跨公司识别同一真人：email 相同的用户合并为同一用户（email 缺失时按姓名匹配），用户级指标为跨公司合计；某公司无符合条件任务时，该公司不出现在该用户名下。

每个用户级与公司级各计算一组指标：
- 创建总数（该范围内全部任务，不限状态）；
- 完成数：`status = 'done'`；
- 堵塞数：`status = 'blocked'`；
- 评审中数：`status = 'in_review'`；
- 完成率 = 完成数 ÷ 创建总数 × 100%（保留 1 位小数；创建总数为 0 的用户不出现）。

每个任务输出一行，含三个要素：
- 任务名称：`title`（附 `identifier`，如 PAP-39）；
- 耗时：`status = 'done'` 时取 `completedAt - createdAt`；其他状态取"当前时刻 - createdAt"；格式化为"X 小时 Y 分钟"（不足 1 小时显示"Y 分钟"）；若列表响应未包含 `completedAt`，对 done 任务先调 `GET /api/issues/{issueId}`（带 `"${AUTH[@]}"`）补全该字段再计算；
- 完成情况：done=已完成、in_progress=进行中、in_review=评审中、blocked=已堵塞、todo=待办、backlog=积压、cancelled=已取消。

报告 Markdown 格式（严格按此模板）：

```
# 用户任务创建日报（YYYY-MM-DD）

## {用户姓名}：创建任务 X 个，完成 X 个，堵塞 X 个，评审中 X 个，完成率 X%

### {公司名称}：创建任务 X 个，完成 X 个，堵塞 X 个，评审中 X 个，完成率 X%

- **{任务名称}（{identifier}）** ｜ 耗时 X 小时 Y 分钟 ｜ {完成情况}
- **{任务名称}（{identifier}）** ｜ 耗时 X 小时 Y 分钟 ｜ {完成情况}

（下一个公司、下一个用户依同样格式继续；某用户只在一个公司有任务时也保留公司层级标题）
```

## 第 5 步：保存报告到当前任务

"当前任务"指你正在执行、调用本技能的 issue。设报告全文存于变量 `REPORT`。

```bash
# 5.1 发布评论（用 jq 构造请求体，避免转义问题）
curl -s -X POST \
  "${AUTH[@]}" -H "Content-Type: application/json" \
  -d "$(jq -n --arg body "$REPORT" '{body: $body}')" \
  "${PAPERCLIP_API_URL}/api/issues/${ISSUE_ID}/comments"

# 5.2 写入本地文件并上传为附件（multipart/form-data，文件字段名 file）
printf '%s' "$REPORT" > "用户任务创建日报-${TODAY}.md"
curl -s -X POST \
  "${AUTH[@]}" \
  -F "file=@用户任务创建日报-${TODAY}.md;type=text/markdown" \
  "${PAPERCLIP_API_URL}/api/companies/${ISSUE_COMPANY_ID}/issues/${ISSUE_ID}/attachments"
rm -f "用户任务创建日报-${TODAY}.md"   # 上传后清理，避免工作区文件堆积
```

## 第 6 步：推送钉钉（自定义 Webhook，关键词校验）

```bash
REPORT_TEXT="${REPORT}

> 本日报由 ai 例程机器人自动推送"

curl -s -X POST \
  -H "Content-Type: application/json" \
  -d "$(jq -n --arg title "ai日报｜用户任务创建 ${TODAY}" --arg text "$REPORT_TEXT" \
        '{msgtype: "markdown", markdown: {title: $title, text: $text}}')" \
  "https://oapi.dingtalk.com/robot/send?access_token=${ACCESS_TOKEN}"
```

成功判定：HTTP 200 且响应 `errcode == 0`（形如 `{"errcode":0,"errmsg":"ok"}`）。

关键词规则（重要）：
- 该机器人安全设置为自定义关键词 `ai`：消息的 `title` 与 `text` 都必须包含 `ai` 才会被钉钉接收，否则返回 errcode 310000；
- 因此 `title` 固定为 `ai日报｜用户任务创建 ${TODAY}`，`text` 末尾固定追加署名行（见上方 `REPORT_TEXT` 的构造）；
- 若机器人实际配置的关键词大小写不同（如 `AI`），以机器人配置为准同步替换上述两处关键词。

注意：
- 钉钉 markdown 消息有长度上限，若报告全文超过约 20000 字符，`text` 只保留各用户的汇总行（含公司级汇总）与末尾署名行，并追加一行"完整任务明细见 Paperclip 附件"；
- 推送返回 errcode 310000 时，先检查 `title` / `text` 是否遗漏关键词 `ai`，修正后重发；
- 其他失败最多重试 2 次，仍失败则在当前任务评论中补充说明"钉钉推送失败：{errcode 与 errmsg}"。

## 空数据场景

今天所有公司均无符合条件的任务时：
- `REPORT` 内容为："今日无用户创建任务（${TODAY}）"；
- 跳过附件上传（第 5.2 步），仅执行第 5.1 步发布评论；
- 钉钉推送照常执行：title 为"ai日报｜用户任务创建 ${TODAY}"，text 为"今日无用户创建任务"+ 末尾署名行（满足关键词 `ai` 要求）。

## 收尾

报告保存与推送全部完成后，将当前任务状态置为 `done`：

```bash
curl -s -X PATCH \
  "${AUTH[@]}" -H "Content-Type: application/json" \
  -d '{"status":"done","comment":"日报已生成、保存并推送完成"}' \
  "${PAPERCLIP_API_URL}/api/issues/${ISSUE_ID}"
```
