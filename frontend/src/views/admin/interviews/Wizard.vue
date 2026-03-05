<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import {
  createInterviewSession,
  updateInterviewSession,
  deleteInterviewSession,
  getInterviewSession,
  assignInterviewer,
  getAssignableInterviewers,
  type InterviewSession,
  type CreateInterviewSessionData,
  type AssignableInterviewer,
} from '@/api/modules/interview'
import { getRecruitmentSessions } from '@/api/modules/recruitment'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Stepper } from '@/components/ui/stepper'
import {
  ChevronLeft,
  ChevronRight,
  Calendar,
  Clock,
  MapPin,
  Users,
  FileText,
  ArrowLeft,
  Check,
  UserCheck,
  Trash2,
} from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const sessionId = computed(() => Number(route.query.id) || null)
const isEditing = computed(() => !!sessionId.value)

// 步骤定义
const steps = [
  { title: '选择招新场次', description: '选择要安排面试的招新场次' },
  { title: '场次信息', description: '填写面试场次基础信息' },
  { title: '分配面试官', description: '为场次分配面试官' },
  { title: '评分模板', description: '配置评分项' },
  { title: '发布', description: '确认并发布面试' },
]

const currentStep = ref(0)
const loading = ref(false)
const error = ref('')
const success = ref('')

// 获取社团 ID
const getClubId = () => {
  return userStore.userInfo?.roles.find((r) => r.code === 'CLUB_ADMIN')?.club_id
}

// 招新场次列表
const recruitmentSessions = ref<any[]>([])
const selectedRecruitmentSessionId = ref<number | null>(null)

// 表单数据
const formData = ref({
  name: '',
  description: '',
  start_time: '',
  end_time: '',
  place: '',
})

// 面试官列表
const interviewers = ref<AssignableInterviewer[]>([])
const selectedInterviewerIds = ref<number[]>([])
const interviewersLoading = ref(false)

// 评分模板
const useCustomTemplate = ref(false)
const selectedTemplateId = ref<number | null>(null)
const customScoreItems = ref<Array<{ title: string; description: string; max_score: number; weight: number }>>([
  { title: '专业能力', description: '考察专业知识和技能', max_score: 100, weight: 1 },
  { title: '沟通能力', description: '考察表达和沟通能力', max_score: 100, weight: 1 },
  { title: '团队协作', description: '考察团队合作意识', max_score: 100, weight: 1 },
])

// 新增评分项
const newScoreItem = ref({ title: '', description: '', max_score: 100, weight: 1 })

// 获取招新场次列表
const fetchRecruitmentSessions = async () => {
  const clubId = getClubId()
  if (!clubId) return

  try {
    const res = await getRecruitmentSessions({ club_id: clubId })
    recruitmentSessions.value = res.filter(s => s.status === 'PUBLISHED')
  } catch (err) {
  }
}

// 获取可分配的面试官列表
const fetchInterviewers = async () => {
  const clubId = getClubId()
  if (!clubId) return

  try {
    interviewersLoading.value = true
    const res = await getAssignableInterviewers(clubId)
    interviewers.value = res
  } catch (err: any) {
    error.value = err.message || '获取面试官列表失败'
  } finally {
    interviewersLoading.value = false
  }
}

// 获取场次详情（编辑模式）
const fetchSessionDetail = async () => {
  if (!sessionId.value) return

  try {
    loading.value = true
    const res = await getInterviewSession(sessionId.value)
    formData.value = {
      name: res.name || '',
      description: res.description || '',
      start_time: res.start_time ? formatDateTimeLocal(res.start_time) : '',
      end_time: res.end_time ? formatDateTimeLocal(res.end_time) : '',
      place: res.place || '',
    }
    selectedRecruitmentSessionId.value = res.recruitment_session_id || null
    // TODO: 加载面试官和评分项
  } catch (err: any) {
    error.value = err.message || '获取场次详情失败'
  } finally {
    loading.value = false
  }
}

// 格式化日期时间
const formatDateTimeLocal = (dateStr: string) => {
  if (!dateStr) return ''
  return dateStr.substring(0, 16)
}

