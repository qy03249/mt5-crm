const API_BASE = "/api/v1";
const TOKEN_KEY = "mt5_crm_token";

const state = {
  token: localStorage.getItem(TOKEN_KEY),
  user: null,
  topMenu: "setting",
  sidePage: "admin.account",
  accounts: [],
  roles: [],
  permissionTree: [],
  operationLogs: [],
  crmUsers: [],
  crmEditingUser: null,
  crmFilters: {
    keyword: "",
    mt5_login: "",
  },
};

const topMenus = [
  { key: "home", label: "首页" },
  { key: "task", label: "任务" },
  { key: "client", label: "客户" },
  { key: "report", label: "报表" },
  { key: "record", label: "记录" },
  { key: "setting", label: "设置" },
];

const enumLabels = {
  roleType: {
    customer: "普通客户",
    agent: "代理",
    ib: "IB",
  },
  certificationStatus: {
    pending: "待认证",
    approved: "认证通过",
    rejected: "认证拒绝",
  },
  userStatus: {
    active: "启用",
    disabled: "禁用",
    blacklisted: "黑名单",
  },
};

const navigation = {
  home: [
    {
      group: "工作台",
      children: [{ key: "home.dashboard", label: "首页概览" }],
    },
  ],
  task: [
    {
      group: "审核任务",
      children: [
        { key: "task.identity", label: "认证审核" },
        { key: "task.accountOpen", label: "开户审核" },
        { key: "task.deposit", label: "入金审核" },
        { key: "task.withdrawal", label: "出金审核" },
      ],
    },
  ],
  client: [
    {
      group: "客户管理",
      children: [
        { key: "client.crmUser", label: "CRM用户" },
        { key: "client.hierarchy", label: "CRM上下级" },
        { key: "client.mt5Account", label: "MT5账户" },
      ],
    },
  ],
  report: [
    {
      group: "财务报表",
      children: [
        { key: "report.deposit", label: "入金报表" },
        { key: "report.withdrawal", label: "出金报表" },
        { key: "report.transfer", label: "转账报表" },
        { key: "report.funds", label: "资金报表" },
        { key: "report.financeStatistics", label: "统计报表" },
      ],
    },
    {
      group: "交易报表",
      children: [
        { key: "report.tradeStatistics", label: "统计报表" },
        { key: "report.symbol", label: "品种报表" },
        { key: "report.profit", label: "盈亏/查询报表" },
        { key: "report.position", label: "持仓报表" },
        { key: "report.closed", label: "平仓报表" },
        { key: "report.pending", label: "挂单报表" },
      ],
    },
    {
      group: "佣金报表",
      children: [{ key: "report.commissionOrder", label: "订单返佣" }],
    },
  ],
  record: [
    {
      group: "消息记录",
      children: [
        { key: "record.email", label: "邮件记录" },
        { key: "record.notification", label: "短信/通知记录" },
      ],
    },
    {
      group: "审计记录",
      children: [{ key: "record.operationLog", label: "操作日志" }],
    },
  ],
  setting: [
    {
      group: "CRM设置",
      children: [
        { key: "setting.platform", label: "平台设置" },
        { key: "setting.security", label: "安全设置" },
        { key: "setting.authentication", label: "认证设置" },
        { key: "setting.general", label: "通用设置" },
      ],
    },
    {
      group: "MT5设置",
      children: [
        { key: "setting.mt5Base", label: "基础设置" },
        { key: "setting.mt5Server", label: "服务器设置" },
        { key: "setting.mt5Sync", label: "同步设置" },
      ],
    },
    {
      group: "出入金设置",
      children: [
        { key: "setting.fundsBase", label: "基础设置" },
        { key: "setting.onlineDeposit", label: "在线入金" },
        { key: "setting.wallet", label: "汇款/钱包配置" },
      ],
    },
    {
      group: "返佣设置",
      children: [{ key: "setting.commissionRule", label: "返佣规则" }],
    },
    {
      group: "消息设置",
      children: [
        { key: "setting.email", label: "邮件设置" },
        { key: "setting.message", label: "短信/通知设置" },
      ],
    },
    {
      group: "用户管理",
      children: [{ key: "setting.blacklist", label: "黑名单" }],
    },
    {
      group: "后台权限",
      children: [
        { key: "admin.account", label: "后台账户" },
        { key: "admin.role", label: "角色权限" },
      ],
    },
    {
      group: "下载中心",
      children: [{ key: "setting.download", label: "下载资源" }],
    },
  ],
};

