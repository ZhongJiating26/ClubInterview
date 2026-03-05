<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import {
  getInterviewSessions,
  type InterviewSession,
} from '@/api/modules/interview'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Calendar, MapPin, Users, ArrowRight } from 'lucide-vue-next'

const userStore = useUserStore()

// 面试场次列表
const sessions = ref<InterviewSession[]>([])
const loading = ref(false)
const error = ref('')

// 获取社团 ID
const getClubId = () => {
  return userStore.userInfo?.roles.find((r) => r.code === 'INTERVIEWER')?.club_id
}

// 获取面试场次列表
const fetchSessions = async () => {
  const clubId = getClubId()
  if (!clubId) {
    error.value = '未找到社团信息，请先接受社团邀请'
    return
  }

  try {
    loading.value = true
    const res = await getInterviewSessions({ club_id: clubId })
    sessions.value = res
  } catch (err: any) {
    error.value = err.message || '获取面试场次列表失败'
  } finally {
    loading.value = false
  }
}

// 状态文本
const getStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    DRAFT: '草稿',
    OPEN: '进行中',
    CLOSED: '已结束',
  }
  return statusMap[status] || status
}

// 状态样式
const getStatusClass = (status: string) => {
  switch (status) {
    case 'OPEN':
      return 'bg-green-100 text-green-800'
    case 'CLOSED':
      return 'bg-gray-100 text-gray-800'
    case 'DRAFT':
      return 'bg-yellow-100 text-yellow-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
}

// 格式化日期
const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

onMounted(() => {
  fetchSessions()
})
</script>

<template>
  <div class="flex flex-col flex-1 overflow-hidden">
    <div class="flex-1 min-h-0 overflow-y-auto p-6">
      <div class="mb-6">
        <h1 class="text-2xl font-bold">面试场次</h1>
      </div>

      <!-- 错误提示 -->
      <div v-if="error" class="mb-4 p-3 text-sm text-red-600 bg-red-50 rounded-md">
        {{ error }}
      </div>

      <!-- 面试场次列表 -->
      <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <Card
          v-for="session in sessions"
          :key="session.id"
          class="border-0 hover:shadow-md transition-shadow"
        >
          <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle class="text-lg">{{ session.name }}</CardTitle>
            <span :class="['px-2 py-1 text-xs rounded-full', getStatusClass(session.status)]">
              {{ getStatusText(session.status) }}
            </span>
          </CardHeader>
          <CardContent class="space-y-3">
            <div class="flex items-center gap-2 text-sm text-muted-foreground">
              <Calendar class="w-4 h-4" />
              <span>{{ formatDate(session.start_time) }} - {{ formatDate(session.end_time) }}</span>
            </div>
            <div v-if="session.place" class="flex items-center gap-2 text-sm text-muted-foreground">
              <MapPin class="w-4 h-4" />
              <span>{{ session.place }}</span>
            </div>
            <div class="flex items-center gap-2 text-sm text-muted-foreground">
              <Users class="w-4 h-4" />
              <span>
                {{ session.interviewer_count || 0 }} 位面试官
                <span v-if="session.candidate_count !== undefined" class="ml-2">
                  | {{ session.candidate_count }} 位候选人
                </span>
              </span>
            </div>
            <div v-if="session.description" class="text-sm text-muted-foreground line-clamp-2">
              {{ session.description }}
            </div>
          </CardContent>
        </Card>

        <!-- 空状态 -->
        <div v-if="sessions.length === 0 && !loading" class="col-span-full">
          <Card class="border-0">
            <CardContent class="flex flex-col items-center justify-center py-12">
              <p class="text-muted-foreground">暂无面试场次</p>
            </CardContent>
          </Card>
        </div>

        <!-- 加载状态 -->
        <div v-if="loading" class="col-span-full text-center py-12">
          <p class="text-muted-foreground">加载中...</p>
        </div>
      </div>
    </div>
  </div>
</template>
