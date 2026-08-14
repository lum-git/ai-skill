# 原型HTML生成器 — 参考模板

本文档是 `prototype-generator` 技能的模板参考手册，包含 PC 端、App 端、登录页、框架页、入口页的完整代码模板，以及代码风格规范和共享资源（CSS/JS）附录。

---

## 一、PC 端页面模板

### 1.1 通用页面壳

每个 PC 内容页面（在 iframe 中加载）的标准结构：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>[页面名称] — [系统名称]</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/css/bootstrap.min.css">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.13.1/font/bootstrap-icons.css">
  <link rel="stylesheet" href="../shared/design-tokens.css">
  <link rel="stylesheet" href="../shared/components.css">
</head>
<body class="bg-light">
  <div id="page-content" style="padding:1.25rem;">
    <!-- ===== 面包屑 ===== -->
    <div class="page-header">
      <ol class="breadcrumb mb-0">
        <li class="breadcrumb-item"><a href="index-content.html" target="mainFrame" onclick="try{parent.document.querySelectorAll('.sidebar-nav-link').forEach(function(s){s.classList.remove('active');});var m=parent.document.querySelector('.sidebar-nav-link[data-url=&quot;index-content.html&quot;]');if(m)m.classList.add('active');}catch(e){}">首页</a></li>
        <li class="breadcrumb-item active" aria-current="page">[模块名]</li>
      </ol>
    </div>
    <!-- ===== 页面内容区 ===== -->
    <!-- ===== 六态 ===== -->
  </div>
  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/js/bootstrap.bundle.min.js"></script>
  <script src="../shared/components.js"></script>
  <script>/* 页面逻辑 */</script>
</body>
</html>
```

### 1.2 列表页（含筛选栏+表格+分页+弹窗+六态）

```html
<!-- 筛选栏 -->
<div class="filter-bar">
  <div class="row g-2 align-items-end">
    <div class="col-md-2">
      <label class="form-label small mb-1">关键词搜索</label>
      <input type="text" class="form-control form-control-sm" id="filterKeyword" placeholder="请输入关键词" oninput="applyAllFilters()">
    </div>
    <div class="col-md-2">
      <label class="form-label small mb-1">状态</label>
      <select class="form-select form-select-sm" id="filterStatus" onchange="applyAllFilters()">
        <option value="">全部</option>
        <option value="pending">待处理</option>
        <option value="approved">已通过</option>
        <option value="rejected">已驳回</option>
      </select>
    </div>
    <div class="col-md-3">
      <label class="form-label small mb-1">时间范围</label>
      <div class="d-flex gap-1">
        <input type="date" class="form-control form-control-sm" id="filterDateFrom" onchange="applyAllFilters()">
        <input type="date" class="form-control form-control-sm" id="filterDateTo" onchange="applyAllFilters()">
      </div>
    </div>
    <div class="col-md-2">
      <label class="form-label small mb-1">&nbsp;</label>
      <div class="d-flex gap-1">
        <button class="btn btn-primary btn-sm" onclick="applyAllFilters()"><i class="bi bi-search"></i> 搜索</button>
        <button class="btn btn-outline-secondary btn-sm" onclick="clearAllFilters()"><i class="bi bi-x-circle"></i> 清除</button>
      </div>
    </div>
    <div class="col-md-3 text-md-end">
      <label class="form-label small mb-1">&nbsp;</label>
      <div><span class="result-count text-muted small">共 N 条</span></div>
    </div>
  </div>
</div>

<!-- 表格 -->
<div class="table-container">
  <table class="table table-hover align-middle" id="dataTable">
    <thead>
      <tr>
        <th style="width:40px;">#</th>
        <th class="sortable" onclick="sortTable(this, 1)">[列名1]</th>
        <th>[列名2]</th>
        <th>[列名3]</th>
        <th class="sortable" onclick="sortTable(this, 4)">创建时间</th>
        <th style="width:220px;white-space:nowrap;">操作</th>
      </tr>
    </thead>
    <tbody>
      <tr data-status="pending" data-id="1" data-name="[标题]" data-date="2026-08-10">
        <td class="text-muted small">1</td>
        <td><span class="fw-semibold text-primary" style="cursor:pointer" onclick="showDetail(this)">[数据标题]</span></td>
        <td><span class="text-muted small">[内容]</span></td>
        <td><span class="badge bg-warning text-dark">待处理</span></td>
        <td class="text-nowrap small">2026-08-10 10:30</td>
        <td class="text-nowrap">
          <button class="btn btn-sm btn-outline-primary" onclick="showDetail(this)" title="查看"><i class="bi bi-eye"></i> 查看</button>
          <button class="btn btn-sm btn-outline-secondary" onclick="editItem(this)" title="编辑"><i class="bi bi-pencil"></i> 编辑</button>
        </td>
      </tr>
      <!-- 更多数据行（至少 11~20 条） -->
    </tbody>
  </table>
  <div class="pagination-bar d-flex justify-content-between align-items-center">
    <span class="page-info">共 N 条，第 1/1 页</span>
    <div class="d-flex gap-2 align-items-center">
      <select class="form-select form-select-sm d-inline-block" style="width:auto;min-width:90px;" onchange="changePageSize(this.value)">
        <option value="10" selected>10条/页</option><option value="30">30条/页</option><option value="50">50条/页</option><option value="100">100条/页</option>
      </select>
      <div>
        <button class="btn btn-sm btn-outline-secondary page-btn disabled" onclick="goPage(currentPage-1)">上一页</button>
        <button class="btn btn-sm btn-outline-secondary page-btn disabled" onclick="goPage(currentPage+1)">下一页</button>
      </div>
    </div>
  </div>
</div>

<!-- 详情弹窗 -->
<div class="modal fade" id="detailModal" tabindex="-1" aria-hidden="true">
  <div class="modal-dialog modal-dialog-centered modal-lg">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title fw-bold">[模块]详情</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
      </div>
      <div class="modal-body">
        <div class="detail-card"><h6><i class="bi bi-info-circle me-1"></i>基本信息</h6>
          <div class="row g-3">
            <div class="col-md-6"><div class="detail-label">[字段]</div><div class="detail-value" id="detailName">-</div></div>
          </div>
        </div>
      </div>
      <div class="modal-footer">
        <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal">关闭</button>
      </div>
    </div>
  </div>
</div>

<!-- 表单弹窗 -->
<div class="modal fade" id="formModal" tabindex="-1" aria-hidden="true">
  <div class="modal-dialog modal-dialog-centered modal-lg">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title fw-bold"><span id="formTitle">新增</span>[模块]</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
      </div>
      <div class="modal-body">
        <div class="form-section"><h6 class="form-section-title">基本信息 <span class="text-danger">*</span></h6>
          <div class="row g-2">
            <div class="col-md-6 mb-2">
              <label class="form-label small fw-semibold">[字段] <span class="text-danger">*</span></label>
              <input type="text" class="form-control form-control-sm" id="formField" placeholder="请输入">
            </div>
          </div>
        </div>
      </div>
      <div class="modal-footer">
        <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal">取消</button>
        <button type="button" class="btn btn-primary" onclick="saveForm()"><i class="bi bi-check-lg"></i> 保存</button>
      </div>
    </div>
  </div>
</div>

<script>
  function showDetail(el) { var row = el.closest('tr'); document.getElementById('detailName').textContent = row.dataset.name || '-'; new bootstrap.Modal(document.getElementById('detailModal')).show(); }
  function editItem(el) { var row = el.closest('tr'); document.getElementById('formTitle').textContent = '编辑'; document.getElementById('formField').value = row.dataset.name || ''; new bootstrap.Modal(document.getElementById('formModal')).show(); }
  function openAddForm() { document.getElementById('formTitle').textContent = '新增'; document.getElementById('formField').value = ''; new bootstrap.Modal(document.getElementById('formModal')).show(); }
  function saveForm() { showToast('保存成功', 'success'); bootstrap.Modal.getInstance(document.getElementById('formModal')).hide(); }
</script>
```

### 1.3 详情页（独立页面，已废弃）

推荐优先使用弹窗模式。如需保留独立详情页（如复杂流转记录时间线）：

```html
<div class="page-header">
  <ol class="breadcrumb mb-0">
    <li class="breadcrumb-item"><a href="index-content.html" target="mainFrame">首页</a></li>
    <li class="breadcrumb-item"><a href="[list].html" target="mainFrame">[列表]</a></li>
    <li class="breadcrumb-item active">[详情]</li>
  </ol>
</div>
<div class="detail-card">
  <h6 class="mb-3"><i class="bi bi-info-circle me-1"></i> 基本信息</h6>
  <div class="row g-3"><div class="col-md-6"><div class="detail-label">[字段]</div><div class="detail-value">[值]</div></div></div>
</div>
<div class="detail-card">
  <h6 class="mb-3"><i class="bi bi-clock-history me-1"></i> 流转记录</h6>
  <div class="timeline">
    <div class="timeline-item"><div class="time">2026-08-10 14:30</div><div class="content"><strong>[操作人]</strong> [描述]</div></div>
  </div>