const pageTitles = Object.values(navigation)
  .flat()
  .flatMap((group) => group.children)
  .reduce((result, item) => ({ ...result, [item.key]: item.label }), {});

async function request(path, options = {}) {
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };
  if (state.token) {
    headers.Authorization = `Bearer ${state.token}`;
  }

  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    logout(false);
    throw new Error("登录已失效，请重新登录");
  }

  const text = await response.text();
  const data = text ? JSON.parse(text) : null;
  if (!response.ok) {
    throw new Error(data?.message || data?.detail || "请求失败");
  }
  return data;
}

function setToken(token) {
  state.token = token;
  localStorage.setItem(TOKEN_KEY, token);
}

function logout(renderLogin = true) {
  state.token = null;
  state.user = null;
  localStorage.removeItem(TOKEN_KEY);
  if (renderLogin) render();
}

async function login(username, password) {
  const data = await request("/auth/login", {
    method: "POST",
    body: JSON.stringify({ username, password }),
  });
  setToken(data.access_token);
  await loadAppData();
}

async function loadAppData() {
  const [user, accounts, roles, permissionTree, operationLogs, crmUsers] = await Promise.all([
    request("/auth/me"),
    request("/admin/accounts"),
    request("/admin/roles"),
    request("/admin/permissions/tree"),
    request("/admin/operation-logs"),
    request("/crm/users"),
  ]);
  state.user = user;
  state.accounts = accounts;
  state.roles = roles;
  state.permissionTree = permissionTree;
  state.operationLogs = operationLogs;
  state.crmUsers = crmUsers;
  render();
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function enumLabel(group, value) {
  return enumLabels[group]?.[value] || value || "-";
}

function render() {
  if (!state.token || !state.user) {
    renderLogin();
    return;
  }
  renderApp();
}

function renderLogin() {
  document.querySelector("#app").innerHTML = `
    <main class="login-shell">
      <section class="login-panel">
        <div class="brand-mark">MT5 CRM</div>
        <h1 class="login-title">后台登录</h1>
        <p class="login-subtitle">进入客户管理、权限配置和运营任务工作台</p>
        <form id="loginForm">
          <div class="field">
            <label for="username">账号</label>
            <input id="username" name="username" autocomplete="username" value="admin" />
          </div>
          <div class="field">
            <label for="password">密码</label>
            <input id="password" name="password" type="password" autocomplete="current-password" value="Admin@123456" />
          </div>
          <button class="primary-button login-button" type="submit">登录</button>
          <div class="error" id="loginError"></div>
        </form>
      </section>
      <section class="login-visual">
        <div class="login-copy">
          <h1>MT5 CRM 客户管理系统</h1>
          <p>对齐参考系统的菜单和业务逻辑，先完成后台基础框架，再逐步接入客户、任务、报表、记录和设置模块。</p>
        </div>
      </section>
    </main>
  `;

  document.querySelector("#loginForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const error = document.querySelector("#loginError");
    error.textContent = "";
    try {
      await login(form.get("username"), form.get("password"));
    } catch (err) {
      error.textContent = err.message;
    }
  });
}

function renderApp() {
  document.querySelector("#app").innerHTML = `
    <div class="app-shell">
      <header class="topbar">
        <div class="topbar-logo">MT5 CRM</div>
        <nav class="top-nav">
          ${topMenus
            .map(
              (item) => `
                <button class="${state.topMenu === item.key ? "active" : ""}" data-top-menu="${item.key}">
                  ${item.label}
                </button>
              `,
            )
            .join("")}
        </nav>
        <div class="top-actions">
          <span>${escapeHtml(state.user.display_name)}</span>
          <button class="ghost-button" id="logoutButton">退出</button>
        </div>
      </header>
      <section class="workspace">
        ${renderSidebar()}
        <main class="main">${renderMain()}</main>
      </section>
    </div>
  `;

  document.querySelectorAll("[data-top-menu]").forEach((button) => {
    button.addEventListener("click", () => {
      state.topMenu = button.dataset.topMenu;
      state.sidePage = navigation[state.topMenu][0].children[0].key;
      renderApp();
    });
  });

  document.querySelectorAll("[data-side-page]").forEach((button) => {
    button.addEventListener("click", () => {
      state.sidePage = button.dataset.sidePage;
      renderApp();
    });
  });

  document.querySelector("#logoutButton")?.addEventListener("click", () => logout());
  bindCrmUserActions();
}

