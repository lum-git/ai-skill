# 主题风格规范

`prototype-generator` 技能内置 **三套主题**，仅以**背景**为视觉主区分点，结构、组件、交互、数据完全一致。主题由用户需求中的关键词在**生成时一次性确定**，写入 `<html data-skin="...">`，**不支持运行时切换**。

## 〇、三套样式模板（独立预览）

技能提供 3 个**自包含**样式模板文件，可独立打开预览整套风格规范，无需搭建项目：

| 文件 | 主题 | 适用场景 | 主色 |
|------|------|---------|------|
| [styleguide/index.html](styleguide/index.html) | 入口 | 三套风格选择器 | — |
| [styleguide/default.html](styleguide/default.html) | 默认风格 | 通用业务 / SaaS / 互联网产品 | `#3370FF` 品牌蓝 |
| [styleguide/gov.html](styleguide/gov.html) | 政企风格 | 政务 / 国企 / 事业单位 | `#1E3A8A` 政务蓝 |
| [styleguide/party.html](styleguide/party.html) | 党建风格 | 党建 / 党政机关 / 红色主题 | `#C9302C` 党旗红 |

每个模板文件特点：
- ✅ **自包含**：design-tokens.css 已内联，可直接浏览器打开
- ✅ **预置主题**：`<html data-skin="xxx">` 已设定固定主题值
- ✅ **固定展示**：每页固定显示其对应主题，**不放切换按钮、不做运行时切换**
- ✅ **暗色模式（仅 App 端）**：App 页自动检测 `prefers-color-scheme`，可与主题正交叠加；PC 端不提供暗色模式
- ✅ **7 大区块**：色彩 / 字体 / 组件 / 业务模块 / 列表表格 / **PC 真实框架布局演示** / **App 移动端布局演示**（含 390×844 顶部状态栏 + 导航头 + 内容区 + 底部 Tab Bar）

---

## 一、主题对照表

| 维度 | 默认风格 `default` | 政企风格 `gov` | 党建风格 `party` |
|------|------------------|---------------|------------------|
| **触发关键词** | （默认） | "政企/政务/政府/国企/国资/事业单位/行政/机关" | "党建/党务/党支部/党组织/党员/党课/党群/先锋" |
| **主色 `var(--primary)`** | `#3370FF` 品牌蓝 | `#1E3A8A` 藏蓝 | `#C9302C` 党旗红 |
| **主色深 `var(--primary-dark)`** | `#1F4DC4` | `#172554` | `#8B1A1A` |
| **主色浅 `var(--primary-light)`** | `#E1EBFF` | `#DBE5FE` | `#FCE4E3` |
| **主色背景 `var(--primary-bg)`** | `#F0F5FF` | `#EFF4FE` | `#FEF1F0` |
| **Body 背景 `var(--bg-body)`** | `#F5F6F7` 浅灰 | `#F4F1EA` 档案米 | `#FDF6E3` 米黄 |
| **顶栏背景 `var(--header-bg)`** | `#FFFFFF` 白 | `#FFFFFF` 白 | `#C9302C` 党旗红 |
| **顶栏文字** | 深色 | 深色 | `#FFFFFF` 白 |
| **侧边栏背景 `var(--sidebar-bg)`** | `#1F2329` 深石板 | `#0F1E3D` 深藏蓝 | `#7F1D1D` 深红 |
| **侧边栏文字** | `#8B8F97` | `#94A3B8` | `rgba(255,255,255,0.7)` |
| **强调金色 `var(--accent-gold)`** | （未用） | `#B8860B` 暗金 | `#F59E0B` 五星金 |
| **整体气质** | 科技、效率、互联网 | 庄重、严谨、权威 | 红色主调、党旗元素 |

---

## 二、自动识别逻辑

**第 0 步**仅扫描"XXX 原型"中的系统名称 XXX（大小写不敏感），**不扫描需求中的背景描述、功能说明等其他文字**：

```js
function detectSkin(req) {
  var name = extractSystemName(req);  // 提取"XXX 原型"中的系统名称 XXX
  var partyWords = ['党建','党务','党支部','党组织','党员','党课','党群','先锋'];
  var govWords   = ['政企','政务','政府','国企','国资','事业单位','行政','机关'];
  if (partyWords.some(w => name.indexOf(w) >= 0)) return 'party';   // 党建优先
  if (govWords.some(w => name.indexOf(w) >= 0))  return 'gov';      // 政企
  return 'default';                                                  // 默认
}
```

