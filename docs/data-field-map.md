# MT5 CRM 字段映射与数据字典

本文档用于开发时查询“每个页面需要哪些字段”。开发任务清单只负责开发顺序；本文件负责字段级范围。后续写模型、迁移、接口、前端表格时，优先参考本文档，再参考 `docs/mt5-crm-feature-inventory.md`。

## 1. 通用字段规范

所有核心业务表建议包含：

| 字段 | 类型建议 | 说明 |
|---|---|---|
| id | BIGINT | 主键 |
| created_at | DATETIME(6) | 创建时间 |
| updated_at | DATETIME(6) | 更新时间 |
| deleted_at | DATETIME(6), NULL | 软删除时间 |
| status | VARCHAR(32) | 状态 |
| remark | VARCHAR(1000), NULL | 备注 |

金额字段：

| 字段 | 类型建议 | 说明 |
|---|---|---|
| amount | DECIMAL(20, 8) | 通用金额 |
| request_amount | DECIMAL(20, 8) | 申请金额 |
| actual_amount | DECIMAL(20, 8) | 实际到账/扣款金额 |
| fee_amount | DECIMAL(20, 8) | 手续费 |
| exchange_rate | DECIMAL(20, 8) | 汇率 |
| currency | VARCHAR(16) | 币种 |

审核字段：

| 字段 | 类型建议 | 说明 |
|---|---|---|
| review_status | VARCHAR(32) | pending/approved/rejected |
| reviewer_id | BIGINT, NULL | 审核人 |
| reviewed_at | DATETIME(6), NULL | 审核时间 |
| review_remark | VARCHAR(1000), NULL | 审核备注 |

MT5 常用字段：

| 字段 | 类型建议 | 说明 |
|---|---|---|
| mt5_login | BIGINT | MT5 登录账号 |
| mt5_group | VARCHAR(128) | MT5 组别 |
| leverage | INT | 杠杆 |
| balance | DECIMAL(20, 8) | 余额 |
| equity | DECIMAL(20, 8) | 净值 |
| credit | DECIMAL(20, 8) | 信用 |

## 2. 首页字段

### 2.1 待办统计接口

建议接口：`GET /api/v1/dashboard/todos`

返回字段：

| 字段 | 说明 |
|---|---|
| certification_pending_count | 认证审核待办数 |
| account_open_pending_count | 开户审核待办数 |
| deposit_pending_count | 入金审核待办数 |
| withdrawal_pending_count | 出金审核待办数 |

### 2.2 平台总览接口

建议接口：`GET /api/v1/dashboard/platform-summary`

返回字段：

| 字段 | 说明 |
|---|---|
| today_deposit_amount | 今日入金 |
| today_withdrawal_amount | 今日出金 |
| today_commission_amount | 今日返佣 |
| total_commission_amount | 返佣合计 |
| total_deposit_amount | 入金合计 |
| total_withdrawal_amount | 出金合计 |
| crm_user_count | 用户总数 |
| today_new_user_count | 今日新增用户 |

### 2.3 交易总览接口

建议接口：`GET /api/v1/dashboard/trade-summary`

返回字段：

| 字段 | 说明 |
|---|---|
| total_interest | 总利息 |
| total_trade_profit | 总交易盈亏 |
| mt5_account_count | 账号总数 |
| total_floating_profit | 总浮动盈亏 |
| closed_volume | 平仓总交易量 |
| position_volume | 持仓总交易量 |
| total_commission_fee | 总手续费 |

## 3. 认证与权限

### 3.1 admin_users

页面：设置 / 角色权限 / 后台账户

| 字段 | 类型建议 | 页面含义 |
|---|---|---|
| id | BIGINT | 主键 |
| username | VARCHAR(64) | 账号 |
| password_hash | VARCHAR(255) | 密码哈希 |
| display_name | VARCHAR(64) | 角色/账户显示名 |
| email | VARCHAR(255) | 电子邮箱 |
| status | VARCHAR(32) | 启用/停用 |
| last_login_at | DATETIME(6), NULL | 最后登录时间 |

### 3.2 roles

页面：设置 / 角色权限 / 角色权限

| 字段 | 类型建议 | 页面含义 |
|---|---|---|
| id | BIGINT | 主键 |
| code | VARCHAR(64) | 角色标识 |
| name | VARCHAR(64) | 角色名称 |
| permission_count | INT | 权限数量，查询时可聚合 |
| description | VARCHAR(255), NULL | 说明 |

### 3.3 permissions

