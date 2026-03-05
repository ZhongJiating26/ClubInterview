<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  getRecruitmentSession,
  getSessionPositions,
  type RecruitmentSession,
  type SessionPosition,
} from '@/api/modules/recruitment'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { ArrowLeft, Calendar, Users, FileText, Building2 } from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()

// 场次信息
const session = ref<RecruitmentSession | null>(null)
const positions = ref<SessionPosition[]>([])
const loading = ref(false)
const error = ref('')

// 获取场次 ID
const sessionId = Number(route.params.id)

// 获取场次详情
const fetchSessionDetail = async () => {
  if (!sessionId) {
    error.value = '无效的场次 ID'
    return
  }

  try {
    loading.value = true
    error.value = ''

    // 并行获取场次详情和岗位列表
    const [sessionData, positionsData] = await Promise.all([
      getRecruitmentSession(sessionId),
      getSessionPositions(sessionId)
    ])

    session.value = sessionData
    positions.value = positionsData
  } catch (err: any) {
    error.value = err.message || '获取场次详情失败'
  } finally {
    loading.value = false
  }
}

// 返回列表页
const goBack = () => {
  router.push('/interviewer/applications/sessions')
}

// 获取动态状态（基于时间和 status）
const getDynamicStatus = () => {
  if (!session.value) return { text: '未知', variant: 'outline' as const }

  if (session.value.status === 'DRAFT') {
    return { text: '草稿', variant: 'secondary' as const }
  }

  const now = new Date()
  const startTime = new Date(session.value.start_time)
  const endTime = new Date(session.value.end_time)

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
  fetchSessionDetail()
})
</script>

<template>
  <div class="absolute inset-0 flex flex-col">
    <!-- 头部固定部分 -->
    <div class="flex-shrink-0 px-6 pt-6 pb-4">
      <div class="flex items-center gap-4 mb-4">
        <Button variant="ghost" size="sm" @click="goBack">
          <ArrowLeft class="w-4 h-4 mr-1" />
          返回
        </Button>
        <h1 class="text-2xl font-bold">场次详情</h1>
      </div>

      <!-- 错误提示 -->
      <div v-if="error" class="p-3 text-sm text-red-600 bg-red-50 rounded-md">
        {{ error }}
      </div>
    </div>

    <!-- 滚动内容区域 -->
    <div class="flex-1 min-h-0 overflow-y-auto px-6 pb-6">
      <!-- 加载状态 -->
      <div v-if="loading" class="text-center py-12">
        <p class="text-muted-foreground">加载中...</p>
      </div>

      <!-- 内容区域 -->
      <div v-else-if="session" class="space-y-6">
        <!-- 场次基本信息 -->
        <Card>
          <CardHeader>
            <div class="flex items-start justify-between">
              <div class="flex-1">
                <CardTitle class="text-2xl mb-2">{{ session.name }}</CardTitle>
                <Badge :variant="getDynamicStatus().variant">
                  {{ getDynamicStatus().text }}
                </Badge>
              </div>
            </div>
          </CardHeader>
          <CardContent class="space-y-4">
            <div v-if="session.description" class="flex items-start gap-3">
              <FileText class="w-5 h-5 text-muted-foreground mt-0.5 flex-shrink-0" />
              <div>
                <p class="text-sm font-medium mb-1">描述</p>
                <p class="text-sm text-muted-foreground">{{ session.description }}</p>
              </div>
            </div>

            <div class="flex items-center gap-3">
              <Calendar class="w-5 h-5 text-muted-foreground flex-shrink-0" />
              <div class="flex-1">
                <p class="text-sm font-medium mb-1">报名时间</p>
                <p class="text-sm text-muted-foreground">
                  {{ formatDate(session.start_time) }} 至 {{ formatDate(session.end_time) }}
                </p>
              </div>
            </div>

            <div class="flex items-center gap-3">
              <Users class="w-5 h-5 text-muted-foreground flex-shrink-0" />
              <div>
                <p class="text-sm font-medium mb-1">报名上限</p>
                <p class="text-sm text-muted-foreground">{{ session.max_candidates }} 人</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <!-- 岗位列表 -->
        <Card>
          <CardHeader>
            <CardTitle class="flex items-center gap-2">
              <Building2 class="w-5 h-5" />
              招聘岗位 ({{ positions.length }})
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div v-if="positions.length > 0" class="space-y-4">
              <div
                v-for="position in positions"
                :key="position.id"
                class="border rounded-lg p-4 hover:bg-muted/50 transition-colors"
              >
                <div class="flex items-start justify-between mb-2">
                  <h3 class="font-semibold text-lg">{{ position.position_name }}</h3>
                  <Badge variant="outline">
                    招聘 {{ position.recruit_quota }} 人
                  </Badge>
                </div>

                <div v-if="position.position_description" class="text-sm text-muted-foreground mb-2">
                  <span class="font-medium">岗位描述：</span>
                  {{ position.position_description }}
                </div>

                <div v-if="position.position_requirement" class="text-sm text-muted-foreground">
                  <span class="font-medium">岗位要求：</span>
                  {{ position.position_requirement }}
                </div>
              </div>
            </div>

            <!-- 空状态 -->
            <div v-else class="text-center py-8 text-muted-foreground">
              暂无招聘岗位
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  </div>
</template>
