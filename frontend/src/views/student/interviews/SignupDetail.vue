<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getSignupApplicationDetail, type SignupApplication } from '@/api/modules/application'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { ArrowLeft, Calendar, Clock, FileText, Check, X } from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()

const signupId = Number(route.params.signupId)
const signup = ref<SignupApplication | null>(null)
const loading = ref(false)
const error = ref('')

// 获取报名详情
const fetchDetail = async () => {
  try {
    loading.value = true
    error.value = ''
    const data = await getSignupApplicationDetail(signupId)
    signup.value = data
  } catch (err: any) {
    error.value = err.message || '获取报名详情失败'
  } finally {
    loading.value = false
  }
}

// 返回
const goBack = () => {
  router.back()
}

// 获取报名状态文本
const getStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    PENDING: '待审核',
    APPROVED: '已通过',
    REJECTED: '已拒绝'
  }
  return statusMap[status] || status
}

// 获取报名状态样式
const getStatusVariant = (status: string): 'default' | 'secondary' | 'destructive' | 'outline' => {
  switch (status) {
    case 'APPROVED':
      return 'default'
    case 'REJECTED':
      return 'destructive'
    case 'PENDING':
      return 'outline'
    default:
      return 'outline'
  }
}

// 格式化日期
const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

onMounted(() => {
  fetchDetail()
})
</script>

<template>
  <div class="min-h-screen flex flex-col" style="background-color: #F8F8F8">
    <!-- 自定义顶部导航栏 -->
    <div class="sticky top-0 z-30 bg-white border-b border-gray-100">
      <div class="flex items-center justify-between px-4 py-3">
        <Button variant="ghost" size="icon" @click="goBack" class="h-8 w-8">
          <ArrowLeft class="h-5 w-5" />
        </Button>
        <h1 class="text-base font-semibold">报名详情</h1>
        <div class="h-8 w-8"></div>
      </div>
    </div>

    <!-- 错误提示 -->
    <div v-if="error" class="p-4">
      <div class="bg-red-50 text-red-600 p-4 rounded-lg">
        {{ error }}
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="flex-1 flex items-center justify-center">
      <p class="text-muted-foreground">加载中...</p>
    </div>

    <!-- 内容区域 -->
    <div v-else-if="signup" class="flex-1 p-4 space-y-4 pb-24">
      <!-- 状态信息 -->
      <div v-if="signup.session_name" class="flex items-center justify-between gap-4 mx-8">
        <h2 class="text-2xl font-bold break-words flex-1">{{ signup.session_name }}</h2>
        <Badge :variant="getStatusVariant(signup.status)" class="text-base px-3 py-1 flex-shrink-0">
          {{ getStatusText(signup.status) }}
        </Badge>
      </div>

      <!-- 基本信息 -->
      <div class="bg-white rounded-lg p-4 space-y-4">
        <h3 class="text-base font-semibold">基本信息</h3>

        <div class="flex items-center gap-3">
          <Calendar class="w-5 h-5 text-gray-500" />
          <div class="flex-1">
            <p class="text-sm text-gray-500">报名时间</p>
            <p class="font-medium">{{ formatDate(signup.created_at) }}</p>
          </div>
        </div>

        <div v-if="signup.audit_time" class="flex items-center gap-3">
          <Clock class="w-5 h-5 text-gray-500" />
          <div class="flex-1">
            <p class="text-sm text-gray-500">审核时间</p>
            <p class="font-medium">{{ formatDate(signup.audit_time) }}</p>
          </div>
        </div>

        <div v-if="signup.status === 'REJECTED' && signup.audit_reason" class="flex items-start gap-3 bg-red-50 p-4 rounded-lg">
          <X class="w-5 h-5 text-red-500 mt-0.5 flex-shrink-0" />
          <div class="flex-1">
            <p class="text-sm text-red-600 font-medium mb-1">拒绝原因</p>
            <p class="text-sm text-red-600">{{ signup.audit_reason }}</p>
          </div>
        </div>

        <div v-if="signup.status === 'APPROVED'" class="flex items-start gap-3 bg-green-50 p-4 rounded-lg">
          <Check class="w-5 h-5 text-green-500 mt-0.5 flex-shrink-0" />
          <div class="flex-1">
            <p class="text-sm text-green-600 font-medium">报名已通过，请留意面试通知</p>
          </div>
        </div>
      </div>

      <!-- 自我介绍 -->
      <div v-if="signup.self_intro" class="bg-white rounded-lg p-4">
        <h3 class="text-base font-semibold mb-3">自我介绍</h3>
        <p class="text-sm text-gray-600 whitespace-pre-wrap">{{ signup.self_intro }}</p>
      </div>

      <!-- 报名岗位 -->
      <div v-if="signup.items && signup.items.length > 0" class="bg-white rounded-lg p-4">
        <h3 class="text-base font-semibold mb-3">报名岗位 ({{ signup.items.length }})</h3>
        <div class="space-y-3">
          <div
            v-for="(item, index) in signup.items"
            :key="item.id"
            class="flex items-center gap-3 p-3 bg-gray-50 rounded-lg"
          >
            <div class="w-6 h-6 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-sm font-medium">
              {{ index + 1 }}
            </div>
            <div class="flex-1">
              <p class="font-medium text-sm">{{ item.position_name || `岗位 ${index + 1}` }}</p>
              <p v-if="item.department_name" class="text-xs text-gray-500">{{ item.department_name }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 附件 -->
      <div v-if="signup.attachments && signup.attachments.length > 0" class="bg-white rounded-lg p-4">
        <h3 class="text-base font-semibold mb-3">附件 ({{ signup.attachments.length }})</h3>
        <div class="space-y-2">
          <div
            v-for="attachment in signup.attachments"
            :key="attachment.id"
            class="flex items-center gap-2 p-3 bg-gray-50 rounded-lg"
          >
            <FileText class="w-5 h-5 text-gray-500" />
            <span class="flex-1 text-sm">{{ attachment.file_name || attachment.name || '附件' }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