</div>
```

### 1.4 表单页（独立页面，已废弃）

```html
<form data-dirty="false" oninput="this.setAttribute('data-dirty','true')"
      onsubmit="event.preventDefault();this.setAttribute('data-dirty','false');showToast('保存成功','success');">
  <div class="form-section">
    <h6 class="form-section-title">基本信息 <span class="text-danger">*</span></h6>
    <div class="row g-2">
      <div class="col-md-6">
        <label class="form-label small fw-semibold">[字段] <span class="text-danger">*</span></label>
        <input type="text" class="form-control form-control-sm" required placeholder="请输入">
      </div>
    </div>
  </div>
  <div class="d-flex gap-2"><button type="submit" class="btn btn-primary"><i class="bi bi-check-lg"></i> 提交</button></div>
</form>
```

### 1.5 Dashboard 仪表板

```html
<div class="dashboard-stat-row mb-4">
  <div class="stat-card"><div class="stat-label">总数</div><div class="stat-value" style="color:var(--primary);">156</div><div class="stat-desc"><i class="bi bi-arrow-up" style="color:var(--success);"></i> 较上月 +12</div></div>
  <div class="stat-card"><div class="stat-label">已完成</div><div class="stat-value" style="color:var(--success);">108</div><div class="stat-desc">本月累计</div></div>
  <div class="stat-card"><div class="stat-label">进行中</div><div class="stat-value" style="color:var(--warning);">34</div><div class="stat-desc">待处理</div></div>
  <div class="stat-card"><div class="stat-label">超时</div><div class="stat-value" style="color:var(--danger);">7</div><div class="stat-desc">需关注</div></div>
</div>
```

### 1.6 六态（PC 端）

```html
<div class="state-empty d-none text-center py-5"><i class="bi bi-inbox" style="font-size:3rem;color:var(--gray-300);"></i><p class="mt-3 text-muted">暂无[数据]</p></div>
<div class="state-empty_filter d-none text-center py-5"><i class="bi bi-funnel" style="font-size:3rem;color:var(--gray-300);"></i><p class="mt-3 text-muted">没有匹配的结果</p><button class="btn btn-outline-secondary btn-sm mt-2" onclick="clearAllFilters();showState('page-content','normal')"><i class="bi bi-x-circle"></i> 清除筛选</button></div>
<div class="state-loading d-none"><div class="skeleton-placeholder skeleton-line w-100 mb-2" style="height:2rem;"></div><div class="skeleton-placeholder skeleton-line w-100 mb-2" style="height:2rem;"></div><div class="skeleton-placeholder skeleton-line w-100 mb-2" style="height:2rem;"></div><div class="skeleton-placeholder skeleton-line w-75" style="height:2rem;"></div></div>
<div class="state-error d-none text-center py-5"><i class="bi bi-exclamation-triangle" style="font-size:3rem;color:var(--danger);"></i><p class="mt-3 text-muted">加载失败，请重试</p><button class="btn btn-outline-danger btn-sm mt-2" onclick="showToast('正在重试...','info')"><i class="bi bi-arrow-clockwise"></i> 重试</button></div>
<div class="state-network_error d-none text-center py-5"><i class="bi bi-wifi-off" style="font-size:3rem;color:var(--gray-300);"></i><p class="mt-3 text-muted">网络连接已断开</p></div>
```

### 1.7 确认弹窗模板

```html
<div class="modal fade" id="confirmModal" tabindex="-1" aria-hidden="true">
  <div class="modal-dialog modal-dialog-centered modal-sm">
    <div class="modal-content">
      <div class="modal-header"><h5 class="modal-title" id="modalTitle">确认</h5><button type="button" class="btn-close" data-bs-dismiss="modal"></button></div>
      <div class="modal-body" id="modalBody"></div>
      <div class="modal-footer">
        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">取消</button>
        <button type="button" class="btn btn-primary" id="modalConfirmBtn">确认</button>
      </div>
    </div>
  </div>
</div>
```

---

## 二、App 端页面模板

### 2.1 Tab 页（有底部导航栏）

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>[页面名] — [系统名称]</title>
  <script>
    (function(){var t=localStorage.getItem('theme');if(t==='dark'||(!t&&window.matchMedia('(prefers-color-scheme:dark)').matches))document.documentElement.setAttribute('data-theme','dark');})();
  </script>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/css/bootstrap.min.css">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.13.1/font/bootstrap-icons.css">
  <link rel="stylesheet" href="../shared/design-tokens.css">
  <link rel="stylesheet" href="../shared/components.css">
  <link rel="stylesheet" href="assets/app.css">
</head>
<body class="bg-light phone-frame-body">
<div class="phone-frame">
  <div class="phone-status-bar">
    <span class="time">9:41</span>
    <span class="status-icons"><i class="bi bi-reception-4"></i><i class="bi bi-wifi"></i><i class="bi bi-battery-full"></i></span>
  </div>
  <div class="phone-nav-header">
    <h1 class="nav-title">[页面标题]</h1>
    <div class="nav-actions"><i class="bi bi-search" onclick="showToast('搜索','info')"></i></div>
  </div>
  <div class="phone-content">
    <!-- 页面内容 -->
    <!-- 六态 -->
    <div class="state-empty d-none text-center py-4"><i class="bi bi-inbox" style="font-size:3rem;color:#d0d0d5"></i><p class="mt-2 text-muted">暂无数据</p></div>
    <div class="state-empty_filter d-none text-center py-5"><i class="bi bi-funnel" style="font-size:3rem;color:#d0d0d5"></i><p class="mt-3 text-muted">没有匹配的结果</p><button class="btn btn-outline-secondary btn-sm" onclick="clearFilters();showState('page-content','normal')">清除筛选</button></div>
    <div class="state-loading d-none text-center py-5"><div class="spinner-border text-primary mb-2" role="status"></div><p class="text-muted">加载中...</p></div>
    <div class="state-error d-none text-center py-5"><i class="bi bi-exclamation-triangle" style="font-size:3rem;color:var(--danger)"></i><p class="mt-2 text-danger">加载失败，请重试</p><button class="btn btn-danger btn-sm" onclick="showState('page-content','normal')">重试</button></div>
    <div class="state-network_error d-none text-center py-5"><i class="bi bi-wifi-off" style="font-size:3rem;color:#d0d0d5"></i><p class="mt-2 text-muted">网络连接已断开</p></div>
  </div>
  <nav class="phone-tabbar">
    <a href="index.html" class="tab-item [active]"><i class="bi bi-house"></i>首页</a>
    <a href="messages.html" class="tab-item [active]"><i class="bi bi-bell"></i>消息<span class="badge-dot">3</span></a>
    <a href="profile.html" class="tab-item [active]"><i class="bi bi-person"></i>我的</a>
  </nav>
</div>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/js/bootstrap.bundle.min.js"></script>
<script src="../shared/components.js"></script>
<script>
  function showToast(msg, type) { var t=document.createElement('div'); t.className='alert alert-'+(type==='success'?'success':type==='danger'?'danger':'info')+' app-toast'; t.textContent=msg; document.body.appendChild(t); setTimeout(function(){t.remove();},2500); }
  function clearFilters() {}
  function showState(id, state) { var container=document.getElementById(id)||document.querySelector('.phone-content'); container.querySelectorAll('[class*="state-"]').forEach(function(el){el.classList.add('d-none');}); var target=container.querySelector('.state-'+state); if(target)target.classList.remove('d-none'); }
</script>
</body>
</html>
```

### 2.2 非 Tab 页（有返回箭头，无底部 Tab）

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>[页面名] — [系统名称]</title>
  <script>(function(){var t=localStorage.getItem('theme');if(t==='dark'||(!t&&window.matchMedia('(prefers-color-scheme:dark)').matches))document.documentElement.setAttribute('data-theme','dark');})();</script>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/css/bootstrap.min.css">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.13.1/font/bootstrap-icons.css">
  <link rel="stylesheet" href="../shared/design-tokens.css">
  <link rel="stylesheet" href="../shared/components.css">
  <link rel="stylesheet" href="assets/app.css">
</head>
<body class="bg-light phone-frame-body">
<div class="phone-frame">
  <div class="phone-status-bar"><span class="time">9:41</span><span class="status-icons"><i class="bi bi-reception-4"></i><i class="bi bi-wifi"></i><i class="bi bi-battery-full"></i></span></div>
  <div class="phone-nav-header">
    <div class="nav-left">
      <a href="[parent-page].html" class="nav-back"><i class="bi bi-chevron-left"></i></a>
      <h1 class="nav-title">[页面标题]</h1>
    </div>
    <div class="nav-actions"><i class="bi bi-search" onclick="showToast('搜索','info')"></i></div>
  </div>
  <div class="phone-content"><!-- 页面内容 + 六态 --></div>
</div>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/js/bootstrap.bundle.min.js"></script>
<script src="../shared/components.js"></script>
<script>/* 同上 showToast + showState */</script>
</body>
</html>
```

### 2.3 App 组件速查

**筛选标签（胶囊形）：**
```html
<div class="filter-tabs mb-2">
  <button class="filter-tab active" onclick="switchFilter(this,'all')">全部</button>
  <button class="filter-tab" onclick="switchFilter(this,'pending')">待处理</button>