**应用方式**：

```html
<!-- 检测到"党建" -->
<html lang="zh-CN" data-skin="party">

<!-- 检测到"政企" --><html lang="zh-CN" data-skin="gov">

<!-- 默认 -->
<html lang="zh-CN" data-skin="default">
```

**与暗色模式正交叠加（仅 App 端）**：

```html
<!-- 暗色 + 党建 -->
<html lang="zh-CN" data-skin="party" data-theme="dark">
```

---

## 三、主题固定（生成时确定，禁止运行时切换）

主题由第 0 步关键词识别**一次性确定**，作为项目"出厂设置"写入所有页面的 `<html data-skin="...">`。**任何页面（含 PC 框架/业务页/登录/根导航/App/风格总览）都不放主题切换按钮**，也不提供 `cycleSkin` / `setSkin` / `getSkin` 等运行时切换 API——主题不能由用户切换。

> **为什么禁止切换**：多个原型项目部署在同一源（如本地预览服务器、`file://`）时会共享 `localStorage`。若用 `localStorage.skin` 持久化主题，A 项目切换后会污染 B 项目。因此主题只以 `<html data-skin="...">` 写死在标记中，**不读不写 `localStorage.skin`**。

**FOUC 阻止脚本**（仅 App 端页面在 `<head>` 内、CSS 之前同步执行）——只处理暗色模式，**不读取 `skin`**：

```html
<script>
  (function(){
    var t = localStorage.getItem('theme');
    if (t === 'dark' || (!t && window.matchMedia('(prefers-color-scheme:dark)').matches))
      document.documentElement.setAttribute('data-theme', 'dark');
  })();
</script>
```

**关键点**：FOUC 脚本仅 App 端页面需要，且必须在所有 CSS **之前**同步执行；保证暗色模式在首屏渲染前已生效。主题本身由 `<html data-skin="...">` 静态标记决定，无需脚本干预。PC 端不读 `theme`、不放暗色切换按钮。

---

## 四、CSS 变量定义模板

完整令牌（含 `--font-size-xs/sm`、`--text-link`、`--primary-active-bg` 以及暗色完整变量）以 [examples.md 附录 A](examples.md) 为唯一来源，直接整段复制到 `shared/design-tokens.css`，不在此重复维护精简版。

---

## 五、组件级适配要点

三套主题仅颜色变量不同，**结构、布局、字号、圆角、阴影完全不变**。但有少量组件需要按主题做语义化微调：

### 5.1 顶栏

- **默认 / 政企**：白底深字（`--header-bg: #FFFFFF` / `--header-text: 深色`）
- **党建**：红底白字（`--header-bg: #C9302C` / `--header-text: #FFFFFF`），对应 CSS：

```css
.header-navbar { background: var(--header-bg); color: var(--header-text); border-bottom: 1px solid var(--header-border); }
.header-navbar .header-logo,
.header-navbar .header-notification,
.header-navbar .header-user { color: var(--header-text); }
.header-navbar .env-badge { background: var(--success-light); color: var(--success); }   /* 浅色徽章在红底下仍可读 */
```

### 5.2 侧边栏激活态

- **默认**：左 3px 蓝条 + 半透明蓝底
- **政企**：左 3px 藏蓝条 + 半透明藏蓝底
- **党建**：左 3px 金条（用 `--accent-gold`）+ 半透明红底（金色在红底下更醒目，党旗元素）

```css
.sidebar .sidebar-nav-link.active::before {
  background: var(--primary);
}
[data-skin="party"] .sidebar .sidebar-nav-link.active::before {
  background: var(--accent-gold);   /* 党建用金色，呼应党徽 */
}
```

### 5.3 App 状态栏 / 顶栏

App 端无 Header 顶栏，状态栏文字色 `var(--text-primary)` 即可。**但**党建风格的 App 页面可在状态栏右侧加一颗小金色党徽装饰（可选）：

