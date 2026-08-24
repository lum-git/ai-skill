---
name: "prototype-generator"
description: "从零生成完整原型HTML项目（PC管理端 + App移动端 + 登录页），也可在已有项目中新增功能模块。当用户需要创建后台管理系统原型、在已有原型项目中新增功能模块、或生成与现有原型项目风格一致的HTML页面时调用。生成代码自动包含三套主题（默认品牌蓝#3370FF / 政企藏蓝#1E3A8A / 党建红#C9302C，按关键词自动识别）、深色侧边栏+顶栏的PC布局、六态覆盖、App端暗色模式、Bootstrap 5.3 组件、PC端弹窗模式、App端手机模型框架。"
---

# 原型HTML项目生成器

根据用户需求，自动生成完整的原型 HTML 项目，或向已有项目新增功能模块。所有生成的页面在代码写法、视觉风格、交互模式上保持严格一致。

---

## 核心能力

1. **从零生成项目**：创建完整目录结构 + 所有共享资源文件 + 框架页 + 登录页 + 导航入口页 + 业务页面
2. **新增功能模块**：在已有项目中按规范新增页面，并自动更新框架注册
3. **双端覆盖**：PC 管理端（iframe SPA）+ App 移动端（手机模型框架）+ 登录页
4. **风格总览页**：从零生成项目时，按 [references/styleguide.md](references/styleguide.md) 规范生成 `styleguide.html`
5. **PC 数据大屏（必备 · 驾驶舱形态）**：每个项目**必须**生成 `pc/dashboard.html` 并注册为侧边栏独立菜单。**大屏 = PC 后台内嵌驾驶舱**（DataV / 京东 / 阿里云风格），**不是 BI 报表页**——单屏不滚动、超大字 KPI、告警闪烁、事件流实时滚动、可派单交互。

> **结构（按业务自主判断，无固定模板）**：
>
> **驾驶舱没有唯一正确的模板**。业务不同（物流调度 / 销售监控 / 运维态势 / 党建风采 / 应急指挥），核心模块、视觉重心、信息密度都不一样。本规范只沉淀**通用骨架 + 典型范式参考**，具体由 AI 按需求自主判断。
>
> 通用骨架（所有驾驶舱共享）：
> 1. **单屏 fit**：`html, body { height: 100%; overflow: hidden }`，1920×900 iframe
> 2. **顶层 CSS Grid 分配高度**（行数和行高按业务定），禁止每段独立 height 后让 overflow 裁掉
> 3. **ECharts 必用 `ResizeObserver`** 监听容器尺寸（容器在 flex/grid 中高度变化时图表才能跟上）
> 4. **CSS 变量驱动主题色**：所有强调色走 `var(--db-*)`，ECharts 用 `getComputedStyle` 读变量
>
> 三大典型范式（参考，不强制）：
> - **A 地图主导型**：物流调度 / 区域监控 / 应急指挥 → 顶栏 + KPI + 左分析/中央地图/右监控 + 状态栏
> - **B 数据洞察型**：经营分析 / 销售 / 财务 → 顶栏 + KPI + 大趋势图 + 榜单/饼图
> - **C 综合指挥型**：智慧城市 / 综合态势 → 顶栏 + 告警条 + KPI + 含地图的多列布局
>
> 地图决策（**有强制规则，必须遵守**）：
> - ✅ **加地图（硬规则）**：需求文档中出现**省/市/区/县名**（如"广东省""广州市""天河区"）+ 数据能匹配行政区划 → **必须加地图**，不允许用条形图/饼图替代
> - ✅ 加地图（一般）：业务涉及地域 / 路径 / 位置 / 区域对比
> - ❌ 不加地图：纯财务 / 库存 / 系统监控；数据维度是"学院/专业/产品/部门/库存 SKU"等**完全非行政的纯业务维度**（DataV 没有这种地图）
> - ⚠️ **关键区分**："高校分布""校区数据"等看起来像非行政维度，但归属在行政区划内（如 21 地市内高校、某市内校区），**视为行政维度的下级**，应加地图展示地域分布；只在地图上以散点/标签标注具体高校即可，不要因"高校"二字否决地图
> - 地图级别：**按关键词匹配任意一级**（全国→100000 / 省→320000 / **市→320100，最小可到市级**），不要硬性写死"默认国家级"
> - 初始层级由业务决定（全国 / 省 / 市），最小只能到市级（区县数据量过大、视觉碎片化，不建议作初始层级）
>
> **完整骨架 / 组件样式 / 地图组件 / 经验沉淀 见 [references/dashboard.md](references/dashboard.md)**，尤其要读"§1 设计原则（按业务自主判断）"。
>
> **视觉风格由主题决定**（不在大屏里硬编码）：
> - 颜色：所有强调色走 CSS 变量 `--db-accent` 等，**禁止**直接写 `#4DD0E1` 等色值
> - 字体大小、密度、是否带 3D 效果由项目主题和业务决定（default 偏科技蓝、gov 偏庄重藏蓝、party 偏红色党旗风）
> - 数字动效（递增动画、滚动事件流）作为**通用能力**提供，但具体是否使用由业务场景决定

