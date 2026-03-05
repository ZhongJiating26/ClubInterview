<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import {
  getMyInvitations,
  acceptInvitation,
  rejectInvitation,
  type InterviewerInvitation,
} from '@/api/modules/invitation'
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
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Building2, User, Check, X, Clock } from 'lucide-vue-next'

// 邀请列表
const invitations = ref<InterviewerInvitation[]>([])
const loading = ref(false)
const error = ref('')
const success = ref('')

// 拒绝弹窗
const showRejectDialog = ref(false)
const selectedInvitation = ref<InterviewerInvitation | null>(null)
const rejectReason = ref('')
const rejectLoading = ref(false)

// 接受弹窗
const showAcceptDialog = ref(false)
const acceptLoading = ref(false)

// 状态文本
const statusText: Record<string, string> = {
  PENDING: '待处理',
  ACCEPTED: '已接受',
  REJECTED: '已拒绝',
  EXPIRED: '已过期',
}

// 状态样式
const getStatusVariant = (status: string): 'default' | 'secondary' | 'destructive' | 'outline' => {
  switch (status) {
    case 'ACCEPTED':
      return 'default'
    case 'PENDING':
      return 'secondary'
    case 'REJECTED':
    case 'EXPIRED':
      return 'destructive'
    default:
      return 'outline'
  }
}

// 格式化日期
const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

// 获取邀请列表
const fetchInvitations = async () => {
  try {
    loading.value = true
    error.value = ''
    const res = await getMyInvitations()
    // 兼容 { items: [...] } 或 [...] 两种格式
    invitations.value = Array.isArray(res) ? res : (res.items || [])
  } catch (err: any) {
    error.value = err.message || '获取邀请列表失败'
  } finally {
    loading.value = false
  }
}

// 打开发送拒绝弹窗
const openRejectDialog = (invitation: InterviewerInvitation) => {
  selectedInvitation.value = invitation
  rejectReason.value = ''
  showRejectDialog.value = true
}

// 拒绝邀请
const handleReject = async () => {
  if (!selectedInvitation.value) return

  try {
    rejectLoading.value = true
    await rejectInvitation(selectedInvitation.value.id, rejectReason.value || undefined)
    success.value = '已拒绝邀请'
    showRejectDialog.value = false
    await fetchInvitations()
  } catch (err: any) {
    error.value = err.message || '操作失败'
  } finally {
    rejectLoading.value = false
  }
}

// 打开发送接受弹窗
const openAcceptDialog = (invitation: InterviewerInvitation) => {
  selectedInvitation.value = invitation
  showAcceptDialog.value = true
}

// 接受邀请
const handleAccept = async () => {
  if (!selectedInvitation.value) return

  try {
    acceptLoading.value = true
    await acceptInvitation(selectedInvitation.value.id)
    success.value = '已接受邀请，成为该社团面试官'
    showAcceptDialog.value = false
    await fetchInvitations()
  } catch (err: any) {
    error.value = err.message || '操作失败'
  } finally {
    acceptLoading.value = false
  }
}

// 待处理的邀请
const pendingInvitations = computed(() =>
  invitations.value.filter((i) => i.status === 'PENDING')
)

// 已处理的邀请
const processedInvitations = computed(() =>
  invitations.value.filter((i) => i.status !== 'PENDING')
)

onMounted(() => {
  fetchInvitations()
})
</script>

