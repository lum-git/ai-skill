# 风格总览页（styleguide.html）规范

## 用途

从零生成项目时，自动创建 `styleguide.html`，作为当前主题的完整视觉规范参考页，用于核对主题色系、组件样式、字体级别、业务模块、PC 框架布局、App 手机模型等。

## 生成方式

以 `references/styleguide/` 下与项目同主题的完整实现文件为唯一蓝本，**一比一复刻**：

| 项目主题 | 蓝本文件 |
|---------|---------|
| default（品牌蓝） | `references/styleguide/default.html` |
| gov（政务藏蓝） | `references/styleguide/gov.html` |
| party（党旗红） | `references/styleguide/party.html` |

**复刻要求**

- HTML 结构、`<style>` 全部样式（CSS 变量 + 组件样式 + App 样式 + 框架预览样式）、`<script>` 全部脚本，逐段照搬，不删减、不改写。
- 仅替换系统名称相关文案（`<title>`、页头标题、页脚信息），其余结构、数据、示例文案一律保持与蓝本一致。
- `data-skin` 值及标题中的风格名与项目主题一致（`default` / `gov` / `party`）。
- **自包含**：不引用 `shared/design-tokens.css`、`shared/components.css`、`app/assets/app.css`；不放 FOUC 暗色脚本；仅外链 CDN 的 Bootstrap CSS/JS 与 Bootstrap Icons。
- 主题特化规则（政企顶栏金线、党建金色元素等）已内联于蓝本样式中，复刻即自动生效，无需额外处理。

## 7 个必需区块

页面须包含以下 7 个区块，按顺序排列，缺一不可：

| # | 区块 | 说明 |
|---|------|------|
| 01 | 色彩 | 主色板 10 色卡（主色/悬停/按下/浅底/点缀/成功/警示/危险/背景/侧边栏）；default 另加文字色卡 |
| 02 | 字体 | H1~H4 + 正文 + 小字共 6 级字号，展示实际文本效果 |
| 03 | 组件 | 按钮 7 种、徽章 6 种、数据小卡 4 个 |
| 04 | 业务模块 | 3 个模块卡片（图标/标题/描述/功能列表） |
| 05 | 列表 | 图文列表（news-card）+ 数据表格（含表头、操作列） |
| 06 | PC 框架 | 真实 `header-navbar` + `sidebar` + `main-layout` 布局演示，支持折叠 |
| 07 | App 移动端 | 真实 `phone-frame` 手机模型（状态栏/导航栏/内容区/底部 Tab） |
| 08 | PC 数据大屏（可选） | 当项目含 `pc/dashboard.html` 时追加；展示三栏暗色驾驶舱布局 + 地图占位 + KPI 卡片样式 |

## 页面结构

1. **头部 `.sg-header`**：渐变深色背景 + 径向光晕 + 右上角徽章；含标题、副标题、主题标签
2. **7 个 `.sg-section`**：悬浮白色卡片，左上编号角标，`margin` 负值重叠效果
3. **页脚**：系统名 + 主题风格 + 标语

## 生成要点

- 色卡中的色值文字（如 `#C9302C`）硬编码在 HTML 中，不做 JS 读取。
- 内联脚本必须包含：`showToast`、`toggleSidebar`（localStorage 记忆折叠状态）、`closeSidebar`、折叠状态初始化自执行函数。
- 在根 `index.html` 第 4 卡片注册入口（`href="styleguide.html"`）；PC 侧边栏不放"风格总览"菜单。
- 暗色变量仅作为 CSS 定义存在，页面不执行暗色模式切换。

## 08 区块：PC 数据大屏（仅含 dashboard.html 的项目）

**触发条件**：仅当项目包含 `pc/dashboard.html` 时追加；不含则跳过。

**包含内容**（自包含样式，复刻同主题 dashboard.html 的视觉，但用占位元素不接 ECharts）：

| 子区块 | 说明 |
|--------|------|
| 暗色背景渐变 | `linear-gradient(180deg, var(--db-bg-from), var(--db-bg-to))` 整块铺设 |
| 标题区 | 28px 金红渐变文字 + 实时时间占位（不真跑 setInterval） |
| 三栏布局 | 320px / 1fr / 320px grid，左 KPI+榜单 / 中地图占位 / 右进度+待办 |
| KPI 卡片 4 个 | 2×2 网格，金色大数字 + 浅灰小标签 |
| 地图占位 | 用虚线边框 + 主题色文字"地图区域"代替真地图（避免外网请求） |
| 排行榜 5 行 | 序号 + 名称 + 进度条 + 数值 |
| 主题强条示例 | `--accent-gold` / `--primary` 在面板边框、标题、地图高亮的应用 |

**生成要点**：
- 自包含内联样式，不引用 `shared/dashboard.css`
- 地图区域**不接 ECharts**（避免外网请求），用静态占位
- 实时时间**不跑 setInterval**（写死一个时间字符串"2026-08-22 14:30:25"）
- 暗色规则同 [themes.md 第八章](themes.md#八pc-数据大屏暗色规则)

## 参考实现

| 文件 | 说明 |
|------|------|
| `references/styleguide/default.html` | 默认风格完整实现 |
| `references/styleguide/gov.html` | 政企风格完整实现 |
| `references/styleguide/party.html` | 党建风格完整实现 |