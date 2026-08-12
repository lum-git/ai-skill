# ai-skill

> 基于 Skill 文档体系的 **AI 技能集合**，提供原型 HTML 项目生成、项目部署等自动化能力。

## 项目名称
AI Skill 技能集合（ai-skill）

## 项目简介

本项目提供多套 AI Skill 规范，让 AI 能够：

- 根据需求描述自动生成完整的 HTML 原型项目
- 在已有项目中按规范新增功能模块
- 保持所有页面在代码写法、视觉风格、交互模式上的严格一致
- 同时覆盖 PC 管理端、App 移动端和登录页
- 将前端构建产物通过 rsync 部署到公司内网 Nginx 服务器

## 技能列表

### 1. prototype-generator — 原型 HTML 项目生成器

根据需求描述自动生成完整的后台管理系统原型，或在已有项目中新增功能模块。

#### 双端覆盖

| 端 | 技术方案 | 特点 |
|---|---------|------|
| **PC 管理端** | iframe SPA 架构 | Header + 深色 Sidebar + 内容区，弹窗模式交互 |
| **App 移动端** | 手机模型框架 | 390x844px 圆角外框，flexbox 列布局，底部 Tab Bar |
| **登录页** | 独立页面 | 品牌蓝渐变背景，居中登录卡片 |

#### 设计规范

| 规范 | 说明 |
|------|------|
| 品牌色 | 主题蓝 `#3370FF`，侧边栏深色 `#1F2329` |
| 组件库 | Bootstrap 5.3 + Bootstrap Icons 1.13 |
| 六态覆盖 | 正常/空数据/筛选空/加载中/错误/网络错误 |
| 暗色模式 | `data-theme="dark"` 一键切换，完整适配 |
| 交互模式 | PC 端弹窗模式(Modal)，App 端页面跳转，登录页独立入口 |

#### 内置工具函数（components.js，30+）

| 分类 | 函数 |
|------|------|
| 状态切换 | `showState()`, `showToast()` |
| 确认弹窗 | `confirmModal()` |
| 分页 | `initPagination()`, `changePageSize()`, `goPage()`, `renderPage()` |
| 排序 | `sortTable()` |
| 筛选 | `clearAllFilters()` |
| 主题 | `toggleTheme()` |
| 侧边栏 | `toggleSidebar()`, `closeSidebar()` |
| 标签页 | `openTab()`, `switchTab()`, `closeTab()`, `closeAll()` |
| 格式化 | `formatDate()`, `formatMoney()` |

### 2. sales-project-deploy — 销售项目部署

将前端构建产物部署到公司内网 Nginx 服务器。

| 特性 | 说明 |
|------|------|
| 传输方式 | Python paramiko（自动选择 SFTP 或 tar+SSH pipe），等同 rsync -avz --delete --progress |
| 配置管理 | 统一 conf.md，账号密码通过 Secrets API 实时获取不落盘 |
| 部署方式 | `python references/deploy.py <本地产物路径> <项目拼音首字母>` |
| 同步策略 | `--delete` 等效行为，确保远程与本地完全一致 |
| 依赖 | `pip install paramiko`（纯 Python，无需 rsync/sshpass） |

## Skill 文件结构

```
skills/
├── prototype-generator/
│   ├── SKILL.md                       # Skill 定义
│   │                                  #   - 核心能力说明
│   │                                  #   - 从零生成项目的完整步骤
│   │                                  #   - PC 端/App 端关键约束
│   │                                  #   - 输出检查清单
│   └── references/
│       └── examples.md                # 参考模板
│                                      #   - PC 端页面模板（列表/详情/表单/Dashboard）
│                                      #   - App 端页面模板（Tab 页/子页/组件）
│                                      #   - 登录页/框架页/导航入口页模板
│                                      #   - 代码风格规范
│                                      #   - 附录 A~D：共享资源完整代码（CSS/JS）
└── sales-project-deploy/
    ├── SKILL.md                       # Skill 定义
    │                                  #   - 部署执行流程
    ├── assets/                        # 静态资源
    ├── references/
    │   ├── conf.md                    # 部署参数配置
    │   └── deploy.py                  # 部署执行脚本（Python paramiko）
    └── scripts/                       # 保留空目录
```

## 使用方式

### 原型生成 — 新建项目

向 AI 描述需求即可：

> "帮我生成一个客户关系管理系统的原型，包含客户列表、客户详情、跟进记录、数据看板"

AI 会自动：
1. 规划页面清单并确认
2. 创建目录结构
3. 生成共享资源文件（design-tokens.css / components.css / components.js / app.css）
4. 生成框架文件（导航入口页 / PC 框架 / App 框架 / 登录页）
5. 生成所有业务页面（PC + App 双端）
6. 注册到框架并完成导航连接

### 原型生成 — 在已有项目中新增模块

> "在项目中添加订单管理模块"

AI 会按模板创建新页面并自动更新框架的 sidebar 菜单和页面注册。

### 项目部署

> "帮我部署项目到 Nginx"

AI 会：
1. 读取 conf.md 服务器配置，通过 Secrets API 获取账号密码
2. 确认本地产物路径和项目名称
3. 执行 python deploy.py 同步部署
4. 输出访问地址

## 技术栈

- **HTML5** - 语义化标签
- **CSS3** - CSS 自定义属性（变量）实现主题系统
- **Bootstrap 5.3** - 组件库和布局系统（CDN 引入）
- **Bootstrap Icons 1.13** - 图标库（CDN 引入）
- **Vanilla JavaScript** - ES5 兼容写法（var / function）

## 视觉预览

| 页面 | 描述 |
|------|------|
| 导航入口 | 卡片式入口，链接到 PC 端 / App 端 / 登录页 |
| PC 框架 | 白色顶栏 + 深色侧边栏 + iframe 内容区 |
| PC 列表 | 筛选栏 + 数据表格 + 分页栏 + 弹窗（详情/编辑） |
| App 首页 | 手机模型外框 + 统计卡片 + 快捷操作 + 列表 |
| 登录页 | 品牌蓝渐变背景 + 居中白色登录卡片 |

## 项目状态

- prototype-generator：Skill 定义已完成，参考模板完整（含 4 套附录完整代码），生成流水线就绪
- sales-project-deploy：Skill 定义已完成，deploy.py 脚本和 conf.md 配置就绪

## 开源协议

本项目基于 [MIT License](LICENSE) 开源。

## Jenkins地址
技能项目暂无

## 数据库地址
技能项目暂无

## 禅道地址
技能项目暂无
