# 校园社团招新与面试管理系统 - 完整 API 接口文档

## 文档信息

- **系统名称**：校园社团招新与面试管理系统
- **版本**：v2.0.0
- **更新日期**：2026-01-10
- **Base URL**：`http://localhost:8000/api/v1`（本地开发）

---

## 目录

- [通用说明](#通用说明)
- [1. 用户认证模块](#1-用户认证模块)
- [2. 学校管理模块](#2-学校管理模块)
- [3. 社团管理模块](#3-社团管理模块)
- [4. 部门管理模块](#4-部门管理模块)
- [5. 岗位管理模块](#5-岗位管理模块)
- [6. 招新场次管理模块](#6-招新场次管理模块)
- [7. 报名管理模块](#7-报名管理模块)
- [8. 面试管理模块](#8-面试管理模块)
- [9. 学生端模块](#9-学生端模块)
- [数据模型](#数据模型)
- [错误码说明](#错误码说明)

---

## 通用说明

### 认证方式

所有需要认证的接口都需要在请求头中携带 JWT Token：

```
Authorization: Bearer {token}
```

### 响应格式

成功响应：
```json
{
  "code": 200,
  "data": {},
  "message": "success"
}
```

错误响应：
```json
{
  "detail": "错误描述信息"
}
```

---

## 1. 用户认证模块

### 1.1 发送验证码

```
POST /api/v1/auth/send-code
```

**请求体：**
```json
{
  "phone": "13800138000"
}
```

### 1.2 用户注册

```
POST /api/v1/auth/register
```

**请求体：**
```json
{
  "phone": "13800138000",
  "code": "123456",
  "name": "张三"
}
```

### 1.3 用户登录

```
POST /api/v1/auth/login
```

**请求体：**
```json
{
  "phone": "13800138000",
  "code": "123456"
}
```

### 1.4 获取当前用户信息

```
GET /api/v1/auth/me
Authorization: Bearer {token}
```

### 1.5 初始化账号

```
POST /api/v1/auth/init
Authorization: Bearer {token}
```

### 1.6 分配角色

```
POST /api/v1/auth/assign-role
```

### 1.7 修改密码

```
POST /api/v1/auth/change-password
Authorization: Bearer {token}
```

**功能说明：** 修改当前用户密码（需要验证旧密码）

**请求体：**
```json
{
  "old_password": "旧密码",
  "new_password": "新密码"
}
```

**字段说明：**
- `old_password`: 旧密码（6-72字符）
- `new_password`: 新密码（6-72字符，不能与旧密码相同）

**响应：**
```json
{
  "detail": "密码修改成功，请重新登录"
}
```

**注意事项：**
- 修改密码成功后，所有 Token 将失效，需要重新登录
- 新密码不能与旧密码相同

---

### 1.8 忘记密码

```
POST /api/v1/auth/forgot-password
```

**功能说明：** 发送验证码到手机号（用于重置密码）

**请求体：**
```json
{
  "phone": "13800138000"
}
```

**字段说明：**
- `phone`: 已注册的手机号

**响应：**
```json
{
  "detail": "验证码已发送"
}
```

**注意事项：**
- 验证码有效期为 5 分钟
- 仅向已注册的手机号发送验证码

---

### 1.9 重置密码

```
POST /api/v1/auth/reset-password
```

**功能说明：** 使用验证码重置密码

**请求体：**
```json
{
  "phone": "13800138000",
  "code": "123456",
  "new_password": "新密码"
}
```

**字段说明：**
- `phone`: 手机号
- `code`: 验证码（6位数字）
- `new_password`: 新密码（6-72字符）

**响应：**
```json
{
  "detail": "密码重置成功，请使用新密码登录"
}
```

**注意事项：**
- 验证码验证成功后，密码将被重置
- 重置成功后可以使用新密码登录

---

### 1.10 注销账号

```
POST /api/v1/auth/account/delete
Authorization: Bearer {token}
```

**功能说明：** 注销当前账号（软删除，无法恢复）

**请求体：**
```json
{
  "password": "当前密码",
  "confirmation": "DELETE"
}
```

**字段说明：**
- `password`: 当前密码（用于验证身份）
- `confirmation`: 确认文本，必须输入 "DELETE"

**响应：**
```json
{
  "detail": "账号已注销"
}
```

**注意事项：**
- 账号注销后无法恢复，请谨慎操作
- 注销后所有数据将被标记为删除
- 需要输入密码验证身份
- 需要输入 "DELETE" 确认操作

---

## 2. 学校管理模块

### 2.1 搜索学校

```
GET /api/v1/schools/search?keyword={keyword}
```

**查询参数：**
- `keyword`: 搜索关键词（学校名称）

---

## 3. 社团管理模块

### 3.1 检查社团是否存在

```
POST /api/v1/clubs/check
```

**请求体：**
```json
{
  "name": "计算机协会"
}
```

### 3.2 初始化社团（创建）

```
POST /api/v1/clubs/init
```

### 3.3 修改社团信息

```
PUT /api/v1/clubs/{club_id}
```

### 3.4 获取首页社团列表

```
GET /api/v1/clubs/home-list?school_code={code}&status={status}
```

### 3.5 获取社团详情

```
GET /api/v1/clubs/{club_id}
```

### 3.6 获取社团完整详情

```
GET /api/v1/clubs/{id}/detail
```

### 3.7 检查社团资料是否完善

```
GET /api/v1/clubs/{club_id}/profile-check
```

### 3.8 绑定用户到社团

```
POST /api/v1/clubs/{club_id}/bind-user
```

### 3.9 获取社团列表（分页、搜索）

```
GET /api/v1/clubs
```

**功能说明：** 获取社团列表，支持分页和多种筛选条件

**查询参数：**
- `school_code`: 学校标识码（可选）
- `status`: 社团状态（ACTIVE/INACTIVE/REVIEW，可选）
- `category`: 社团分类（可选）
- `keyword`: 搜索关键词（社团名称，可选）
- `page`: 页码（默认1）
- `page_size`: 每页数量（默认20，最大100）

**响应：**
```json
{
  "items": [
    {
      "id": 1,
      "school_name": "武汉大学",
      "name": "计算机协会",
      "logo_url": "https://...",
      "category": "技术",
      "description": "...",
      "status": "ACTIVE",
      "created_at": "2026-01-01 12:00:00"
    }
  ],
  "total": 100,
  "page": 1,
  "page_size": 20
}
```

---

### 3.10 审核社团

```
POST /api/v1/clubs/{club_id}/audit
Authorization: Bearer {token}
```

**功能说明：** 审核社团创建申请（管理员功能）

**请求体：**
```json
{
  "approved": true,
  "reason": "拒绝原因（approved=false 时必填）"
}
```

**字段说明：**
- `approved`: 是否通过审核
- `reason`: 拒绝原因（approved=false 时必填）

**响应：**
```json
{
  "detail": "社团审核完成"
}
```

---

### 3.11 获取社团成员列表

```
GET /api/v1/clubs/{club_id}/members
Authorization: Bearer {token}
```

**功能说明：** 获取社团所有成员及其角色

**响应：**
```json
{
  "items": [
    {
      "user_id": 1,
      "user_name": "张三",
      "user_phone": "13800138000",
      "role_id": 2,
      "role_name": "社团管理员",
      "club_id": 1,
      "joined_at": "2026-01-01 12:00:00"
    }
  ],
  "total": 10
}
```

---

### 3.12 更新成员角色

```
PUT /api/v1/clubs/{club_id}/members/{user_id}/role
Authorization: Bearer {token}
```

**功能说明：** 更新社团成员的角色

**请求体：**
```json
{
  "role_id": 3,
  "club_id": 1
}
```

**字段说明：**
- `role_id`: 新角色ID
- `club_id`: 社团ID（角色关联的社团）

**响应：**
```json
{
  "detail": "成员角色已更新"
}
```

---

### 3.13 移除社团成员

```
DELETE /api/v1/clubs/{club_id}/members/{user_id}
Authorization: Bearer {token}
```

**功能说明：** 将成员从社团中移除

**请求体：**
```json
{
  "reason": "移除原因（可选）"
}
```

**响应：**
```json
{
  "detail": "成员已移除"
}
```

---

### 3.14 获取社团统计数据

```
GET /api/v1/clubs/{club_id}/stats
Authorization: Bearer {token}
```

**功能说明：** 获取社团各项统计数据

**响应：**
```json
{
  "club_id": 1,
  "club_name": "计算机协会",
  "total_members": 50,
  "active_positions": 10,
  "active_recruitments": 2,
  "total_applications": 100,
  "total_interviews": 30,
  "pending_reviews": 5,
  "upcoming_interviews": 3
}
```

**字段说明：**
- `total_members`: 总成员数
- `active_positions`: 活跃岗位数
- `active_recruitments`: 活跃招新场次数
- `total_applications`: 总报名数
- `total_interviews`: 总面试数
- `pending_reviews`: 待审核报名数
- `upcoming_interviews`: 即将到来的面试数（未来7天）

---

## 4. 部门管理模块

### 4.1 获取社团部门列表

```
GET /api/v1/clubs/{club_id}/departments
```

### 4.2 创建部门

```
POST /api/v1/clubs/{club_id}/departments
Authorization: Bearer {token}
```

**请求体：**
```json
{
  "name": "技术部",
  "description": "负责技术开发"
}
```

### 4.3 更新部门

```
PUT /api/v1/clubs/{club_id}/departments/{dept_id}
Authorization: Bearer {token}
```

### 4.4 删除部门

```
DELETE /api/v1/clubs/{club_id}/departments/{dept_id}
Authorization: Bearer {token}
```

---

## 5. 岗位管理模块

### 5.1 获取社团岗位列表

```
GET /api/v1/clubs/{club_id}/positions
```

### 5.2 创建岗位

```
POST /api/v1/clubs/{club_id}/positions
Authorization: Bearer {token}
```

**请求体：**
```json
{
  "name": "前端开发",
  "department_id": 1,
  "description": "负责前端开发工作",
  "quota": 5
}
```

### 5.3 更新岗位

```
PUT /api/v1/clubs/{club_id}/positions/{position_id}
Authorization: Bearer {token}
```

### 5.4 删除岗位

```
DELETE /api/v1/clubs/{club_id}/positions/{position_id}
Authorization: Bearer {token}
```

---

## 6. 招新场次管理模块

### 6.1 获取招新场次列表

```
GET /api/v1/recruitment/sessions?club_id={club_id}&status={status}
```

### 6.2 创建招新场次

```
POST /api/v1/recruitment/sessions
```

**请求体：**
```json
{
  "club_id": 1,
  "name": "2026年春季招新",
  "description": "年度春季招新活动",
  "start_time": "2026-03-01T00:00:00",
  "end_time": "2026-03-31T23:59:59",
  "status": "ACTIVE"
}
```

### 6.3 获取招新场次详情

```
GET /api/v1/recruitment/sessions/{session_id}
```

### 6.4 更新招新场次

```
PUT /api/v1/recruitment/sessions/{session_id}
```

### 6.5 删除招新场次

```
DELETE /api/v1/recruitment/sessions/{session_id}
```

### 6.6 添加岗位到招新场次

```
POST /api/v1/recruitment/sessions/{session_id}/positions
```

**请求体：**
```json
{
  "position_id": 1,
  "quota": 10
}
```

### 6.7 更新岗位招聘配额

```
PUT /api/v1/recruitment/sessions/{session_id}/positions/{pos_id}
```

### 6.8 移除招新场次的岗位

```
DELETE /api/v1/recruitment/sessions/{session_id}/positions/{pos_id}
```

### 6.9 获取场次岗位列表

```
GET /api/v1/recruitment/sessions/{session_id}/positions
```

---

## 7. 报名管理模块

### 7.1 学生提交报名

```
POST /api/v1/signup/signup
Authorization: Bearer {token}
```

**请求体：**
```json
{
  "recruitment_session_id": 1,
  "position_ids": [1, 2],
  "self_intro": "我对编程充满热情"
}
```

### 7.2 获取我的报名列表

```
GET /api/v1/student/applications/my
Authorization: Bearer {token}
```

### 7.3 获取报名详情

```
GET /api/v1/student/applications/{application_id}
Authorization: Bearer {token}
```

### 7.4 更新报名申请

```
PUT /api/v1/student/applications/{application_id}
Authorization: Bearer {token}
```

### 7.5 取消报名申请

```
DELETE /api/v1/student/applications/{application_id}
Authorization: Bearer {token}
```

### 7.6 面试官 - 获取报名审核列表

```
GET /api/v1/signup/interviewer/signup/applications?recruitment_session_id={id}&status={status}
Authorization: Bearer {token}
```

### 7.7 社团管理员 - 获取报名审核列表

```
GET /api/v1/signup/admin/signup/applications?recruitment_session_id={id}&status={status}
Authorization: Bearer {token}
```

### 7.8 获取报名详情（管理员/面试官）

```
GET /api/v1/signup/admin/signup/applications/{signup_id}
Authorization: Bearer {token}
```

### 7.9 审核报名

```
POST /api/v1/signup/admin/signup/applications/{signup_id}/audit
Authorization: Bearer {token}
```

**请求体：**
```json
{
  "status": "APPROVED",
  "audit_reason": "符合要求"
}
```

---

### 7.10 上传报名附件

```
POST /api/v1/signup/signup/{signup_id}/attachments
Authorization: Bearer {token}
```

**功能说明：** 为报名添加附件（简历、作品集等）

**请求体：**
```json
{
  "file_type": "PDF",
  "file_name": "个人简历.pdf"
}
```

**字段说明：**
- `file_type`: 附件类型（PDF/IMG/DOC/OTHER）
- `file_name`: 文件名

**响应：**
```json
{
  "detail": "附件上传成功",
  "attachment_id": 1,
  "file_url": "https://..."
}
```

---

### 7.11 删除报名附件

```
DELETE /api/v1/signup/signup/attachments/{attachment_id}
Authorization: Bearer {token}
```

**功能说明：** 删除报名附件

**响应：**
```json
{
  "detail": "附件已删除"
}
```

---

### 7.12 设置报名自定义字段

```
POST /api/v1/signup/recruitment/{recruitment_session_id}/custom-fields
Authorization: Bearer {token}
```

**功能说明：** 为招新场次配置自定义报名字段（社团管理员）

**请求体：**
```json
{
  "recruitment_session_id": 1,
  "fields": [
    {
      "key": "experience",
      "label": "项目经验",
      "field_type": "text",
      "required": true,
      "placeholder": "请描述您的项目经验",
      "max_length": 500
    },
    {
      "key": "skills",
      "label": "技能特长",
      "field_type": "select",
      "required": false,
      "options": ["Python", "Java", "前端", "设计", "其他"]
    }
  ]
}
```

**字段类型：**
- `text`: 文本输入
- `number`: 数字输入
- `select`: 下拉选择
- `checkbox`: 多选框
- `date`: 日期选择

**响应：**
```json
{
  "detail": "自定义字段设置成功"
}
```

---

### 7.13 获取报名自定义字段

```
GET /api/v1/signup/recruitment/{recruitment_session_id}/custom-fields
```

**功能说明：** 获取招新场次的自定义字段配置（用于前端渲染报名表单）

**响应：**
```json
{
  "recruitment_session_id": 1,
  "fields": [
    {
      "key": "experience",
      "label": "项目经验",
      "field_type": "text",
      "required": true,
      "placeholder": "请描述您的项目经验",
      "max_length": 500
    }
  ]
}
```

---

### 7.14 导出报名数据

```
POST /api/v1/signup/recruitment/export-signups
Authorization: Bearer {token}
```

**功能说明：** 导出指定场次的报名数据（社团管理员）

**请求体：**
```json
{
  "recruitment_session_id": 1,
  "status": "APPROVED",
  "format": "xlsx"
}
```

**字段说明：**
- `recruitment_session_id`: 招新场次ID
- `status`: 状态筛选（可选）
- `format`: 导出格式（xlsx/csv）

**响应：**
```json
{
  "detail": "报名数据导出成功",
  "recruitment_session_id": 1,
  "total_count": 10,
  "data": [
    {
      "signup_id": 1,
      "user_name": "张三",
      "user_phone": "13800138000",
      "user_email": "example@email.com",
      "user_school": "武汉大学",
      "user_major": "计算机科学",
      "recruitment_session_name": "2024春季招新",
      "positions": "技术部/后端开发",
      "self_intro": "我对编程充满热情...",
      "custom_fields": {
        "experience": "有过项目经验"
      },
      "status": "APPROVED",
      "audit_time": "2026-03-05 10:00:00",
      "audit_reason": null,
      "created_at": "2026-03-01 15:30:00"
    }
  ]
}
```

---

## 8. 面试管理模块

### 8.1 面试场次管理

#### 8.1.1 创建面试场次

```
POST /api/v1/interview/sessions?club_id={club_id}
Authorization: Bearer {token}
```

**请求体：**
```json
{
  "recruitment_session_id": 1,
  "name": "第一轮面试",
  "description": "技术面试",
  "start_time": "2026-03-15T09:00:00",
  "end_time": "2026-03-15T18:00:00",
  "place": "学生活动中心201",
  "status": "DRAFT"
}
```

#### 8.1.2 获取面试场次列表

```
GET /api/v1/interview/sessions?club_id={club_id}&recruitment_session_id={id}&status={status}
```

#### 8.1.3 获取面试场次详情

```
GET /api/v1/interview/sessions/{session_id}
```

#### 8.1.4 更新面试场次

```
PUT /api/v1/interview/sessions/{session_id}
```

#### 8.1.5 删除面试场次

```
DELETE /api/v1/interview/sessions/{session_id}
```

### 8.2 面试官分配

#### 8.2.1 获取可分配的面试官列表

```
GET /api/v1/interview/clubs/{club_id}/assignable-interviewers
```

#### 8.2.2 为场次分配面试官

```
POST /api/v1/interview/sessions/{session_id}/interviewers
```

**请求体：**
```json
{
  "interviewer_id": 1
}
```

#### 8.2.3 获取场次的面试官列表

```
GET /api/v1/interview/sessions/{session_id}/interviewers
```

### 8.3 候选人排期管理

#### 8.3.1 生成候选人排期

```
POST /api/v1/interview/sessions/{session_id}/generate-candidates
```

**请求体：**
```json
{
  "signup_application_ids": [1, 2, 3],
  "time_slot_duration": 60,
  "start_time": "2026-03-15T09:00:00",
  "end_time": "2026-03-15T18:00:00"
}
```

#### 8.3.2 获取场次的候选人列表

```
GET /api/v1/interview/sessions/{session_id}/candidates?status={status}
```

#### 8.3.3 获取候选人详情

```
GET /api/v1/interview/candidates/{candidate_id}
```

### 8.4 评分模板管理

#### 8.4.1 获取评分模板列表

```
GET /api/v1/interview/score-templates?club_id={club_id}
Authorization: Bearer {token}
```

#### 8.4.2 获取模板的评分项

```
GET /api/v1/interview/score-templates/{template_id}/items
Authorization: Bearer {token}
```

#### 8.4.3 获取场次的评分项

```
GET /api/v1/interview/sessions/{session_id}/score-items
```

#### 8.4.4 添加评分项到场次

```
POST /api/v1/interview/sessions/{session_id}/score-items
```

#### 8.4.5 设置场次评分模板

```
POST /api/v1/interview/sessions/{session_id}/score-template
Authorization: Bearer {token}
```

**请求体（使用模板）：**
```json
{
  "template_id": 1
}
```

**请求体（自定义评分项）：**
```json
{
  "custom_items": [
    {
      "name": "专业能力",
      "description": "考察专业知识和技能",
      "max_score": 100,
      "weight": 1,
      "order_no": 1
    }
  ]
}
```

### 8.5 面试记录与评分

#### 8.5.1 更新面试记录

```
PUT /api/v1/interview/records/{record_id}
Authorization: Bearer {token}
```

**请求体：**
```json
{
  "summary": "面试表现良好",
  "record_text": "手写记录内容",
  "recording_url": "https://example.com/recording.mp3",
  "face_image_url": "https://example.com/face.jpg"
}
```

#### 8.5.2 添加单项评分

```
POST /api/v1/interview/records/{record_id}/scores
Authorization: Bearer {token}
```

**请求体：**
```json
{
  "score_item_id": 1,
  "score": 85,
  "remark": "表现不错"
}
```

#### 8.5.3 获取评分列表

```
GET /api/v1/interview/records/{record_id}/scores
```

### 8.6 面试结果与录取

#### 8.6.1 获取场次面试结果汇总

```
GET /api/v1/interview/sessions/{session_id}/results-summary
Authorization: Bearer {token}
```

#### 8.6.2 更新录取结果

```
PUT /api/v1/interview/candidates/{candidate_id}/admission
Authorization: Bearer {token}
```

**请求体：**
```json
{
  "result": "PASS",
  "department_id": 2,
  "position_id": 5,
  "remark": "面试表现优秀"
}
```

### 8.7 面试官任务

#### 8.7.1 获取当前面试官的任务列表

```
GET /api/v1/interview/my-tasks?club_id={club_id}
Authorization: Bearer {token}
```

---

### 8.8 面试功能增强

#### 8.8.1 批量分配候选人给面试官

```
POST /api/v1/interview/sessions/{session_id}/batch-assign
Authorization: Bearer {token}
```

**功能说明：** 将多个候选人批量分配给多个面试官

**请求体：**
```json
{
  "candidate_ids": [1, 2, 3],
  "interviewer_ids": [10, 20]
}
```

**字段说明：**
- `candidate_ids`: 候选人ID列表
- `interviewer_ids`: 面试官 user_role ID列表

**响应：**
```json
{
  "detail": "候选人分配完成",
  "assigned_count": 2,
  "conflict_count": 1,
  "conflicts": [
    {
      "candidate_id": 1,
      "interviewer_id": 10,
      "interviewer_name": "张三",
      "conflict_session": "第二场面试"
    }
  ]
}
```

---

#### 8.8.2 检测面试时间冲突

```
POST /api/v1/interview/sessions/check-conflict
Authorization: Bearer {token}
```

**功能说明：** 检测指定时间段内面试官或候选人的时间冲突

**请求体：**
```json
{
  "start_time": "2026-03-15T10:00:00",
  "end_time": "2026-03-15T12:00:00",
  "exclude_session_id": 5,
  "interviewer_ids": [10, 20],
  "candidate_user_ids": [100, 200]
}
```

**字段说明：**
- `start_time`: 开始时间
- `end_time`: 结束时间
- `exclude_session_id`: 排除的场次ID（编辑时使用）
- `interviewer_ids`: 面试官ID列表（可选）
- `candidate_user_ids`: 候选人用户ID列表（可选）

**响应：**
```json
{
  "has_conflict": true,
  "conflicts": [
    {
      "type": "INTERVIEWER",
      "name": "张三",
      "session_name": "第二场面试",
      "conflict_time": "2026-03-15 09:00 - 2026-03-15 11:00"
    }
  ]
}
```

**冲突类型：**
- `INTERVIEWER`: 面试官时间冲突
- `CANDIDATE`: 候选人时间冲突

---

#### 8.8.3 发送面试提醒

```
POST /api/v1/interview/candidates/{candidate_id}/send-reminder
Authorization: Bearer {token}
```

**功能说明：** 向候选人发送面试提醒通知

**响应：**
```json
{
  "detail": "面试提醒已发送"
}
```

**通知内容包含：**
- 面试时间
- 面试地点
- 相关说明

---

#### 8.8.4 导出面试记录

```
POST /api/v1/interview/sessions/{session_id}/export-records
Authorization: Bearer {token}
```

**功能说明：** 导出指定场次的面试记录

**请求体：**
```json
{
  "format": "xlsx"
}
```

**字段说明：**
- `format`: 导出格式（xlsx/csv）

**响应：**
```json
{
  "message": "面试记录导出成功",
  "session_id": 1,
  "session_name": "第一轮面试",
  "total_records": 10,
  "data": [...]
}
```

---

#### 8.8.5 获取面试场次统计

```
GET /api/v1/interview/sessions/{session_id}/stats
Authorization: Bearer {token}
```

**功能说明：** 获取面试场次的详细统计数据

**响应：**
```json
{
  "session_id": 1,
  "session_name": "第一轮面试",
  "total_candidates": 30,
  "completed_candidates": 20,
  "pending_candidates": 8,
  "cancelled_candidates": 2,
  "average_score": 85.5,
  "pass_count": 15,
  "reject_count": 4,
  "waitlist_count": 1
}
```

**统计字段说明：**
- `total_candidates`: 候选人总数
- `completed_candidates`: 已完成面试数
- `pending_candidates`: 待面试数
- `cancelled_candidates`: 取消面试数
- `average_score`: 平均得分
- `pass_count`: 录用人数
- `reject_count`: 拒绝人数
- `waitlist_count`: 候补人数

---

## 9. 学生端模块

### 9.1 报名管理

#### 9.1.1 创建报名申请

```
POST /api/v1/student/applications
Authorization: Bearer {token}
```

#### 9.1.2 获取我的报名列表

```
GET /api/v1/student/applications/my
Authorization: Bearer {token}
```

#### 9.1.3 获取报名详情

```
GET /api/v1/student/applications/{application_id}
Authorization: Bearer {token}
```

#### 9.1.4 更新报名申请

```
PUT /api/v1/student/applications/{application_id}
Authorization: Bearer {token}
```

#### 9.1.5 取消报名申请

```
DELETE /api/v1/student/applications/{application_id}
Authorization: Bearer {token}
```

### 9.2 面试管理

#### 9.2.1 获取我的面试列表

```
GET /api/v1/student/interviews/my
Authorization: Bearer {token}
```

#### 9.2.2 获取面试详情

```
GET /api/v1/student/interviews/{interview_id}
Authorization: Bearer {token}
```

#### 9.2.3 确认/拒绝面试

```
PUT /api/v1/student/interviews/{interview_id}/confirmation
Authorization: Bearer {token}
```

**请求体：**
```json
{
  "confirmation_status": "CONFIRMED"
}
```

#### 9.2.4 获取面试结果

```
GET /api/v1/student/interviews/{interview_id}/result
Authorization: Bearer {token}
```

### 9.3 通知管理

#### 9.3.1 获取通知列表

```
GET /api/v1/student/notifications?unread_only={true|false}
Authorization: Bearer {token}
```

#### 9.3.2 标记通知为已读

```
PUT /api/v1/student/notifications/{notification_id}/read
Authorization: Bearer {token}
```

#### 9.3.3 标记所有通知为已读

```
PUT /api/v1/student/notifications/read-all
Authorization: Bearer {token}
```

#### 9.3.4 获取未读通知数量

```
GET /api/v1/student/notifications/count
Authorization: Bearer {token}
```

### 9.4 工单管理

#### 9.4.1 创建工单

```
POST /api/v1/student/tickets
Authorization: Bearer {token}
```

**请求体：**
```json
{
  "title": "面试时间冲突",
  "content": "我的两场面试时间冲突了",
  "category": "INTERVIEW"
}
```

#### 9.4.2 获取我的工单列表

```
GET /api/v1/student/tickets/my
Authorization: Bearer {token}
```

#### 9.4.3 获取工单详情

```
GET /api/v1/student/tickets/{ticket_id}
Authorization: Bearer {token}
```

#### 9.4.4 添加工单回复

```
POST /api/v1/student/tickets/{ticket_id}/messages
Authorization: Bearer {token}
```

**请求体：**
```json
{
  "content": "补充说明"
}
```

### 9.5 个人中心

#### 9.5.1 获取学生个人资料

```
GET /api/v1/student/students/profile
Authorization: Bearer {token}
```

#### 9.5.2 更新学生个人资料

```
PUT /api/v1/student/students/profile
Authorization: Bearer {token}
```

**请求体：**
```json
{
  "name": "张三",
  "student_no": "2021001",
  "major": "计算机科学与技术",
  "school_code": "WHU"
}
```

#### 9.5.3 获取报名统计

```
GET /api/v1/student/students/applications/stats
Authorization: Bearer {token}
```

---

## 数据模型

### InterviewSession（面试场次）

```json
{
  "id": number,
  "club_id": number,
  "recruitment_session_id": number,
  "name": string,
  "description": string,
  "start_time": string,
  "end_time": string,
  "place": string,
  "status": "DRAFT | OPEN | CLOSED",
  "created_by": number,
  "created_at": string,
  "updated_at": string
}
```

### InterviewCandidate（面试候选人）

```json
{
  "id": number,
  "session_id": number,
  "signup_session_id": number,
  "candidate_user_id": number,
  "user_name": string,
  "user_phone": string,
  "position_name": string,
  "department_name": string,
  "planned_start_time": string,
  "planned_end_time": string,
  "actual_start_time": string,
  "actual_end_time": string,
  "status": "SCHEDULED | CONFIRMED | CANCELLED | COMPLETED | NO_SHOW",
  "final_score": number,
  "created_at": string
}
```

### SignupSession（报名记录）

```json
{
  "id": number,
  "user_id": number,
  "recruitment_session_id": number,
  "self_intro": string,
  "status": "PENDING | APPROVED | REJECTED",
  "audit_user_id": number,
  "audit_time": string,
  "audit_reason": string,
  "created_at": string,
  "updated_at": string
}
```

---

## 错误码说明

| HTTP状态码 | 说明 |
|-----------|------|
| 200 | 请求成功 |
| 201 | 创建成功 |
| 204 | 删除成功（无响应体） |
| 400 | 请求参数错误 |
| 401 | 未授权 |
| 403 | 无权限访问 |
| 404 | 资源不存在 |
| 409 | 资源冲突 |
| 422 | 参数验证失败 |
| 500 | 服务器内部错误 |

---

## 更新日志

| 版本 | 日期 | 说明 |
|------|------|------|
| 1.0.0 | 2026-01-05 | 初始版本 |
| 1.5.0 | 2026-01-05 | 完成面试管理、报名管理等核心功能 |
| 2.0.0 | 2026-01-10 | 删除已废弃的admin和interviewer模块，统一路由前缀为/api/v1 |

---

## 接口实现状态说明

### ✅ 已实现的模块

- 用户认证模块
- 学校管理模块
- 社团管理模块
- 部门管理模块
- 岗位管理模块
- 招新场次管理模块
- 报名管理模块
- 面试管理模块
- 学生端模块

### 🔄 已删除的模块

- **管理员模块** (admin.py) - 功能已整合到其他模块
- **面试官端模块** (interviewer.py) - 功能已整合到其他模块

### ⚠️ 重要变更

1. **路由前缀统一**：所有接口统一使用 `/api/v1` 作为前缀
2. **删除的接口**：
   - `POST /api/auth/revoke-role` - 已删除
   - `GET /api/admin/users/search` - 已删除
   - `POST /api/admin/clubs/{club_id}/invite-interviewer` - 已删除
   - `GET /api/admin/clubs/{club_id}/interviewers` - 已删除
   - `GET /api/admin/dashboard` - 已删除
   - `GET /api/interviewer/invitations` - 已删除
   - `POST /api/interviewer/invitations/{id}/accept` - 已删除
   - `POST /api/interviewer/invitations/{id}/reject` - 已删除
   - `GET /api/interviewer/recruitment-sessions/{id}/stats` - 已删除
   - 以及其他已删除的面试官邀请相关接口

3. **面试管理模块变更**：
   - 删除了手动创建候选人的接口
   - 删除了开始面试/创建面试记录的接口
   - 删除了获取面试记录详情的接口
   - 删除了提交评分的接口
   - 删除了修改评分的接口
   - 删除了获取候选人录取结果的接口
   - 删除了移除面试官的接口
   - 删除了移除评分项的接口
   - 删除了设置评分项列表的接口
   - 删除了上传录音和照片的接口
   - 删除了发送面试通知和确认面试的接口

---

## 权限说明

### 角色类型

- **STUDENT**: 学生
- **CLUB_ADMIN**: 社团管理员
- **INTERVIEWER**: 面试官

### 权限矩阵

| 功能 | 学生 | 社团管理员 | 面试官 |
|------|------|-----------|--------|
| 报名管理 | ✅ 查看/创建/更新/删除 | ✅ 查看/审核 | ✅ 查看 |
| 面试管理 | ✅ 查看自己的面试 | ✅ 完整权限 | ✅ 查看任务、评分 |
| 社团管理 | ❌ | ✅ 完整权限 | ❌ |
| 部门/岗位管理 | ❌ | ✅ 完整权限 | ❌ |
