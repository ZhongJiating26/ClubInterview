<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
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
import { getMyInterviewTasks, type InterviewCandidate } from '@/api/modules/interview'

// 模拟我的面试记录数据（暂时不用后端）
const myRecords = ref([
  {
    id: 1,
    candidate_id: 101,
    session_name: '2026年春季招新第一轮',
    candidate_name: '张三',
    candidate_phone: '138****1234',
    position: '前端开发',
    department: '技术部',
    score: 85,
    status: 'SCORED',
    notes: '技术基础扎实，Vue经验丰富，沟通能力强',
    interview_date: '2026-01-05 14:30',
    recording_url: '',
    face_image_url: ''
  },
  {
    id: 2,
    candidate_id: 102,
    session_name: '2026年春季招新第一轮',
    candidate_name: '李四',
    candidate_phone: '139****5678',
    position: '后端开发',
    department: '技术部',
    score: null,
    status: 'PENDING',
    notes: '',
    interview_date: '2026-01-05 15:00',
    recording_url: '',
    face_image_url: ''
  },
  {
    id: 3,
    candidate_id: 103,
    session_name: '2026年春季招新第一轮',
    candidate_name: '王五',
    candidate_phone: '137****9012',
    position: '产品经理',
    department: '产品部',
    score: 78,
    status: 'SCORED',
    notes: '思维活跃，逻辑清晰，对产品有独到见解',
    interview_date: '2026-01-05 16:00',
    recording_url: '',
    face_image_url: ''
  },
  {
    id: 4,
    candidate_id: 104,
    session_name: '2026年春季招新第二轮',
    candidate_name: '赵六',
    candidate_phone: '136****3456',
    position: 'UI设计师',
    department: '设计部',
    score: 92,
    status: 'SCORED',
    notes: '作品集优秀，设计感强，审美在线',
    interview_date: '2026-01-06 10:00',
    recording_url: '',
    face_image_url: ''
  },
  {
    id: 5,
    candidate_id: 105,
    session_name: '2026年春季招新第二轮',
    candidate_name: '孙七',
    candidate_phone: '135****7890',
    position: '前端开发',
    department: '技术部',
    score: null,
    status: 'PENDING',
    notes: '',
    interview_date: '2026-01-06 11:00',
    recording_url: '',
    face_image_url: ''
  }
])

const loading = ref(false)
const statusFilter = ref<'all' | 'SCORED' | 'PENDING'>('all')
const sessionFilter = ref('all')

// 状态文本
const statusText: Record<string, string> = {
  SCORED: '已评分',
  PENDING: '待评分'
}

// 状态样式
const getStatusVariant = (status: string): 'default' | 'secondary' | 'destructive' | 'outline' => {
  switch (status) {
    case 'SCORED':
      return 'default'
    case 'PENDING':
      return 'secondary'
    default:
      return 'outline'
  }
}

// 过滤后的记录
const filteredRecords = computed(() => {
  let filtered = myRecords.value

  if (statusFilter.value !== 'all') {
    filtered = filtered.filter(r => r.status === statusFilter.value)
  }

  if (sessionFilter.value !== 'all') {
    filtered = filtered.filter(r => r.session_name.includes(sessionFilter.value))
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
            <SelectItem value="第一轮">第一轮</SelectItem>
            <SelectItem value="第二轮">第二轮</SelectItem>
          </SelectContent>
        </Select>
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
                <p class="text-sm text-muted-foreground">已评分</p>
                <p class="text-2xl font-bold text-green-600">{{ stats.scored }}</p>
              </div>
              <CheckCircle2 class="w-8 h-8 text-green-600 opacity-50" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent class="pt-6">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm text-muted-foreground">待评分</p>
                <p class="text-2xl font-bold text-orange-600">{{ stats.pending }}</p>
              </div>
              <Clock class="w-8 h-8 text-orange-600 opacity-50" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent class="pt-6">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm text-muted-foreground">平均分</p>
                <p class="text-2xl font-bold text-blue-600">{{ stats.avgScore }}</p>
              </div>
              <User class="w-8 h-8 text-blue-600 opacity-50" />
            </div>
          </CardContent>
        </Card>
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
    </div>
  </div>
</template>
