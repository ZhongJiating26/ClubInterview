<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import {
  getRecruitmentSessions,
  type RecruitmentSession,
} from '@/api/modules/recruitment'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Calendar, Users, AlignLeft, Plus, ArrowRight } from 'lucide-vue-next'

const router = useRouter()
const userStore = useUserStore()

// 招新场次列表
const sessions = ref<RecruitmentSession[]>([])
const loading = ref(false)
const error = ref('')

// 获取社团 ID
const getClubId = () => {
  return userStore.userInfo?.roles.find((r) => r.code === 'CLUB_ADMIN')?.club_id
}

// 获取招新场次列表
const fetchSessions = async () => {
  const clubId = getClubId()
  if (!clubId) {
    error.value = '未找到社团信息'
    return
  }

  try {
    loading.value = true
    const res = await getRecruitmentSessions({ club_id: clubId })
    sessions.value = res
  } catch (err: any) {
    error.value = err.message || '获取招新场次列表失败'
  } finally {
    loading.value = false
  }
}

// 跳转到编辑页面
const goToEdit = (sessionId: number) => {
  router.push(`/admin/applications/session/${sessionId}`)
}

// 跳转到新建向导
const goToCreate = () => {
  router.push('/admin/applications/session/new')
}

// 跳转到审核页面
const goToReview = (sessionId: number) => {
  router.push(`/admin/applications/review?session_id=${sessionId}`)
}

// 获取动态状态（基于时间和 status）
const getDynamicStatus = (session: RecruitmentSession) => {
  if (session.status === 'DRAFT') {
    return { text: '草稿', class: 'bg-yellow-100 text-yellow-800' }
  }

  const now = new Date()
  const startTime = new Date(session.start_time)
  const endTime = new Date(session.end_time)

  if (now < startTime) {
    return { text: '未到时间', class: 'bg-blue-100 text-blue-800' }
  } else if (now >= startTime && now <= endTime) {
    return { text: '发布中', class: 'bg-green-100 text-green-800' }
  } else {
    return { text: '已截止', class: 'bg-gray-100 text-gray-800' }
  }
}

// 状态文本（保留用于兼容）
const statusText: Record<string, string> = {
  DRAFT: '草稿',
  PUBLISHED: '发布中',
  CLOSED: '已结束',
}

// 状态样式（保留用于兼容）
const getStatusClass = (status: string) => {
  switch (status) {
    case 'PUBLISHED':
      return 'bg-green-100 text-green-800'
    case 'DRAFT':
      return 'bg-yellow-100 text-yellow-800'
    case 'CLOSED':
      return 'bg-gray-100 text-gray-800'
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
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold">发布报名</h1>
      <Button @click="goToCreate">
        <Plus class="w-4 h-4 mr-2" />
        新建招新场次
      </Button>
    </div>

    <!-- 错误提示 -->
    <div v-if="error" class="mb-4 p-3 text-sm text-red-600 bg-red-50 rounded-md">
      {{ error }}
    </div>

    <!-- 招新场次列表 -->
    <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      <Card v-for="session in sessions" :key="session.id" class="border-0 hover:shadow-md transition-shadow">
        <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle class="text-lg">{{ session.name }}</CardTitle>
          <span :class="['px-2 py-1 text-xs rounded-full', getDynamicStatus(session).class]">
            {{ getDynamicStatus(session).text }}
          </span>
        </CardHeader>
        <CardContent class="space-y-3">
          <div class="flex items-center gap-2 text-sm text-muted-foreground">
            <Calendar class="w-4 h-4 flex-shrink-0" />
            <span>{{ formatDate(session.start_time) }} - {{ formatDate(session.end_time) }}</span>
          </div>
          <div class="flex items-center gap-2 text-sm text-muted-foreground">
            <Users class="w-4 h-4 flex-shrink-0" />
            <span>上限 {{ session.max_candidates }} 人</span>
          </div>
          <div v-if="session.description" class="flex items-center gap-2 text-sm text-muted-foreground">
            <AlignLeft class="w-4 h-4 flex-shrink-0" />
            <span class="line-clamp-2">{{ session.description }}</span>
          </div>
          <div class="pt-2 flex gap-2">
            <Button variant="outline" size="sm" @click="goToEdit(session.id)">
              <ArrowRight class="w-3 h-3 mr-1" />
              管理
            </Button>
            <Button variant="outline" size="sm" @click="goToReview(session.id)">
              审核
            </Button>
          </div>
        </CardContent>
      </Card>

      <!-- 空状态 -->
      <div v-if="sessions.length === 0 && !loading" class="col-span-full">
        <Card class="border-0">
          <CardContent class="flex flex-col items-center justify-center py-12">
            <p class="text-muted-foreground mb-4">暂无招新场次，点击下方按钮创建</p>
            <Button @click="goToCreate">
              <Plus class="w-4 h-4 mr-2" />
              新建招新场次
            </Button>
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
