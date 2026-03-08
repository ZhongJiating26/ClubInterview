<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue'
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
import { getRecruitmentSessions, type RecruitmentSession } from '@/api/modules/recruitment'
import { getInterviewFilter, type PendingCandidate, type ScheduledCandidate } from '@/api/modules/interview'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

// 招新场次列表
const recruitmentSessions = ref<RecruitmentSession[]>([])
const sessionsLoading = ref(false)

// 待筛选学生
const pendingCandidates = ref<(PendingCandidate & { selected: boolean })[]>([])
const selectedCount = ref(0)
const pendingLoading = ref(false)

// 已安排面试学生
const scheduledCandidates = ref<ScheduledCandidate[]>([])
const scheduledLoading = ref(false)

const sessionFilter = ref('all')
const departmentFilter = ref('all')

// 加载招新场次列表
const loadRecruitmentSessions = async () => {
  sessionsLoading.value = true
  try {
    // 获取当前用户管理的社团的招新场次
    const clubId = userStore.userInfo?.roles?.[0]?.club_id
    const sessions = await getRecruitmentSessions({ club_id: clubId })
    recruitmentSessions.value = sessions || []
  } catch (error) {
    console.error('加载招新场次失败:', error)
  } finally {
    sessionsLoading.value = false
  }
}

// 加载面试筛选数据
const loadInterviewFilter = async () => {
  if (!sessionFilter.value || sessionFilter.value === 'all') {
    pendingCandidates.value = []
    scheduledCandidates.value = []
    return
  }

  const sessionId = parseInt(sessionFilter.value)
  const clubId = userStore.userInfo?.roles?.[0]?.club_id

  pendingLoading.value = true
  scheduledLoading.value = true

  try {
    const data = await getInterviewFilter({
      recruitment_session_id: sessionId,
      club_id: clubId
    })

    // 处理待筛选学生
    pendingCandidates.value = (data.pending_candidates || []).map(item => ({
      ...item,
      selected: false
    }))

    // 处理已安排面试学生
    scheduledCandidates.value = data.scheduled_candidates || []
  } catch (error) {
    console.error('加载面试筛选数据失败:', error)
  } finally {
    pendingLoading.value = false
    scheduledLoading.value = false
  }
}

// 监听招新场次选择变化
watch(sessionFilter, (newVal) => {
  if (newVal && newVal !== 'all') {
    loadInterviewFilter()
  } else {
    pendingCandidates.value = []
    scheduledCandidates.value = []
  }
})

// 切换选择状态
const toggleSelect = (candidate: PendingCandidate & { selected: boolean }) => {
  candidate.selected = !candidate.selected
  selectedCount.value = pendingCandidates.value.filter(s => s.selected).length
}

// 全选/取消全选
const toggleSelectAll = () => {
  const allSelected = pendingCandidates.value.every(s => s.selected)
  pendingCandidates.value.forEach(s => s.selected = !allSelected)
  selectedCount.value = allSelected ? 0 : pendingCandidates.value.length
}

// 批量分配面试官
const assignInterviewers = () => {
  console.log('批量分配面试官', pendingCandidates.value.filter(s => s.selected))
}

// 分配面试
const assignInterview = (candidate: PendingCandidate) => {
  console.log('分配面试', candidate)
}

// 取消面试
const cancelInterview = (candidate: ScheduledCandidate) => {
  console.log('取消面试', candidate)
}

// 获取部门列表（从待筛选数据中提取）
const departments = computed(() => {
  const deptSet = new Set<string>()
  pendingCandidates.value.forEach(c => {
    if (c.department_name) deptSet.add(c.department_name)
  })
  scheduledCandidates.value.forEach(c => {
    if (c.department_name) deptSet.add(c.department_name)
  })
  return Array.from(deptSet)
})

// 过滤后的待筛选学生
const filteredPendingCandidates = computed(() => {
  if (departmentFilter.value === 'all') return pendingCandidates.value
  return pendingCandidates.value.filter(c => c.department_name === departmentFilter.value)
})

onMounted(() => {
  loadRecruitmentSessions()
})
</script>

