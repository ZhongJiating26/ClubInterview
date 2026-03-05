# Club Interview System Backend

<div align="center">

**校园社团招新与面试管理系统后端**

基于 FastAPI + SQLModel + MySQL 的现代化 Web 应用

[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green?logo=fastapi)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)](https://www.python.org)
[![MySQL](https://img.shields.io/badge/MySQL-8.0+-orange?logo=mysql)](https://www.mysql.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

---

## 📋 项目简介

这是一个基于 **FastAPI** + **SQLModel** + **MySQL** 的校园社团招新与面试管理系统后端。项目采用现代化的 Python Web 开发架构，提供用户注册、登录认证、社团管理、报名审核、面试安排、评分录取等完整的招新面试流程。

### ✨ 核心功能

- **🔐 用户认证**：手机号 + 验证码注册、JWT Token 认证
- **🏢 社团管理**：社团创建、资料管理、成员管理、部门岗位管理
- **📢 招新管理**：招新场次发布、岗位配置、报名审核
- **💼 面试管理**：面试场次管理、候选人排期、面试记录、评分模板
- **👨‍🎓 学生端**：报名申请、面试记录、个人信息、通知工单

---

## 🛠️ 技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| **FastAPI** | 0.104+ | 异步 Web 框架 |
| **SQLModel** | 0.0.14+ | ORM + Pydantic 模型 |
| **MySQL** | 8.0+ | 关系型数据库 |
| **Alembic** | 1.13+ | 数据库迁移工具 |
| **Passlib** | 1.7+ | 密码哈希 (bcrypt) |
| **python-jose** | 3.3+ | JWT 令牌处理 |
| **Pydantic** | 2.5+ | 数据验证 |
| **boto3** | 1.34+ | S3 兼容存储 (RustFS) |

---

## 🚀 快速开始

### 前置要求

- Python 3.10+
- MySQL 8.0+
- RustFS（或其他 S3 兼容存储）

### 1. 克隆项目

```bash
git clone <repository-url>
cd ClubInterviewSystem-Backend
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

创建 `.env` 文件（参考 `.env.example`）：

```env
# ========== 基础配置 ==========
APP_NAME=Club Interview System Backend
APP_ENV=development
DEBUG=true

# ========== 数据库配置 ==========
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=campus_club_interview

# ========== JWT 配置 ==========
JWT_SECRET_KEY=your_secret_key_change_me_in_production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# ========== 存储配置 ==========
STORAGE_PROVIDER=rustfs
STORAGE_ENDPOINT=http://127.0.0.1:9000
STORAGE_ACCESS_KEY=rustfsadmin
STORAGE_SECRET_KEY=rustfsadmin
STORAGE_BUCKET=club-interview-system
STORAGE_ENV=dev
```

### 4. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑配置
vim .env
```

关键配置项说明：

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `DB_HOST` | MySQL 服务器地址 | localhost |
| `DB_PORT` | MySQL 端口 | 3306 |
| `DB_USER` | 数据库用户名 | root |
| `DB_PASSWORD` | 数据库密码 | - |
| `DB_NAME` | 数据库名称 | club_interview |
| `APP_ENV` | 环境：development / production | development |
| `JWT_SECRET_KEY` | JWT 密钥（生产环境必改） | CHANGE_ME |
| `STORAGE_ENDPOINT` | RustFS 服务地址 | http://127.0.0.1:9000 |
| `STORAGE_BUCKET` | 存储桶名称 | club-interview |

### 5. 启动服务

```bash
# 开发模式（支持热重载，数据库迁移需手动执行）
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 生产模式（启动时自动执行数据库迁移和存储初始化）
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

> **注意**：生产模式 (`APP_ENV=production`) 会在启动时自动执行 `alembic upgrade head` 和存储服务初始化。

### 6. 访问 API 文档

启动服务后，访问以下地址查看自动生成的 API 文档：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 📁 项目结构

```
ClubInterviewSystem-Backend/
├── app/
│   ├── api/                    # API 路由层
│   │   ├── v1/                 # API v1 版本
│   │   │   ├── auth.py         # 用户认证
│   │   │   ├── school.py       # 学校管理
│   │   │   ├── club.py         # 社团管理
│   │   │   ├── department.py   # 部门管理
│   │   │   ├── position.py     # 岗位管理
│   │   │   ├── recruitment_session.py  # 招新场次
│   │   │   ├── signup.py       # 报名管理
│   │   │   ├── interview.py    # 面试管理
│   │   │   └── student.py      # 学生端
│   │   └── deps.py             # 依赖注入
│   ├── core/                   # 核心配置
│   │   ├── config.py           # 配置管理
│   │   ├── security.py         # 安全相关（JWT）
│   │   └── storage.py          # 存储服务
│   ├── db/                     # 数据库
│   │   └── session.py          # 数据库会话
│   ├── models/                 # 数据模型
│   │   ├── user_account.py     # 用户账号
│   │   ├── school.py           # 学校
│   │   ├── club.py             # 社团
│   │   ├── department.py       # 部门
│   │   ├── club_position.py    # 岗位
│   │   ├── recruitment_session.py  # 招新场次
│   │   ├── signup_session.py   # 报名记录
│   │   ├── interview_session.py    # 面试场次
│   │   ├── interview_candidate.py  # 候选人
│   │   ├── interview_record.py     # 面试记录
│   │   ├── score_template.py   # 评分模板
│   │   ├── notification.py     # 通知
│   │   └── ticket.py           # 工单
│   ├── repositories/           # 数据访问层
│   ├── schemas/                # Pydantic 模型（请求/响应）
│   └── main.py                 # 应用入口
├── alembic/                    # 数据库迁移
├── tests/                      # 测试用例
├── scripts/                    # 脚本工具
├── .env.example                # 环境变量示例
├── requirements.txt            # 依赖列表
└── README.md                   # 项目文档
```

---

## 📡 API 接口概览

### 基础信息

- **Base URL**: `http://localhost:8000/api/v1`
- **认证方式**: JWT Bearer Token
- **响应格式**: JSON

### 模块列表

| 模块 | 路径前缀 | 说明 | 接口数量 |
|------|----------|------|----------|
| 认证模块 | `/auth` | 用户注册、登录、Token 管理 | 6 |
| 学校模块 | `/schools` | 学校搜索 | 1 |
| 社团模块 | `/clubs` | 社团创建、管理、查询 | 8 |
| 部门模块 | `/clubs/{club_id}/departments` | 部门 CRUD | 4 |
| 岗位模块 | `/clubs/{club_id}/positions` | 岗位 CRUD | 4 |
| 招新模块 | `/recruitment/sessions` | 招新场次管理 | 9 |
| 报名模块 | `/signup` | 报名审核管理 | 5 |
| 报名模块 | `/student/applications` | 学生报名管理 | 5 |
| 面试模块 | `/interview` | 面试全流程管理 | ~20 |
| 学生模块 | `/student` | 学生端综合服务 | ~20 |

**总计**：约 **82** 个 API 接口

### 快速查询

```bash
# 查看所有接口
curl http://localhost:8000/docs

# 健康检查
curl http://localhost:8000/health

# 获取学校列表
curl http://localhost:8000/api/v1/schools/search?keyword=武汉大学

# 用户登录
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"phone": "13800138000", "code": "123456"}'
```

---

## ✅ 已完成功能

### 🔑 基础功能
- [x] 用户注册/登录/初始化流程
- [x] JWT 认证与权限控制
- [x] 软删除机制（数据可追溯）
- [x] 数据库迁移 (Alembic)
- [x] API 自动文档（Swagger/ReDoc）

### 🏢 社团管理
- [x] 社团创建与初始化
- [x] 社团资料管理
- [x] 部门 CRUD 操作
- [x] 岗位 CRUD 操作
- [x] 招新场次管理
- [x] 岗位招聘配额管理

### 📝 报名管理
- [x] 学生报名申请
- [x] 报名审核流程
- [x] 多岗位报名支持
- [x] 报名记录查询（支持分页、筛选）

### 💼 面试管理
- [x] 面试场次 CRUD
- [x] 面试官分配
- [x] 候选人排期生成
- [x] 评分模板管理
- [x] 面试记录管理
- [x] 录取结果管理
- [x] 面试结果汇总统计

### 👨‍🎓 学生端
- [x] 个人信息管理
- [x] 报名记录查询
- [x] 面试记录查询
- [x] 通知管理（已读/未读）
- [x] 工单系统
- [x] 报名统计

### 💾 存储集成
- [x] RustFS 对象存储集成
- [x] 文件上传/下载接口
- [x] 图片处理

---

## 📊 数据模型

### 核心模型

| 模型 | 说明 | 关键字段 |
|------|------|----------|
| `UserAccount` | 用户账号 | phone, name, school_code |
| `School` | 学校信息 | code, name |
| `Club` | 社团信息 | name, description, logo_url |
| `Department` | 部门信息 | name, club_id |
| `ClubPosition` | 岗位信息 | name, department_id, quota |
| `RecruitmentSession` | 招新场次 | name, start_time, end_time |
| `SignupSession` | 报名记录 | user_id, recruitment_session_id, status |
| `InterviewSession` | 面试场次 | name, place, start_time, end_time |
| `InterviewCandidate` | 候选人排期 | session_id, candidate_user_id, status |
| `ScoreTemplate` | 评分模板 | name, club_id |
| `Notification` | 通知 | title, content, is_read |
| `Ticket` | 工单 | title, content, status |

---

## 🔒 权限管理

### 角色类型

| 角色 | 代码 | 说明 |
|------|------|------|
| 学生 | `STUDENT` | 普通学生用户 |
| 社团管理员 | `CLUB_ADMIN` | 社团管理员，可管理社团相关业务 |
| 面试官 | `INTERVIEWER` | 面试官，可参与面试评分 |

### 权限矩阵

| 功能模块 | 学生 | 社团管理员 | 面试官 |
|---------|------|-----------|--------|
| 报名申请 | ✅ | ✅ | ✅ |
| 报名审核 | ❌ | ✅ | ✅ |
| 社团管理 | ❌ | ✅ | ❌ |
| 部门岗位管理 | ❌ | ✅ | ❌ |
| 面试场次管理 | ❌ | ✅ | ❌ |
| 面试评分 | ❌ | ✅ | ✅ |
| 录取决策 | ❌ | ✅ | ❌ |
| 个人信息 | ✅ | ✅ | ✅ |

---

## 🧪 测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_auth.py

# 查看测试覆盖率
pytest --cov=app tests/
```

---

## 📝 更新日志

### v2.1.0 (2026-01-21)

**自动化改进**
- 🚀 **启动时自动数据库迁移**：生产模式 (`APP_ENV=production`) 下，应用启动时自动执行 `alembic upgrade head`，确保数据库结构正确
- 🔧 **存储服务自动初始化**：启动时自动检测并创建 RustFS bucket，无需手动预配置
- 📖 **完善部署文档**：更新快速开始指南，详细说明配置项用途

### v2.0.0 (2026-01-10)

**重大更新**
- 🔥 **删除废弃模块**：移除 admin.py 和 interviewer.py 模块
- 🔧 **统一路由前缀**：所有接口统一使用 `/api/v1` 前缀
- 🗑️ **清理未使用接口**：删除约 30+ 个未使用的接口
- 🐛 **修复 Repository 重复定义**：解决 ScoreItemRepository 重复问题
- 📚 **更新文档**：完善 API 接口文档

### v1.4.0 (2026-01-05)

- 完成面试官任务模块
- 完成文件上传功能
- 完成通知管理功能

### v1.0.0 (2025-12-XX)

- 初始版本发布
- 完成基础功能模块

---

## 📖 相关文档

- [完整 API 接口文档](./文档/完整API接口文档.md)
- [数据库设计文档](./文档/数据库设计文档v2.1.md)
- [系统详细设计文档](./文档/系统详细设计文档v2.7.md)
- [前端 API 文档](./前端给出的API接口文档.md)

---

## 🤝 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

## 👥 作者

校园社团招新与面试管理系统开发团队

---

## 📮 联系方式

如有问题或建议，请提交 Issue 或 Pull Request。

<div align="center">

**⭐ 如果这个项目对你有帮助，请给我们一个 Star！**

</div>
