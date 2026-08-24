# PC 数据大屏 `pc/dashboard.html`（驾驶舱子系统）

> **本文件是驾驶舱子系统的指导规范**，与 PC 业务页 (`examples.md`) 完全分离。
>
> **重要说明**：驾驶舱**没有唯一正确的模板**。业务不同（物流调度 / 销售监控 / 运维态势 / 党建风采），驾驶舱的核心模块、视觉重心、配色密度都不一样。本规范只沉淀**通用骨架**（CSS 变量、布局机制、自适应方案、ECharts 接入）和**典型范式参考**（业内常见的几种布局思路），**具体业务该展示什么，由 AI 根据需求自主判断**。

---

## 0. 通用骨架（与业务无关，所有驾驶舱都适用）

### 0.1 基础特性

| 维度 | 规则 |
|------|------|
| 形态 | **驾驶舱**（暗色大屏风格），**单屏不滚动**，1920×900 fit iframe |
| 容器 | **直接铺满 iframe**，不嵌 `#page-content`，无内边距 |
| 总高度 | **`html, body { height: 100%; overflow: hidden }`**，所有区块高度相加 ≤ 100vh |
| 字号 | KPI 数字 ≥ 44px（推荐 48~56px），标题 22~28px，面板标题 13~14px |
| 背景 | **强制暗色 + 径向渐变光晕**：`linear-gradient` 用 `var(--db-bg-from)` / `var(--db-bg-to)`；叠加左上 + 右下 `radial-gradient` 光晕 |
| 组件 | **不引用** `shared/components.css`，直接内联样式（避免后台浅色卡片污染） |
| 路由 | iframe 加载（与业务页一致），侧边栏独立菜单 |
| 主题 | `<html data-skin="[识别结果]">`，与项目一致；**所有颜色全部走 CSS 变量** |
| 图表 | ECharts 5.5，**所有色值用 `getComputedStyle()` 读 CSS 变量**（ECharts 不解析 var()） |
| 时间 | 顶栏固定显示**实时时间**（`setInterval` 1s 刷新） |
| 数据 | 演示数据 hardcode 在 HTML 脚本里 |
| **ECharts 自适应** | **必须用 `ResizeObserver` 监听容器尺寸**（容器在 flex/grid 中高度变化时图表才能跟上） |
| **告警** | 红色 + 闪烁呼吸（`animation: pulse 2s infinite`） |
| **数字** | 带语义单位/趋势（▲/▼/¥/K/件；千分位 `toLocaleString`） |
| **入场动效** | KPI 数字递增（`requestAnimationFrame` + ease-out 1.2~1.5s） |
| **榜单** | 前三名**金银铜牌高亮**（渐变 + 发光阴影） |

### 0.2 顶层布局（CSS Grid）

顶层用 CSS Grid 分配垂直空间，**所有驾驶舱共享此骨架**，但具体行数、行高、内容由业务决定：

```css
html, body { height: 100%; margin: 0; padding: 0; overflow: hidden; }
body {
  background:
    radial-gradient(ellipse at 12% 8%, var(--db-bg-glow-1) 0%, transparent 45%),
    radial-gradient(ellipse at 88% 92%, var(--db-bg-glow-2) 0%, transparent 45%),
    linear-gradient(180deg, var(--db-bg-from) 0%, var(--db-bg-to) 100%);
  color: var(--db-text);
  font-family: -apple-system, "PingFang SC", "Microsoft YaHei", sans-serif;
}
.db-root {
  display: grid;
  /* 行数和行高按业务定：业务有几个核心模块就分几行 */
  grid-template-rows: 60px 110px 1fr 30px;  /* 例：顶栏 + KPI + 主区 + 状态栏 */
  height: 100vh;
  gap: 8px;
  padding: 10px 14px;
  box-sizing: border-box;
}
```

> **关键**：**禁止**给每段独立 `height: 320px / 220px` 后让 `overflow: hidden` 裁掉。要么用 Grid `1fr` 自动收缩，要么让所有 section 高度相加严格 ≤ 100vh。

### 0.3 ECharts 自适应模板（所有图表通用）

> **核心约定（避免 `xxx is not defined` 类低级错误）**：
> 工厂函数统一签名 `function(chart, theme)`，**所有 `--db-*` 颜色通过 `theme.xxx` 读取，禁止在工厂内 `var xxx = cv('--db-xxx')` 自行声明**。
> `autoResizeChart` 内部已一次性把 `--db-accent` / `--db-accent-2` / `--db-accent-warm` / `--db-text` / `--db-text-dim` / `--db-text-mute` / `--db-good` / `--db-warn` / `--db-bad` / `--db-bar-bg` / `--db-bg-from` / `--db-bg-to` / `--db-glow` 等全部读出注入到 `theme`，工厂直接 `theme.accent` 即可。

```js
// 读 CSS 变量（小工具，工厂外部用，工厂内部不再调）
function cv(name) { return getComputedStyle(document.documentElement).getPropertyValue(name).trim(); }

// 一次性预读所有 --db-* 主题变量（每个图表工厂共享）
function readTheme() {
  return {
    bgFrom:      cv('--db-bg-from'),
    bgTo:        cv('--db-bg-to'),
    accent:      cv('--db-accent'),
    accent2:     cv('--db-accent-2'),
    accentWarm:  cv('--db-accent-warm'),
    text:        cv('--db-text'),
    textDim:     cv('--db-text-dim'),
    textMute:    cv('--db-text-mute'),
    good:        cv('--db-good'),
    warn:        cv('--db-warn'),
    bad:         cv('--db-bad'),
    barBg:       cv('--db-bar-bg'),
    glow:        cv('--db-glow')
  };
}

function autoResizeChart(id, factory) {
  var el = document.getElementById(id);
  if (!el) return;
  var chart = echarts.init(el, null, { renderer: 'canvas' });
  var theme = readTheme();              // 自动注入 theme
  factory(chart, theme);                // 工厂签名：function(chart, theme)
  charts.push(chart);
  // 核心：监听容器尺寸变化（flex/grid 中容器高度会变）
  if (window.ResizeObserver) {
    new ResizeObserver(function() { chart.resize(); }).observe(el);
  }
}
// 兜底
window.addEventListener('resize', function() { charts.forEach(function(c) { c.resize(); }); });

// ===== 工厂使用示例（推荐写法）=====
autoResizeChart('chartOrderType', function(chart, theme){
  chart.setOption({
    tooltip: { backgroundColor: theme.bgTo + 'EE', borderColor: theme.accent, textStyle: { color: theme.text } },
    series: [{
      type: 'pie',
      data: [
        { value: 482, name: '整车', itemStyle: { color: theme.accent } },
        { value: 365, name: '零担', itemStyle: { color: theme.accent2 } },
        { value: 198, name: '冷链', itemStyle: { color: theme.accentWarm } },
        { value: 142, name: '危化品', itemStyle: { color: theme.warn } }
      ]
    }]
  });
});
```

> **为什么必须用 `theme.xxx` 而不是工厂内 `var xxx = cv('--db-xxx')`？**
> ① 复制粘贴工厂时极易遗漏变量声明，触发 `xxx is not defined at autoResizeChart`（典型：`accentW` 漏声明）；② `readTheme()` 在 `autoResizeChart` 入口统一预读，所有工厂零成本复用；③ 主题色增删只改 `readTheme()` 一处，不散落在 N 个工厂里。
>
> **少数需要动态读取的场景**（如不同主题切换后立即生效）仍可在工厂内调 `cv()`，但**仅限动态场景**，静态主题色一律走 `theme.xxx`。

