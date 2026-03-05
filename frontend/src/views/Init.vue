<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { initAccount, assignRole, initClub, getMe } from '@/api/modules/auth'
import { checkClub, bindUserToClub } from '@/api/modules/clubs'
import { useUserStore } from '@/stores/user'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import SchoolSelect from '@/components/SchoolSelect.vue'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

// 从路由获取角色参数
const role = ref(route.query.role as string || '')

// 角色ID映射（根据实际后端配置调整）
const roleIdMap: Record<string, number> = {
  admin: 2,        // 社团管理员
  interviewer: 3,  // 面试官
  student: 4       // 普通学生
}

// 角色代码映射（用于 bind-user 接口）
const roleCodeMap: Record<string, string> = {
  admin: 'CLUB_ADMIN',
  interviewer: 'INTERVIEWER',
  student: 'STUDENT'
}

// 表单数据
const password = ref('')
const confirmPassword = ref('')
const name = ref('')
const idCardNo = ref('')
const schoolId = ref<number | null>(null)
const schoolCode = ref<string | null>(null)
const major = ref('')
const studentNo = ref('')
const email = ref('')
const clubName = ref('')

// 状态
const loading = ref(false)
const error = ref('')

// 校验规则
const validators = {
  // 姓名：2-10个汉字
  name: (v: string) => {
    if (!v.trim()) return '请输入姓名'
    if (v.length < 2 || v.length > 10) return '姓名应为2-10个字符'
    if (!/^[\u4e00-\u9fa5]+$/.test(v)) return '姓名必须为中文'
    return ''
  },

  // 身份证号：15位或18位
  idCardNo: (v: string) => {
    if (!v.trim()) return '请输入身份证号'
    if (!/^[0-9]{15}$|^[0-9]{17}[0-9Xx]$/.test(v)) return '身份证号格式不正确'
    return ''
  },

  // 专业：2-30个字符
  major: (v: string) => {
    if (!v.trim()) return '请输入专业'
    if (v.length < 2 || v.length > 30) return '专业应为2-30个字符'
    return ''
  },

  // 学号：6-20位数字或字母
  studentNo: (v: string) => {
    if (!v.trim()) return '请输入学号'
    if (!/^[A-Za-z0-9]{6,20}$/.test(v)) return '学号应为6-20位数字或字母'
    return ''
  },

  // 密码：至少6位
  password: (v: string) => {
    if (!v) return '请输入密码'
    if (v.length < 6) return '密码至少6位'
    return ''
  },

  // 邮箱：可选，格式验证
  email: (v: string) => {
    if (!v) return ''
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v)) return '邮箱格式不正确'
    return ''
  },

  // 社团名称：2-30个字符
  clubName: (v: string) => {
    if (!v.trim()) return '请输入社团名称'
    if (v.length < 2 || v.length > 30) return '社团名称应为2-30个字符'
    return ''
  },
}

