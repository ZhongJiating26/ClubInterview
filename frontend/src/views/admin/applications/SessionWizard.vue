<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import {
  createRecruitmentSession,
  getRecruitmentSession,
  updateRecruitmentSession,
  deleteRecruitmentSession,
  getRecruitmentSessions,
  addSessionPosition,
  getSessionPositions,
  updateSessionPosition,
  removeSessionPosition,
  type RecruitmentSession,
  type SessionPosition,
} from '@/api/modules/recruitment'
import { getPositions } from '@/api/modules/clubs'
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
  Plus,
  Trash2,
  Building2,
  Calendar,
  Users,
  FileText,
  ArrowLeft,
  Check,
} from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const sessionId = computed(() => Number(route.params.id) || null)
const isEditing = computed(() => !!sessionId.value)

// 步骤定义
const steps = [
  { title: '基础信息', description: '填写招新基本信息' },
  { title: '设置招新岗位', description: '设置本次招新的岗位及人数' },
  { title: '发布', description: '确认并发布招新' },
]

const currentStep = ref(0)
const loading = ref(false)
const error = ref('')
const success = ref('')

// 草稿相关
const draftKey = computed(() => `recruitment_draft_${userStore.userInfo?.id}_${sessionId.value || 'new'}`)
const draftSaving = ref(false)
let draftSaveTimer: ReturnType<typeof setTimeout> | null = null

// 表单数据
const formData = ref({
  name: '',
  description: '',
  start_time: '',
  end_time: '',
  max_candidates: 100,
})

// 岗位数据
const availablePositions = ref<any[]>([])
const sessionPositions = ref<SessionPosition[]>([])

// 新增岗位时的临时配额
const newPositionQuota = ref(1)

// 添加岗位处理
const onAddPosition = (val: string) => {
  if (val) {
    handleAddPosition(Number(val))
    newPositionQuota.value = 1
  }
}

// 获取社团 ID
const getClubId = () => {
  return userStore.userInfo?.roles.find((r) => r.code === 'CLUB_ADMIN')?.club_id
}

// ==================== 草稿功能 ====================

// 保存草稿
const saveDraft = async () => {
  try {
    draftSaving.value = true
    const draft = {
      formData: formData.value,
      sessionPositions: sessionPositions.value,
      step: currentStep.value,
      updatedAt: new Date().toISOString(),
    }
    localStorage.setItem(draftKey.value, JSON.stringify(draft))
  } catch (err) {
  } finally {
    draftSaving.value = false
  }
}

// 加载草稿
const loadDraft = () => {
  try {
    const saved = localStorage.getItem(draftKey.value)
    if (saved) {
      const draft = JSON.parse(saved)
      formData.value = draft.formData || formData.value
      sessionPositions.value = draft.sessionPositions || []
      currentStep.value = draft.step || 0
      return true
    }
  } catch (err) {
  }
  return false
}

// 清除草稿
const clearDraft = () => {
  localStorage.removeItem(draftKey.value)
}

// 自动保存定时器
const startAutoSave = () => {
  draftSaveTimer = setInterval(() => {
    saveDraft()
  }, 5000) // 每5秒自动保存
}

const stopAutoSave = () => {
  if (draftSaveTimer) {
    clearInterval(draftSaveTimer)
    draftSaveTimer = null
  }
}

// 监听表单变化自动保存
const onFormChange = () => {
  saveDraft()
}

// ==================== 数据获取 ====================

// 获取社团岗位列表
const fetchPositions = async () => {
  const clubId = getClubId()
  if (!clubId) return

  try {
    const res = await getPositions(clubId)
    availablePositions.value = res
  } catch (err) {
  }
}

// 获取场次关联的岗位
const fetchSessionPositions = async () => {
  if (!sessionId.value) return

  try {
    const res = await getSessionPositions(sessionId.value)
    sessionPositions.value = res
  } catch (err) {
  }
}

