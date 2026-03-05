<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import {
  getSignupApplications,
  getSignupApplicationDetail,
  auditSignupApplication,
  type SignupApplication,
  type SignupStatus,
} from '@/api/modules/application'
import {
  getRecruitmentSessions,
  type RecruitmentSession,
} from '@/api/modules/recruitment'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Check, X, Eye, User } from 'lucide-vue-next'

const route = useRoute()
const userStore = useUserStore()

// 报名列表
const applications = ref<SignupApplication[]>([])
const total = ref(0)
const loading = ref(false)
const error = ref('')
const success = ref('')

// 分页
const page = ref(1)
const pageSize = ref(20)
const statusFilter = ref<SignupStatus | 'all'>('all')

// 招新场次列表（用于筛选）
const sessions = ref<RecruitmentSession[]>([])
const selectedSessionId = ref<number | null>(null)

// 详情弹窗
const showDetailDialog = ref(false)
const currentApplication = ref<SignupApplication | null>(null)

// 审核弹窗
const showAuditDialog = ref(false)
const auditLoading = ref(false)
const auditForm = ref({
  status: 'APPROVED' as 'APPROVED' | 'REJECTED',
  reason: '',
})

// 获取社团 ID
const getClubId = () => {
  return userStore.userInfo?.roles.find((r) => r.code === 'CLUB_ADMIN')?.club_id
}

// 获取招新场次列表
const fetchSessions = async () => {
  const clubId = getClubId()
  if (!clubId) return

  try {
    const res = await getRecruitmentSessions({ club_id: clubId })
    sessions.value = res

    // 如果 URL 有 session_id 参数，设置为选中状态
    const sessionId = route.query.session_id
    if (sessionId) {
      selectedSessionId.value = Number(sessionId)
    } else if (res.length > 0) {
      selectedSessionId.value = res[0].id
    }
  } catch (err) {
  }
}

// 获取报名列表
const fetchApplications = async () => {
  if (!selectedSessionId.value) {
    applications.value = []
    total.value = 0
    return
  }

  try {
    loading.value = true
    error.value = ''

    const res = await getSignupApplications({
      recruitment_session_id: selectedSessionId.value,
      status: statusFilter.value === 'all' ? undefined : statusFilter.value,
      page: page.value,
      page_size: pageSize.value,
    })

    applications.value = res.items
    total.value = res.total
  } catch (err: any) {
    error.value = err.message || '获取报名列表失败'
  } finally {
    loading.value = false
  }
}

// 查看详情
const viewDetail = async (app: SignupApplication) => {
  try {
    const res = await getSignupApplicationDetail(app.id)
    currentApplication.value = res
    showDetailDialog.value = true
  } catch (err: any) {
    error.value = err.message || '获取详情失败'
  }
}

// 打开发送审核弹窗
const openAuditDialog = (app: SignupApplication, status: 'APPROVED' | 'REJECTED') => {
  currentApplication.value = app
  auditForm.value = {
    status,
    reason: status === 'REJECTED' ? '' : '',
  }
  showAuditDialog.value = true
}

// 提交审核
const handleAudit = async () => {
  if (!currentApplication.value) return

  if (auditForm.value.status === 'REJECTED' && !auditForm.value.reason.trim()) {
    error.value = '请输入拒绝理由'
    return
  }

  try {
    auditLoading.value = true
    error.value = ''

    await auditSignupApplication(currentApplication.value.id, auditForm.value)
    success.value = '审核完成'
    showAuditDialog.value = false
    await fetchApplications()
  } catch (err: any) {
    error.value = err.message || '审核失败'
  } finally {
    auditLoading.value = false
  }
}

// 状态文本
const statusText: Record<string, string> = {
  PENDING: '待审核',
  APPROVED: '已通过',
  REJECTED: '已拒绝',
}

