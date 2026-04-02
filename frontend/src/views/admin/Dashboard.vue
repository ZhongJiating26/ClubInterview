<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { checkClubProfile } from '@/api/modules/clubs'
import { getDashboardStats, type DashboardStats } from '@/api/modules/statistics'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import {
  AlertCircle,
  Users,
  Calendar,
  CheckCircle,
  ArrowUp,
  ArrowDown,
  Activity,
  UserCheck,
  Trophy,
  TriangleAlert
} from 'lucide-vue-next'

const router = useRouter()
const userStore = useUserStore()

// 社团资料检查状态
interface ProfileCheck {
  club_id: number
  is_complete: boolean
  missing_fields: string[]
}

const profileCheck = ref<ProfileCheck | null>(null)
const checked = ref(false)
const noClub = ref(false)

// 看板数据
const stats = ref<DashboardStats | null>(null)
const loading = ref(false)
const error = ref('')

// 获取社团资料检查状态
const fetchProfileCheck = async () => {
  if (checked.value && profileCheck.value?.is_complete) {
    return
  }

  const clubAdminRole = userStore.userInfo?.roles.find(r => r.code === 'CLUB_ADMIN')
  const clubId = clubAdminRole?.club_id

  if (!clubId) {
    noClub.value = true
    return
  }

  noClub.value = false

  try {
    const res = await checkClubProfile(clubId)
    profileCheck.value = res
    checked.value = true
  } catch (error) {
  }
}

// 获取看板统计数据
const fetchDashboardStats = async () => {
  const clubAdminRole = userStore.userInfo?.roles.find(r => r.code === 'CLUB_ADMIN')
  const clubId = clubAdminRole?.club_id

  if (!clubId) {
    return
  }

  try {
    loading.value = true
    error.value = ''
    const res = await getDashboardStats(clubId)
    stats.value = res
  } catch (err: any) {
    error.value = err.message || '获取统计数据失败'
  } finally {
    loading.value = false
  }
}

// 缺失字段中文映射
const missingFieldLabels: Record<string, string> = {
  school_code: '学校代码',
  name: '社团名称',
  category: '社团分类',
  description: '社团简介',
  cert_file_url: '证书文件'
}

const getMissingFieldText = (fields: string[]) => {
  return fields.map(f => missingFieldLabels[f] || f).join('、')
}

// 格式化日期
const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  return `${date.getMonth() + 1}月${date.getDate()}日`
}

// 趋势图标和颜色
const getTrendIcon = (value: number) => {
  return value >= 0 ? ArrowUp : ArrowDown
}

const getTrendColor = (value: number) => {
  return value >= 0 ? 'text-green-600' : 'text-red-600'
}

const getTrendBgColor = (value: number) => {
  return value >= 0 ? 'bg-green-50' : 'bg-red-50'
}

const screeningPassedCount = computed(() => stats.value?.total_interviews ?? 0)
const interviewCompletedCount = computed(() => stats.value?.completed_interviews ?? 0)
const interviewPendingCount = computed(() =>
  Math.max((stats.value?.total_interviews ?? 0) - (stats.value?.completed_interviews ?? 0), 0),
)
const interviewToScheduleCount = computed(() =>
  Math.max(
    (stats.value?.total_applications ?? 0) -
      (stats.value?.pending_review ?? 0) -
      (stats.value?.total_interviews ?? 0),
    0,
  ),
)
const rejectedAfterInterviewCount = computed(() =>
  Math.max(interviewCompletedCount.value - (stats.value?.admitted_count ?? 0), 0),
)
const dailyApplicationsMax = computed(() =>
  Math.max(...(stats.value?.daily_applications || []).map(item => item.count), 1),
)
const departmentApplicationsMax = computed(() =>
  Math.max(...(stats.value?.department_stats || []).map(item => item.application_count), 1),
)

