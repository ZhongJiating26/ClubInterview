<script setup lang="ts">
  import { ref } from 'vue'
  import { useRouter } from 'vue-router'
  import { Eye, EyeOff } from 'lucide-vue-next'
  import { forgotPassword, resetPassword } from '@/api/modules/auth'
  import { Button } from '@/components/ui/button'
  import { Input } from '@/components/ui/input'
  import { Label } from '@/components/ui/label'

  const router = useRouter()

  // 步骤：1-输入手机号，2-输入验证码和新密码
  const step = ref(1)

  // 表单数据
  const phone = ref('')
  const code = ref('')
  const newPassword = ref('')
  const confirmPassword = ref('')

  // 状态
  const loading = ref(false)
  const error = ref('')
  const success = ref('')
  const countdown = ref(0)
  const showPassword = ref(false)

  // 手机号格式验证
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
      const res = await forgotPassword({ phone: phone.value })
      success.value = res.detail || '验证码已发送'
      // 进入下一步
      step.value = 2
      // 启动倒计时
      countdown.value = 60
      const timer = setInterval(() => {
        countdown.value--
        if (countdown.value <= 0) {
          clearInterval(timer)
        }
      }, 1000)
    } catch (err: any) {
      error.value = err.detail || err.message || '发送失败'
    } finally {
      loading.value = false
    }
  }

  // 重置密码
  const handleResetPassword = async () => {
    error.value = ''
    success.value = ''

    if (!code.value) {
      error.value = '请输入验证码'
      return
    }

    if (code.value.length !== 6) {
      error.value = '验证码为6位数字'
      return
    }

    if (!newPassword.value) {
      error.value = '请输入新密码'
      return
    }

    if (newPassword.value.length < 6) {
      error.value = '密码长度至少6位'
      return
    }

    if (newPassword.value !== confirmPassword.value) {
      error.value = '两次输入的密码不一致'
      return
    }

    loading.value = true

    try {
      const res = await resetPassword({
        phone: phone.value,
        code: code.value,
        new_password: newPassword.value
      })
      success.value = res.detail || '密码重置成功'
      // 延迟跳转回登录页
      setTimeout(() => {
        router.push('/login')
      }, 1500)
    } catch (err: any) {
      error.value = err.detail || err.message || '重置失败，请检查验证码'
    } finally {
      loading.value = false
    }
  }

  // 返回上一步
  const goBack = () => {
    step.value = 1
    error.value = ''
    success.value = ''
    code.value = ''
    newPassword.value = ''
    confirmPassword.value = ''
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
          <h1 class="text-2xl font-bold">忘记密码</h1>
          <p class="text-muted-foreground text-sm">
            {{ step === 1 ? '请输入您的手机号' : '请输入验证码和新密码' }}
          </p>
        </div>

        <!-- 步骤指示器 -->
        <div class="flex justify-center gap-2">
          <div
            class="h-1.5 flex-1 rounded-full transition-colors"
            :class="step >= 1 ? 'bg-primary' : 'bg-gray-200'"
          ></div>
          <div
            class="h-1.5 flex-1 rounded-full transition-colors"
            :class="step >= 2 ? 'bg-primary' : 'bg-gray-200'"
          ></div>
        </div>

        <!-- 步骤1：输入手机号 -->
        <form v-if="step === 1" @submit.prevent="sendCodeAction" class="flex flex-col gap-4">
          <!-- 错误提示 -->
          <div v-if="error" class="p-3 text-sm text-red-600 bg-red-50 rounded-md">
            {{ error }}
          </div>

          <!-- 成功提示 -->
          <div v-if="success" class="p-3 text-sm text-green-600 bg-green-50 rounded-md">
            {{ success }}
          </div>

          <!-- 手机号 -->
          <div class="grid gap-2">
            <Label for="phone" class="text-lg">手机号</Label>
            <Input
              id="phone"
              v-model="phone"
              type="tel"
              placeholder="请输入注册时的手机号"
              class="h-12 text-xl rounded-xl"
              required
            />
          </div>

          <Button type="submit" class="w-full h-12 text-lg rounded-xl" :disabled="loading">
            <span v-if="loading">发送中...</span>
            <span v-else>获取验证码</span>
          </Button>
        </form>

        <!-- 步骤2：输入验证码和新密码 -->
        <form v-else @submit.prevent="handleResetPassword" class="flex flex-col gap-4">
          <!-- 错误提示 -->
          <div v-if="error" class="p-3 text-sm text-red-600 bg-red-50 rounded-md">
            {{ error }}
          </div>

          <!-- 成功提示 -->
          <div v-if="success" class="p-3 text-sm text-green-600 bg-green-50 rounded-md">
            {{ success }}
          </div>

          <!-- 手机号（只读） -->
          <div class="grid gap-2">
            <div class="text-lg text-right">手机号</div>
            <div class="text-xl text-gray-900 h-12 flex items-center justify-end">
              {{ phone }}
            </div>
          </div>

          <!-- 验证码 -->
          <div class="grid gap-2">
            <Label for="code" class="text-lg">验证码</Label>
            <div class="flex gap-2">
              <Input
                id="code"
                v-model="code"
                type="text"
                placeholder="请输入6位验证码"
                maxlength="6"
                class="flex-1 h-12 text-xl rounded-xl"
                required
              />
              <Button
                type="button"
                variant="outline"
                class="h-12 w-24 rounded-xl"
                :disabled="countdown > 0"
                @click="sendCodeAction"
              >
                {{ countdown > 0 ? `${countdown}s` : '重发' }}
              </Button>
            </div>
            <p class="text-sm text-muted-foreground">
              当前未接入真实验证码，任意输入 6 位数字即可。
            </p>
          </div>

          <!-- 新密码 -->
          <div class="grid gap-2">
            <Label for="newPassword" class="text-lg">新密码</Label>
            <div class="relative">
              <Input
                id="newPassword"
                v-model="newPassword"
                :type="showPassword ? 'text' : 'password'"
                placeholder="请输入新密码（至少6位）"
                class="h-12 text-xl rounded-xl pr-10"
                required
              />
              <button
                type="button"
                class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                @click="showPassword = !showPassword"
              >
                <EyeOff v-if="showPassword" class="w-4 h-4" />
                <Eye v-else class="w-4 h-4" />
              </button>
            </div>
          </div>

          <!-- 确认新密码 -->
          <div class="grid gap-2">
            <Label for="confirmPassword" class="text-lg">确认新密码</Label>
            <Input
              id="confirmPassword"
              v-model="confirmPassword"
              type="password"
              placeholder="请再次输入新密码"
              class="h-12 text-xl rounded-xl"
              required
            />
          </div>

          <!-- 按钮组 -->
          <div class="flex gap-2">
            <Button type="button" variant="outline" class="flex-1 h-12 text-lg rounded-xl" @click="goBack">
              上一步
            </Button>
            <Button type="submit" class="flex-1 h-12 text-lg rounded-xl" :disabled="loading">
              <span v-if="loading">重置中...</span>
              <span v-else>重置密码</span>
            </Button>
          </div>
        </form>

        <!-- 登录入口 -->
        <p class="text-center text-sm text-muted-foreground">
          想起密码了？
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
          操作即表示同意
          <a href="#" class="underline underline-offset-4 hover:text-primary">服务条款</a>
          和
          <a href="#" class="underline underline-offset-4 hover:text-primary">隐私政策</a>
        </p>
      </div>
    </div>
  </template>