</div>
```

**列表卡片：**
```html
<div class="task-card" onclick="location.href='[detail].html'">
  <div class="d-flex justify-content-between align-items-start"><div class="task-title">[标题]</div><span class="badge bg-warning">[状态]</span></div>
  <div class="task-table">[副标题]</div><div class="task-meta">[单位] · [时间]</div>
</div>
```

**内容卡片+详情行：**
```html
<div class="content-card mb-3">
  <div class="card-title">[标题]</div>
  <div class="detail-row"><span class="detail-label">[标签]</span><span class="detail-value">[值]</span></div>
</div>
```

**统计网格 2×2：**
```html
<div class="stat-grid mb-3">
  <div class="stat-card"><div class="stat-num">12</div><div class="stat-label">今日</div></div>
  <div class="stat-card warning"><div class="stat-num">5</div><div class="stat-label">进行中</div></div>
  <div class="stat-card success"><div class="stat-num">48</div><div class="stat-label">已完成</div></div>
  <div class="stat-card danger"><div class="stat-num">3</div><div class="stat-label">超时</div></div>
</div>
```

**快捷操作 4 列：**
```html
<div class="quick-actions">
  <button class="quick-action-item" onclick="location.href='[url].html'"><i class="bi bi-[icon]"></i> [名称]</button>
</div>
```

**用户卡片：**
```html
<div class="user-card mb-3">
  <div class="avatar">[姓]</div>
  <div class="user-info"><div class="user-name">[姓名]</div><div class="user-unit">[单位] · <span class="role-badge">[角色]</span></div></div>
</div>
```

**底部弹出选择器：**
```html
<div id="xxxPicker" class="picker-overlay d-none" onclick="closeXxxPicker()">
  <div class="picker-sheet" onclick="event.stopPropagation()">
    <div class="picker-handle"></div>
    <div class="picker-header"><h6 class="fw-bold mb-0">[标题]</h6><button type="button" class="btn-close" onclick="closeXxxPicker()"></button></div>
    <div class="picker-list px-3"><!-- 列表项 --></div>
    <div class="picker-footer">
      <button class="btn btn-outline-secondary flex-fill" onclick="closeXxxPicker()">取消</button>
      <button class="btn btn-primary flex-fill fw-semibold" onclick="confirmXxx()">确认</button>
    </div>
  </div>
</div>
```

---

## 三、登录页模板

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>登录 — [系统名称]</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/css/bootstrap.min.css">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.13.1/font/bootstrap-icons.css">
  <link rel="stylesheet" href="../shared/design-tokens.css">
  <style>
    body{min-height:100vh;display:flex;align-items:center;justify-content:center;background:linear-gradient(135deg,var(--primary-dark),var(--primary));}
    .login-card{width:100%;max-width:400px;background:#fff;border-radius:12px;padding:2.5rem 2rem;box-shadow:var(--shadow-lg);}
    .login-card .logo{text-align:center;margin-bottom:1.5rem;}
    .login-card .logo i{font-size:2.5rem;color:var(--primary);}
    .login-card .logo h4{margin-top:0.5rem;font-weight:700;}
    .login-card .logo p{color:var(--gray-500);font-size:0.85rem;}
  </style>
</head>
<body>
<div class="login-card">
  <div class="logo"><i class="bi bi-shield-check"></i><h4>[系统名称]</h4><p>[系统描述]</p></div>
  <form onsubmit="event.preventDefault();showToast('登录成功','success');setTimeout(function(){window.location.href='../pc/index.html';},800);">
    <div class="mb-3"><label class="form-label">用户名</label><div class="input-group"><span class="input-group-text"><i class="bi bi-person"></i></span><input type="text" class="form-control" placeholder="请输入用户名" required value="admin"></div></div>
    <div class="mb-3"><label class="form-label">密码</label><div class="input-group"><span class="input-group-text"><i class="bi bi-lock"></i></span><input type="password" class="form-control" placeholder="请输入密码" required value="password"></div></div>
    <button type="submit" class="btn btn-primary w-100 py-2"><i class="bi bi-box-arrow-in-right me-1"></i> 登 录</button>
  </form>
</div>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/js/bootstrap.bundle.min.js"></script>
<script src="../shared/components.js"></script>
</body>
</html>
```

---

