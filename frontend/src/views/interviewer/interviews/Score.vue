<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
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
  Mic, MicOff, Upload, FileAudio, User, Phone, Mail, Calendar, Clock, CheckCircle2, AlertCircle, Loader2
} from 'lucide-vue-next'
import {
  getCandidateDetail,
  getSessionScoreItems,
  startInterview,
  updateInterviewRecord,
  submitScore as submitInterviewScore,
  uploadInterviewRecording,
  type InterviewCandidate,
  type ScoreItem
} from '@/api/modules/interview'

const route = useRoute()
const router = useRouter()

// 文件上传的 ref
const fileInputRef = ref<HTMLInputElement | null>(null)

// 获取候选人ID
const candidateId = ref<number>(Number(route.params.candidateId) || Number(route.query.candidateId))

// 加载状态
const loading = ref(false)
const error = ref('')

// 候选人信息
const candidate = ref<InterviewCandidate & { application?: any } | null>(null)

// 面试记录ID
const interviewRecordId = ref<number | null>(null)

// 录音状态
const isRecording = ref(false)
const recordingTime = ref(0)
const recordingUrl = ref('')
const hasRecording = ref(false)

// 计时器
let timer: number | null = null

// 上传状态
const uploadedFile = ref<File | null>(null)
const uploadProgress = ref(0)
const uploading = ref(false)

// 评分项
const scoreItems = ref<ScoreItem[]>([])

// 评分
const scores = ref<Record<number, number>>({})

// 面试记录
const interviewNotes = ref('')

// 提交状态
const isSubmitting = ref(false)
const showSubmitDialog = ref(false)

// 计算总分
const totalScore = computed(() => {
  if (scoreItems.value.length === 0) return 0
  return scoreItems.value.reduce((sum, item) => {
    const score = scores.value[item.id] || 0
    return sum + (score * item.weight)
  }, 0)
})

// 获取候选人详情
const fetchCandidateDetail = async () => {
  try {
    loading.value = true
    error.value = ''
    const data = await getCandidateDetail(candidateId.value)
    candidate.value = data

    // 如果候选人已有面试记录，获取该记录的评分
    if (data.session_id) {
      await fetchScoreItems(data.session_id)
    }
  } catch (err: any) {
    error.value = err.message || '获取候选人信息失败'
  } finally {
    loading.value = false
  }
}

// 获取评分项
const fetchScoreItems = async (sessionId: number) => {
  try {
    const items = await getSessionScoreItems(sessionId)
    scoreItems.value = items
    // 初始化评分
    items.forEach(item => {
      if (!scores.value[item.id]) {
        scores.value[item.id] = 0
      }
    })
  } catch (err: any) {
    console.error('获取评分项失败:', err)
  }
}

// 开始面试
const handleStartInterview = async () => {
  try {
    const record = await startInterview(candidateId.value)
    interviewRecordId.value = record.id
  } catch (err: any) {
    console.error('开始面试失败:', err)
  }
}

// 开始录音
const startRecording = () => {
  isRecording.value = true
  recordingTime.value = 0
  timer = setInterval(() => {
    recordingTime.value++
  }, 1000) as unknown as number
}

// 停止录音
const stopRecording = () => {
  isRecording.value = false
  if (timer) {
    clearInterval(timer)
    timer = null
  }
  // 模拟录音完成
  hasRecording.value = true
  recordingUrl.value = 'mock-recording-url'
}

// 删除录音
const deleteRecording = () => {
  hasRecording.value = false
  recordingUrl.value = ''
  recordingTime.value = 0
}

// 触发文件选择
const triggerFileSelect = () => {
  fileInputRef.value?.click()
}

// 处理文件选择
const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files[0]) {
    uploadedFile.value = target.files[0]
    uploadProgress.value = 100
  }
}

// 删除上传文件
const deleteUploadedFile = () => {
  uploadedFile.value = null
  uploadProgress.value = 0
}

