# 项目记忆：Skill 创建规范（来源：Paperclip 官方文档）

> 来源：https://docs.paperclip.ing/reference/skills/ （2026-09 分析）
> 本项目（ai-skill）的 `skills/` 目录遵循同一套 Skill 文件体系，新增/修改技能时遵守以下规范。

## 1. Skill 文件结构

一个 Skill = 一个包含 `SKILL.md` 的文件夹：

```
my-skill/
├── SKILL.md          # 必需，唯一核心文件
├── references/       # 可选，参考文档（markdown only）
├── scripts/          # 可选，可执行脚本
└── assets/           # 可选，静态资源
```

三个子目录会被自动识别并分类（classifyInventoryKind）：

| 目录 | 库存类型 | 信任级别贡献 |
|---|---|---|
| `references/` | 参考文档 | 仅 markdown |
| `scripts/` | 脚本/可执行 | 可执行 |
| `assets/` | 静态资源 | 资源 |

**信任级别**（由库存中最高分类决定）：`markdown_only < assets < scripts_executables`

特殊模式：`SKILL.md` 位于仓库根目录时启用 `project_root` 库存模式，只遍历 `references/`、`scripts/`、`assets/`，不吞整个仓库。

## 2. SKILL.md 格式 = YAML frontmatter + Markdown 正文

```yaml
---
name: code-review              # 推荐：人类可读标签，缺省回退到 slug
description: >                 # 推荐：路由逻辑，Agent 判断是否激活此技能的依据
  Use when asked to review a pull request.
  Don't use when writing new code from scratch.
slug: code-review               # 可选：稳定 kebab-case 标识符（缺省由 name 或文件夹名派生）
key: my-key                     # 可选：规范键覆盖（解决命名冲突）
metadata:                       # 可选：任意元数据（其余字段原样透传）
  sourceKind: github            # paperclip_bundled/github/skills_sh/url/local_path 等
  owner: xxx                    # GitHub 坐标，用于更新检查
  repo: yyy
---

# 正文（Markdown）
```

### 关键限制与最佳实践

- frontmatter 由极简 YAML 解析器解析：**只支持扁平标量、嵌套对象、列表字面量，不支持完整 YAML 语法**
- `description` 是**路由逻辑**：Agent 首先读它决定是否使用技能，必须写清"何时用 / 何时不用"（正向 + 负向触发条件）
- 正文无长度限制，但技能被判定相关后**整个正文载入上下文** → 正文保持简短，长内容放 `references/` 支撑文件

### 识别的 metadata 子字段

- `skillKey` / `canonicalKey` / `paperclip.skillKey`：跨导入携带规范键
- `sourceKind`：来源类型枚举
- `sources[]`：来源描述符列表（kind/repo/path/commit/trackingRef/hostname/url 等）
- `owner` / `repo` / `ref` / `trackingRef`：GitHub 坐标，用于更新检查

## 3. 安装与分发（了解即可，本地开发不涉及）

- 技能安装在**公司级**（company level），安装后公司内任意 Agent 可被分配
- 导入源灵活：GitHub 仓库/子目录/blob URL、`owner/repo` 简写、skills.sh URL、`npx skills add` 命令、裸 URL、本地路径（单文件/单技能/多技能文件夹均可）
- 项目扫描识别 30+ 约定目录：`skills/`、`.claude/skills/`、`.trae/skills/`、`.cursor/`、`.windsurf/skills/` 等
- 存储规则：可编辑技能写入 `<instanceRoot>/skills/{companyId}/<slug>/`；只读源正文存数据库；内置技能每次重新导入，不可编辑删除

## 4. 核心设计理念

1. **单一入口文件**：`SKILL.md` 是技能的心脏，frontmatter 提供元数据，正文提供指令
2. **上下文经济学**：正文全量载入 → 强制"短正文 + references 支撑文件"的结构纪律
3. **声明式信任模型**：目录结构即信任声明，系统自动推导风险等级
4. **description 即路由**：写好 description 等于写好 Agent 的技能选择逻辑

## 5. 本仓库硬性约束：禁止提交可执行文件（当前方案）

**技能仓库不允许 `.py`、`.sh` 等可执行文件入库**（对应 Paperclip 信任模型：技能保持 `markdown_only` 信任级别，避免升级为 `scripts_executables`）。当前项目的解决方案：

### 5.1 脚本以 `.md` 后缀存放，解释器直接执行

- 脚本源码放 `references/source/<name>.py.md`，**内容是纯源码**（含 shebang 和 docstring，不包 markdown 代码块围栏）
- Python 解释器不检查文件扩展名 → `python references/source/deploy.py.md <参数>` **直接执行，无需复制或重命名**
- 脚本头部 docstring 必须写明：用法、示例、依赖（如 `pip install paramiko`）、`.md` 后缀原因
- 范本：`skills/sales-project-deploy/references/source/deploy.py.md`；Shell 脚本同理存 `.sh.md`，用 `bash xxx.sh.md` 执行
- SKILL.md 正文中写明直接执行命令，并解释"源码以 .md 后缀存放（技能仓库不允许 .py 文件）"

### 5.2 配置与敏感信息的存放方式

| 内容类型 | 存放位置 | 说明 |
|---|---|---|
| 非敏感配置（IP/端口/路径/地图 Key） | `references/conf.md` 或 `references/config.md` | markdown 表格（`` `KEY` \| `value` ``）或 `KEY=value` 行；脚本内用正则解析（`read_conf`，按 `__file__` 相对路径定位） |
| 账号密码等凭据 | Paperclip Secrets API 运行时获取 | `POST {PAPERCLIP_API_URL}/api/agents/me/secrets/{key}/value`（Bearer 认证），**不落盘** |
| 公司资料/业务数据 | 项目侧目录（如 `bid-data/`） | **skill 内不放任何公司数据**，只放规范和模板；项目数据按固定目录规则读取 |

### 5.3 该方案的优势

- 全仓库均为 markdown 文档 → 所有技能信任级别保持 `markdown_only`（最低风险等级）
- 无需"复制/重命名"中间步骤，Agent 执行路径最短
- 脚本迭代走正常文档提交流程，无额外权限

## 6. 本项目落地约定

新建技能时遵守：

1. 新技能放 `skills/<kebab-case-name>/SKILL.md`，至少包含 frontmatter 的 `name` + `description`（含正向/负向触发条件）
2. 正文保持简短：只写能力说明、执行步骤、关键约束、检查清单；长内容拆到 `references/*.md` 并在正文中引用
3. **禁止提交任何可执行文件**（.py/.sh/.exe 等）：脚本一律按 §5.1 以 `.md` 后缀存放 `references/source/`，并在 SKILL.md 中写明直接执行命令
4. 配置按 §5.2 拆分：非敏感配置进 `references/conf.md`，凭据走 Secrets API 不落盘，公司数据放项目侧目录
5. 新增技能后同步更新根目录 `README.md` 和 `CLAUDE.md` 的技能索引表