// 格式化日期
const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

// 添加评分项
const addScoreItem = () => {
  if (!newScoreItem.value.title.trim()) {
    error.value = '请输入评分项标题'
    return
  }
  customScoreItems.value.push({ ...newScoreItem.value })
  newScoreItem.value = { title: '', description: '', max_score: 100, weight: 1 }
  error.value = ''
}

// 移除评分项
const removeScoreItem = (index: number) => {
  customScoreItems.value.splice(index, 1)
}

// 创建面试场次（通用函数）
const handleCreate = async (status: 'DRAFT' | 'OPEN' = 'OPEN') => {
  const clubId = getClubId()
  if (!clubId) {
    error.value = '未找到社团信息'
    return
  }

  // 验证必填项
  if (!selectedRecruitmentSessionId.value) {
    error.value = '请选择招新场次'
    return
  }
  if (!formData.value.name.trim()) {
    error.value = '请输入面试场次名称'
    return
  }
  if (!formData.value.start_time) {
    error.value = '请选择面试开始时间'
    return
  }
  if (!formData.value.end_time) {
    error.value = '请选择面试结束时间'
    return
  }
  if (!formData.value.place.trim()) {
    error.value = '请输入面试地点'
    return
  }

  const formatTime = (time: string) => time ? time + ':00' : ''

  const data: CreateInterviewSessionData = {
    recruitment_session_id: selectedRecruitmentSessionId.value,
    name: formData.value.name.trim(),
    start_time: formatTime(formData.value.start_time),
    end_time: formatTime(formData.value.end_time),
    place: formData.value.place.trim(),
    status: status, // 设置状态：DRAFT 或 OPEN
  }

  if (formData.value.description.trim()) {
    data.description = formData.value.description.trim()
  }

  try {
    loading.value = true
    error.value = ''

    const session = await createInterviewSession(clubId, data)

    // 分配面试官（循环调用，每次分配一个）
    if (selectedInterviewerIds.value.length > 0) {
      for (const interviewerId of selectedInterviewerIds.value) {
        await assignInterviewer(session.id, { interviewer_id: interviewerId })
      }
    }

    success.value = status === 'OPEN' ? '发布成功' : '草稿已保存'
    setTimeout(() => {
      router.push('/admin/interviews/list')
    }, 1500)
  } catch (err: any) {
    error.value = err.response?.data?.detail || err.message || '创建失败'
  } finally {
    loading.value = false
  }
}

// 更新面试场次
const handleUpdate = async () => {
  if (!sessionId.value) return

  const clubId = getClubId()
  if (!clubId) {
    error.value = '未找到社团信息'
    return
  }

  // 验证必填项
  if (!formData.value.name.trim()) {
    error.value = '请输入面试场次名称'
    return
  }
  if (!formData.value.start_time) {
    error.value = '请选择面试开始时间'
    return
  }
  if (!formData.value.end_time) {
    error.value = '请选择面试结束时间'
    return
  }
  if (!formData.value.place.trim()) {
    error.value = '请输入面试地点'
    return
  }

  const formatTime = (time: string) => time ? time + ':00' : ''

  const data: any = {
    name: formData.value.name.trim(),
    start_time: formatTime(formData.value.start_time),
    end_time: formatTime(formData.value.end_time),
    place: formData.value.place.trim(),
  }

  if (formData.value.description.trim()) {
    data.description = formData.value.description.trim()
  }

  try {
    loading.value = true
    error.value = ''

    await updateInterviewSession(sessionId.value, data)
    success.value = '更新成功'
    setTimeout(() => {
      router.push('/admin/interviews/list')
    }, 1500)
  } catch (err: any) {
    error.value = err.response?.data?.detail || err.message || '更新失败'
  } finally {
    loading.value = false
  }
}

// 保存草稿
const handleSaveDraft = async () => {
  if (isEditing.value) {
    await handleUpdate()
  } else {
    await handleCreate('DRAFT')
  }
}

// 确认发布
const handlePublish = async () => {
  if (isEditing.value) {
    await handleUpdate()
  } else {
    await handleCreate('OPEN')
  }
}