function renderSidebar() {
  return `
    <aside class="sidebar">
      ${navigation[state.topMenu]
        .map(
          (group) => `
            <div class="side-group">
              <button class="side-parent" type="button">
                <span>${group.group}</span>
                <span>${group.children.length ? "^" : "v"}</span>
              </button>
              ${group.children
                .map(
                  (child) => `
                    <button class="side-link ${state.sidePage === child.key ? "active" : ""}" data-side-page="${child.key}" type="button">
                      ${child.label}
                    </button>
                  `,
                )
                .join("")}
            </div>
          `,
        )
        .join("")}
    </aside>
  `;
}

function renderMain() {
  if (state.sidePage === "admin.role") {
    return renderRolePermissionPage();
  }
  if (state.sidePage === "admin.account") {
    return renderAccountPage();
  }
  if (state.sidePage === "record.operationLog") {
    return renderOperationLogPage();
  }
  if (state.sidePage === "client.crmUser") {
    return renderCrmUserPage();
  }
  return renderPlaceholderPage();
}

function renderPlaceholderPage() {
  const topMenu = topMenus.find((item) => item.key === state.topMenu);
  const pageTitle = pageTitles[state.sidePage] || topMenu.label;
  return `
    <section class="page-title">${pageTitle}</section>
    <section class="panel placeholder-panel">
      <div class="placeholder-title">${topMenu.label} / ${pageTitle}</div>
      <div class="placeholder-text">菜单已按参考系统写入，当前页面将在对应开发任务中接入筛选、表格、表单和业务操作。</div>
    </section>
  `;
}

function renderAccountPage() {
  return `
    <section class="page-title">后台账户</section>
    <section class="toolbar">
      <input class="search-input" placeholder="搜索账号/姓名/邮箱" />
      <button class="primary-button" type="button">+ 新增账户</button>
      <button class="ghost-button" type="button">刷新</button>
    </section>
    <section class="panel">
      <table class="table">
        <thead>
          <tr>
            <th>ID</th>
            <th>账号</th>
            <th>姓名</th>
            <th>邮箱</th>
            <th>角色</th>
            <th>状态</th>
          </tr>
        </thead>
        <tbody>
          ${state.accounts
            .map(
              (account) => `
                <tr>
                  <td>${account.id}</td>
                  <td>${escapeHtml(account.username)}</td>
                  <td>${escapeHtml(account.display_name)}</td>
                  <td>${escapeHtml(account.email || "-")}</td>
                  <td>${account.roles.map((role) => `<span class="tag">${escapeHtml(role.name)}</span>`).join(" ")}</td>
                  <td><span class="tag success">${account.status === "active" ? "启用" : "停用"}</span></td>
                </tr>
              `,
            )
            .join("")}
        </tbody>
      </table>
    </section>
  `;
}

function renderRolePermissionPage() {
  return `
    <section class="page-title">角色权限</section>
    <div class="content-grid">
      <section class="panel">
        <div class="panel-header">
          <span>角色列表</span>
          <button class="primary-button" type="button">+ 新增角色</button>
        </div>
        <table class="table">
          <thead>
            <tr>
              <th>角色编码</th>
              <th>角色名称</th>
              <th>权限数</th>
            </tr>
          </thead>
          <tbody>
            ${state.roles
              .map(
                (role) => `
                  <tr>
                    <td>${escapeHtml(role.code)}</td>
                    <td>${escapeHtml(role.name)}</td>
                    <td>${role.permission_count}</td>
                  </tr>
                `,
              )
              .join("")}
          </tbody>
        </table>
      </section>
      <section class="panel">
        <div class="panel-header">
          <span>权限树</span>
          <button class="ghost-button" type="button">保存权限</button>
        </div>
        ${renderPermissionTree(state.permissionTree)}
      </section>
    </div>
  `;
}

