下面是一份**简要、结构化、可快速上手的开发进度文档**，适合你在**新对话 / 新上下文**中直接粘贴使用，让对方立刻知道：

* 项目在做什么
* 已经完成到哪一步
* 当前架构与设计决策

---

# ClubInterviewSystem Backend —— 当前开发进度说明

## 一、项目概述

* 项目类型：校园社团 / 面试系统后端
* 技术栈：

  * FastAPI
  * SQLModel + SQLAlchemy
  * MySQL
  * Alembic（数据库迁移）
  * JWT（访问令牌）
  * pytest + FastAPI TestClient（接口测试）
* Python 版本：3.10
* 环境管理：conda + pip

---

## 二、已完成的核心功能（✅）

### 1. 用户账号生命周期设计（已完整实现）

采用**“手机号注册 + 账号初始化”**的两阶段模型：

```text
手机号注册（仅手机号）
   ↓
账号存在（password_hash = NULL，未初始化）
   ↓
通过 JWT 保持登录态
   ↓
账号初始化（设置密码 + 用户资料）
   ↓
正式登录
```

这是一个**符合真实业务的设计**，而不是简单的“注册即登录”。

---

### 2. 用户表（user_account）

已完成建模 + 迁移，关键字段包括：

* phone（唯一）
* password_hash（可为 NULL，用于区分是否初始化）
* token_version（用于强制下线）
* status（启用 / 禁用）
* 软删除字段（is_deleted / deleted_at）
* 用户资料字段（姓名、学校、专业、学号、邮箱等）

---

### 3. 登录接口 `/auth/login`

功能与约束：

* 根据手机号查用户
* 校验用户状态（禁用不可登录）
* 校验是否已初始化（未初始化禁止登录）
* 校验密码（bcrypt）
* 签发 JWT（payload 包含 `user_id` + `token_version`）

---

### 4. 账号初始化接口 `/auth/init`（已完成）

* 必须登录（JWT）
* 仅允许 **未初始化账号** 调用
* 设置内容包括：

  * 密码
  * 姓名
  * 身份证号
  * 学校 / 专业 / 学号
  * 邮箱、头像（可选）
* 重复初始化返回 `409 Conflict`
* 初始化完成后即可正常登录

---

### 5. JWT 鉴权体系（已完成）

* access token 生成与解析
* payload 精简设计（不暴露敏感信息）
* token_version 校验（支持强制下线）
* 统一依赖：

  * `get_current_user_by_token`（纯逻辑，可测试）
  * `get_current_user`（FastAPI Depends）

---

### 6. 项目结构（已稳定）

```text
ClubInterviewSystem-Backend/
├── app/
│   ├── api/
│   │   ├── deps.py              # FastAPI 依赖注入 (JWT 认证)
│   │   └── v1/
│   │       └── auth.py          # 认证 API (注册/登录/初始化/用户信息)
│   ├── core/
│   │   ├── config.py            # 配置管理 (Pydantic Settings)
│   │   └── security.py          # JWT 工具 (签发/解码)
│   ├── db/
│   │   └── session.py           # 数据库引擎 & Session 工厂
│   ├── models/
│   │   ├── base.py              # 基础模型 (软删除/时间戳/恢复方法)
│   │   ├── school.py            # 学校表模型
│   │   └── user_account.py      # 用户账号表模型
│   ├── repositories/
│   │   ├── base.py              # 通用仓储基类 (CRUD + 软删除)
│   │   └── user_account.py      # 用户仓储 (密码哈希/初始化)
│   └── main.py                  # FastAPI 应用入口 & 路由注册
├── alembic/
│   ├── versions/                # 数据库迁移历史
│   │   ├── 7906d6cae979_create_school_table.py
│   │   └── 9e13212a1495_create_user_account_table.py
│   └── env.py                   # Alembic 配置 (SQLModel 集成)
├── tests/
│   └── test_auth_init.py        # 账号初始化流程测试
├── .env                         # 环境变量配置
└── tmp_test_user_repo.py        # 用户仓储测试脚本
```

分层清晰，便于后续扩展。

---

### 7. 测试（已完成）

* 使用 `pytest`
* 使用 `FastAPI TestClient`
* 已完成接口级测试：

  * `/auth/init` 全流程测试

    * 未登录 → 401
    * 初始化成功 → 200
    * 重复初始化 → 409
    * 初始化后登录成功
* 测试已通过（`pytest -q` 全绿）

---

## 三、已解决的关键工程问题（🛠）

* Alembic 迁移链断裂修复
* 数据库字段 nullable 与业务设计对齐
* JWT / Depends / Swagger Header 使用问题
* 测试环境依赖（httpx）补齐
* 路由前缀不一致导致的 404 问题定位与修复

---

## 四、当前状态总结

> **Auth 模块已完成闭环，具备生产级雏形**

* 账号生命周期清晰
* 数据库设计与业务一致
* 接口具备测试保障
* 架构支持后续扩展（学校、面试、权限等）

---

## 五、下一步可选方向（未开始）

* `/auth/me`：获取当前用户信息（前端强依赖）
* 学校 / 专业等基础数据接口
* 密码修改 & token 强制失效
* 实名认证流程拆分
* 面试 / 报名 / 管理端模块

---

> **当前阶段定位**：
> 已完成“用户与认证”核心基础设施，系统进入 **业务扩展阶段**。

---