**图表容器必须有明确高度**：
```css
.chart-wrap { flex: 1; min-height: 0; position: relative; }
.db-chart { width: 100%; height: 100%; }
```

> **⚠️ Grid/Flex 容器三件套（强制，避免图表不可见）**：
>
> 1. **每个 `.db-panel` 必须有 `display: flex; flex-direction: column; min-height: 0`** —— 否则 panel-body 的 `flex:1` 无法撑开（grid 子项默认 `min-height: auto`，按内容撑开会拒绝收缩 → 父 grid 行 `1fr` 跟着塌）
> 2. **每个图表 div 必须有显式 `min-height` 兜底**（如 `min-height: 220px` / `min-height: 460px`）—— flex 子项默认 `min-height: auto`，iframe 内嵌时 flex 计算可能延迟，兜底高度保证 ECharts init 拿到非零高度
> 3. **iframe 内嵌场景**：父框架 resize 后，子页面要主动监听父窗口 resize 并 `chart.resize()`，否则父窗口拉伸子页面图表不跟变
>
> **反向排查清单**（图表不可见时按此排查）：
> - 打开浏览器 DevTools Console，看 `[Chart] init xxx: WxH` 日志，**W 或 H 为 0 即是布局问题**
> - 检查 `.db-panel` 是否有 `display:flex; min-height:0`
> - 检查图表 div 是否有 `min-height` 兜底
> - 在 ECharts init 后加 `setTimeout(() => chart.resize(), 200)` 延迟双保险
> - 检查父 grid/行高是否被某段 `height` 写死撑爆

---

## 1. 设计原则（按业务自主判断）

驾驶舱该展示什么，**没有固定答案**。以下原则用于指导 AI 自主判断：

### 1.1 通用决策流程

```
需求分析
  ├─ Q1: 业务的核心目标是什么？
  │     - 态势感知（5 秒看到异常）→ 实时监控型
  │     - 经营分析（看趋势/结构）  → 数据洞察型
  │     - 综合指挥（既看监控又看分析）→ 指挥调度型
  │
  ├─ Q2: 业务有无空间属性？
  │     - 有（涉及地域/位置/路径）  → 考虑加地图
  │     - 无（纯财务/库存/系统监控）→ 用图表矩阵
  │
  └─ Q3: 数据规模与优先级
        - 关键指标 3~5 个           → KPI 卡（4 个为宜）
        - 实时事件有 N 条          → 滚动事件流 + 可操作按钮
        - 排名/排行数据             → 榜单（金银铜前三高亮）
        - 趋势对比                  → 折线/柱状图
        - 占比构成                  → 饼图/环形图
```

> **判断必须可解释**：在 dashboard.html 顶部加一行注释说明「为什么加/不加地图」「为什么是这种布局」。**禁止解释"用条形图替代了省级地图"** —— 这是被 §1.3 硬规则明确禁止的反模式。

### 1.2 三大典型范式（参考，不强制）

> 这只是行业里常见的几种布局思路，**业务不同应灵活变通**。

#### 范式 A · 地图主导型（物流调度 / 区域监控 / 交通态势）

```
┌────────────────────────────────────────────┐
│ 顶栏 (Logo + 大标题 + 实时时间 + 状态)      │
├────────────────────────────────────────────┤
│ KPI 横排 (4~6 个核心指标)                   │
├──────────┬───────────────────┬─────────────┤
│ 左分析列  │   中央地图（视觉中心）│  右监控列   │
│ - 业务流转│   (占最大面积)     │ - 实时事件  │
│ - 排行榜  │   配悬浮数据 pill  │ - 告警列表  │
├──────────┴───────────────────┴─────────────┤
│ 底部状态栏 (数据刷新频率 · 累计指标)         │
└────────────────────────────────────────────┘
```
**适用**：物流、调度、运维监控、应急指挥、区域分布

#### 范式 B · 数据洞察型（经营分析 / 销售 / 财务 / 党建风采）

```
┌────────────────────────────────────────────┐
│ 顶栏                                          │
├────────────────────────────────────────────┤
│ KPI 横排 (4~6 个核心指标)                    │
├──────────────────────┬─────────────────────┤
│ 主趋势图（大面积）    │  排行榜 / 占比饼图   │
│ (折线/柱状/堆叠)     │                     │
├──────────────────────┼─────────────────────┤
│ 明细表格 / 滚动事件流 │  辅助图表            │
└────────────────────────────────────────────┘
```
**适用**：经营分析、销售管理、财务监控、绩效看板

#### 范式 C · 综合指挥型（既要地图又要数据）

```
┌────────────────────────────────────────────┐
│ 顶栏 + 实时告警条                            │
├────────────────────────────────────────────┤
│ KPI 横排                                    │
├─────────────┬───────────────────┬───────────┤
│ 左分析      │  中央地图          │  右监控    │
│ (与 A 同)   │  (稍小, ~50%)     │  (与 A 同)│
├─────────────┴───────────────────┴───────────┤
│ 底部状态 + 趋势图                            │
└────────────────────────────────────────────┘
```
**适用**：应急指挥、智慧城市、综合态势

### 1.3 地图决策（**强制规则 + 业务判断**，违反硬规则会被驳回）

**✅ 必须加地图（硬规则，强制）**：
- 需求文档中出现**省/市/区/县名**（如"广东省""广州市""天河区"）+ 数据能按行政区划汇总 → **必须加地图**，不允许用条形图/饼图/雷达替代
- 业务涉及地域分布 / 路径 / 位置 / 区域对比
- 数据能匹配到行政区划（省/市/区/县）

**❌ 不加地图**：
- 纯财务 / 库存 / 系统监控等无空间属性业务
- 数据维度是"学院/专业/产品/部门/库存 SKU/客户分群"等**完全非行政的纯业务维度**（DataV 没有这种地图） → 改用柱状/饼图/雷达

**⚠️ 关键区分（曾踩过的坑）**：
- "高校分布""校区数据""门店分布"等看似非行政维度，但**归属在行政区划内**（如 21 地市内高校、某市内校区/门店）→ **视为行政维度的下级**，**必须加地图**
- 正确做法：地图主体显示行政区域（省/市），高校/门店/校区作为区域内**散点/标签标注**，不要因"高校/门店"等字面词否决地图
- 反例：**广东省 21 地市高校党员发展** → 应为「广东省地图 + 21 地市热力 + 点击地市下钻 + 区域内散点标注高校」；**不能**用横向条形图替代地图

**地图级别**（按需求关键词自动匹配）：
| 关键词 | 级别 | adcode |
|--------|------|--------|
| 某区/县/校园/街道 | 区县级 | 6 位 |
| 某市/市内 | 市级 | 6 位 |
| 某省/省内 | 省级 | 6 位 |
| 全国/各省/省际 | 国家级 | 100000 |

**匹配不到具体地名时**：按业务范围决定（业务只涉及某省/某市 → 用该省/市作初始；业务范围不明 → 国家级 100000，但避免盲目套用）。**不要硬性写死"默认国家级"**。

---

## 2. 三主题 CSS 变量（dashboard.html 顶部 `<style>` 必备）