const funnelStages = computed(() => {
  const totalApplications = stats.value?.total_applications ?? 0
  const screeningPassed = screeningPassedCount.value
  const interviewCompleted = interviewCompletedCount.value
  const admitted = stats.value?.admitted_count ?? 0
  const maxValue = Math.max(totalApplications, screeningPassed, interviewCompleted, admitted, 1)

  return [
    { label: '报名', count: totalApplications, color: 'bg-slate-900', width: (totalApplications / maxValue) * 100 },
    { label: '初筛通过', count: screeningPassed, color: 'bg-sky-600', width: (screeningPassed / maxValue) * 100 },
    { label: '面试完成', count: interviewCompleted, color: 'bg-amber-500', width: (interviewCompleted / maxValue) * 100 },
    { label: '录取', count: admitted, color: 'bg-emerald-600', width: (admitted / maxValue) * 100 },
  ]
})

const admissionDistribution = computed(() => [
  {
    label: '已录取',
    count: stats.value?.admitted_count ?? 0,
    color: 'bg-emerald-500',
  },
  {
    label: '未录取',
    count: rejectedAfterInterviewCount.value,
    color: 'bg-rose-500',
  },
  {
    label: '待定',
    count: interviewPendingCount.value,
    color: 'bg-amber-400',
  },
])

const hotPositions = computed(() =>
  [...(stats.value?.position_stats || [])]
    .sort((a, b) => b.application_count - a.application_count)
    .slice(0, 5),
)

const shortagePositions = computed(() =>
  [...(stats.value?.position_stats || [])]
    .sort((a, b) => a.application_count - b.application_count)
    .slice(0, 5),
)

const processAlerts = computed(() => {
  const alerts: { title: string; description: string; variant: 'warning' | 'default' }[] = []

  if (profileCheck.value && !profileCheck.value.is_complete) {
    alerts.push({
      title: '社团资料不完整',
      description: `当前仍缺少：${getMissingFieldText(profileCheck.value.missing_fields)}。`,
      variant: 'warning',
    })
  }

  if ((stats.value?.pending_review ?? 0) > 0) {
    alerts.push({
      title: '存在待审核报名',
      description: `当前还有 ${stats.value?.pending_review ?? 0} 份报名未完成初筛，可能影响后续安排。`,
      variant: 'warning',
    })
  }

  if (interviewToScheduleCount.value > 0) {
    alerts.push({
      title: '存在待安排面试',
      description: `${interviewToScheduleCount.value} 名候选人已进入后续流程，但尚未纳入面试安排。`,
      variant: 'warning',
    })
  }

  if (interviewPendingCount.value > 0) {
    alerts.push({
      title: '存在未完成面试',
      description: `${interviewPendingCount.value} 场面试已安排但尚未完成，建议尽快跟进结果录入。`,
      variant: 'default',
    })
  }

  if (!alerts.length) {
    alerts.push({
      title: '流程运行正常',
      description: '当前未发现明显审批或流程阻塞项。',
      variant: 'default',
    })
  }

  return alerts
})

// 跳转到相应页面
const goToPage = (path: string) => {
  router.push(path)
}

onMounted(() => {
  fetchProfileCheck()
  if (!noClub.value) {
    fetchDashboardStats()
  }
})
</script>

