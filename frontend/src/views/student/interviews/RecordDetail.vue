<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getMyInterviewRecordDetail, confirmInterview, getMyInterviewResult } from '@/api/modules/interview'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { ArrowLeft, Calendar, Clock, MapPin, User, FileText, Star, CheckCircle, XCircle, AlertCircle, Loader2 } from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()

const candidateId = Number(route.params.candidateId)
const record = ref<any>(null)
const loading = ref(false)
const error = ref('')
const confirming = ref(false)
const successMessage = ref('')

// 面试结果
const interviewResult = ref<any>(null)
const loadingResult = ref(false)

// 是否可以确认/拒绝面试
const canConfirm = computed(() => {
  return record.value && record.value.status === 'SCHEDULED'
})

// 是否已完成面试
const isCompleted = computed(() => {
  return record.value && record.value.status === 'COMPLETED'
})

// 获取录取状态信息
const getDecisionInfo = (decision: string) => {
  const infoMap: Record<string, { text: string; icon: any; color: string; bgColor: string }> = {
    PASS: { text: '恭喜！您已通过面试', icon: CheckCircle, color: 'text-green-700', bgColor: 'bg-green-50 border-green-200' },
    REJECT: { text: '很遗憾，您未通过面试', icon: XCircle, color: 'text-red-700', bgColor: 'bg-red-50 border-red-200' },
    WAITLIST: { text: '您已被列入候补名单', icon: AlertCircle, color: 'text-yellow-700', bgColor: 'bg-yellow-50 border-yellow-200' }
  }
  return infoMap[decision] || { text: '面试结果待公布', icon: Clock, color: 'text-gray-700', bgColor: 'bg-gray-50 border-gray-200' }
}

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

// 确认面试
const handleConfirm = async () => {
  try {
    confirming.value = true
    error.value = ''
    await confirmInterview(candidateId, { status: 'CONFIRMED' })
    successMessage.value = '已确认面试'
    // 刷新详情
    await fetchDetail()
    setTimeout(() => {
      successMessage.value = ''
    }, 3000)
  } catch (err: any) {
    error.value = err.message || '确认面试失败'
  } finally {
    confirming.value = false
  }
}

// 拒绝面试
const handleReject = async () => {
  if (!confirm('确定要拒绝这次面试吗？')) {
    return
  }

  try {
    confirming.value = true
    error.value = ''
    await confirmInterview(candidateId, { status: 'REJECTED' })
    successMessage.value = '已拒绝面试'
    // 刷新详情
    await fetchDetail()
    setTimeout(() => {
      successMessage.value = ''
    }, 3000)
  } catch (err: any) {
    error.value = err.message || '拒绝面试失败'
  } finally {
    confirming.value = false
  }
}

// 获取面试结果
const fetchResult = async () => {
  try {
    loadingResult.value = true
    interviewResult.value = await getMyInterviewResult(candidateId)
  } catch (err: any) {
    // 如果获取失败，可能还没有结果，忽略错误
    console.warn('获取面试结果失败:', err.message)
  } finally {
    loadingResult.value = false
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
  fetchResult()
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

      <!-- 确认/拒绝面试按钮（仅 SCHEDULED 状态显示） -->
      <div v-if="canConfirm" class="bg-white rounded-lg p-4 space-y-3">
        <h3 class="text-base font-semibold">确认面试时间</h3>
        <p class="text-sm text-gray-500">请确认您是否能按时参加面试</p>
        <div class="flex gap-3 pt-2">
          <Button
            @click="handleConfirm"
            :disabled="confirming"
            class="flex-1"
          >
            <Loader2 v-if="confirming" class="w-4 h-4 mr-2 animate-spin" />
            <CheckCircle v-else class="w-4 h-4 mr-2" />
            确认参加
          </Button>
          <Button
            @click="handleReject"
            :disabled="confirming"
            variant="outline"
            class="flex-1"
          >
            <Loader2 v-if="confirming" class="w-4 h-4 mr-2 animate-spin" />
            <XCircle v-else class="w-4 h-4 mr-2" />
            无法参加
          </Button>
        </div>
      </div>

      <!-- 面试结果（仅 COMPLETED 状态且有结果时显示） -->
      <div v-if="isCompleted && interviewResult" class="rounded-lg p-4 border-2" :class="getDecisionInfo(interviewResult.decision || '').bgColor">
        <div class="flex items-start gap-3">
          <component :is="getDecisionInfo(interviewResult.decision || '').icon" class="w-6 h-6 mt-0.5 flex-shrink-0" :class="getDecisionInfo(interviewResult.decision || '').color" />
          <div class="flex-1">
            <h3 class="text-lg font-semibold mb-2" :class="getDecisionInfo(interviewResult.decision || '').color">
              {{ getDecisionInfo(interviewResult.decision || '').text }}
            </h3>
            <div v-if="interviewResult.decision === 'PASS' && interviewResult.position_name" class="bg-white p-3 rounded-lg mt-3">
              <p class="text-sm text-gray-600">录用岗位</p>
              <p class="font-medium">{{ interviewResult.position_name }}</p>
            </div>
            <div v-if="interviewResult.notes" class="bg-white p-3 rounded-lg mt-3">
              <p class="text-sm text-gray-600">备注</p>
              <p class="text-sm">{{ interviewResult.notes }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 成功提示 -->
      <div v-if="successMessage" class="bg-green-50 text-green-700 p-4 rounded-lg">
        {{ successMessage }}
      </div>

      <!-- 自我介绍 -->
      <div v-if="record.application && record.application.self_intro" class="bg-white rounded-lg p-4">
        <h3 class="text-base font-semibold mb-3">自我介绍</h3>
        <p class="text-sm text-gray-600 whitespace-pre-wrap">{{ record.application.self_intro }}</p>
      </div>
    </div>
  </div>
</template>