```css
:root {
  --db-bg-from: #0a0e1a;
  --db-bg-to: #0f1729;
  --db-bg-glow-1: rgba(77, 208, 225, 0.18);
  --db-bg-glow-2: rgba(125, 249, 255, 0.10);
  --db-card-from: rgba(20, 30, 50, 0.55);
  --db-card-to: rgba(15, 23, 41, 0.35);
  --db-card-edge: rgba(77, 208, 225, 0.25);
  --db-border: rgba(77, 208, 225, 0.18);
  --db-accent: #4DD0E1;
  --db-accent-2: #7DF9FF;
  --db-accent-warm: #FFD700;
  --db-text: #E5E7EB;
  --db-text-dim: #9CA3AF;
  --db-text-mute: #6B7280;
  --db-good: #00B578;
  --db-warn: #FF7D00;
  --db-bad: #F53F3F;
  --db-glow: rgba(77, 208, 225, 0.5);
  --db-bar-bg: rgba(77, 208, 225, 0.1);
}
[data-skin="gov"] {
  --db-bg-from: #0a0f1f; --db-bg-to: #0f1a35;
  --db-bg-glow-1: rgba(184, 134, 11, 0.18);
  --db-bg-glow-2: rgba(30, 58, 138, 0.15);
  --db-card-from: rgba(20, 30, 60, 0.55); --db-card-to: rgba(15, 26, 53, 0.35);
  --db-card-edge: rgba(184, 134, 11, 0.25); --db-border: rgba(184, 134, 11, 0.18);
  --db-accent: #B8860B; --db-accent-2: #DAA520; --db-accent-warm: #FFD700;
  --db-text: #E5E7EB; --db-text-dim: #9CA3AF; --db-text-mute: #6B7280;
  --db-good: #2E7D32; --db-warn: #ED6C02; --db-bad: #C62828;
  --db-glow: rgba(184, 134, 11, 0.5); --db-bar-bg: rgba(184, 134, 11, 0.1);
}
[data-skin="party"] {
  --db-bg-from: #1a0a0a; --db-bg-to: #2a0f0f;
  --db-bg-glow-1: rgba(245, 63, 63, 0.18); --db-bg-glow-2: rgba(201, 48, 44, 0.15);
  --db-card-from: rgba(40, 15, 15, 0.55); --db-card-to: rgba(26, 10, 10, 0.35);
  --db-card-edge: rgba(245, 63, 63, 0.25); --db-border: rgba(245, 63, 63, 0.18);
  --db-accent: #F59E0B; --db-accent-2: #FCD34D; --db-accent-warm: #FFD700;
  --db-text: #E5E7EB; --db-text-dim: #9CA3AF; --db-text-mute: #6B7280;
  --db-good: #15803D; --db-warn: #EA580C; --db-bad: #B91C1C;
  --db-glow: rgba(245, 63, 63, 0.5); --db-bar-bg: rgba(245, 63, 63, 0.1);
}
```

---

## 3. 通用组件样式（按需组合，不强制全套）

> 以下是**可选组件库**，按业务需要取用。**不要无脑全装**。

### 3.1 顶栏（建议有）

```css
.db-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 12px; border-bottom: 1px solid var(--db-border);
  position: relative;
}
.db-header::before {
  content: ''; position: absolute; bottom: -1px;
  left: 20%; right: 20%; height: 1px;
  background: linear-gradient(90deg, transparent, var(--db-accent), transparent);
}
.db-title {
  font-size: 24px; font-weight: 700; letter-spacing: 4px;
  background: linear-gradient(180deg, #fff 0%, var(--db-accent) 100%);
  -webkit-background-clip: text; background-clip: text; color: transparent;
}
```

### 3.2 KPI 卡片（按需 3~6 个）

```css
.db-kpis { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; }  /* 列数按需 */
.db-kpi {
  background: linear-gradient(135deg, var(--db-card-from), var(--db-card-to));
  border: 1px solid var(--db-card-edge);
  border-radius: 6px; padding: 14px 22px;
  position: relative; display: flex; align-items: center; gap: 18px;
  overflow: hidden;
}
.db-kpi::before {
  content: ''; position: absolute; top: 0; left: 0; width: 3px; height: 100%;
  background: var(--db-accent);
}
.db-kpi.warn::before { background: var(--db-bad); animation: warnFlash 2s infinite; }
.db-kpi-num {
  font-size: 44px; font-weight: 700; color: var(--db-accent);
  line-height: 1.1; text-shadow: 0 0 16px var(--db-glow);
  font-family: 'DIN', 'Helvetica Neue', monospace;
}
.db-kpi-num .unit { font-size: 14px; color: var(--db-text-dim); margin-left: 4px; font-weight: 400; }
.db-kpi.warn .db-kpi-num { color: var(--db-bad); animation: pulse 2s infinite; }
```

### 3.3 通用卡片

```css
.panel {
  background: linear-gradient(180deg, var(--db-card-from), var(--db-card-to));
  border: 1px solid var(--db-border);
  border-radius: 6px; padding: 10px 12px;
  display: flex; flex-direction: column;
  min-height: 0; overflow: hidden;
}
.panel-title {
  font-size: 13px; font-weight: 600; color: var(--db-text);
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 8px; padding-left: 8px;
  border-left: 3px solid var(--db-accent);
  flex-shrink: 0;
}
```

### 3.4 地图容器（仅在加地图时需要）

```css
.db-map-wrap {
  flex: 1; min-height: 0; position: relative;
  border-radius: 4px; overflow: hidden;
  background: radial-gradient(ellipse at center, rgba(77,208,225,0.06) 0%, transparent 70%);
}
.db-map { width: 100%; height: 100%; }
/* 地图四象限 UI 元素（与上面 UI 元素清单一一对应） */
.db-map-toolbar    { position:absolute; top:10px; left:10px;  z-index:5; display:flex; gap:6px; }
.db-map-breadcrumb { position:absolute; top:10px; right:10px; z-index:5; display:flex; gap:4px; max-width:60%; justify-content:flex-end; }
.db-map-back       { position:absolute; bottom:10px; left:10px;  z-index:5; pointer-events:auto;
                     background:rgba(15,23,41,0.7); border:1px solid var(--db-border); color:var(--db-text);
                     font-size:12px; padding:5px 12px; border-radius:4px; cursor:pointer; display:flex; align-items:center; gap:4px; }
.db-map-stats      { position:absolute; bottom:10px; right:10px; z-index:5; display:flex; gap:8px; }
.db-map-toolbar button,
.db-map-breadcrumb .crumb { pointer-events:auto; }   /* 防 canvas 拦截 */
```

#### 3.4.1 地图下钻支持（按业务需要）

> 当需求涉及"按地理位置下钻"（如全国 → 省 → 市 → 区/县）时启用。
> 不是所有地图驾驶舱都需要下钻（如销售全球热力图、客户分布图通常只展示单级）。

**核心方案：单层 init + 路径栈（推荐 A + C）**

```
国家 (100000) → 省 (110000/440000/...) → 市 (440100/440300/...) → 区/县 (440103/...)
adcode 编码规则：省级 = 省份编码 + 0000；市级 = 省级 + 两位；县区 = 市级 + 两位
```

**初始层级由业务决定（不固定为国家级）**：

```js
// 业务为"广西货物运输" → 初始层级 = 广西省级
var ROOT_ADCODE = '450000';
var ROOT_NAME = '广西壮族自治区';
var breadcrumbStack = [{ adcode: ROOT_ADCODE, name: ROOT_NAME }];

// 业务为"南宁市内调度" → 初始层级 = 南宁市级
// var ROOT_ADCODE = '450100';
// var ROOT_NAME = '南宁市';
// var breadcrumbStack = [{ adcode: ROOT_ADCODE, name: ROOT_NAME }];

// 业务为"全国调度" → 初始层级 = 国家级
// var ROOT_ADCODE = '100000';
// var ROOT_NAME = '中华人民共和国';
// var breadcrumbStack = [{ adcode: ROOT_ADCODE, name: ROOT_NAME }];
```

