# 社团面试系统 - API 接口文档

本文档记录了前端项目中使用的所有后端 API 接口。

---

## 目录

- [认证模块 (auth)](#认证模块-auth)
- [报名申请模块 (application)](#报名申请模块-application)
- [社团管理模块 (clubs)](#社团管理模块-clubs)
- [面试管理模块 (interview)](#面试管理模块-interview)
- [通知模块 (notification)](#通知模块-notification)
- [招新管理模块 (recruitment)](#招新管理模块-recruitment)
- [学校模块 (school)](#学校模块-school)
- [评分模块 (score)](#评分模块-score)
- [统计模块 (statistics)](#统计模块-statistics)
- [学生模块 (student)](#学生模块-student)
- [工单模块 (ticket)](#工单模块-ticket)

---

## 认证模块 (auth)

### 1. 发送验证码

**接口**: `POST /api/auth/send-code`

**请求参数**:
```typescript
{
  phone: string          // 手机号
  scene: 'REGISTER' | 'LOGIN'  // 场景类型
}
```

**响应**:
```typescript
{
  message: string        // 提示信息
  dev_code: string | null  // 开发环境直接返回的验证码
}
```

---

### 2. 用户注册

**接口**: `POST /api/auth/register`

**请求参数**:
```typescript
{
  phone: string          // 手机号
  code: string           // 验证码
}
```

**响应**:
```typescript
{
  access_token: string   // 访问令牌
  token_type: string     // 令牌类型
}
```

---

### 3. 用户登录

**接口**: `POST /api/auth/login`

**请求参数**:
```typescript
{
  phone: string          // 手机号
  password: string       // 密码
}
```

**响应**:
```typescript
{
  access_token: string   // 访问令牌
  token_type: string     // 令牌类型
}
```

---

### 4. 获取当前用户信息

**接口**: `GET /api/auth/me`

**响应**:
```typescript
{
  id: number
  phone: string
  name: string | null
  status: number
  is_initialized: boolean
  roles: UserRoleInfo[]
  school_code?: string | null
  school_name?: string | null
}

// UserRoleInfo
{
  id: number
  code: string           // CLUB_ADMIN | INTERVIEWER | STUDENT
  name: string
  club_id: number | null
}
```

---

### 5. 初始化账号

**接口**: `POST /api/auth/init`

**请求参数**:
```typescript
{
  password: string
  name: string
  id_card_no: string
  school_code: string
  major: string
  student_no: string
  role: string           // CLUB_ADMIN | INTERVIEWER | STUDENT
  club_name?: string     // 社团管理员必填
  email?: string
  avatar_url?: string
}
```

**响应**:
```typescript
{
  detail: string         // 初始化结果描述
}
```

---

### 6. 分配角色

**接口**: `POST /api/auth/assign-role`

**请求参数**:
```typescript
{
  user_id: number
  role_id: number
  club_id?: number | null
}
```

**响应**:
```typescript
{
  detail: string
  user_role: {
    id: number
    user_id: number
    role_id: number
    club_id: number | null
  }
}
```

---

### 7. 社团管理员创建社团

**接口**: `POST /api/clubs/init`

**请求参数**:
```typescript
{
  club_name: string
  school_code: string
}
```

**响应**:
```typescript
{
  detail: string
  club_id: number
  is_new: boolean        // 是否为新创建的社团
}
```

---

## 报名申请模块 (application)

### 1. 提交报名（学生端）

**接口**: `POST /api/student/signup/applications`

**请求参数**:
```typescript
{
  recruitment_session_id: number
  position_ids: number[]
  self_intro?: string
}
```

**响应**:
```typescript
{
  signup_id: number
  status: string
}
```

---

### 2. 获取我的报名列表（学生端）

**接口**: `GET /api/student/signup/applications`

**查询参数**:
```typescript
{
  recruitment_session_id?: number
  status?: 'PENDING' | 'APPROVED' | 'REJECTED'
  page?: number
  page_size?: number
}
```

**响应**:
```typescript
{
  items: SignupApplication[]
  total: number
}

// SignupApplication
{
  id: number
  user_id: number
  recruitment_session_id: number
  self_intro: string | null
  status: 'PENDING' | 'APPROVED' | 'REJECTED'
  audit_user_id: number | null
  audit_time: string | null
  audit_reason: string | null
  created_at: string
  updated_at: string
  items: SignupItem[]
  attachments: any[]
  user_name?: string
  user_phone?: string
  user_email?: string
  session_name?: string
}

// SignupItem
{
  id: number
  signup_session_id: number
  department_id: number | null
  position_id: number
  department_name?: string
  position_name?: string
}
```

---

### 3. 获取报名审核列表（管理员端）

**接口**: `GET /api/admin/signup/applications`

**查询参数**:
```typescript
{
  recruitment_session_id: number
  status?: 'PENDING' | 'APPROVED' | 'REJECTED'
  page?: number
  page_size?: number
}
```

**响应**: 同上

---

### 4. 获取报名详情（管理员端）

**接口**: `GET /api/admin/signup/applications/{id}`

**响应**: `SignupApplication`

---

### 5. 审核报名（管理员端）

**接口**: `POST /api/admin/signup/applications/{id}/audit`

**请求参数**:
```typescript
{
  status: 'APPROVED' | 'REJECTED'
  reason?: string
}
```

**响应**:
```typescript
{
  detail: string
  signup_id: number
  new_status: string
}
```

---

### 6. 获取报名列表（面试官端）

**接口**: `GET /api/interviewer/signup/applications`

**查询参数**: 同管理员端

**响应**: 同上

---

### 7. 获取报名详情（面试官端）

**接口**: `GET /api/interviewer/signup/applications/{id}`

**响应**: `SignupApplication`

---

## 社团管理模块 (clubs)

### 1. 检查社团资料完整性

**接口**: `GET /api/clubs/{clubId}/profile-check`

**响应**:
```typescript
{
  club_id: number
  is_complete: boolean
  missing_fields: string[]
}
```

---

### 2. 检查社团是否存在

**接口**: `POST /api/clubs/check`

**请求参数**:
```typescript
{
  club_name: string
  school_code: string
}
```

**响应**:
```typescript
{
  exists: boolean
  club_id: number | null
  message: string
}
```

---

### 3. 绑定用户到社团

**接口**: `POST /api/clubs/{clubId}/bind-user`

**请求参数**:
```typescript
{
  user_id: number
  role_code: string      // INTERVIEWER | CLUB_ADMIN
}
```

---

### 4. 获取社团详情

**接口**: `GET /api/clubs/{clubId}`

**响应**:
```typescript
{
  id: number
  school_name: string
  name: string
  logo_url: string
  category: string
  description: string | null
  cert_file_url: string | null
  status: string
  created_at: string
  recruiting_status?: 'RECRUITING' | 'NO_RECRUITMENT'
}
```

---

### 5. 获取学校社团列表（首页）

**接口**: `GET /api/clubs/home-list`

**查询参数**:
```typescript
{
  school_code: string
  status?: string
}
```

**响应**:
```typescript
{
  id: number
  name: string
  logo_url: string
  description: string | null
  category: string
  school_name: string
  status: string
  recruiting_status: 'RECRUITING' | 'NO_RECRUITMENT'
}[]
```

---

### 6. 获取社团详情页数据（扁平结构）

**接口**: `GET /api/clubs/{clubId}/detail`

**响应**:
```typescript
{
  // ...社团基本信息
  departments: Department[]
  positions: Position[]
  recruitment_sessions: any[]
}

// Department
{
  id: number
  club_id: number
  name: string
  description: string | null
  created_at: string
  updated_at: string
}

// Position
{
  id: number
  club_id: number
  department_id: number | null
  name: string
  description: string | null
  requirement: string | null
  created_at: string
  updated_at: string
}
```

---

### 7. 更新社团信息

**接口**: `PUT /api/clubs/{clubId}`

**请求参数** (JSON):
```typescript
{
  name?: string
  category?: string
  description?: string
}
```

**请求参数** (FormData - 包含文件时):
```typescript
{
  name?: string
  category?: string
  description?: string
  logo?: File
  cert_file?: File
}
```

---

### 8. 获取部门列表

**接口**: `GET /api/clubs/{clubId}/departments`

**响应**: `Department[]`

---

### 9. 创建部门

**接口**: `POST /api/clubs/{clubId}/departments`

**请求参数**:
```typescript
{
  name: string
  description?: string
}
```

**响应**: `Department`

---

### 10. 更新部门

**接口**: `PUT /api/clubs/{clubId}/departments/{deptId}`

**请求参数**:
```typescript
{
  name?: string
  description?: string
}
```

**响应**: `Department`

---

### 11. 删除部门

**接口**: `DELETE /api/clubs/{clubId}/departments/{deptId}`

---

### 12. 获取岗位列表

**接口**: `GET /api/clubs/{clubId}/positions`

**查询参数**:
```typescript
{
  department_id?: number
}
```

**响应**: `Position[]`

---

### 13. 创建岗位

**接口**: `POST /api/clubs/{clubId}/positions`

**请求参数**:
```typescript
{
  department_id?: number
  name: string
  description?: string
  requirement?: string
}
```

**响应**: `Position`

---

### 14. 更新岗位

**接口**: `PUT /api/clubs/{clubId}/positions/{posId}`

**请求参数**:
```typescript
{
  name?: string
  description?: string
  requirement?: string
}
```

**响应**: `Position`

---

### 15. 删除岗位

**接口**: `DELETE /api/clubs/{clubId}/positions/{posId}`

---

## 面试管理模块 (interview)

### 1. 获取面试场次列表

**接口**: `GET /api/interview/sessions`

**查询参数**:
```typescript
{
  club_id?: number
  recruitment_session_id?: number
  status?: 'DRAFT' | 'OPEN' | 'CLOSED'
}
```

**响应**:
```typescript
{
  id: number
  club_id: number
  recruitment_session_id: number | null
  name: string
  description: string | null
  start_time: string
  end_time: string
  place: string | null
  status: 'DRAFT' | 'OPEN' | 'CLOSED'
  created_by: number
  created_at: string
  updated_at: string
  interviewer_count?: number
  candidate_count?: number
}[]
```

---

### 2. 获取面试场次详情

**接口**: `GET /api/interview/sessions/{id}`

**响应**: `InterviewSession`

---

### 3. 创建面试场次

**接口**: `POST /api/interview/sessions`

**查询参数**: `club_id: number`

**请求参数**:
```typescript
{
  recruitment_session_id?: number
  name: string
  description?: string
  start_time: string
  end_time: string
  place?: string
  status?: 'DRAFT' | 'OPEN' | 'CLOSED'
}
```

**响应**: `InterviewSession`

---

### 4. 更新面试场次

**接口**: `PUT /api/interview/sessions/{id}`

**请求参数**:
```typescript
{
  name?: string
  description?: string
  start_time?: string
  end_time?: string
  place?: string
  status?: 'DRAFT' | 'OPEN' | 'CLOSED'
}
```

**响应**: `InterviewSession`

---

### 5. 删除面试场次

**接口**: `DELETE /api/interview/sessions/{id}`

---

### 6. 获取可分配的面试官列表

**接口**: `GET /api/interview/clubs/{clubId}/assignable-interviewers`

**响应**:
```typescript
{
  id: number
  user_id: number
  name: string
  phone?: string
  email?: string
  role: 'CLUB_ADMIN' | 'INTERVIEWER'
}[]
```

---

### 7. 为场次分配面试官

**接口**: `POST /api/interview/sessions/{sessionId}/interviewers`

**请求参数**:
```typescript
{
  interviewer_id: number
}
```

---

### 8. 获取场次的面试官列表

**接口**: `GET /api/interview/sessions/{sessionId}/interviewers`

**响应**:
```typescript
{
  id: number
  user_id: number
  club_id: number
  name: string
  phone?: string
  email?: string
}[]
```

---

### 9. 生成候选人排期

**接口**: `POST /api/interview/sessions/{sessionId}/generate-candidates`

**请求参数**:
```typescript
{
  signup_application_ids?: number[]
  time_slot_duration?: number      // 默认60分钟
  start_time?: string
  end_time?: string
}
```

**响应**:
```typescript
{
  id: number
  session_id: number
  signup_application_id: number
  user_id: number
  user_name: string
  user_phone?: string
  position_id: number
  position_name?: string
  department_id?: number
  department_name?: string
  planned_start_time: string
  planned_end_time: string
  actual_start_time: string | null
  actual_end_time: string | null
  status: 'SCHEDULED' | 'CONFIRMED' | 'CANCELLED' | 'COMPLETED' | 'NO_SHOW'
  final_score: number | null
  created_at: string
}[]
```

---

### 10. 获取场次的候选人列表

**接口**: `GET /api/interview/sessions/{sessionId}/candidates`

**查询参数**:
```typescript
{
  status?: 'SCHEDULED' | 'CONFIRMED' | 'CANCELLED' | 'COMPLETED' | 'NO_SHOW'
}
```

**响应**: `InterviewCandidate[]`

---

### 11. 获取候选人详情

**接口**: `GET /api/interview/candidates/{candidateId}`

**响应**:
```typescript
{
  ...InterviewCandidate
  application?: any
}
```

---

### 12. 获取评分模板列表

**接口**: `GET /api/score-templates`

**查询参数**:
```typescript
{
  club_id?: number
}
```

**响应**:
```typescript
{
  id: number
  club_id: number
  name: string
  description?: string
  is_default: boolean
  created_at: string
  updated_at: string
}[]
```

---

### 13. 获取评分模板的评分项

**接口**: `GET /api/score-templates/{templateId}/items`

**响应**:
```typescript
{
  id: number
  template_id: number | null
  session_id: number | null
  title: string
  description?: string
  max_score: number
  weight: number
  sort_order: number
}[]
```

---

### 14. 获取场次的评分项

**接口**: `GET /api/interview/sessions/{sessionId}/score-items`

**响应**: `ScoreItem[]`

---

### 15. 设置场次评分模板

**接口**: `POST /api/interview/sessions/{sessionId}/score-template`

**请求参数**:
```typescript
{
  template_id?: number
  custom_items?: {
    title: string
    description?: string
    max_score: number
    weight: number
  }[]
}
```

**响应**: `ScoreItem[]`

---

### 16. 获取面试记录

**接口**: `GET /api/interview/records/{recordId}`

**响应**:
```typescript
{
  id: number
  candidate_id: number
  interviewer_id: number
  recording_url?: string
  transcript?: string
  notes?: string
  total_score?: number
  status: 'PENDING' | 'SCORED'
  created_at: string
  updated_at: string
  scores?: InterviewScore[]
}
```

---

### 17. 开始面试（创建面试记录）

**接口**: `POST /api/interview/records/{candidateId}/start`

**响应**: `InterviewRecord`

---

### 18. 更新面试记录

**接口**: `PUT /api/interview/records/{recordId}`

**请求参数**:
```typescript
{
  notes?: string
  transcript?: string
}
```

**响应**: `InterviewRecord`

---

### 19. 提交评分

**接口**: `POST /api/interview/records/{recordId}/score`

**请求参数**:
```typescript
{
  scores: {
    score_item_id: number
    score: number
    notes?: string
  }[]
  notes?: string
}
```

**响应**: `InterviewRecord`

---

### 20. 修改评分

**接口**: `POST /api/interview/records/{recordId}/rescore`

**请求参数**: 同提交评分

**响应**: `InterviewRecord`

---

### 21. 获取场次面试结果汇总

**接口**: `GET /api/interview/sessions/{sessionId}/results`

**响应**:
```typescript
{
  candidate_id: number
  user_name: string
  user_phone?: string
  position_name?: string
  department_name?: string
  records: {
    record_id: number
    interviewer_name: string
    total_score: number
    notes?: string
  }[]
  average_score: number
  final_score: number
}[]
```

---

### 22. 设置候选人录取结果

**接口**: `POST /api/interview/candidates/{candidateId}/decision`

**请求参数**:
```typescript
{
  decision: 'PASS' | 'REJECT' | 'WAITLIST'
  position_id?: number
  notes?: string
}
```

---

### 23. 获取面试官任务列表

**接口**: `GET /api/interview/my-tasks`

**响应**: `InterviewCandidate[]`

---

### 24. 上传面试录音

**接口**: `POST /api/interview/records/{recordId}/upload-recording`

**请求参数**: FormData `{ file: File }`

**响应**:
```typescript
{
  url: string
}
```

---

### 25. 上传候选人照片

**接口**: `POST /api/interview/records/{recordId}/upload-face`

**请求参数**: FormData `{ file: File }`

**响应**:
```typescript
{
  url: string
}
```

---

### 26. 发送面试通知

**接口**: `POST /api/interview/sessions/{sessionId}/send-notification`

**请求参数**:
```typescript
{
  candidate_ids?: number[]
  auto_send?: boolean
}
```

---

### 27. 候选人确认/拒绝面试

**接口**: `PUT /api/interviews/{interviewId}/confirmation`

**请求参数**:
```typescript
{
  status: 'CONFIRMED' | 'REJECTED'
}
```

---

### 28. 获取学生的面试记录列表

**接口**: `GET /api/student/interviews`

**查询参数**:
```typescript
{
  status?: 'SCHEDULED' | 'CONFIRMED' | 'CANCELLED' | 'COMPLETED' | 'NO_SHOW'
  session_id?: number
}
```

**响应**: `InterviewCandidate[]`

---

### 29. 获取学生的面试记录详情

**接口**: `GET /api/student/interviews/{candidateId}`

**响应**:
```typescript
{
  ...InterviewCandidate
  session?: InterviewSession
  application?: SignupApplication
}
```

---

## 通知模块 (notification)

### 1. 获取通知列表

**接口**: `GET /api/notifications`

**查询参数**:
```typescript
{
  page?: number
  pageSize?: number
  isRead?: boolean
}
```

**响应**:
```typescript
{
  id: number
  title: string
  content: string
  type: 'application' | 'interview' | 'result' | 'system'
  isRead: boolean
  relatedId?: number
  createdAt: string
}[]
```

---

### 2. 获取未读通知数量

**接口**: `GET /api/notifications/unread-count`

---

### 3. 标记通知为已读

**接口**: `PUT /notifications/{id}/read`

---

### 4. 标记所有通知为已读

**接口**: `PUT /api/notifications/read-all`

---

## 招新管理模块 (recruitment)

### 1. 创建招新场次

**接口**: `POST /api/recruitment/sessions`

**查询参数**: `club_id: number`

**请求参数**:
```typescript
{
  name: string
  description?: string
  start_time: string
  end_time: string
  max_candidates?: number
}
```

**响应**:
```typescript
{
  id: number
  club_id: number
  name: string
  description: string | null
  start_time: string
  end_time: string
  max_candidates: number
  status: 'DRAFT' | 'PUBLISHED' | 'CLOSED'
  created_by: number
  created_at: string
  updated_at: string
  positions?: SessionPosition[]
}
```

---

### 2. 获取招新场次列表

**接口**: `GET /api/recruitment/sessions`

**查询参数**:
```typescript
{
  club_id?: number
  status?: 'DRAFT' | 'PUBLISHED' | 'CLOSED'
}
```

**响应**: `RecruitmentSession[]`

---

### 3. 获取招新场次详情

**接口**: `GET /api/recruitment/sessions/{id}`

**响应**: `RecruitmentSession`

---

### 4. 更新招新场次

**接口**: `PUT /api/recruitment/sessions/{id}`

**请求参数**:
```typescript
{
  name?: string
  description?: string
  start_time?: string
  end_time?: string
  max_candidates?: number
  status?: 'DRAFT' | 'PUBLISHED' | 'CLOSED'
}
```

**响应**: `RecruitmentSession`

---

### 5. 删除招新场次

**接口**: `DELETE /api/recruitment/sessions/{id}`

---

### 6. 关联岗位到招新场次

**接口**: `POST /api/recruitment/sessions/{sessionId}/positions`

**请求参数**:
```typescript
{
  position_id: number
  recruit_quota: number
}
```

**响应**:
```typescript
{
  id: number
  session_id: number
  position_id: number
  position_name: string
  position_description: string | null
  position_requirement: string | null
  recruit_quota: number
}
```

---

### 7. 更新招新场次的岗位配额

**接口**: `PUT /api/recruitment/sessions/{sessionId}/positions/{positionId}`

**请求参数**:
```typescript
{
  recruit_quota: number
}
```

**响应**: `SessionPosition`

---

### 8. 取消关联岗位

**接口**: `DELETE /api/recruitment/sessions/{sessionId}/positions/{positionId}`

---

### 9. 获取招新场次关联的岗位

**接口**: `GET /api/recruitment/sessions/{sessionId}/positions`

**响应**: `SessionPosition[]`

---

## 学校模块 (school)

### 1. 搜索学校

**接口**: `GET /api/schools/search`

**查询参数**:
```typescript
{
  q: string             // 搜索关键词
}
```

**响应**:
```typescript
{
  total: number
  items: {
    id: number
    name: string
    code: string
  }[]
}
```

---

## 评分模块 (score)

### 1. 获取评分标准

**接口**: `GET /api/score/criteria`

**查询参数**:
```typescript
{
  department: string
}
```

---

### 2. 提交评分

**接口**: `POST /api/score`

**请求参数**:
```typescript
{
  interviewResultId: number
  scores: {
    criterionId: number
    score: number
    remark?: string
  }[]
  remark?: string
}
```

---

### 3. 获取评分详情

**接口**: `GET /score/{resultId}`

**响应**:
```typescript
{
  id: number
  interviewResultId: number
  criterionId: number
  criterionName: string
  score: number
  maxScore: number
  remark?: string
}[]
```

---

### 4. 修改评分

**接口**: `PUT /score/{resultId}`

**请求参数**: 同提交评分

---

## 统计模块 (statistics)

### 1. 获取概览统计

**接口**: `GET /api/statistics/overview`

**响应**:
```typescript
{
  totalApplications: number
  pendingApplications: number
  approvedApplications: number
  rejectedApplications: number
  totalInterviews: number
  completedInterviews: number
  upcomingInterviews: number
}
```

---

### 2. 获取仪表盘统计数据

**接口**: `GET /api/admin/dashboard`

**查询参数**:
```typescript
{
  club_id: number
}
```

**响应**:
```typescript
{
  total_sessions: number
  active_sessions: number
  total_applications: number
  pending_review: number
  total_interviews: number
  completed_interviews: number
  admitted_count: number
  application_growth: number
  interview_completion_rate: number
  admission_rate: number
  daily_applications: {
    date: string
    count: number
  }[]
  department_stats: {
    department_name: string
    application_count: number
    admission_count: number
  }[]
  position_stats: {
    position_name: string
    department_name: string
    application_count: number
    admission_count: number
  }[]
}
```

---

### 3. 获取部门统计

**接口**: `GET /api/statistics/department`

**查询参数**:
```typescript
{
  department?: string
}
```

---

### 4. 获取每日统计

**接口**: `GET /api/statistics/daily`

**查询参数**:
```typescript
{
  startDate: string
  endDate: string
  type?: string
}
```

---

### 5. 获取面试统计

**接口**: `GET /api/statistics/interview`

**查询参数**:
```typescript
{
  interviewId?: number
}
```

---

### 6. 导出统计数据

**接口**: `POST /api/statistics/export`

**请求参数**: 根据导出类型而定

**响应**: Blob (文件流)

---

## 学生模块 (student)

### 1. 获取学生详细信息

**接口**: `GET /api/student/profile`

**响应**:
```typescript
{
  id: number
  phone: string
  name: string | null
  email: string | null
  student_no: string | null
  major: string | null
  school_code: string | null
  school_name: string | null
  status: number
  is_initialized: boolean
  avatar_url: string | null
}
```

---

### 2. 更新学生信息

**接口**: `PUT /api/student/profile`

**请求参数**:
```typescript
{
  phone?: string
  email?: string
  nickname?: string
}
```

---

### 3. 获取我的申请

**接口**: `GET /api/student/application`

**响应**:
```typescript
{
  id: number
  department: string
  introduction: string
  status: 'pending' | 'approved' | 'rejected'
  applyTime: string
  remark?: string
}
```

---

### 4. 提交申请

**接口**: `POST /api/student/application`

**请求参数**:
```typescript
{
  department: string
  introduction: string
}
```

---

### 5. 获取我的面试信息

**接口**: `GET /api/student/interview`

---

## 工单模块 (ticket)

### 1. 获取工单列表（管理员）

**接口**: `GET /api/tickets`

**查询参数**:
```typescript
{
  page: number
  pageSize: number
  status?: 'pending' | 'replied' | 'closed'
  type?: 'question' | 'feedback' | 'appeal' | 'other'
  priority?: 'low' | 'medium' | 'high'
}
```

**响应**:
```typescript
{
  id: number
  title: string
  content: string
  type: 'question' | 'feedback' | 'appeal' | 'other'
  status: 'pending' | 'replied' | 'closed'
  priority: 'low' | 'medium' | 'high'
  studentId: number
  studentName: string
  reply?: string
  repliedBy?: string
  repliedAt?: string
  createdAt: string
  updatedAt: string
}[]
```

---

### 2. 获取工单详情

**接口**: `GET /tickets/{id}`

**响应**: `Ticket`

---

### 3. 创建工单

**接口**: `POST /api/tickets`

**请求参数**:
```typescript
{
  title: string
  content: string
  type: 'question' | 'feedback' | 'appeal' | 'other'
  priority?: 'low' | 'medium' | 'high'
}
```

---

### 4. 回复工单

**接口**: `PUT /tickets/{id}/reply`

**请求参数**:
```typescript
{
  reply: string
}
```

---

### 5. 关闭工单

**接口**: `PUT /tickets/{id}/close`

---

### 6. 获取我的工单（学生）

**接口**: `GET /api/student/tickets`

---

## 通用说明

### 认证方式

除了登录和注册接口外，所有接口需要在请求头中携带 `Authorization`：

```
Authorization: Bearer {access_token}
```

### 响应格式

**成功响应**:
```json
{
  "code": 200,
  "data": { ... },
  "message": ""
}
```

**错误响应**:
```json
{
  "code": 400,
  "data": null,
  "message": "错误信息描述"
}
```

### 分页参数

```typescript
{
  page: number           // 页码，从 1 开始
  page_size: number     // 每页数量
}
```

### 时间格式

所有时间字段使用 ISO 8601 格式：`YYYY-MM-DDTHH:mm:ss.sssZ`

### 状态码

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未授权 |
| 403 | 禁止访问 |
| 404 | 资源不存在 |
| 500 | 服务器错误 |

---

> 更新日期：2026-01-10
