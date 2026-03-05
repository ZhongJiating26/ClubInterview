<script setup lang="ts">
import { ref } from 'vue'
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
import { Eye, Calendar, User, FileText } from 'lucide-vue-next'

// 模拟数据
const records = ref([
  {
    id: 1,
    session_name: '2026年春季招新第一轮',
    student_name: '张三',
    student_id: '202301001',
    department: '技术部',
    position: '前端开发',
    interviewers: ['李面试官', '王面试官'],
    score: 85,
    status: 'PASSED',
    interview_date: '2026-01-05 14:30',
    feedback: '表现优秀，技术扎实'
  },
  {
    id: 2,
    session_name: '2026年春季招新第一轮',
    student_name: '李四',
    student_id: '202301002',
    department: '活动部',
    position: '活动策划',
    interviewers: ['赵面试官'],
    score: 72,
    status: 'PENDING',
    interview_date: '2026-01-05 15:00',
    feedback: '表现良好，待进一步考察'
  },
  {
    id: 3,
    session_name: '2026年春季招新第一轮',
    student_name: '王五',
    student_id: '202301003',
    department: '技术部',
    position: '后端开发',
    interviewers: ['李面试官', '王面试官', '刘面试官'],
    score: 58,
    status: 'FAILED',
    interview_date: '2026-01-05 15:30',
    feedback: '基础知识不够扎实'
  },
  {
    id: 4,
    session_name: '2026年春季招新第一轮',
    student_name: '赵六',
    student_id: '202301004',
    department: '宣传部',
    position: '新媒体运营',
    interviewers: ['陈面试官'],
    score: 91,
    status: 'PASSED',
    interview_date: '2026-01-05 16:00',
    feedback: '创意丰富，沟通能力强'
  }
])

const statusFilter = ref<'all' | 'PASSED' | 'PENDING' | 'FAILED'>('all')
const sessionFilter = ref('all')

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

// 过滤后的记录
const filteredRecords = ref(records.value)

// 查看详情
const viewDetail = (record: any) => {
}
</script>

<template>
  <div class="absolute inset-0 flex flex-col">
    <div class="flex-1 min-h-0 overflow-y-auto p-6">
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
              <SelectItem value="1">2026年春季招新第一轮</SelectItem>
              <SelectItem value="2">2026年春季招新第二轮</SelectItem>
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
                <p class="text-2xl font-bold">{{ records.length }}</p>
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
                <p class="text-2xl font-bold text-green-600">{{ records.filter(r => r.status === 'PASSED').length }}</p>
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
                <p class="text-2xl font-bold text-orange-600">{{ records.filter(r => r.status === 'PENDING').length }}</p>
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
                <p class="text-2xl font-bold text-red-600">{{ records.filter(r => r.status === 'FAILED').length }}</p>
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
                    <span class="text-xs text-muted-foreground">{{ record.student_id }}</span>
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
                  </div>
                </TableCell>
                <TableCell>
                  <span class="font-bold" :class="{
                    'text-green-600': record.score >= 80,
                    'text-orange-600': record.score >= 60 && record.score < 80,
                    'text-red-600': record.score < 60
                  }">{{ record.score }}</span>
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
        </CardContent>
      </Card>
    </div>
  </div>
</template>