| 字段 | 类型建议 | 页面含义 |
|---|---|---|
| id | BIGINT | 主键 |
| code | VARCHAR(128) | 权限编码 |
| name | VARCHAR(128) | 权限名称 |
| type | VARCHAR(32) | menu/button/data |
| parent_id | BIGINT, NULL | 父级权限 |
| path | VARCHAR(255), NULL | 前端路由或 API 路径 |

## 4. CRM 用户

### 4.1 crm_users

页面：客户 / CRM用户、CRM上下级、黑名单

| 字段 | 类型建议 | 页面含义 |
|---|---|---|
| id | BIGINT | 编号 |
| username | VARCHAR(64), NULL | 用户名 |
| name | VARCHAR(128), NULL | 姓名 |
| nickname | VARCHAR(128), NULL | 昵称 |
| phone | VARCHAR(64), NULL | 手机 |
| email | VARCHAR(255), NULL | 邮箱 |
| parent_id | BIGINT, NULL | 上级 CRM 用户 |
| parent_code | VARCHAR(64), NULL | 上级代码 |
| role_type | VARCHAR(32) | customer/agent/ib |
| certification_status | VARCHAR(32) | 认证状态 |
| status | VARCHAR(32) | 正常/禁用/黑名单 |
| remark | VARCHAR(1000), NULL | 备注 |

### 4.2 crm_user_profiles

页面：认证审核、认证设置、安全设置

| 字段 | 类型建议 | 页面含义 |
|---|---|---|
| user_id | BIGINT | CRM 用户 ID |
| gender | VARCHAR(16), NULL | 性别 |
| country | VARCHAR(64), NULL | 国家地区 |
| address | VARCHAR(255), NULL | 居住地 |
| education | VARCHAR(64), NULL | 学历 |
| birthday | DATE, NULL | 出生日期 |
| occupation | VARCHAR(128), NULL | 职业 |
| id_type | VARCHAR(32), NULL | 证件类型 |
| id_number | VARCHAR(128), NULL | 身份证/证件号 |
| id_front_file_id | BIGINT, NULL | 证件正面 |
| id_back_file_id | BIGINT, NULL | 证件反面 |
| proof_file_id | BIGINT, NULL | 身份证明 |

### 4.3 crm_user_finance_profiles

页面：认证审核、认证设置、安全设置

| 字段 | 类型建议 | 页面含义 |
|---|---|---|
| user_id | BIGINT | CRM 用户 ID |
| account_holder | VARCHAR(128), NULL | 开户人姓名 |
| bank_name | VARCHAR(128), NULL | 开户银行 |
| bank_address | VARCHAR(255), NULL | 开户行地址 |
| bank_account_no | VARCHAR(128), NULL | 银行卡账户 |
| bank_card_front_file_id | BIGINT, NULL | 银行卡正面 |
| bank_card_back_file_id | BIGINT, NULL | 银行卡反面 |

### 4.4 crm_user_hierarchy 查询字段

页面：客户 / CRM上下级

该页面可以由 `crm_users`、`mt5_accounts`、`deposit_requests`、`withdrawal_requests`、`commission_records` 聚合得到。

| 字段 | 来源建议 | 页面含义 |
|---|---|---|
| name | crm_users.name | 姓名 |
| certification_status | crm_users.certification_status | 认证状态 |
| child_count | crm_users 聚合 | 下级账号 |
| email | crm_users.email | 邮箱 |
| role_type | crm_users.role_type | 角色 |
| parent_code | crm_users.parent_code | 上级代码 |
| created_at | crm_users.created_at | 创建时间 |
| mt5_account_count | mt5_accounts 聚合 | MT5账号数量 |
| total_deposit_amount | deposit_requests 聚合 | 累计入金 |
| total_withdrawal_amount | withdrawal_requests 聚合 | 累计出金 |
| commission_balance | commission_records 聚合 | 佣金余额 |

## 5. MT5 基础

### 5.1 mt5_servers

页面：设置 / MT5设置 / 基础设置、服务器设置

| 字段 | 类型建议 | 页面含义 |
|---|---|---|
| id | BIGINT | 主键 |
| name | VARCHAR(128) | 服务器名称 |
| host | VARCHAR(255) | 地址 |
| port | INT | 连接端口 |
| manager_login | VARCHAR(64) | Manager账号 |
| token_encrypted | VARCHAR(1024) | MT5令牌，加密保存 |
| default_group | VARCHAR(128), NULL | 默认组别 |
| timezone | VARCHAR(64), NULL | MT5时区 |
| status | VARCHAR(32) | 启用/停用 |