// 获取场次详情（编辑模式）
const fetchSessionDetail = async () => {
  if (!sessionId.value) return

  try {
    loading.value = true
    const res = await getRecruitmentSession(sessionId.value)
    formData.value = {
      name: res.name || '',
      description: res.description || '',
      start_time: res.start_time ? formatDateTimeLocal(res.start_time) : '',
      end_time: res.end_time ? formatDateTimeLocal(res.end_time) : '',
      max_candidates: res.max_candidates || 100,
    }
    await fetchSessionPositions()
  } catch (err: any) {
    error.value = err.message || '获取场次详情失败'
  } finally {
    loading.value = false
  }
}

// ==================== 业务操作 ====================

// 格式化日期时间（用于 datetime-local 输入）
const formatDateTimeLocal = (dateStr: string) => {
  if (!dateStr) return ''
  return dateStr.substring(0, 16)
}

// 格式化日期
const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

// 添加岗位
const handleAddPosition = async (positionId: number, quota?: number) => {
  const finalQuota = quota ?? newPositionQuota.value

  if (!sessionId.value) {
    // 新建模式：直接添加到本地
    const position = availablePositions.value.find(p => p.id === positionId)
    if (position) {
      sessionPositions.value.push({
        id: Date.now(), // 临时 ID
        session_id: 0,
        position_id: position.id,
        position_name: position.name,
        position_description: position.description,
        position_requirement: position.requirement,
        recruit_quota: finalQuota,
      })
    }
    return
  }

  // 编辑模式：调用 API
  try {
    error.value = ''
    await addSessionPosition(sessionId.value, {
      position_id: Number(positionId),
      recruit_quota: Number(finalQuota),
    })
    await fetchSessionPositions()
  } catch (err: any) {
    error.value = err.response?.data?.detail || err.message || '添加岗位失败'
  }
}

// 移除岗位
const handleRemovePosition = async (sessionPositionId: number, positionId: number) => {
  if (!sessionId.value) {
    // 新建模式：从本地移除（使用原始岗位ID查找）
    sessionPositions.value = sessionPositions.value.filter(p => p.position_id !== positionId)
    return
  }

  // 编辑模式：调用 API（使用关联记录ID）
  try {
    await removeSessionPosition(sessionId.value, sessionPositionId)
    await fetchSessionPositions()
  } catch (err: any) {
    error.value = err.message || '移除岗位失败'
  }
}

// 更新岗位配额
const handleUpdateQuota = async (sessionPositionId: number, positionId: number, newQuota: number) => {
  if (newQuota < 1) {
    error.value = '招聘人数不能小于1'
    return
  }

  if (!sessionId.value) {
    // 新建模式：直接修改本地数据（使用原始岗位ID查找）
    const position = sessionPositions.value.find(p => p.position_id === positionId)
    if (position) {
      position.recruit_quota = newQuota
    }
    return
  }

  // 编辑模式：调用 API（使用关联记录ID）
  try {
    error.value = ''
    await updateSessionPosition(sessionId.value, sessionPositionId, { recruit_quota: newQuota })
    await fetchSessionPositions()
  } catch (err: any) {
    error.value = err.response?.data?.detail || err.message || '更新配额失败'
  }
}

// 创建场次（通用函数）
const handleCreate = async (status: 'DRAFT' | 'PUBLISHED' = 'DRAFT') => {
  const clubId = getClubId()
  if (!clubId) {
    error.value = '未找到社团信息'
    return
  }

  // 验证必填项
  if (!formData.value.name.trim()) {
    error.value = '请输入招新名称'
    return
  }
  if (!formData.value.start_time) {
    error.value = '请选择报名开始时间'
    return
  }
  if (!formData.value.end_time) {
    error.value = '请选择报名截止时间'
    return
  }

  const formatTime = (time: string) => time ? time + ':00' : ''

  const data: any = {
    name: formData.value.name.trim(),
    start_time: formatTime(formData.value.start_time),
    end_time: formatTime(formData.value.end_time),
    status,
  }

  if (formData.value.description.trim()) {
    data.description = formData.value.description.trim()
  }
  if (formData.value.max_candidates > 0) {
    data.max_candidates = formData.value.max_candidates
  }

  try {
    loading.value = true
    error.value = ''

    // 创建场次
    const session = await createRecruitmentSession(clubId, data)

    // 添加岗位（如果有）
    for (const pos of sessionPositions.value) {
      await addSessionPosition(session.id, {
        position_id: pos.position_id,
        recruit_quota: pos.recruit_quota,
      })
    }

    success.value = status === 'PUBLISHED' ? '发布成功' : '草稿已保存'
    clearDraft()
    router.push('/admin/applications/create')
  } catch (err: any) {
    error.value = err.response?.data?.detail || err.message || '创建失败'
  } finally {
    loading.value = false
  }
}

