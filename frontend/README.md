# 社团面试系统前端

> 基于 Vue 3 + TypeScript + Vite + shadcn-vue 构建的现代化社团面试管理系统前端项目。

## 项目简介

本系统是一个面向高校社团的面试管理平台，支持社团招新、报名审核、面试安排、评分管理等全流程功能。系统采用多端适配设计：
- **管理员端/面试官端**：桌面 Web 端
- **学生端**：移动端 H5

## 文档导航

| 文档 | 说明 |
|------|------|
| [完整API接口文档](./文档/完整API接口文档.md) | 后端 API 接口文档 |
| [系统详细设计文档](./文档/系统详细设计文档v2.7.md) | 系统设计文档 |

## 技术栈

| 技术 | 版本 | 说明 |
|------|------|------|
| **Vue** | 3.5+ | 渐进式 JavaScript 框架 (Script Setup 语法) |
| **TypeScript** | 5.9+ | 类型安全的 JavaScript 超集 |
| **Vite** | 7.2+ | 新一代前端构建工具 |
| **Vue Router** | 4.6+ | Vue 官方路由管理器 |
| **Pinia** | 3.0+ | Vue 官方状态管理库 |
| **shadcn-vue** | 2.4+ | 基于 reka-ui 的组件库 |
| **Tailwind CSS** | 4.1+ | 实用优先的 CSS 框架 |
| **Axios** | 1.13+ | HTTP 客户端 |
| **Lucide Vue** | 0.562+ | 图标库 |

## 项目结构

```
src/
├── api/                      # API 接口封装
│   ├── modules/              # 按模块组织的 API
│   │   ├── auth.ts           # 认证相关接口
│   │   ├── application.ts    # 报名申请接口
│   │   ├── clubs.ts          # 社团管理接口
│   │   ├── interview.ts      # 面试管理接口
│   │   ├── notification.ts   # 通知接口
│   │   ├── recruitment.ts    # 招新管理接口
│   │   ├── school.ts         # 学校数据接口
│   │   ├── score.ts          # 评分接口
│   │   ├── statistics.ts     # 统计数据接口
│   │   ├── student.ts        # 学生管理接口
│   │   └── ticket.ts         # 工单管理接口
│   ├── request.ts            # Axios 请求配置（拦截器）
│   └── index.ts              # API 统一导出
├── components/               # 公共组件
│   ├── ui/                   # shadcn-vue 基础组件
│   ├── AppSidebar.vue        # 侧边栏组件
│   ├── NavGroup.vue          # 导航分组
│   ├── NavMain.vue           # 主导航
│   ├── NavUser.vue           # 用户导航
│   └── SchoolSelect.vue      # 学校选择器
├── layouts/                  # 布局组件
│   ├── AdminLayout.vue       # 管理员端布局（桌面端）
│   ├── InterviewerLayout.vue # 面试官端布局（桌面端）
│   └── StudentLayout.vue     # 学生端布局（移动端）
├── lib/                      # 工具库
│   └── utils.ts              # 通用工具函数
├── router/                   # 路由配置
│   └── index.ts              # 路由定义和守卫
├── stores/                   # Pinia 状态管理
│   └── user.ts               # 用户状态
├── views/                    # 页面组件
│   ├── Login.vue             # 登录页
│   ├── Register.vue          # 注册页
│   ├── ForgetPassword.vue    # 忘记密码
│   ├── RoleSelect.vue        # 角色选择
│   ├── Init.vue              # 信息初始化
│   ├── NotFound.vue          # 404 页面
│   ├── admin/                # 管理员端页面
│   │   ├── Dashboard.vue     # 仪表盘
│   │   ├── Applications.vue  # 报名管理（父路由）
│   │   ├── Interviews.vue    # 面试管理（父路由）
│   │   ├── Statistics.vue    # 数据统计
│   │   ├── Tickets.vue       # 工单管理
│   │   ├── applications/     # 报名子页面
│   │   │   ├── Create.vue    # 发布报名
│   │   │   ├── SessionWizard.vue # 场次向导
│   │   │   ├── History.vue   # 历史记录
│   │   │   └── Review.vue    # 报名审核
│   │   ├── interviews/       # 面试子页面
│   │   │   ├── List.vue      # 场次列表
│   │   │   ├── Wizard.vue    # 发布向导
│   │   │   ├── Records.vue   # 面试记录
│   │   │   └── Filter.vue    # 面试筛选
│   │   ├── clubs/            # 社团管理
│   │   │   ├── Profile.vue   # 社团资料
│   │   │   ├── Departments.vue # 部门管理
│   │   │   ├── Positions.vue   # 岗位管理
│   │   │   └── Members.vue   # 人员管理
│   │   └── settings/
│   │       └── Settings.vue  # 系统设置
│   ├── interviewer/          # 面试官端页面
│   │   ├── Join.vue          # 加入社团
│   │   ├── Applications.vue  # 报名管理（父路由）
│   │   ├── Interviews.vue    # 面试管理（父路由）
│   │   ├── applications/
│   │   │   ├── Sessions.vue  # 报名场次
│   │   │   ├── SessionDetail.vue # 场次详情
│   │   │   └── History.vue   # 历史记录
│   │   └── interviews/
│   │       ├── List.vue      # 面试场次
│   │       ├── Score.vue     # 面试评分
│   │       ├── Records.vue   # 面试记录
│   │       └── Filter.vue    # 面试筛选
│   └── student/              # 学生端页面（移动端）
│       ├── Home.vue          # 社团首页
│       ├── ClubDetail.vue    # 社团详情
│       ├── Apply.vue         # 报名申请
│       ├── Interviews.vue    # 面试列表
│       ├── Profile.vue       # 个人中心
│       └── interviews/
│           ├── SignupDetail.vue  # 报名详情
│           └── RecordDetail.vue  # 面试详情
├── App.vue                   # 根组件
├── main.ts                   # 应用入口
└── style.css                 # 全局样式
```

