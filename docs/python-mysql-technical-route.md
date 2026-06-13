# MT5 CRM Python + MySQL 技术路线

本文档确定 MT5 CRM 管理系统的首版技术路线。目标是在未拿到 MT5 官方 Manager API 前，先完成 CRM、审核、报表、配置和权限系统；后续通过独立 MT5 Adapter 接入官方 API、第三方 REST API 或 CSV 导入。

## 1. 技术选型

### 1.1 前端

- Vue 3
- TypeScript
- Element Plus
- Pinia
- Vue Router
- ECharts
- Axios

选择原因：

- 适合后台管理系统。
- Element Plus 表格、表单、弹窗、分页、日期范围、下拉筛选能力成熟。
- 与参考系统交互模式接近，开发成本低。

### 1.2 后端

- Python 3.13
- FastAPI
- Pydantic v2
- SQLAlchemy 2.x
- Alembic
- PyMySQL
- JWT 登录认证
- passlib/bcrypt 密码哈希

选择原因：

- FastAPI 开发效率高，适合快速搭建 CRM 和审核流 API。
- Pydantic 适合请求参数、响应数据和配置校验。
- SQLAlchemy 2.x 支持清晰的数据模型和 MySQL 8。
- 后续对接第三方 REST API、CSV/Excel 导入、报表导出较方便。

### 1.3 数据库

- MySQL 8
- 字符集：`utf8mb4`
- 排序规则：`utf8mb4_0900_ai_ci`
- 金额字段使用 `DECIMAL(20, 8)` 或按业务精度拆分。
- 时间字段统一存储 UTC 或明确时区字段，后台展示按配置时区转换。

### 1.4 缓存与异步任务

- Redis
- Celery 或 RQ

首版建议：

- API 主流程先同步实现。
- 邮件、短信、MT5 同步、报表聚合后续放入异步任务。

### 1.5 报表与导出

- openpyxl
- pandas
- 后台分页查询
- Excel 导出
- 后续可增加报表聚合表，避免实时扫描交易大表。

### 1.6 MT5 对接

主系统不直接耦合 MT5 SDK。统一通过 `Mt5Adapter` 抽象层接入。

首版 Adapter：

- `MockMt5Adapter`：本地开发和演示使用。
- `CsvImportAdapter`：通过 MT5 Manager 导出的报表导入。

后续 Adapter：

- `OfficialManagerApiAdapter`：官方 Manager API。
- `ThirdPartyRestAdapter`：第三方 MT5 REST API。
- `DotNetBridgeAdapter`：如果官方 API 只能通过 Windows DLL/C# 服务调用。

## 2. 后端架构

后端采用模块化单体结构：

```text
backend/
  app/
    main.py
    core/
      config.py
      database.py
      security.py
      errors.py
    modules/
      auth/
      admin/
      crm/
      mt5/
      tasks/
      finance/
      reports/
      records/
      settings/
    tests/
```

### 2.1 模块边界

- `auth`：登录、JWT、密码、当前用户。
- `admin`：后台账户、角色、权限。
- `crm`：CRM 用户、资料、上下级、黑名单。
- `mt5`：MT5 账户、服务器、组别、Adapter。
- `tasks`：认证审核、开户审核、入金审核、出金审核。
- `finance`：入金、出金、转账、支付通道。
- `reports`：财务报表、交易报表、佣金报表。
- `records`：邮件记录、短信记录、操作日志。
- `settings`：平台、安全、认证、通用、出入金、邮件、消息配置。

### 2.2 API 路径规划

```text
/api/v1/auth
/api/v1/admin
/api/v1/crm
/api/v1/mt5
/api/v1/tasks
/api/v1/finance
/api/v1/reports
/api/v1/records
/api/v1/settings
/api/v1/health
```

### 2.3 权限设计

采用 RBAC：

- 后台账户
- 角色
- 权限
- 角色权限
- 账户角色

权限分三类：

- 菜单权限
- 按钮权限
- 数据范围权限

数据范围建议：

- 仅自己
- 本部门/团队
- 指定代理树
- 全部

### 2.4 审计日志

所有敏感操作必须记录：

- 操作人
- 操作模块
- 请求路径
- 请求方法
- 请求参数摘要
- IP
- User-Agent
- 操作时间
- 操作结果

敏感参数如密码、Token、密钥、银行卡号需要脱敏。

## 3. 数据库设计原则

- 所有表使用 `id` 主键。
- 业务编号单独建字段，如 `order_no`、`ticket`、`mt5_login`。
- 所有表保留 `created_at`、`updated_at`。
- 审核类表保留 `status`、`reviewer_id`、`reviewed_at`、`review_remark`。
- 资金类表保留 `request_amount`、`actual_amount`、`fee_amount`、`currency`、`exchange_rate`。
- MT5 写操作必须保留 `idempotency_key`。
- 删除优先软删除，保留审计。

## 4. 首版开发范围

首版先完成：

- 项目骨架
- 配置管理
- MySQL 连接
- Alembic 迁移
- 健康检查
- 后台账户登录
- RBAC 权限
- CRM 用户
- MT5 账户基础表
- 审核任务
- 入出金流程
- 操作日志

首版暂不做：

- 真实 MT5 Manager API 联调
- 真实支付通道自动回调
- 复杂 BI 数据仓库
- 多租户品牌隔离

## 5. 部署路线

开发环境：

```text
FastAPI dev server
MySQL 8
Redis
Vue dev server
```

生产环境：

```text
Nginx
Frontend static files
FastAPI API service
Celery worker
Celery beat
MySQL 8
Redis
MT5 Adapter service
```

## 6. 质量要求

- 后端核心业务使用测试先行。
- 所有列表接口支持分页。
- 所有金额计算使用 Decimal。
- 所有写操作返回可追踪业务编号。
- 资金和 MT5 写操作必须幂等。
- 所有审核流程必须可追溯。
- 所有配置变更必须写操作日志。