// 上传录音文件
const handleUploadRecording = async () => {
  if (!uploadedFile.value || !interviewRecordId.value) return

  try {
    uploading.value = true
    await uploadInterviewRecording(interviewRecordId.value, uploadedFile.value)
    hasRecording.value = true
    alert('录音上传成功')
  } catch (err: any) {
    alert('上传失败: ' + (err.message || '未知错误'))
  } finally {
    uploading.value = false
  }
}

// 打开提交确认对话框
const openSubmitDialog = () => {
  if (!validateScores()) {
    alert('请检查评分，分数必须在有效范围内')
    return
  }
  showSubmitDialog.value = true
}

// 提交评分
const handleSubmitScore = async () => {
  if (!interviewRecordId.value) {
    alert('请先开始面试')
    return
  }

  try {
    isSubmitting.value = true

    // 先保存面试记录
    await updateInterviewRecord(interviewRecordId.value, {
      notes: interviewNotes.value
    })

    // 提交评分
    const scoreData = {
      scores: Object.entries(scores.value).map(([scoreItemId, score]) => ({
        score_item_id: Number(scoreItemId),
        score,
        notes: ''
      })),
      notes: interviewNotes.value
    }

    await submitInterviewScore(interviewRecordId.value, scoreData)

    showSubmitDialog.value = false
    alert('评分提交成功')
    router.push({ name: 'InterviewerInterviewsRecords' })
  } catch (err: any) {
    alert('提交失败: ' + (err.message || '未知错误'))
  } finally {
    isSubmitting.value = false
  }
}

// 保存草稿
const saveDraft = async () => {
  if (!interviewRecordId.value) {
    alert('请先开始面试')
    return
  }

  try {
    await updateInterviewRecord(interviewRecordId.value, {
      notes: interviewNotes.value
    })
    alert('草稿已保存')
  } catch (err: any) {
    alert('保存失败: ' + (err.message || '未知错误'))
  }
}

// 返回列表
const goBack = () => {
  router.push({ name: 'InterviewerInterviewsFilter' })
}