<template>
  <div class="flex flex-col flex-1 overflow-hidden">
    <div class="flex-1 min-h-0 overflow-y-auto p-6">
      <div class="mb-6">
        <h1 class="text-2xl font-bold mb-2">加入社团</h1>
        <p class="text-muted-foreground">查看并处理成为面试官的邀请</p>
      </div>

      <!-- 错误提示 -->
      <div v-if="error" class="mb-4 p-3 text-sm text-red-600 bg-red-50 rounded-md">
        {{ error }}
      </div>

      <!-- 成功提示 -->
      <div v-if="success" class="mb-4 p-3 text-sm text-green-600 bg-green-50 rounded-md">
        {{ success }}
      </div>

      <!-- 待处理的邀请 -->
      <div v-if="pendingInvitations.length > 0" class="mb-8">
        <h2 class="text-lg font-semibold mb-4 flex items-center gap-2">
          <Clock class="w-5 h-5 text-yellow-500" />
          待处理 ({{ pendingInvitations.length }})
        </h2>
        <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          <Card
            v-for="invitation in pendingInvitations"
            :key="invitation.id"
            class="border-yellow-200 bg-yellow-50/50"
          >
            <CardHeader class="flex flex-row items-center gap-4 pb-2">
              <div class="flex items-center justify-center w-12 h-12 rounded-lg bg-primary/10">
                <Building2 class="w-6 h-6 text-primary" />
              </div>
              <div>
                <CardTitle class="text-lg">{{ invitation.club_name }}</CardTitle>
                <Badge variant="secondary" class="mt-1">
                  {{ statusText[invitation.status] }}
                </Badge>
              </div>
            </CardHeader>
            <CardContent class="space-y-4">
              <div class="text-sm text-muted-foreground">
                邀请人：{{ invitation.inviter_name || '管理员' }}
              </div>
              <div class="text-sm text-muted-foreground">
                收到时间：{{ formatDate(invitation.created_at) }}
              </div>
              <div class="flex gap-2">
                <Button
                  class="flex-1"
                  @click="openAcceptDialog(invitation)"
                >
                  <Check class="w-4 h-4 mr-1" />
                  接受
                </Button>
                <Button
                  variant="outline"
                  class="flex-1"
                  @click="openRejectDialog(invitation)"
                >
                  <X class="w-4 h-4 mr-1" />
                  拒绝
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      <!-- 无待处理邀请 -->
      <div v-else-if="invitations.length > 0" class="mb-8">
        <h2 class="text-lg font-semibold mb-4 flex items-center gap-2">
          <Clock class="w-5 h-5 text-gray-400" />
          待处理
        </h2>
        <Card class="border-dashed">
          <CardContent class="flex flex-col items-center justify-center py-8">
            <p class="text-muted-foreground">暂无待处理的邀请</p>
          </CardContent>
        </Card>
      </div>

      <!-- 已处理的邀请 -->
      <div v-if="processedInvitations.length > 0">
        <h2 class="text-lg font-semibold mb-4">历史记录</h2>
        <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          <Card v-for="invitation in processedInvitations" :key="invitation.id">
            <CardHeader class="flex flex-row items-center gap-4 pb-2">
              <div class="flex items-center justify-center w-12 h-12 rounded-lg bg-muted">
                <Building2 class="w-6 h-6 text-muted-foreground" />
              </div>
              <div>
                <CardTitle class="text-lg">{{ invitation.club_name }}</CardTitle>
                <Badge :variant="getStatusVariant(invitation.status)" class="mt-1">
                  {{ statusText[invitation.status] }}
                </Badge>
              </div>
            </CardHeader>
            <CardContent class="space-y-2 text-sm text-muted-foreground">
              <div>邀请人：{{ invitation.inviter_name || '管理员' }}</div>
              <div>收到时间：{{ formatDate(invitation.created_at) }}</div>
            </CardContent>
          </Card>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-if="invitations.length === 0 && !loading" class="text-center py-12">
        <Card class="border-dashed">
          <CardContent class="flex flex-col items-center justify-center py-12">
            <Building2 class="w-12 h-12 text-muted-foreground mb-4" />
            <p class="text-muted-foreground mb-2">暂无邀请</p>
            <p class="text-sm text-muted-foreground">
              收到社团管理员邀请后会显示在这里
            </p>
          </CardContent>
        </Card>
      </div>

      <!-- 加载状态 -->
      <div v-if="loading" class="text-center py-12">
        <p class="text-muted-foreground">加载中...</p>
      </div>
    </div>

    <!-- 接受确认弹窗 -->
    <Dialog :open="showAcceptDialog" @update:open="showAcceptDialog = $event">
      <DialogContent class="max-w-md">
        <DialogHeader>
          <DialogTitle>接受邀请</DialogTitle>
          <DialogDescription>
            确认接受「{{ selectedInvitation?.club_name }}」的面试官邀请吗？
          </DialogDescription>
        </DialogHeader>
        <div class="py-4">
          <p class="text-sm text-muted-foreground">
            接受后您将成为该社团的面试官，可以参与面试评分等工作。
          </p>
        </div>
        <DialogFooter>
          <Button variant="outline" @click="showAcceptDialog = false">取消</Button>
          <Button @click="handleAccept" :disabled="acceptLoading">
            {{ acceptLoading ? '处理中...' : '确认接受' }}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>

    <!-- 拒绝确认弹窗 -->
    <Dialog :open="showRejectDialog" @update:open="showRejectDialog = $event">
      <DialogContent class="max-w-md">
        <DialogHeader>
          <DialogTitle>拒绝邀请</DialogTitle>
          <DialogDescription>
            确认拒绝「{{ selectedInvitation?.club_name }}」的面试官邀请吗？
          </DialogDescription>
        </DialogHeader>
        <div class="space-y-4 py-4">
          <div class="space-y-2">
            <Label for="reason">拒绝理由（可选）</Label>
            <Textarea
              id="reason"
              v-model="rejectReason"
              placeholder="请输入拒绝理由..."
              rows="3"
            />
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" @click="showRejectDialog = false">取消</Button>
          <Button
            variant="destructive"
            @click="handleReject"
            :disabled="rejectLoading"
          >
            {{ rejectLoading ? '处理中...' : '确认拒绝' }}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  </div>
</template>