// 返回
const handleGoBack = () => {
  router.push('/admin/interviews/list')
}

// 删除场次
const handleDelete = async () => {
  if (!sessionId.value) return
  if (!confirm('确定要删除这个面试场次吗？删除后无法恢复。')) return

  try {
    loading.value = true
    error.value = ''
    await deleteInterviewSession(sessionId.value)
    success.value = '删除成功'
    setTimeout(() => {
      router.push('/admin/interviews/list')
    }, 1000)
  } catch (err: any) {
    error.value = err.response?.data?.detail || err.message || '删除失败'
  } finally {
    loading.value = false
  }
}

// 获取选中的招新场次信息
const selectedRecruitmentSession = computed(() => {
  if (!selectedRecruitmentSessionId.value) return null
  return recruitmentSessions.value.find(s => s.id === selectedRecruitmentSessionId.value)
})

// 步骤标题
const wizardTitle = computed(() => {
  if (isEditing.value) {
    return '编辑面试场次'
  }
  return '新建面试场次'
})

onMounted(async () => {
  await fetchRecruitmentSessions()
  await fetchInterviewers()

  if (isEditing.value) {
    await fetchSessionDetail()
  }
})
</script>

<template>
  <div class="absolute inset-0 flex flex-col">
    <!-- 固定部分：返回按钮、标题、提示 -->
    <div class="flex-shrink-0 px-6 pt-6 pb-4">
      <!-- 返回按钮和标题 -->
      <div class="flex items-center gap-4 mb-4">
        <Button variant="ghost" size="icon" @click="handleGoBack">
          <ArrowLeft class="w-4 h-4" />
        </Button>
        <div>
          <h1 class="text-2xl font-bold">{{ wizardTitle }}</h1>
          <p class="text-sm text-muted-foreground">
            {{ isEditing ? '修改信息后点击保存' : '按步骤填写信息，创建面试场次' }}
          </p>
        </div>
      </div>

      <!-- 错误/成功提示 -->
      <div v-if="error" class="p-3 text-sm text-red-600 bg-red-50 rounded-md">
        {{ error }}
      </div>
      <div v-if="success" class="p-3 text-sm text-green-600 bg-green-50 rounded-md">
        {{ success }}
      </div>
    </div>

    <!-- 滚动部分：表单内容 -->
    <!-- 编辑模式：直接显示表单 -->
    <div v-if="isEditing" class="flex-1 min-h-0 overflow-y-auto px-6 pb-6">
      <div class="space-y-6">
        <!-- 选择招新场次 -->
        <Card>
          <CardHeader>
            <CardTitle>选择招新场次</CardTitle>
          </CardHeader>
          <CardContent class="space-y-4">
            <div class="space-y-2">
              <Label>招新场次</Label>
              <div class="p-3 bg-muted rounded-lg">
                {{ selectedRecruitmentSession?.name || '未选择' }}
              </div>
              <p class="text-sm text-muted-foreground">
                编辑模式下不可更改招新场次
              </p>
            </div>

            <!-- 选中的招新场次信息 -->
            <div v-if="selectedRecruitmentSession" class="bg-muted rounded-lg p-4 space-y-2">
              <div class="flex items-center gap-2">
                <FileText class="w-4 h-4 text-muted-foreground" />
                <span class="font-medium">{{ selectedRecruitmentSession.name }}</span>
              </div>
              <div class="flex items-center gap-2 text-sm text-muted-foreground">
                <Calendar class="w-4 h-4" />
                <span>{{ formatDate(selectedRecruitmentSession.start_time) }} - {{ formatDate(selectedRecruitmentSession.end_time) }}</span>
              </div>
              <div v-if="selectedRecruitmentSession.description" class="text-sm text-muted-foreground">
                {{ selectedRecruitmentSession.description }}
              </div>
            </div>
          </CardContent>
        </Card>

        <!-- 场次信息 -->
        <Card>
          <CardHeader>
            <CardTitle>场次信息</CardTitle>
          </CardHeader>
          <CardContent class="space-y-4">
            <div class="space-y-2">
              <Label for="name">面试场次名称 *</Label>
              <Input
                id="name"
                v-model="formData.name"
                placeholder="例如：第一轮面试"
              />
            </div>

            <div class="space-y-2">
              <Label for="description">场次说明</Label>
              <Textarea
                id="description"
                v-model="formData.description"
                placeholder="请输入场次说明（选填）"
                rows="3"
              />
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div class="space-y-2">
                <Label for="start_time">面试开始时间 *</Label>
                <Input
                  id="start_time"
                  type="datetime-local"
                  v-model="formData.start_time"
                />
              </div>
              <div class="space-y-2">
                <Label for="end_time">面试结束时间 *</Label>
                <Input
                  id="end_time"
                  type="datetime-local"
                  v-model="formData.end_time"
                />
              </div>
            </div>

            <div class="space-y-2">
              <Label for="place">面试地点 *</Label>
              <Input
                id="place"
                v-model="formData.place"
                placeholder="例如：学生活动中心201"
              />
            </div>
          </CardContent>
        </Card>

        <!-- 分配面试官 -->
        <Card>
          <CardHeader>
            <CardTitle>分配面试官</CardTitle>
          </CardHeader>
          <CardContent class="space-y-4">
            <div class="space-y-2">
              <Label>选择面试官</Label>
              <p class="text-sm text-muted-foreground">
                选择负责本场次面试的面试官，可以选择多名
              </p>
            </div>

            <!-- 面试官列表 -->
            <div v-if="interviewersLoading" class="text-center py-8 text-muted-foreground">
              加载中...
            </div>
            <div v-else-if="interviewers.length > 0" class="space-y-2">
              <div
                v-for="interviewer in interviewers"
                :key="interviewer.id"
                class="flex items-center justify-between p-3 border rounded-lg hover:bg-muted/50 cursor-pointer"
                :class="{ 'bg-primary/10 border-primary': selectedInterviewerIds.includes(interviewer.id) }"
                @click="
                  selectedInterviewerIds.includes(interviewer.id)
                    ? selectedInterviewerIds.splice(selectedInterviewerIds.indexOf(interviewer.id), 1)
                    : selectedInterviewerIds.push(interviewer.id)
                "
              >
                <div class="flex items-center gap-3">
                  <UserCheck class="w-5 h-5 text-muted-foreground" />
                  <div>
                    <div class="flex items-center gap-2">
                      <span class="font-medium">{{ interviewer.name }}</span>
                      <span class="text-xs px-2 py-0.5 rounded-full"
                        :class="interviewer.role === 'CLUB_ADMIN' ? 'bg-purple-100 text-purple-700' : 'bg-blue-100 text-blue-700'">
                        {{ interviewer.role === 'CLUB_ADMIN' ? '管理员' : '面试官' }}
                      </span>
                    </div>
                    <div class="text-sm text-muted-foreground">{{ interviewer.phone || '未设置手机号' }}</div>
                  </div>
                </div>
                <div class="w-5 h-5 rounded border flex items-center justify-center"
                  :class="selectedInterviewerIds.includes(interviewer.id) ? 'bg-primary border-primary' : 'border-muted-foreground'"
                >
                  <Check v-if="selectedInterviewerIds.includes(interviewer.id)" class="w-3 h-3 text-primary-foreground" />
                </div>
              </div>
            </div>
            <div v-else class="text-center py-8 text-muted-foreground">
              暂无可分配的面试官
            </div>

            <!-- 已选择的面试官 -->
            <div v-if="selectedInterviewerIds.length > 0" class="bg-muted rounded-lg p-3">
              <div class="text-sm font-medium mb-2">已选择 {{ selectedInterviewerIds.length }} 名面试官</div>
              <div class="flex flex-wrap gap-2">
                <span
                  v-for="id in selectedInterviewerIds"
                  :key="id"
                  class="px-2 py-1 bg-white rounded text-sm"
                >
                  {{ interviewers.find(i => i.id === id)?.name }}
                </span>
              </div>
            </div>
          </CardContent>
        </Card>

        <!-- 评分模板 -->
        <Card>
          <CardHeader>
            <CardTitle>评分模板</CardTitle>
          </CardHeader>
          <CardContent class="space-y-4">
            <div class="space-y-2">
              <Label>评分项配置 *</Label>
              <p class="text-sm text-muted-foreground">
                配置面试时的评分项，每项包含标题、描述、满分和权重
              </p>
            </div>

            <div class="space-y-3">
              <div
                v-for="(item, index) in customScoreItems"
                :key="index"
                class="p-3 border rounded-lg space-y-2"
              >
                <div class="flex items-start justify-between gap-2">
                  <div class="flex-1 space-y-2">
                    <div class="flex gap-2">
                      <Input
                        :model-value="item.title"
                        @update:model-value="customScoreItems[index].title = $event"
                        placeholder="评分项标题"
                        class="flex-1"
                      />
                      <Input
                        type="number"
                        :model-value="item.max_score"
                        @update:model-value="customScoreItems[index].max_score = Number($event)"
                        placeholder="满分"
                        class="w-20"
                        min="1"
                      />
                      <Input
                        type="number"
                        :model-value="item.weight"
                        @update:model-value="customScoreItems[index].weight = Number($event)"
                        placeholder="权重"
                        class="w-20"
                        min="1"
                      />
                    </div>
                    <Input
                      :model-value="item.description"
                      @update:model-value="customScoreItems[index].description = $event"
                      placeholder="评分项描述（选填）"
                    />
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    class="text-red-500 hover:text-red-600"
                    @click="removeScoreItem(index)"
                  >
                    <span class="text-lg">×</span>
                  </Button>
                </div>
              </div>
            </div>

            <div class="p-3 border rounded-lg border-dashed space-y-2">
              <div class="text-sm font-medium">添加评分项</div>
              <div class="flex gap-2">
                <Input
                  v-model="newScoreItem.title"
                  placeholder="评分项标题"
                  class="flex-1"
                />
                <Input
                  type="number"
                  v-model.number="newScoreItem.max_score"
                  placeholder="满分"
                  class="w-20"
                  min="1"
                />
                <Input
                  type="number"
                  v-model.number="newScoreItem.weight"
                  placeholder="权重"
                  class="w-20"
                  min="1"
                />
              </div>
              <Input
                v-model="newScoreItem.description"
                placeholder="评分项描述（选填）"
              />
              <Button
                variant="outline"
                size="sm"
                @click="addScoreItem"
                :disabled="!newScoreItem.title"
              >
                添加评分项
              </Button>
            </div>
          </CardContent>
        </Card>

        <!-- 操作按钮 -->
        <div class="flex justify-between">
          <Button
            variant="outline"
            class="text-red-600 hover:text-red-700 hover:bg-red-50"
            @click="handleDelete"
            :disabled="loading"
          >
            <Trash2 class="w-4 h-4 mr-1" />
            删除场次
          </Button>
          <div class="flex gap-2">
            <Button variant="outline" @click="handleGoBack">
              取消
            </Button>
            <Button @click="handlePublish" :disabled="loading">
              <Check class="w-4 h-4 mr-1" />
              {{ loading ? '保存中...' : '保存修改' }}
            </Button>
          </div>
        </div>
      </div>
    </div>

    <!-- 新建模式：使用步骤向导 -->
    <div v-else class="flex-1 min-h-0 overflow-y-auto px-6 pb-6">
      <!-- Stepper 进度条 -->
      <div class="mb-8">
        <Stepper v-model="currentStep" :steps="steps" />
      </div>

      <!-- Step 1: 选择招新场次 -->
      <Card v-if="currentStep === 0">
        <CardHeader>
          <CardTitle>选择招新场次</CardTitle>
        </CardHeader>
        <CardContent class="space-y-4">
          <div class="space-y-2">
            <Label for="recruitmentSession">招新场次 *</Label>
            <Select v-model="selectedRecruitmentSessionId" @update:model-value="error = ''">
              <SelectTrigger>
                <SelectValue placeholder="选择要安排面试的招新场次" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem
                  v-for="session in recruitmentSessions"
                  :key="session.id"
                  :value="session.id"
                >
                  {{ session.name }}
                </SelectItem>
              </SelectContent>
            </Select>
            <p class="text-sm text-muted-foreground">
              选择后，系统将自动从该招新场次中已通过审核的报名生成面试候选人
            </p>
          </div>

          <!-- 选中的招新场次信息 -->
          <div v-if="selectedRecruitmentSession" class="bg-muted rounded-lg p-4 space-y-2">
            <div class="flex items-center gap-2">
              <FileText class="w-4 h-4 text-muted-foreground" />
              <span class="font-medium">{{ selectedRecruitmentSession.name }}</span>
            </div>
            <div class="flex items-center gap-2 text-sm text-muted-foreground">
              <Calendar class="w-4 h-4" />
              <span>{{ formatDate(selectedRecruitmentSession.start_time) }} - {{ formatDate(selectedRecruitmentSession.end_time) }}</span>
            </div>
            <div v-if="selectedRecruitmentSession.description" class="text-sm text-muted-foreground">
              {{ selectedRecruitmentSession.description }}
            </div>
          </div>

          <div class="flex justify-end pt-4">
            <Button @click="currentStep++" :disabled="!selectedRecruitmentSessionId">
              下一步
              <ChevronRight class="w-4 h-4 ml-1" />
            </Button>
          </div>
        </CardContent>
      </Card>

      <!-- Step 2: 场次信息 -->
      <Card v-if="currentStep === 1">
        <CardHeader>
          <CardTitle>场次信息</CardTitle>
        </CardHeader>
        <CardContent class="space-y-4">
          <div class="space-y-2">
            <Label for="name">面试场次名称 *</Label>
            <Input
              id="name"
              v-model="formData.name"
              placeholder="例如：第一轮面试"
            />
          </div>

          <div class="space-y-2">
            <Label for="description">场次说明</Label>
            <Textarea
              id="description"
              v-model="formData.description"
              placeholder="请输入场次说明（选填）"
              rows="3"
            />
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div class="space-y-2">
              <Label for="start_time">面试开始时间 *</Label>
              <Input
                id="start_time"
                type="datetime-local"
                v-model="formData.start_time"
              />
            </div>
            <div class="space-y-2">
              <Label for="end_time">面试结束时间 *</Label>
              <Input
                id="end_time"
                type="datetime-local"
                v-model="formData.end_time"
              />
            </div>
          </div>

          <div class="space-y-2">
            <Label for="place">面试地点 *</Label>
            <Input
              id="place"
              v-model="formData.place"
              placeholder="例如：学生活动中心201"
            />
          </div>

          <div class="flex justify-between pt-4">
            <Button variant="outline" @click="currentStep--">
              <ChevronLeft class="w-4 h-4 mr-1" />
              上一步
            </Button>
            <Button
              @click="currentStep++"
              :disabled="!formData.name || !formData.start_time || !formData.end_time || !formData.place"
            >
              下一步
              <ChevronRight class="w-4 h-4 ml-1" />
            </Button>
          </div>
        </CardContent>
      </Card>

      <!-- Step 3: 分配面试官 -->
      <Card v-if="currentStep === 2">
        <CardHeader>
          <CardTitle>分配面试官</CardTitle>
        </CardHeader>
        <CardContent class="space-y-4">
          <div class="space-y-2">
            <Label>选择面试官</Label>
            <p class="text-sm text-muted-foreground">
              选择负责本场次面试的面试官，可以选择多名
            </p>
          </div>

          <!-- 面试官列表 -->
          <div v-if="interviewersLoading" class="text-center py-8 text-muted-foreground">
            加载中...
          </div>
          <div v-else-if="interviewers.length > 0" class="space-y-2">
            <div
              v-for="interviewer in interviewers"
              :key="interviewer.id"
              class="flex items-center justify-between p-3 border rounded-lg hover:bg-muted/50 cursor-pointer"
              :class="{ 'bg-primary/10 border-primary': selectedInterviewerIds.includes(interviewer.id) }"
              @click="
                selectedInterviewerIds.includes(interviewer.id)
                  ? selectedInterviewerIds.splice(selectedInterviewerIds.indexOf(interviewer.id), 1)
                  : selectedInterviewerIds.push(interviewer.id)
              "
            >
              <div class="flex items-center gap-3">
                <UserCheck class="w-5 h-5 text-muted-foreground" />
                <div>
                  <div class="flex items-center gap-2">
                    <span class="font-medium">{{ interviewer.name }}</span>
                    <span class="text-xs px-2 py-0.5 rounded-full"
                      :class="interviewer.role === 'CLUB_ADMIN' ? 'bg-purple-100 text-purple-700' : 'bg-blue-100 text-blue-700'">
                      {{ interviewer.role === 'CLUB_ADMIN' ? '管理员' : '面试官' }}
                    </span>
                  </div>
                  <div class="text-sm text-muted-foreground">{{ interviewer.phone || '未设置手机号' }}</div>
                </div>
              </div>
              <div class="w-5 h-5 rounded border flex items-center justify-center"
                :class="selectedInterviewerIds.includes(interviewer.id) ? 'bg-primary border-primary' : 'border-muted-foreground'"
              >
                <Check v-if="selectedInterviewerIds.includes(interviewer.id)" class="w-3 h-3 text-primary-foreground" />
              </div>
            </div>
          </div>
          <div v-else class="text-center py-8 text-muted-foreground">
            暂无可分配的面试官
          </div>

          <!-- 已选择的面试官 -->
          <div v-if="selectedInterviewerIds.length > 0" class="bg-muted rounded-lg p-3">
            <div class="text-sm font-medium mb-2">已选择 {{ selectedInterviewerIds.length }} 名面试官</div>
            <div class="flex flex-wrap gap-2">
              <span
                v-for="id in selectedInterviewerIds"
                :key="id"
                class="px-2 py-1 bg-white rounded text-sm"
              >
                {{ interviewers.find(i => i.id === id)?.name }}
              </span>
            </div>
          </div>

          <div class="flex justify-between pt-4">
            <Button variant="outline" @click="currentStep--">
              <ChevronLeft class="w-4 h-4 mr-1" />
              上一步
            </Button>
            <Button @click="currentStep++">
              下一步
              <ChevronRight class="w-4 h-4 ml-1" />
            </Button>
          </div>
        </CardContent>
      </Card>

      <!-- Step 4: 评分模板 -->
      <Card v-if="currentStep === 3">
        <CardHeader>
          <CardTitle>评分模板</CardTitle>
        </CardHeader>
        <CardContent class="space-y-4">
          <div class="space-y-4">
            <div class="space-y-2">
              <Label>评分项配置 *</Label>
              <p class="text-sm text-muted-foreground">
                配置面试时的评分项，每项包含标题、描述、满分和权重
              </p>
            </div>

            <div class="space-y-3">
              <div
                v-for="(item, index) in customScoreItems"
                :key="index"
                class="p-3 border rounded-lg space-y-2"
              >
                <div class="flex items-start justify-between gap-2">
                  <div class="flex-1 space-y-2">
                    <div class="flex gap-2">
                      <Input
                        :model-value="item.title"
                        @update:model-value="customScoreItems[index].title = $event"
                        placeholder="评分项标题"
                        class="flex-1"
                      />
                      <Input
                        type="number"
                        :model-value="item.max_score"
                        @update:model-value="customScoreItems[index].max_score = Number($event)"
                        placeholder="满分"
                        class="w-20"
                        min="1"
                      />
                      <Input
                        type="number"
                        :model-value="item.weight"
                        @update:model-value="customScoreItems[index].weight = Number($event)"
                        placeholder="权重"
                        class="w-20"
                        min="1"
                      />
                    </div>
                    <Input
                      :model-value="item.description"
                      @update:model-value="customScoreItems[index].description = $event"
                      placeholder="评分项描述（选填）"
                    />
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    class="text-red-500 hover:text-red-600"
                    @click="removeScoreItem(index)"
                  >
                    <span class="text-lg">×</span>
                  </Button>
                </div>
              </div>
            </div>

            <div class="p-3 border rounded-lg border-dashed space-y-2">
              <div class="text-sm font-medium">添加评分项</div>
              <div class="flex gap-2">
                <Input
                  v-model="newScoreItem.title"
                  placeholder="评分项标题"
                  class="flex-1"
                />
                <Input
                  type="number"
                  v-model.number="newScoreItem.max_score"
                  placeholder="满分"
                  class="w-20"
                  min="1"
                />
                <Input
                  type="number"
                  v-model.number="newScoreItem.weight"
                  placeholder="权重"
                  class="w-20"
                  min="1"
                />
              </div>
              <Input
                v-model="newScoreItem.description"
                placeholder="评分项描述（选填）"
              />
              <Button
                variant="outline"
                size="sm"
                @click="addScoreItem"
                :disabled="!newScoreItem.title"
              >
                添加评分项
              </Button>
            </div>
          </div>

          <div class="flex justify-between pt-4">
            <Button variant="outline" @click="currentStep--">
              <ChevronLeft class="w-4 h-4 mr-1" />
              上一步
            </Button>
            <Button @click="currentStep++">
              下一步
              <ChevronRight class="w-4 h-4 ml-1" />
            </Button>
          </div>
        </CardContent>
      </Card>

      <!-- Step 5: 确认发布 -->
      <Card v-if="currentStep === 4">
        <CardHeader>
          <CardTitle>确认发布</CardTitle>
        </CardHeader>
        <CardContent class="space-y-6">
          <div class="bg-muted rounded-lg p-4 space-y-4">
            <div class="flex items-center gap-2">
              <FileText class="w-4 h-4 text-muted-foreground" />
              <span class="font-medium">{{ formData.name || '未填写' }}</span>
            </div>

            <div class="flex items-center gap-2 text-sm text-muted-foreground">
              <Calendar class="w-4 h-4" />
              <Clock class="w-4 h-4 ml-1" />
              <span>
                {{ formatDate(formData.start_time) }} - {{ formatDate(formData.end_time) }}
              </span>
            </div>

            <div class="flex items-center gap-2 text-sm text-muted-foreground">
              <MapPin class="w-4 h-4" />
              <span>{{ formData.place || '未填写' }}</span>
            </div>

            <div class="flex items-center gap-2 text-sm text-muted-foreground">
              <UserCheck class="w-4 h-4" />
              <span>面试官: {{ selectedInterviewerIds.length }} 人</span>
            </div>

            <div v-if="selectedRecruitmentSession" class="pt-2 border-t">
              <div class="text-sm font-medium mb-1">关联招新场次</div>
              <div class="text-sm text-muted-foreground">{{ selectedRecruitmentSession.name }}</div>
            </div>

            <div class="pt-2 border-t">
              <div class="text-sm font-medium mb-2">评分项 ({{ customScoreItems.length }})</div>
              <div class="space-y-1">
                <div
                  v-for="(item, index) in customScoreItems"
                  :key="index"
                  class="text-sm text-muted-foreground flex items-center gap-2"
                >
                  <span>{{ item.title }}</span>
                  <span class="text-xs bg-white px-1 rounded">满分{{ item.max_score }}</span>
                  <span class="text-xs bg-white px-1 rounded">权重{{ item.weight }}</span>
                </div>
              </div>
            </div>
          </div>

          <div class="flex justify-between pt-4">
            <Button variant="outline" @click="currentStep--">
              <ChevronLeft class="w-4 h-4 mr-1" />
              上一步
            </Button>
            <div class="flex gap-2">
              <Button variant="outline" @click="handleSaveDraft" :disabled="loading">
                {{ loading ? '保存中...' : '保存草稿' }}
              </Button>
              <Button @click="handlePublish" :disabled="loading">
                <Check class="w-4 h-4 mr-1" />
                {{ loading ? '发布中...' : '确认发布' }}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  </div>
</template>