### 5.2 mt5_groups

| 字段 | 类型建议 | 页面含义 |
|---|---|---|
| id | BIGINT | 主键 |
| server_id | BIGINT | MT5 服务器 |
| name | VARCHAR(128) | 组别名称 |
| default_leverage | INT, NULL | 默认杠杆 |
| status | VARCHAR(32) | 启用/停用 |

### 5.3 mt5_accounts

页面：客户 / MT5账户、开户审核、交易报表

| 字段 | 类型建议 | 页面含义 |
|---|---|---|
| id | BIGINT | 主键 |
| crm_user_id | BIGINT | CRM用户 |
| server_id | BIGINT | MT5服务器 |
| mt5_login | BIGINT | MT5账号 |
| parent_mt5_login | BIGINT, NULL | 上级MT5账号 |
| group_name | VARCHAR(128) | 组别 |
| leverage | INT | 杠杆 |
| balance | DECIMAL(20, 8) | 余额 |
| equity | DECIMAL(20, 8) | 净值 |
| credit | DECIMAL(20, 8) | 信用 |
| registered_at | DATETIME(6), NULL | 注册日期 |
| trade_enabled | BOOLEAN | 是否允许交易 |
| status | VARCHAR(32) | 状态 |

## 6. 审核任务

### 6.1 identity_verifications

页面：任务 / 认证审核

| 字段 | 类型建议 | 页面含义 |
|---|---|---|
| id | BIGINT | 序号 |
| crm_user_id | BIGINT | 用户 |
| recommender_id | BIGINT, NULL | 推荐人ID |
| parent_mt5_login | BIGINT, NULL | 上级MT5账号 |
| name | VARCHAR(128) | 姓名，查询冗余或关联 |
| phone | VARCHAR(64), NULL | 手机 |
| email | VARCHAR(255), NULL | 邮箱 |
| review_status | VARCHAR(32) | 审核状态 |
| reviewer_id | BIGINT, NULL | 审核人 |
| reviewed_at | DATETIME(6), NULL | 审核时间 |
| review_remark | VARCHAR(1000), NULL | 审核备注 |

### 6.2 account_open_requests

页面：任务 / 开户审核

| 字段 | 类型建议 | 页面含义 |
|---|---|---|
| id | BIGINT | 序号 |
| crm_user_id | BIGINT | 用户 |
| name | VARCHAR(128) | 姓名 |
| email | VARCHAR(255) | 邮箱 |
| requested_group | VARCHAR(128) | 组别 |
| requested_leverage | INT | 杠杆 |
| mt5_login | BIGINT, NULL | 开户成功后的MT5账号 |
| review_status | VARCHAR(32) | 状态 |
| reviewer_id | BIGINT, NULL | 审核人 |
| review_remark | VARCHAR(1000), NULL | 备注 |

### 6.3 deposit_requests

页面：任务 / 入金审核、财务报表 / 入金报表

| 字段 | 类型建议 | 页面含义 |
|---|---|---|
| id | BIGINT | 主键 |
| order_no | VARCHAR(64) | 交易编号/订单编号 |
| crm_user_id | BIGINT | 用户 |
| mt5_login | BIGINT | 账号 |
| deposit_method | VARCHAR(64) | 入金方式 |
| currency | VARCHAR(16) | 币种 |
| request_amount | DECIMAL(20, 8) | 入金金额 |
| actual_amount | DECIMAL(20, 8) | 实际金额 |
| fee_amount | DECIMAL(20, 8) | 手续费 |
| exchange_rate | DECIMAL(20, 8) | 汇率 |
| parent_email | VARCHAR(255), NULL | 上级代理邮箱 |
| review_status | VARCHAR(32) | 审核状态 |
| idempotency_key | VARCHAR(128), NULL | 幂等键 |
| mt5_synced_at | DATETIME(6), NULL | 写入MT5时间 |

### 6.4 withdrawal_requests

页面：任务 / 出金审核、财务报表 / 出金报表