**关键约束**：
- **初始层级最小只能到市级**（adcode 6 位），不要用区/县级作初始（数据碎片化）
- 顶栏「当前层级」标识 = `breadcrumbStack[stack.length - 1].name`，**不是固定常量**
- 下钻失败的兜底回退到 `ROOT_ADCODE`（初始层级），不是固定回退到 100000
- 「返回按钮」初始为 `disabled`（因为 `breadcrumbStack.length === 1`，根级就是初始层级）
- **不允许向上回到 ROOT_ADCODE 之上的层级**：省级初始时不能"回到全国"，市级初始时不能"回到省"，除非显式提供「回到 ROOT」入口

**兜底 GeoJSON 模板**：根据 `ROOT_ADCODE` 决定画多少个矩形：
- `100000` → 34 省
- `450000` → 14 市
- `450100`（南宁）→ 12 区/县

**数据源**

| CDN | URL 模板 | 说明 |
|-----|---------|------|
| DataV v3（推荐） | `https://geo.datav.aliyun.com/areas_v3/bound/{adcode}_full.json` | 主接口，含子级区划 |
| DataV v2 兜底 | `https://geo.datav.aliyun.com/areas/bound/{adcode}_full.json` | 旧接口，可作为 fallback |

每个 feature 的 `properties` 字段都包含 `adcode` / `name` / `childrenNum`，**直接驱动下钻判断**，无需查表。

**JS 引擎骨架（生成方法）**

> 这部分告诉**怎么写**，不是给固定数据。所有代码生成时按业务重新生成，**禁止把示例里的硬编码数据抄到业务页**。

**§A 业务配置生成方法**

生成大屏地图时，**声明 5 个变量**——其中 **SUB_REGIONS** 用于兜底时也能渲染完整的下辖地图：

```js
// 1) ROOT_ADCODE / ROOT_NAME：按业务可视范围从 §D 表查
//    国家级 = '100000'；省级 = 省码+'0000'；市级 = 省码+市码
var ROOT_ADCODE = '按业务决定';
var ROOT_NAME   = '按业务决定';

// 2) MAP_INDICATOR_LABEL：tooltip 里要展示的指标中文名
var MAP_INDICATOR_LABEL = '按业务决定';

// 3) BIZ_DATA：业务数据 map。key = GeoJSON properties.name，value = 指标值
var BIZ_DATA = { ... };

// 4) SUB_REGIONS：ROOT_ADCODE 的下辖区划列表（CDN 全挂时绘制完整兜底地图用）
//    格式：[{a:'下辖adcode', n:'下辖名称'}, ...]
//    国家级（100000）：引擎内置 34 省级标准列表，无需手写
//    省级 / 市级：按 §E 方法 fetch 拿到下辖 properties 后，转成 {a, n} 格式填入
var SUB_REGIONS = [
  // ROOT_ADCODE = '450000'（广西）示例：
  // {a:'450100', n:'南宁市'}, {a:'450300', n:'桂林市'}, ...
];
```

**§B 引擎代码（生成时整段写入，按业务填 §A 变量即可）**

> 下面是完整引擎代码，**生成时必须原样照抄到 dashboard.html**，只改 §A 的业务变量。引擎已内化：
> - **国家级 34 省级标准列表**（ROOT_ADCODE=100000 时无需传 SUB_REGIONS 自动画34 矩形）
> - 多 CDN 容错 + localStorage 缓存兜底
> - 矩形坐标按 adcode 稳定派生
> - 容器三保险（`min-height` + `ResizeObserver` + `setTimeout`）
> - 二段低透明 visualMap + 暗底配色