// 提交初始化
const handleInit = async () => {
  error.value = ''

  // 验证必填
  if (!password.value || !name.value || !idCardNo.value ||
      !schoolCode.value || !major.value || !studentNo.value) {
    error.value = '请填写所有必填项'
    return
  }

  // 姓名校验
  let msg = validators.name(name.value)
  if (msg) { error.value = msg; return }

  // 身份证号校验
  msg = validators.idCardNo(idCardNo.value)
  if (msg) { error.value = msg; return }

  // 专业校验
  msg = validators.major(major.value)
  if (msg) { error.value = msg; return }

  // 学号校验
  msg = validators.studentNo(studentNo.value)
  if (msg) { error.value = msg; return }

  // 密码校验
  msg = validators.password(password.value)
  if (msg) { error.value = msg; return }

  // 确认密码
  if (password.value !== confirmPassword.value) {
    error.value = '两次密码不一致'
    return
  }

  // 邮箱校验（可选）
  msg = validators.email(email.value)
  if (msg) { error.value = msg; return }

  // 社团管理员需要填写社团名称
  if (role.value === 'admin') {
    msg = validators.clubName(clubName.value)
    if (msg) { error.value = msg; return }
  }

  loading.value = true

  try {
    // 社团管理员：先检查社团是否存在
    let clubId: number | null = null

    if (role.value === 'admin' && schoolCode.value) {
      // 1. 检查社团是否存在
      const checkRes = await checkClub({
        club_name: clubName.value,
        school_code: schoolCode.value
      })

      if (checkRes.exists) {
        // 社团已存在，报错提示联系社长加入
        throw new Error('该社团已存在，请联系社长加入')
      } else {
        // 社团不存在，创建社团
        const initRes = await initClub({
          club_name: clubName.value,
          school_code: schoolCode.value
        })
        clubId = initRes.club_id
      }
    }

    // 2. 调用 initAccount 完成注册
    const data: any = {
      password: password.value,
      name: name.value,
      id_card_no: idCardNo.value,
      school_code: schoolCode.value,
      major: major.value,
      student_no: studentNo.value,
      role: role.value
    }
    // 邮箱可选
    if (email.value) {
      data.email = email.value
    }
    await initAccount(data)

    // 3. 获取用户信息
    const userData = await getMe()
    userStore.setUserInfo(userData)
    const userId = userData.id
    if (!userId) {
      throw new Error('无法获取用户信息')
    }

    // 4. 社团管理员：关联用户到社团
    if (role.value === 'admin' && clubId) {
      await bindUserToClub(clubId, {
        user_id: userId,
        role_code: roleCodeMap[role.value] || roleCodeMap.admin
      })
      // 重新获取用户信息，更新 club_id
      const updatedUserData = await getMe()
      userStore.setUserInfo(updatedUserData)
    } else {
      // 非社团管理员：调用 assignRole 分配角色
      await assignRole({
        user_id: userId,
        role_id: roleIdMap[role.value] || roleIdMap.student,
        club_id: null
      })
    }

    // 5. 重新获取用户信息，确保最新状态
    const finalUserData = await getMe()
    userStore.setUserInfo(finalUserData)

    // 6. 初始化成功，跳转到对应端首页
    // 使用 replace 避免路由历史问题
    if (role.value === 'student') {
      router.replace('/student/home')
    } else if (role.value === 'interviewer') {
      router.replace('/interviewer/join')
    } else {
      router.replace('/admin/dashboard')
    }
  } catch (err: any) {
    error.value = err.message || '初始化失败'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen w-full bg-white flex items-center justify-center p-6">
    <div class="w-full max-w-sm flex flex-col gap-6">
      <!-- 标题 -->
      <div class="flex flex-col items-center gap-2 text-center">
        <h1 class="text-2xl font-bold">完善个人信息</h1>
        <p class="text-muted-foreground text-sm">
          请填写以下信息完成注册
          <span v-if="role" class="text-primary">({{ role === 'admin' ? '社团管理员' : role === 'interviewer' ? '面试官' : '普通学生' }})</span>
        </p>
      </div>

      <!-- 表单 -->
      <form @submit.prevent="handleInit" class="flex flex-col gap-4">
        <!-- 错误提示 -->
        <div v-if="error" class="p-3 text-sm text-red-600 bg-red-50 rounded-md">
          {{ error }}
        </div>

        <!-- 姓名 -->
        <div class="grid gap-2">
          <Label for="name">姓名</Label>
          <Input
            id="name"
            v-model="name"
            type="text"
            placeholder="请输入您的真实姓名"
            required
          />
        </div>

        <!-- 身份证号 -->
        <div class="grid gap-2">
          <Label for="id_card_no">身份证号</Label>
          <Input
            id="id_card_no"
            v-model="idCardNo"
            type="text"
            placeholder="请输入身份证号"
            required
          />
        </div>

        <!-- 学校选择 -->
        <SchoolSelect
          v-model="schoolId"
          v-model:modelCode="schoolCode"
          label="学校"
          placeholder="输入学校名称搜索"
          :required="true"
        />

        <!-- 社团名称（仅社团管理员） -->
        <div v-if="role === 'admin'" class="grid gap-2">
          <Label for="club_name">社团名称</Label>
          <Input
            id="club_name"
            v-model="clubName"
            type="text"
            placeholder="请输入社团名称"
            required
          />
        </div>

        <!-- 专业 -->
        <div class="grid gap-2">
          <Label for="major">专业</Label>
          <Input
            id="major"
            v-model="major"
            type="text"
            placeholder="请输入专业"
            required
          />
        </div>

        <!-- 学号 -->
        <div class="grid gap-2">
          <Label for="student_no">学号</Label>
          <Input
            id="student_no"
            v-model="studentNo"
            type="text"
            placeholder="请输入学号"
            required
          />
        </div>

        <!-- 邮箱（可选） -->
        <div class="grid gap-2">
          <Label for="email">邮箱</Label>
          <Input
            id="email"
            v-model="email"
            type="email"
            placeholder="选填"
          />
        </div>

        <!-- 密码 -->
        <div class="grid gap-2">
          <Label for="password">密码</Label>
          <Input
            id="password"
            v-model="password"
            type="password"
            placeholder="至少6位"
            required
          />
        </div>

        <!-- 确认密码 -->
        <div class="grid gap-2">
          <Label for="confirm_password">确认密码</Label>
          <Input
            id="confirm_password"
            v-model="confirmPassword"
            type="password"
            placeholder="请再次输入密码"
            required
          />
        </div>

        <Button type="submit" class="w-full" :disabled="loading">
          <span v-if="loading">提交中...</span>
          <span v-else>提交</span>
        </Button>
      </form>
    </div>
  </div>
</template>