| 字段 | 类型建议 | 页面含义 |
|---|---|---|
| id | BIGINT | 主键 |
| order_no | VARCHAR(64) | 交易编号/订单编号 |
| crm_user_id | BIGINT | 用户 |
| mt5_login | BIGINT | 账号 |
| withdrawal_method | VARCHAR(64) | 出金方式 |
| withdrawal_type | VARCHAR(64) | 出金类型 |
| account_holder | VARCHAR(128), NULL | 开户人 |
| bank_name | VARCHAR(128), NULL | 银行名称 |
| bank_branch | VARCHAR(128), NULL | 支行名称/开户行 |
| bank_account_no | VARCHAR(128), NULL | 银行卡号 |
| currency | VARCHAR(16) | 币种 |
| request_amount | DECIMAL(20, 8) | 出金金额 |
| actual_amount | DECIMAL(20, 8) | 实际金额 |
| fee_amount | DECIMAL(20, 8) | 手续费 |
| exchange_rate | DECIMAL(20, 8) | 汇率 |
| review_status | VARCHAR(32) | 审核状态 |
| idempotency_key | VARCHAR(128), NULL | 幂等键 |
| mt5_synced_at | DATETIME(6), NULL | 写入MT5时间 |

## 7. 财务与资金报表

### 7.1 transfer_records

页面：财务报表 / 转账报表

| 字段 | 类型建议 | 页面含义 |
|---|---|---|
| id | BIGINT | 主键 |
| order_no | VARCHAR(64) | 订单编号 |
| crm_user_id | BIGINT | 用户 |
| from_mt5_login | BIGINT | 转出账号 |
| to_mt5_login | BIGINT | 转入账号 |
| amount | DECIMAL(20, 8) | 金额合计 |
| currency | VARCHAR(16) | 币种 |
| transferred_at | DATETIME(6) | 转账/打款时间 |
| remark | VARCHAR(1000), NULL | 备注 |

### 7.2 payment_channels

页面：设置 / 出入金设置 / 在线入金

| 字段 | 类型建议 | 页面含义 |
|---|---|---|
| id | BIGINT | 序号 |
| name | VARCHAR(128) | 通道名称 |
| type | VARCHAR(64) | 通道类型 |
| config_json | JSON | 通道配置 |
| status | VARCHAR(32) | 状态 |
| last_updated_at | DATETIME(6), NULL | 上次更新时间 |

### 7.3 bank_accounts / wallet_accounts

页面：设置 / 出入金设置 / 汇款/钱包配置

| 字段 | 类型建议 | 页面含义 |
|---|---|---|
| id | BIGINT | 主键 |
| type | VARCHAR(64) | international_bank/local_bank/wallet/crypto |
| name | VARCHAR(128) | 显示名称 |
| account_holder | VARCHAR(128), NULL | 收款人姓名 |
| account_no | VARCHAR(255), NULL | 收款账号 |
| bank_name | VARCHAR(128), NULL | 银行名称 |
| bank_address | VARCHAR(255), NULL | 银行地址 |
| qr_file_id | BIGINT, NULL | 二维码 |
| status | VARCHAR(32) | 启用/停用 |
| remark | VARCHAR(1000), NULL | 备注 |

## 8. 交易报表

### 8.1 trade_orders

页面：交易报表 / 盈亏查询、持仓、平仓、挂单

| 字段 | 类型建议 | 页面含义 |
|---|---|---|
| id | BIGINT | 主键 |
| order_ticket | BIGINT | 订单编号 |
| position_ticket | BIGINT, NULL | 持仓编号 |
| deal_ticket | BIGINT, NULL | 成交编号 |
| mt5_login | BIGINT | MT5账户 |
| crm_user_id | BIGINT, NULL | CRM用户 |
| email | VARCHAR(255), NULL | 邮箱 |
| name | VARCHAR(128), NULL | 姓名 |
| group_name | VARCHAR(128), NULL | 所属组别 |
| symbol | VARCHAR(64) | 交易品种 |
| order_type | VARCHAR(64) | 订单类型 |
| direction | VARCHAR(16) | buy/sell/in/out |
| volume | DECIMAL(20, 8) | 交易数量/手数 |
| open_price | DECIMAL(20, 8), NULL | 开仓价格 |
| close_price | DECIMAL(20, 8), NULL | 平仓价格 |
| pending_price | DECIMAL(20, 8), NULL | 挂单价格 |
| stop_loss | DECIMAL(20, 8), NULL | 止损 |
| take_profit | DECIMAL(20, 8), NULL | 止盈 |
| commission | DECIMAL(20, 8) | 手续费 |
| swap | DECIMAL(20, 8) | 利息 |
| profit | DECIMAL(20, 8) | 盈亏 |
| opened_at | DATETIME(6), NULL | 开仓时间 |
| closed_at | DATETIME(6), NULL | 平仓时间 |
| order_time | DATETIME(6), NULL | 订单时间 |
| status | VARCHAR(32) | open/closed/pending |
| comment | VARCHAR(255), NULL | 订单备注 |

