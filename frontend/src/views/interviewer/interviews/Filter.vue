<script setup lang="ts">
import { ref, computed } from 'vue'
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

const router = useRouter()

// 模拟待面试候选人数据
const candidates = ref([
  {
    id: 1,
    name: '张三',
    student_id: '202301001',
    phone: '13812341234',
    email: 'zhangsan@example.com',
    department: '技术部',
    position: '前端开发',
    session_name: '2026年春季招新第一轮',
    planned_time: '2026-01-07 14:00',
    status: 'SCHEDULED',
    self_intro: '热爱编程，有Vue开发经验，希望加入技术部提升自己。掌握HTML、CSS、JavaScript基础，熟悉Vue3框架。',
    skills: ['Vue3', 'TypeScript', 'TailwindCSS', 'Git'],
    signup_time: '2026-01-01 10:30'
  },
  {
    id: 2,
    name: '李四',
    student_id: '202301002',
    phone: '13956785678',
    email: 'lisi@example.com',
    department: '活动部',
    position: '活动策划',
    session_name: '2026年春季招新第一轮',
    planned_time: '2026-01-07 15:00',
    status: 'SCHEDULED',
    self_intro: '性格开朗，组织能力强，曾组织多次班级活动。希望能在活动部发挥自己的能力，为社团活动增添色彩。',
    skills: ['活动策划', '团队协作', 'PPT制作'],
    signup_time: '2026-01-01 11:20'
  },
  {
    id: 3,
    name: '王五',
    student_id: '202301003',
    phone: '13790129012',
    email: 'wangwu@example.com',
    department: '技术部',
    position: '后端开发',
    session_name: '2026年春季招新第一轮',
    planned_time: '2026-01-07 16:00',
    status: 'SCHEDULED',
    self_intro: '熟悉Python和Java，对后端架构有深入了解。有项目开发经验，希望能在技术部继续提升技术能力。',
    skills: ['Python', 'Java', 'MySQL', 'Redis', 'FastAPI'],
    signup_time: '2026-01-01 14:50'
  },
  {
    id: 4,
    name: '赵六',
    student_id: '202301004',
    phone: '13634563456',
    email: 'zhaoliu@example.com',
    department: '宣传部',
    position: '新媒体运营',
    session_name: '2026年春季招新第二轮',
    planned_time: '2026-01-08 10:00',
    status: 'SCHEDULED',
    self_intro: '擅长文案写作和视频剪辑，运营过个人抖音账号，粉丝过万。对新媒体营销有自己的理解。',
    skills: ['文案写作', '视频剪辑', '抖音运营', '平面设计'],
    signup_time: '2026-01-02 09:15'
  },
  {
    id: 5,
    name: '孙七',
    student_id: '202301005',
    phone: '13578907890',
    email: 'sunqi@example.com',
    department: '外联部',
    position: '外联干事',
    session_name: '2026年春季招新第二轮',
    planned_time: '2026-01-08 11:00',
    status: 'SCHEDULED',
    self_intro: '沟通能力强，有校外合作经验。曾成功拉取多次赞助，希望能在外联部继续锻炼自己的能力。',
    skills: ['商务谈判', '沟通能力', '赞助洽谈'],
    signup_time: '2026-01-02 10:45'
  }
])

// 已完成的面试
const completedCandidates = ref([
  {
    id: 6,
    name: '周八',
    student_id: '202301006',
    department: '技术部',
    position: '前端开发',
    session_name: '2026年春季招新第一轮',
    interview_time: '2026-01-05 14:00',
    score: 85,
    notes: '技术基础扎实，Vue经验丰富'
  },
  {
    id: 7,
    name: '吴九',
    student_id: '202301007',
    department: '活动部',
    position: '活动策划',
    session_name: '2026年春季招新第一轮',
    interview_time: '2026-01-05 15:30',
    score: 78,
    notes: '表达清晰，有创意'
  }
])

