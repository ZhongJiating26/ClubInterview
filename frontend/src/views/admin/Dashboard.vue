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
  FileText,
  Calendar,
  CheckCircle,
  Clock,
  TrendingUp,
  ArrowUp,
  ArrowDown,
  Activity
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
const useMockData = ref(true) // 默认使用模拟数据

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

    if (useMockData.value) {
      // 模拟数据（演示阶段使用）
      stats.value = {
        total_sessions: 12,
        active_sessions: 3,
        total_applications: 248,
        pending_review: 35,
        total_interviews: 156,
        completed_interviews: 98,
        admitted_count: 67,
        application_growth: 15.6,
        interview_completion_rate: 62.8,
        admission_rate: 43.0,
        daily_applications: [
          { date: '2025-12-08', count: 18 },
          { date: '2025-12-09', count: 24 },
          { date: '2025-12-10', count: 32 },
          { date: '2025-12-11', count: 28 },
          { date: '2025-12-12', count: 35 },
          { date: '2025-12-13', count: 42 },
          { date: '2025-12-14', count: 38 }
        ],
        department_stats: [
          { department_name: '技术部', application_count: 89, admission_count: 42 },
          { department_name: '活动部', application_count: 67, admission_count: 28 },
          { department_name: '外联部', application_count: 52, admission_count: 18 },
          { department_name: '宣传部', application_count: 40, admission_count: 15 }
        ],
        position_stats: [
          { position_name: '前端开发', department_name: '技术部', application_count: 45, admission_count: 22 },
          { position_name: '后端开发', department_name: '技术部', application_count: 38, admission_count: 18 },
          { position_name: '活动策划', department_name: '活动部', application_count: 35, admission_count: 15 },
          { position_name: '新媒体运营', department_name: '宣传部', application_count: 28, admission_count: 11 }
        ]
      }
    } else {
      // 调用后端接口获取真实数据
      const res = await getDashboardStats(clubId)
      stats.value = res
    }
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
      <div class="mb-6 flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold mb-2">数据看板</h1>
          <p class="text-muted-foreground">实时查看社团招新数据和统计信息</p>
        </div>
        <div class="flex items-center gap-3">
          <span class="text-sm text-muted-foreground">
            {{ useMockData ? '演示数据' : '真实数据' }}
          </span>
          <Button
            @click="useMockData = !useMockData; fetchDashboardStats()"
            :variant="useMockData ? 'default' : 'outline'"
            size="sm"
          >
            {{ useMockData ? '切换到真实数据' : '切换到演示数据' }}
          </Button>
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
      <Alert v-else-if="profileCheck && !profileCheck.is_complete" variant="warning" class="mb-6">
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
      <template v-if="stats && profileCheck?.is_complete">
        <!-- 统计卡片 -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <!-- 进行中招新场次 -->
          <Card>
            <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle class="text-sm font-medium text-muted-foreground">进行中招新</CardTitle>
              <Calendar class="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div class="text-2xl font-bold">{{ stats.active_sessions ?? 0 }}</div>
              <p class="text-xs text-muted-foreground mt-1">共 {{ stats.total_sessions ?? 0 }} 个场次</p>
            </CardContent>
          </Card>

          <!-- 总报名人数 -->
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

          <!-- 待审核 -->
          <Card @click="goToPage('/admin/applications/review')" class="cursor-pointer hover:shadow-md transition-shadow">
            <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle class="text-sm font-medium text-muted-foreground">待审核</CardTitle>
              <FileText class="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div class="text-2xl font-bold text-orange-600">{{ stats.pending_review ?? 0 }}</div>
              <p class="text-xs text-muted-foreground mt-1">点击前往审核</p>
            </CardContent>
          </Card>

          <!-- 已录取 -->
          <Card>
            <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle class="text-sm font-medium text-muted-foreground">已录取</CardTitle>
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

        <!-- 图表和列表 -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <!-- 报名趋势图 -->
          <Card class="lg:col-span-2">
            <CardHeader>
              <CardTitle>近7天报名趋势</CardTitle>
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
                    :style="{ height: `${(item.count / Math.max(...(stats.daily_applications || []).map(d => d.count))) * 200}px` }"
                  ></div>
                  <span class="text-xs text-muted-foreground">{{ formatDate(item.date) }}</span>
                  <span class="text-sm font-medium">{{ item.count }}</span>
                </div>
              </div>
            </CardContent>
          </Card>

          <!-- 关键指标 -->
          <Card>
            <CardHeader>
              <CardTitle>关键指标</CardTitle>
            </CardHeader>
            <CardContent class="space-y-4">
              <div class="space-y-2">
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

              <div class="space-y-2">
                <div class="flex items-center justify-between">
                  <span class="text-sm text-muted-foreground">录取率</span>
                  <span class="text-sm font-semibold">{{ stats.admission_rate ?? 0 }}%</span>
                </div>
                <div class="w-full bg-gray-200 rounded-full h-2">
                  <div
                    class="bg-green-600 h-2 rounded-full transition-all"
                    :style="{ width: `${stats.admission_rate ?? 0}%` }"
                  ></div>
                </div>
              </div>

              <div class="pt-4 space-y-3">
                <div class="flex items-center justify-between text-sm">
                  <span class="text-muted-foreground">总面试数</span>
                  <span class="font-medium">{{ stats.total_interviews ?? 0 }}</span>
                </div>
                <div class="flex items-center justify-between text-sm">
                  <span class="text-muted-foreground">已完成</span>
                  <span class="font-medium text-green-600">{{ stats.completed_interviews ?? 0 }}</span>
                </div>
                <div class="flex items-center justify-between text-sm">
                  <span class="text-muted-foreground">待面试</span>
                  <span class="font-medium text-orange-600">{{ (stats.total_interviews ?? 0) - (stats.completed_interviews ?? 0) }}</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <!-- 热门部门 -->
        <Card class="mt-6 mb-6">
          <CardHeader>
            <CardTitle>部门报名统计</CardTitle>
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
                      :style="{ width: `${(dept.application_count / Math.max(...(stats.department_stats || []).map(d => d.application_count))) * 100}%` }"
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

        <!-- 热门岗位 -->
        <Card>
          <CardHeader>
            <CardTitle>热门岗位</CardTitle>
          </CardHeader>
          <CardContent>
            <div class="space-y-3">
              <div
                v-for="(position, index) in (stats.position_stats || []).slice(0, 5)"
                :key="position.position_name"
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
      </template>
    </div>
  </div>
</template>
