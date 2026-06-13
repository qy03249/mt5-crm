const API_BASE = "/api/v1";
const TOKEN_KEY = "mt5_crm_token";

const state = {
  token: localStorage.getItem(TOKEN_KEY),
  user: null,
  topMenu: "setting",
  sidePage: "account",
  accounts: [],
  roles: [],
  permissionTree: [],
};

const topMenus = [
  { key: "home", label: "首页" },
  { key: "task", label: "任务" },
  { key: "client", label: "客户" },
  { key: "report", label: "报表" },
  { key: "record", label: "记录" },
  { key: "setting", label: "设置" },
];

const settingMenus = [
  { group: "CRM设置", children: [] },
  { group: "MT5设置", children: [] },
  { group: "出入金设置", children: [] },
  { group: "返佣设置", children: [] },
  { group: "消息设置", children: [] },
  { group: "用户管理", children: [] },
  {
    group: "后台权限",
    children: [
      { key: "account", label: "后台账户" },
      { key: "role", label: "角色权限" },
    ],
  },
  { group: "下载中心", children: [] },
];

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
    throw new Error(data?.detail || "请求失败");
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
  const [user, accounts, roles, permissionTree] = await Promise.all([
    request("/auth/me"),
    request("/admin/accounts"),
    request("/admin/roles"),
    request("/admin/permissions/tree"),
  ]);
  state.user = user;
  state.accounts = accounts;
  state.roles = roles;
  state.permissionTree = permissionTree;
  render();
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
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
          <p>对齐参考系统的菜单和业务逻辑，先完成后台账户、角色权限和基础工作台，再逐步扩展客户、任务、报表和记录模块。</p>
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
        ${state.topMenu === "setting" ? renderSidebar() : ""}
        <main class="main">${renderMain()}</main>
      </section>
    </div>
  `;

  document.querySelectorAll("[data-top-menu]").forEach((button) => {
    button.addEventListener("click", () => {
      state.topMenu = button.dataset.topMenu;
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
}

function renderSidebar() {
  return `
    <aside class="sidebar">
      ${settingMenus
        .map(
          (group) => `
            <div class="side-group">
              <button class="side-parent" type="button">
                <span>${group.group}</span>
                <span>${group.children.length ? "⌃" : "⌄"}</span>
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
  if (state.topMenu !== "setting") {
    const menu = topMenus.find((item) => item.key === state.topMenu);
    return `<section class="empty-page">${menu.label}模块将在对应功能清单开发时接入</section>`;
  }

  if (state.sidePage === "role") {
    return renderRolePermissionPage();
  }
  return renderAccountPage();
}

function renderAccountPage() {
  return `
    <section class="page-title">后台账户</section>
    <section class="toolbar">
      <input class="search-input" placeholder="搜索账号/姓名/邮箱" />
      <button class="primary-button" type="button">＋ 新增账户</button>
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
          <button class="primary-button" type="button">＋ 新增角色</button>
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