### 8.2 trade_deals

| 字段 | 类型建议 | 页面含义 |
|---|---|---|
| id | BIGINT | 主键 |
| deal_ticket | BIGINT | 成交编号 |
| order_ticket | BIGINT, NULL | 订单编号 |
| mt5_login | BIGINT | MT5账户 |
| symbol | VARCHAR(64), NULL | 交易品种 |
| deal_type | VARCHAR(64) | 成交类型 |
| direction | VARCHAR(16) | 方向 |
| volume | DECIMAL(20, 8) | 手数 |
| price | DECIMAL(20, 8) | 成交价 |
| profit | DECIMAL(20, 8) | 盈亏 |
| commission | DECIMAL(20, 8) | 手续费 |
| swap | DECIMAL(20, 8) | 利息 |
| deal_time | DATETIME(6) | 成交时间 |

### 8.3 品种报表聚合字段

页面：交易报表 / 品种报表

| 字段 | 来源建议 | 页面含义 |
|---|---|---|
| symbol | trade_orders.symbol | 品种 |
| trade_count | COUNT(*) | 交易笔数 |
| total_volume | SUM(volume) | 交易手数 |
| total_profit | SUM(profit) | 品种盈亏 |

## 9. 返佣

### 9.1 commission_rules

| 字段 | 类型建议 | 页面含义 |
|---|---|---|
| id | BIGINT | 主键 |
| name | VARCHAR(128) | 规则名称 |
| role_type | VARCHAR(32), NULL | 适用角色 |
| symbol_group | VARCHAR(128), NULL | 品种组 |
| rate_type | VARCHAR(32) | fixed/percentage/per_lot |
| rate_value | DECIMAL(20, 8) | 返佣值 |
| status | VARCHAR(32) | 启用/停用 |

### 9.2 commission_records

页面：佣金报表 / 订单返佣

| 字段 | 类型建议 | 页面含义 |
|---|---|---|
| id | BIGINT | 主键 |
| order_ticket | BIGINT | 订单编号 |
| trade_mt5_login | BIGINT | 交易账号 |
| order_volume | DECIMAL(20, 8) | 订单手数 |
| rebate_mt5_login | BIGINT | 返佣账户 |
| email | VARCHAR(255), NULL | 邮箱 |
| commission_amount | DECIMAL(20, 8) | 返佣金额 |
| actual_amount | DECIMAL(20, 8) | 实际金额 |
| commission_time | DATETIME(6) | 返佣时间 |
| status | VARCHAR(32) | 状态 |

## 10. 记录与通知

### 10.1 email_templates

| 字段 | 类型建议 | 页面含义 |
|---|---|---|
| id | BIGINT | 主键 |
| code | VARCHAR(128) | 模板编码 |
| subject | VARCHAR(255) | 邮件标题 |
| body | TEXT | 邮件内容 |
| language | VARCHAR(32) | 语言 |
| status | VARCHAR(32) | 启用/停用 |

### 10.2 email_logs

页面：记录 / 邮件记录

| 字段 | 类型建议 | 页面含义 |
|---|---|---|
| id | BIGINT | 主键 |
| subject | VARCHAR(255) | 邮件标题 |
| template_code | VARCHAR(128), NULL | 邮件模板 |
| recipient_email | VARCHAR(255) | 邮件人邮箱 |
| recipient_user_id | BIGINT, NULL | 邮件人ID |
| sent_at | DATETIME(6), NULL | 发送时间 |
| status | VARCHAR(32) | 发送状态 |
| failure_reason | VARCHAR(1000), NULL | 失败原因 |

### 10.3 notification_logs

页面：记录 / 短信记录、通知记录

| 字段 | 类型建议 | 页面含义 |
|---|---|---|
| id | BIGINT | 主键 |
| title | VARCHAR(255) | 通知标题 |
| type | VARCHAR(64) | 通知类型 |
| recipient | VARCHAR(255), NULL | 接收人 |
| content | TEXT | 内容 |
| sent_at | DATETIME(6), NULL | 发送时间 |
| status | VARCHAR(32) | 状态 |
| failure_reason | VARCHAR(1000), NULL | 失败原因 |

### 10.4 operation_logs

页面：记录 / 操作日志

