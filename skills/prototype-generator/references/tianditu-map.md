# 天地图组件规范

> **何时使用**:数据模型中存在「地点」字段(`isAddressField()` 返回 true)时,按本规范为 PC 详情 Modal 与 App 详情子页接入天地图 JS API 4.0。
>
> - **API**:天地图 JS API 4.0(`https://api.tianditu.gov.cn/api?v=4.0&tk=TIANDITU_KEY`)
- **Key 来源**:统一从 [config.md](config.md) `TIANDITU_KEY` 字段读取(项目级配置,集中维护,不要在生成时硬编码或留占位符)
- **Key 申请**:<https://lbs.tianditu.gov.cn/server/key.html>(浏览器端,白名单 `*` 或 `localhost`)
- **本地预览**:必须 HTTPS(`python -m http.server` / `npx serve`),`api.tianditu.gov.cn` 不支持 HTTP
- **来源**:从 [examples.md](examples.md) 附录 E 抽离

---

## 概述

当数据存在「地点」字段时(**字段名**或**字段值**命中关键词),AI 应**主动**为页面增加地图导航体验,**不依赖用户提示**。

**交互形态**:

- **PC 端**:业务详情页提供「在地图中查看」按钮,点击后**在框架的同一 iframe 内切换到地图页** `pc/map.html`(单 iframe 机制,无多页签栏),返回业务页走侧边栏或面包屑。
- **App 端**:业务详情页提供「在地图中查看」按钮,点击后**原生跳转到 `app/map.html` 子页面**。

> 这是与早期版本(弹窗折叠 iframe + 高德 iframe 公开页)**不兼容的升级**——新项目请直接使用本规范方案。

---

## 识别规则(宽松模式)

字段名或字段值命中以下任一即视为「地点字段」:

- **字段名关键词**(不区分大小写、匹配开头):`address` / `location` / `addr` / `地址` / `位置` / `地点` / `场所` / `站点` / `园区` / `门店` / `仓库` / `工地` / `项目地` / `坐标` / `经纬度` / `lng` / `lat` / `lon` / `long`
- **字段值关键词**(中文地名):包含 `省 / 市 / 区 / 县 / 镇 / 路 / 街 / 道 / 巷 / 弄 / 号 / 栋 / 楼 / 座 / 园 / 区 / 站 / 厂 / 店 / 中心` 任一

**数据形态兼容(混合)优先级**:

| 优先级 | 数据形态 | 处理 |
|--------|----------|------|
| 1 | `lng + lat` 两个字段,或值是 `lng,lat` 字符串 | iframe 用坐标定位 |
| 2 | 完整地址字符串 | iframe 走 `address=` 参数 |
| 3 | 仅中文短文本(如「西湖店」) | iframe 走 `name=` 参数 |

---

## 通用工具函数(在 `shared/components.js` 暴露)

| 函数 | 用途 |
|------|------|
| `TIANDITU_KEY` | 全局变量:从 [config.md](config.md) 读取的天地图 Key |
| `loadTianDiTu()` | 动态加载天地图 JS API(防重复) |
| `isAddressField(fieldName, value)` | 识别一个字段是否是地点字段 |
| `extractLngLat(value)` | 从值里提取经纬度(支持 `"lng,lat"` / `"lng lat"`) |
| `initTianDiMap(opts)` | 在指定容器里初始化天地图(opts: containerId, lng, lat, name, address, zoom, markers) |
| `openMapTabInFrame(opts)` | 通知父页面在同一 iframe 内打开地图页(opts: title, lng, lat, address, name, markers) |

---

## PC 端接入:详情页触发「打开地图」

**场景**:用户点击列表「查看」→ 弹出详情 Modal → 详情里含地址字段 + 经纬度 → 显示「�🗺️ 在地图中查看」按钮 → 点击后**在框架同一 iframe 内切换到地图页** `pc/map.html`(单 iframe 机制,无多页签栏;返回业务页走侧边栏或面包屑),全屏展示地图(左侧活动列表 + 右侧天地图)。

### 框架页必备结构(`pc/index.html`)

**前置依赖**:PC 框架页必须实现 `openMapTab()` 全局函数(单 iframe 机制,内部即 `loadPage`),否则业务页「在地图中查看」按钮无效。

```html
<div class="main-layout">
  <aside class="sidebar">…</aside>
  <div class="main-content">
    <iframe name="mainFrame" id="mainFrame" …></iframe>
  </div>
</div>

<script>
/* 单 iframe:所有跳转直接切换 iframe 页面,侧边栏高亮自动同步 */
window.loadPage = function(url){
  document.querySelectorAll('.sidebar-nav-link').forEach(function(s){s.classList.remove('active');});
  var m = document.querySelector('.sidebar-nav-link[data-url="'+url+'"]'); if(m)m.classList.add('active');
  var f = document.getElementById('mainFrame'); if(f && url){ f.src = url; }
};
/** 业务页面调此函数打开地图页:直接切 iframe 到 pc/map.html */
window.openMapTab = function(url, title){ loadPage(url); };
document.querySelectorAll('.sidebar-nav-link[data-url]').forEach(function(item){
  item.addEventListener('click', function(e){ e.preventDefault(); loadPage(this.getAttribute('data-url')); });
});
</script>
```