```js
// ===== 引擎代码（整段照抄，不要重写）=====
var breadcrumbStack = [{ adcode: ROOT_ADCODE, name: ROOT_NAME }];
var elMap = document.getElementById('dbMap');
var elMapLoading = document.getElementById('mapLoading');
var geoCache = {};
var mapChart = null;

// 国家级 34 省级标准下辖列表（这是国家标准，所有国家级业务都直接用）
// 省级 / 市级：生成时按 §E 方法填 SUB_REGIONS
var NATIONAL_PROVINCES = [
  {a:'110000', n:'北京市'},           {a:'120000', n:'天津市'},
  {a:'310000', n:'上海市'},           {a:'500000', n:'重庆市'},
  {a:'130000', n:'河北省'},           {a:'140000', n:'山西省'},
  {a:'150000', n:'内蒙古自治区'},     {a:'210000', n:'辽宁省'},
  {a:'220000', n:'吉林省'},           {a:'230000', n:'黑龙江省'},
  {a:'320000', n:'江苏省'},           {a:'330000', n:'浙江省'},
  {a:'340000', n:'安徽省'},           {a:'350000', n:'福建省'},
  {a:'360000', n:'江西省'},           {a:'370000', n:'山东省'},
  {a:'410000', n:'河南省'},           {a:'420000', n:'湖北省'},
  {a:'430000', n:'湖南省'},           {a:'440000', n:'广东省'},
  {a:'450000', n:'广西壮族自治区'},   {a:'460000', n:'海南省'},
  {a:'510000', n:'四川省'},           {a:'520000', n:'贵州省'},
  {a:'530000', n:'云南省'},           {a:'540000', n:'西藏自治区'},
  {a:'610000', n:'陕西省'},           {a:'620000', n:'甘肃省'},
  {a:'630000', n:'青海省'},           {a:'640000', n:'宁夏回族自治区'},
  {a:'650000', n:'新疆维吾尔自治区'}, {a:'710000', n:'台湾省'},
  {a:'810000', n:'香港特别行政区'},   {a:'820000', n:'澳门特别行政区'}
];

// 按 ROOT_ADCODE 拿子级 adcode+name 列表（国家级 = 内置 34 省；其他层级 = 用户 SUB_REGIONS）
function getSubRegions() {
  if (ROOT_ADCODE === '100000') return NATIONAL_PROVINCES;
  return SUB_REGIONS || [];
}

// 按 adcode 稳定派生矩形坐标（任何 adcode 都通用，CDN 全挂时用）
function mockRegionXY(adcode, idx, total) {
  var s = parseInt(String(adcode).slice(-4), 10) || 1;
  // 用 idx 让矩形均匀分布；同 adcode 多次调用位置稳定
  var row = Math.floor((idx || 0) / Math.ceil(Math.sqrt(total || 1)));
  var col = (idx || 0) % Math.ceil(Math.sqrt(total || 1));
  var x = 1 + col * 0.9 + (s * 7) % 3 * 0.1;
  var y = 1 + row * 0.9 + (s * 13) % 3 * 0.1;
  return { x: x, y: y };
}

// 把一个矩形（60×40 px）放在 (cx, cy) 中心
function rectPolygon(cx, cy) {
  return [[
    [cx-30, cy-20],[cx+30, cy-20],[cx+30, cy+20],[cx-30, cy+20],[cx-30, cy-20]
  ]];
}

// CDN 全挂时构造完整 GeoJSON（用 SUB_REGIONS + 派生矩形）
function makeFallbackGeo() {
  var subs = getSubRegions();
  var total = subs.length || 1;
  var features = subs.map(function(p, i) {
    var xy = mockRegionXY(p.a, i, total);
    var cx = xy.x * 70, cy = xy.y * 60;
    return {
      type: 'Feature',
      properties: { adcode: p.a, name: p.n, childrenNum: 1 },
      geometry: { type: 'Polygon', coordinates: rectPolygon(cx, cy) }
    };
  });
  // 兜底时顺便缓存到 localStorage，下次直接用真实缓存
  try { localStorage.setItem('map_' + ROOT_ADCODE, JSON.stringify({type:'FeatureCollection', features: features})); } catch(e){}
  return { type: 'FeatureCollection', features: features };
}

// 业务数据 mock（按 GeoJSON features 自动生成）
function mockBizData(features) {
  return (features || []).map(function(f){
    var name = f.properties.name || '';
    var adcode = f.properties.adcode;
    var base = BIZ_DATA[name];
    if (base === undefined) {
      var s = parseInt(String(adcode).slice(-2), 10) || 1;
      base = 1 + (s * 7) % 18;
    }
    return { name: name, adcode: adcode, childrenNum: f.properties.childrenNum, value: base };
  });
}

function showMap(node) {
  elMapLoading.innerHTML = '<span class="spin"></span>地图加载中...';
  elMapLoading.style.display = 'flex';

  // 缓存命中（包含 localStorage 持久化的兜底）
  if (geoCache[node.adcode]) { renderMap(geoCache[node.adcode]); return; }
  try {
    var ls = localStorage.getItem('map_' + node.adcode);
    if (ls) { var g = JSON.parse(ls); geoCache[node.adcode] = g; renderMap(g); return; }
  } catch(e){}

  var cdns = [
    'https://geo.datav.aliyun.com/areas_v3/bound/',
    'https://geo.datav.aliyun.com/areas/bound/'
  ];
  var tryFetch = function(i) {
    if (i >= cdns.length) {
      if (node.adcode === ROOT_ADCODE) {
        renderMap(makeFallbackGeo());
      } else {
        breadcrumbStack = [{ adcode: ROOT_ADCODE, name: ROOT_NAME }];
        showMap(breadcrumbStack[0]);
      }
      return;
    }
    fetch(cdns[i] + node.adcode + '_full.json')
      .then(function(r){ if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); })
      .then(function(geo){
        geoCache[node.adcode] = geo;
        try { localStorage.setItem('map_' + node.adcode, JSON.stringify(geo)); } catch(e){}
        renderMap(geo);
      })
      .catch(function(){ tryFetch(i + 1); });
  };
  tryFetch(0);
}

function renderMap(geo) {
  var top = breadcrumbStack[breadcrumbStack.length - 1];
  var data = mockBizData(geo.features || []);

  if (!mapChart) {
    mapChart = echarts.init(elMap, null, { renderer: 'canvas' });
    if (window.ResizeObserver) {
      new ResizeObserver(function(){ mapChart.resize(); }).observe(elMap);
    }
    mapChart.on('click', function(params){
      if (!params.data || !params.data.adcode) return;
      if (params.data.childrenNum === 0) return;
      drillDown(params.data.adcode, params.name);
    });
  }

  try {
    echarts.registerMap('map_' + top.adcode, geo);
    var max = Math.max.apply(null, data.map(function(d){ return d.value; }).concat([1]));
    mapChart.setOption({
      backgroundColor: 'transparent',
      tooltip: {
        trigger: 'item',
        backgroundColor: 'rgba(26,10,10,0.92)', borderColor: gold,
        textStyle: { color: '#fff', fontSize: 12 },
        formatter: function(p){
 return p.name + '<br/>' + MAP_INDICATOR_LABEL + '：<b style="color:' + gold + '">' + (p.value || 0) + '</b>'; }
      },
      visualMap: {
        min: 0, max: max, calculable: false, show: false,
        inRange: { color: ['rgba(245,158,11,0.06)', 'rgba(245,158,11,0.5)'] }
      },
      series: [{
        type: 'map', map: 'map_' + top.adcode, roam: false, zoom: 1.1,
        label: { show: true, color: '#FCE4E3', fontSize: 10 },
        itemStyle: {
          areaColor: 'rgba(245,158,11,0.06)',
          borderColor: 'rgba(224,62,58,0.45)', borderWidth: 0.8
        },
        emphasis: { itemStyle: { areaColor: 'rgba(245,158,11,0.18)', borderColor: gold, borderWidth: 1.5 }, label: { color: '#fff', fontWeight: 600 } },
        select: { itemStyle: { areaColor: 'rgba(245,158,11,0.25)', borderColor: gold }, label: { color: '#fff' } },
        data: data
      }]
    }, true);
  } catch (err) {
    elMapLoading.innerHTML = '地图渲染异常：' + (err && err.message ? err.message : err);
    setTimeout(function(){ elMapLoading.style.display = 'none'; }, 2500);
    return;
  }
  elMapLoading.style.display = 'none';
}

function drillDown(adcode, name) {
  breadcrumbStack.push({ adcode: String(adcode), name: name });
  showMap(breadcrumbStack[breadcrumbStack.length - 1]);
}
function goBack() {
  if (breadcrumbStack.length <= 1) return;
  breadcrumbStack.pop();
  showMap(breadcrumbStack[breadcrumbStack.length - 1]);
}
function refreshMap() {
  geoCache = {};
  breadcrumbStack = [{ adcode: ROOT_ADCODE, name: ROOT_NAME }];
  showMap(breadcrumbStack[0]);
}

setTimeout(function(){ if (mapChart) mapChart.resize(); }, 200);
showMap(breadcrumbStack[0]);
```

**§C HTML 容器（CSS 三保险 + 蒙层）**

```html
<div class="db-map-wrap">
  <div id="dbMap" class="db-map"></div>
  <div id="mapLoading"><span class="spin"></span>地图加载中...</div>
</div>
```

```css
.db-map { width: 100%; height: 100%; min-height: 380px; }
#mapLoading {
  position: absolute; inset: 0; z-index: 6;
  display: flex; align-items: center; justify-content: center;
  background: rgba(26,10,10,0.55); color: var(--db-text-dim);
  pointer-events: none;
}
```

**§D adcode 编码规则（生成时按业务可视范围查）**

| 业务范围 | 编码规则 | 示例 |
|---|---|---|
| 国家级 | `100000` | 全国调度 |
| 省级 | 省码 + `0000` | 江苏=320000 / 广东=440000 / 广西=450000 / 四川=510000 |
| 市级 | 省码 + 市码（6 位） | 广州=440100 / 南宁=450100 / 成都=510100 |

> 最小到市级（adcode 6 位），不要用区/县级做初始层级（数据碎片化）。
> 业务可视范围 = 初始层级：业务只在某省 → 不要硬塞 100000 国家级。

**§E 如何获取下辖列表（生成时怎么填 SUB_REGIONS 和 BIZ_DATA）**

> SUB_REGIONS 和 BIZ_DATA 的 key 都必须是 DataV GeoJSON 的标准行政区名（properties.name 字段），不能自己造名。生成时按下面任一方法获取实际下辖列表：

| 方法 | 步骤 | 适用 |
|---|---|---|
| **方法1：浏览器 fetch（首选）** | `fetch('https://geo.datav.aliyun.com/areas_v3/bound/ROOT_ADCODE_full.json').then(r=>r.json()).then(geo=>console.log(JSON.stringify(geo.features.map(f=>({a:f.properties.adcode,n:f.properties.name})))))` | 任何 ROOT_ADCODE |
| **方法2：常见省份速查** | 见下方"常见省级 adcode + 下辖列表" | ROOT_ADCODE 在速查表内时 |