> **大屏强调色强制规则（避免深底不可见）**：`default` 主题的 `--accent-gold` 是 `transparent`，直接用作大屏数字/标题色时**完全不可见**。`pc/dashboard.html` **必须**在页面顶部 `<style>` 内重新定义大屏专用强调色变量（覆盖 design-tokens），三套主题各自有值：
> - `--db-accent` / `--db-accent-2` / `--db-accent-warm` — KPI 数字/标题强调色 + 辅助渐变色 + 金银铜奖牌色
> - `--db-text` / `--db-text-dim` — 大屏正文/次要文字色（深底固定浅灰）
> - `--db-bar-bg` — 进度条底色
> - `--db-good` / `--db-warn` / `--db-bad` — 告警三态色
> - `--db-glow` — Logo/告警发光阴影
>
> 大屏所有强调元素一律用 `var(--db-accent)`；ECharts 文字色通过 `getComputedStyle` 读 CSS 变量传入（详见 [dashboard.md 5 / 7](references/dashboard.md)）。

> **地图级别匹配（仅在"已决定加地图"时使用）**：
> | 业务关键词 | 地图级别 | adcode 格式 | 作初始层级？ |
> |---|---|---|---|
> | 含"全国/省际/全国物流/全国态势" | 国家级 | 100000 | ✅ 推荐 |
> | 明确省名（如"广西/江苏省内"） | 省级 | 6 位（省码+0000） | ✅ 推荐 |
> | 明确市名（如"南宁市内"） | 市级 | 6 位（省码+市码） | ✅ 推荐（最小可到这一级） |
> | 明确区/县/校名 | 区县级 | 6 位 | ❌ 不推荐（数据碎片化，仅作下钻终点） |
>
> **关键原则**：
> - **初始层级 = 业务决定**，可任意选 全国/省/市 一级（**最小到市级**）
> - 国家级 100000 作初始时，可下钻到 省/市/区县
> - 省级作初始时，可下钻到 市/区县（**不能**向上"回到全国"，除非显式提供「返回全国」入口）
> - 市级作初始时，可下钻到 区/县（**不能**向上回到省/全国）
> - "当前层级"标识 = `breadcrumbStack[breadcrumbStack.length - 1].name`，**不是固定常量**
>
> 这个表**只解决"加地图时用哪一级"**，不解决"是否要加地图"。完整 adcode 速查、URL 模板、ECharts 视觉参数详见 [dashboard.md 6 节](references/dashboard.md#6-地图组件echarts--datav-geojson)。

> **模板代码详见**：[references/examples.md](references/examples.md)，包含 PC 端页面模板、App 端页面模板、登录页/框架页/入口页模板、代码风格范例、附录（CSS/JS 共享资源完整代码）。
>
> **地址 → 地图增强**：当数据模型里有地点字段（地址/经纬度等），PC 详情弹窗内嵌折叠地图面板，App 详情页内嵌小地图卡片 + 唤起原生地图 App。详见 [references/tianditu-map.md](references/tianditu-map.md)。
>
> **天地图 Key 处理（强制）**：生成项目时**必须**从 [references/config.md](references/config.md) 的 `TIANDITU_KEY` 字段读取 Key，直接写入 `shared/components.js` 顶部的 `var TIANDITU_KEY = '…';`（**不要保留 `YOUR_TIANDITU_KEY` 占位符**）。Key 需要更新时,只改 `config.md` 这一处即可同步到所有原型项目。

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
│   ├── dashboard.html             # PC 数据大屏（必备，暗色驾驶舱；布局按需求动态生成）
│   └── *.html                     # 各业务页面
├── app/                           # App 移动端
│   ├── index.html                 # 首页（固定第一个 Tab，含底部 Tab Bar + 角色切换）
│   ├── profile.html               # 个人中心（固定最后一个 Tab "我的"）
│   ├── *.html                     # 中间 Tab 自定义页（1~2 个）+ 各业务子页面
│   └── assets/
│       └── app.css                # App 端专用样式
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
>
> **例外 — 风格总览页是自包含页**：`styleguide.html` **不引用** `shared/design-tokens.css`、`shared/components.css`、`app/assets/app.css`，所有样式（CSS 变量 + 组件样式 + App 样式）全部内联在 `<style>` 中，脚本也全部内联在 `<script>` 中，仅外链 CDN 的 Bootstrap CSS/JS 与 Icons。详见 [references/styleguide.md](references/styleguide.md)。

---

## 二、从零生成项目的步骤

当用户说"帮我生成一个XXX管理系统原型"时，按以下顺序执行：

### 第 0 步：识别主题风格

在理解需求前，**先提取"XXX 原型"中的系统名称 XXX**，按 [references/themes.md](references/themes.md) 的「自动识别逻辑」在该系统名称内匹配关键词，确定 `data-skin` 值（`default` / `gov` / `party`）。**不得**从系统名称之外的背景描述、功能说明等文字中识别主题。

主题确定后，**整个项目所有页面（PC + App + 登录 + 根导航）**统一在 `<html>` 上写该 `data-skin`，项目级整体应用（详见[第八章](#八主题风格自动识别生成时固定)）。

> **预览三套风格效果**：打开 [references/styleguide/index.html](references/styleguide/index.html) 入口页，分别进入 `default.html` / `gov.html` / `party.html` 查看完整风格规范（每页已固定显示各自主题，不做切换）。
> **生成项目自动含风格总览页**：从零生成项目时，会在根 `index.html` 添加"风格总览"入口卡片（指向项目内的 `styleguide.html`）。**按 [references/styleguide.md](references/styleguide.md) 规范生成 `styleguide.html`**；**PC 侧边栏不放"风格总览"菜单**。

### 第 1 步：理解需求，规划页面

从用户描述中提取：
- **系统名称**
- **功能模块**
- **每个模块需要哪些页面**（PC 列表/详情/表单，App 列表/详情/表单）

输出页面清单供用户确认。

**地点字段识别（贯穿后续生成，不依赖用户提示）**：
- 扫描数据字段名，命中 `address / location / 地址 / 位置 / 坐标 / 经纬度 / lng / lat / 地点 / 场所 / 站点 / 园区 / 门店 / 仓库 / 工地 / 项目地` 等关键词 → 标记为「地点字段」
- 也扫描字段值，命中 `省/市/区/县/路/街/号/栋/楼` 等中文地名词 → 同样标记
- 一旦标记，PC 详情弹窗与 App 详情子页**自动**接入地图组件（[references/tianditu-map.md](references/tianditu-map.md)）

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
| `shared/design-tokens.css` | CSS 变量（三套主题） | 附录 A |
| `shared/components.css` | 全局组件样式 | 附录 B |
| `shared/components.js` | 30+ 工具函数 | 附录 C |
| `app/assets/app.css` | App 端专用样式（含手机模型框架） | 附录 D |

### 第 4 步：生成框架文件

| 文件 | 模板位置 |
|------|----------|
| `index.html`（根导航） | [examples.md 四、根导航入口页](references/examples.md#四根导航入口页-indexhtml) |
| `styleguide.html`（风格总览） | 按 [references/styleguide.md](references/styleguide.md) 规范生成 |
| `login/index.html` | [examples.md 三、登录页模板](references/examples.md#三登录页模板) |
| `pc/index.html`（PC 框架） | [examples.md 五、PC 框架页](references/examples.md#五pc-端框架页-pcindexhtml) |
| `pc/index-content.html`（首页） | Dashboard 仪表板模板 |
| `app/index.html`（App 首页，固定第一个 Tab） | Tab 页模板 |
| `app/profile.html`（App "我的"，固定最后一个 Tab） | Tab 页模板 |
| 中间 Tab 自定义页（1~2 个，按需求） | Tab 页模板 |

### 第 5 步：生成业务页面

根据需求，为每个模块创建 PC + App 页面，模板详见 [examples.md 第一~二章](references/examples.md)。

### 第 6 步：注册到框架

- 更新 `pc/index.html` 的 sidebar 菜单、`_knownPages` 数组、`data-active-menu` 映射
- 更新 `app/index.html` 的快捷操作按钮
- 更新根 `index.html` 的页面计数

---

## 三、PC 端页面关键约束

### 3.0 全局按钮规范（PC 端所有按钮适用）

PC 端**所有可交互按钮**（含操作列、筛选栏、表单、弹窗、六态、分页等全部场景）必须遵守以下规则：

1. **图标 + 文字**：每个按钮内必须包含 Bootstrap Icons 图标和中文名称，格式为 `<i class="bi bi-xxx"></i> 名称`
2. **禁止仅用图标**：如 `<i class="bi bi-eye"></i>` 单独出现
3. **禁止无图标的纯文字按钮**：如 `<button>查看</button>`
4. **整体间距**：同一行多个按钮并排时用 `d-flex gap-2` 容器（或 `ms-2`）拉开距离，禁止贴在一起

按钮配色与图标按业务语义选型，不可随意搭配（详见下方 [3.1 操作列配色表](#31-列表页操作列)）。

### 3.1 列表页操作列

操作列按钮**必须同时满足以下五条约束**：

1. **按需取舍**：操作列放哪些按钮由**业务需求**决定，按配色表选型，**禁止无脑全放**——不需要的操作（如删除、审核、导出等）就不放对应按钮。
2. **图标 + 名称**：每个按钮内必须包含 Bootstrap Icons 图标和中文名称，格式为 `<i class="bi bi-xxx"></i> 名称`
3. **水平排列、不换行**：`<td>` 加 `class="text-nowrap"`，`<th>` 设 `white-space:nowrap` 和足够的 `width`（通常 220px+）
4. **相邻按钮保留间距**：多个按钮并排时用 `d-flex gap-2` 容器（或给非首个按钮加 `ms-2`）拉开距离，禁止贴在一起
5. **功能适配闭环**：操作列中**已放置的每个按钮都必须有对应的 `onclick` 函数和实际交互**，禁止"只有按钮没有功能"——查看→`showDetail()`、编辑→`editItem()`、新增→`openAddForm()`、删除→`deleteItem()`（`confirmModal` 确认后删行 + Toast）；其余按钮（审核通过/驳回/导出/启用/停用等）同样须有对应处理函数 + Toast。

**按钮配色与图标规范（按业务语义选型，不可随意搭配）：**

| 操作 | 配色 | 图标 | 示例 |
|------|------|------|------|
| 查看/详情 | `btn-outline-primary` | `bi-eye` | `<i class="bi bi-eye"></i> 查看` |
| 编辑 | `btn-outline-secondary` | `bi-pencil` | `<i class="bi bi-pencil"></i> 编辑` |
| 删除 | `btn-outline-danger` | `bi-trash` | `<i class="bi bi-trash"></i> 删除` |
| 新增/添加 | `btn-outline-success` | `bi-plus-lg` | `<i class="bi bi-plus-lg"></i> 新增` |
| 审核通过/批准 | `btn-outline-success` | `bi-check-circle` | `<i class="bi bi-check-circle"></i> 通过` |
| 驳回/拒绝 | `btn-outline-danger` | `bi-x-circle` | `<i class="bi bi-x-circle"></i> 驳回` |
| 导出 | `btn-outline-primary` | `bi-download` | `<i class="bi bi-download"></i> 导出` |
| 提交 | `btn-outline-primary` | `bi-send` | `<i class="bi bi-send"></i> 提交` |
| 配置/设置 | `btn-outline-secondary` | `bi-gear` | `<i class="bi bi-gear"></i> 配置` |
| 启用/展示 | `btn-outline-success` | `bi-eye` | `<i class="bi bi-eye"></i> 展示` |
| 禁用/停用 | `btn-outline-warning text-dark` | `bi-pause-circle` | `<i class="bi bi-pause-circle"></i> 停用` |

```html
<th style="width:220px;white-space:nowrap;">操作</th>
...
<td class="text-nowrap">
  <div class="d-flex gap-2">
    <button class="btn btn-sm btn-outline-primary" onclick="showDetail(this)" title="查看"><i class="bi bi-eye"></i> 查看</button>
    <button class="btn btn-sm btn-outline-secondary" onclick="editItem(this)" title="编辑"><i class="bi bi-pencil"></i> 编辑</button>
    <button class="btn btn-sm btn-outline-danger" onclick="deleteItem(this)" title="删除"><i class="bi bi-trash"></i> 删除</button>
  </div>
</td>
```

### 3.2 详情/新增/编辑 → 弹窗模式

列表页的详情/新增/编辑统一用 Bootstrap Modal 实现：
- `#[module]DetailModal` — 详情展示，modal-lg
- `#[module]FormModal` — 新增/编辑表单

### 3.3 分页（数据量 + 分页栏标准结构）

列表数据至少 **11~20 条**，确保默认每页 10 条时能产生分页效果。

分页栏模板见 [examples.md 1.2 列表页模板](references/examples.md#12-列表页含筛选栏表格分页弹窗六态)。

**标准分页栏结构（必须与规范一致，不可自行改动）：**

```html
<div class="pagination-bar d-flex justify-content-between align-items-center">
  <span class="page-info">共 N 条，第 1/1 页</span>   <!-- 左侧：页信息，必须用 span -->
  <div class="d-flex gap-2 align-items-center">      <!-- 右侧：每页条数 + 翻页按钮 -->
    <select class="form-select form-select-sm d-inline-block" style="width:auto;min-width:90px;" onchange="changePageSize(this.value)">
      <option value="10" selected>10条/页</option><option value="30">30条/页</option><option value="50">50条/页</option><option value="100">100条/页</option>
    </select>
    <div>                                            <!-- 注意：按钮容器是普通 div，不是 d-flex gap-2 -->
      <button class="btn btn-sm btn-outline-secondary page-btn" onclick="goPage(currentPage-1)">上一页</button>
      <button class="btn btn-sm btn-outline-secondary page-btn" onclick="goPage(currentPage+1)">下一页</button>
    </div>
  </div>
</div>
```

**关键约束：**
- 分页栏容器：`pagination-bar d-flex justify-content-between align-items-center`
- `.page-info` **必须用 `<span>`**，不可用 `<div>`——`updatePaginationUI` 通过 `querySelector('.page-info')` 动态更新其 `textContent`；**位于分页栏左侧**，文字是 `共 N 条，第 X/Y 页`
- 按钮**必须带 `page-btn` class**——`updatePaginationUI` 通过 `.page-btn:first-child` / `.page-btn:last-child` 定位上一页/下一页按钮并控制 disabled 状态
- 按钮文字必须是 **"上一页""下一页"**，不可仅用 chevron 图标；按钮上**不要**加 `disabled` 初始状态（由 `updatePaginationUI` 动态控制）
- **每页条数选择器**：`<select>` 绑定 `changePageSize(this.value)`，默认选中 `10`，option 文字用 `10条/页` 格式（如 `10条/页`/`30条/页`/`50条/页`/`100条/页`），放在右侧 `d-flex gap-2` 容器内
- **禁止**右侧再嵌套 `d-flex gap-2` 包按钮或加"每页/条"文字前缀——保持与规范结构完全一致
- 初始化必须调用 `initPagination(10)`

### 3.4 PC 端导航

- **弹窗模式（推荐）**：`new bootstrap.Modal(document.getElementById('detailModal')).show()`
- **页面跳转（PC 框架内）**：菜单 `<a>` 必须是 `class="sidebar-nav-link"` + `href="xxx.html"` + `data-url="xxx.html"` 三件套。**不要写** `target="mainFrame"`（iframe sandbox 下失效）。框架为单 iframe 机制（无多页签栏）：菜单点击、业务页跳转（详情 Modal「在地图中查看」、顶栏通知等）统一用 `parent.loadPage('xxx.html')` 直接切换 iframe，切换后侧边栏高亮自动同步。
- **面包屑跳转**：PC 内容页用 `<a href="xx.html" onclick="parent.loadPage('xx.html')">` 跳转，**不要**用 `target="mainFrame"`。
- **确认操作**：`confirmModal('标题', '内容', callback)`（业务页需自带 `#confirmModal` 节点，见 examples.md 1.7）

> PC 框架页定义 `window.loadPage = function(url){...}` 与 `window.openMapTab = function(url, title){...}`（地图场景兼容入口，内部即 `loadPage`）全局函数。详见 [examples.md 第五章](references/examples.md#五pc-端框架页-pcindexhtml)。

### 3.5 六态

每个 PC 内容页面必须在 `#page-content` 末尾包含：空数据(`state-empty`)、筛选空(`state-empty_filter`)、加载中(`state-loading`)、错误(`state-error`)、网络错误(`state-network_error`)。

### 3.7 表格列数一致性

**所有表格必须确保 `<thead>` 中的 `<th>` 数量与 `<tbody>` 中每行 `<td>` 数量严格一致。**

```html
<!-- 正确示例：thead 和 tbody 列数一致 -->
<thead>
  <tr>
    <th>#</th>
    <th>[列名1]</th>
    <th>[列名2]</th>
    <th>[列名3]</th>
    <th>操作</th>
  </tr>
</thead>
<tbody>
  <tr>
    <td>1</td>
    <td>[列名1值]</td>
    <td>[列名2值]</td>
    <td>[列名3值]</td>
    <td class="text-nowrap"><!-- 操作按钮 --></td>
  </tr>
</tbody>
```

**常见错误**：AI 在 tbody 中根据业务需求自动添加了额外的数据列（如状态 badge、标签等），但忘记了在 thead 中对应添加标题列，导致列数错位。

**技巧**：先确定业务需要几列数据，在 thead 中定义好所有列标题，再填充 tbody 的数据行，确保一一对应。

### 3.8 通用页面壳

每个 PC 内容页面的标准 HTML 壳参见 [examples.md 1.1 通用页面壳](references/examples.md#11-通用页面壳)。

---

## 四、App 端页面关键约束

### 4.1 手机模型框架

所有 App 页面统一使用 `phone-frame` 浅色无边框手机外框结构：
- 浅灰底色 #e8eaed、390×844px 圆角外框
- flexbox 列布局：状态栏 → 导航栏 → 内容区 → 底部 Tab
- 无黑影边框、无灵动岛
- 内容区独立滚动，状态栏/导航栏/底部 Tab 固定

### 4.2 底部 Tab 栏（Tab Bar）

App 底部导航 Tab 规则：

1. **首尾固定**：第一个 Tab 固定「首页」（`app/index.html`），最后一个固定「我的」（`app/profile.html`）。
2. **中间自定义（1~2 个，按需增减）**：中间 Tab 由 AI 按业务需求取名、选图标；**实在没有合适内容时回退用「消息」**。
3. **中间 Tab 须符合移动端设计**：用用户视角的高频入口（如「事项」「服务」「工作台」「预约」「办事」等 2~4 字命名 + 语义清晰图标）；**禁止照搬 PC 管理端后台标签**（如「用户管理」「数据管理」「权限配置」「系统设置」等）。

> 若需求明确指定了底部 Tab，则按需求来。

### 4.3 Tab 页与子页

| 类型 | 特征 | nav-header |
|------|------|------------|
| Tab 页 | 有 `.phone-tabbar` | `<h1 class="nav-title">标题</h1>` + `<div class="nav-actions">` |
| 子页面 | 无 `.phone-tabbar`，有返回箭头 | `.nav-left > .nav-back` + `.nav-title` |

### 4.4 App 端导航

- Tab 页用 `location.href = 'xxx.html'`
- 子页面用 `<a class="nav-back" href="parent.html">`，浏览器原生跳转即可。
- 业务页面**不要**自写跨页跳转函数；所有跳转都通过原生 `<a href>` 完成。

### 4.5 App 端六态

六态放在 `.phone-content` 末尾：空数据/筛选空(清除筛选按钮)/加载中(spinner)/错误(重试按钮)/网络错误。

### 4.6 App 端本地函数

每个 App 页面需定义本地 `showToast()` 和 `showState()` 函数。

---

## 五、PC 框架页关键配置

PC 框架页完整模板及 Sidebar 菜单格式参见 [examples.md 五 PC 框架页](references/examples.md#五pc-端框架页-pcindexhtml)。

**PC 框架页 header 结构：** header 内部左侧必须是 `d-flex align-items-center gap-2` 包裹层（**不是** `header-left`，但 CSS 同时兼容 `.header-left` 类名），依次包含 LOGO 和汉堡按钮，结构如下：

```html
<header class="header-navbar">
  <!-- 关键：LOGO 与汉堡按钮必须同处一个直接子元素内，二者并排显示在 header 最左侧；header 直接子元素只能是「左侧包裹层」+「.header-right」两个，禁止把 LOGO / 汉堡按钮拆成两个独立子元素，否则会被 space-between 挤到中间位置 -->
  <div class="d-flex align-items-center gap-2">
    <div class="header-logo"><i class="bi bi-xxx"></i> [系统名称]</div>
    <button class="navbar-toggler-responsive" onclick="toggleSidebar()"><i class="bi bi-list"></i></button>
  </div>
  <div class="header-right">
    <!-- 环境徽标、通知、用户下拉 -->
  </div>
</header>
```

**深色侧边栏特点：**
- 深色背景 `#1F2329`，菜单项圆角 6px
- 分组间用 `sidebar-divider` 分隔，标题用 `sidebar-section-title`
- 激活态：左侧 3px 蓝色细线条 + 半透明蓝色背景，文字白色
- 单一 iframe 区域承载所有业务页面，导航通过左侧菜单完成
- **隐藏滚动条**：`.sidebar` 设置 `overflow-y: auto` 保留滚动功能，但需添加 `scrollbar-width: none`（Firefox）和 `::-webkit-scrollbar { display: none }`（Chrome/Safari）隐藏滚动条外观

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
- [ ] **主题识别已执行（第 0 步）**：仅在"XXX 原型"的系统名称 XXX 中扫描党建/政企类关键词，确定 `data-skin` 值；所有页面（含 PC 框架/业务页/App 页/登录页/根导航页）`<html>` 标签带**统一**的 `data-skin` 属性（默认 `default`）—— 这是**项目级**应用，不是单页设置
- [ ] **风格总览页已生成且完整**：从零生成项目时，自动创建 `styleguide.html`，**按 [references/styleguide.md](references/styleguide.md) 规范生成**；`data-skin` 与项目主题一致；**所有样式/脚本内联，不引用 shared/ 和 app/ 下的 CSS/JS 文件**；在根 `index.html` 第 4 卡片注册入口；**PC 侧边栏不放"风格总览"菜单**
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
- [ ] **PC 框架页 header 子元素结构**：`header.header-navbar` 直接子元素只能是「左侧包裹层（`.header-left` 或 `.d-flex`，内含 LOGO + 汉堡按钮 `navbar-toggler-responsive`）+ `.header-right`」两个，**禁止**把 LOGO 和按钮拆成两个独立直接子元素（会被 `justify-content: space-between` 挤到中间）
- [ ] `body class="bg-light"`（App 加 `phone-frame-body`）
- [ ] 六态全部包含（正常/空数据/筛选空/加载中/错误/网络错误）
- [ ] App Tab 页有 `.phone-tabbar`，非 Tab 页有返回箭头 `.nav-back`
- [ ] App 底部 Tab：首「首页」+ 尾「我的」固定；中间 1~2 个自定义（符合移动端设计、禁止照搬后台管理标签，无合适内容回退「消息」）
- [ ] PC 详情/新增/编辑优先用弹窗模式（Bootstrap Modal 嵌入列表页）
- [ ] **PC 端所有按钮图标+文字**：全 PC 端（操作列/筛选栏/表单/弹窗/六态/分页等）所有按钮必须同时包含 Bootstrap Icons 图标和中文名称，禁止纯图标或纯文字按钮
- [ ] PC 操作列：`<button class="btn btn-sm btn-outline-primary"><i class="bi bi-xxx"></i> 文字</button>`，`td class="text-nowrap"`，多按钮用 `d-flex gap-2` 保持间距
- [ ] PC 侧边栏菜单 `<a>` 用 `class="sidebar-nav-link"`，并带 `href="..."` + `data-url="..."`（**不写** `target="mainFrame"`）
- [ ] PC 框架内跳转用 `<a href="xxx.html" onclick="parent.loadPage('xxx.html')">`（不写 `target="mainFrame"`）
- [ ] App 导航用 `location.href`
- [ ] 表单页有 `data-dirty` 属性
- [ ] App 页面有本地 `showToast()` 定义
- [ ] 所有颜色用 CSS 变量（主题色 `var(--primary)`，默认 `#3370FF`，政企 `#1E3A8A`，党建 `#C9302C`）
- [ ] 带分页的列表：数据量 11~20 条、`initPagination(10)`、分页栏含页面大小选择器(10/30/50/100)+上一页/下一页按钮+`page-btn` class、`.page-info` 用 `<span>`
- [ ] **表格列数一致**：`<thead>` 中的 `<th>` 数量与 `<tbody>` 中每行 `<td>` 数量严格一致，tbody 根据业务需求增加的列，thead 必须对应添加标题列
- [ ] **地址 → 地图（仅当数据含地点字段时）**：PC 详情弹窗嵌入折叠地图面板（`address-map-container` + `renderAddressMap`），App 详情子页嵌入小地图卡片（`address-map-card` 180px 高 + `openInAMap` 唤起原生）；iframe 加载失败有兜底外链；高德公开页 URL，无需 Key
- [ ] **天地图 Key 已写入**：`shared/components.js` 顶部 `TIANDITU_KEY` **必须**已替换为 [references/config.md](references/config.md) 中的真实值,不允许保留 `YOUR_TIANDITU_KEY` 占位符
- [ ] 中文文本（标签、提示、占位符）
- [ ] App 状态栏统一格式：时间 9:41 + 信号/电池图标
- [ ] **PC 数据大屏通用骨架自检（dashboard.html）**：见 [dashboard.md §5 经验沉淀](references/dashboard.md#5-经验沉淀踩过的坑--作为参考不是规定)，**通用规则**：① 总高 `100vh; overflow: hidden`；② ECharts 用 `ResizeObserver` 监听容器；③ CSS 变量驱动主题色；④ 顶层 CSS Grid 分配高度（不用每段独立 height）；⑤ 不引用 `shared/components.css`（避免浅色卡片污染）；⑥ 加地图时遵循 [§4 地图组件](references/dashboard.md#4-地图组件仅在-13-决定加地图时使用)

### PC 数据大屏自检要点（实战必看）

- [ ] **Grid/Flex 容器三件套（强制 · 避免图表不可见）**：① 每个 `.db-panel` 必须有 `display:flex; flex-direction:column; min-height:0`；② 每个图表 div 必须有 `min-height` 兜底（220px / 460px）；③ iframe 内嵌时父窗口 resize 后子页面要主动 `chart.resize()`。详见 [dashboard.md §0.3](references/dashboard.md#03-echarts-自适应模板所有图表通用)「Grid/Flex 容器三件套」。**违反此条 = 图表容器高度为 0 = ECharts 渲染失败但 canvas 已存在，看似没内容**
- [ ] **ECharts 工厂加调试日志**：工厂入口打 `console.log('[Chart] init xxx: WxH')`，便于排查布局问题
- [ ] **地图占满空余地方**：主区 grid `260px 1fr 260px`（左右业务列不超过 280px）；KPI 砍到 4 个、行高 88px；总 padding 8×12
- [ ] **地图四象限 UI 元素位置（必须严格遵守，不允许合并堆叠）**：
  - **左下**：返回上级按钮（`.db-map-back` 单独按钮，初始 `disabled`）
  - **左上**：工具栏（刷新按钮，可放其他次要按钮）
  - **右上**：面包屑（`.db-map-breadcrumb`，点击任意级跳回）
  - **右下**：悬浮统计 pill（`.db-map-stats`，订单/车辆/司机汇总）
  - **禁止**：把"返回按钮 + 刷新按钮"合并到一个左上/右上容器；禁止把面包屑放左上；禁止把悬浮统计放左下（与返回按钮冲突）
- [ ] **地图交互按钮可点击**：返回按钮、刷新按钮、面包屑项必须加 `pointer-events: auto`，否则会被 canvas + loading 蒙层拦截
- [ ] **地图 label 防撞色三件套（强制）**：默认 label 必须有 `textBorderColor` + `textBorderWidth`（建议加 `textShadow` 双保险）；emphasis/select 用 `#fff` + 更深更粗的描边。否则浅色字糊在主题色透明底上，地名看不清。详见 [dashboard.md §4](references/dashboard.md#4-地图组件仅在-13-决定加地图时使用)「地图 label 颜色防撞色三件套」
- [ ] **地图容器兜底**：`.db-map { width:100%; height:100%; min-height: 420px }`；init 时若 `clientHeight===0` 强制 min-height；`setTimeout(resize, 200)` 延迟双保险
- [ ] **地图暗夜配色**：边框 `rgba(accent, 0.45)` 半透明；emphasis 边框用 `accent`；**visualMap 配色用 `[rgba(accent, 0.06), rgba(accent, 0.5)]` 二段低透明，禁止 `barBg→accent→accent2` 三段渐变**
- [ ] **散点 value 结构**：scatter `{ name, value: [lng, lat, bizValue] }` 三元素；`symbolSize: val[2]` 取业务值
- [ ] **异常处理**：render 包独立 try/catch 区分"加载失败 vs 渲染异常"；catch 文案带 `err.message`；暴露 `window.__dbgMap = { el, chart }` 与 `console.log` 日志
- [ ] **网络容错**：多 CDN 顺序尝试；国家级内置矩形 GeoJSON 兜底（`buildFallbackCountryGeo()`）；下钻层级失败自动退回国家级 + Toast
- [ ] **错误三态文案分离**：① loading spinner + "加载 xxx 地图..."；② 错误态显示 `err.message` + "重新加载"按钮；③ demo 模式顶部横幅 "⚠ 当前为演示数据"
- [ ] **KPI 数字递增**：保留 `.unit` 子节点，只替换数字文本；用 `data-prefix`/`data-suffix`/`data-decimals` 三个 dataset 属性驱动；`toLocaleString('zh-CN')` 格式化
- [ ] **ECharts 工厂必须用 `theme.xxx`**：`autoResizeChart(id, factory)` / `autoResizeMap(id, factory)` 的工厂签名统一为 `function(chart, theme)`，所有 `--db-*` 颜色通过 `theme.accent` / `theme.accent2` / `theme.accentWarm` / `theme.text` 等读取；**禁止在工厂内 `var xxx = cv('--db-xxx')` 自行声明**（复制粘贴极易遗漏 → 触发 `xxx is not defined at autoResizeChart`，典型 `accentW`）。详见 [dashboard.md §0.3](references/dashboard.md#03-echarts-自适应模板所有图表通用)
- [ ] **visualMap.max 容错**：`if (!isFinite(max) || max <= 0) max = 1` 避免 0 值告警
- [ ] **初始层级变量化**：业务决定 `ROOT_ADCODE`（全国/省/市，最小到市级），不要硬编码 100000；HTML「当前层级」初值 = `ROOT_NAME`；兜底回退 = `loadLevel(ROOT_ADCODE, ROOT_NAME)`；返回按钮初始 disabled（栈底就是 ROOT）

---

## 八、主题风格（自动识别，生成时固定）

技能内置 **三套主题**（默认 `default` / 政企 `gov` / 党建 `party`），以**背景**为主要视觉区分，共享同一套布局/组件/交互，仅颜色变量不同。主题在生成时由关键词识别**一次性确定**并写入 `<html data-skin="...">`，**不支持运行时切换**。

**触发关键词、自动识别逻辑、主题固定规则、FOUC 脚本、色板与组件级适配，统一以 [references/themes.md](references/themes.md) 为唯一来源**。此处仅保留执行要点：

- **识别时机**：第 0 步在"XXX 原型"的系统名称 XXX 中匹配关键词，输出 `data-skin` 值（默认 `default`）。
- **项目级应用**：所有页面（PC 框架/业务页/App/登录/根导航/风格总览）的 `<html>` 统一写该 `data-skin`。
- **禁止运行时切换**：任何页面都不放主题切换按钮，不提供 `cycleSkin` / `setSkin` / `getSkin`，不读不写 `localStorage.skin`。
- **CSS 变量驱动**：颜色全部走 `var(--primary)` 等变量，禁止硬编码主题色。
- **正交叠加（仅 App 端）**：`data-skin` 与 `data-theme="dark"`（暗色）可叠加；暗色仅 App 端，PC 端不提供。
- **FOUC 脚本（仅 App 端）**：仅在 App 页 `<head>` 内、CSS 前放暗色阻止脚本（只读 `theme`，不读 `skin`），完整脚本见 themes.md。

---

## 九、风格总览页（styleguide.html）

从零生成项目时，按 [references/styleguide.md](references/styleguide.md) 规范生成 `styleguide.html`。

> **FOUC 阻止脚本**（仅 App 端页面在 `<head>` 内同步执行，CSS 之前）——只处理暗色模式，**不读取 `skin`**（完整脚本见 [references/themes.md](references/themes.md)）。