// 筛选条件
const searchKeyword = ref('')
const sessionFilter = ref('all')
const departmentFilter = ref('all')

// 选中的候选人
const selectedCandidate = ref<any>(null)
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

// 过滤后的候选人
const filteredCandidates = computed(() => {
  let filtered = candidates.value

  // 关键词搜索
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    filtered = filtered.filter(c =>
      c.name.toLowerCase().includes(keyword) ||
      c.student_id.includes(keyword) ||
      c.position.toLowerCase().includes(keyword)
    )
  }

  // 场次筛选
  if (sessionFilter.value !== 'all') {
    filtered = filtered.filter(c => c.session_name.includes(sessionFilter.value))
  }

  // 部门筛选
  if (departmentFilter.value !== 'all') {
    filtered = filtered.filter(c => c.department === departmentFilter.value)
  }

  return filtered
})

// 统计数据
const stats = computed(() => {
  const total = candidates.value.length
  const completed = completedCandidates.value.length
  const today = candidates.value.filter(c => c.planned_time.startsWith('2026-01-07')).length

  return { total, completed, today }
})

// 打开详情对话框
const openDetail = (candidate: any) => {
  selectedCandidate.value = candidate
  showDetailDialog.value = true
}

// 开始面试
const startInterview = (candidate: any) => {
  router.push({
    name: 'InterviewerInterviewsScore',
    query: { candidateId: candidate.id }
  })
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
              placeholder="搜索姓名、学号、岗位..."
              class="pl-9"
            />
          </div>
          <Select v-model="sessionFilter">
            <SelectTrigger class="w-[180px]">
              <SelectValue placeholder="选择场次" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">全部场次</SelectItem>
              <SelectItem value="第一轮">第一轮</SelectItem>
              <SelectItem value="第二轮">第二轮</SelectItem>
            </SelectContent>
          </Select>
          <Select v-model="departmentFilter">
            <SelectTrigger class="w-[150px]">
              <SelectValue placeholder="选择部门" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">全部部门</SelectItem>
              <SelectItem value="技术部">技术部</SelectItem>
              <SelectItem value="活动部">活动部</SelectItem>
              <SelectItem value="宣传部">宣传部</SelectItem>
              <SelectItem value="外联部">外联部</SelectItem>
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
                <p class="text-sm text-gray-600">待面试</p>
                <p class="text-2xl font-bold">{{ stats.total }}</p>
              </div>
              <User class="w-8 h-8 text-gray-400" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent class="pt-6">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm text-gray-600">已完成</p>
                <p class="text-2xl font-bold text-green-600">{{ stats.completed }}</p>
              </div>
              <CheckCircle2 class="w-8 h-8 text-green-600 opacity-50" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent class="pt-6">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm text-gray-600">今日面试</p>
                <p class="text-2xl font-bold text-blue-600">{{ stats.today }}</p>
              </div>
              <Calendar class="w-8 h-8 text-blue-600 opacity-50" />
            </div>
          </CardContent>
        </Card>
      </div>

      <!-- 待面试候选人列表 -->
      <Card class="mb-6">
        <CardHeader>
          <CardTitle>待面试候选人</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
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
              <TableRow v-for="candidate in filteredCandidates" :key="candidate.id">
                <TableCell>
                  <div class="flex flex-col">
                    <span class="font-medium">{{ candidate.name }}</span>
                    <span class="text-xs text-gray-500">{{ candidate.student_id }}</span>
                    <span class="text-xs text-gray-500">{{ candidate.phone }}</span>
                  </div>
                </TableCell>
                <TableCell>
                  <div class="flex flex-col">
                    <span>{{ candidate.position }}</span>
                    <Badge variant="outline" class="w-fit text-xs mt-1">{{ candidate.department }}</Badge>
                  </div>
                </TableCell>
                <TableCell class="text-sm text-gray-600">
                  {{ candidate.session_name }}
                </TableCell>
                <TableCell class="text-sm text-gray-600">
                  {{ formatDate(candidate.planned_time) }}
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
          <div v-if="filteredCandidates.length === 0" class="text-center py-12">
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
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>候选人信息</TableHead>
                <TableHead>应聘岗位</TableHead>
                <TableHead>面试时间</TableHead>
                <TableHead>评分</TableHead>
                <TableHead>评语</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow v-for="candidate in completedCandidates" :key="candidate.id">
                <TableCell>
                  <div class="flex flex-col">
                    <span class="font-medium">{{ candidate.name }}</span>
                    <span class="text-xs text-gray-500">{{ candidate.student_id }}</span>
                  </div>
                </TableCell>
                <TableCell>
                  <div class="flex flex-col">
                    <span>{{ candidate.position }}</span>
                    <Badge variant="outline" class="w-fit text-xs mt-1">{{ candidate.department }}</Badge>
                  </div>
                </TableCell>
                <TableCell class="text-sm text-gray-600">
                  {{ formatDate(candidate.interview_time) }}
                </TableCell>
                <TableCell>
                  <span class="font-bold" :class="{
                    'text-green-600': candidate.score >= 85,
                    'text-blue-600': candidate.score >= 75 && candidate.score < 85,
                    'text-orange-600': candidate.score < 75
                  }">{{ candidate.score }}</span>
                </TableCell>
                <TableCell class="text-sm text-gray-600 max-w-[200px] truncate">
                  {{ candidate.notes }}
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>

          <!-- 空状态 -->
          <div v-if="completedCandidates.length === 0" class="text-center py-12">
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
                <span>{{ selectedCandidate.name }}</span>
                <span class="text-gray-500">({{ selectedCandidate.student_id }})</span>
              </div>
              <div class="flex items-center gap-2">
                <Phone class="w-4 h-4 text-gray-400" />
                <span>{{ selectedCandidate.phone }}</span>
              </div>
              <div class="flex items-center gap-2 col-span-2">
                <Mail class="w-4 h-4 text-gray-400" />
                <span>{{ selectedCandidate.email }}</span>
              </div>
            </div>
          </div>

          <!-- 面试信息 -->
          <div class="space-y-2">
            <h4 class="font-semibold text-gray-700">面试信息</h4>
            <div class="grid grid-cols-2 gap-2 text-sm">
              <div>
                <span class="text-gray-500">面试场次：</span>
                <span class="text-gray-800">{{ selectedCandidate.session_name }}</span>
              </div>
              <div>
                <span class="text-gray-500">面试时间：</span>
                <span class="text-gray-800">{{ formatDate(selectedCandidate.planned_time) }}</span>
              </div>
              <div>
                <span class="text-gray-500">应聘部门：</span>
                <Badge variant="outline" class="bg-blue-50 text-blue-700 border-blue-200">{{ selectedCandidate.department }}</Badge>
              </div>
              <div>
                <span class="text-gray-500">应聘岗位：</span>
                <Badge variant="outline" class="bg-purple-50 text-purple-700 border-purple-200">{{ selectedCandidate.position }}</Badge>
              </div>
            </div>
          </div>

          <!-- 自我介绍 -->
          <div class="space-y-2">
            <h4 class="font-semibold text-gray-700">自我介绍</h4>
            <p class="text-sm text-gray-600 bg-gray-50 p-3 rounded-md">{{ selectedCandidate.self_intro }}</p>
          </div>

          <!-- 技能 -->
          <div class="space-y-2">
            <h4 class="font-semibold text-gray-700">技能标签</h4>
            <div class="flex flex-wrap gap-2">
              <Badge
                v-for="skill in selectedCandidate.skills"
                :key="skill"
                variant="secondary"
                class="bg-blue-50 text-blue-700"
              >
                {{ skill }}
              </Badge>
            </div>
          </div>

          <!-- 报名时间 -->
          <div class="text-sm text-gray-500">
            报名时间：{{ formatDate(selectedCandidate.signup_time) }}
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
