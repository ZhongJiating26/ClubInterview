<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getClubDetail, type ClubDetailData } from '@/api/modules/clubs'
import { submitSignup } from '@/api/modules/application'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Checkbox } from '@/components/ui/checkbox'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { ArrowLeft, Building2 } from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()

const clubId = ref<number>(parseInt(route.params.id as string))
const detail = ref<ClubDetailData | null>(null)
const loading = ref(false)
const submitting = ref(false)
const error = ref('')
const success = ref('')

// 自我介绍
const selfIntro = ref('')

// 选中的岗位
const selectedPositions = ref<Set<number>>(new Set())

// 判断是否正在报名时间内
const isInRegistrationPeriod = (startTime: string, endTime: string) => {
  const now = new Date()
  const start = new Date(startTime)
  const end = new Date(endTime)
  return now >= start && now <= end
}

// 获取所有正在招新的岗位
const activeRecruitingPositions = computed(() => {
  if (!detail.value?.recruitment_sessions) return []
  const positions: any[] = []
  detail.value.recruitment_sessions.forEach(session => {
    if (isInRegistrationPeriod(session.start_time, session.end_time)) {
      session.positions.forEach((position: any) => {
        // 使用 position_id 作为真正的岗位ID，id 是关联表的ID
        positions.push({
          ...position,
          id: position.position_id, // 覆盖 id，使用真正的岗位ID
          session_id: session.id,
          session_name: session.name
        })
      })
    }
  })
  return positions
})

// 按部门分组
const positionsByDepartment = computed(() => {
  const grouped = new Map<string, any[]>()
  activeRecruitingPositions.value.forEach(position => {
    const deptName = position.department_name || '未分组'
    if (!grouped.has(deptName)) {
      grouped.set(deptName, [])
    }
    grouped.get(deptName)!.push(position)
  })
  return grouped
})

// 是否有正在招新的岗位
const hasActiveRecruitment = computed(() => activeRecruitingPositions.value.length > 0)

// 获取招新场次ID
const sessionId = computed(() => {
  if (activeRecruitingPositions.value.length > 0) {
    return activeRecruitingPositions.value[0].session_id
  }
  return null
})

// 获取社团详情
const fetchDetail = async () => {
  try {
    loading.value = true
    error.value = ''
    const result = await getClubDetail(clubId.value)
    detail.value = result

    // 如果没有正在招新的岗位，返回详情页
    if (!hasActiveRecruitment.value) {
      router.replace(`/student/club/${clubId.value}`)
    }
  } catch (err: any) {
    error.value = err.message || '获取社团详情失败'
  } finally {
    loading.value = false
  }
}

// 切换岗位选择
const togglePosition = (positionId: number) => {
  if (selectedPositions.value.has(positionId)) {
    selectedPositions.value.delete(positionId)
  } else {
    selectedPositions.value.add(positionId)
  }
}

// 检查岗位是否选中
const isSelected = (positionId: number) => {
  return selectedPositions.value.has(positionId)
}

// 返回详情页
const goBack = () => {
  router.push(`/student/club/${clubId.value}`)
}

// 提交报名
const handleSubmit = async () => {
  if (selectedPositions.value.size === 0) {
    error.value = '请至少选择一个岗位'
    setTimeout(() => {
      error.value = ''
    }, 3000)
    return
  }

  if (!sessionId.value) {
    error.value = '招新信息异常，请重新进入页面'
    return
  }

  try {
    submitting.value = true
    error.value = ''
    success.value = ''

    await submitSignup({
      recruitment_session_id: sessionId.value,
      position_ids: Array.from(selectedPositions.value),
      self_intro: selfIntro.value.trim() || undefined,
    })

    success.value = '报名成功！'
    setTimeout(() => {
      router.push('/student/home')
    }, 1500)
  } catch (err: any) {
    error.value = err.message || '报名失败，请稍后重试'
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  fetchDetail()
})
</script>

