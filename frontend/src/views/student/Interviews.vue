<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getMySignups, type SignupApplication } from '@/api/modules/application'
import { getMyInterviewRecords, type InterviewCandidate } from '@/api/modules/interview'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Calendar, MapPin, FileText, ArrowRight, User, Clock } from 'lucide-vue-next'

const router = useRouter()

// 报名记录
const signups = ref<SignupApplication[]>([])
const signupsLoading = ref(false)
const signupsError = ref('')

// 面试记录
const interviews = ref<InterviewCandidate[]>([])
const interviewsLoading = ref(false)
const interviewsError = ref('')

// 获取报名记录
const fetchSignups = async () => {
  try {
    signupsLoading.value = true
    signupsError.value = ''
    const res = await getMySignups()
    signups.value = res.items || res
  } catch (err: any) {
    signupsError.value = err.message || '获取报名记录失败'
  } finally {
    signupsLoading.value = false
  }
}

// 获取面试记录
const fetchInterviews = async () => {
  try {
    interviewsLoading.value = true
    interviewsError.value = ''
    interviews.value = await getMyInterviewRecords()
  } catch (err: any) {
    interviewsError.value = err.message || '获取面试记录失败'
  } finally {
    interviewsLoading.value = false
  }
}

// 跳转到报名详情
const goToSignupDetail = (signupId: number) => {
  router.push(`/student/interviews/signup/${signupId}`)
}

// 跳转到面试详情
const goToInterviewDetail = (candidateId: number) => {
  router.push(`/student/interviews/record/${candidateId}`)
}

// 获取报名状态文本
const getSignupStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    PENDING: '待审核',
    APPROVED: '已通过',
    REJECTED: '已拒绝'
  }
  return statusMap[status] || status
}

// 获取报名状态样式
const getSignupStatusVariant = (status: string): 'default' | 'secondary' | 'destructive' | 'outline' => {
  switch (status) {
    case 'APPROVED':
      return 'default'
    case 'REJECTED':
      return 'destructive'
    case 'PENDING':
      return 'outline'
    default:
      return 'outline'
  }
}

// 获取面试状态文本
const getInterviewStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    SCHEDULED: '已安排',
    CONFIRMED: '已确认',
    CANCELLED: '已取消',
    COMPLETED: '已完成',
    NO_SHOW: '未到场'
  }
  return statusMap[status] || status
}

// 获取面试状态样式
const getInterviewStatusVariant = (status: string): 'default' | 'secondary' | 'destructive' | 'outline' => {
  switch (status) {
    case 'CONFIRMED':
      return 'default'
    case 'COMPLETED':
      return 'default'
    case 'CANCELLED':
      return 'secondary'
    case 'NO_SHOW':
      return 'destructive'
    case 'SCHEDULED':
      return 'outline'
    default:
      return 'outline'
  }
}

// 格式化日期
const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 格式化日期（完整）
const formatFullDate = (dateStr: string) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

onMounted(() => {
  fetchSignups()
  fetchInterviews()
})
</script>

<template>
  <div class="bg-gray-50 pb-20">
    <!-- 切换标签 -->
    <Tabs default-value="signups" class="w-full">
      <TabsList class="w-full h-12 sticky top-[81px] z-10 bg-gray-50 border border-gray-200">
        <TabsTrigger value="signups">
          报名记录
        </TabsTrigger>
        <TabsTrigger value="interviews">
          面试记录
        </TabsTrigger>
      </TabsList>

        <!-- 报名记录内容 -->
        <TabsContent value="signups" class="mt-4 pb-4">
          <!-- 加载状态 -->
          <div v-if="signupsLoading" class="text-center py-12 text-muted-foreground">
            加载中...
          </div>

          <!-- 错误提示 -->
          <div v-else-if="signupsError" class="text-center py-12 text-red-500">
            {{ signupsError }}
          </div>

          <!-- 空状态 -->
          <div v-else-if="signups.length === 0" class="text-center py-12 text-muted-foreground">
            <FileText class="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p>暂无报名记录</p>
          </div>

          <!-- 报名记录列表 -->
          <div v-else class="space-y-4">
            <Card
              v-for="signup in signups"
              :key="signup.id"
              class="w-full hover:shadow-md transition-shadow cursor-pointer"
              @click="goToSignupDetail(signup.id)"
            >
              <CardHeader class="pb-3">
                <div class="flex items-start justify-between">
                  <CardTitle class="text-lg">{{ signup.session_name || '招新报名' }}</CardTitle>
                  <Badge :variant="getSignupStatusVariant(signup.status)">
                    {{ getSignupStatusText(signup.status) }}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent class="space-y-2">
                <div class="flex items-center gap-2 text-sm text-muted-foreground">
                  <Calendar class="w-4 h-4" />
                  <span>报名时间：{{ formatDate(signup.created_at) }}</span>
                </div>
                <div v-if="signup.items && signup.items.length > 0" class="flex items-center gap-2 text-sm text-muted-foreground">
                  <FileText class="w-4 h-4" />
                  <span>报名岗位：{{ signup.items.map(item => item.position_name || `岗位${item.position_id}`).join('、') }}</span>
                </div>
                <div v-if="signup.audit_time" class="flex items-center gap-2 text-sm text-muted-foreground">
                  <Clock class="w-4 h-4" />
                  <span>审核时间：{{ formatDate(signup.audit_time) }}</span>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <!-- 面试记录内容 -->
        <TabsContent value="interviews" class="mt-4 pb-4">
          <!-- 加载状态 -->
          <div v-if="interviewsLoading" class="text-center py-12 text-muted-foreground">
            加载中...
          </div>

          <!-- 错误提示 -->
          <div v-else-if="interviewsError" class="text-center py-12 text-red-500">
            {{ interviewsError }}
          </div>

          <!-- 空状态 -->
          <div v-else-if="interviews.length === 0" class="text-center py-12 text-muted-foreground">
            <Calendar class="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p>暂无面试记录</p>
          </div>

          <!-- 面试记录列表 -->
          <div v-else class="space-y-4">
            <Card
              v-for="interview in interviews"
              :key="interview.id"
              class="w-full hover:shadow-md transition-shadow cursor-pointer"
              @click="goToInterviewDetail(interview.id)"
            >
              <CardHeader class="pb-3">
                <div class="flex items-start justify-between">
                  <div class="flex-1">
                    <CardTitle class="text-lg mb-1">{{ interview.position_name || '面试' }}</CardTitle>
                    <p v-if="interview.department_name" class="text-sm text-muted-foreground">{{ interview.department_name }}</p>
                  </div>
                  <Badge :variant="getInterviewStatusVariant(interview.status)">
                    {{ getInterviewStatusText(interview.status) }}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent class="space-y-2">
                <div class="flex items-center gap-2 text-sm text-muted-foreground">
                  <Calendar class="w-4 h-4" />
                  <span>面试时间：{{ formatDate(interview.planned_start_time) }}</span>
                </div>
                <div class="flex items-center gap-2 text-sm text-muted-foreground">
                  <MapPin class="w-4 h-4" />
                  <span>地点：暂未安排</span>
                </div>
                <div v-if="interview.final_score !== null" class="flex items-center gap-2 text-sm">
                  <span class="font-medium">最终得分：</span>
                  <span class="text-lg font-bold text-primary">{{ interview.final_score }}</span>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
  </div>
</template>
