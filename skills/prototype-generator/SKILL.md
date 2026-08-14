---
name: "prototype-generator"
description: "从零生成完整原型HTML项目（PC管理端 + App移动端 + 登录页），也可在已有项目中新增功能模块。当用户需要创建后台管理系统原型、新增功能模块、或生成与现有项目风格一致的HTML页面时调用。生成代码自动包含品牌蓝(#3370FF)主题、深色侧边栏(#1F2329)+白色顶栏的PC布局、六态覆盖、App端暗色模式、Bootstrap 5.3 组件、PC端弹窗模式、App端手机模型框架。"
---

# 原型HTML项目生成器

根据用户需求，自动生成完整的原型 HTML 项目，或向已有项目新增功能模块。所有生成的页面在代码写法、视觉风格、交互模式上保持严格一致。

---

## 核心能力

1. **从零生成项目**：创建完整目录结构 + 所有共享资源文件 + 框架页 + 登录页 + 导航入口页 + 业务页面
2. **新增功能模块**：在已有项目中按规范新增页面，并自动更新框架注册
3. **双端覆盖**：PC 管理端（iframe SPA）+ App 移动端（手机模型框架）+ 登录页

> **模板代码详见**：[references/examples.md](references/examples.md)，包含 PC 端页面模板、App 端页面模板、登录页/框架页/入口页模板、代码风格范例、附录（CSS/JS 共享资源完整代码）。

---

## 一、项目结构

```
project/
├── index.html                     # 导航入口页，链接到 PC 端和 App 端
├── shared/                        # 共享资源（从零生成时必须创建）
│   ├── design-tokens.css          # CSS 变量：主题色、灰度、阴影、布局
│   ├── components.css             # 全局组件样式：Header/Sidebar/表格/表单/六态/暗色模式（仅 App 端启用）
│   ├── components.js              # 30+ 工具函数：状态切换/Toast/确认弹窗/分页/排序/主题
│   └── assets/                    # CDN 兜底本地资源（如项目已有则保留，新建则跳过）
├── pc/                            # PC 管理端
│   ├── index.html                 # 框架页：Header + Sidebar + iframe
│   ├── index-content.html         # 首页工作台（iframe 默认加载）
│   └── *.html                     # 各业务页面
├── app/                           # App 移动端
│   ├── index.html                 # 首页（含底部 Tab Bar + 角色切换）
│   ├── messages.html              # 消息通知
│   ├── profile.html               # 个人中心
│   ├── assets/
│   │   └── app.css                # App 端专用样式
│   └── *.html                     # 各业务页面
└── login/
    └── index.html                 # 登录页
```

### 外部资源引用策略

**CDN 优先，本地兜底**。所有页面统一引用方式：

```html
<!-- Bootstrap 5.3 CSS -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/css/bootstrap.min.css">
<!-- Bootstrap Icons 1.13 -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.13.1/font/bootstrap-icons.css">
<!-- 项目共享样式 -->
<link rel="stylesheet" href="../shared/design-tokens.css">
<link rel="stylesheet" href="../shared/components.css">
<!-- App 端额外样式 -->
<link rel="stylesheet" href="assets/app.css">  <!-- 仅 App 页面 -->

<!-- JS -->
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/js/bootstrap.bundle.min.js"></script>
<script src="../shared/components.js"></script>
```

> **重要**：如果项目已有 `shared/bootstrap/` 和 `shared/icons/` 本地文件，则使用本地路径。**新建项目时统一使用 CDN**，不再生成本地文件。

---

## 二、从零生成项目的步骤

当用户说"帮我生成一个XXX管理系统原型"时，按以下顺序执行：

### 第 0 步：识别主题风格