function renderOperationLogPage() {
  return `
    <section class="page-title">操作日志</section>
    <section class="toolbar">
      <input class="search-input" placeholder="操作员/路径/IP" />
      <select class="filter-select">
        <option>全部结果</option>
        <option>success</option>
        <option>failure</option>
      </select>
      <button class="ghost-button" type="button" id="refreshLogsButton">刷新</button>
    </section>
    <section class="panel table-panel">
      <table class="table">
        <thead>
          <tr>
            <th>ID</th>
            <th>操作员</th>
            <th>方法</th>
            <th>路径</th>
            <th>IP地址</th>
            <th>结果</th>
            <th>操作时间</th>
          </tr>
        </thead>
        <tbody>
          ${state.operationLogs
            .map(
              (log) => `
                <tr>
                  <td>${log.id}</td>
                  <td>${escapeHtml(log.operator_name)}</td>
                  <td><span class="tag">${escapeHtml(log.method)}</span></td>
                  <td>${escapeHtml(log.path)}</td>
                  <td>${escapeHtml(log.ip_address)}</td>
                  <td><span class="tag ${log.result === "success" ? "success" : "danger"}">${escapeHtml(log.result)}</span></td>
                  <td>${formatDateTime(log.operated_at)}</td>
                </tr>
              `,
            )
            .join("")}
        </tbody>
      </table>
    </section>
  `;
}

function renderCrmUserPage() {
  return `
    <section class="page-title">CRM用户</section>
    <section class="toolbar">
      <input class="search-input" id="crmKeywordInput" placeholder="姓名/手机/邮箱" value="${escapeHtml(state.crmFilters.keyword)}" />
      <input class="search-input compact-input" id="crmMt5LoginInput" placeholder="交易账号" value="${escapeHtml(state.crmFilters.mt5_login)}" />
      <button class="ghost-button" type="button" id="crmSearchButton">查询</button>
      <button class="ghost-button" type="button" id="crmResetButton">重置</button>
      <button class="ghost-button" type="button" id="crmExportButton">导出</button>
      <button class="primary-button" type="button" id="openCrmCreateButton">+ 新增用户</button>
    </section>
    <section class="panel table-panel">
      <table class="table">
        <thead>
          <tr>
            <th>编号</th>
            <th>备注</th>
            <th>MT5账号</th>
            <th>创建时间</th>
            <th>姓名</th>
            <th>上级</th>
            <th>上级MT5账号</th>
            <th>手机</th>
            <th>邮箱</th>
            <th>状态</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          ${state.crmUsers
            .map(
              (user) => `
                <tr>
                  <td>${user.id}</td>
                  <td>${escapeHtml(user.remark || "-")}</td>
                  <td>${escapeHtml(user.mt5_login || "-")}</td>
                  <td>${formatDateTime(user.created_at)}</td>
                  <td>${escapeHtml(user.name || user.nickname || "-")}</td>
                  <td>${escapeHtml(user.parent_name || "-")}</td>
                  <td>${escapeHtml(user.parent_mt5_login || "-")}</td>
                  <td>${escapeHtml(user.phone || "-")}</td>
                  <td>${escapeHtml(user.email || "-")}</td>
                  <td><span class="tag success">${escapeHtml(enumLabel("userStatus", user.status))}</span></td>
                  <td>
                    <button class="table-action" type="button" data-crm-edit="${user.id}">编辑</button>
                    <button class="table-action" type="button" data-crm-status="${user.id}" data-next-status="${user.status === "active" ? "disabled" : "active"}">
                      ${user.status === "active" ? "禁用" : "启用"}
                    </button>
                  </td>
                </tr>
              `,
            )
            .join("")}
        </tbody>
      </table>
    </section>
    ${state.crmEditingUser ? renderCrmUserModal() : ""}
  `;
}

