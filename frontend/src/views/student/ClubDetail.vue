<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getClubDetail, type ClubDetailData } from '@/api/modules/clubs'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { ArrowLeft, Building2, Briefcase } from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()

const clubId = ref<number>(parseInt(route.params.id as string))
const detail = ref<ClubDetailData | null>(null)
const loading = ref(false)
const error = ref('')

// 获取社团详情
const fetchDetail = async () => {
  try {
    loading.value = true
    error.value = ''
    const result = await getClubDetail(clubId.value)
    detail.value = result
  } catch (err: any) {
    error.value = err.message || '获取社团详情失败'
  } finally {
    loading.value = false
  }
}

// 返回首页
const goBack = () => {
  router.push('/student/home')
}

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
        positions.push({
          ...position,
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

// 点击报名
const handleApply = () => {
  router.push(`/student/apply/${clubId.value}`)
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
        <h1 class="text-base font-semibold">社团详情</h1>
        <div class="h-8 w-8"></div>
      </div>
    </div>

    <!-- 错误提示 -->
    <div v-if="error" class="m-4 p-3 text-sm text-red-600 bg-red-50 rounded-md">
      {{ error }}
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="text-center text-gray-400 py-12">
      加载中...
    </div>

    <!-- 内容区域 -->
    <div v-else-if="detail" class="flex-1 p-4 space-y-4 pb-24">
      <!-- 社团基本信息 -->
      <div class="flex gap-4">
        <!-- 社团 Logo -->
        <img
          :src="detail.logo_url || '/placeholder-logo.png'"
          :alt="detail.name"
          class="w-20 h-20 rounded-lg object-cover bg-gray-100 flex-shrink-0"
          @error="(e) => { (e.target as HTMLImageElement).src = '/placeholder-logo.png' }"
        />

        <!-- 社团信息 -->
        <div class="flex-1">
          <div class="flex items-center justify-between mb-1">
            <h2 class="text-xl font-bold">{{ detail.name }}</h2>
            <Badge v-if="hasActiveRecruitment" class="bg-green-500 text-white text-xs">
              招新中
            </Badge>
          </div>
          <Badge variant="outline" class="text-xs mb-1">
            {{ detail.category || '未分类' }}
          </Badge>
          <div class="text-xs text-gray-500">
            {{ detail.school_name }}
          </div>
        </div>
      </div>

      <!-- 社团简介 -->
      <div v-if="detail.description" class="text-sm text-gray-600">
        {{ detail.description }}
      </div>
      <div v-else class="text-sm text-gray-400 italic">
        暂无简介
      </div>

      <!-- 正在招新的岗位 - 统一在一个白底框内 -->
      <div v-if="hasActiveRecruitment" class="bg-white rounded-lg p-4">
        <template v-for="[deptName, positions], index in positionsByDepartment" :key="deptName">
          <!-- 部门分割线 -->
          <div v-if="index > 0" class="border-t border-gray-200 my-6"></div>

          <div>
            <!-- 部门标题 -->
            <h3 class="text-base font-semibold mb-3 flex items-center gap-2">
              <Building2 class="w-4 h-4 text-gray-600" />
              {{ deptName }}
            </h3>

          <!-- 该部门的岗位列表 -->
          <div class="space-y-4">
            <div
              v-for="position in positions"
              :key="position.id"
            >
              <div class="flex items-start justify-between mb-1">
                <h4 class="font-medium text-sm">{{ position.position_name }}</h4>
                <span class="text-sm font-semibold text-gray-700">
                  招 {{ position.recruit_quota }} 人
                </span>
              </div>
              <p v-if="position.position_description" class="text-xs text-gray-600 mt-1 mb-1 break-words">
                {{ position.position_description }}
              </p>
              <p v-if="position.position_requirement" class="text-xs text-gray-500 break-words">
                <span class="font-medium text-gray-700">任职要求：</span>{{ position.position_requirement }}
              </p>
            </div>
          </div>
          </div>
        </template>
      </div>

      <!-- 暂无招新的状态 -->
      <div v-else class="bg-white rounded-lg p-4">
        <div class="text-center py-8">
          <div class="text-gray-400 mb-2">
            <Briefcase class="w-12 h-12 mx-auto mb-2 opacity-50" />
          </div>
          <p class="text-gray-500">该社团暂无正在进行的招新</p>
          <p class="text-xs text-gray-400 mt-1">请关注后续招新信息</p>
        </div>
      </div>
    </div>

    <!-- 底部固定按钮 -->
    <div class="fixed bottom-0 left-0 right-0 p-4 bg-white border-t border-gray-100">
      <Button
        v-if="hasActiveRecruitment"
        class="w-full bg-gray-900 hover:bg-gray-800 text-white"
        size="lg"
        @click="handleApply"
      >
        立即报名
      </Button>
      <Button
        v-else
        variant="outline"
        class="w-full"
        size="lg"
        disabled
      >
        暂无招新
      </Button>
    </div>
  </div>
</template>
