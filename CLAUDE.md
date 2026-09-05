# CLAUDE.md - AI Skill 技能集合

> 本文件为 AI 辅助开发工作流提供项目规范和 Skill 使用指南。

---

## 项目概述

基于 Skill 文档体系的 **AI 技能集合**，目前包含两套技能：原型 HTML 项目生成器（根据需求自动生成后台管理系统原型，内置三套主题风格）和销售项目部署（通过 paramiko 将构建产物部署到公司内网 Nginx 服务器）。

**技术栈**: HTML5 + Bootstrap 5.3 + Bootstrap Icons 1.13 + Vanilla JS / Python + paramiko

---

## Skill 索引

| Skill | 路径 | 说明 |
|-------|------|------|
| prototype-generator | [skills/prototype-generator/SKILL.md](skills/prototype-generator/SKILL.md) | 从零生成完整原型 HTML 项目，支持三套主题风格（默认/政企/党建）和新增模块 |
| sales-project-deploy | [skills/sales-project-deploy/SKILL.md](skills/sales-project-deploy/SKILL.md) | 将构建产物通过 paramiko 部署到公司内网 Nginx 服务器 |
| zhaocai-test-deploy | [skills/zhaocai-test-deploy/SKILL.md](skills/zhaocai-test-deploy/SKILL.md) | 部署集团招采（jt12302）测试环境：Gradle 构建 WAR → Docker 镜像（配置替换）→ 启动容器 |
| daily-user-task-report | [skills/daily-user-task-report/SKILL.md](skills/daily-user-task-report/SKILL.md) | 每日用户任务创建日报：用 board 凭证遍历所有公司，统计所有真人用户今天人工创建的任务，生成 Markdown 日报（评论 + 附件 + 钉钉推送） |

---

## 核心能力

| 能力 | 说明 |
|------|------|
| **从零生成项目** | 完整目录结构 + 共享资源 + 框架页 + 登录页 + 导航入口页 + 风格总览页 + 业务页面 |
| **新增功能模块** | 在已有项目中按规范新增页面，自动更新框架注册 |
| **双端覆盖** | PC 管理端（iframe SPA）+ App 移动端（手机模型框架）+ 登录页 |
| **三套主题风格** | 默认品牌蓝 / 政企藏蓝 / 党建党旗红，关键词自动识别，生成时固定 |
| **项目部署** | paramiko（SFTP）部署到 Nginx，等效 rsync -avz --delete --progress |
| **招采后端部署** | Gradle 容器构建 WAR → Docker 制镜像（自动替换 Redis/数据库配置）→ 启动容器，镜像保留最近 2 版 |

---

## 项目结构（生成产物）

```
project/
├── index.html                     # 导航入口页，链接到 PC 端和 App 端
├── styleguide.html                # 风格总览页（从零生成时自动创建，入口页注册第 4 卡片）
├── shared/                        # 共享资源
│   ├── design-tokens.css          # CSS 变量：主题色、灰度、阴影、布局（含三套 data-skin 主题块）
│   ├── components.css             # 全局组件样式：Header/Sidebar/表格/表单/六态/暗色模式（仅 App 端启用）
│   ├── components.js              # 30+ 工具函数：状态切换/Toast/确认弹窗/分页/排序/主题
│   └── assets/                    # CDN 兜底本地资源（如项目已有则保留，新建则跳过）
├── pc/                            # PC 管理端
│   ├── index.html                 # 框架页：Header + 深色 Sidebar + iframe
│   ├── index-content.html         # 首页工作台（iframe 默认加载）
│   └── *.html                     # 各业务页面
├── app/                           # App 移动端
│   ├── index.html                 # 首页（含底部 Tab Bar + 角色切换）
│   ├── messages.html              # 消息通知
│   ├── profile.html               # 个人中心
│   ├── assets/
│   │   └── app.css                # App 端专用样式（含手机模型框架）
│   └── *.html                     # 各业务页面
└── login/
    └── index.html                 # 登录页
```

