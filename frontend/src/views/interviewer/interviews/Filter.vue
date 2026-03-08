<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Search, Calendar, User, Phone, Mail, FileText, Play, CheckCircle2, Clock } from 'lucide-vue-next'
import { getMyInterviewTasks, type InterviewCandidate } from '@/api/modules/interview'
import { getRecruitmentSessions, type RecruitmentSession } from '@/api/modules/recruitment'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

// 招新场次列表
const recruitmentSessions = ref<RecruitmentSession[]>([])
const sessionsLoading = ref(false)

// 待面试候选人
const pendingCandidates = ref<InterviewCandidate[]>([])
const pendingLoading = ref(false)

// 已完成面试候选人
const completedCandidates = ref<InterviewCandidate[]>([])
const completedLoading = ref(false)

// 筛选条件
const searchKeyword = ref('')
const sessionFilter = ref('all')
const departmentFilter = ref('all')

// 选中的候选人
const selectedCandidate = ref<InterviewCandidate | null>(null)
const showDetailDialog = ref(false)

// 状态文本
const statusText: Record<string, string> = {
  SCHEDULED: '待面试',
  CONFIRMED: '已确认',
  COMPLETED: '已完成',
  CANCELLED: '已取消',
  NO_SHOW: '未到场'
}

// 状态样式
const getStatusVariant = (status: string): 'default' | 'secondary' | 'destructive' | 'outline' => {
  switch (status) {
    case 'COMPLETED':
      return 'default'
    case 'SCHEDULED':
    case 'CONFIRMED':
      return 'secondary'
    case 'CANCELLED':
    case 'NO_SHOW':
      return 'destructive'
    default:
      return 'outline'
  }
}

// 加载面试官任务
const loadInterviewTasks = async () => {
  pendingLoading.value = true
  completedLoading.value = true

  try {
    const tasks = await getMyInterviewTasks()

    // 按状态分类
    const pending = tasks.filter(t => t.status === 'SCHEDULED' || t.status === 'CONFIRMED')
    const completed = tasks.filter(t => t.status === 'COMPLETED')

    pendingCandidates.value = pending
    completedCandidates.value = completed
  } catch (error) {
    console.error('加载面试任务失败:', error)
  } finally {
    pendingLoading.value = false
    completedLoading.value = false
  }
}

// 加载招新场次列表
const loadRecruitmentSessions = async () => {
  sessionsLoading.value = true
  try {
    const clubId = userStore.userInfo?.roles?.[0]?.club_id
    const sessions = await getRecruitmentSessions({ club_id: clubId })
    recruitmentSessions.value = sessions || []
  } catch (error) {
    console.error('加载招新场次失败:', error)
  } finally {
    sessionsLoading.value = false
  }
}

// 过滤后的待面试候选人
const filteredPendingCandidates = computed(() => {
  let filtered = pendingCandidates.value

  // 关键词搜索
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    filtered = filtered.filter(c =>
      (c.user_name && c.user_name.toLowerCase().includes(keyword)) ||
      (c.position_name && c.position_name.toLowerCase().includes(keyword))
    )
  }

  // 场次筛选
  if (sessionFilter.value !== 'all') {
    filtered = filtered.filter(c => c.session_id.toString() === sessionFilter.value)
  }

  // 部门筛选
  if (departmentFilter.value !== 'all') {
    filtered = filtered.filter(c => c.department_name === departmentFilter.value)
  }

  return filtered
})

// 统计数据
const stats = computed(() => {
  const total = pendingCandidates.value.length
  const completed = completedCandidates.value.length
  const today = pendingCandidates.value.filter(c => {
    if (!c.planned_start_time) return false
    const today = new Date().toDateString()
    return new Date(c.planned_start_time).toDateString() === today
  }).length

  return { total, completed, today }
})

// 部门列表
const departments = computed(() => {
  const deptSet = new Set<string>()
  pendingCandidates.value.forEach(c => {
    if (c.department_name) deptSet.add(c.department_name)
  })
  completedCandidates.value.forEach(c => {
    if (c.department_name) deptSet.add(c.department_name)
  })
  return Array.from(deptSet)
})

// 打开详情对话框
const openDetail = (candidate: InterviewCandidate) => {
  selectedCandidate.value = candidate
  showDetailDialog.value = true
}

// 开始面试
const startInterview = (candidate: InterviewCandidate) => {
  router.push({
    name: 'InterviewerInterviewsScore',
    query: { candidateId: candidate.id }
  })
}

// 格式化日期
const formatDate = (dateStr: string | undefined) => {
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
  loadInterviewTasks()
  loadRecruitmentSessions()
})
</script>

