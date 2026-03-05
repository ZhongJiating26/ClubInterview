<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import {
  getInterviewSessions,
  deleteInterviewSession,
  type InterviewSession,
} from '@/api/modules/interview'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Calendar, MapPin, Users, Plus, ArrowRight, Trash2, AlertTriangle } from 'lucide-vue-next'

const router = useRouter()
const userStore = useUserStore()

// 面试场次列表
const sessions = ref<InterviewSession[]>([])
const loading = ref(false)
const error = ref('')

// 删除确认弹窗
const showDeleteDialog = ref(false)
const selectedSession = ref<InterviewSession | null>(null)
const deleteLoading = ref(false)

// 获取社团 ID
const getClubId = () => {
  return userStore.userInfo?.roles.find((r) => r.code === 'CLUB_ADMIN')?.club_id
}

// 获取面试场次列表
const fetchSessions = async () => {
  const clubId = getClubId()
  if (!clubId) {
    error.value = '未找到社团信息'
    return
  }

  try {
    loading.value = true
    error.value = ''
    const res = await getInterviewSessions({ club_id: clubId })
    sessions.value = res
  } catch (err: any) {
    error.value = err.message || '获取面试场次列表失败'
  } finally {
    loading.value = false
  }
}

// 跳转到向导页面
const goToWizard = () => {
  router.push('/admin/interviews/wizard')
}

// 跳转到编辑页面
const goToEdit = (sessionId: number) => {
  router.push(`/admin/interviews/wizard?id=${sessionId}`)
}

// 打开删除确认弹窗
const openDeleteDialog = (session: InterviewSession, event: Event) => {
  event.stopPropagation() // 阻止触发卡片点击
  selectedSession.value = session
  showDeleteDialog.value = true
}

// 删除面试场次
const handleDelete = async () => {
  if (!selectedSession.value) return

  try {
    deleteLoading.value = true
    await deleteInterviewSession(selectedSession.value.id)
    showDeleteDialog.value = false
    // 刷新列表
    await fetchSessions()
  } catch (err: any) {
    error.value = err.message || '删除失败'
  } finally {
    deleteLoading.value = false
  }
}

// 获取动态状态（基于时间和 status）
const getDynamicStatus = (session: InterviewSession) => {
  if (session.status === 'DRAFT') {
    return { text: '草稿', variant: 'outline' as const }
  }

  const now = new Date()
  const startTime = new Date(session.start_time)
  const endTime = new Date(session.end_time)

  if (now < startTime) {
    return { text: '未到时间', variant: 'outline' as const }
  } else if (now >= startTime && now <= endTime) {
    return { text: '进行中', variant: 'default' as const }
  } else {
    return { text: '已截止', variant: 'secondary' as const }
  }
}

// 状态文本（保留用于兼容）
const getStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    DRAFT: '草稿',
    OPEN: '进行中',
    CLOSED: '已结束',
  }
  return statusMap[status] || status
}

// 状态样式（保留用于兼容）
const getStatusVariant = (status: string): 'default' | 'secondary' | 'destructive' | 'outline' => {
  switch (status) {
    case 'OPEN':
      return 'default'
    case 'CLOSED':
      return 'secondary'
    case 'DRAFT':
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

// 所有场次都可以删除
const canDelete = (session: InterviewSession) => {
  return true
}

onMounted(() => {
  fetchSessions()
})
</script>

<template>
  <div class="flex flex-col flex-1 overflow-hidden">
    <div class="flex-1 min-h-0 overflow-y-auto p-6">
      <div class="flex items-center justify-between mb-6">
        <h1 class="text-2xl font-bold">面试场次</h1>
        <Button @click="goToWizard">
          <Plus class="w-4 h-4 mr-2" />
          新建面试场次
        </Button>
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
          class="border-0 hover:shadow-md transition-shadow cursor-pointer"
          @click="goToEdit(session.id)"
        >
          <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle class="text-lg">{{ session.name }}</CardTitle>
            <div class="flex items-center gap-2">
              <Badge :variant="getDynamicStatus(session).variant">
                {{ getDynamicStatus(session).text }}
              </Badge>
              <!-- 删除按钮（所有状态都显示） -->
              <Button
                variant="ghost"
                size="icon"
                class="h-8 w-8 text-red-500 hover:text-red-600 hover:bg-red-50"
                @click="openDeleteDialog(session, $event)"
              >
                <Trash2 class="w-4 h-4" />
              </Button>
            </div>
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
            <div class="pt-2">
              <Button variant="outline" size="sm" class="w-full" @click="goToEdit(session.id)">
                <ArrowRight class="w-3 h-3 mr-1" />
                管理
              </Button>
            </div>
          </CardContent>
        </Card>

        <!-- 空状态 -->
        <div v-if="sessions.length === 0 && !loading" class="col-span-full">
          <Card class="border-0">
            <CardContent class="flex flex-col items-center justify-center py-12">
              <p class="text-muted-foreground mb-4">暂无面试场次，点击下方按钮创建</p>
              <Button @click="goToWizard">
                <Plus class="w-4 h-4 mr-2" />
                新建面试场次
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

    <!-- 删除确认弹窗 -->
    <Dialog :open="showDeleteDialog" @update:open="showDeleteDialog = $event">
      <DialogContent class="max-w-md">
        <DialogHeader>
          <DialogTitle class="flex items-center gap-2">
            <AlertTriangle class="w-5 h-5 text-red-500" />
            删除面试场次
          </DialogTitle>
          <DialogDescription>
            确定要删除面试场次「{{ selectedSession?.name }}」吗？此操作不可恢复。
          </DialogDescription>
        </DialogHeader>

        <div class="py-4">
          <div class="bg-muted rounded-md p-4 space-y-2 text-sm">
            <div class="flex justify-between">
              <span class="text-muted-foreground">场次名称</span>
              <span class="font-medium">{{ selectedSession?.name }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-muted-foreground">状态</span>
              <Badge v-if="selectedSession" :variant="getDynamicStatus(selectedSession).variant">
                {{ selectedSession && getDynamicStatus(selectedSession).text }}
              </Badge>
            </div>
            <div class="flex justify-between">
              <span class="text-muted-foreground">面试时间</span>
              <span class="font-medium">{{ selectedSession && formatDate(selectedSession.start_time) }}</span>
            </div>
          </div>
          <p class="text-sm text-muted-foreground mt-4">
            注意：删除后，该场次的所有关联数据（面试官分配、候选人排期等）都将被删除。
          </p>
        </div>

        <DialogFooter>
          <Button variant="outline" @click="showDeleteDialog = false" :disabled="deleteLoading">
            取消
          </Button>
          <Button
            variant="destructive"
            @click="handleDelete"
            :disabled="deleteLoading"
          >
            {{ deleteLoading ? '删除中...' : '确认删除' }}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  </div>
</template>