function renderCrmUserModal() {
  const user = state.crmEditingUser;
  const isCreate = !user.id;
  return `
    <div class="modal-backdrop">
      <section class="modal">
        <div class="modal-header">
          <h2>${isCreate ? "新增用户" : "编辑用户"}</h2>
          <button class="icon-button" type="button" id="closeCrmModalButton">×</button>
        </div>
        <form id="crmUserForm" class="form-grid">
          <input type="hidden" name="id" value="${escapeHtml(user.id || "")}" />
          <div class="field">
            <label>用户名</label>
            <input name="username" value="${escapeHtml(user.username || "")}" />
          </div>
          <div class="field">
            <label>姓名</label>
            <input name="name" value="${escapeHtml(user.name || "")}" />
          </div>
          <div class="field">
            <label>昵称</label>
            <input name="nickname" value="${escapeHtml(user.nickname || "")}" />
          </div>
          <div class="field">
            <label>手机</label>
            <input name="phone" value="${escapeHtml(user.phone || "")}" />
          </div>
          <div class="field">
            <label>邮箱</label>
            <input name="email" value="${escapeHtml(user.email || "")}" />
          </div>
          <div class="field">
            <label>MT5账号</label>
            <input name="mt5_login" value="${escapeHtml(user.mt5_login || "")}" />
          </div>
          <div class="field">
            <label>上级MT5账号</label>
            <input name="parent_mt5_login" value="${escapeHtml(user.parent_mt5_login || "")}" />
          </div>
          <div class="field">
            <label>上级用户</label>
            <select name="parent_id">
              <option value="">无</option>
              ${state.crmUsers
                .filter((item) => item.id !== user.id)
                .map(
                  (item) => `
                    <option value="${item.id}" ${user.parent_id === item.id ? "selected" : ""}>
                      ${escapeHtml(item.name || item.username || item.email || item.id)}
                    </option>
                  `,
                )
                .join("")}
            </select>
          </div>
          <div class="field">
            <label>上级代码</label>
            <input name="parent_code" value="${escapeHtml(user.parent_code || "")}" />
          </div>
          <div class="field">
            <label>角色</label>
            <select name="role_type">
              ${Object.entries(enumLabels.roleType)
                .map(
                  ([value, label]) => `<option value="${value}" ${user.role_type === value ? "selected" : ""}>${label}</option>`,
                )
                .join("")}
            </select>
          </div>
          <div class="field">
            <label>认证状态</label>
            <select name="certification_status">
              ${Object.entries(enumLabels.certificationStatus)
                .map(
                  ([value, label]) => `<option value="${value}" ${user.certification_status === value ? "selected" : ""}>${label}</option>`,
                )
                .join("")}
            </select>
          </div>
          <div class="field">
            <label>状态</label>
            <select name="status">
              ${Object.entries(enumLabels.userStatus)
                .map(
                  ([value, label]) => `<option value="${value}" ${user.status === value ? "selected" : ""}>${label}</option>`,
                )
                .join("")}
            </select>
          </div>
          <div class="field form-full">
            <label>备注</label>
            <input name="remark" value="${escapeHtml(user.remark || "")}" />
          </div>
          <div class="modal-actions">
            <button class="ghost-button" type="button" id="cancelCrmModalButton">取消</button>
            <button class="primary-button" type="submit">保存</button>
          </div>
        </form>
      </section>
    </div>
  `;
}

function bindCrmUserActions() {
  document.querySelector("#openCrmCreateButton")?.addEventListener("click", () => {
    state.crmEditingUser = {
      username: "",
      name: "",
      nickname: "",
      phone: "",
      email: "",
      mt5_login: "",
      parent_mt5_login: "",
      parent_id: null,
      parent_code: "",
      role_type: "customer",
      certification_status: "pending",
      status: "active",
      remark: "",
    };
    renderApp();
  });

  document.querySelectorAll("[data-crm-edit]").forEach((button) => {
    button.addEventListener("click", async () => {
      const user = await request(`/crm/users/${button.dataset.crmEdit}`);
      state.crmEditingUser = user;
      renderApp();
    });
  });

  document.querySelectorAll("[data-crm-status]").forEach((button) => {
    button.addEventListener("click", async () => {
      await request(`/crm/users/${button.dataset.crmStatus}/status`, {
        method: "PATCH",
        body: JSON.stringify({ status: button.dataset.nextStatus }),
      });
      await refreshCrmUsers();
    });
  });

  document.querySelector("#closeCrmModalButton")?.addEventListener("click", closeCrmModal);
  document.querySelector("#cancelCrmModalButton")?.addEventListener("click", closeCrmModal);
  document.querySelector("#crmUserForm")?.addEventListener("submit", submitCrmUserForm);
  document.querySelector("#crmSearchButton")?.addEventListener("click", searchCrmUsers);
  document.querySelector("#crmResetButton")?.addEventListener("click", resetCrmFilters);
  document.querySelector("#crmExportButton")?.addEventListener("click", exportCrmUsers);
}