<template>
  <div class="absolute inset-0 flex flex-col">
    <div class="flex-1 min-h-0 overflow-y-auto p-6">
      <div class="mb-6">
        <h1 class="text-2xl font-bold mb-4">面试筛选</h1>

        <!-- 筛选器 -->
        <div class="flex gap-3">
          <Select v-model="sessionFilter">
            <SelectTrigger class="w-[250px]" :disabled="sessionsLoading">
              <SelectValue placeholder="选择招新场次" />
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
          <Select v-model="departmentFilter" :disabled="!sessionFilter || sessionFilter === 'all'">
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
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <Card>
          <CardContent class="pt-6">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm text-muted-foreground">待筛选</p>
                <p class="text-2xl font-bold">{{ pendingCandidates.length }}</p>
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
                <p class="text-2xl font-bold text-green-600">{{ scheduledCandidates.length }}</p>
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
              <Button variant="outline" size="sm" @click="toggleSelectAll" :disabled="pendingCandidates.length === 0">
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
          <div v-if="pendingLoading" class="text-center py-8 text-muted-foreground">
            加载中...
          </div>
          <Table v-else-if="filteredPendingCandidates.length > 0">
            <TableHeader>
              <TableRow>
                <TableHead class="w-[50px]">
                  <Checkbox
                    :checked="pendingCandidates.length > 0 && pendingCandidates.every(s => s.selected)"
                    @update:checked="toggleSelectAll"
                  />
                </TableHead>
                <TableHead>学生信息</TableHead>
                <TableHead>面试岗位</TableHead>
                <TableHead>自我介绍</TableHead>
                <TableHead>操作</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow v-for="candidate in filteredPendingCandidates" :key="candidate.signup_session_id">
                <TableCell>
                  <Checkbox
                    :checked="candidate.selected"
                    @update:checked="toggleSelect(candidate)"
                  />
                </TableCell>
                <TableCell>
                  <div class="flex flex-col">
                    <span class="font-medium">{{ candidate.user_name || '未知' }}</span>
                    <span class="text-xs text-muted-foreground">{{ candidate.user_phone || '' }}</span>
                  </div>
                </TableCell>
                <TableCell>
                  <div class="flex flex-col">
                    <span>{{ candidate.position_name || '未知岗位' }}</span>
                    <Badge v-if="candidate.department_name" variant="outline" class="w-fit text-xs mt-1">{{ candidate.department_name }}</Badge>
                  </div>
                </TableCell>
                <TableCell>
                  <div class="max-w-[300px] truncate text-sm text-muted-foreground">
                    {{ candidate.self_intro || '无' }}
                  </div>
                </TableCell>
                <TableCell>
                  <Button variant="outline" size="sm" @click="assignInterview(candidate)">
                    分配面试
                  </Button>
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
          <div v-else class="text-center py-8 text-muted-foreground">
            {{ sessionFilter === 'all' ? '请选择招新场次' : '暂无待筛选学生' }}
          </div>
        </CardContent>
      </Card>

      <!-- 已分配面试列表 -->
      <Card>
        <CardHeader>
          <CardTitle>已分配面试</CardTitle>
        </CardHeader>
        <CardContent>
          <div v-if="scheduledLoading" class="text-center py-8 text-muted-foreground">
            加载中...
          </div>
          <Table v-else-if="scheduledCandidates.length > 0">
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
              <TableRow v-for="candidate in scheduledCandidates" :key="candidate.candidate_id">
                <TableCell>
                  <div class="flex flex-col">
                    <span class="font-medium">{{ candidate.user_name || '未知' }}</span>
                    <span class="text-xs text-muted-foreground">{{ candidate.user_phone || '' }}</span>
                  </div>
                </TableCell>
                <TableCell>
                  <div class="flex flex-col">
                    <span>{{ candidate.position_name || '未知岗位' }}</span>
                    <Badge v-if="candidate.department_name" variant="outline" class="w-fit text-xs mt-1">{{ candidate.department_name }}</Badge>
                  </div>
                </TableCell>
                <TableCell>
                  <div class="flex flex-wrap gap-1">
                    <Badge v-for="interviewer in candidate.interviewers" :key="interviewer" variant="outline" class="text-xs">
                      {{ interviewer }}
                    </Badge>
                  </div>
                </TableCell>
                <TableCell class="text-sm text-muted-foreground">
                  {{ candidate.planned_start_time ? new Date(candidate.planned_start_time).toLocaleString() : '待安排' }}
                </TableCell>
                <TableCell>
                  <Button variant="ghost" size="sm" @click="cancelInterview(candidate)">
                    取消
                  </Button>
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
          <div v-else class="text-center py-8 text-muted-foreground">
            {{ sessionFilter === 'all' ? '请选择招新场次' : '暂无已分配面试学生' }}
          </div>
        </CardContent>
      </Card>
    </div>
  </div>
</template>