在理解需求前，**先扫描用户需求中的关键词**，确定主题风格（详见[第八章](#八主题风格自动识别生成时固定)）：

- 包含"**党建**" → 党建风格（`data-skin="party"`）
- 包含"**政企**"（无"党建"时） → 政企风格（`data-skin="gov"`）
- 都不包含 → 默认风格（`data-skin="default"`，默认）

主题风格确定后，**整个项目所有页面（PC + App + 登录 + 根导航）**统一使用该主题的 CSS 变量 —— 不是仅某几页变色，而是项目级整体应用：

| 用户说 | 自动应用 |
|--------|---------|
| "开发一套xxx党建管理系统" | 整站党旗红 + 米黄背景 + 金色党徽 |
| "做一个xxx政务服务平台" | 整站政务蓝 + 档案米背景 + 金色顶栏底线 |
| "做一个xxx SaaS 平台" | 整站品牌蓝 + 浅灰背景 + 深色侧边栏（默认） |

> **预览三套风格效果**：打开 [references/styleguide/index.html](references/styleguide/index.html) 入口页，分别进入 `default.html` / `gov.html` / `party.html` 查看完整风格规范（每页已固定显示各自主题，不做切换）。
> **生成项目自动含风格总览页**：从零生成项目时，会在根 `index.html` 添加"风格总览"入口卡片（指向项目内的 `styleguide.html`），便于团队随时核对当前主题效果；**PC 侧边栏不放"风格总览"菜单**。

### 第 1 步：理解需求，规划页面

从用户描述中提取：
- **系统名称**
- **功能模块**
- **每个模块需要哪些页面**（PC 列表/详情/表单，App 列表/详情/表单）

输出页面清单供用户确认。

### 第 2 步：创建目录结构

```
mkdir project/shared
mkdir project/pc
mkdir project/app/assets
mkdir project/login
```

### 第 3 步：生成共享资源文件

依次创建以下文件，完整代码详见 [references/examples.md](references/examples.md) 附录 A~D：

| 文件 | 说明 | 见附录 |
|------|------|--------|
| `shared/design-tokens.css` | CSS 变量（品牌蓝主题） | 附录 A |
| `shared/components.css` | 全局组件样式 | 附录 B |
| `shared/components.js` | 30+ 工具函数 | 附录 C |
| `app/assets/app.css` | App 端专用样式（含手机模型框架） | 附录 D |

### 第 4 步：生成框架文件

| 文件 | 模板位置 |
|------|----------|
| `index.html`（根导航） | [examples.md 第六章](references/examples.md#六根导航入口页模板-indexhtml) |
| `login/index.html` | [examples.md 第五章](references/examples.md#五登录页模板) |
| `pc/index.html`（PC 框架） | [examples.md 第七章](references/examples.md#七pc-端框架页-pcindexhtml) |
| `pc/index-content.html`（首页） | Dashboard 仪表板模板 |
| `app/index.html`（App 首页） | Tab 页模板 |
| `app/messages.html` | Tab 页模板 |
| `app/profile.html` | Tab 页模板 |

### 第 5 步：生成业务页面

根据需求，为每个模块创建 PC + App 页面，模板详见 [examples.md 第三~四章](references/examples.md)。

### 第 6 步：注册到框架

- 更新 `pc/index.html` 的 sidebar 菜单、`_knownPages` 数组、`data-active-menu` 映射
- 更新 `app/index.html` 的快捷操作按钮
- 更新根 `index.html` 的页面计数

---

## 三、PC 端页面关键约束

### 3.1 列表页操作列

操作列按钮**必须同时满足以下三条约束**：

1. **图标 + 名称**：每个按钮内必须包含 Bootstrap Icons 图标和中文名称，格式为 `<i class="bi bi-xxx"></i> 名称`
2. **水平排列、不换行**：`<td>` 加 `class="text-nowrap"`，`<th>` 设 `white-space:nowrap` 和足够的 `width`
3. **相邻按钮保留间距**：多个按钮并排时用 `d-flex gap-2` 容器（或给非首个按钮加 `ms-2`）拉开距离，禁止贴在一起

```html
<th style="width:220px;white-space:nowrap;">操作</th>
...
<td class="text-nowrap">
  <div class="d-flex gap-2">
    <button class="btn btn-sm btn-outline-primary" onclick="showDetail(this)" title="查看"><i class="bi bi-eye"></i> 查看</button>
    <button class="btn btn-sm btn-outline-secondary" onclick="editItem(this)" title="编辑"><i class="bi bi-pencil"></i> 编辑</button>
  </div>
</td>
```

禁止仅用图标（如 `<i class="bi bi-eye"></i>`）或无图标的纯文字按钮。

### 3.2 详情/新增/编辑 → 弹窗模式

列表页的详情/新增/编辑统一用 Bootstrap Modal 实现：
- `#[module]DetailModal` — 详情展示，modal-lg
- `#[module]FormModal` — 新增/编辑表单

### 3.3 分页（数据量 + 分页栏标准结构）

列表数据至少 **11~20 条**，确保默认每页 10 条时能产生分页效果。

分页栏模板见 [examples.md 1.2 列表页模板](references/examples.md#12-列表页含筛选栏表格分页弹窗六态)。

**关键约束：**
- `.page-info` **必须用 `<span>`**，不可用 `<div>`——`updatePaginationUI` 通过 `querySelector('.page-info')` 动态更新其 `textContent`
- 按钮**必须带 `page-btn` class**——`updatePaginationUI` 通过 `.page-btn:first-child` / `.page-btn:last-child` 定位上一页/下一页按钮并控制 disabled 状态
- 按钮文字必须是 **"上一页""下一页"**，不可仅用 chevron 图标
- 上一页/下一页按钮放在 `d-flex gap-2` 容器内保持间距，禁止贴在一起
- 每页条数 `<select>` 绑定 `changePageSize(this.value)`，默认选中 `10`
- 初始化必须调用 `initPagination(10)`

### 3.4 PC 端导航

- **弹窗模式（推荐）**：`new bootstrap.Modal(document.getElementById('detailModal')).show()`
- **页面跳转（PC 框架内）**：菜单 `<a>` 必须是 `class="sidebar-nav-link"` + `href="xxx.html"` + `data-url="xxx.html"` 三件套。**不要写** `target="mainFrame"`（iframe sandbox 下失效）。点击时由框架脚本调用 `loadPage(url)` 同步 `.active` 与 iframe 加载，业务页面**无需**自写跳转函数。
- **面包屑跳转**：PC 内容页用 `<a href="xx.html" onclick="parent.loadPage('xx.html')">` 跳转，**不要**用 `target="mainFrame"`。
- **确认操作**：`parent.confirmModal('标题', '内容', callback)`

> PC 框架页定义 `window.loadPage = function(url){...}` 全局函数。详见 [examples.md 第五章](references/examples.md#五pc-端框架页-pcindexhtml)。

### 3.5 六态

每个 PC 内容页面必须在 `#page-content` 末尾包含：空数据(`state-empty`)、筛选空(`state-empty_filter`)、加载中(`state-loading`)、错误(`state-error`)、网络错误(`state-network_error`)。

### 3.6 通用页面壳

每个 PC 内容页面的标准 HTML 壳参见 [examples.md 1.1 通用页面壳](references/examples.md#11-通用页面壳)。

---

## 四、App 端页面关键约束

### 4.1 手机模型框架

所有 App 页面统一使用 `phone-frame` 浅色无边框手机外框结构：
- 浅灰底色 #e8eaed、390×844px 圆角外框
- flexbox 列布局：状态栏 → 导航栏 → 内容区 → 底部 Tab
- 无黑影边框、无灵动岛
- 内容区独立滚动，状态栏/导航栏/底部 Tab 固定

### 4.2 Tab 页与子页

| 类型 | 特征 | nav-header |
|------|------|------------|
| Tab 页 | 有 `.phone-tabbar` | `<h1 class="nav-title">标题</h1>` + `<div class="nav-actions">` |
| 子页面 | 无 `.phone-tabbar`，有返回箭头 | `.nav-left > .nav-back` + `.nav-title` |

### 4.3 App 端导航

- Tab 页用 `location.href = 'xxx.html'`
- 子页面用 `<a class="nav-back" href="parent.html">`，浏览器原生跳转即可。
- 业务页面**不要**自写跨页跳转函数；所有跳转都通过原生 `<a href>` 完成。

### 4.4 App 端六态

六态放在 `.phone-content` 末尾：空数据/筛选空(清除筛选按钮)/加载中(spinner)/错误(重试按钮)/网络错误。

### 4.5 App 端本地函数

每个 App 页面需定义本地 `showToast()` 和 `showState()` 函数。

---

## 五、PC 框架页关键配置

PC 框架页完整模板及 Sidebar 菜单格式参见 [examples.md 五 PC 框架页](references/examples.md#五pc-端框架页-pcindexhtml)。

**深色侧边栏特点：**
- 深色背景 `#1F2329`，菜单项圆角 6px
- 分组间用 `sidebar-divider` 分隔，标题用 `sidebar-section-title`
- 激活态：左侧 3px 蓝色细线条 + 半透明蓝色背景，文字白色
- 单一 iframe 区域承载所有业务页面，导航通过左侧菜单完成

---

## 六、新增模块工作流

1. 确定模块名称和需要的页面
2. 按模板创建 PC + App 页面文件
3. 更新 `pc/index.html`：在 sidebar 对应分组下新增菜单 `<a>`（必须是 `class="sidebar-nav-link"` + `href="xxx.html"` + `data-url="xxx.html"` 三件套；**不写** `target="mainFrame"`）
4. 如需要快捷入口，更新 `app/index.html` 的 quick-actions
5. 更新根 `index.html` 的页面计数

---

## 七、输出检查清单

生成每个页面前确认：
- [ ] **根导航入口页 `index.html` 严格保持纯净**：① 禁止出现任何技术栈内容（HTML/CSS/JS、Bootstrap、Vue、React、jQuery、CDN 等技术名词一律不写）；② 禁止描述页面风格/UI 特点（如「深色侧边栏+白色顶栏」「390×844 手机框架」「弹窗模式」「六态」「暗色模式」「分页排序」等样式/交互/布局描述）。
- [ ] **主题识别已执行（第 0 步）**：扫描用户需求中的"党建"/"政企"关键词，确定 `data-skin` 值；所有页面（含 PC 框架/业务页/App 页/登录页/根导航页）`<html>` 标签带**统一**的 `data-skin` 属性（默认 `default`）—— 这是**项目级**应用，不是单页设置
- [ ] **风格总览页已生成**：从零生成项目时，自动创建 `styleguide.html`（参考 [references/styleguide/party.html](references/styleguide/party.html) 结构），并在根 `index.html` 第 4 卡片注册入口；**PC 侧边栏不放"风格总览"菜单**
- [ ] **主题色全部走 CSS 变量**：未硬编码 `#3370FF` / `#1E3A8A` / `#C9302C` 等主题色，全部用 `var(--primary)` 等变量
- [ ] **FOUC 阻止脚本（仅 App 端暗色）**：只有 App 页必须放（含暗色模式 `theme` 读取，**不读 `skin`**）；PC 框架页/PC 内容页/登录页/根导航页/风格总览页都**不放**暗色脚本
- [ ] `<html lang="zh-CN">`
- [ ] `<title>[页面名] — [系统名]</title>`
- [ ] CSS：CDN bootstrap → CDN icons → design-tokens.css → components.css → [app.css]
- [ ] JS：CDN bootstrap.bundle → components.js → 页面脚本
- [ ] App 页面有暗色 FOUC 阻止脚本，PC 页面（框架/内容/登录/根导航/风格总览）无需
- [ ] App 页面使用 `phone-frame-body` + `phone-frame` 手机框架结构（无黑边框）
- [ ] App 页面 `.phone-content` 承载内容，状态栏 + 导航栏 + 底部Tab 均在 phone-content 外部
- [ ] PC 页面使用 `#page-content` 包裹层
- [ ] `body class="bg-light"`（App 加 `phone-frame-body`）
- [ ] 六态全部包含（正常/空数据/筛选空/加载中/错误/网络错误）
- [ ] App Tab 页有 `.phone-tabbar`，非 Tab 页有返回箭头 `.nav-back`
- [ ] PC 详情/新增/编辑优先用弹窗模式（Bootstrap Modal 嵌入列表页）
- [ ] PC 操作列：`<button class="btn btn-sm btn-outline-primary"><i class="bi bi-xxx"></i> 文字</button>`，`td class="text-nowrap"`，多按钮用 `d-flex gap-2` 保持间距
- [ ] PC 侧边栏菜单 `<a>` 用 `class="sidebar-nav-link"`，并带 `href="..."` + `data-url="..."`（**不写** `target="mainFrame"`）
- [ ] PC 框架内跳转用 `<a href="xxx.html" onclick="parent.loadPage('xxx.html')">`（不写 `target="mainFrame"`）
- [ ] App 导航用 `location.href`
- [ ] 表单页有 `data-dirty` 属性
- [ ] App 页面有本地 `showToast()` 定义
- [ ] 所有颜色用 CSS 变量（主题色 `var(--primary)`，默认 `#3370FF`，政企 `#1E3A8A`，党建 `#C9302C`）
- [ ] 带分页的列表：数据量 11~20 条、`initPagination(10)`、分页栏含页面大小选择器(10/30/50/100)+上一页/下一页按钮+`page-btn` class、`.page-info` 用 `<span>`
- [ ] 中文文本（标签、提示、占位符）
- [ ] App 状态栏统一格式：时间 9:41 + 信号/电池图标

---

## 八、主题风格（自动识别，生成时固定）

技能内置 **三套主题**，以**背景**为主要视觉区分。所有主题共享同一套布局/组件/交互，仅颜色变量不同。主题在生成时由关键词识别**一次性确定**并写入 `<html data-skin="...">`，**不支持运行时切换**。

### 8.1 三套主题对照

| 主题 | 触发关键词 | 主色 | Body 背景 | 顶栏 | 侧边栏 | 适用场景 |
|------|-----------|------|----------|------|--------|---------|
| **默认风格** | （默认） | `#3370FF` 品牌蓝 | `#F5F6F7` 浅灰 | 白 | `#1F2329` 深石板 | 互联网/科技/通用业务 |
| **政企风格** | "政企" | `#1E3A8A` 藏蓝 | `#F4F1EA` 档案米 | 白 | `#0F1E3D` 深藏蓝 | 政府/国企/事业单位/严肃业务 |
| **党建风格** | "党建" | `#C9302C` 党旗红 | `#FDF6E3` 米黄 | `#C9302C` 红色 | `#7F1D1D` 深红 | 党建/党政机关/红色主题 |

> 完整色板与组件级应用规范见 [references/themes.md](references/themes.md)。

### 8.2 自动识别规则

**第 0 步**扫描用户需求文本（大小写不敏感）：

```
if (req.indexOf('党建') >= 0)      theme = 'party'   // 党建优先
else if (req.indexOf('政企') >= 0) theme = 'gov'     // 政企
else                                theme = 'default' // 默认
```

- **优先级**：当两个关键词都出现时，"党建" 优先（更具体）。
- **应用方式**：在所有生成页面的 `<html>` 标签上添加 `data-skin="xxx"` 属性（无关键词时为 `data-skin="default"`）。
- **固定**：识别结果直接写入 `<html data-skin="...">` 标记，**不写入 `localStorage.skin`**、**不提供运行时切换**。

### 8.3 主题固定（生成时确定，禁止运行时切换）

主题由第 0 步关键词识别**一次性确定**，作为项目"出厂设置"写入所有页面的 `<html data-skin="...">`。**任何页面（含 PC 框架/业务页/登录/根导航/App/风格总览）都不放主题切换按钮**，也不提供 `cycleSkin` / `setSkin` / `getSkin` 等运行时切换 API——主题不能由用户切换。

> **为什么禁止切换**：多个原型项目部署在同一源（如本地预览服务器、`file://`）时会共享 `localStorage`。若用 `localStorage.skin` 持久化主题，A 项目切换后会污染 B 项目。因此主题只以 `<html data-skin="...">` 写死在标记中，**不读不写 `localStorage.skin`**。

**FOUC 阻止脚本**（仅 App 端页面在 `<head>` 内同步执行，CSS 之前）——只处理暗色模式，**不读取 `skin`**：

```html
<script>
  (function(){
    var t = localStorage.getItem('theme');
    if (t === 'dark' || (!t && window.matchMedia('(prefers-color-scheme:dark)').matches))
      document.documentElement.setAttribute('data-theme', 'dark');
  })();
</script>
```

> 主题色板与组件级应用规范见 [references/themes.md](references/themes.md)。

### 8.4 核心约束

- ✅ **不影响核心功能**：主题仅改变颜色变量，不动布局/结构/交互/数据。
- ✅ **正交叠加（仅 App 端）**：`data-skin`（主题）与 `data-theme="dark"`（暗色）可叠加（如：暗色 + 党建），互不干扰；暗色模式仅 App 端启用，PC 端不提供暗色。
- ✅ **CSS 变量驱动**：通过 `shared/design-tokens.css` 中的 `[data-skin="xxx"]` 块切换，**禁止硬编码主题色**。
- ✅ **背景显著区分**：三套主题的 body 背景必须明显不同（灰/米/黄），保证一眼可辨。
- ✅ **主题识别必须在生成前完成**：第 0 步输出 `data-skin` 值，所有生成文件统一遵循。
