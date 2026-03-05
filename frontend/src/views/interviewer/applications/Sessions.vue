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
import { Badge } from '@/components/ui/badge'
import { Calendar, Users, FileText, ArrowRight } from 'lucide-vue-next'

const router = useRouter()
const userStore = useUserStore()

// 招新场次列表
const sessions = ref<RecruitmentSession[]>([])
const loading = ref(false)
const error = ref('')

// 获取社团 ID
const getClubId = () => {
  return userStore.userInfo?.roles.find((r) => r.code === 'INTERVIEWER')?.club_id
}

// 获取招新场次列表
const fetchSessions = async () => {
  const clubId = getClubId()
  if (!clubId) {
    error.value = '未找到社团信息，请先接受社团邀请'
    return
  }

  try {
    loading.value = true
    error.value = ''
    const res = await getRecruitmentSessions({ club_id: clubId })
    sessions.value = res
  } catch (err: any) {
    error.value = err.message || '获取招新场次列表失败'
  } finally {
    loading.value = false
  }
}

// 查看场次详情
const viewDetails = (sessionId: number) => {
  router.push(`/interviewer/applications/session/${sessionId}`)
}

// 获取动态状态（基于时间和 status）
const getDynamicStatus = (session: RecruitmentSession) => {
  if (session.status === 'DRAFT') {
    return { text: '草稿', variant: 'secondary' as const }
  }

  const now = new Date()
  const startTime = new Date(session.start_time)
  const endTime = new Date(session.end_time)

  if (now < startTime) {
    return { text: '未开始', variant: 'outline' as const }
  } else if (now >= startTime && now <= endTime) {
    return { text: '进行中', variant: 'default' as const }
  } else {
    return { text: '已截止', variant: 'secondary' as const }
  }
}

// 格式化日期
const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(() => {
  fetchSessions()
})
</script>

<template>
  <div class="flex flex-col flex-1 overflow-hidden">
    <div class="flex-1 min-h-0 overflow-y-auto p-6">
      <div class="mb-6">
        <h1 class="text-2xl font-bold mb-2">报名场次</h1>
        <p class="text-muted-foreground">查看当前社团的招新报名场次</p>
      </div>

      <!-- 错误提示 -->
      <div v-if="error" class="mb-4 p-3 text-sm text-red-600 bg-red-50 rounded-md">
        {{ error }}
      </div>

      <!-- 招新场次列表 -->
      <div v-if="sessions.length > 0" class="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <Card
          v-for="session in sessions"
          :key="session.id"
          class="border-0 hover:shadow-md transition-shadow"
        >
          <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle class="text-lg">{{ session.name }}</CardTitle>
            <Badge :variant="getDynamicStatus(session).variant">
              {{ getDynamicStatus(session).text }}
            </Badge>
          </CardHeader>
          <CardContent class="space-y-3">
            <div class="flex items-center gap-2 text-sm text-muted-foreground">
              <Calendar class="w-4 h-4" />
              <span class="text-xs">
                {{ formatDate(session.start_time) }} - {{ formatDate(session.end_time) }}
              </span>
            </div>
            <div class="flex items-center gap-2 text-sm text-muted-foreground">
              <Users class="w-4 h-4" />
              <span>上限 {{ session.max_candidates }} 人</span>
            </div>
            <div v-if="session.description" class="flex items-start gap-2 text-sm">
              <FileText class="w-4 h-4 mt-0.5 flex-shrink-0" />
              <span class="line-clamp-2 text-muted-foreground">{{ session.description }}</span>
            </div>
            <div class="pt-2">
              <Button variant="outline" size="sm" class="w-full" @click="viewDetails(session.id)">
                <ArrowRight class="w-3 h-3 mr-1" />
                查看详情
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      <!-- 空状态 -->
      <Card v-else-if="!loading && !error" class="border-0">
        <CardContent class="flex flex-col items-center justify-center py-12">
          <Calendar class="w-12 h-12 text-muted-foreground mb-4" />
          <p class="text-muted-foreground mb-2">暂无招新场次</p>
          <p class="text-sm text-muted-foreground">
            等待管理员创建招新场次
          </p>
        </CardContent>
      </Card>

      <!-- 加载状态 -->
      <div v-if="loading" class="text-center py-12">
        <p class="text-muted-foreground">加载中...</p>
      </div>
    </div>
  </div>
</template>