**生成时拿到 JSON 后**：
- 复制 `{a: '...', n: '...'}` 数组填到 §A 的 `SUB_REGIONS`
- 复制 `n` 字段填到 `BIZ_DATA` 的 key，value 按业务量级 mock

**常见省级 adcode + 下辖列表（速查，不全；不在表内走方法1）**

| 省级 adcode | 省名 | SUB_REGIONS 的 n 列表 |
|---|---|---|
| 110000 | 北京 | （直辖市，无下辖市） |
| 120000 | 天津 | （直辖市） |
| 310000 | 上海 | （直辖市） |
| 500000 | 重庆 | （直辖市） |
| 320000 | 江苏 | 南京市/无锡市/徐州市/常州市/苏州市/南通市/连云港市/淮安市/盐城市/扬州市/镇江市/泰州市/宿迁市 |
| 330000 | 浙江 | 杭州市/宁波市/温州市/嘉兴市/湖州市/绍兴市/金华市/衢州市/舟山市/台州市/丽水市 |
| 440000 | 广东 | 广州市/韶关市/深圳市/珠海市/汕头市/佛山市/江门市/湛江市/茂名市/肇庆市/惠州市/梅州市/汕尾市/河源市/阳江市/清远市/东莞市/中山市/潮州市/揭阳市/云浮市 |
| 450000 | 广西 | 南宁市/柳州市/桂林市/梧州市/北海市/防城港市/钦州市/贵港市/玉林市/百色市/贺州市/河池市/来宾市/崇左市 |
| 510000 | 四川 | 成都市/自贡市/攀枝花市/泸州市/德阳市/绵阳市/广元市/遂宁市/内江市/乐山市/南充市/眉山市/宜宾市/广安市/达州市/雅安市/巴中市/资阳市/阿坝藏族羌族自治州/甘孜藏族自治州/凉山彝族自治州 |
| 520000 | 贵州 | 贵阳市/六盘水市/遵义市/安顺市/毕节市/铜仁市/黔西南布依族苗族自治州/黔东南苗族侗族自治州/黔南布依族苗族自治州 |
| 460000 | 海南 | 海口市/三亚市/三沙市/儋州市 + 15 个省直辖县级行政区划（白沙黎族自治县等） |
| 130000 | 河北 | 石家庄市/唐山市/秦皇岛市/邯郸市/邢台市/保定市/张家口市/承德市/沧州市/廊坊市/衡水市 |
| 370000 | 山东 | 济南市/青岛市/淄博市/枣庄市/东营市/烟台市/潍坊市/济宁市/泰安市/威海市/日照市/临沂市/德州市/聊城市/滨州市/菏泽市 |
| 410000 | 河南 | 郑州市/开封市/洛阳市/平顶山市/安阳市/鹤壁市/新乡市/焦作市/濮阳市/许昌市/漯河市/三门峡市/南阳市/商丘市/信阳市/周口市/驻马店市/济源市 |

> ROOT_ADCODE='100000' 时**不要填 SUB_REGIONS**——引擎内置 NATIONAL_PROVINCES 兜底（34 个省级全在内）。
> ROOT_ADCODE 不在速查表内（其他省份或市级）必须用方法1。

**§F 生成大屏地图时的执行步骤**

1. **确定 ROOT_ADCODE**：按业务可视范围查 §D 表
2. **fetch 一次拿 SUB_REGIONS 和 BIZ_DATA key**：浏览器控制台跑方法1，复制 `[{a,n}, ...]` 到 SUB_REGIONS
3. **写 §A 五个变量**：ROOT_ADCODE / ROOT_NAME / MAP_INDICATOR_LABEL / BIZ_DATA / SUB_REGIONS
4. **整段复制 §B 引擎代码 + §C HTML/CSS**，**不改动任何字符**
5. **验证**：
   - 打开 dashboard.html 应看到完整地图（CDN 通）
   - 第一次访问成功后即使断网，下次打开仍能用（localStorage 缓存）
   - CDN 全挂 + localStorage 空时，仍能看到 ROOT_ADCODE 下辖的完整矩形兜底地图

**UI 元素清单（按四象限严格分区，不允许合并堆叠）**

| 元素 | 位置 | 作用 |
|------|------|------|
| 工具栏（刷新等次要按钮） | 地图**左上** | `top:10px; left:10px`；`.db-map-toolbar` 容器 |
| 面包屑（crumb） | 地图**右上** | `top:10px; right:10px`；`.db-map-breadcrumb`；路径导航 `全国 › 广东省 › 广州市`，点击任意级跳回 |
| 返回按钮 | 地图**左下**（**独立按钮**，不与其他按钮合并） | `bottom:10px; left:10px`；`.db-map-back`；主操作入口，国家级/初始层时 `disabled` |
| 悬浮统计 pill | 地图**右下** | `bottom:10px; right:10px`；`.db-map-stats`；当前级汇总指标（订单/车辆/司机） |
| 右键菜单 | 地图任意处 | 替代双击，避免误触；`contextmenu` + `preventDefault` |
| Loading 蒙层 | 地图中央 | fetch 期间显示，**关键：`pointer-events: none` 不拦截按钮点击** |
| 降级提示横幅 | 地图上方居中 | 网络故障用 demo 数据时显示"⚠ 当前为演示数据" |

> **生成时必须按此四象限分布**：左上工具栏 / 右上面包屑 / 左下返回按钮 / 右下悬浮统计。**返回按钮必须独立**（不要与刷新按钮合并到工具栏），否则会被 canvas + loading 蒙层拦截，且视觉重心偏离左下习惯位。所有地图交互按钮显式加 `pointer-events: auto`。

**地图配色（不要喧宾夺主）**

```js
itemStyle: {
  areaColor: 'rgba(77,208,225,0.06)',       // 默认态：低透明度蓝绿
  borderColor: 'rgba(77,208,225,0.45)',     // 描边清晰但不过亮
  borderWidth: 0.8,
  shadowColor: 'rgba(77,208,225,0.15)',     // 微微发光
  shadowBlur: 6
},
emphasis: {                                  // hover：微亮 + 描边加粗
  itemStyle: { areaColor: 'rgba(77,208,225,0.18)', borderColor: accent(), borderWidth: 1.5 }
},
select: {                                    // 选中（下钻后保持高亮）
  itemStyle: { areaColor: 'rgba(77,208,225,0.25)', borderColor: accent2() }
}
```

> **不要**用饱和度过高的三段渐变填充（`barBg→accent→accent2`），会让地图与暗夜基调冲突。

**业务数据 mock**

按 `adcode` 做稳定 hash（同区域数据稳定不跳变）。**已在 §3.4.1 引擎骨架的 `mockBizData()` 内置**，直接抄即可。接入真实 API 时替换 `mockBizData` 函数体，**入参 adcode / features 不变**。

**网络容错**

完整的多 CDN + 内置矩形兜底 + 下钻回退逻辑**已在 §3.4.1 引擎骨架的 `showMap()` 内置**（CDN 数组 + tryFetch 递归 + ROOT/CDN 全挂时 `makeFallbackGeo` + 下钻失败退回 ROOT）。不需要再额外写。

**初始层级兜底 GeoJSON 模板**

