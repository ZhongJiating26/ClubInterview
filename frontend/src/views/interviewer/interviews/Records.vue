<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Loader2 } from 'lucide-vue-next'
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
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { FileText, Clock, Calendar, User, CheckCircle2, XCircle } from 'lucide-vue-next'
import { getMyInterviewTasks, getInterviewSessions, type InterviewCandidate } from '@/api/modules/interview'

// 面试记录数据类型（适配后端 API）
interface InterviewRecord {
  id: number
  session_id: number
  session_name: string
  candidate_id: number
  candidate_name: string
  candidate_phone: string
  position: string
  department: string
  score: number | null
  status: string
  notes: string
  interview_date: string
  planned_start_time: string
  planned_end_time: string
  final_score: number | null
}

const myRecords = ref<InterviewRecord[]>([])
const loading = ref(false)
const error = ref('')
const statusFilter = ref<'all' | 'COMPLETED' | 'PENDING'>('all')
const sessionFilter = ref('all')
const sessionNames = ref<Record<number, string>>({})

// 获取面试官任务列表
const fetchRecords = async () => {
  try {
    loading.value = true
    error.value = ''

    // 获取我的面试任务
    const tasks = await getMyInterviewTasks()

    // 获取所有相关的场次信息
    const sessionIds = [...new Set(tasks.map((t: InterviewCandidate) => t.session_id))]
    if (sessionIds.length > 0) {
      const sessions = await getInterviewSessions()
      sessions.forEach((s: any) => {
        sessionNames.value[s.id] = s.name
      })
    }

    // 转换数据格式
    myRecords.value = tasks.map((task: InterviewCandidate) => {
      // 将后端状态转换为前端显示状态
      let displayStatus = 'PENDING'
      if (task.status === 'COMPLETED') {
        displayStatus = task.final_score !== null ? 'SCORED' : 'PENDING'
      } else if (task.status === 'SCHEDULED' || task.status === 'CONFIRMED') {
        displayStatus = 'PENDING'
      }

      // 格式化时间
      const interviewDate = task.planned_start_time
        ? new Date(task.planned_start_time).toLocaleString('zh-CN', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
          })
        : ''

      return {
        id: task.id,
        session_id: task.session_id,
        session_name: sessionNames.value[task.session_id] || `面试场次${task.session_id}`,
        candidate_id: task.candidate_user_id,
        candidate_name: task.user_name || '未知',
        candidate_phone: task.user_phone ? maskPhone(task.user_phone) : '',
        position: task.position_name || '未知岗位',
        department: task.department_name || '未知部门',
        score: task.final_score,
        status: displayStatus,
        notes: '',
        interview_date: interviewDate,
        planned_start_time: task.planned_start_time || '',
        planned_end_time: task.planned_end_time || '',
        final_score: task.final_score
      }
    })
  } catch (err: any) {
    console.error('获取面试记录失败:', err)
    error.value = err.message || '获取面试记录失败'
  } finally {
    loading.value = false
  }
}

// 手机号脱敏
const maskPhone = (phone: string) => {
  if (!phone || phone.length < 7) return phone
  return phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2')
}

onMounted(() => {
  fetchRecords()
})

// 状态文本
const statusText: Record<string, string> = {
  SCORED: '已评分',
  PENDING: '待评分',
  COMPLETED: '已完成'
}

// 状态样式
const getStatusVariant = (status: string): 'default' | 'secondary' | 'destructive' | 'outline' => {
  switch (status) {
    case 'SCORED':
      return 'default'
    case 'PENDING':
      return 'secondary'
    case 'COMPLETED':
      return 'outline'
    default:
      return 'outline'
  }
}

// 获取所有场次选项
const sessionOptions = computed(() => {
  const sessions = [...new Set(myRecords.value.map(r => r.session_name))]
  return sessions
})

// 过滤后的记录
const filteredRecords = computed(() => {
  let filtered = myRecords.value

  if (statusFilter.value !== 'all') {
    filtered = filtered.filter(r => r.status === statusFilter.value)
  }

  if (sessionFilter.value !== 'all') {
    filtered = filtered.filter(r => r.session_name === sessionFilter.value)
  }

  return filtered
})

// 统计数据
const stats = computed(() => {
  const total = myRecords.value.length
  const scored = myRecords.value.filter(r => r.status === 'SCORED').length
  const pending = myRecords.value.filter(r => r.status === 'PENDING').length
  const avgScore = myRecords.value
    .filter(r => r.score !== null)
    .reduce((sum, r) => sum + (r.score || 0), 0) / (scored || 1)

  return { total, scored, pending, avgScore: scored ? Math.round(avgScore * 10) / 10 : 0 }
})

// 查看详情
const viewDetail = (record: any) => {
  // TODO: 跳转到详情页或打开弹窗
}
</script>

