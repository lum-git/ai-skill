# CLAUDE.md - AI Skill 技能集合

> 本文件为 AI 辅助开发工作流提供项目规范和 Skill 使用指南。

---

## 项目概述

基于 Skill 文档体系的 **AI 技能集合**，目前包含两套技能：原型 HTML 项目生成器（根据需求自动生成后台管理系统原型）和销售项目部署（通过 rsync 将构建产物部署到公司内网 Nginx 服务器）。

**技术栈**: HTML5 + Bootstrap 5.3 + Bootstrap Icons 1.13 + Vanilla JS / Bash + rsync

---

## Skill 索引

| Skill | 路径 | 说明 |
|-------|------|------|
| prototype-generator | [skills/prototype-generator/SKILL.md](skills/prototype-generator/SKILL.md) | 从零生成完整原型 HTML 项目，支持新增模块 |
| sales-project-deploy | [skills/sales-project-deploy/SKILL.md](skills/sales-project-deploy/SKILL.md) | 将构建产物通过 rsync 部署到公司内网 Nginx 服务器 |

---

## 核心能力

| 能力 | 说明 |
|------|------|
| **从零生成项目** | 完整目录结构 + 共享资源 + 框架页 + 登录页 + 导航入口页 + 业务页面 |
| **新增功能模块** | 在已有项目中按规范新增页面，自动更新框架注册 |
| **双端覆盖** | PC 管理端（iframe SPA）+ App 移动端（手机模型框架）+ 登录页 |
| **项目部署** | rsync over SSH 同步部署，配置集中管理，账号密码实时获取不落盘 |

---

## 项目结构（生成产物）

```
project/
├── index.html                     # 导航入口页，链接到 PC 端和 App 端
├── shared/                        # 共享资源
│   ├── design-tokens.css          # CSS 变量：品牌蓝主题
│   ├── components.css             # 全局组件样式：Header/Sidebar/表格/表单/六态/暗色模式
│   └── components.js              # 30+ 工具函数：状态切换/Toast/确认弹窗/分页/排序/主题
├── pc/                            # PC 管理端
│   ├── index.html                 # 框架页：Header + 深色 Sidebar + iframe
│   ├── index-content.html         # 首页工作台
│   └── *.html                     # 各业务页面
├── app/                           # App 移动端
│   ├── index.html                 # 首页（含底部 Tab Bar）
│   ├── messages.html              # 消息通知
│   ├── profile.html               # 个人中心
│   ├── assets/app.css             # App 端专用样式（含手机模型框架）
│   └── *.html                     # 各业务页面
└── login/
    └── index.html                 # 登录页
```

---

## PC 端关键约束

| 约束 | 说明 |
|------|------|
| 页面壳 | 使用 `#page-content` 包裹层 + body `bg-light` |
| 操作列 | `icon + 文字` 按钮格式，`td.text-nowrap` 不换行 |
| 弹窗模式 | 详情/新增/编辑使用 Bootstrap Modal 嵌入列表页 |
| 分页 | 数据量 11~20 条，`initPagination(10)`，分页栏含 10/30/50/100 条选择器 |
| 六态 | 正常/空数据/筛选空/加载中/错误/网络错误 全部覆盖 |
| 导航 | 弹窗用 `bootstrap.Modal`，Tab 用 `parent.openTab()` |
| 确认操作 | `parent.confirmModal('标题', '内容', callback)` |

---

## App 端关键约束

| 约束 | 说明 |
|------|------|
| 手机框架 | `phone-frame` 浅色无边框外框，390×844px，flexbox 列布局 |
| Tab 页 | 有 `.phone-tabbar` 底部导航 |
| 子页面 | 无 `.phone-tabbar`，有返回箭头 `.nav-back` |
| 导航 | 使用 `location.href`，不用 `parent.openTab()` |
| 本地函数 | 每个 App 页面定义本地 `showToast()` 和 `showState()` |
| 六态 | 空数据/筛选空(清除按钮)/加载中(spinner)/错误(重试按钮)/网络错误 |

---

## 视觉规范速查

| 项目 | 值 |
|------|-----|
| 主题色 | `#3370FF`（品牌蓝） |
| PC 侧边栏 | 深色 `#1F2329`，菜单圆角 6px |
| PC 顶栏 | 白色 `#FFFFFF`，高度 56px |
| 激活态 | 左侧 3px 蓝色细线 + 半透明蓝色背景 |
| App 底色 | `#e8eaed` |
| App 手机框 | 390×844px，圆角 44px |
| 暗色模式 | `data-theme="dark"` 切换 |

---

## Skill 文件结构

```
skills/
├── prototype-generator/
│   ├── SKILL.md                       # Skill 定义：能力说明、生成步骤、PC/App 约束、检查清单
│   └── references/
│       └── examples.md                # 参考模板：PC/App 页面模板、登录页/框架页/入口页、附录（CSS/JS）
└── sales-project-deploy/
    ├── SKILL.md                       # Skill 定义：部署执行流程
    ├── assets/                        # 静态资源
    ├── references/
    │   └── conf.md                    # 部署参数配置
    └── scripts/
        └── deploy.sh                  # 部署执行脚本
```

---

## 使用场景

| 场景 | 触发方式 | 说明 |
|------|---------|------|
| 新建原型项目 | "帮我生成一个XXX管理系统原型" | 从零生成完整原型项目 |
| 新增模块 | "在现有项目中添加XXX功能" | 按规范新增页面并注册到框架 |
| 修改页面 | "修改XXX列表页/详情页" | 基于现有模板修改业务页面 |
| 项目部署 | "部署项目到Nginx"/"发布" | 通过 rsync 将构建产物同步到远程服务器 |

---

## 外部资源引用

- Bootstrap 5.3 CSS/JS: `cdn.jsdelivr.net`
- Bootstrap Icons 1.13: `cdn.jsdelivr.net`
- 共享样式: `../shared/design-tokens.css` + `../shared/components.css`
- 共享脚本: `../shared/components.js`