// 保存草稿
const handleSaveDraft = async () => {
  await handleCreate('DRAFT')
}

// 发布新建场次
const handlePublishForNew = async () => {
  await handleCreate('PUBLISHED')
}

// 发布场次
const handlePublish = async () => {
  if (isEditing.value) {
    // 编辑模式：更新字段并发布
    const clubId = getClubId()
    if (!clubId) {
      error.value = '未找到社团信息'
      return
    }

    // 验证必填项
    if (!formData.value.name.trim()) {
      error.value = '请输入招新名称'
      return
    }
    if (!formData.value.start_time) {
      error.value = '请选择报名开始时间'
      return
    }
    if (!formData.value.end_time) {
      error.value = '请选择报名截止时间'
      return
    }

    const formatTime = (time: string) => time ? time + ':00' : ''

    const data: any = {
      name: formData.value.name.trim(),
      start_time: formatTime(formData.value.start_time),
      end_time: formatTime(formData.value.end_time),
      status: 'PUBLISHED',
    }

    if (formData.value.description.trim()) {
      data.description = formData.value.description.trim()
    }
    if (formData.value.max_candidates > 0) {
      data.max_candidates = formData.value.max_candidates
    }

    try {
      loading.value = true
      error.value = ''

      // 更新所有字段
      await updateRecruitmentSession(sessionId.value!, data)

      success.value = '已发布'
      clearDraft()
      router.push('/admin/applications/create')
    } catch (err: any) {
      error.value = err.message || '发布失败'
    } finally {
      loading.value = false
    }
  } else {
    // 新建模式：先创建再发布
    await handleCreate()
  }
}

// 返回（保存草稿）
const handleGoBack = () => {
  saveDraft() // 保存草稿
  router.push('/admin/applications/create')
}

// 删除招新场次
const handleDelete = async () => {
  if (!sessionId.value) return

  if (!confirm(`确定要删除招新场次"${formData.value.name}"吗？此操作不可恢复。`)) {
    return
  }

  try {
    loading.value = true
    error.value = ''
    await deleteRecruitmentSession(sessionId.value)
    clearDraft()
    router.push('/admin/applications/create')
  } catch (err: any) {
    error.value = err.message || '删除失败'
  } finally {
    loading.value = false
  }
}

// ==================== 生命周期 ====================

onMounted(async () => {
  await fetchPositions()

  // 新建模式：清除草稿，从空白表单开始
  // 编辑模式：直接加载服务器数据
  if (isEditing.value) {
    // 编辑模式清除旧草稿
    clearDraft()
    await fetchSessionDetail()
  } else {
    // 新建模式清除草稿
    clearDraft()
  }

  // 开始自动保存（仅用于意外关闭时恢复）
  startAutoSave()
})