function closeCrmModal() {
  state.crmEditingUser = null;
  renderApp();
}

async function submitCrmUserForm(event) {
  event.preventDefault();
  const form = new FormData(event.currentTarget);
  const id = form.get("id");
  const payload = {
    username: emptyToNull(form.get("username")),
    name: emptyToNull(form.get("name")),
    nickname: emptyToNull(form.get("nickname")),
    phone: emptyToNull(form.get("phone")),
    email: emptyToNull(form.get("email")),
    mt5_login: emptyToNull(form.get("mt5_login")),
    parent_mt5_login: emptyToNull(form.get("parent_mt5_login")),
    parent_id: form.get("parent_id") ? Number(form.get("parent_id")) : null,
    parent_code: emptyToNull(form.get("parent_code")),
    role_type: form.get("role_type"),
    certification_status: form.get("certification_status"),
    status: form.get("status"),
    remark: emptyToNull(form.get("remark")),
  };
  await request(id ? `/crm/users/${id}` : "/crm/users", {
    method: id ? "PUT" : "POST",
    body: JSON.stringify(payload),
  });
  state.crmEditingUser = null;
  await refreshCrmUsers();
}

async function refreshCrmUsers() {
  const params = new URLSearchParams();
  if (state.crmFilters.keyword) params.set("keyword", state.crmFilters.keyword);
  if (state.crmFilters.mt5_login) params.set("mt5_login", state.crmFilters.mt5_login);
  const query = params.toString();
  state.crmUsers = await request(`/crm/users${query ? `?${query}` : ""}`);
  renderApp();
}

async function searchCrmUsers() {
  state.crmFilters.keyword = document.querySelector("#crmKeywordInput")?.value.trim() || "";
  state.crmFilters.mt5_login = document.querySelector("#crmMt5LoginInput")?.value.trim() || "";
  await refreshCrmUsers();
}

async function resetCrmFilters() {
  state.crmFilters = { keyword: "", mt5_login: "" };
  await refreshCrmUsers();
}

function exportCrmUsers() {
  const headers = [
    "编号",
    "备注",
    "MT5账号",
    "创建时间",
    "姓名",
    "上级",
    "上级MT5账号",
    "手机",
    "邮箱",
    "状态",
  ];
  const rows = state.crmUsers.map((user) => [
    user.id,
    user.remark || "",
    user.mt5_login || "",
    formatDateTime(user.created_at),
    user.name || user.nickname || "",
    user.parent_name || "",
    user.parent_mt5_login || "",
    user.phone || "",
    user.email || "",
    enumLabel("userStatus", user.status),
  ]);
  downloadCsv("crm-users.csv", [headers, ...rows]);
}

function downloadCsv(filename, rows) {
  const csv = rows
    .map((row) => row.map((value) => `"${String(value).replaceAll('"', '""')}"`).join(","))
    .join("\n");
  const blob = new Blob([`\ufeff${csv}`], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

function emptyToNull(value) {
  const text = String(value || "").trim();
  return text ? text : null;
}

function formatDateTime(value) {
  if (!value) return "-";
  return String(value).replace("T", " ").slice(0, 19);
}

function renderPermissionTree(nodes) {
  return `
    <ul class="permission-tree">
      ${nodes
        .map(
          (node) => `
            <li>
              <label class="tree-node">
                <input type="checkbox" checked />
                <span>${escapeHtml(node.name)}</span>
                <span class="node-type">${node.type}</span>
              </label>
              ${node.children?.length ? renderPermissionTree(node.children) : ""}
            </li>
          `,
        )
        .join("")}
    </ul>
  `;
}

if (state.token) {
  loadAppData().catch(() => {
    logout(false);
    renderLogin();
  });
} else {
  renderLogin();
}