<template>
  <div class="absolute inset-0 flex flex-col">
    <div class="flex-1 min-h-0 overflow-y-auto p-6">
      <!-- 加载状态 -->
      <div v-if="loading" class="flex items-center justify-center py-20">
        <Loader2 class="w-8 h-8 animate-spin text-primary" />
        <span class="ml-2 text-muted-foreground">加载中...</span>
      </div>

      <!-- 错误状态 -->
      <div v-else-if="error" class="text-center py-12">
        <XCircle class="w-12 h-12 text-red-500 mx-auto mb-4" />
        <p class="text-red-500">{{ error }}</p>
        <Button variant="outline" class="mt-4" @click="fetchRecords">
          重试
        </Button>
      </div>

      <template v-else>
        <div class="mb-6">
          <h1 class="text-2xl font-bold mb-2">面试记录</h1>
          <p class="text-muted-foreground">查看和管理我的面试记录</p>
        </div>

        <!-- 筛选器 -->
        <div class="flex gap-3 mb-6">
          <Select v-model="statusFilter">
            <SelectTrigger class="w-[150px]">
              <SelectValue placeholder="选择状态" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">全部状态</SelectItem>
              <SelectItem value="SCORED">已评分</SelectItem>
              <SelectItem value="PENDING">待评分</SelectItem>
            </SelectContent>
          </Select>
          <Select v-model="sessionFilter">
            <SelectTrigger class="w-[200px]">
              <SelectValue placeholder="选择场次" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">全部场次</SelectItem>
              <SelectItem v-for="session in sessionOptions" :key="session" :value="session">
                {{ session }}
              </SelectItem>
            </SelectContent>
          </Select>
        </div>

        <!-- 统计卡片 -->
        <div class="flex gap-4 mb-6">
          <div class="bg-gray-200 rounded-2xl p-6 w-64">
            <div class="flex items-end justify-between">
              <div class="flex items-end">
                <p class="text-4xl font-bold">{{ stats.total }}</p>
                <p class="text-sm text-muted-foreground mb-1 ml-1">总面试数</p>
              </div>
              <div class="bg-white rounded-2xl p-3 border border-gray-400 border-0.5">
                <FileText class="w-6 h-6 text-black" />
              </div>
            </div>
          </div>
          <div class="bg-gray-200 rounded-2xl p-6 w-64">
            <div class="flex items-end justify-between">
              <div class="flex items-end">
                <p class="text-4xl font-bold text-green-500">{{ stats.scored }}</p>
                <p class="text-sm text-muted-foreground mb-1 ml-1">已评分</p>
              </div>
              <div class="bg-white rounded-2xl p-3 border border-gray-400 border-0.5">
                <CheckCircle2 class="w-6 h-6 text-black" />
              </div>
            </div>
          </div>
          <div class="bg-gray-200 rounded-2xl p-6 w-64">
            <div class="flex items-end justify-between">
              <div class="flex items-end">
                <p class="text-4xl font-bold text-orange-500">{{ stats.pending }}</p>
                <p class="text-sm text-muted-foreground mb-1 ml-1">待评分</p>
              </div>
              <div class="bg-white rounded-2xl p-3 border border-gray-400 border-0.5">
                <Clock class="w-6 h-6 text-black" />
              </div>
            </div>
          </div>
          <div class="bg-gray-200 rounded-2xl p-6 w-64">
            <div class="flex items-end justify-between">
              <div class="flex items-end">
                <p class="text-4xl font-bold text-blue-500">{{ stats.avgScore }}</p>
                <p class="text-sm text-muted-foreground mb-1 ml-1">平均分</p>
              </div>
              <div class="bg-white rounded-2xl p-3 border border-gray-400 border-0.5">
                <User class="w-6 h-6 text-black" />
              </div>
            </div>
          </div>
        </div>

        <!-- 面试记录表格 -->
        <Card>
          <CardHeader>
            <CardTitle>我的面试记录</CardTitle>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>面试场次</TableHead>
                  <TableHead>候选人信息</TableHead>
                  <TableHead>面试岗位</TableHead>
                  <TableHead>分数</TableHead>
                  <TableHead>状态</TableHead>
                  <TableHead>面试时间</TableHead>
                  <TableHead class="text-right">操作</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                <TableRow v-for="record in filteredRecords" :key="record.id">
                  <TableCell class="font-medium">{{ record.session_name }}</TableCell>
                  <TableCell>
                    <div class="flex flex-col">
                      <span class="font-medium">{{ record.candidate_name }}</span>
                      <span class="text-xs text-muted-foreground">{{ record.candidate_phone }}</span>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div class="flex flex-col">
                      <span>{{ record.position }}</span>
                      <Badge variant="outline" class="w-fit text-xs mt-1">{{ record.department }}</Badge>
                    </div>
                  </TableCell>
                  <TableCell>
                    <span v-if="record.score !== null" class="font-bold" :class="{
                      'text-green-600': record.score >= 85,
                      'text-blue-600': record.score >= 75 && record.score < 85,
                      'text-orange-600': record.score < 75
                    }">{{ record.score }}</span>
                    <span v-else class="text-muted-foreground">-</span>
                  </TableCell>
                  <TableCell>
                    <Badge :variant="getStatusVariant(record.status)">
                      {{ statusText[record.status] }}
                    </Badge>
                  </TableCell>
                  <TableCell class="text-sm text-muted-foreground">
                    {{ record.interview_date }}
                  </TableCell>
                  <TableCell class="text-right">
                    <Button variant="ghost" size="sm" @click="viewDetail(record)">
                      查看详情
                    </Button>
                  </TableCell>
                </TableRow>
              </TableBody>
            </Table>

            <!-- 空状态 -->
            <div v-if="filteredRecords.length === 0" class="text-center py-12">
              <FileText class="w-12 h-12 text-muted-foreground mx-auto mb-4 opacity-50" />
              <p class="text-muted-foreground">暂无面试记录</p>
            </div>
          </CardContent>
        </Card>
      </template>
    </div>
  </div>
</template>