## 用户角色

| 角色 | 端类型 | 主要职责 |
|------|--------|----------|
| **社团管理员 (admin)** | 桌面 Web 端 | 管理社团招新、面试安排、审核报名等 |
| **面试官 (interviewer)** | 桌面 Web 端 | 参与面试评分、评审工作 |
| **普通学生 (student)** | 移动端 H5 | 申请加入社团、查看面试状态 |

## 功能特性

### 认证流程

```
注册 → 登录 → 选择角色 → 初始化信息 → 进入对应端
```

- 新用户注册后登录需选择角色（社团管理员/面试官/普通学生）
- 根据角色初始化不同的用户信息
- 社团管理员需创建或关联社团

### 管理员端功能

| 模块 | 功能 |
|------|------|
| **仪表盘** | 数据概览、社团资料完整性检查 |
| **报名管理** | 发布招新场次、历史报名记录查看、报名审核 |
| **面试管理** | 发布面试场次、面试记录查看、面试筛选分配 |
| **社团管理** | 社团资料编辑、部门/岗位管理、成员管理 |
| **数据统计** | 招新数据统计分析 |
| **工单管理** | 工单处理 |
| **系统设置** | 系统参数配置 |

### 面试官端功能

| 模块 | 功能 |
|------|------|
| **加入社团** | 查看和接受社团邀请 |
| **报名管理** | 查看报名场次、报名详情、历史记录 |
| **面试管理** | 查看面试任务、面试评分、面试记录 |

### 学生端功能

| 模块 | 功能 |
|------|------|
| **社团首页** | 浏览所有社团、搜索筛选 |
| **社团详情** | 查看社团信息、招新场次 |
| **报名申请** | 选择岗位、填写自我介绍 |
| **面试中心** | 查看面试记录、面试详情 |
| **个人中心** | 个人资料管理 |

## 开发指南

### 环境要求

- Node.js >= 18.0.0
- npm >= 9.0.0

### 安装依赖

```bash
npm install
```

### 启动开发服务器

```bash
npm run dev
```

默认访问地址: http://localhost:5173

> 项目已配置 `host: '0.0.0.0'`，支持通过局域网 IP 访问，方便移动端调试。

### 构建生产版本

```bash
npm run build
```

构建产物将输出到 `dist/` 目录。

### 预览生产构建

```bash
npm run preview
```

## API 代理配置

开发环境下通过 Vite 代理访问后端 API，配置文件 `vite.config.ts`：

```typescript
server: {
  proxy: {
    '/auth': 'http://localhost:8000',
    '/schools': 'http://localhost:8000',
    // ... 其他代理配置
  }
}
```

### 请求拦截器

项目在 `src/api/request.ts` 中配置了 Axios 请求/响应拦截器：

- **请求拦截**：自动添加 Authorization 头
- **响应拦截**：统一处理响应格式和错误

## 组件使用

### shadcn-vue 组件

项目使用 shadcn-vue 组件库，组件位于 `src/components/ui/` 目录。

```vue
<script setup lang="ts">
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
</script>

<template>
  <Card>
    <CardHeader>
      <CardTitle>标题</CardTitle>
    </CardHeader>
    <CardContent>
      <Button>点击</Button>
    </CardContent>
  </Card>
</template>
```

### 添加新组件

```bash
# 使用 shadcn-vue CLI 添加组件
npx shadcn-vue add [组件名]
```

## 状态管理

使用 Pinia 进行状态管理，Store 位于 `src/stores/` 目录：

```typescript
// 使用用户 Store
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
userStore.doLogin(phone, password)
```

## 路由配置

路由采用嵌套路由结构，支持权限控制和角色路由：

- **公开路由**：登录、注册、忘记密码等
- **角色路由**：根据用户角色动态渲染对应端布局
- **路由守卫**：自动处理权限验证和重定向

## 代码规范

- **组件命名**：使用 PascalCase（多词组合，首字母大写）
- **文件命名**：
  - Vue 组件：PascalCase.vue
  - TypeScript 文件：camelCase.ts
- **代码风格**：遵循 Vue 3 官方风格指南

## 浏览器支持

| 浏览器 | 版本 |
|--------|------|
| Chrome | 最新版 |
| Firefox | 最新版 |
| Safari | 最新版 |
| Edge | 最新版 |

移动端浏览器支持 iOS Safari 和 Chrome Android。

## 常见问题

### Q: 如何添加新的 API 模块？

在 `src/api/modules/` 下创建新的 TypeScript 文件，导出 API 函数：

```typescript
// src/api/modules/example.ts
import request from '../request'

export function getExampleData() {
  return request.get('/example')
}
```

### Q: 如何添加新的页面？

1. 在 `src/views/` 对应角色目录下创建 Vue 组件
2. 在 `src/router/index.ts` 中添加路由配置
3. 如需侧边栏显示，在 `src/components/AppSidebar.vue` 中添加导航项

### Q: 如何调试移动端？

1. 确保开发服务器配置了 `host: '0.0.0.0'`
2. 获取本机局域网 IP（如 `192.168.1.100`）
3. 手机连接同一 Wi-Fi，访问 `http://192.168.1.100:5173`

## License

MIT License

## 联系方式

如有问题或建议，请提交 Issue。