<template>
  <div class="min-h-screen flex flex-col" style="background-color: #F8F8F8">
    <!-- 自定义顶部导航栏 -->
    <div class="sticky top-0 z-30 bg-white border-b border-gray-100">
      <div class="flex items-center justify-between px-4 py-3">
        <Button variant="ghost" size="icon" class="h-8 w-8" @click="goBack">
          <ArrowLeft class="h-5 w-5" />
        </Button>
        <h1 class="text-base font-semibold">选择报名岗位</h1>
        <div class="h-8 w-8"></div>
      </div>
    </div>

    <!-- 错误提示 -->
    <div v-if="error" class="m-4 p-3 text-sm text-destructive bg-destructive/10 rounded-md">
      {{ error }}
    </div>

    <!-- 成功提示 -->
    <div v-if="success" class="m-4 p-3 text-sm text-green-600 bg-green-50 rounded-md">
      {{ success }}
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="text-center text-gray-400 py-12">
      加载中...
    </div>

    <!-- 内容区域 -->
    <div v-else-if="detail" class="flex-1 p-4 space-y-4 pb-32">
      <!-- 社团基本信息 -->
      <div class="flex items-center justify-between">
        <h2 class="text-xl font-bold">{{ detail.name }}</h2>
        <Badge class="bg-green-500 text-white text-xs">
          招新中
        </Badge>
      </div>

      <!-- 自我介绍 -->
      <div class="bg-white rounded-lg p-4">
        <Label for="self-intro" class="text-sm font-semibold mb-2 block">
          自我介绍 <span class="text-gray-400 font-normal">(选填)</span>
        </Label>
        <Textarea
          id="self-intro"
          v-model="selfIntro"
          placeholder="简单介绍一下自己，让社团更好地了解你..."
          rows="4"
          class="resize-none"
          :disabled="submitting"
        />
        <p class="text-xs text-gray-400 mt-1">建议 50-200 字</p>
      </div>

      <!-- 招新岗位列表 -->
      <div class="bg-white rounded-lg p-4">
        <template v-for="[deptName, positions], index in positionsByDepartment" :key="deptName">
          <!-- 部门分割线 -->
          <div v-if="index > 0" class="border-t border-gray-200 my-4"></div>

          <div>
            <!-- 部门标题 -->
            <h3 class="text-base font-semibold mb-3 flex items-center gap-2">
              <Building2 class="w-4 h-4 text-gray-600" />
              {{ deptName }}
            </h3>

            <!-- 该部门的岗位列表 -->
            <div class="space-y-3">
              <label
                v-for="position in positions"
                :key="position.id"
                class="flex items-center gap-3 p-3 border border-gray-200 rounded-lg cursor-pointer hover:bg-gray-50 transition-colors"
                :class="{ 'bg-gray-50 border-gray-900': isSelected(position.id) }"
              >
                <Checkbox
                  :model-value="isSelected(position.id)"
                  @update:model-value="() => togglePosition(position.id)"
                  class="flex-shrink-0"
                  :disabled="submitting"
                />
                <div class="flex-1 min-w-0">
                  <div class="flex items-center justify-between mb-1">
                    <span class="text-sm font-medium">{{ position.position_name }}</span>
                    <span class="text-xs text-gray-500">招 {{ position.recruit_quota }} 人</span>
                  </div>
                  <p v-if="position.position_description" class="text-xs text-gray-600 line-clamp-1">
                    {{ position.position_description }}
                  </p>
                </div>
              </label>
            </div>
          </div>
        </template>
      </div>

      <!-- 暂无招新的状态 -->
      <div v-if="!hasActiveRecruitment" class="bg-white rounded-lg p-4">
        <div class="text-center py-8">
          <div class="text-gray-400 mb-2">
            <Building2 class="w-12 h-12 mx-auto mb-2 opacity-50" />
          </div>
          <p class="text-gray-500">该社团暂无正在进行的招新</p>
          <p class="text-xs text-gray-400 mt-1">请关注后续招新信息</p>
        </div>
      </div>
    </div>

    <!-- 底部固定按钮 -->
    <div v-if="hasActiveRecruitment" class="fixed bottom-0 left-0 right-0 p-4 bg-white border-t border-gray-100">
      <div class="flex items-center justify-between mb-2">
        <span class="text-sm text-gray-600">已选择</span>
        <span class="text-sm font-semibold">{{ selectedPositions.size }} 个岗位</span>
      </div>
      <Button
        class="w-full bg-gray-900 hover:bg-gray-800 text-white"
        size="lg"
        :disabled="selectedPositions.size === 0 || submitting"
        @click="handleSubmit"
      >
        {{ submitting ? '提交中...' : '确认报名' }}
      </Button>
    </div>
  </div>
</template>

<style scoped>
.line-clamp-1 {
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