### 业务详情页 Modal(HTML 片段)

```html
<!-- 活动地点行:不再折叠面板,改成按钮 -->
<div class="col-md-12">
  <div class="detail-label">活动地点</div>
  <div class="detail-value">
    <i class="bi bi-geo-alt-fill text-primary"></i> <span id="detailAddressTextSpan">—</span>
    <button class="btn btn-sm btn-outline-primary ms-2" id="btnOpenMap" onclick="openCurrentInMap()">
      <i class="bi bi-map"></i> 在地图中查看
    </button>
  </div>
</div>
```

### 业务页 JS(`showDetail` 记录当前活动,按钮触发父级打开地图页)

```javascript
var _currentActivity = null;

function showDetail(el) {
  var row = el.closest('tr'); var d = row.dataset;
  // ... 既有字段填充 ...
  document.getElementById('detailAddressTextSpan').textContent = d.address || '—';
  _currentActivity = {
    id: d.id, name: d.name || '', address: d.address || '',
    lng: parseFloat(d.lng), lat: parseFloat(d.lat)
  };
  new bootstrap.Modal(document.getElementById('xxxDetailModal')).show();
}

function openCurrentInMap() {
  if (!_currentActivity) return;
  if (isNaN(_currentActivity.lng) || isNaN(_currentActivity.lat)) {
    showToast('该活动未配置经纬度,无法定位', 'warning'); return;
  }
  // 通知父页面(PC 框架)在同一 iframe 内打开地图页
  openMapTabInFrame({
    title: '地图:' + (_currentActivity.name || '活动地点'),
    lng: _currentActivity.lng, lat: _currentActivity.lat,
    address: _currentActivity.address, name: _currentActivity.name
  });
  // 关闭 Modal
  var modal = bootstrap.Modal.getInstance(document.getElementById('xxxDetailModal'));
  if (modal) modal.hide();
}
```

> `openMapTabInFrame()`(在 `shared/components.js`)会自动调用 `window.parent.openMapTab()`。

### 地图页必备结构(`pc/map.html`)

```html
<!DOCTYPE html><html lang="zh-CN" data-skin="…">
<head>
  <link rel="stylesheet" href="…bootstrap…">
  <link rel="stylesheet" href="../shared/design-tokens.css">
  <link rel="stylesheet" href="../shared/components.css">
</head>
<body class="bg-light">
  <div id="page-content" style="padding:0;">
    <div class="map-page">
      <aside class="map-side">
        <div class="map-side-header">…</div>
        <div class="map-side-list" id="mapSideList"></div>
      </aside>
      <div class="map-canvas">
        <div id="tdtMap"></div>
        <div class="map-loading-overlay" id="mapLoading">…</div>
        <div class="map-key-warning d-none" id="keyWarning">
          请先在 <code>shared/components.js</code> 顶部将 <code>TIANDITU_KEY</code> 替换为真实 Key。
        </div>
      </div>
    </div>
  </div>
  <script src="…bootstrap.bundle.min.js"></script>
  <script src="../shared/components.js"></script>
  <script>
    function parseUrlParams() {
      var p = new URLSearchParams(location.search);
      return {
        title: p.get('title') || '活动地图',
        lng: p.get('lng') ? parseFloat(p.get('lng')) : null,
        lat: p.get('lat') ? parseFloat(p.get('lat')) : null,
        address: p.get('address') || '',
        name: p.get('name') || ''
      };
    }
    var opts = parseUrlParams();
    document.title = opts.title + ' — 系统名';
    initTianDiMap({
      containerId: 'tdtMap',
      lng: opts.lng || 120.0, lat: opts.lat || 30.5,
      zoom: opts.lng ? 15 : 9,
      markers: opts.lng ? [{lng:opts.lng, lat:opts.lat, name:opts.name, address:opts.address}] : []
    }).then(function(){
      document.getElementById('mapLoading').style.display = 'none';
      if (!TIANDITU_KEY || TIANDITU_KEY === 'YOUR_TIANDITU_KEY') document.getElementById('keyWarning').classList.remove('d-none');
    });
  </script>
</body>
</html>
```

---

## App 端接入:详情页「在地图中查看」按钮跳转子页

**场景**:用户点击列表项进入 App 详情子页 → 看到地址字段 → 显示「�🗺️ 在地图中查看」按钮 → 点击后**原生跳转 `app/map.html?lng=…&lat=…&title=…`**。

### 详情页 HTML 片段

```html
<div class="info-row">
  <span class="info-label">项目地点</span>
  <span class="info-value">
    <i class="bi bi-geo-alt-fill text-primary"></i>
    <span>浙江省杭州市西湖区文三路 478 号</span>
  </span>
</div>

<button class="btn btn-outline-primary w-100 mt-3" onclick="goToMap()">
  <i class="bi bi-map"></i> 在地图中查看
</button>
```

### JS