## 四、根导航入口页 `index.html`

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>[系统名称] — 原型导航</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/css/bootstrap.min.css">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.13.1/font/bootstrap-icons.css">
  <style>
    body{background:var(--gray-50);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;}
    :root{--primary:#1e40af;--primary-dark:#1e3a8a;--gray-50:#f8f9fa;--gray-500:#64748b;--shadow-md:0 4px 12px rgba(0,0,0,0.12);}
    .container{max-width:800px;}
    .header{background:linear-gradient(135deg,var(--primary-dark),var(--primary));color:#fff;padding:2.5rem 0;margin-bottom:2rem;}
    .entry-card{background:#fff;border-radius:10px;padding:1.5rem;box-shadow:var(--shadow-md);transition:transform 0.15s;}
    .entry-card:hover{transform:translateY(-2px);}.entry-card .icon{font-size:2rem;}
  </style>
</head>
<body>
<div class="header text-center"><h2 class="mb-1"><i class="bi bi-shield-check me-2"></i>[系统名称]</h2><small>[日期] · PC X 页 + App Y 页</small></div>
<div class="container">
  <div class="row g-4">
    <div class="col-md-6"><a href="pc/index.html" class="text-decoration-none"><div class="entry-card"><div class="d-flex align-items-center gap-3 mb-2"><i class="bi bi-display icon text-primary"></i><div><h5 class="mb-0">PC 管理端</h5><small class="text-muted">全功能 · X 页</small></div></div></div></a></div>
    <div class="col-md-6"><a href="app/index.html" class="text-decoration-none"><div class="entry-card"><div class="d-flex align-items-center gap-3 mb-2"><i class="bi bi-phone icon text-success"></i><div><h5 class="mb-0">App 端</h5><small class="text-muted">移动端 · Y 页</small></div></div></div></a></div>
    <div class="col-md-6"><a href="login/index.html" class="text-decoration-none"><div class="entry-card"><div class="d-flex align-items-center gap-3 mb-2"><i class="bi bi-box-arrow-in-right icon text-danger"></i><div><h5 class="mb-0">登录页</h5><small class="text-muted">用户认证</small></div></div></div></a></div>
  </div>
</div>
</body>
</html>
```

---

## 五、PC 框架页 `pc/index.html`

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>[系统名称] — 管理后台</title>
  <script>(function(){var t=localStorage.getItem('theme');if(t==='dark'||(!t&&window.matchMedia('(prefers-color-scheme:dark)').matches))document.documentElement.setAttribute('data-theme','dark');})();</script>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/css/bootstrap.min.css">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.13.1/font/bootstrap-icons.css">
  <link rel="stylesheet" href="../shared/design-tokens.css">
  <link rel="stylesheet" href="../shared/components.css">
</head>
<body>
<header class="header-navbar">
  <div class="d-flex align-items-center gap-2">
    <div class="header-logo"><i class="bi bi-shield-check"></i> [系统简称]</div>
    <button class="navbar-toggler-responsive" onclick="toggleSidebar()"><i class="bi bi-list"></i></button>
  </div>
  <div class="header-right">
    <span class="env-badge non-secret">正式版</span>
    <span class="header-notification" onclick="document.getElementById('mainFrame').src='messages.html';document.querySelectorAll('.sidebar-nav-link').forEach(function(s){s.classList.remove('active');});var m=document.querySelector('.sidebar-nav-link[data-url=&quot;messages.html&quot;]');if(m)m.classList.add('active');"><i class="bi bi-bell"></i><span class="badge rounded-pill bg-danger badge-notify">3</span></span>
    <div class="header-user dropdown">
      <div class="d-flex align-items-center gap-2" data-bs-toggle="dropdown"><div class="user-avatar">管</div><span class="user-name">管理员 <i class="bi bi-chevron-down" style="font-size:0.7rem;"></i></span></div>
      <ul class="dropdown-menu dropdown-menu-end">
        <li><a class="dropdown-item" href="#" onclick="showToast('功能开发中','info')"><i class="bi bi-person me-2"></i>个人信息</a></li>
        <li><hr class="dropdown-divider"></li>
        <li><a class="dropdown-item" href="../login/index.html"><i class="bi bi-box-arrow-right me-2"></i>退出登录</a></li>
      </ul>
    </div>
  </div>
</header>
<div class="main-layout">
  <aside class="sidebar"><!-- MENU_ITEMS_PLACEHOLDER --></aside>
  <div class="main-content">
    <div style="position:relative;"><div class="iframe-loading-overlay" id="iframeLoading" style="display:none;"><div class="spinner-border text-primary"></div></div><iframe name="mainFrame" id="mainFrame" src="index-content.html" style="border:none;width:100%;min-height:calc(100vh - var(--header-height));" sandbox="allow-same-origin allow-scripts allow-forms allow-popups"></iframe></div>
  </div>
</div>
<div id="sidebarBackdrop" class="sidebar-backdrop" onclick="closeSidebar()"></div>
<button onclick="toggleTheme()" class="btn btn-sm btn-outline-secondary rounded-circle" style="position:fixed;bottom:1rem;right:1rem;width:36px;height:36px;z-index:1050;"><i class="bi bi-moon-stars"></i></button>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/js/bootstrap.bundle.min.js"></script>
<script src="../shared/components.js"></script>
<script>
  // PC 框架菜单跳转：原生 <a target="mainFrame"> + 同步 .active + 显示 loading
  document.querySelectorAll('.sidebar-nav-link[data-url]').forEach(function(item){
    item.addEventListener('click', function(e){
      e.preventDefault();
      document.querySelectorAll('.sidebar-nav-link').forEach(function(s){s.classList.remove('active');});
      this.classList.add('active');
      var url = this.getAttribute('data-url');
      var frame = document.getElementById('mainFrame');
      var overlay = document.getElementById('iframeLoading');
      if (frame && url) { if (overlay) overlay.style.display = 'flex'; frame.src = url; }
    });
  });
  // iframe 加载完关闭 loading
  var _mainFrame = document.getElementById('mainFrame');
  if (_mainFrame) _mainFrame.addEventListener('load', function(){ var o=document.getElementById('iframeLoading'); if(o) o.style.display='none'; });
  // 侧边栏折叠状态持久化
  if (localStorage.getItem('sidebar-collapsed')==='1') document.body.classList.add('sidebar-collapsed');
  // 菜单跳转通过原生 <a target="mainFrame">，框架不提供额外跳转 API
</script>
</body>
</html>
```

**Sidebar 菜单项格式：**
```html
<a class="sidebar-nav-link active" data-url="index-content.html" href="index-content.html" target="mainFrame"><i class="bi bi-speedometer2"></i> <span>工作台</span></a>
<div class="sidebar-divider"></div>
<div class="sidebar-section-title">系统管理</div>
<a class="sidebar-nav-link" data-url="[file].html" href="[file].html" target="mainFrame"><i class="bi bi-[icon]"></i> <span>[名称]</span></a>
<!-- 折叠分组 -->
<a class="sidebar-nav-link" data-bs-toggle="collapse" data-bs-target="#navGroup1" aria-expanded="false" href="#navGroup1" role="button"><i class="bi bi-[icon]"></i> <span>[分组名]</span></a>
<div class="collapse" id="navGroup1"><a class="sidebar-nav-link" data-url="[file].html" href="[file].html" target="mainFrame"><i class="bi bi-[icon]"></i> <span>[名称]</span></a></div>
```

---

## 六、代码风格规范

```javascript
// 用 var，用 function 声明
var data = [...];
function applyAllFilters() {
  var keyword = document.getElementById('filterKeyword').value.trim().toLowerCase();
  var rows = document.querySelectorAll('#dataTable tbody tr');
  var count = 0;
  rows.forEach(function(row) { /* 筛选逻辑 */ row.classList.toggle('d-none', !match); if (match) count++; });
  document.querySelector('.result-count').textContent = '共 ' + count + ' 条';
  if (typeof renderPage === 'function') renderPage();
}
// 分页（默认每页10条，数据量 11~20 条才能体现分页）
initPagination(10);
```

```html
<!-- 分区注释 ==== --> <!-- 可见性注释 --> <!-- 状态 Badge -->
<span class="badge bg-warning text-dark">进行中</span>
<span class="badge bg-success">已完成</span>
<!-- 表格行属性 --><tr data-status="pending">
<!-- 按钮 --><button class="btn btn-sm btn-outline-primary"><i class="bi bi-[name] me-1"></i> 操作</button>
```

CSS：始终用 `var(--primary)`、`var(--gray-200)` 等变量，不硬编码色值。

---

## 附录 A：shared/design-tokens.css

```css
:root {
  --primary:#3370FF;--primary-hover:#2860E1;--primary-active:#1F4DC4;--primary-light:#E1EBFF;--primary-bg:#F0F5FF;
  --success:#00B578;--success-light:#E8F9F2;--warning:#FF7D00;--warning-light:#FFF3E8;--danger:#F53F3F;--danger-light:#FFEDED;
  --text-primary:#1F2329;--text-secondary:#646A73;--text-tertiary:#8F959E;--text-disabled:#BEC2C7;
  --bg-body:#F5F6F7;--bg-white:#FFFFFF;--bg-card:#FFFFFF;--bg-hover:#F2F3F5;--bg-active:#E8EAED;--bg-mask:rgba(0,0,0,0.4);
  --border-default:#E5E6EB;--border-light:#F0F1F4;--border-heavy:#C9CDD4;
  --sidebar-bg:#1F2329;--sidebar-hover:#2B2F36;--sidebar-text:#8B8F97;--sidebar-text-hover:#C9CDD4;--sidebar-text-active:#FFFFFF;--sidebar-section-title:#5E6269;--sidebar-divider:rgba(255,255,255,0.06);
  --header-bg:#FFFFFF;--header-border:#E5E6EB;--header-height:56px;
  --shadow-xs:0 1px 2px rgba(0,0,0,0.04);--shadow-sm:0 1px 3px rgba(0,0,0,0.06);--shadow-md:0 4px 12px rgba(0,0,0,0.08);--shadow-lg:0 8px 24px rgba(0,0,0,0.12);--shadow-card:0 1px 4px rgba(0,0,0,0.04);
  --radius-xs:4px;--radius-sm:6px;--radius-md:8px;--radius-lg:12px;--radius-xl:16px;--radius-full:9999px;
  --space-xs:4px;--space-sm:8px;--space-md:12px;--space-lg:16px;--space-xl:20px;--space-2xl:24px;--space-3xl:32px;
  --font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei","Helvetica Neue",Arial,sans-serif;
  --font-size-base:13px;--font-size-md:14px;--font-size-lg:16px;--font-size-xl:18px;--font-size-2xl:20px;--font-size-3xl:24px;
  --sidebar-width:220px;--sidebar-collapsed-width:64px;
}
```

## 附录 B：shared/components.css

以下为完整的 PC 端全局组件样式，生成项目时直接写入 `shared/components.css`：

```css
/* ============================================================
   全局组件样式
   ============================================================ */

body {
  font-family: var(--font-family);
  background: var(--bg-body);
  color: var(--text-primary);
  font-size: var(--font-size-md);
  line-height: 1.5;
  -webkit-font-smoothing: antialiased;
}

a { color: var(--text-link); text-decoration: none; }
a:hover { color: var(--primary-hover); }

/* ---- Header ---- */
.header-navbar {
  position: fixed; top: 0; left: 0; right: 0; z-index: 1030;
  height: var(--header-height);
  background: var(--header-bg);
  border-bottom: 1px solid var(--header-border);
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 var(--space-lg);
  box-shadow: var(--shadow-xs);
}
.header-navbar .header-logo { font-size: var(--font-size-lg); font-weight: 600; color: var(--text-primary); display: flex; align-items: center; gap: var(--space-sm); white-space: nowrap; }
.header-navbar .header-logo i { font-size: 1.3rem; color: var(--primary); }
.header-navbar .header-right { display: flex; align-items: center; gap: var(--space-md); }
.header-navbar .env-badge { font-size: var(--font-size-xs); padding: 2px 8px; border-radius: var(--radius-full); background: var(--success-light); color: var(--success); font-weight: 500; }
.header-navbar .header-notification { color: var(--text-secondary); cursor: pointer; font-size: 1.15rem; position: relative; padding: 6px; border-radius: var(--radius-sm); }
.header-navbar .header-notification:hover { background: var(--bg-hover); color: var(--text-primary); }
.header-navbar .header-notification .badge-notify { position: absolute; top: 2px; right: 2px; min-width: 16px; height: 16px; font-size: 10px; font-weight: 600; border-radius: var(--radius-full); background: var(--danger); color: #fff; text-align: center; padding: 0 4px; line-height: 16px; }
.header-navbar .header-user { display: flex; align-items: center; gap: var(--space-sm); cursor: pointer; color: var(--text-primary); padding: 4px 8px; border-radius: var(--radius-sm); }
.header-navbar .header-user:hover { background: var(--bg-hover); }
.header-navbar .header-user .user-avatar { width: 30px; height: 30px; border-radius: var(--radius-full); background: var(--primary); color: #fff; display: flex; align-items: center; justify-content: center; font-size: var(--font-size-sm); font-weight: 600; }
.header-navbar .header-user .user-name { font-size: var(--font-size-md); font-weight: 500; }
.navbar-toggler-responsive { color: var(--text-secondary); background: none; border: none; font-size: 1.2rem; cursor: pointer; padding: 4px 8px; border-radius: var(--radius-sm); }
.navbar-toggler-responsive:hover { background: var(--bg-hover); }

/* ---- Layout ---- */
.main-layout { display: flex; padding-top: var(--header-height); }

/* ---- Sidebar ---- */
.sidebar { position: fixed; top: var(--header-height); left: 0; bottom: 0; width: var(--sidebar-width); z-index: 1010; background: var(--sidebar-bg); overflow-y: auto; overflow-x: hidden; display: flex; flex-direction: column; }
.sidebar .sidebar-section-title { font-size: var(--font-size-xs); font-weight: 500; color: var(--sidebar-section-title); padding: var(--space-lg) var(--space-lg) var(--space-sm); text-transform: uppercase; letter-spacing: 0.05em; }
.sidebar .sidebar-nav-link { display: flex; align-items: center; gap: 10px; padding: 8px 12px; margin: 1px 8px; color: var(--sidebar-text); text-decoration: none; font-size: var(--font-size-md); font-weight: 400; border-radius: var(--radius-sm); transition: all 0.15s; position: relative; cursor: pointer; border: none; background: none; width: auto; text-align: left; }
.sidebar .sidebar-nav-link i { font-size: 1.1rem; width: 20px; text-align: center; flex-shrink: 0; color: var(--sidebar-text); }
.sidebar .sidebar-nav-link:hover { background: var(--sidebar-hover); color: var(--sidebar-text-hover); }
.sidebar .sidebar-nav-link:hover i { color: var(--sidebar-text-hover); }
.sidebar .sidebar-nav-link.active { background: rgba(51,112,255,0.12); color: var(--sidebar-text-active); font-weight: 500; }
.sidebar .sidebar-nav-link.active i { color: var(--primary); }
.sidebar .sidebar-nav-link.active::before { content: ''; position: absolute; left: 0; top: 50%; transform: translateY(-50%); width: 3px; height: 16px; background: var(--primary); border-radius: 0 2px 2px 0; }
.sidebar .collapse { padding: 0; }
.sidebar .collapse .sidebar-nav-link { padding-left: 42px; font-size: var(--font-size-base); }
.sidebar .sidebar-divider { height: 1px; background: var(--sidebar-divider); margin: var(--space-sm) var(--space-lg); }

/* collapsed */
.sidebar-collapsed .sidebar { width: var(--sidebar-collapsed-width); }
.sidebar-collapsed .sidebar .sidebar-nav-link span { display: none; }
.sidebar-collapsed .sidebar .sidebar-nav-link { justify-content: center; padding: 10px 0; margin: 2px 8px; }
.sidebar-collapsed .sidebar .sidebar-section-title { display: none; }
.sidebar-collapsed .sidebar .sidebar-divider { display: none; }
.sidebar-collapsed .sidebar .collapse { display: none !important; }
.sidebar-collapsed .sidebar .sidebar-nav-link.active::before { display: none; }
.sidebar-collapsed .main-content { margin-left: var(--sidebar-collapsed-width); }
.sidebar-backdrop { display: none; position: fixed; inset: 0; background: var(--bg-mask); z-index: 1005; }

.main-content { flex: 1; margin-left: var(--sidebar-width); min-width: 0; }
.iframe-loading-overlay { position: absolute; inset: 0; background: rgba(255,255,255,0.7); display: flex; align-items: center; justify-content: center; z-index: 10; }

/* ---- Breadcrumb ---- */
.breadcrumb { font-size: var(--font-size-sm); background: transparent; padding: 0; margin: 0; }
.breadcrumb .breadcrumb-item a { color: var(--text-tertiary); }
.breadcrumb .breadcrumb-item a:hover { color: var(--primary); }
.breadcrumb .breadcrumb-item.active { color: var(--text-primary); font-weight: 500; }

/* ---- Stat Card ---- */
.dashboard-stat-row { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: var(--space-lg); }
.stat-card { background: var(--bg-white); border: 1px solid var(--border-light); border-radius: var(--radius-md); padding: var(--space-xl); box-shadow: var(--shadow-card); }
.stat-card:hover { box-shadow: var(--shadow-md); transform: translateY(-1px); }
.stat-card .stat-label { font-size: var(--font-size-sm); color: var(--text-tertiary); margin-bottom: var(--space-sm); }
.stat-card .stat-value { font-size: 28px; font-weight: 600; color: var(--text-primary); line-height: 1.2; }
.stat-card .stat-desc { font-size: var(--font-size-sm); color: var(--text-tertiary); margin-top: var(--space-xs); }

/* ---- Page ---- */
#page-content { padding: var(--space-2xl); }
.page-header { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: var(--space-md); margin-bottom: var(--space-2xl); }
.page-header h5 { margin: 0; font-weight: 600; font-size: var(--font-size-xl); }
.content-card { background: var(--bg-white); border: 1px solid var(--border-light); border-radius: var(--radius-md); padding: var(--space-xl); box-shadow: var(--shadow-card); }

/* ---- Filter ---- */
.filter-bar { background: var(--bg-white); border: 1px solid var(--border-light); border-radius: var(--radius-md); padding: var(--space-lg); margin-bottom: var(--space-lg); box-shadow: var(--shadow-card); }
.filter-bar .form-label { font-size: var(--font-size-sm); color: var(--text-secondary); font-weight: 500; }

/* ---- Table ---- */
.table-container { background: var(--bg-white); border: 1px solid var(--border-light); border-radius: var(--radius-md); overflow: hidden; box-shadow: var(--shadow-card); }
.table-container .table { margin: 0; }
.table-container .table thead th { background: var(--bg-body); font-size: var(--font-size-sm); font-weight: 500; color: var(--text-secondary); border-bottom: 1px solid var(--border-default); padding: 10px var(--space-lg); white-space: nowrap; }
.table-container .table tbody td { font-size: var(--font-size-md); color: var(--text-primary); vertical-align: middle; padding: 10px var(--space-lg); border-bottom: 1px solid var(--border-light); }
.table-container .table tbody tr:hover { background: var(--bg-hover); }
.table-container .table tbody tr:last-child td { border-bottom: none; }
th.sortable { cursor: pointer; user-select: none; }
th.sortable:hover { color: var(--primary); }
th.sortable::after { content: ' ↕'; font-size: 10px; color: var(--text-disabled); margin-left: 2px; }
.pagination-bar { display: flex; align-items: center; justify-content: space-between; padding: var(--space-md) var(--space-lg); border-top: 1px solid var(--border-light); background: var(--bg-white); }
.pagination-bar .page-info { font-size: var(--font-size-sm); color: var(--text-tertiary); }

/* ---- Form ---- */
.form-section { background: var(--bg-white); border: 1px solid var(--border-light); border-radius: var(--radius-md); padding: var(--space-xl); margin-bottom: var(--space-lg); box-shadow: var(--shadow-card); }
.form-section .form-section-title { font-size: var(--font-size-lg); font-weight: 600; color: var(--text-primary); margin-bottom: var(--space-lg); padding-bottom: var(--space-md); border-bottom: 1px solid var(--border-light); }

/* ---- Detail ---- */
.detail-card { background: var(--bg-white); border: 1px solid var(--border-light); border-radius: var(--radius-md); padding: var(--space-xl); margin-bottom: var(--space-lg); box-shadow: var(--shadow-card); }
.detail-card h6 { font-size: var(--font-size-lg); font-weight: 600; color: var(--text-primary); margin-bottom: var(--space-lg); padding-bottom: var(--space-md); border-bottom: 1px solid var(--border-light); }
.detail-card .detail-label { font-size: var(--font-size-sm); color: var(--text-tertiary); margin-bottom: 4px; }
.detail-card .detail-value { font-size: var(--font-size-md); color: var(--text-primary); font-weight: 500; }

/* ---- Timeline ---- */
.timeline { position: relative; padding-left: var(--space-2xl); }
.timeline::before { content: ''; position: absolute; left: 7px; top: 4px; bottom: 0; width: 1px; background: var(--border-default); }
.timeline-item { position: relative; padding-bottom: var(--space-xl); }
.timeline-item:last-child { padding-bottom: 0; }
.timeline-item::before { content: ''; position: absolute; left: -21px; top: 4px; width: 8px; height: 8px; border-radius: var(--radius-full); background: var(--primary); border: 2px solid var(--bg-white); box-shadow: 0 0 0 2px var(--primary-light); }
.timeline-item .time { font-size: var(--font-size-sm); color: var(--text-tertiary); margin-bottom: 2px; }
.timeline-item .content { font-size: var(--font-size-md); color: var(--text-primary); }

/* ---- Skeleton ---- */
.skeleton-placeholder { background: linear-gradient(90deg, var(--border-light) 25%, var(--bg-hover) 50%, var(--border-light) 75%); background-size: 200% 100%; animation: skeleton-shimmer 1.5s infinite; border-radius: var(--radius-sm); }
@keyframes skeleton-shimmer { 0% { background-position: 200% 0; } 100% { background-position: -200% 0; } }

/* ---- Button ---- */
.btn { font-weight: 500; font-size: var(--font-size-md); border-radius: var(--radius-sm); padding: 6px 16px; }
.btn-sm { font-size: var(--font-size-sm); padding: 4px 12px; border-radius: var(--radius-xs); }
.btn-primary { background: var(--primary); border-color: var(--primary); }
.btn-primary:hover { background: var(--primary-hover); border-color: var(--primary-hover); }
.btn-primary:active { background: var(--primary-active) !important; border-color: var(--primary-active) !important; }
.btn-outline-primary { color: var(--primary); border-color: var(--primary); }
.btn-outline-primary:hover { background: var(--primary-light); color: var(--primary-hover); border-color: var(--primary-hover); }
.btn-outline-secondary { color: var(--text-secondary); border-color: var(--border-default); }
.btn-outline-secondary:hover { background: var(--bg-hover); border-color: var(--border-heavy); color: var(--text-primary); }
.btn-success { background: var(--success); border-color: var(--success); }
.btn-danger { background: var(--danger); border-color: var(--danger); }
.btn-warning { background: var(--warning); border-color: var(--warning); color: #fff; }

/* ---- Input ---- */
.form-control, .form-select { font-size: var(--font-size-md); border-radius: var(--radius-sm); border-color: var(--border-default); padding: 6px 12px; }
.form-control:focus, .form-select:focus { border-color: var(--primary); box-shadow: 0 0 0 3px var(--primary-light); }
.form-control-sm, .form-select-sm { font-size: var(--font-size-sm); padding: 4px 10px; border-radius: var(--radius-xs); }

/* ---- Badge ---- */
.badge { font-weight: 500; font-size: var(--font-size-xs); padding: 3px 8px; border-radius: var(--radius-xs); }
.bg-primary { background: var(--primary) !important; }
.bg-success { background: var(--success) !important; }
.bg-danger { background: var(--danger) !important; }
.bg-warning { background: var(--warning) !important; }
.bg-info { background: var(--primary-light) !important; color: var(--primary) !important; }

/* ---- Modal ---- */
.modal-content { border-radius: var(--radius-lg); border: none; box-shadow: var(--shadow-lg); }
.modal-header { padding: var(--space-xl) var(--space-xl) var(--space-md); border-bottom: none; }
.modal-header .modal-title { font-weight: 600; font-size: var(--font-size-lg); }
.modal-body { padding: var(--space-md) var(--space-xl); font-size: var(--font-size-md); color: var(--text-secondary); }
.modal-footer { padding: var(--space-md) var(--space-xl) var(--space-xl); border-top: none; gap: var(--space-sm); }

/* ---- Dropdown ---- */
.dropdown-menu { border: 1px solid var(--border-default); border-radius: var(--radius-md); box-shadow: var(--shadow-lg); padding: var(--space-xs) 0; min-width: 180px; animation: dropdownFadeIn 0.15s; }
.dropdown-item { font-size: var(--font-size-md); padding: 8px var(--space-lg); color: var(--text-primary); }
.dropdown-item:hover { background: var(--bg-hover); }
.dropdown-divider { border-color: var(--border-light); margin: var(--space-xs) 0; }
@keyframes dropdownFadeIn { from { opacity: 0; transform: translateY(-4px); } to { opacity: 1; transform: translateY(0); } }

/* ---- Dark Mode ---- */
[data-theme="dark"] {
  --bg-body: #1A1A1A; --bg-white: #262626; --bg-card: #262626; --bg-hover: #333333; --bg-active: #3D3D3D;
  --text-primary: #E5E5E5; --text-secondary: #999999; --text-tertiary: #707070; --text-disabled: #555555;
  --border-default: #3D3D3D; --border-light: #333333; --border-heavy: #555555;
  --header-bg: #262626; --header-border: #333333;
  --sidebar-bg: #1A1A1A; --sidebar-hover: #2B2B2B; --sidebar-text: #808080; --sidebar-text-hover: #B3B3B3; --sidebar-text-active: #E5E5E5; --sidebar-section-title: #666666; --sidebar-divider: rgba(255,255,255,0.04);
  --primary-bg: #1A2D4D; --primary-light: #1F3A66;
  --shadow-xs: 0 1px 2px rgba(0,0,0,0.2); --shadow-sm: 0 1px 3px rgba(0,0,0,0.3); --shadow-md: 0 4px 12px rgba(0,0,0,0.4); --shadow-lg: 0 8px 24px rgba(0,0,0,0.5); --shadow-card: 0 1px 4px rgba(0,0,0,0.2);
}
[data-theme="dark"] body { background: var(--bg-body); }
[data-theme="dark"] .content-card, [data-theme="dark"] .stat-card, [data-theme="dark"] .filter-bar, [data-theme="dark"] .table-container, [data-theme="dark"] .form-section, [data-theme="dark"] .detail-card { background: var(--bg-card); border-color: var(--border-light); }
[data-theme="dark"] .table-container .table thead th { background: #2A2A2A; color: var(--text-tertiary); }
[data-theme="dark"] .table-container .table tbody td { border-color: var(--border-light); }
[data-theme="dark"] .table-container .table tbody tr:hover { background: var(--bg-hover); }
[data-theme="dark"] .pagination-bar { border-top-color: var(--border-light); }
[data-theme="dark"] .form-control, [data-theme="dark"] .form-select { background: #333333; border-color: var(--border-default); color: var(--text-primary); }
[data-theme="dark"] .form-control:focus, [data-theme="dark"] .form-select:focus { box-shadow: 0 0 0 3px rgba(51,112,255,0.15); }
[data-theme="dark"] .header-navbar { background: var(--bg-card); border-color: var(--border-light); }
[data-theme="dark"] .header-navbar .header-logo { color: var(--text-primary); }
[data-theme="dark"] .header-navbar .header-notification { color: var(--text-secondary); }
[data-theme="dark"] .header-navbar .header-notification:hover { background: var(--bg-hover); }
[data-theme="dark"] .header-navbar .header-user { color: var(--text-primary); }
[data-theme="dark"] .header-navbar .header-user:hover { background: var(--bg-hover); }
[data-theme="dark"] .navbar-toggler-responsive { color: var(--text-secondary); }
[data-theme="dark"] .dropdown-menu { background: #333333; border-color: var(--border-default); }
[data-theme="dark"] .dropdown-item { color: var(--text-primary); }
[data-theme="dark"] .dropdown-item:hover { background: #444444; }
[data-theme="dark"] .dropdown-divider { border-color: var(--border-default); }
[data-theme="dark"] .modal-content { background: var(--bg-card); }
[data-theme="dark"] .modal-header, [data-theme="dark"] .modal-footer { border-color: var(--border-light); }
[data-theme="dark"] .timeline::before { background: var(--border-default); }
[data-theme="dark"] .timeline-item::before { border-color: var(--bg-card); }
[data-theme="dark"] .breadcrumb .breadcrumb-item a { color: var(--text-tertiary); }
[data-theme="dark"] .breadcrumb .breadcrumb-item.active { color: var(--text-primary); }
[data-theme="dark"] .breadcrumb-item + .breadcrumb-item::before { color: var(--text-disabled); }
[data-theme="dark"] .filter-bar .form-label { color: var(--text-tertiary); }
[data-theme="dark"] .stat-card .stat-value { color: var(--text-primary); }
[data-theme="dark"] .detail-card .detail-value { color: var(--text-primary); }
[data-theme="dark"] .text-muted { color: var(--text-tertiary) !important; }
[data-theme="dark"] .btn-outline-secondary { color: var(--text-secondary); border-color: var(--border-default); }
[data-theme="dark"] .btn-outline-secondary:hover { background: var(--bg-hover); color: var(--text-primary); }
```

## 附录 C：shared/components.js

以下为完整的共享工具库，生成项目时直接写入 `shared/components.js`：

本工具库只提供"页面内"工具函数（Toast/弹窗/分页/排序/筛选/主题/侧边栏）。PC 端菜单跳转通过原生 `<a href="xxx.html" target="mainFrame">` 完成，业务页面无需自写跳转逻辑。

```javascript
/* ============================================================
   共享工具库 — 原型项目
   提供：状态切换/Toast/确认弹窗/分页/排序/筛选/主题/侧边栏
   说明：菜单跳转通过原生 <a target="mainFrame"> 完成
   ============================================================ */

function showToast(msg, type) {
  var t = document.createElement('div');
  t.className = 'alert alert-' + (type==='success'?'success':type==='danger'?'danger':type==='warning'?'warning':'info') + ' position-fixed top-0 start-50 translate-middle-x mt-2';
  t.style.cssText = 'z-index:9999;max-width:400px;font-size:0.85rem;padding:0.6rem 1rem;border-radius:8px;box-shadow:0 4px 12px rgba(0,0,0,0.2)';
  t.textContent = msg; document.body.appendChild(t); setTimeout(function() { t.remove(); }, 2500);
}

function showState(containerId, state) {
  var container = document.getElementById(containerId);
  if (!container) return;
  container.querySelectorAll('[class*="state-"]').forEach(function(el) { el.classList.add('d-none'); });
  var target = container.querySelector('.state-' + state);
  if (target) target.classList.remove('d-none');
}

function confirmModal(title, body, onConfirm) {
  var modalEl = document.getElementById('confirmModal');
  if (!modalEl) return;
  var modalTitle = modalEl.querySelector('#modalTitle');
  var modalBody = modalEl.querySelector('#modalBody');
  var confirmBtn = modalEl.querySelector('#modalConfirmBtn');
  if (modalTitle) modalTitle.textContent = title;
  if (modalBody) modalBody.textContent = body;
  var bsModal = new bootstrap.Modal(modalEl);
  var handler = function() { bsModal.hide(); if (onConfirm) onConfirm(); };
  if (confirmBtn) { confirmBtn.replaceWith(confirmBtn.cloneNode(true)); confirmBtn = modalEl.querySelector('#modalConfirmBtn'); confirmBtn.addEventListener('click', handler); }
  bsModal.show();
}

var currentPage = 1, pageSize = 10, totalItems = 0;
function initPagination(size) { pageSize = size || 10; currentPage = 1; renderPage(); }
function changePageSize(size) { pageSize = parseInt(size); currentPage = 1; renderPage(); }
function goPage(p) { var visibleRows = document.querySelectorAll('#dataTable tbody tr:not(.d-none)'); if (!visibleRows.length) { currentPage = p; renderPage(); return; } totalItems = visibleRows.length; var totalPages = Math.ceil(totalItems / pageSize); if (p < 1 || p > totalPages) return; currentPage = p; visibleRows.forEach(function(row, i) { row.style.display = (i >= (currentPage - 1) * pageSize && i < currentPage * pageSize) ? '' : 'none'; }); updatePaginationUI(totalPages); }
function renderPage() { var rows = document.querySelectorAll('#dataTable tbody tr:not(.d-none)'); totalItems = rows.length; var totalPages = totalItems === 0 ? 1 : Math.ceil(totalItems / pageSize); if (currentPage > totalPages) currentPage = totalPages; rows.forEach(function(row, i) { row.style.display = (i >= (currentPage - 1) * pageSize && i < currentPage * pageSize) ? '' : 'none'; }); updatePaginationUI(totalPages); }
function updatePaginationUI(totalPages) {
  var infoEl = document.querySelector('.page-info');
  if (infoEl) infoEl.textContent = '共 ' + totalItems + ' 条，第 ' + currentPage + '/' + Math.max(totalPages, 1) + ' 页';
  var prevBtn = document.querySelector('.page-btn:first-child');
  var nextBtn = document.querySelector('.page-btn:last-child');
  if (prevBtn) prevBtn.classList.toggle('disabled', currentPage <= 1);
  if (nextBtn) nextBtn.classList.toggle('disabled', currentPage >= totalPages);
}

var lastSortCol = -1, sortDirection = 1;
function sortTable(th, colIndex) {
  var table = th.closest('table'), tbody = table.querySelector('tbody');
  var rows = Array.from(tbody.querySelectorAll('tr'));
  if (lastSortCol !== colIndex) { sortDirection = 1; lastSortCol = colIndex; }
  var dir = sortDirection;
  rows.sort(function(a, b) { var av = a.cells[colIndex].textContent.trim(), bv = b.cells[colIndex].textContent.trim(); return av.localeCompare(bv, 'zh-CN') * dir; });
  rows.forEach(function(row) { tbody.appendChild(row); });
  sortDirection *= -1; renderPage();
}

function clearAllFilters() {
  document.querySelectorAll('input[type="text"]:not([readonly]), input[type="date"], select').forEach(function(el) {
    if (el.tagName === 'SELECT') el.selectedIndex = 0; else el.value = '';
  });
  document.querySelectorAll('#dataTable tbody tr').forEach(function(tr) { tr.classList.remove('d-none'); tr.style.display = ''; });
  currentPage = 1; showState('page-content', 'normal'); renderPage();
}

function toggleTheme() {
  var current = document.documentElement.getAttribute('data-theme');
  var next = current === 'dark' ? '' : 'dark';
  document.documentElement.setAttribute('data-theme', next);
  if (!next) document.documentElement.removeAttribute('data-theme');
  localStorage.setItem('theme', next || 'light');
}

function toggleSidebar() {
  var collapsed = document.body.classList.toggle('sidebar-collapsed');
  localStorage.setItem('sidebar-collapsed', collapsed ? '1' : '0');
}
function closeSidebar() {
  if (window.innerWidth < 992) { document.body.classList.add('sidebar-collapsed'); document.getElementById('sidebarBackdrop').style.display = 'none'; }
}

function formatDate(d) { if (!d) return ''; var dt = new Date(d); return dt.getFullYear() + '-' + String(dt.getMonth()+1).padStart(2,'0') + '-' + String(dt.getDate()).padStart(2,'0'); }
function formatMoney(n) { return n.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ','); }
```

## 附录 D：app/assets/app.css

以下为完整的 App 端专用样式，生成项目时直接写入 `app/assets/app.css`：

```css
/* ============================================================
   App 端专用样式 — 手机模型框架
   浅色外框，无黑边，flexbox 列布局
   ============================================================ */

body.phone-frame-body {
  background: #e8eaed;
  display: flex; align-items: center; justify-content: center;
  min-height: 100vh; padding: 16px;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", sans-serif;
  -webkit-font-smoothing: antialiased;
}

.phone-frame {
  width: 390px; height: 844px;
  background: var(--bg-body);
  border-radius: 44px; overflow: hidden;
  box-shadow: 0 30px 80px rgba(0,0,0,0.25), 0 10px 20px rgba(0,0,0,0.1);
  display: flex; flex-direction: column; flex-shrink: 0; position: relative;
}

.phone-status-bar {
  padding: 12px 28px 6px 28px;
  display: flex; justify-content: space-between; align-items: center;
  font-size: 14px; font-weight: 600; color: var(--text-primary);
  letter-spacing: 0.3px; flex-shrink: 0;
}
.phone-status-bar .time { font-weight: 700; }
.phone-status-bar .status-icons { display: flex; gap: 6px; align-items: center; font-size: 14px; color: var(--text-primary); }

.phone-nav-header {
  padding: 6px 20px 12px 20px;
  display: flex; justify-content: space-between; align-items: center;
  flex-shrink: 0; border-bottom: 1px solid rgba(0,0,0,0.04);
}
.phone-nav-header .nav-left { display: flex; align-items: center; gap: 8px; }
.phone-nav-header .nav-back { font-size: 20px; color: var(--text-primary); cursor: pointer; text-decoration: none; display: flex; align-items: center; }
.phone-nav-header .nav-back:active { opacity: 0.5; }
.phone-nav-header .nav-title { font-size: 22px; font-weight: 700; color: var(--text-primary); letter-spacing: -0.5px; margin: 0; }
.phone-nav-header .nav-actions { display: flex; gap: 18px; color: var(--text-secondary); font-size: 20px; align-items: center; }
.phone-nav-header .nav-actions i, .phone-nav-header .nav-actions a { color: var(--text-secondary); cursor: pointer; text-decoration: none; }
.phone-nav-header .nav-actions i:active, .phone-nav-header .nav-actions a:active { transform: scale(0.9); opacity: 0.6; }

.phone-content { flex: 1; overflow-y: auto; padding: 12px 16px 8px 16px; scroll-behavior: smooth; }
.phone-content::-webkit-scrollbar { width: 0; background: transparent; }

.phone-tabbar {
  border-top: 1px solid rgba(0,0,0,0.05);
  display: flex; justify-content: space-around;
  padding: 8px 0 10px 0; flex-shrink: 0; background: transparent;
}
.phone-tabbar .tab-item {
  display: flex; flex-direction: column; align-items: center; gap: 2px;
  font-size: 10px; font-weight: 500; color: #8e8e93;
  cursor: pointer; text-decoration: none; padding: 4px 12px;
  border-radius: 8px; position: relative; min-width: 52px;
  background: transparent; border: none; font-family: inherit;
}
.phone-tabbar .tab-item i { font-size: 22px; }
.phone-tabbar .tab-item.active { color: var(--primary); }
.phone-tabbar .tab-item.active i { font-weight: 900; }
.phone-tabbar .tab-item:active { transform: scale(0.92); opacity: 0.7; }
.phone-tabbar .badge-dot {
  position: absolute; top: 2px; right: 0;
  background: var(--danger); color: #fff; font-size: 10px; font-weight: 700;
  min-width: 18px; height: 18px; border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  padding: 0 5px; border: 2px solid var(--bg-body);
}

/* Responsive */
@media (max-width: 420px) {
  body.phone-frame-body { padding: 0; background: var(--bg-body); }
  .phone-frame { width: 100%; height: 100vh; border-radius: 0; box-shadow: none; }
  .phone-status-bar, .phone-nav-header { padding-left: 20px; padding-right: 20px; }
}
@media (max-height: 880px) and (min-width: 421px) {
  .phone-frame { height: 96vh; width: auto; aspect-ratio: 390/844; max-height: 96vh; }
}

/* Section header */
.section-header { font-size: 13px; font-weight: 600; color: #8e8e93; letter-spacing: 0.3px; padding: 8px 0 6px 0; }

/* Task card */
.task-card {
  background: #ffffff; border-radius: 10px; padding: 14px 16px;
  margin-bottom: 2px; cursor: pointer; border: none; border-left: none;
  text-decoration: none; display: block; color: inherit;
}
.task-card:active { background: #eef0f4; }
.task-card .task-title { font-size: 16px; font-weight: 600; color: #1a1a1e; flex: 1; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.task-card .task-table { font-size: 14px; color: #6c6c70; }
.task-card .task-meta { margin-top: 6px; font-size: 12px; color: #8e8e93; }

/* Content card */
.content-card { background: #ffffff; border-radius: 10px; padding: 14px 16px; margin-bottom: 8px; border: none; }
.content-card .card-title { font-size: 15px; font-weight: 600; color: #1a1a1e; padding-bottom: 10px; border-bottom: 1px solid rgba(0,0,0,0.06); margin-bottom: 10px; }

/* Detail row */
.detail-row { display: flex; padding: 10px 0; border-bottom: 1px solid rgba(0,0,0,0.04); font-size: 14px; }
.detail-row:last-child { border-bottom: none; }
.detail-label { width: 72px; flex-shrink: 0; color: #8e8e93; font-weight: 400; font-size: 13px; }
.detail-value { flex: 1; color: #1a1a1e; }

/* Stat grid */
.stat-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.stat-grid .stat-card { background: #ffffff; border-radius: 10px; padding: 14px; text-align: center; border: none; }
.stat-grid .stat-card .stat-num { font-size: 22px; font-weight: 700; color: #1a1a1e; }
.stat-grid .stat-card .stat-label { font-size: 12px; color: #8e8e93; margin-top: 4px; }
.stat-grid .stat-card.warning .stat-num { color: var(--warning); }
.stat-grid .stat-card.success .stat-num { color: var(--success); }
.stat-grid .stat-card.danger .stat-num { color: var(--danger); }

/* Quick actions */
.quick-actions { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; }
.quick-action-item { display: flex; flex-direction: column; align-items: center; gap: 6px; padding: 14px 6px; background: #ffffff; border-radius: 10px; border: none; cursor: pointer; font-size: 12px; font-weight: 500; color: #1a1a1e; }
.quick-action-item:active { transform: scale(0.95); background: #eef0f4; }
.quick-action-item i { font-size: 1.4rem; color: var(--primary); }

/* User card */
.user-card { display: flex; align-items: center; gap: 12px; background: #ffffff; border-radius: 12px; padding: 14px 16px; border: none; }
.user-card .avatar { width: 44px; height: 44px; border-radius: 12px; background: var(--primary); color: #fff; display: flex; align-items: center; justify-content: center; font-size: 18px; font-weight: 600; flex-shrink: 0; }
.user-card .user-name { font-size: 16px; font-weight: 600; color: #1a1a1e; }
.user-card .user-unit { font-size: 13px; color: #8e8e93; }
.user-card .role-badge { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 500; background: var(--primary-bg); color: var(--primary); }

/* Filter tabs */
.filter-tabs { display: flex; gap: 8px; overflow-x: auto; padding: 4px 0 8px; scrollbar-width: none; }
.filter-tabs::-webkit-scrollbar { display: none; }
.filter-tabs .filter-tab { flex-shrink: 0; padding: 6px 14px; border-radius: 20px; border: 1px solid #d0d0d5; background: #ffffff; font-size: 13px; font-weight: 500; color: #6c6c70; cursor: pointer; white-space: nowrap; }
.filter-tabs .filter-tab.active { background: var(--primary); color: #fff; border-color: var(--primary); font-weight: 600; }

/* Menu list */
.menu-list { background: #ffffff; border-radius: 10px; overflow: hidden; border: none; }
.menu-item { display: flex; align-items: center; justify-content: space-between; padding: 14px 16px; border-bottom: 1px solid rgba(0,0,0,0.04); cursor: pointer; font-size: 15px; color: #1a1a1e; text-decoration: none; }
.menu-item:last-child { border-bottom: none; }
.menu-item:active { background: #eef0f4; }
.menu-item i { color: #8e8e93; }
.menu-item i.bi-chevron-right { font-size: 14px; color: #c7c7cc; }

/* Picker */
.picker-overlay { position: fixed; inset: 0; z-index: 2000; background: rgba(0,0,0,0.4); display: flex; align-items: flex-end; justify-content: center; animation: pickerFadeIn 0.2s ease; }
.picker-sheet { background: #ffffff; border-radius: 16px 16px 0 0; width: 100%; max-width: 390px; max-height: 60vh; display: flex; flex-direction: column; animation: pickerSlideUp 0.2s ease; }
.picker-handle { width: 36px; height: 4px; background: #d0d0d5; border-radius: 2px; margin: 8px auto; }
.picker-header { display: flex; align-items: center; justify-content: space-between; padding: 8px 16px; border-bottom: 1px solid rgba(0,0,0,0.04); }
.picker-list { flex: 1; overflow-y: auto; padding: 0; }
.picker-footer { display: flex; gap: 8px; padding: 12px 16px; border-top: 1px solid rgba(0,0,0,0.04); padding-bottom: 24px; }
.picker-list .picker-item { padding: 14px 16px; border-bottom: 1px solid rgba(0,0,0,0.04); cursor: pointer; font-size: 15px; color: #1a1a1e; }
.picker-list .picker-item.selected { color: var(--primary); background: var(--primary-bg); font-weight: 500; }
@keyframes pickerFadeIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes pickerSlideUp { from { transform: translateY(100%); } to { transform: translateY(0); } }

/* Form controls */
.phone-content .form-control, .phone-content .form-select { font-size: 15px; padding: 10px 14px; border-radius: 8px; border-color: #d0d0d5; background: #ffffff; }
.phone-content .form-control:focus, .phone-content .form-select:focus { border-color: var(--primary); box-shadow: 0 0 0 3px rgba(51,112,255,0.12); }
.phone-content .btn { font-weight: 500; font-size: 15px; padding: 10px 20px; border-radius: 8px; }
.phone-content .btn-sm { font-size: 13px; padding: 6px 14px; }
.phone-content .btn-primary { background: var(--primary); border-color: var(--primary); }
.phone-content .btn-outline-primary { color: var(--primary); border-color: var(--primary); }
.phone-content .badge { font-weight: 500; font-size: 11px; padding: 3px 8px; }

/* Toast */
.app-toast { position: fixed; top: 12px; left: 50%; transform: translateX(-50%); z-index: 9999; max-width: 90%; font-size: 14px; padding: 10px 20px; border-radius: 8px; box-shadow: 0 8px 24px rgba(0,0,0,0.16); animation: toastSlideIn 0.25s ease; }
@keyframes toastSlideIn { from { opacity: 0; transform: translateX(-50%) translateY(-12px); } to { opacity: 1; transform: translateX(-50%) translateY(0); } }

/* Dark Mode */
[data-theme="dark"] body.phone-frame-body { background: #111; }
[data-theme="dark"] .phone-frame { background: #1a1a1a; }
[data-theme="dark"] .phone-status-bar { color: #e5e5e5; }
[data-theme="dark"] .phone-nav-header { border-bottom-color: rgba(255,255,255,0.06); }
[data-theme="dark"] .phone-nav-header .nav-title { color: #e5e5e5; }
[data-theme="dark"] .phone-nav-header .nav-back, [data-theme="dark"] .phone-nav-header .nav-actions i { color: #999; }
[data-theme="dark"] .task-card { background: #262626; }
[data-theme="dark"] .task-card:active { background: #333; }
[data-theme="dark"] .task-card .task-title { color: #e5e5e5; }
[data-theme="dark"] .task-card .task-table { color: #999; }
[data-theme="dark"] .task-card .task-meta { color: #707070; }
[data-theme="dark"] .content-card { background: #262626; }
[data-theme="dark"] .content-card .card-title { color: #e5e5e5; border-bottom-color: rgba(255,255,255,0.06); }
[data-theme="dark"] .detail-row { border-bottom-color: rgba(255,255,255,0.04); }
[data-theme="dark"] .detail-label { color: #707070; }
[data-theme="dark"] .detail-value { color: #e5e5e5; }
[data-theme="dark"] .stat-grid .stat-card { background: #262626; }
[data-theme="dark"] .stat-grid .stat-card .stat-num { color: #e5e5e5; }
[data-theme="dark"] .stat-grid .stat-card .stat-label { color: #707070; }
[data-theme="dark"] .quick-action-item { background: #262626; color: #e5e5e5; }
[data-theme="dark"] .quick-action-item:active { background: #333; }
[data-theme="dark"] .user-card { background: #262626; }
[data-theme="dark"] .user-card .user-name { color: #e5e5e5; }
[data-theme="dark"] .menu-list { background: #262626; }
[data-theme="dark"] .menu-item { color: #e5e5e5; border-bottom-color: rgba(255,255,255,0.04); }
[data-theme="dark"] .menu-item:active { background: #333; }
[data-theme="dark"] .filter-tabs .filter-tab { background: #262626; border-color: #3d3d3d; color: #999; }
[data-theme="dark"] .picker-sheet { background: #262626; }
[data-theme="dark"] .picker-list .picker-item { color: #e5e5e5; border-bottom-color: rgba(255,255,255,0.04); }
[data-theme="dark"] .picker-header, [data-theme="dark"] .picker-footer { border-color: rgba(255,255,255,0.04); }
[data-theme="dark"] .phone-content .form-control, [data-theme="dark"] .phone-content .form-select { background: #333; border-color: #3d3d3d; color: #e5e5e5; }
[data-theme="dark"] .section-header { color: #707070; }
[data-theme="dark"] .phone-tabbar { border-top-color: rgba(255,255,255,0.06); }
[data-theme="dark"] .phone-tabbar .badge-dot { border-color: #1a1a1a; }
```
