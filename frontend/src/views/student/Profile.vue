<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { LogOut, User, Mail, Phone, School, IdCard } from 'lucide-vue-next'
import { getProfile, type StudentProfile } from '@/api/modules/student'

const router = useRouter()
const userStore = useUserStore()

const profile = ref<StudentProfile | null>(null)
const loading = ref(false)

// 获取学生详细信息
const fetchProfile = async () => {
  try {
    loading.value = true
    profile.value = await getProfile()
  } catch (err: any) {
  } finally {
    loading.value = false
  }
}

const handleLogout = () => {
  userStore.logout()
  router.push('/login')
}

const userInfo = userStore.userInfo

onMounted(() => {
  fetchProfile()
})
</script>

<template>
  <div class="pb-4 space-y-4">
    <!-- 用户信息卡片 -->
    <Card class="py-3 !bg-transparent border-0 shadow-none">
      <CardContent class="p-3">
        <div class="flex items-center gap-4">
          <!-- 头像 -->
          <div class="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center">
            <User class="w-8 h-8 text-primary" />
          </div>

          <!-- 用户基本信息 -->
          <div class="flex-1">
            <h2 class="text-lg font-semibold">{{ profile?.name || userInfo?.name || '未设置' }}</h2>
            <p class="text-sm text-gray-500">{{ profile?.school_name || userInfo?.school_name || '未选择学校' }}</p>
          </div>
        </div>
      </CardContent>
    </Card>

    <!-- 详细信息 -->
    <Card class="py-3 bg-white rounded-lg border-0 shadow-none">
      <CardContent class="p-0">
        <div>
          <!-- 学号 -->
          <div class="flex items-center gap-3 p-3">
            <IdCard class="w-5 h-5 text-gray-400" />
            <span class="text-sm text-gray-600 w-20">学号</span>
            <span class="text-sm flex-1">{{ profile?.student_no || '未设置' }}</span>
          </div>

          <!-- 手机号 -->
          <div class="flex items-center gap-3 p-3">
            <Phone class="w-5 h-5 text-gray-400" />
            <span class="text-sm text-gray-600 w-20">手机号</span>
            <span class="text-sm flex-1">{{ profile?.phone || userInfo?.phone || '未设置' }}</span>
          </div>

          <!-- 邮箱 -->
          <div class="flex items-center gap-3 p-3">
            <Mail class="w-5 h-5 text-gray-400" />
            <span class="text-sm text-gray-600 w-20">邮箱</span>
            <span class="text-sm flex-1">{{ profile?.email || '未设置' }}</span>
          </div>

          <!-- 专业 -->
          <div class="flex items-center gap-3 p-3">
            <School class="w-5 h-5 text-gray-400" />
            <span class="text-sm text-gray-600 w-20">专业</span>
            <span class="text-sm flex-1">{{ profile?.major || '未设置' }}</span>
          </div>
        </div>
      </CardContent>
    </Card>

    <!-- 退出登录按钮 -->
    <Button
      variant="outline"
      class="w-full text-red-600 border-red-200 hover:bg-red-50 hover:text-red-700"
      @click="handleLogout"
    >
      <LogOut class="w-4 h-4 mr-2" />
      退出登录
    </Button>
  </div>
</template>