---

## PC 端关键约束

| 约束 | 说明 |
|------|------|
| 页面壳 | 使用 `#page-content` 包裹层 + body `bg-light` |
| 操作列 | `icon + 文字` 按钮格式（`<i class="bi bi-xxx"></i> 文字`），`td.text-nowrap` 不换行，多按钮用 `d-flex gap-2` 保持间距 |
| 弹窗模式 | 详情/新增/编辑使用 Bootstrap Modal 嵌入列表页（`#[module]DetailModal` / `#[module]FormModal`） |
| 分页 | 数据量 11~20 条，`initPagination(10)`，分页栏含 10/30/50/100 条选择器 + 上一页/下一页按钮；`.page-info` 必须用 `<span>`，按钮必须带 `page-btn` class |
| 六态 | 正常/空数据/筛选空/加载中/错误/网络错误 全部覆盖 |
| 导航 | 菜单 `<a>` 用 `class="sidebar-nav-link"` + `href` + `data-url` 三件套（**不写** `target="mainFrame"`）；框架内跳转用 `parent.loadPage('xx.html')`；弹窗用 `bootstrap.Modal` |
| 确认操作 | `parent.confirmModal('标题', '内容', callback)` |

---

## App 端关键约束

| 约束 | 说明 |
|------|------|
| 手机框架 | `phone-frame` 浅色无边框外框，390×844px，flexbox 列布局，无黑影边框 |
| Tab 页 | 有 `.phone-tabbar` 底部导航，`nav-header` 为 `nav-title` + `nav-actions` |
| 子页面 | 无 `.phone-tabbar`，有返回箭头 `.nav-back` |
| 导航 | 使用 `location.href`，子页面用原生 `<a href>`，不自写跨页跳转函数 |
| 本地函数 | 每个 App 页面定义本地 `showToast()` 和 `showState()` |
| 六态 | 空数据/筛选空(清除按钮)/加载中(spinner)/错误(重试按钮)/网络错误 |
| FOUC 脚本 | 仅 App 页 `<head>` 内放暗色模式阻止脚本（读 `theme`，**不读 `skin`**） |

---

## 主题风格（自动识别，生成时固定）

技能内置 **三套主题**，以**背景**为主要视觉区分，所有主题共享同一套布局/组件/交互，仅颜色变量不同。主题在生成时由关键词识别**一次性确定**并写入 `<html data-skin="...">`，**不支持运行时切换**。

### 三套主题对照

| 主题 | 触发关键词 | 主色 | Body 背景 | 顶栏 | 侧边栏 | 适用场景 |
|------|-----------|------|----------|------|--------|---------|
| **默认风格** | （默认） | `#3370FF` 品牌蓝 | `#F5F6F7` 浅灰 | 白 | `#1F2329` 深石板 | 互联网/科技/通用业务 |
| **政企风格** | "政企" | `#1E3A8A` 藏蓝 | `#F4F1EA` 档案米 | 白 | `#0F1E3D` 深藏蓝 | 政府/国企/事业单位 |
| **党建风格** | "党建" | `#C9302C` 党旗红 | `#FDF6E3` 米黄 | `#C9302C` 红 | `#7F1D1D` 深红 | 党建/党政机关/红色主题 |

### 自动识别规则（第 0 步，优先级：党建 > 政企 > 默认）

- 包含"**党建**" → 党建风格（`data-skin="party"`）
- 包含"**政企**"（无"党建"时） → 政企风格（`data-skin="gov"`）
- 都不包含 → 默认风格（`data-skin="default"`）

### 核心约束

- 主题色**全部走 CSS 变量**（`var(--primary)` 等），禁止硬编码主题色
- 主题写入 `<html data-skin="...">`，**不读不写 `localStorage.skin`**，不放任何主题切换按钮
- `data-skin`（主题）与 `data-theme="dark"`（暗色）可正交叠加，暗色模式仅 App 端启用
- 完整色板与组件级应用规范见 [themes.md](skills/prototype-generator/references/themes.md)

