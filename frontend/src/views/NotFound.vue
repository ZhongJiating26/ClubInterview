<script setup lang="ts">
import { useRouter } from 'vue-router'
import { Button } from '@/components/ui/button'
import { Home } from 'lucide-vue-next'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

// 返回首页
const goHome = () => {
  // 未登录，跳转到登录页
  if (!userStore.token) {
    router.push('/login')
    return
  }

  // 获取用户角色
  const role = userStore.primaryRole

  // 根据角色跳转到对应首页
  if (role === 'interviewer') {
    router.push('/interviewer/join')
  } else if (role === 'student') {
    router.push('/student/home')
  } else if (role === 'admin') {
    router.push('/admin/dashboard')
  } else {
    // 默认跳转到学生首页
    router.push('/student/home')
  }
}
</script>

<template>
  <div class="min-h-screen w-full bg-white flex items-center justify-center p-6">
    <div class="w-full max-w-sm flex flex-col gap-6">
      <!-- 标题 -->
      <div class="flex flex-col items-center gap-2 text-center">
        <h1 class="text-[8rem] md:text-[20rem] font-bold text-gray-300 leading-none">404</h1>
        <p class="text-2xl font-semibold">页面未找到</p>
        <p class="text-muted-foreground text-sm">您访问的页面不存在或已被移除</p>
      </div>

      <!-- 操作按钮 -->
      <div class="flex flex-col gap-3">
        <Button variant="outline" class="w-full" @click="goHome">
          <Home class="w-4 h-4 mr-2" />
          返回首页
        </Button>
      </div>
    </div>
  </div>
</template>