onUnmounted(() => {
  stopAutoSave()
  saveDraft() // 离开前保存草稿
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
        <h1 class="text-2xl font-bold">
          {{ isEditing ? '编辑招新场次' : '新建招新场次' }}
        </h1>
        <p class="text-sm text-muted-foreground">
          {{ isEditing ? '修改信息后点击保存' : '填写信息后按步骤完成创建' }}
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
        <!-- 基础信息 -->
        <Card>
          <CardHeader>
            <CardTitle>基础信息</CardTitle>
          </CardHeader>
          <CardContent class="space-y-4">
            <div class="space-y-2">
              <Label for="name">招新名称 *</Label>
              <Input
                id="name"
                v-model="formData.name"
                placeholder="例如：2025秋季招新"
              />
            </div>

            <div class="space-y-2">
              <Label for="description">招新说明</Label>
              <Textarea
                id="description"
                v-model="formData.description"
                placeholder="请输入招新说明（选填）"
                rows="3"
              />
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div class="space-y-2">
                <Label for="start_time">报名开始时间 *</Label>
                <Input
                  id="start_time"
                  type="datetime-local"
                  v-model="formData.start_time"
                />
              </div>
              <div class="space-y-2">
                <Label for="end_time">报名截止时间 *</Label>
                <Input
                  id="end_time"
                  type="datetime-local"
                  v-model="formData.end_time"
                />
              </div>
            </div>

            <div class="space-y-2">
              <Label for="max_candidates">报名上限人数</Label>
              <Input
                id="max_candidates"
                type="number"
                v-model="formData.max_candidates"
                min="1"
              />
            </div>
          </CardContent>
        </Card>

        <!-- 设置招新岗位 -->
        <Card>
          <CardHeader>
            <CardTitle>设置招新岗位</CardTitle>
          </CardHeader>
          <CardContent class="space-y-4">
            <!-- 已选岗位列表 -->
            <div v-if="sessionPositions.length > 0" class="space-y-2">
              <Label>已选岗位</Label>
              <div class="space-y-2">
                <div
                  v-for="pos in sessionPositions"
                  :key="pos.id"
                  class="flex items-center justify-between p-3 bg-gray-50 rounded-lg gap-3"
                >
                  <div class="flex items-center gap-3 flex-1">
                    <Building2 class="w-4 h-4 text-muted-foreground" />
                    <div class="font-medium">{{ pos.position_name }}</div>
                  </div>
                  <div class="flex items-center gap-2">
                    <Label class="text-sm text-muted-foreground whitespace-nowrap">招聘人数:</Label>
                    <Input
                      type="number"
                      :model-value="pos.recruit_quota"
                      @update:model-value="(val) => handleUpdateQuota(pos.id, pos.position_id, Number(val))"
                      min="1"
                      class="w-20 h-8"
                    />
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    class="text-red-500 hover:text-red-600"
                    @click="handleRemovePosition(pos.id, pos.position_id)"
                  >
                    <Trash2 class="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </div>

            <!-- 添加岗位 -->
            <div class="space-y-2">
              <Label>添加岗位</Label>
              <div class="flex gap-2">
                <Select @update:model-value="onAddPosition">
                  <SelectTrigger class="flex-1">
                    <SelectValue placeholder="选择要添加的岗位" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem
                      v-for="position in availablePositions"
                      :key="position.id"
                      :value="position.id.toString()"
                      :disabled="sessionPositions.some(p => p.position_id === position.id)"
                    >
                      {{ position.name }}
                    </SelectItem>
                  </SelectContent>
                </Select>
                <Input
                  type="number"
                  v-model.number="newPositionQuota"
                  min="1"
                  class="w-24"
                  placeholder="人数"
                />
              </div>
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

      <!-- Step 1: 基础信息 -->
      <Card v-if="currentStep === 0">
        <CardHeader>
          <CardTitle>基础信息</CardTitle>
        </CardHeader>
        <CardContent class="space-y-4">
          <div class="space-y-2">
            <Label for="name">招新名称 *</Label>
            <Input
              id="name"
              v-model="formData.name"
              placeholder="例如：2025秋季招新"
              @input="onFormChange"
            />
          </div>

          <div class="space-y-2">
            <Label for="description">招新说明</Label>
            <Textarea
              id="description"
              v-model="formData.description"
              placeholder="请输入招新说明（选填）"
              rows="3"
              @input="onFormChange"
            />
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div class="space-y-2">
              <Label for="start_time">报名开始时间 *</Label>
              <Input
                id="start_time"
                type="datetime-local"
                v-model="formData.start_time"
                @input="onFormChange"
              />
            </div>
            <div class="space-y-2">
              <Label for="end_time">报名截止时间 *</Label>
              <Input
                id="end_time"
                type="datetime-local"
                v-model="formData.end_time"
                @input="onFormChange"
              />
            </div>
          </div>

          <div class="space-y-2">
            <Label for="max_candidates">报名上限人数</Label>
            <Input
              id="max_candidates"
              type="number"
              v-model="formData.max_candidates"
              min="1"
              @input="onFormChange"
            />
          </div>

          <div class="flex justify-end pt-4">
            <Button @click="currentStep++">
              下一步
              <ChevronRight class="w-4 h-4 ml-1" />
            </Button>
          </div>
        </CardContent>
      </Card>

      <!-- Step 2: 设置招新岗位 -->
      <Card v-if="currentStep === 1">
        <CardHeader>
          <CardTitle>设置招新岗位</CardTitle>
        </CardHeader>
        <CardContent class="space-y-4">
          <!-- 已选岗位列表 -->
          <div v-if="sessionPositions.length > 0" class="space-y-2">
            <Label>已选岗位</Label>
            <div class="space-y-2">
              <div
                v-for="pos in sessionPositions"
                :key="pos.id"
                class="flex items-center justify-between p-3 bg-gray-50 rounded-lg gap-3"
              >
                <div class="flex items-center gap-3 flex-1">
                  <Building2 class="w-4 h-4 text-muted-foreground" />
                  <div class="font-medium">{{ pos.position_name }}</div>
                </div>
                <div class="flex items-center gap-2">
                  <Label class="text-sm text-muted-foreground whitespace-nowrap">招聘人数:</Label>
                  <Input
                    type="number"
                    :model-value="pos.recruit_quota"
                    @update:model-value="(val) => handleUpdateQuota(pos.id, pos.position_id, Number(val))"
                    @blur="saveDraft"
                    min="1"
                    class="w-20 h-8"
                  />
                </div>
                <Button
                  variant="ghost"
                  size="icon"
                  class="text-red-500 hover:text-red-600"
                  @click="handleRemovePosition(pos.id, pos.position_id)"
                >
                  <Trash2 class="w-4 h-4" />
                </Button>
              </div>
            </div>
          </div>

          <!-- 添加岗位 -->
          <div class="space-y-2">
            <Label>添加岗位</Label>
            <div class="flex gap-2">
              <Select @update:model-value="onAddPosition">
                <SelectTrigger class="flex-1">
                  <SelectValue placeholder="选择要添加的岗位" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem
                    v-for="position in availablePositions"
                    :key="position.id"
                    :value="position.id.toString()"
                    :disabled="sessionPositions.some(p => p.position_id === position.id)"
                  >
                    {{ position.name }}
                  </SelectItem>
                </SelectContent>
              </Select>
              <Input
                type="number"
                v-model.number="newPositionQuota"
                min="1"
                class="w-24"
                placeholder="人数"
              />
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

      <!-- Step 3: 发布 -->
      <Card v-if="currentStep === 2">
        <CardHeader>
          <CardTitle>确认发布</CardTitle>
        </CardHeader>
        <CardContent class="space-y-6">
          <!-- 信息预览 -->
          <div class="bg-gray-50 rounded-lg p-4 space-y-4">
            <div class="flex items-center gap-2">
              <FileText class="w-4 h-4 text-muted-foreground" />
              <span class="font-medium">{{ formData.name || '未填写' }}</span>
            </div>

            <div class="flex items-center gap-2 text-sm text-muted-foreground">
              <Calendar class="w-4 h-4" />
              <span>
                {{ formatDate(formData.start_time) }} - {{ formatDate(formData.end_time) }}
              </span>
            </div>

            <div class="flex items-center gap-2 text-sm text-muted-foreground">
              <Users class="w-4 h-4" />
              <span>上限 {{ formData.max_candidates }} 人</span>
            </div>

            <div v-if="sessionPositions.length > 0" class="pt-2 border-t">
              <div class="text-sm font-medium mb-2">招新岗位 ({{ sessionPositions.length }})</div>
              <div class="flex flex-wrap gap-2">
                <span
                  v-for="pos in sessionPositions"
                  :key="pos.id"
                  class="px-2 py-1 bg-white rounded text-sm"
                >
                  {{ pos.position_name }} ({{ pos.recruit_quota }})
                </span>
              </div>
            </div>
          </div>

          <!-- 操作按钮 -->
          <div class="flex justify-between pt-4">
            <Button variant="outline" @click="currentStep--">
              <ChevronLeft class="w-4 h-4 mr-1" />
              上一步
            </Button>
            <div class="flex gap-2">
              <Button variant="outline" @click="handleSaveDraft" :disabled="loading">
                {{ loading ? '保存中...' : '保存草稿' }}
              </Button>
              <Button @click="handlePublishForNew" :disabled="loading">
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