| 字段 | 类型建议 | 页面含义 |
|---|---|---|
| id | BIGINT | 主键 |
| operator_id | BIGINT, NULL | 操作员ID |
| operator_name | VARCHAR(64) | 操作员 |
| path | VARCHAR(255) | 路径 |
| method | VARCHAR(16) | HTTP方法 |
| ip_address | VARCHAR(64) | IP地址 |
| user_agent | VARCHAR(512), NULL | 浏览器信息 |
| params_json | JSON, NULL | 参数 |
| result | VARCHAR(32) | success/failure |
| operated_at | DATETIME(6) | 操作时间 |

## 11. 系统设置

### 11.1 platform_settings

页面：设置 / CRM设置 / 平台设置

| 字段 | 类型建议 | 页面含义 |
|---|---|---|
| key | VARCHAR(128) | 配置键 |
| value_json | JSON | 配置值 |

建议配置键：

- site_chinese_name
- site_english_name
- default_language
- enabled_languages
- logo_file_id
- favicon_file_id
- register_methods
- email_domain
- admin_login_verify_method

首版语言默认值：

- `zh-CN`：简体中文
- `zh-TW`：繁体中文
- `en-US`：English

品牌信息、语言、Logo、favicon 均由后台配置维护。初始化时可以写默认值，但不得在业务代码中写死。

### 11.2 security_settings

页面：设置 / CRM设置 / 安全设置、认证设置、通用设置

建议使用 JSON 配置保存：

| 配置键 | 说明 |
|---|---|
| registration_limit | 注册限制 |
| password_rule | 密码规则 |
| account_lock_rule | 账户锁定规则 |
| required_profile_fields | 认证资料必填项 |
| auth_review_enabled | 认证审核开关 |
| user_review_enabled | 用户审核开关 |
| deposit_review_enabled | 入金审核开关 |
| withdrawal_review_enabled | 出金审核开关 |
| order_review_enabled | 新订单审核开关 |
| supported_languages | 支持语言 |
| field_visibility_rules | 字段展示/隐藏规则 |

### 11.3 funds_settings

页面：设置 / 出入金设置 / 基础设置

| 配置键 | 说明 |
|---|---|
| deposit_currency | 入金币种 |
| withdrawal_currency | 出金币种 |
| deposit_exchange_rate | 入金汇率 |
| withdrawal_exchange_rate | 出金汇率 |
| min_deposit_amount | 最低入金金额 |
| max_deposit_amount | 最高入金金额 |
| min_withdrawal_amount | 最低出金金额 |
| max_withdrawal_amount | 最高出金金额 |
| deposit_fee_rule | 入金手续费规则 |
| withdrawal_fee_rule | 出金手续费规则 |
| auto_deposit_enabled | 自动入金 |
| withdrawal_review_mode | 出金审核策略 |
| payment_check_enabled | 支付检查开关 |

入出金规则必须后台可配置，不能写死在代码中。首版应支持：

- 入金币种
- 出金币种
- 最低入金金额
- 最高入金金额
- 最低出金金额
- 最高出金金额
- 入金手续费规则
- 出金手续费规则
- 汇率规则
- 入金是否自动审核
- 出金是否人工审核
- 出金是否需要支付检查

### 11.4 payment_method_settings

页面：设置 / 出入金设置 / 在线入金、固定钱包、本地汇款、数字货币

支付/收款方式必须后台可配置，不能写死在代码中。

| 字段 | 类型建议 | 说明 |
|---|---|---|
| id | BIGINT | 主键 |
| method_type | VARCHAR(64) | online/bank/wallet/crypto |
| name | VARCHAR(128) | 名称 |
| currency | VARCHAR(16) | 币种 |
| config_json | JSON | 通道或收款配置 |
| sort_order | INT | 排序 |
| status | VARCHAR(32) | 启用/停用 |

不同方式的 `config_json` 可保存不同结构：

- 在线入金：网关地址、商户号、回调地址、密钥引用。
- 银行汇款：收款人、银行名、开户地址、账号、SWIFT。
- 固定钱包：钱包名称、账户、二维码文件。
- 数字货币：链类型、币种、地址、二维码文件、确认数。

## 12. 开发时如何使用本文档

每开发一个模块，按这个顺序查文档：

1. `docs/development-task-list.md`：确认当前开发任务。
2. `docs/data-field-map.md`：确认表字段、接口字段、页面字段。
3. `docs/mt5-crm-feature-inventory.md`：确认页面交互和菜单来源。
4. `docs/python-mysql-technical-route.md`：确认技术路线和架构边界。

当发现参考系统还有本文档未覆盖的字段时：

- 先补充本文档。
- 再写模型/迁移/接口。
- 不直接把字段散落写进代码里。