```html
<!-- 仅党建风格：状态栏增加金色五角星 -->
<span class="status-icons">
  <i class="bi bi-star-fill" style="color:var(--accent-gold);font-size:12px;"></i>
  <i class="bi bi-reception-4"></i>
  <i class="bi bi-wifi"></i>
  <i class="bi bi-battery-full"></i>
</span>
```

**App 端背景规则**：移动端页面（`@media (max-width: 768px)`）不应用主题的米黄 / 档案米底色，`body` 统一为白底（`var(--bg-white)`）。主题色仅用于品牌区 / 顶栏 / 按钮 / 标签等组件，确保小屏视觉清爽：

```css
@media (max-width: 768px) {
  [data-skin="party"] body,
  [data-skin="gov"] body {
    background: var(--bg-white);
  }
}
```

### 5.4 登录页

- **默认 / 政企**：左品牌区用 `linear-gradient(135deg, --sidebar-bg, --primary)`
- **党建**：左品牌区用 `linear-gradient(135deg, #7F1D1D, #C9302C)`，并可加 `bi-star-fill` 金色五角星装饰

```html
<!-- 党建风格登录页左品牌区 -->
<div class="login-brand">
  <div class="logo">
    <i class="bi bi-tools"></i>
    <i class="bi bi-star-fill" style="color:var(--accent-gold);font-size:1.5rem;margin-left:6px;"></i>
  </div>
  <h2>党建管理系统</h2>
  ...
</div>
```

### 5.5 根导航入口页

- **默认 / 政企**：顶部 header 用 `linear-gradient(135deg, --primary-dark, --primary)` 渐变
- **党建**：顶部 header 用 `linear-gradient(135deg, #7F1D1D, #C9302C)`，并在 title 旁加金色五角星

```html
<!-- 党建风格根导航 header -->
<div class="header" style="background:linear-gradient(135deg,#7F1D1D,#C9302C);">
  <h2>
    <i class="bi bi-star-fill" style="color:var(--accent-gold);"></i>
    党建管理系统
  </h2>
</div>
```

---

## 六、平滑过渡

为保证暗色模式切换时**无闪烁、无跳动**，在 `shared/components.css` 末尾增加：

```css
/* 暗色模式切换平滑过渡 */
body, .header-navbar, .sidebar, .card, .content-card, .stat-card,
.filter-bar, .table-container, .form-section, .detail-card,
.modal-content, .phone-frame, .dropdown-menu {
  transition: background-color 0.25s ease, color 0.25s ease, border-color 0.25s ease;
}
```

> 注意：**不要**给 `transform` / `width` / `height` / `margin` / `padding` 等加 transition，否则暗色模式切换时会有"晃动"感。

---

## 七、迁移现有项目

如果一个旧项目（无主题系统）需要迁移为固定主题（生成时确定）：

1. 复制 [examples.md 附录 A](examples.md) 的完整令牌（含三套 `[data-skin="..."]` 变量块），追加到现有 `shared/design-tokens.css` 的 `:root` 之后。
2. 移除现有 `shared/components.js` 中任何 `SKIN_LIST` / `getSkin` / `setSkin` / `cycleSkin` 等主题切换代码（`toggleTheme()` 单独保留，仅用于 App 端暗色模式）。
3. 仅在 App 端页面的 `<head>` 内、CSS 之前，插入本文件第 3 节的 FOUC 阻止脚本（只处理暗色模式，不读 `skin`）。
4. 根据项目需求关键词确定唯一 `data-skin` 值，写死在所有页面 `<html data-skin="...">` 上；删除任何主题切换按钮。
5. 全局替换：将硬编码的 `#3370FF` 替换为 `var(--primary)`（含业务页和登录页）。

> 迁移完成后，主题由 `<html data-skin="...">` 静态决定，同源多项目不再互相污染。

---

## 八、最小使用示例

**生成新项目时**：

1. 用户说："帮我做一个党建学习管理系统原型"
2. 技能第 0 步在系统名称"党建学习管理系统"中检测到"党建" → `data-skin="party"`
3. 所有页面 `<html>` 上写 `<html lang="zh-CN" data-skin="party">`
4. `shared/design-tokens.css` 内联 [examples.md 附录 A](examples.md) 全部三套变量
5. 业务页面照常生成，无需关心主题细节（颜色全部走变量）
6. 所有页面保持 `data-skin="party"` 固定不变，不放任何主题切换按钮