**已在 §3.4.1 引擎骨架的 `makeFallbackGeo()` 内置**——按 ROOT_ADCODE 实际行政区补 `cities` 数组即可。**全国（100000）** 画 34 省矩形；**省级（450000）** 画 14 市矩形；**市级（450100）** 画 12 区/县矩形。

#### 3.4.2 地图常见踩坑（事后参考，不要事后修）

> §3.4.1 的引擎骨架已经"做对"的事不在此重复。这里只列**容易被新需求破坏的规则**——下次生成大屏地图时，照抄 §3.4.1 即可，不要写自定义版本。

| 现象 | 根因 | 做法（不是事后补救，是**生成时就必须遵守**）|
|------|------|----------------------------------------------|
| `<button>` 默认 type="submit" | 部分浏览器触发表单提交 | HTML 显式 `type="button"`（§3.4.1 工具栏/返回按钮已显式标注） |
| 双击返回太敏感（误触下钻） | dblclick 与 click 冲突 | 用右键 `contextmenu` 触发下钻（不是 dblclick） |
| 业务只在广西却硬编码 100000 国家级 | 没区分业务范围 | §3.4.1 顶部 `var ROOT_ADCODE = '450000'`，**按业务决定**，不固定 100000 |
| 顶栏「当前层级」写成"中华人民共和国"常量 | 没意识到 ROOT 是变量 | HTML 初值 = `ROOT_NAME`；JS 每次 render 同步更新 |
| 下钻失败回退到全国 | catch 内写死 `100000` | §3.4.1 的 `tryFetch` 回退到 `ROOT_ADCODE`，不是 100000 |
| 面包屑/刷新/返回按钮位置错乱 | 生成时图省事合并到顶部 | 按 §3.4.1 UI 清单分区：面包屑→右上 / 返回按钮→左下（独立）/ 工具栏→左上 / 悬浮统计→右下 |
| JS 报错 `xxx is not defined at autoResizeChart` | 工厂内 `var xxx = cv('--db-xxx')` 漏写 | §0.3 工厂签名固定为 `function(chart, theme)`，直接 `theme.accent`，**禁止工厂内 cv() 声明** |
| `getComputedStyle('--db-accent-warm')` 返回空字符串 | default 主题 `:root` 漏声明该变量 | §2 三主题 CSS 变量**逐主题完整定义** `--db-accent` / `--db-accent-2` / `--db-accent-warm` 三件套 |
| 按钮被 canvas 拦截，点击无响应 | canvas 在 z-index 上层，按钮忘 `pointer-events: auto` | §3.4.1 所有地图按钮显式 `pointer-events: auto` |

### 3.5 实时事件流（按需）

```css
.event-list { animation: scrollStream 30s linear infinite; }
.event-list:hover { animation-play-state: paused; }
.event-item {
  display: grid; grid-template-columns: 50px 60px 1fr 50px; gap: 6px;
  align-items: center; padding: 7px 2px;
  border-bottom: 1px dashed var(--db-border); font-size: 11px;
}
.event-action {
  background: transparent; border: 1px solid var(--db-accent);
  color: var(--db-accent); padding: 2px 6px; border-radius: 3px;
  font-size: 10px; cursor: pointer;
}
@keyframes scrollStream { 0% { transform: translateY(0); } 100% { transform: translateY(-50%); } }
```

### 3.6 排行榜（按需）

```css
.rank-item:nth-child(1) .r { background: linear-gradient(135deg, var(--db-accent-warm), #FFA500); color: #0a0e1a; box-shadow: 0 0 10px rgba(255,215,0,0.5); }
.rank-item:nth-child(2) .r { background: linear-gradient(135deg, #C0C0C0, #909090); color: #0a0e1a; }
.rank-item:nth-child(3) .r { background: linear-gradient(135deg, #CD7F32, #8B5A2B); color: #fff; }
```

### 3.7 全局动效

```css
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: .5; } }
@keyframes warnFlash { 0%, 100% { box-shadow: 0 0 0 rgba(245,63,63,0); } 50% { box-shadow: 0 0 20px rgba(245,63,63,0.3); } }
```

---

## 4. 地图组件（仅在 §1.3 决定加地图时使用）

> **⚠️ 地图 label 颜色防撞色三件套（强制，避免地名看不清）**：
>
> 1. **必须给 label 加 `textBorderColor` + `textBorderWidth`**（描边）
> 2. **建议加 `textShadowColor` + `textShadowBlur`**（阴影）作为双保险
> 3. **emphasis/select 态必须用 `color: '#fff'` + 更深更粗的描边**
>
> **为什么必加**：
> - 默认 label 文字是浅色（`var(--db-text)` 或 `theme.text`），底色是主题色透明叠加（`rgba(red, 0.15)` ~ `rgba(red, 0.5)`），**对比度不够，地名糊在底色里**
> - emphasis 态白字 + 亮红底色（`accent` / `red`），更看不清
> - 下钻到地市级时图斑更小更挤，文字会更糊
>
> **正确模板**（适用所有主题色，直接照抄）：
>
> ```js
> label: {
>   show: true,
>   color: theme.text,                            // 浅灰白
>   fontSize: 10,
>   textBorderColor: 'rgba(20, 8, 12, 0.85)',     // 深底色描边
>   textBorderWidth: 2,
>   textShadowColor: 'rgba(20, 8, 12, 0.85)',     // 阴影双保险
>   textShadowBlur: 4
> },
> emphasis: {
>   label: {
>     show: true, color: '#fff', fontWeight: 700, fontSize: 12,
>     textBorderColor: 'rgba(20, 8, 12, 1)',       // hover 更深更粗
>     textBorderWidth: 3,
>     textShadowColor: 'rgba(20, 8, 12, 0.9)',
>     textShadowBlur: 6
>   },
>   itemStyle: { ... }
> },
> select: {
>   label: {
>     color: '#fff',
>     textBorderColor: 'rgba(20, 8, 12, 1)',
>     textBorderWidth: 3
>   },
>   itemStyle: { ... }
> }
> ```
>
> **反向排查**（地图地名看不清时）：
> - 看 label 是否只设了 `color` 没设 `textBorderColor` —— 必加
> - emphasis 是否用了白字但区域底色也是浅色 —— 描边加粗
> - 下钻后图斑变小 —— `fontSize` 不要小于 10px，描边要更粗

### 4.1 通用地图初始化

```js
function autoResizeMap(id, factory) {
  var el = document.getElementById(id);
  if (!el) return;
  var chart = echarts.init(el, null, { renderer: 'canvas' });
  var theme = readTheme();              // 同样注入 theme（复用 §0.3 的 readTheme）
  factory(chart, theme);                // 工厂签名：function(chart, theme)
  charts.push(chart);
  if (window.ResizeObserver) {
    new ResizeObserver(function() { chart.resize(); }).observe(el);
  }
}

fetch('https://geo.datav.aliyun.com/areas_v3/bound/[adcode]_full.json')
  .then(function(r) { return r.json(); })
  .then(function(geo) {
    echarts.registerMap('[name]', geo);
    autoResizeMap('[地图id]', function(chart) {
      var accent = cv('--db-accent');
      var accent2 = cv('--db-accent-2');
      chart.setOption({
        backgroundColor: 'transparent',
        tooltip: { trigger: 'item', backgroundColor: cv('--db-bg-to') + 'EE', borderColor: accent, textStyle: { color: cv('--db-text') } },
        series: [{
          type: 'map', map: '[name]', roam: false, zoom: 1.2,
          label: { show: true, color: cv('--db-text-dim'), fontSize: 10 },
          itemStyle: { areaColor: cv('--db-bar-bg'), borderColor: accent, borderWidth: 0.6 },
          emphasis: { itemStyle: { areaColor: accent }, label: { color: '#fff', fontWeight: 600 } },
          data: [/* {name:'[区域名]', value:[N]} */]
        }],
        visualMap: { min: 0, max: [按数据实际最大值定], calculable: false, show: false, inRange: { color: [cv('--db-bar-bg'), accent, accent2] } }
      });
    });
  })
  .catch(function() {
    var el = document.getElementById('[地图id]');
    if (el) el.innerHTML = '<div style="display:flex;align-items:center;justify-content:center;height:100%;color:var(--db-text-dim);">地图加载失败，请检查网络</div>';
  });
```