// 格式化日期
const formatDate = () => {
  return new Date().toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 验证评分
const validateScores = () => {
  for (const item of scoreItems.value) {
    const score = scores.value[item.id] ?? 0
    if (score < 0 || score > item.max_score) {
      return false
    }
  }
  return true
}

// 格式化时间
const formatTime = (seconds: number) => {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

// 页面加载时获取数据
onMounted(() => {
  if (candidateId.value) {
    fetchCandidateDetail()
  }
})

onUnmounted(() => {
  if (timer) {
    clearInterval(timer)
  }
})
</script>

<template>
  <div class="absolute inset-0 flex flex-col">
    <!-- 加载状态 -->
    <div v-if="loading" class="flex-1 flex items-center justify-center bg-gray-50">
      <div class="text-center">
        <Loader2 class="w-8 h-8 animate-spin mx-auto mb-4 text-blue-600" />
        <p class="text-gray-600">加载中...</p>
      </div>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="error" class="flex-1 flex items-center justify-center bg-gray-50">
      <div class="text-center">
        <AlertCircle class="w-12 h-12 text-red-500 mx-auto mb-4" />
        <p class="text-red-600 mb-4">{{ error }}</p>
        <Button @click="router.back()">返回</Button>
      </div>
    </div>

    <!-- 主要内容 -->
    <div v-else-if="candidate" class="flex-1 flex flex-col min-h-0">
      <!-- 顶部导航栏 -->
      <div class="bg-white border-b border-gray-200 px-6 py-4 flex-shrink-0">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-4">
            <Button variant="ghost" size="sm" @click="router.back()">
              ← 返回
            </Button>
            <div>
              <h1 class="text-xl font-semibold text-gray-800">面试评分</h1>
              <p class="text-sm text-gray-500">{{ formatDate() }}</p>
            </div>
          </div>
          <div class="flex gap-2">
            <Button variant="outline" @click="saveDraft" :disabled="!interviewRecordId">
              保存草稿
            </Button>
            <Button @click="handleStartInterview" v-if="!interviewRecordId" class="bg-green-600 hover:bg-green-700">
              开始面试
            </Button>
            <Button class="bg-blue-600 hover:bg-blue-700" @click="openSubmitDialog" :disabled="!interviewRecordId || (!hasRecording && !uploadedFile)">
              提交评分
            </Button>
          </div>
        </div>
      </div>

      <!-- 主要内容 -->
      <div class="flex-1 min-h-0 overflow-y-auto p-6 bg-gray-50">
        <div class="max-w-6xl mx-auto">
          <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <!-- 左侧：候选人信息和录音 -->
            <div class="lg:col-span-2 space-y-6">
              <!-- 候选人信息卡片 -->
              <Card class="bg-white">
                <CardHeader>
                  <CardTitle class="text-lg flex items-center gap-2">
                    <User class="w-5 h-5 text-blue-600" />
                    候选人信息
                  </CardTitle>
                </CardHeader>
                <CardContent class="space-y-4">
                  <div class="grid grid-cols-2 gap-4">
                    <div>
                      <Label class="text-gray-600 text-sm">姓名</Label>
                      <p class="font-medium text-gray-800">{{ candidate.user_name }}</p>
                    </div>
                    <div>
                      <Label class="text-gray-600 text-sm">联系电话</Label>
                      <p class="font-medium text-gray-800 flex items-center gap-1">
                        <Phone class="w-4 h-4 text-gray-400" />
                        {{ candidate.user_phone || '-' }}
                      </p>
                    </div>
                    <div>
                      <Label class="text-gray-600 text-sm">应聘部门</Label>
                      <Badge variant="outline" class="bg-blue-50 text-blue-700 border-blue-200 mt-1">
                        {{ candidate.department_name || '-' }}
                      </Badge>
                    </div>
                    <div>
                      <Label class="text-gray-600 text-sm">应聘岗位</Label>
                      <Badge variant="outline" class="bg-purple-50 text-purple-700 border-purple-200 mt-1">
                        {{ candidate.position_name || '-' }}
                      </Badge>
                    </div>
                  </div>
                  <div v-if="candidate.application && candidate.application.self_intro">
                    <Label class="text-gray-600 text-sm">自我介绍</Label>
                    <p class="text-sm text-gray-600 bg-gray-50 p-3 rounded-md mt-1">
                      {{ candidate.application.self_intro }}
                    </p>
                  </div>
                </CardContent>
              </Card>

              <!-- 录音/上传区域 -->
              <Card class="bg-white">
              <CardHeader>
                <CardTitle class="text-lg flex items-center gap-2">
                  <FileAudio class="w-5 h-5 text-blue-600" />
                  面试录音
                </CardTitle>
              </CardHeader>
              <CardContent class="space-y-4">
                <!-- 录音控制 -->
                <div class="bg-gray-50 rounded-lg p-6">
                  <div class="flex items-center justify-center gap-4">
                    <!-- 录音时间显示 -->
                    <div class="text-center">
                      <div class="text-3xl font-mono font-bold text-gray-800">
                        {{ formatTime(recordingTime) }}
                      </div>
                      <div v-if="isRecording" class="text-sm text-red-600 mt-2 flex items-center justify-center gap-1">
                        <span class="w-2 h-2 bg-red-600 rounded-full animate-pulse"></span>
                        录音中...
                      </div>
                    </div>

                    <!-- 录音按钮 -->
                    <div class="flex gap-3">
                      <Button
                        v-if="!isRecording && !hasRecording"
                        size="lg"
                        @click="startRecording"
                        class="bg-red-600 hover:bg-red-700"
                      >
                        <Mic class="w-5 h-5 mr-2" />
                        开始录音
                      </Button>
                      <Button
                        v-if="isRecording"
                        size="lg"
                        variant="destructive"
                        @click="stopRecording"
                      >
                        <MicOff class="w-5 h-5 mr-2" />
                        停止录音
                      </Button>
                    </div>
                  </div>

                  <!-- 已有录音显示 -->
                  <div v-if="hasRecording" class="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
                    <div class="flex items-center justify-between">
                      <div class="flex items-center gap-2 text-green-700">
                        <CheckCircle2 class="w-5 h-5" />
                        <span class="font-medium">录音已保存</span>
                        <span class="text-sm text-green-600">({{ formatTime(recordingTime) }})</span>
                      </div>
                      <Button variant="ghost" size="sm" @click="deleteRecording" class="text-red-600 hover:text-red-700">
                        删除
                      </Button>
                    </div>
                  </div>
                </div>

                <!-- 分隔线 -->
                <div class="flex items-center gap-4">
                  <div class="flex-1 h-px bg-gray-200"></div>
                  <span class="text-sm text-gray-500">或</span>
                  <div class="flex-1 h-px bg-gray-200"></div>
                </div>

                <!-- 上传录音文件 -->
                <div class="border-2 border-dashed border-gray-300 rounded-lg p-6">
                  <div class="text-center">
                    <Upload class="w-12 h-12 text-gray-400 mx-auto mb-3" />
                    <p class="text-sm text-gray-600 mb-2">上传已有的录音文件</p>
                    <p class="text-xs text-gray-500 mb-4">支持 MP3、WAV、M4A 等音频格式</p>
                    <input
                      ref="fileInputRef"
                      type="file"
                      accept="audio/*"
                      @change="handleFileSelect"
                      class="hidden"
                    />
                    <Button
                      variant="outline"
                      size="sm"
                      @click="triggerFileSelect"
                      :disabled="uploading"
                    >
                      {{ uploading ? '上传中...' : '选择文件' }}
                    </Button>
                    <Button
                      v-if="uploadedFile && !hasRecording"
                      size="sm"
                      @click="handleUploadRecording"
                      :disabled="uploading"
                      class="bg-blue-600 hover:bg-blue-700"
                    >
                      <Loader2 v-if="uploading" class="w-4 h-4 mr-2 animate-spin" />
                      {{ uploading ? '上传中...' : '确认上传' }}
                    </Button>
                  </div>

                  <!-- 上传的文件显示 -->
                  <div v-if="uploadedFile" class="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                    <div class="flex items-center justify-between">
                      <div class="flex items-center gap-2">
                        <FileAudio class="w-5 h-5 text-blue-600" />
                        <div>
                          <p class="text-sm font-medium text-gray-800">{{ uploadedFile.name }}</p>
                          <p class="text-xs text-gray-500">{{ (uploadedFile.size / 1024 / 1024).toFixed(2) }} MB</p>
                        </div>
                      </div>
                      <Button variant="ghost" size="sm" @click="deleteUploadedFile" class="text-red-600 hover:text-red-700">
                        删除
                      </Button>
                    </div>
                  </div>
                </div>

                <!-- 提示信息 -->
                <div v-if="!hasRecording && !uploadedFile" class="flex items-start gap-2 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                  <AlertCircle class="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
                  <div class="text-sm text-yellow-800">
                    <p class="font-medium">请先录音或上传文件</p>
                    <p class="text-yellow-700 mt-1">完成面试录音后才能提交评分</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <!-- 面试记录 -->
            <Card class="bg-white">
              <CardHeader>
                <CardTitle class="text-lg">面试记录</CardTitle>
              </CardHeader>
              <CardContent>
                <Label class="text-gray-600 text-sm mb-2 block">记录面试过程中的重要信息</Label>
                <Textarea
                  v-model="interviewNotes"
                  placeholder="请输入面试记录、候选人表现、亮点、不足等..."
                  rows="6"
                  class="resize-none"
                />
              </CardContent>
            </Card>
          </div>

          <!-- 右侧：评分表 -->
          <div class="space-y-6">
            <!-- 评分卡片 -->
            <Card class="bg-white sticky top-0">
              <CardHeader>
                <CardTitle class="text-lg">评分表</CardTitle>
              </CardHeader>
              <CardContent class="space-y-4">
                <div v-if="scoreItems.length === 0" class="text-center text-gray-500 py-4">
                  暂无评分项
                </div>
                <div v-for="item in scoreItems" :key="item.id" class="space-y-2">
                  <div class="flex items-center justify-between">
                    <Label class="text-sm font-medium text-gray-700">{{ item.title }}</Label>
                    <span class="text-sm text-gray-500">满分 {{ item.max_score }}</span>
                  </div>
                  <div class="flex items-center gap-2">
                    <Input
                      v-model.number="scores[item.id]"
                      type="number"
                      :min="0"
                      :max="item.max_score"
                      class="flex-1"
                      placeholder="0"
                    />
                    <span class="text-sm text-gray-500">/ {{ item.max_score }}</span>
                  </div>
                  <p v-if="item.description" class="text-xs text-gray-500">{{ item.description }}</p>
                </div>

                <!-- 总分显示 -->
                <div class="border-t border-gray-200 pt-4 mt-4">
                  <div class="flex items-center justify-between">
                    <span class="text-base font-medium text-gray-700">总分</span>
                    <span class="text-2xl font-bold text-blue-600">{{ totalScore.toFixed(1) }}</span>
                  </div>
                  <p class="text-xs text-gray-500 mt-1">加权总分</p>
                </div>

                <!-- 评分说明 -->
                <div class="text-xs text-gray-500 bg-gray-50 p-3 rounded-md">
                  <p class="font-medium mb-1">评分说明：</p>
                  <ul class="space-y-1 list-disc list-inside">
                    <li>请根据候选人表现客观评分</li>
                    <li>评分范围为 0 到各项目满分</li>
                    <li>总分为加权计算结果</li>
                  </ul>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  </div>

    <!-- 提交确认对话框 -->
    <Dialog :open="showSubmitDialog" @update:open="showSubmitDialog = $event">
      <DialogContent>
        <DialogHeader>
          <DialogTitle>确认提交评分</DialogTitle>
          <DialogDescription>请确认评分信息无误后提交</DialogDescription>
        </DialogHeader>

        <div class="space-y-4 py-4">
          <div class="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span class="text-gray-600">候选人：</span>
              <span class="font-medium">{{ candidate?.user_name }}</span>
            </div>
            <div>
              <span class="text-gray-600">总分：</span>
              <span class="font-bold text-blue-600">{{ totalScore.toFixed(1) }}</span>
            </div>
          </div>

            <div class="border-t border-gray-200 pt-4">
              <p class="text-sm font-medium text-gray-700 mb-2">评分详情：</p>
              <div class="space-y-1 text-sm">
                <div v-for="item in scoreItems" :key="item.id" class="flex justify-between">
                  <span class="text-gray-600">{{ item.title }}</span>
                  <span class="font-medium">{{ scores[item.id] || 0 }} / {{ item.max_score }}</span>
                </div>
              </div>
            </div>

          <div v-if="interviewNotes" class="border-t border-gray-200 pt-4">
            <p class="text-sm font-medium text-gray-700 mb-1">面试记录：</p>
            <p class="text-sm text-gray-600 line-clamp-3">{{ interviewNotes }}</p>
          </div>

          <div class="flex items-start gap-2 p-3 bg-blue-50 border border-blue-200 rounded-lg">
            <AlertCircle class="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
            <p class="text-sm text-blue-800">提交后评分将锁定，如需修改请联系管理员</p>
          </div>
        </div>
 
        <DialogFooter>
          <Button variant="outline" @click="showSubmitDialog = false" :disabled="isSubmitting">
            取消
          </Button>
          <Button class="bg-blue-600 hover:bg-blue-700" @click="handleSubmitScore" :disabled="isSubmitting">
            <Loader2 v-if="isSubmitting" class="w-4 h-4 mr-2 animate-spin" />
            {{ isSubmitting ? '提交中...' : '确认提交' }}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  </div>
</template>