<template>
  <div class="absolute inset-0 flex flex-col">
    <div class="flex-1 min-h-0 overflow-y-auto p-6">
      <div class="mb-6">
        <h1 class="text-2xl font-bold mb-4">面试候选人</h1>

        <!-- 筛选器 -->
        <div class="flex gap-3">
          <div class="relative w-64">
            <Search class="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            <Input
              v-model="searchKeyword"
              placeholder="搜索姓名、岗位..."
              class="pl-9"
            />
          </div>
          <Select v-model="sessionFilter">
            <SelectTrigger class="w-[180px]" :disabled="sessionsLoading">
              <SelectValue placeholder="选择场次" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">全部场次</SelectItem>
              <SelectItem
                v-for="session in recruitmentSessions"
                :key="session.id"
                :value="String(session.id)"
              >
                {{ session.name }}
              </SelectItem>
            </SelectContent>
          </Select>
          <Select v-model="departmentFilter">
            <SelectTrigger class="w-[150px]">
              <SelectValue placeholder="选择部门" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">全部部门</SelectItem>
              <SelectItem
                v-for="dept in departments"
                :key="dept"
                :value="dept"
              >
                {{ dept }}
              </SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      <!-- 统计卡片 -->
      <div class="flex gap-4 mb-6">
        <div class="bg-gray-200 rounded-2xl p-6 w-64">
          <div class="flex items-end justify-between">
            <div class="flex items-end">
              <p class="text-4xl font-bold">{{ stats.total }}</p>
              <p class="text-sm text-muted-foreground mb-1 ml-1">待面试</p>
            </div>
            <div class="bg-white rounded-2xl p-3 border border-gray-400 border-0.5">
              <User class="w-6 h-6 text-black" />
            </div>
          </div>
        </div>
        <div class="bg-gray-200 rounded-2xl p-6 w-64">
          <div class="flex items-end justify-between">
            <div class="flex items-end">
              <p class="text-4xl font-bold text-green-500">{{ stats.completed }}</p>
              <p class="text-sm text-muted-foreground mb-1 ml-1">已完成</p>
            </div>
            <div class="bg-white rounded-2xl p-3 border border-gray-400 border-0.5">
              <CheckCircle2 class="w-6 h-6 text-black" />
            </div>
          </div>
        </div>
        <div class="bg-gray-200 rounded-2xl p-6 w-64">
          <div class="flex items-end justify-between">
            <div class="flex items-end">
              <p class="text-4xl font-bold text-blue-500">{{ stats.today }}</p>
              <p class="text-sm text-muted-foreground mb-1 ml-1">今日面试</p>
            </div>
            <div class="bg-white rounded-2xl p-3 border border-gray-400 border-0.5">
              <Calendar class="w-6 h-6 text-black" />
            </div>
          </div>
        </div>
      </div>

      <!-- 待面试候选人列表 -->
      <Card class="mb-6">
        <CardHeader>
          <CardTitle>待面试候选人</CardTitle>
        </CardHeader>
        <CardContent>
          <div v-if="pendingLoading" class="text-center py-8 text-gray-500">
            加载中...
          </div>
          <Table v-else-if="filteredPendingCandidates.length > 0">
            <TableHeader>
              <TableRow>
                <TableHead>候选人信息</TableHead>
                <TableHead>应聘岗位</TableHead>
                <TableHead>面试场次</TableHead>
                <TableHead>面试时间</TableHead>
                <TableHead>状态</TableHead>
                <TableHead class="text-right">操作</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow v-for="candidate in filteredPendingCandidates" :key="candidate.id">
                <TableCell>
                  <div class="flex flex-col">
                    <span class="font-medium">{{ candidate.user_name || '未知' }}</span>
                    <span class="text-xs text-gray-500">{{ candidate.user_phone || '' }}</span>
                  </div>
                </TableCell>
                <TableCell>
                  <div class="flex flex-col">
                    <span>{{ candidate.position_name || '未知岗位' }}</span>
                    <Badge v-if="candidate.department_name" variant="outline" class="w-fit text-xs mt-1">{{ candidate.department_name }}</Badge>
                  </div>
                </TableCell>
                <TableCell class="text-sm text-gray-600">
                  {{ candidate.session_id }}
                </TableCell>
                <TableCell class="text-sm text-gray-600">
                  {{ formatDate(candidate.planned_start_time) }}
                </TableCell>
                <TableCell>
                  <Badge :variant="getStatusVariant(candidate.status)">
                    {{ statusText[candidate.status] }}
                  </Badge>
                </TableCell>
                <TableCell class="text-right">
                  <Button variant="ghost" size="sm" @click="openDetail(candidate)">
                    查看详情
                  </Button>
                  <Button
                    size="sm"
                    class="ml-2"
                    @click="startInterview(candidate)"
                  >
                    <Play class="w-4 h-4 mr-1" />
                    开始面试
                  </Button>
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>

          <!-- 空状态 -->
          <div v-else class="text-center py-12">
            <User class="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p class="text-gray-500">暂无待面试候选人</p>
          </div>
        </CardContent>
      </Card>

      <!-- 已完成面试列表 -->
      <Card>
        <CardHeader>
          <CardTitle>已完成面试</CardTitle>
        </CardHeader>
        <CardContent>
          <div v-if="completedLoading" class="text-center py-8 text-gray-500">
            加载中...
          </div>
          <Table v-else-if="completedCandidates.length > 0">
            <TableHeader>
              <TableRow>
                <TableHead>候选人信息</TableHead>
                <TableHead>应聘岗位</TableHead>
                <TableHead>面试时间</TableHead>
                <TableHead>评分</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow v-for="candidate in completedCandidates" :key="candidate.id">
                <TableCell>
                  <div class="flex flex-col">
                    <span class="font-medium">{{ candidate.user_name || '未知' }}</span>
                    <span class="text-xs text-gray-500">{{ candidate.user_phone || '' }}</span>
                  </div>
                </TableCell>
                <TableCell>
                  <div class="flex flex-col">
                    <span>{{ candidate.position_name || '未知岗位' }}</span>
                    <Badge v-if="candidate.department_name" variant="outline" class="w-fit text-xs mt-1">{{ candidate.department_name }}</Badge>
                  </div>
                </TableCell>
                <TableCell class="text-sm text-gray-600">
                  {{ formatDate(candidate.actual_start_time) }}
                </TableCell>
                <TableCell>
                  <span class="font-bold text-green-600">
                    {{ candidate.final_score ?? '-' }}
                  </span>
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>

          <!-- 空状态 -->
          <div v-else class="text-center py-12">
            <CheckCircle2 class="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p class="text-gray-500">暂无已完成面试</p>
          </div>
        </CardContent>
      </Card>
    </div>

    <!-- 详情对话框 -->
    <Dialog :open="showDetailDialog" @update:open="showDetailDialog = $event">
      <DialogContent class="max-w-2xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>候选人详情</DialogTitle>
          <DialogDescription>查看候选人完整报名信息</DialogDescription>
        </DialogHeader>

        <div v-if="selectedCandidate" class="space-y-4 py-4">
          <!-- 基本信息 -->
          <div class="space-y-2">
            <h4 class="font-semibold text-gray-700">基本信息</h4>
            <div class="grid grid-cols-2 gap-2 text-sm">
              <div class="flex items-center gap-2">
                <User class="w-4 h-4 text-gray-400" />
                <span>{{ selectedCandidate.user_name || '未知' }}</span>
              </div>
              <div class="flex items-center gap-2">
                <Phone class="w-4 h-4 text-gray-400" />
                <span>{{ selectedCandidate.user_phone || '-' }}</span>
              </div>
            </div>
          </div>

          <!-- 面试信息 -->
          <div class="space-y-2">
            <h4 class="font-semibold text-gray-700">面试信息</h4>
            <div class="grid grid-cols-2 gap-2 text-sm">
              <div>
                <span class="text-gray-500">面试场次ID：</span>
                <span class="text-gray-800">{{ selectedCandidate.session_id }}</span>
              </div>
              <div>
                <span class="text-gray-500">面试时间：</span>
                <span class="text-gray-800">{{ formatDate(selectedCandidate.planned_start_time) }}</span>
              </div>
              <div>
                <span class="text-gray-500">应聘部门：</span>
                <Badge v-if="selectedCandidate.department_name" variant="outline" class="bg-blue-50 text-blue-700 border-blue-200">{{ selectedCandidate.department_name }}</Badge>
              </div>
              <div>
                <span class="text-gray-500">应聘岗位：</span>
                <Badge v-if="selectedCandidate.position_name" variant="outline" class="bg-purple-50 text-purple-700 border-purple-200">{{ selectedCandidate.position_name }}</Badge>
              </div>
            </div>
          </div>

          <!-- 状态 -->
          <div class="space-y-2">
            <h4 class="font-semibold text-gray-700">状态</h4>
            <Badge :variant="getStatusVariant(selectedCandidate.status)">
              {{ statusText[selectedCandidate.status] }}
            </Badge>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" class="border-gray-300 text-gray-700 hover:bg-gray-100" @click="showDetailDialog = false">
            关闭
          </Button>
          <Button
            v-if="selectedCandidate && (selectedCandidate.status === 'SCHEDULED' || selectedCandidate.status === 'CONFIRMED')"
            class="bg-blue-600 hover:bg-blue-700 text-white"
            @click="startInterview(selectedCandidate)"
          >
            <Play class="w-4 h-4 mr-1" />
            开始面试
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  </div>
</template>