// 状态样式
const getStatusVariant = (status: string): 'default' | 'secondary' | 'destructive' | 'outline' => {
  switch (status) {
    case 'APPROVED':
      return 'default'
    case 'PENDING':
      return 'secondary'
    case 'REJECTED':
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

// 筛选条件变化
const onFilterChange = () => {
  page.value = 1
  fetchApplications()
}

// 总页数
const totalPages = computed(() => Math.ceil(total.value / pageSize.value))

// 监听路由变化
watch(
  () => route.query.session_id,
  (newSessionId) => {
    if (newSessionId) {
      selectedSessionId.value = Number(newSessionId)
      fetchApplications()
    }
  }
)

onMounted(async () => {
  await fetchSessions()
  await fetchApplications()
})
</script>

<template>
  <div class="flex flex-col flex-1 overflow-hidden">
    <div class="flex-1 min-h-0 overflow-y-auto p-6">
      <div class="mb-6">
        <h1 class="text-2xl font-bold mb-4">报名审核</h1>

        <!-- 筛选器 -->
        <div class="flex gap-1 mb-4">
          <Select v-model="selectedSessionId" @update:model-value="fetchApplications">
            <SelectTrigger class="w-[200px] !gap-1">
              <SelectValue placeholder="选择招新场次" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem v-for="session in sessions" :key="session.id" :value="session.id.toString()">
                {{ session.name }}
              </SelectItem>
            </SelectContent>
          </Select>
          <Select v-model="statusFilter" @update:model-value="onFilterChange">
              <SelectTrigger class="!gap-1">
                <SelectValue placeholder="全部状态" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">全部状态</SelectItem>
                <SelectItem value="PENDING">待审核</SelectItem>
                <SelectItem value="APPROVED">已通过</SelectItem>
                <SelectItem value="REJECTED">已拒绝</SelectItem>
              </SelectContent>
            </Select>
          </div>
      </div>

      <!-- 错误提示 -->
      <div v-if="error" class="mb-4 p-3 text-sm text-destructive bg-destructive/10 rounded-md">
        {{ error }}
      </div>

      <!-- 成功提示 -->
      <div v-if="success" class="mb-4 p-3 text-sm text-green-600 bg-green-50 rounded-md">
        {{ success }}
      </div>

      <!-- 报名表格 -->
      <div class="border rounded-md">
        <Table>
          <TableCaption class="pb-4">
            共 {{ total }} 条报名记录
          </TableCaption>
          <TableHeader>
            <TableRow>
              <TableHead class="w-[100px]">报名ID</TableHead>
              <TableHead class="w-[140px]">报名人</TableHead>
              <TableHead>自我介绍</TableHead>
              <TableHead class="w-[100px]">状态</TableHead>
              <TableHead class="w-[180px]">报名时间</TableHead>
              <TableHead class="w-[180px]">审核时间</TableHead>
              <TableHead class="text-right min-w-[200px]">操作</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            <TableRow v-if="applications.length === 0 && !loading">
              <TableCell :colspan="7" class="h-24 text-center text-muted-foreground">
                暂无报名记录
              </TableCell>
            </TableRow>
            <TableRow v-else-if="loading">
              <TableCell :colspan="7" class="h-24 text-center text-muted-foreground">
                加载中...
              </TableCell>
            </TableRow>
            <TableRow v-for="app in applications" :key="app.id" class="hover:bg-muted/50">
              <TableCell class="font-medium">#{{ app.id }}</TableCell>
              <TableCell>
                <div class="flex flex-col">
                  <span class="font-medium">{{ app.user_name || `用户#${app.user_id}` }}</span>
                  <span v-if="app.user_phone" class="text-xs text-muted-foreground">{{ app.user_phone }}</span>
                </div>
              </TableCell>
              <TableCell>
                <div class="max-w-[300px] truncate text-sm text-muted-foreground">
                  {{ app.self_intro || '暂无自我介绍' }}
                </div>
              </TableCell>
              <TableCell>
                <Badge :variant="getStatusVariant(app.status)">
                  {{ statusText[app.status] }}
                </Badge>
              </TableCell>
              <TableCell class="text-sm text-muted-foreground">
                {{ formatDate(app.created_at) }}
              </TableCell>
              <TableCell class="text-sm text-muted-foreground">
                {{ formatDate(app.audit_time) }}
              </TableCell>
              <TableCell class="text-right">
                <div class="flex items-center justify-end gap-1">
                  <Button variant="ghost" size="sm" @click="viewDetail(app)">
                    <Eye class="w-4 h-4" />
                  </Button>
                  <Button
                    v-if="app.status === 'PENDING'"
                    variant="ghost"
                    size="sm"
                    class="text-green-600 hover:text-green-700 hover:bg-green-50"
                    @click="openAuditDialog(app, 'APPROVED')"
                  >
                    <Check class="w-4 h-4" />
                  </Button>
                  <Button
                    v-if="app.status === 'PENDING'"
                    variant="ghost"
                    size="sm"
                    class="text-destructive hover:text-destructive hover:bg-destructive/10"
                    @click="openAuditDialog(app, 'REJECTED')"
                  >
                    <X class="w-4 h-4" />
                  </Button>
                </div>
              </TableCell>
            </TableRow>
          </TableBody>
        </Table>
      </div>

      <!-- 分页 -->
      <div v-if="totalPages > 1" class="mt-4 flex items-center justify-center gap-2">
        <Button
          variant="outline"
          size="sm"
          :disabled="page === 1"
          @click="page--; fetchApplications()"
        >
          上一页
        </Button>
        <span class="text-sm text-muted-foreground">
          第 {{ page }} 页 / 共 {{ totalPages }} 页
        </span>
        <Button
          variant="outline"
          size="sm"
          :disabled="page >= totalPages"
          @click="page++; fetchApplications()"
        >
          下一页
        </Button>
      </div>
    </div>

    <!-- 详情弹窗 -->
    <Dialog :open="showDetailDialog" @update:open="showDetailDialog = $event">
      <DialogContent class="max-w-lg">
        <DialogHeader>
          <DialogTitle>报名详情</DialogTitle>
          <DialogDescription>查看报名人信息及所选岗位</DialogDescription>
        </DialogHeader>
        <div v-if="currentApplication" class="space-y-4 py-4 max-h-[60vh] overflow-y-auto">
          <!-- 用户信息 -->
          <div class="space-y-2">
            <Label class="flex items-center gap-2">
              <User class="w-4 h-4" />
              报名人信息
            </Label>
            <div class="bg-muted rounded-md p-3 space-y-2">
              <div class="flex justify-between text-sm">
                <span class="text-muted-foreground">用户ID</span>
                <span class="font-medium">{{ currentApplication.user_id }}</span>
              </div>
              <div v-if="currentApplication.user_name" class="flex justify-between text-sm">
                <span class="text-muted-foreground">姓名</span>
                <span class="font-medium">{{ currentApplication.user_name }}</span>
              </div>
              <div v-if="currentApplication.user_phone" class="flex justify-between text-sm">
                <span class="text-muted-foreground">电话</span>
                <span class="font-medium">{{ currentApplication.user_phone }}</span>
              </div>
              <div v-if="currentApplication.user_email" class="flex justify-between text-sm">
                <span class="text-muted-foreground">邮箱</span>
                <span class="font-medium">{{ currentApplication.user_email }}</span>
              </div>
            </div>
          </div>

          <!-- 状态 -->
          <div class="space-y-2">
            <Label>状态</Label>
            <div>
              <Badge :variant="getStatusVariant(currentApplication.status)">
                {{ statusText[currentApplication.status] }}
              </Badge>
            </div>
          </div>

          <!-- 自我介绍 -->
          <div class="space-y-2">
            <Label>自我介绍</Label>
            <p class="text-sm bg-muted rounded-md p-3 whitespace-pre-wrap">{{ currentApplication.self_intro || '暂无' }}</p>
          </div>

          <!-- 报名岗位 -->
          <div v-if="currentApplication.items && currentApplication.items.length > 0" class="space-y-2">
            <Label>报名岗位</Label>
            <div class="space-y-2">
              <div
                v-for="item in currentApplication.items"
                :key="item.id"
                class="text-sm bg-muted rounded p-3"
              >
                <div class="font-medium">岗位 #{{ item.position_id }}</div>
                <div v-if="item.department_id" class="text-xs text-muted-foreground mt-1">
                  部门: {{ item.department_id }}
                </div>
              </div>
            </div>
          </div>

          <!-- 时间信息 -->
          <div class="space-y-2">
            <Label>时间信息</Label>
            <div class="bg-muted rounded-md p-3 space-y-1 text-sm">
              <div class="flex justify-between">
                <span class="text-muted-foreground">报名时间</span>
                <span>{{ formatDate(currentApplication.created_at) }}</span>
              </div>
              <div v-if="currentApplication.audit_time" class="flex justify-between">
                <span class="text-muted-foreground">审核时间</span>
                <span>{{ formatDate(currentApplication.audit_time) }}</span>
              </div>
            </div>
          </div>

          <!-- 拒绝理由 -->
          <div v-if="currentApplication.audit_reason" class="space-y-2">
            <Label>拒绝理由</Label>
            <p class="text-sm text-destructive bg-destructive/10 rounded-md p-3">{{ currentApplication.audit_reason }}</p>
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" @click="showDetailDialog = false">关闭</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>

    <!-- 审核弹窗 -->
    <Dialog :open="showAuditDialog" @update:open="showAuditDialog = $event">
      <DialogContent class="max-w-md">
        <DialogHeader>
          <DialogTitle>{{ auditForm.status === 'APPROVED' ? '通过报名' : '拒绝报名' }}</DialogTitle>
          <DialogDescription>
            {{ auditForm.status === 'APPROVED' ? '确认通过该报名申请' : '请输入拒绝理由' }}
          </DialogDescription>
        </DialogHeader>
        <div class="space-y-4 py-4">
          <div v-if="auditForm.status === 'REJECTED'" class="space-y-2">
            <Label for="reason">拒绝理由 *</Label>
            <Textarea
              id="reason"
              v-model="auditForm.reason"
              placeholder="请输入拒绝理由"
              rows="3"
            />
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" @click="showAuditDialog = false">取消</Button>
          <Button
            :variant="auditForm.status === 'APPROVED' ? 'default' : 'destructive'"
            @click="handleAudit"
            :disabled="auditLoading"
          >
            {{ auditLoading ? '处理中...' : '确认' }}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  </div>
</template>
