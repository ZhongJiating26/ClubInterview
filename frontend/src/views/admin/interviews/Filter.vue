<script setup lang="ts">
import { ref } from 'vue'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Checkbox } from '@/components/ui/checkbox'
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
import { CheckCircle, Users, Calendar } from 'lucide-vue-next'

// 模拟数据 - 待筛选学生
const students = ref([
  {
    id: 1,
    name: '张三',
    student_id: '202301001',
    phone: '138****1234',
    department: '技术部',
    position: '前端开发',
    self_intro: '热爱编程，有Vue开发经验，希望加入技术部提升自己。',
    score: 85,
    selected: false
  },
  {
    id: 2,
    name: '李四',
    student_id: '202301002',
    phone: '139****5678',
    department: '活动部',
    position: '活动策划',
    self_intro: '性格开朗，组织能力强，曾组织多次班级活动。',
    score: 78,
    selected: false
  },
  {
    id: 3,
    name: '王五',
    student_id: '202301003',
    phone: '137****9012',
    department: '技术部',
    position: '后端开发',
    self_intro: '熟悉Python和Java，对后端架构有深入了解。',
    score: 92,
    selected: false
  },
  {
    id: 4,
    name: '赵六',
    student_id: '202301004',
    phone: '136****3456',
    department: '宣传部',
    position: '新媒体运营',
    self_intro: '擅长文案写作和视频剪辑，运营过个人抖音账号。',
    score: 88,
    selected: false
  },
  {
    id: 5,
    name: '孙七',
    student_id: '202301005',
    phone: '135****7890',
    department: '外联部',
    position: '外联干事',
    self_intro: '沟通能力强，有校外合作经验。',
    score: 75,
    selected: false
  }
])

const sessionFilter = ref('all')
const departmentFilter = ref('all')
const selectedCount = ref(0)

// 已筛选学生
const filteredStudents = ref([
  {
    id: 6,
    name: '周八',
    student_id: '202301006',
    department: '技术部',
    position: '前端开发',
    interviewers: ['李面试官', '王面试官'],
    interview_date: '2026-01-07 14:00'
  },
  {
    id: 7,
    name: '吴九',
    student_id: '202301007',
    department: '活动部',
    position: '活动策划',
    interviewers: ['赵面试官'],
    interview_date: '2026-01-07 15:30'
  }
])

// 切换选择状态
const toggleSelect = (student: any) => {
  student.selected = !student.selected
  selectedCount.value = students.value.filter(s => s.selected).length
}

// 全选/取消全选
const toggleSelectAll = () => {
  const allSelected = students.value.every(s => s.selected)
  students.value.forEach(s => s.selected = !allSelected)
  selectedCount.value = allSelected ? 0 : students.value.length
}

// 批量分配面试官
const assignInterviewers = () => {
}

// 分配面试
const assignInterview = (student: any) => {
}

// 取消面试
const cancelInterview = (student: any) => {
}
</script>

