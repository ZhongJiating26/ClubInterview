<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { ArrowLeft, Lock, User as UserIcon, Trash2, KeyRound } from 'lucide-vue-next'
import { changePassword, deleteAccount, type UserInfo } from '@/api/modules/auth'
import { updateStudentProfile, getProfile, type StudentProfile } from '@/api/modules/student'

const router = useRouter()
const userStore = useUserStore()

const userInfo = computed(() => userStore.userInfo as UserInfo)

// 表单数据
const profileForm = ref<StudentProfile>({
  id: 0,
  name: '',
  phone: '',
  email: '',
  avatar_url: '',
  major: '',
  student_no: '',
  school_code: '',
  school_name: ''
})

const passwordForm = ref({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const deleteForm = ref({
  password: '',
  confirmation: ''
})

// UI 状态
const activeTab = ref<'profile' | 'password' | 'delete'>('profile')
const loading = ref(false)
const saving = ref(false)

// 错误提示
const errorMessage = ref('')
const successMessage = ref('')

// 获取用户资料
const fetchProfile = async () => {
  try {
    loading.value = true
    const data = await getProfile()
    profileForm.value = {
      ...data,
      id: data.id || userInfo.value?.id || 0
    }
  } catch (err: any) {
    showError('获取用户信息失败')
  } finally {
    loading.value = false
  }
}

// 保存个人资料
const handleSaveProfile = async () => {
  try {
    saving.value = true
    await updateStudentProfile(profileForm.value)
    showSuccess('个人资料已更新')
    // 刷新用户信息
    await userStore.fetchUserInfo()
  } catch (err: any) {
    showError(err.message || '更新失败')
  } finally {
    saving.value = false
  }
}

// 修改密码
const handleChangePassword = async () => {
  // 验证
  if (!passwordForm.value.oldPassword) {
    showError('请输入当前密码')
    return
  }
  if (!passwordForm.value.newPassword || passwordForm.value.newPassword.length < 6) {
    showError('新密码至少需要6位')
    return
  }
  if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
    showError('两次输入的新密码不一致')
    return
  }

  try {
    saving.value = true
    await changePassword({
      old_password: passwordForm.value.oldPassword,
      new_password: passwordForm.value.newPassword
    })
    showSuccess('密码修改成功，请重新登录')
    // 清空表单
    passwordForm.value = {
      oldPassword: '',
      newPassword: '',
      confirmPassword: ''
    }
    // 3秒后自动登出
    setTimeout(() => {
      handleLogout()
    }, 3000)
  } catch (err: any) {
    showError(err.message || '密码修改失败')
  } finally {
    saving.value = false
  }
}

// 注销账号
const handleDeleteAccount = async () => {
  // 验证
  if (!deleteForm.value.password) {
    showError('请输入密码以确认身份')
    return
  }
  if (deleteForm.value.confirmation !== 'DELETE') {
    showError('请输入 DELETE 确认注销')
    return
  }

  // 二次确认
  if (!confirm('注销账号后，所有数据将被删除且无法恢复。确定要继续吗？')) {
    return
  }

  try {
    saving.value = true
    await deleteAccount({
      password: deleteForm.value.password,
      confirmation: 'DELETE'
    })
    showSuccess('账号已注销')
    // 自动登出
    setTimeout(() => {
      handleLogout()
    }, 1500)
  } catch (err: any) {
    showError(err.message || '注销失败')
  } finally {
    saving.value = false
  }
}

const handleLogout = () => {
  userStore.logout()
  router.push('/login')
}

const showSuccess = (msg: string) => {
  successMessage.value = msg
  errorMessage.value = ''
  setTimeout(() => {
    successMessage.value = ''
  }, 3000)
}

const showError = (msg: string) => {
  errorMessage.value = msg
  successMessage.value = ''
  setTimeout(() => {
    errorMessage.value = ''
  }, 3000)
}

// 页面加载时获取资料
fetchProfile()
</script>

<template>
  <div class="min-h-screen bg-gray-50 py-8">
    <div class="max-w-3xl mx-auto px-4">
      <!-- 页面头部 -->
      <div class="mb-6">
        <Button
          variant="ghost"
          @click="router.back()"
          class="mb-4"
        >
          <ArrowLeft class="w-4 h-4 mr-2" />
          返回
        </Button>
        <h1 class="text-2xl font-bold text-gray-900">账号设置</h1>
      </div>

      <!-- 标签页 -->
      <div class="mb-6 flex gap-2 border-b border-gray-200">
        <button
          :class="[
            'px-4 py-2 font-medium text-sm transition-colors',
            activeTab === 'profile'
              ? 'text-blue-600 border-b-2 border-blue-600'
              : 'text-gray-500 hover:text-gray-700'
          ]"
          @click="activeTab = 'profile'"
        >
          <UserIcon class="w-4 h-4 mr-2" />
          个人资料
        </button>
        <button
          :class="[
            'px-4 py-2 font-medium text-sm transition-colors',
            activeTab === 'password'
              ? 'text-blue-600 border-b-2 border-blue-600'
              : 'text-gray-500 hover:text-gray-700'
          ]"
          @click="activeTab = 'password'"
        >
          <KeyRound class="w-4 h-4 mr-2" />
          修改密码
        </button>
        <button
          :class="[
            'px-4 py-2 font-medium text-sm transition-colors',
            activeTab === 'delete'
              ? 'text-red-600 border-b-2 border-red-600'
              : 'text-gray-500 hover:text-gray-700'
          ]"
          @click="activeTab = 'delete'"
        >
          <Trash2 class="w-4 h-4 mr-2" />
          注销账号
        </button>
      </div>

      <!-- 消息提示 -->
      <div
        v-if="successMessage"
        class="mb-4 p-4 bg-green-50 border border-green-200 text-green-700 rounded-lg"
      >
        {{ successMessage }}
      </div>
      <div
        v-if="errorMessage"
        class="mb-4 p-4 bg-red-50 border border-red-200 text-red-700 rounded-lg"
      >
        {{ errorMessage }}
      </div>

      <!-- 个人资料标签页 -->
      <div v-if="activeTab === 'profile'">
        <Card class="mb-6">
          <CardHeader>
            <CardTitle>个人资料</CardTitle>
          </CardHeader>
          <CardContent class="space-y-4">
            <!-- 姓名 -->
            <div class="space-y-2">
              <Label for="name">姓名</Label>
              <Input
                id="name"
                v-model="profileForm.name"
                placeholder="请输入姓名"
                :disabled="loading || saving"
              />
            </div>

            <!-- 学号 -->
            <div class="space-y-2">
              <Label for="student_no">学号</Label>
              <Input
                id="student_no"
                v-model="profileForm.student_no"
                placeholder="请输入学号"
                :disabled="loading || saving"
              />
            </div>

            <!-- 邮箱 -->
            <div class="space-y-2">
              <Label for="email">邮箱</Label>
              <Input
                id="email"
                v-model="profileForm.email"
                type="email"
                placeholder="请输入邮箱"
                :disabled="loading || saving"
              />
            </div>

            <!-- 专业 -->
            <div class="space-y-2">
              <Label for="major">专业</Label>
              <Input
                id="major"
                v-model="profileForm.major"
                placeholder="请输入专业"
                :disabled="loading || saving"
              />
            </div>

            <!-- 保存按钮 -->
            <div class="pt-4">
              <Button
                @click="handleSaveProfile"
                :disabled="loading || saving"
                class="w-full md:w-auto"
              >
                {{ saving ? '保存中...' : '保存资料' }}
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      <!-- 修改密码标签页 -->
      <div v-if="activeTab === 'password'">
        <Card class="mb-6">
          <CardHeader>
            <CardTitle>修改密码</CardTitle>
          </CardHeader>
          <CardContent class="space-y-4">
            <!-- 当前密码 -->
            <div class="space-y-2">
              <Label for="oldPassword">当前密码</Label>
              <Input
                id="oldPassword"
                v-model="passwordForm.oldPassword"
                type="password"
                placeholder="请输入当前密码"
                :disabled="saving"
              />
            </div>

            <!-- 新密码 -->
            <div class="space-y-2">
              <Label for="newPassword">新密码</Label>
              <Input
                id="newPassword"
                v-model="passwordForm.newPassword"
                type="password"
                placeholder="请输入新密码（至少6位）"
                :disabled="saving"
              />
            </div>

            <!-- 确认密码 -->
            <div class="space-y-2">
              <Label for="confirmPassword">确认新密码</Label>
              <Input
                id="confirmPassword"
                v-model="passwordForm.confirmPassword"
                type="password"
                placeholder="请再次输入新密码"
                :disabled="saving"
              />
            </div>

            <!-- 提示信息 -->
            <div class="text-sm text-gray-500 bg-blue-50 p-3 rounded-lg">
              <Lock class="w-4 h-4 inline-block mr-2" />
              密码修改成功后需要重新登录
            </div>

            <!-- 提交按钮 -->
            <div class="pt-4">
              <Button
                @click="handleChangePassword"
                :disabled="saving"
                class="w-full md:w-auto"
              >
                {{ saving ? '修改中...' : '修改密码' }}
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      <!-- 注销账号标签页 -->
      <div v-if="activeTab === 'delete'">
        <Card class="border-red-200 bg-red-50">
          <CardHeader class="border-red-200">
            <CardTitle class="text-red-700">注销账号</CardTitle>
          </CardHeader>
          <CardContent class="space-y-4">
            <!-- 警告信息 -->
            <div class="text-sm text-red-700 bg-red-100 p-4 rounded-lg">
              <strong>⚠️ 重要提示</strong>
              <p class="mt-2">注销账号后，以下数据将被永久删除且无法恢复：</p>
              <ul class="list-disc list-inside ml-4 mt-2">
                <li>个人资料和账号信息</li>
                <li>所有报名记录</li>
                <li>面试记录和评分</li>
                <li>通知和工单历史</li>
              </ul>
            </div>

            <!-- 确认输入 -->
            <div class="space-y-4 pt-4">
              <div class="space-y-2">
                <Label for="deletePassword">请输入密码以确认身份</Label>
                <Input
                  id="deletePassword"
                  v-model="deleteForm.password"
                  type="password"
                  placeholder="请输入密码"
                  :disabled="saving"
                />
              </div>

              <div class="space-y-2">
                <Label for="confirmation">请输入 DELETE 确认注销</Label>
                <Input
                  id="confirmation"
                  v-model="deleteForm.confirmation"
                  placeholder="请输入 DELETE（大写）"
                  :disabled="saving"
                />
              </div>

              <!-- 注销按钮 -->
              <div class="pt-4">
                <Button
                  @click="handleDeleteAccount"
                  :disabled="saving"
                  variant="destructive"
                  class="w-full md:w-auto"
                >
                  <Trash2 class="w-4 h-4 mr-2" />
                  {{ saving ? '注销中...' : '确认注销账号' }}
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  </div>
</template>