### 4.2 DataV GeoJSON URL 规则

URL 模板：`https://geo.datav.aliyun.com/areas_v3/bound/{adcode}_full.json`

| 级别 | 示例 | URL |
|------|------|-----|
| 国家级 | 中国 | `bound/100000_full.json` |
| 省级 | 江苏省 | `bound/320000_full.json` |
| 市级 | 南京市 | `bound/320100_full.json` |
| 区/县级 | 鼓楼区 | `bound/320106_full.json` |

### 4.3 各级别适配要点

| 级别 | data 规模 | `label.show` | `roam` | `fontSize` | `zoom` |
|------|----------|--------------|--------|------------|--------|
| 国家级 | 34 省级全覆盖 | `true` | `false` | 10 | 1.2 |
| 省级 | 13~21 个市 | `true` | `false` | 10 | 1.0 |
| 市级 | 50~150 个区/县 | `false`（hover 显示） | `true` | 9 | 1.0 |
| 区/县级 | 几百个街道 | `false` | `true` | 8 | 1.0 |

---

## 5. 经验沉淀（踩过的坑 · 作为参考，不是规定）

> 这些是历版驾驶舱的翻车经验，**作为常识提醒**，不强制每条都遵守。

### 5.1 布局与尺寸

| 翻车现象 | 根因 | 修复建议 |
|---------|------|----------|
| 地图"很小"且重叠 | `.db-map` 没显式 height，ECharts init 拿到 0 高度 | `.db-map { width: 100%; height: 100%; min-height: 420px }` |
| 地图显示太小（被左右列挤压） | 左右业务分析列太宽（320px×2），中央 1fr 被压缩 | 主区 grid `260px 1fr 260px`；KPI 砍到 4 个、行高 88px；总 padding 8×12；左侧只放必要信息 |
| 地图加载后尺寸不对 | 没用 `ResizeObserver`，只在 `window.resize` 时 resize | 用 `ResizeObserver` 监听容器 |
| 地图下半部分被裁掉 | 主体三列用 `height: 100vh` 而不是 grid `1fr` | 用 grid 顶层分配，1fr 自动收缩 |
| 总高度超 100vh | 每段独立 height 相加 > 900px | 用 grid 顶层分配，或精简区块 |
| 容器在 Grid/Flex 内 init 时高度为 0 | 同步脚本执行时 Grid 布局尚未稳定 | `.db-map { min-height: 420px }` + init 时若 `clientHeight===0` 强制 `min-height` 兜底 + `setTimeout(resize, 200)` 延迟双保险 |

### 5.2 渲染与配色

| 翻车现象 | 根因 | 修复建议 |
|---------|------|----------|
| 标题看起来平淡 | 没用渐变 + 装饰线 | 加 `::before/::after` 渐变横线 + `background-clip: text` |
| 地图看着"空" | 只列了部分省 | 国家级建议 34 省级行政区全覆盖 |
| 地图配色突兀（太亮/与暗夜基调冲突） | `borderColor: accent` 全亮 + visualMap 三段渐变填充 | 边框改 `rgba(accent, 0.45)` 半透明；emphasis 边框用 `accent` 即可；**visualMap 配色用 `[rgba(accent, 0.06), rgba(accent, 0.5)]` 二段低透明**，禁止 `barBg→accent→accent2` 三段渐变 |
| 散点尺寸计算异常 | `value: c.value.concat([lng, lat])` 让 `symbolSize: val[2]` 拿到的是经纬度 | scatter 改 `{ name, value: [lng, lat, bizValue] }` 三元素结构，`symbolSize: val[2]` 取业务值 |

### 5.3 数据与异常处理

| 翻车现象 | 根因 | 修复建议 |
|---------|------|----------|
| 任何抛错都被 catch 吞并显示"加载失败" | catch 兜底范围过大，把"渲染异常"也当成"网络失败" | render 包独立 try/catch，区分"加载失败 vs 渲染异常"；catch 文案带 `err.message`；加 `console.log` 与 `window.__dbgMap` 暴露给控制台 |
| CDN 全挂后空白页 | 仅 innerHTML 覆盖"加载失败"文字 | 初始层级内置矩形 GeoJSON 兜底（`buildFallbackRootGeo()` 按 ROOT_ADCODE 决定 34 省/14 市/12 区/县），下钻层级失败自动退回 ROOT_ADCODE + Toast |
| 错误文案误导排查 | 只说"加载失败"不说原因 | 三态文案分离：① loading spinner + "加载 xxx 地图..."；② 错误态显示 `err.message` + "重新加载"按钮；③ demo 模式下顶部横幅 "⚠ 当前为演示数据" |
| max=0 时 visualMap 抛 warn | 数据全 0 时除以 0 | `if (!isFinite(max) \|\| max <= 0) max = 1` 兜底 |
| 用户被通用"加载失败"误导 | 没暴露真实错误 | 暴露 `window.__dbgMap = { el, chart }`，console 加 `[dashboard] init map, container size: WxH` 与 `setOption OK, features=N` 日志 |

### 5.4 KPI 数字递增

| 翻车现象 | 根因 | 修复建议 |
|---------|------|----------|
| KPI 数字旁没有单位 | `el.innerHTML = prefix+val+suffix` 直接覆盖，`.unit` 子节点丢失 | 递增动画里只替换数字文本，保留 `.unit` 子节点：`el.firstChild.nodeValue = formatted` 或在渲染前保存 unit 元素 |
| 前缀/后缀/小数位丢失 | 简单拼接字符串 | 用 `data-prefix`/`data-suffix`/`data-decimals` 三个 dataset 属性驱动 |
| 数字格式化不友好 | `38.0` 显示为 `38.000000` | `toLocaleString('zh-CN', { minimumFractionDigits: decimals })` |

---

## 6. 侧边栏注册

在 `pc/index.html` 的 `<aside class="sidebar">` 内插入：

```html
<a class="sidebar-nav-link" data-url="dashboard.html" href="dashboard.html">
  <i class="bi bi-display"></i> <span>数据大屏</span>
</a>
```

**位置**：放在「工作台」之后，业务管理菜单之前（驾驶舱是高频入口）。

---

## 7. 输出原则（重申 · 自主判断 > 模板堆砌）

1. **业务优先**：先理解需求（Q1 核心目标 / Q2 空间属性 / Q3 数据规模），再决定展示什么
2. **骨架可循**：CSS Grid 顶层 + flex 列内 + ECharts `ResizeObserver` 这套机制**通用**
3. **样式按需**：§3 的组件样式（顶栏/KPI/卡片/地图/事件流/榜单）按业务取用，**不要全套照搬**
4. **判断可解释**：dashboard.html 顶部加一行注释说明布局/地图决策
5. **少即是多**：大屏内容饱和度由信息密度决定，不是"卡片越多越好"