<template>
  <div class="absolute inset-0 flex flex-col">
    <div class="flex-1 min-h-0 overflow-y-auto p-6">
      <div class="mb-6">
        <h1 class="text-2xl font-bold mb-4">面试筛选</h1>

        <!-- 筛选器 -->
        <div class="flex gap-3">
          <Select v-model="sessionFilter">
            <SelectTrigger class="w-[200px]">
              <SelectValue placeholder="选择招新场次" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">全部场次</SelectItem>
              <SelectItem value="1">2026年春季招新</SelectItem>
            </SelectContent>
          </Select>
          <Select v-model="departmentFilter">
            <SelectTrigger class="w-[150px]">
              <SelectValue placeholder="选择部门" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">全部部门</SelectItem>
              <SelectItem value="tech">技术部</SelectItem>
              <SelectItem value="activity">活动部</SelectItem>
              <SelectItem value="publicity">宣传部</SelectItem>
              <SelectItem value="liaison">外联部</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      <!-- 统计卡片 -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <Card>
          <CardContent class="pt-6">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm text-muted-foreground">待筛选</p>
                <p class="text-2xl font-bold">{{ students.length }}</p>
              </div>
              <Users class="w-8 h-8 text-muted-foreground opacity-50" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent class="pt-6">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm text-muted-foreground">已分配</p>
                <p class="text-2xl font-bold text-green-600">{{ filteredStudents.length }}</p>
              </div>
              <CheckCircle class="w-8 h-8 text-green-600 opacity-50" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent class="pt-6">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm text-muted-foreground">已选择</p>
                <p class="text-2xl font-bold text-blue-600">{{ selectedCount }}</p>
              </div>
              <div class="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 text-sm font-medium">
                {{ selectedCount }}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <!-- 待筛选学生列表 -->
      <Card class="mb-6">
        <CardHeader>
          <div class="flex items-center justify-between">
            <CardTitle>待筛选学生</CardTitle>
            <div class="flex items-center gap-2">
              <Button variant="outline" size="sm" @click="toggleSelectAll">
                全选
              </Button>
              <Button
                size="sm"
                :disabled="selectedCount === 0"
                @click="assignInterviewers"
              >
                批量分配面试
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead class="w-[50px]">
                  <Checkbox
                    :checked="students.length > 0 && students.every(s => s.selected)"
                    @update:checked="toggleSelectAll"
                  />
                </TableHead>
                <TableHead>学生信息</TableHead>
                <TableHead>面试岗位</TableHead>
                <TableHead>自我介绍</TableHead>
                <TableHead>评分</TableHead>
                <TableHead>操作</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow v-for="student in students" :key="student.id">
                <TableCell>
                  <Checkbox
                    :checked="student.selected"
                    @update:checked="toggleSelect(student)"
                  />
                </TableCell>
                <TableCell>
                  <div class="flex flex-col">
                    <span class="font-medium">{{ student.name }}</span>
                    <span class="text-xs text-muted-foreground">{{ student.student_id }}</span>
                    <span class="text-xs text-muted-foreground">{{ student.phone }}</span>
                  </div>
                </TableCell>
                <TableCell>
                  <div class="flex flex-col">
                    <span>{{ student.position }}</span>
                    <Badge variant="outline" class="w-fit text-xs mt-1">{{ student.department }}</Badge>
                  </div>
                </TableCell>
                <TableCell>
                  <div class="max-w-[300px] truncate text-sm text-muted-foreground">
                    {{ student.self_intro }}
                  </div>
                </TableCell>
                <TableCell>
                  <span class="font-bold" :class="{
                    'text-green-600': student.score >= 85,
                    'text-blue-600': student.score >= 75 && student.score < 85,
                    'text-orange-600': student.score < 75
                  }">{{ student.score }}</span>
                </TableCell>
                <TableCell>
                  <Button variant="outline" size="sm" @click="assignInterview(student)">
                    分配面试
                  </Button>
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      <!-- 已分配面试列表 -->
      <Card>
        <CardHeader>
          <CardTitle>已分配面试</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>学生信息</TableHead>
                <TableHead>面试岗位</TableHead>
                <TableHead>面试官</TableHead>
                <TableHead>面试时间</TableHead>
                <TableHead>操作</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow v-for="student in filteredStudents" :key="student.id">
                <TableCell>
                  <div class="flex flex-col">
                    <span class="font-medium">{{ student.name }}</span>
                    <span class="text-xs text-muted-foreground">{{ student.student_id }}</span>
                  </div>
                </TableCell>
                <TableCell>
                  <div class="flex flex-col">
                    <span>{{ student.position }}</span>
                    <Badge variant="outline" class="w-fit text-xs mt-1">{{ student.department }}</Badge>
                  </div>
                </TableCell>
                <TableCell>
                  <div class="flex flex-wrap gap-1">
                    <Badge v-for="interviewer in student.interviewers" :key="interviewer" variant="outline" class="text-xs">
                      {{ interviewer }}
                    </Badge>
                  </div>
                </TableCell>
                <TableCell class="text-sm text-muted-foreground">
                  {{ student.interview_date }}
                </TableCell>
                <TableCell>
                  <Button variant="ghost" size="sm" @click="cancelInterview(student)">
                    取消
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