---

## 视觉规范速查

| 项目 | 值 |
|------|-----|
| 主题色 | 走 CSS 变量 `var(--primary)`：默认 `#3370FF` / 政企 `#1E3A8A` / 党建 `#C9302C` |
| PC 侧边栏 | 深色（默认 `#1F2329`），菜单圆角 6px |
| PC 顶栏 | 白色 `#FFFFFF`（党建风格为红色），高度 56px |
| 激活态 | 左侧 3px 蓝色细线 + 半透明蓝色背景 |
| App 底色 | `#e8eaed` |
| App 手机框 | 390×844px，圆角 44px，浅色无边框 |
| 暗色模式 | `data-theme="dark"` 切换（仅 App 端） |
| 外部资源 | Bootstrap 5.3.8 + Bootstrap Icons 1.13.1（CDN 优先） |

---

## Skill 文件结构

```
skills/
├── prototype-generator/
│   ├── SKILL.md                       # Skill 定义：能力说明、生成步骤、PC/App 约束、主题风格、检查清单
│   └── references/
│       ├── examples.md                # 参考模板：PC/App 页面模板、登录页/框架页/入口页、附录（CSS/JS 完整代码）
│       ├── themes.md                  # 主题风格规范：三套主题色板与组件级应用
│       └── styleguide/                # 自包含样式模板（可独立浏览器打开预览）
│           ├── index.html             # 三套风格选择器入口
│           ├── default.html           # 默认风格预览（品牌蓝）
│           ├── gov.html               # 政企风格预览（政务蓝）
│           └── party.html             # 党建风格预览（党旗红）
└── sales-project-deploy/
    ├── SKILL.md                       # Skill 定义：部署执行流程
    └── references/
        ├── conf.md                    # 部署参数配置（IP/端口/远程路径/访问地址前缀）
        └── source/
            └── deploy.py.md           # 部署执行脚本（Python paramiko，等效 rsync -avz --delete）
└── zhaocai-test-deploy/
    ├── SKILL.md                       # Skill 定义：招采测试环境部署流程
    └── references/
        ├── conf.md                    # 部署参数配置（项目名/端口/路径/镜像/配置替换对）
        └── source/
            └── deploy.sh.md           # 部署执行脚本（bash：Gradle 构建 WAR + Docker 制镜像 + 启动容器）
```

---

## 使用场景

| 场景 | 触发方式 | 说明 |
|------|---------|------|
| 新建原型项目 | "帮我生成一个XXX管理系统原型" | 从零生成完整原型项目（自动识别主题风格） |
| 党建项目 | "开发一套XXX党建管理系统" | 整站党旗红 + 米黄背景 + 金色党徽 |
| 政企项目 | "做一个XXX政务服务平台" | 整站政务蓝 + 档案米背景 + 金色顶栏底线 |
| 新增模块 | "在现有项目中添加XXX功能" | 按规范新增页面并注册到框架 |
| 修改页面 | "修改XXX列表页/详情页" | 基于现有模板修改业务页面 |
| 项目部署 | "部署项目到Nginx"/"发布" | 通过 paramiko 将构建产物同步到远程服务器 |
| 招采后端部署 | "部署集团招采测试环境"/"更新招采后端"/"重新构建jt12302" | Gradle 构建制镜像并启动容器（数据库密码走 Secrets API） |

---

## 外部资源引用

- Bootstrap 5.3.8 CSS/JS: `cdn.jsdelivr.net`
- Bootstrap Icons 1.13.1: `cdn.jsdelivr.net`
- 共享样式: `../shared/design-tokens.css` + `../shared/components.css`
- 共享脚本: `../shared/components.js`
- App 端额外样式: `assets/app.css`
