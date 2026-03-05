<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { sendCode, register } from '@/api/modules/auth'
import { useUserStore } from '@/stores/user'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

const router = useRouter()
const userStore = useUserStore()

// 表单数据
const phone = ref('')
const code = ref('')

// 状态
const loading = ref(false)
const error = ref('')
const success = ref('')
const countdown = ref(0)

// 手机号格式验证（中国手机号：11位，以1开头）
const isValidPhone = (phone: string) => {
  return /^1\d{10}$/.test(phone)
}

// 发送验证码
const sendCodeAction = async () => {
  error.value = ''
  success.value = ''

  if (!phone.value) {
    error.value = '请输入手机号'
    return
  }

  if (!isValidPhone(phone.value)) {
    error.value = '请输入正确的手机号'
    return
  }

  loading.value = true

  try {
    const res = await sendCode({ phone: phone.value, scene: 'REGISTER' })
    // 发送成功，显示绿色提示
    success.value = res.message || '验证码已发送'
    countdown.value = 60
    const timer = setInterval(() => {
      countdown.value--
      if (countdown.value <= 0) {
        clearInterval(timer)
      }
    }, 1000)
  } catch (err: any) {
    // 显示后端返回的具体错误信息（红色）
    error.value = err.detail || err.message || '发送失败'
  } finally {
    loading.value = false
  }
}

// 注册
const handleRegister = async () => {
  error.value = ''
  success.value = ''

  if (!phone.value || !code.value) {
    error.value = '请填写手机号和验证码'
    return
  }

  if (code.value.length !== 6) {
    error.value = '验证码为6位数字'
    return
  }

  loading.value = true

  try {
    const res = await register({
      phone: phone.value,
      code: code.value
    })
    // 保存 token
    userStore.setToken(res.access_token)
    // 跳转到角色选择页面
    router.push('/role-select')
  } catch (err: any) {
    const msg = err.detail || err.message || '注册失败，验证码可能不正确'
    // 如果是"手机号已注册"的提示，引导用户去登录
    if (msg.includes('手机号已注册') || msg.includes('已注册')) {
      error.value = msg + '，请直接登录'
    } else {
      error.value = msg
    }
  } finally {
    loading.value = false
  }
}

const goToLogin = () => {
  router.push('/login')
}
</script>

<template>
  <div class="min-h-screen w-full bg-white flex items-center justify-center p-6">
    <div class="w-full max-w-sm flex flex-col gap-6">
      <!-- 标题 -->
      <div class="flex flex-col items-center gap-2 text-center">
        <h1 class="text-2xl font-bold">注册账号</h1>
        <p class="text-muted-foreground text-sm">仅需手机号和验证码即可注册</p>
      </div>

      <!-- 表单 -->
      <form @submit.prevent="handleRegister" class="flex flex-col gap-4">
        <!-- 错误提示（红色） -->
        <div v-if="error" class="p-3 text-sm text-red-600 bg-red-50 rounded-md">
          {{ error }}
        </div>

        <!-- 成功提示（绿色） -->
        <div v-if="success" class="p-3 text-sm text-green-600 bg-green-50 rounded-md">
          {{ success }}
        </div>

        <!-- 手机号 -->
        <div class="grid gap-2">
          <Label for="phone">手机号</Label>
          <div class="flex gap-2">
            <Input
              id="phone"
              v-model="phone"
              type="tel"
              placeholder="请输入手机号"
              class="flex-1"
              required
            />
            <Button
              type="button"
              variant="outline"
              :disabled="countdown > 0 || loading"
              @click="sendCodeAction"
            >
              {{ countdown > 0 ? `${countdown}s` : '获取验证码' }}
            </Button>
          </div>
        </div>

        <!-- 验证码输入 -->
        <div class="grid gap-2">
          <Label for="code">验证码</Label>
          <Input
            id="code"
            v-model="code"
            type="text"
            placeholder="请输入6位验证码"
            maxlength="6"
            required
          />
        </div>

        <Button type="submit" class="w-full" :disabled="loading">
          <span v-if="loading">注册中...</span>
          <span v-else>注册</span>
        </Button>
      </form>

      <!-- 登录入口 -->
      <p class="text-center text-sm text-muted-foreground">
        已有账号？
        <button
          type="button"
          class="text-primary hover:underline font-medium"
          @click="goToLogin"
        >
          立即登录
        </button>
      </p>

      <!-- 底部条款 -->
      <p class="text-center text-xs text-muted-foreground">
        注册即表示同意
        <a href="#" class="underline underline-offset-4 hover:text-primary">服务条款</a>
        和
        <a href="#" class="underline underline-offset-4 hover:text-primary">隐私政策</a>
      </p>
    </div>
  </div>
</template>