```javascript
function goToMap() {
  var url = 'map.html?title=' + encodeURIComponent('地图:活动名称')
    + '&lng=120.088&lat=30.305'
    + '&address=' + encodeURIComponent('浙江省杭州市西湖区文三路 478 号')
    + '&name=' + encodeURIComponent('活动名称');
  location.href = url;
}
```

### 地图子页必备结构(`app/map.html`)

复用 `pc/map.html` 的 `initTianDiMap()` 调用方式,但容器改为 `<div id="tdtMap">` 占满 `phone-content` 内的卡片(`flex: 1; height: 100%`),顶部叠加一个标题卡片显示活动名称与地址。详见 `app/map.html` 实例。

> **App 端只跳转子页**(`location.href`),**不用 `openMapTabInFrame`**(切 iframe 是 PC 框架专属机制)。

---

## AI 生成时的强制规则

1. **任何 PC 业务页面或 App 业务页面**,只要数据模型里有地址类字段(`isAddressField()` 返回 true),**必须**:
   - PC 详情 Modal → 加「业务详情页 Modal」模板("在地图中查看"按钮 + `openCurrentInMap()`)
   - PC 框架页 → 必须实现「框架页必备结构」(`openMapTab()` 全局函数,单 iframe 机制,无此函数则按钮无效)
   - PC 地图页 `pc/map.html` → 必须实现「地图页必备结构」(左侧列表 + 右侧天地图)
   - App 详情子页 → 加「App 详情页 HTML 片段」模板(跳转按钮 + `goToMap()`)
   - App 地图子页 `app/map.html` → 必须有顶部标题卡片 + 全屏 `#tdtMap` 容器
2. **优先使用经纬度**(如 `lng + lat` 双字段),其次是结构化地址字符串,最后才是中文短文本。无经纬度的活动点击按钮时**给 Toast 提示**而不是静默失败
3. **地图页在同一 iframe 内打开**:业务页调用 `openMapTabInFrame()` → 父页面 `openMapTab(url, title)` → 内部即 `loadPage(url)` 切换 iframe;返回业务页走侧边栏或面包屑
4. **配色全部走 CSS 变量**:图标 `var(--primary)`、链接默认色,**不硬编码**主题色
5. **Key 处理**:生成项目时**必须**先读取 [config.md](config.md) 的 `TIANDITU_KEY` 字段,然后把 `shared/components.js` 顶部的 `var TIANDITU_KEY = 'YOUR_TIANDITU_KEY';` 直接替换为真实 Key(不要保留占位符)。地图页检测到占位符或空值时显示橙色提示条,引导申请 Key
6. **天地图需要 HTTPS 访问**(`api.tianditu.gov.cn` 不支持 HTTP),本地预览请用 `python -m http.server` 或 `npx serve`

---

## 共享样式(写入 `shared/components.css` 末尾)

```css
/* ============================================================
   地址 → 地图组件(PC + App 通用,使用天地图 JS API)
   ============================================================ */

/* 可点击的地址文本(保留旧版样式以兼容历史页面) */
.address-link { color: var(--text-primary); text-decoration: none; cursor: pointer; }
.address-link:hover { color: var(--primary); text-decoration: underline; }

/* 天地图容器通用样式 */
#tdtMap { width: 100%; height: 100%; }

/* 暗色模式(仅 App 端生效) */
[data-theme="dark"] .map-side { background: #262626; border-color: #3d3d3d; }
[data-theme="dark"] .map-side-item { color: #e5e5e5; }
[data-theme="dark"] .map-side-item:hover { background: #333; }
[data-theme="dark"] .map-side-item.active { background: rgba(201,48,44,0.15); border-color: var(--primary); }

/* Map Side List(地图页左侧活动列表) */
.map-side { background: #fff; border-right: 1px solid var(--border-default); display: flex; flex-direction: column; height: 100%; }
.map-side-header { padding: 12px 16px; border-bottom: 1px solid var(--border-light); font-weight: 600; font-size: 0.95rem; }
.map-side-list { flex: 1; overflow-y: auto; }
.map-side-item { padding: 12px 16px; border-bottom: 1px solid var(--border-light); cursor: pointer; color: var(--text-primary); font-size: 0.875rem; }
.map-side-item:hover { background: var(--bg-hover); }
.map-side-item.active { background: var(--primary-light); color: var(--primary); border-left: 3px solid var(--primary); font-weight: 500; }

/* Map Page(PC 框架内全屏) */
.map-page { display: grid; grid-template-columns: 320px 1fr; height: calc(100vh - var(--header-height)); }
.map-canvas { position: relative; height: 100%; min-height: 0; }
.map-loading-overlay { position: absolute; inset: 0; background: rgba(255,255,255,0.85); display: flex; align-items: center; justify-content: center; z-index: 5; }
.map-key-warning { position: absolute; top: 12px; left: 50%; transform: translateX(-50%); background: #FFF3E8; color: #B45309; padding: 8px 14px; border-radius: 6px; font-size: 0.85rem; border: 1px solid #B45309; z-index: 10; }

/* App 端地图页:内容卡片样式 */
.phone-content .map-page { height: calc(100vh - 110px); grid-template-columns: 1fr; }
.phone-content .map-side { display: none; }
.phone-content .map-canvas { height: 100%; }
