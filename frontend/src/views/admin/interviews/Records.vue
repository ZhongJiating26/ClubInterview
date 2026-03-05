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
import { Eye, Calendar, User, FileText, XCircle } from 'lucide-vue-next'
import { getInterviewSessions, getSessionResults, type InterviewSession, type InterviewResult } from '@/api/modules/interview'

// 面试记录数据类型
interface InterviewRecord {
  id: number
  session_id: number
  session_name: string
  candidate_id: number
  student_name: string
  student_id: string
  department: string
  position: string
  interviewers: string[]
  score: number | null
  status: string
  interview_date: string
  feedback: string
}

const records = ref<InterviewRecord[]>([])
const loading = ref(false)
const error = ref('')
const statusFilter = ref<'all' | 'PASSED' | 'PENDING' | 'FAILED'>('all')
const sessionFilter = ref('all')
const sessionNames = ref<Record<number, string>>({})

// 获取面试记录数据
const fetchRecords = async () => {
  try {
    loading.value = true
    error.value = ''

    // 获取所有面试场次
    const sessions = await getInterviewSessions() as InterviewSession[]
    const allRecords: InterviewRecord[] = []

    // 为每个场次获取面试结果
    for (const session of sessions) {
      sessionNames.value[session.id] = session.name
      try {
        const results = await getSessionResults(session.id) as InterviewResult[]
        results.forEach((result: InterviewResult) => {
          // 计算最终状态
          let status = 'PENDING'
          if (result.final_score !== undefined && result.final_score !== null) {
            if (result.final_score >= 60) {
              status = 'PASSED'
            } else {
              status = 'FAILED'
            }
          }

          // 获取面试官名称
          const interviewerNames = result.records?.map((r: any) => r.interviewer_name) || []

          // 格式化面试时间
          const interviewDate = session.start_time
            ? new Date(session.start_time).toLocaleString('zh-CN', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit'
              })
            : ''

          allRecords.push({
            id: result.candidate_id,
            session_id: session.id,
            session_name: session.name,
            candidate_id: result.candidate_id,
            student_name: result.user_name || '未知',
            student_id: '',
            department: result.department_name || '未知部门',
            position: result.position_name || '未知岗位',
            interviewers: interviewerNames,
            score: result.average_score,
            status: status,
            interview_date: interviewDate,
            feedback: result.records?.[0]?.notes || ''
          })
        })
      } catch (e) {
        console.warn(`获取场次 ${session.name} 的结果失败:`, e)
      }
    }

    records.value = allRecords
  } catch (err: any) {
    console.error('获取面试记录失败:', err)
    error.value = err.message || '获取面试记录失败'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchRecords()
})

// 状态文本
const statusText: Record<string, string> = {
  PASSED: '通过',
  PENDING: '待定',
  FAILED: '未通过'
}

// 状态样式
const getStatusVariant = (status: string) => {
  switch (status) {
    case 'PASSED':
      return 'default'
    case 'PENDING':
      return 'secondary'
    case 'FAILED':
      return 'destructive'
    default:
      return 'outline'
  }
}

// 获取场次选项
const sessionOptions = computed(() => {
  return Object.values(sessionNames.value)
})

// 过滤后的记录
const filteredRecords = computed(() => {
  let filtered = records.value

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
  const total = records.value.length
  const passed = records.value.filter(r => r.status === 'PASSED').length
  const pending = records.value.filter(r => r.status === 'PENDING').length
  const failed = records.value.filter(r => r.status === 'FAILED').length

  return { total, passed, pending, failed }
})

// 查看详情
const viewDetail = (record: any) => {
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
          <h1 class="text-2xl font-bold mb-4">面试记录</h1>

          <!-- 筛选器 -->
          <div class="flex gap-3">
            <Select v-model="sessionFilter">
              <SelectTrigger class="w-[200px]">
                <SelectValue placeholder="选择面试场次" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">全部场次</SelectItem>
                <SelectItem v-for="session in sessionOptions" :key="session" :value="session">
                  {{ session }}
                </SelectItem>
              </SelectContent>
            </Select>
            <Select v-model="statusFilter">
              <SelectTrigger class="w-[150px]">
                <SelectValue placeholder="选择状态" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">全部状态</SelectItem>
                <SelectItem value="PASSED">通过</SelectItem>
                <SelectItem value="PENDING">待定</SelectItem>
                <SelectItem value="FAILED">未通过</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        <!-- 统计卡片 -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <Card>
            <CardContent class="pt-6">
              <div class="flex items-center justify-between">
                <div>
                  <p class="text-sm text-muted-foreground">总面试数</p>
                  <p class="text-2xl font-bold">{{ stats.total }}</p>
                </div>
                <FileText class="w-8 h-8 text-muted-foreground opacity-50" />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent class="pt-6">
              <div class="flex items-center justify-between">
                <div>
                  <p class="text-sm text-muted-foreground">通过</p>
                  <p class="text-2xl font-bold text-green-600">{{ stats.passed }}</p>
                </div>
                <div class="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center text-green-600 text-sm font-medium">
                  ✓
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent class="pt-6">
              <div class="flex items-center justify-between">
                <div>
                  <p class="text-sm text-muted-foreground">待定</p>
                  <p class="text-2xl font-bold text-orange-600">{{ stats.pending }}</p>
                </div>
                <div class="w-8 h-8 rounded-full bg-orange-100 flex items-center justify-center text-orange-600 text-sm font-medium">
                  ?
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent class="pt-6">
              <div class="flex items-center justify-between">
                <div>
                  <p class="text-sm text-muted-foreground">未通过</p>
                  <p class="text-2xl font-bold text-red-600">{{ stats.failed }}</p>
                </div>
                <div class="w-8 h-8 rounded-full bg-red-100 flex items-center justify-center text-red-600 text-sm font-medium">
                  ✗
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <!-- 面试记录表格 -->
        <Card>
          <CardHeader>
            <CardTitle>面试记录列表</CardTitle>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>面试场次</TableHead>
                  <TableHead>学生信息</TableHead>
                  <TableHead>面试岗位</TableHead>
                  <TableHead>面试官</TableHead>
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
                      <span class="font-medium">{{ record.student_name }}</span>
                      <span class="text-xs text-muted-foreground">{{ record.student_id || '-' }}</span>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div class="flex flex-col">
                      <span>{{ record.position }}</span>
                      <Badge variant="outline" class="w-fit text-xs mt-1">{{ record.department }}</Badge>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div class="flex flex-wrap gap-1">
                      <Badge v-for="interviewer in record.interviewers" :key="interviewer" variant="outline" class="text-xs">
                        {{ interviewer }}
                      </Badge>
                      <span v-if="record.interviewers.length === 0" class="text-muted-foreground text-xs">-</span>
                    </div>
                  </TableCell>
                  <TableCell>
                    <span v-if="record.score !== null" class="font-bold" :class="{
                      'text-green-600': record.score >= 80,
                      'text-orange-600': record.score >= 60 && record.score < 80,
                      'text-red-600': record.score < 60
                    }">{{ Math.round(record.score) }}</span>
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
                      <Eye class="w-4 h-4 mr-1" />
                      详情
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
