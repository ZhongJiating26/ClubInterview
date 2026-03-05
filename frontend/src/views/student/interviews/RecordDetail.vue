<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getMyInterviewRecordDetail } from '@/api/modules/interview'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { ArrowLeft, Calendar, Clock, MapPin, User, FileText, Star, CheckCircle, XCircle, AlertCircle } from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()

const candidateId = Number(route.params.candidateId)
const record = ref<any>(null)
const loading = ref(false)
const error = ref('')

// 获取面试记录详情
const fetchDetail = async () => {
  try {
    loading.value = true
    error.value = ''
    record.value = await getMyInterviewRecordDetail(candidateId)
  } catch (err: any) {
    error.value = err.message || '获取面试记录详情失败'
  } finally {
    loading.value = false
  }
}

// 返回
const goBack = () => {
  router.back()
}

// 获取面试状态信息
const getStatusInfo = (status: string) => {
  const infoMap: Record<string, { text: string; icon: any; variant: 'default' | 'secondary' | 'destructive' | 'outline'; color: string }> = {
    SCHEDULED: { text: '已安排', icon: Calendar, variant: 'outline', color: 'text-gray-600' },
    CONFIRMED: { text: '已确认', icon: CheckCircle, variant: 'default', color: 'text-green-600' },
    CANCELLED: { text: '已取消', icon: XCircle, variant: 'secondary', color: 'text-gray-600' },
    COMPLETED: { text: '已完成', icon: Star, variant: 'default', color: 'text-blue-600' },
    NO_SHOW: { text: '未到场', icon: AlertCircle, variant: 'destructive', color: 'text-red-600' }
  }
  return infoMap[status] || { text: status, icon: Calendar, variant: 'outline', color: 'text-gray-600' }
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
        <h1 class="text-base font-semibold">面试详情</h1>
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
    <div v-else-if="record" class="flex-1 p-4 space-y-4 pb-24">
      <!-- 状态信息 -->
      <div class="bg-white rounded-lg p-4">
        <div class="flex items-center gap-4 mb-4">
          <div class="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center">
            <User class="w-6 h-6 text-primary" />
          </div>
          <div class="flex-1">
            <h2 class="text-2xl font-bold mb-1">{{ record.position_name || '面试' }}</h2>
            <p v-if="record.department_name" class="text-sm text-gray-500">{{ record.department_name }}</p>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <component :is="getStatusInfo(record.status).icon" class="w-5 h-5" :class="getStatusInfo(record.status).color" />
          <span class="font-medium" :class="getStatusInfo(record.status).color">
            {{ getStatusInfo(record.status).text }}
          </span>
        </div>
      </div>

      <!-- 面试时间 -->
      <div class="bg-white rounded-lg p-4 space-y-3">
        <h3 class="text-base font-semibold">面试时间</h3>
        <div class="bg-gray-50 p-3 rounded-lg">
          <div class="flex justify-between items-center mb-2">
            <span class="text-sm text-gray-500">开始时间</span>
            <span class="font-medium">{{ formatDate(record.planned_start_time) }}</span>
          </div>
          <div class="flex justify-between items-center">
            <span class="text-sm text-gray-500">结束时间</span>
            <span class="font-medium">{{ formatDate(record.planned_end_time) }}</span>
          </div>
        </div>
        <div v-if="record.actual_start_time" class="bg-green-50 p-3 rounded-lg border border-green-200">
          <div class="flex justify-between items-center">
            <span class="text-sm text-green-700">实际开始</span>
            <span class="font-medium text-green-700">{{ formatDate(record.actual_start_time) }}</span>
          </div>
        </div>
        <div v-if="record.actual_end_time" class="bg-green-50 p-3 rounded-lg border border-green-200">
          <div class="flex justify-between items-center">
            <span class="text-sm text-green-700">实际结束</span>
            <span class="font-medium text-green-700">{{ formatDate(record.actual_end_time) }}</span>
          </div>
        </div>
      </div>

      <!-- 面试地点 -->
      <div v-if="record.session" class="bg-white rounded-lg p-4 space-y-3">
        <h3 class="text-base font-semibold">面试信息</h3>
        <div class="bg-gray-50 p-3 rounded-lg space-y-2">
          <div class="flex justify-between items-center">
            <span class="text-sm text-gray-500">面试场次</span>
            <span class="font-medium">{{ record.session.name }}</span>
          </div>
          <div class="flex justify-between items-center">
            <span class="text-sm text-gray-500">面试地点</span>
            <span class="font-medium">{{ record.session.place || '暂未安排' }}</span>
          </div>
        </div>
      </div>

      <!-- 面试得分 -->
      <div v-if="record.final_score !== null" class="bg-white rounded-lg p-4 space-y-3">
        <h3 class="text-base font-semibold flex items-center gap-2">
          <Star class="w-5 h-5 text-yellow-500" />
          面试得分
        </h3>
        <div class="text-center py-6">
          <p class="text-5xl font-bold text-primary mb-2">{{ record.final_score }}</p>
          <p class="text-sm text-gray-500">最终得分</p>
        </div>
      </div>

      <!-- 报名信息 -->
      <div v-if="record.application" class="bg-white rounded-lg p-4 space-y-3">
        <h3 class="text-base font-semibold flex items-center gap-2">
          <FileText class="w-5 h-5" />
          报名信息
        </h3>
        <div class="bg-gray-50 p-3 rounded-lg space-y-2">
          <div class="flex justify-between items-center">
            <span class="text-sm text-gray-500">报名场次</span>
            <span class="font-medium">{{ record.application.session_name || '-' }}</span>
          </div>
          <div class="flex justify-between items-center">
            <span class="text-sm text-gray-500">报名状态</span>
            <Badge variant="outline">
              {{ record.application.status === 'APPROVED' ? '已通过' : record.application.status === 'PENDING' ? '待审核' : '已拒绝' }}
            </Badge>
          </div>
        </div>
      </div>

      <!-- 自我介绍 -->
      <div v-if="record.application && record.application.self_intro" class="bg-white rounded-lg p-4">
        <h3 class="text-base font-semibold mb-3">自我介绍</h3>
        <p class="text-sm text-gray-600 whitespace-pre-wrap">{{ record.application.self_intro }}</p>
      </div>
    </div>
  </div>
</template>
