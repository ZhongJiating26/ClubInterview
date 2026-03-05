<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

const router = useRouter()
const userStore = useUserStore()

const phone = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

const handleLogin = async () => {
  error.value = ''

  if (!phone.value || !password.value) {
    error.value = '请输入手机号和密码'
    return
  }

  loading.value = true

  try {
    await userStore.doLogin(phone.value, password.value)

    // 判断是否已初始化
    if (userStore.userInfo?.is_initialized) {
      // 根据角色判断跳转页面（优先级：社团管理员 > 面试官 > 普通学生）
      const role = userStore.primaryRole || 'student'
      const redirectMap: Record<string, string> = {
        admin: '/admin/dashboard',
        interviewer: '/interviewer/join',
        student: '/student/home'
      }
      router.push(redirectMap[role] || '/student/home')
    } else {
      // 未初始化，跳转到角色选择页面
      router.push('/role-select')
    }
  } catch (err: any) {
    // 提示更友好的错误信息
    error.value = '手机号或密码错误'
  } finally {
    loading.value = false
  }
}

const goToRegister = () => {
  router.push('/register')
}

const goToForgetPassword = () => {
  router.push('/forget-password')
}
</script>

<template>
  <div class="min-h-screen w-full bg-white flex items-center justify-center p-6">
    <div class="w-full max-w-sm flex flex-col gap-6">
      <!-- 标题 -->
      <div class="flex flex-col items-center gap-2 text-center">
        <h1 class="text-2xl font-bold">社团面试系统</h1>
        <p class="text-muted-foreground text-sm">请登录您的账号</p>
      </div>

      <!-- 表单 -->
      <form @submit.prevent="handleLogin" class="flex flex-col gap-4">
        <!-- 错误提示 -->
        <div v-if="error" class="p-3 text-sm text-red-600 bg-red-50 rounded-md">
          {{ error }}
        </div>

        <div class="grid gap-2">
          <Label for="phone">手机号</Label>
          <Input
            id="phone"
            v-model="phone"
            type="tel"
            placeholder="请输入手机号"
            required
          />
        </div>

        <div class="grid gap-2">
          <Label for="password">密码</Label>
          <Input
            id="password"
            v-model="password"
            type="password"
            placeholder="请输入密码"
            required
          />
        </div>

        <!-- 忘记密码 -->
        <div class="flex justify-end">
          <button
            type="button"
            class="text-sm text-primary hover:underline"
            @click="goToForgetPassword"
          >
            忘记密码？
          </button>
        </div>

        <Button type="submit" class="w-full" :disabled="loading">
          <span v-if="loading">登录中...</span>
          <span v-else>登录</span>
        </Button>
      </form>

      <!-- 注册入口 -->
      <p class="text-center text-sm text-muted-foreground">
        还没有账号？
        <button
          type="button"
          class="text-primary hover:underline font-medium"
          @click="goToRegister"
        >
          立即注册
        </button>
      </p>

      <!-- 底部条款 -->
      <p class="text-center text-xs text-muted-foreground">
        登录即表示同意
        <a href="#" class="underline underline-offset-4 hover:text-primary">服务条款</a>
        和
        <a href="#" class="underline underline-offset-4 hover:text-primary">隐私政策</a>
      </p>
    </div>
  </div>
</template>