<template>
  <div class="flex flex-col flex-1 overflow-hidden">
    <!-- 主内容区 -->
    <div class="flex-1 min-h-0 overflow-y-auto p-6">
      <!-- 页面标题 -->
      <div class="mb-6">
        <div>
          <h1 class="text-2xl font-bold mb-2">数据看板</h1>
          <p class="text-muted-foreground">实时查看社团招新数据和统计信息</p>
        </div>
      </div>

      <!-- 加载状态 -->
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="text-center">
          <Activity class="w-8 h-8 text-muted-foreground animate-spin mx-auto mb-4" />
          <p class="text-muted-foreground">加载中...</p>
        </div>
      </div>

      <!-- 错误提示 -->
      <div v-else-if="error" class="mb-6 p-4 text-sm text-red-600 bg-red-50 rounded-md">
        {{ error }}
      </div>

      <!-- 还未创建社团提示 -->
      <Alert v-else-if="noClub" variant="warning" class="mb-6">
        <AlertCircle class="h-4 w-4" />
        <AlertTitle>还未创建社团</AlertTitle>
        <AlertDescription>
          您还没有创建社团，请先创建社团后再进行管理。
        </AlertDescription>
      </Alert>

      <!-- 社团资料不完整提示 -->
      <Alert v-else-if="!stats && profileCheck && !profileCheck.is_complete" variant="warning" class="mb-6">
        <AlertCircle class="h-4 w-4" />
        <div class="grid grid-cols-[1fr_auto] gap-2 items-center">
          <div>
            <AlertTitle>社团资料不完整</AlertTitle>
            <AlertDescription>
              您的社团资料还缺少以下信息：{{ getMissingFieldText(profileCheck.missing_fields) }}。
            </AlertDescription>
          </div>
          <Button @click="goToPage('/admin/clubs/profile')">
            立即完善
          </Button>
        </div>
      </Alert>

      <!-- 看板内容 -->
      <template v-if="stats">
        <Alert
          v-if="profileCheck && !profileCheck.is_complete"
          variant="warning"
          class="mb-6"
        >
          <AlertCircle class="h-4 w-4" />
          <div class="grid grid-cols-[1fr_auto] gap-2 items-center">
            <div>
              <AlertTitle>社团资料不完整</AlertTitle>
              <AlertDescription>
                您的社团资料还缺少以下信息：{{ getMissingFieldText(profileCheck.missing_fields) }}。
                请尽快完善，以免影响招新信息展示与流程推进。
              </AlertDescription>
            </div>
            <Button @click="goToPage('/admin/clubs/profile')">
              立即完善
            </Button>
          </div>
        </Alert>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <Card>
            <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle class="text-sm font-medium text-muted-foreground">报名人数</CardTitle>
              <Users class="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div class="flex items-center justify-between">
                <div class="text-2xl font-bold">{{ stats.total_applications ?? 0 }}</div>
                <div v-if="stats.application_growth !== undefined" class="flex items-center gap-1">
                  <component :is="getTrendIcon(stats.application_growth)" class="w-4 h-4" :class="getTrendColor(stats.application_growth)" />
                  <span class="text-sm font-medium" :class="getTrendColor(stats.application_growth)">
                    {{ Math.abs(stats.application_growth) }}%
                  </span>
                </div>
              </div>
              <p class="text-xs text-muted-foreground mt-1">较上期增长</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle class="text-sm font-medium text-muted-foreground">通过人数</CardTitle>
              <UserCheck class="h-4 w-4 text-sky-600" />
            </CardHeader>
            <CardContent>
              <div class="text-2xl font-bold">{{ screeningPassedCount }}</div>
              <p class="text-xs text-muted-foreground mt-1">进入面试流程的人数</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle class="text-sm font-medium text-muted-foreground">面试人数</CardTitle>
              <Calendar class="h-4 w-4 text-amber-500" />
            </CardHeader>
            <CardContent>
              <div class="text-2xl font-bold">{{ interviewCompletedCount }}</div>
              <p class="text-xs text-muted-foreground mt-1">已完成的面试数量</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle class="text-sm font-medium text-muted-foreground">录取人数</CardTitle>
              <CheckCircle class="h-4 w-4 text-green-600" />
            </CardHeader>
            <CardContent>
              <div class="flex items-center justify-between">
                <div class="text-2xl font-bold">{{ stats.admitted_count ?? 0 }}</div>
                <Badge :class="getTrendBgColor(stats.admission_rate)" class="text-sm text-green-700">
                  {{ stats.admission_rate ?? 0 }}% 录取率
                </Badge>
              </div>
              <p class="text-xs text-muted-foreground mt-1">录取率统计</p>
            </CardContent>
          </Card>
        </div>

        <div class="grid grid-cols-1 xl:grid-cols-3 gap-6 mb-6">
          <Card>
            <CardHeader>
              <CardTitle>转化漏斗</CardTitle>
            </CardHeader>
            <CardContent class="space-y-4">
              <div
                v-for="stage in funnelStages"
                :key="stage.label"
                class="space-y-2"
              >
                <div class="flex items-center justify-between text-sm">
                  <span class="font-medium">{{ stage.label }}</span>
                  <span class="text-muted-foreground">{{ stage.count }} 人</span>
                </div>
                <div class="h-3 rounded-full bg-slate-100 overflow-hidden">
                  <div
                    class="h-full rounded-full transition-all"
                    :class="stage.color"
                    :style="{ width: `${stage.width}%` }"
                  ></div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card class="xl:col-span-2">
            <CardHeader>
              <CardTitle>各时间段报名趋势</CardTitle>
            </CardHeader>
            <CardContent>
              <div class="h-64 flex items-end gap-2">
                <div
                  v-for="item in (stats.daily_applications || [])"
                  :key="item.date"
                  class="flex-1 flex flex-col items-center gap-2"
                >
                  <div
                    class="w-full bg-gray-400 rounded-t-md transition-all hover:bg-gray-500"
                    :style="{ height: `${(item.count / dailyApplicationsMax) * 200}px` }"
                  ></div>
                  <span class="text-xs text-muted-foreground">{{ formatDate(item.date) }}</span>
                  <span class="text-sm font-medium">{{ item.count }}</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <div class="grid grid-cols-1 xl:grid-cols-3 gap-6 mb-6">
          <Card>
            <CardHeader>
              <CardTitle>面试安排情况</CardTitle>
            </CardHeader>
            <CardContent class="space-y-4">
              <div class="grid grid-cols-3 gap-3">
                <div class="rounded-lg bg-slate-50 p-4">
                  <div class="text-xs text-muted-foreground mb-1">已安排</div>
                  <div class="text-2xl font-bold">{{ stats.total_interviews ?? 0 }}</div>
                </div>
                <div class="rounded-lg bg-amber-50 p-4">
                  <div class="text-xs text-muted-foreground mb-1">待安排</div>
                  <div class="text-2xl font-bold text-amber-700">{{ interviewToScheduleCount }}</div>
                </div>
                <div class="rounded-lg bg-emerald-50 p-4">
                  <div class="text-xs text-muted-foreground mb-1">已完成</div>
                  <div class="text-2xl font-bold text-emerald-700">{{ interviewCompletedCount }}</div>
                </div>
              </div>

              <div class="space-y-2 pt-2">
                <div class="flex items-center justify-between">
                  <span class="text-sm text-muted-foreground">面试完成率</span>
                  <span class="text-sm font-semibold">{{ stats.interview_completion_rate ?? 0 }}%</span>
                </div>
                <div class="w-full bg-gray-200 rounded-full h-2">
                  <div
                    class="bg-blue-600 h-2 rounded-full transition-all"
                    :style="{ width: `${stats.interview_completion_rate ?? 0}%` }"
                  ></div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>录取结果分布</CardTitle>
            </CardHeader>
            <CardContent class="space-y-4">
              <div
                v-for="item in admissionDistribution"
                :key="item.label"
                class="space-y-2"
              >
                <div class="flex items-center justify-between text-sm">
                  <div class="flex items-center gap-2">
                    <span class="inline-block w-2.5 h-2.5 rounded-full" :class="item.color"></span>
                    <span>{{ item.label }}</span>
                  </div>
                  <span class="font-medium">{{ item.count }} 人</span>
                </div>
                <div class="h-2 rounded-full bg-slate-100 overflow-hidden">
                  <div
                    class="h-full rounded-full transition-all"
                    :class="item.color"
                    :style="{ width: `${(item.count / Math.max(stats.total_interviews || 0, 1)) * 100}%` }"
                  ></div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader class="flex flex-row items-center justify-between space-y-0">
              <CardTitle>审批与流程异常提醒</CardTitle>
              <TriangleAlert class="w-4 h-4 text-amber-500" />
            </CardHeader>
            <CardContent class="space-y-3">
              <div
                v-for="alert in processAlerts"
                :key="alert.title"
                class="rounded-lg border px-4 py-3"
                :class="alert.variant === 'warning' ? 'border-amber-200 bg-amber-50' : 'border-slate-200 bg-slate-50'"
              >
                <div class="font-medium mb-1">{{ alert.title }}</div>
                <div class="text-sm text-muted-foreground">{{ alert.description }}</div>
              </div>

              <Button
                variant="outline"
                class="w-full"
                @click="goToPage('/admin/applications/review')"
              >
                前往审核中心
              </Button>
            </CardContent>
          </Card>
        </div>

        <div class="grid grid-cols-1 xl:grid-cols-2 gap-6 mb-6">
          <Card>
            <CardHeader>
              <CardTitle>各部门报名情况</CardTitle>
            </CardHeader>
            <CardContent>
              <div class="space-y-4">
                <div
                  v-for="dept in (stats.department_stats || [])"
                  :key="dept.department_name"
                  class="flex items-center justify-between"
                >
                  <div class="flex-1">
                    <div class="flex items-center justify-between mb-2">
                      <span class="font-medium">{{ dept.department_name }}</span>
                      <span class="text-sm text-muted-foreground">{{ dept.application_count }} 人报名</span>
                    </div>
                    <div class="w-full bg-gray-200 rounded-full h-2">
                      <div
                        class="bg-primary h-2 rounded-full transition-all"
                        :style="{ width: `${(dept.application_count / departmentApplicationsMax) * 100}%` }"
                      ></div>
                    </div>
                  </div>
                  <div class="ml-4 text-sm">
                    <span class="text-green-600 font-medium">{{ dept.admission_count }}</span>
                    <span class="text-muted-foreground"> / {{ dept.application_count }} 录取</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>各岗位报名情况</CardTitle>
            </CardHeader>
            <CardContent class="space-y-3">
              <div
                v-for="position in (stats.position_stats || [])"
                :key="`${position.department_name}-${position.position_name}`"
                class="rounded-lg border p-4"
              >
                <div class="flex items-center justify-between gap-4 mb-2">
                  <div class="min-w-0">
                    <div class="font-medium truncate">{{ position.position_name }}</div>
                    <div class="text-xs text-muted-foreground">{{ position.department_name }}</div>
                  </div>
                  <Badge variant="outline">{{ position.application_count }} 人报名</Badge>
                </div>
                <div class="text-sm text-muted-foreground">
                  录取 {{ position.admission_count }} 人
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <div class="grid grid-cols-1 xl:grid-cols-2 gap-6">
          <Card>
            <CardHeader class="flex flex-row items-center justify-between space-y-0">
              <CardTitle>热门岗位</CardTitle>
              <Trophy class="w-4 h-4 text-amber-500" />
            </CardHeader>
            <CardContent>
              <div class="space-y-3">
                <div
                  v-for="(position, index) in hotPositions"
                  :key="`${position.department_name}-${position.position_name}`"
                  class="flex items-center gap-4 p-3 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  <div class="flex-shrink-0 w-8 h-8 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-sm font-medium">
                    {{ index + 1 }}
                  </div>
                  <div class="flex-1 min-w-0">
                    <div class="flex items-center gap-2 mb-1">
                      <span class="font-medium truncate">{{ position.position_name }}</span>
                      <Badge variant="outline" class="text-xs">{{ position.department_name }}</Badge>
                    </div>
                    <div class="flex items-center gap-4 text-sm">
                      <span class="text-muted-foreground">{{ position.application_count }} 人报名</span>
                      <span class="text-green-600">{{ position.admission_count }} 人录取</span>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>报名不足岗位</CardTitle>
            </CardHeader>
            <CardContent>
              <div class="space-y-3">
                <div
                  v-for="position in shortagePositions"
                  :key="`${position.department_name}-${position.position_name}`"
                  class="rounded-lg border border-dashed p-4"
                >
                  <div class="flex items-center justify-between gap-4">
                    <div>
                      <div class="font-medium">{{ position.position_name }}</div>
                      <div class="text-xs text-muted-foreground">{{ position.department_name }}</div>
                    </div>
                    <div class="text-right">
                      <div class="text-lg font-bold text-amber-700">{{ position.application_count }}</div>
                      <div class="text-xs text-muted-foreground">当前报名</div>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </template>
    </div>
  </div>
</template>
