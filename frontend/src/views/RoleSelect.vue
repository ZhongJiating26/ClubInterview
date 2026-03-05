<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { Button } from '@/components/ui/button'
import { Loader2 } from 'lucide-vue-next'
import {
  Carousel,
  CarouselContent,
  CarouselItem,
} from '@/components/ui/carousel'
import { Card, CardContent } from '@/components/ui/card'
import { getSystemRoles, type SystemRole } from '@/api/modules/system'

const router = useRouter()
const carouselRef = ref()

// 角色列表（从 API 获取）
const roles = ref<SystemRole[]>([])
const loading = ref(false)
const error = ref('')

// 当前选中的角色索引
const currentIndex = ref(0)

// 获取当前选中的角色
const currentRole = computed(() => roles.value[currentIndex.value])

// 监听轮播切换事件
const onSelect = () => {
  if (carouselRef.value?.carouselApi) {
    const api = carouselRef.value.carouselApi
    const index = api.selectedScrollSnap()
    // 确保索引在有效范围内
    if (index >= 0 && roles.value.length > 0) {
      currentIndex.value = index % roles.value.length
    }
  }
}

// 监听轮播初始化
const onInitApi = (api: any) => {
  // 监听 Embla 的 select 事件
  api.on('select', () => {
    onSelect()
  })
  // 初始化选择
  onSelect()
}

// 获取角色列表
const fetchRoles = async () => {
  try {
    loading.value = true
    error.value = ''
    const data = await getSystemRoles()
    // 过滤掉系统管理员（admin），不显示给用户注册
    roles.value = data.filter(r => r.code !== 'admin')
  } catch (err: any) {
    console.error('获取角色列表失败:', err)
    // 如果 API 调用失败，使用默认角色列表（不包含系统管理员）
    roles.value = [
      { code: 'student', name: '普通学生', description: '申请加入社团、参加面试', sort_order: 1 },
      { code: 'interviewer', name: '面试官', description: '参与面试评分、评审工作', sort_order: 2 },
      { code: 'club_admin', name: '社团管理员', description: '管理社团招新、面试安排等', sort_order: 3 },
    ]
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await fetchRoles()
  // 数据加载完成后，等待 DOM 更新后再设置选择
  setTimeout(() => {
    if (carouselRef.value?.carouselApi) {
      carouselRef.value.carouselApi.on('select', () => {
        onSelect()
      })
    }
  }, 300)
})

// 向前滚动
const scrollPrev = () => {
  if (carouselRef.value?.scrollPrev) {
    carouselRef.value.scrollPrev()
  }
  // 先更新索引，轮播事件会再次更新
  currentIndex.value = (currentIndex.value - 1 + roles.value.length) % roles.value.length
}

// 向后滚动
const scrollNext = () => {
  if (carouselRef.value?.scrollNext) {
    carouselRef.value.scrollNext()
  }
  currentIndex.value = (currentIndex.value + 1) % roles.value.length
}

const confirmRole = () => {
  const role = currentRole.value
  if (role) {
    // 直接使用后端返回的角色代码（可能是 admin 或 club_admin）
    router.push({ path: '/init', query: { role: role.code } })
  }
}
</script>

<template>
  <div class="min-h-screen w-full bg-white flex items-center justify-center p-6">
    <!-- 加载状态 -->
    <div v-if="loading" class="flex items-center justify-center">
      <Loader2 class="w-8 h-8 animate-spin text-primary" />
    </div>

    <!-- 错误状态 -->
    <div v-else-if="error" class="text-center text-red-500">
      {{ error }}
    </div>

    <!-- 主内容 -->
    <div v-else class="w-full max-w-xs flex flex-col gap-6 relative">
      <!-- 标题 -->
      <div class="flex flex-col items-center gap-2 text-center">
        <h1 class="text-2xl font-bold">选择您的角色</h1>
        <p class="text-muted-foreground text-sm">左右滑动或点击按钮选择角色</p>
      </div>

      <!-- 角色选择轮播 -->
      <div class="relative">
        <!-- 左按钮 -->
        <Button
          variant="outline"
          size="icon"
          class="absolute -left-12 top-1/2 -translate-y-1/2 z-10 rounded-full shadow-md bg-white"
          @click="scrollPrev"
        >
          ←
        </Button>

        <Carousel
          ref="carouselRef"
          class="w-full"
          :opts="{ loop: true }"
          @init-api="onInitApi"
        >
          <CarouselContent>
            <CarouselItem v-for="role in roles" :key="role.code" class="basis-full">
              <div class="px-2">
                <Card class="w-full aspect-3/4 transition-all duration-200 border border-gray-200 my-4">
                  <CardContent class="flex flex-col items-center justify-center h-full p-4">
                    <h3 class="text-xl font-semibold mb-2">{{ role.name }}</h3>
                    <p class="text-xs text-muted-foreground text-center">
                      {{ role.description }}
                    </p>
                  </CardContent>
                </Card>
              </div>
            </CarouselItem>
          </CarouselContent>
        </Carousel>

        <!-- 右按钮 -->
        <Button
          variant="outline"
          size="icon"
          class="absolute -right-12 top-1/2 -translate-y-1/2 z-10 rounded-full shadow-md bg-white"
          @click="scrollNext"
        >
          →
        </Button>
      </div>

      <!-- 当前角色名称 -->
      <div class="text-center">
        <p class="text-base">
          <span class="text-muted-foreground">已选择：</span>
          <span class="font-medium text-primary">{{ currentRole?.name || '' }}</span>
        </p>
      </div>

      <!-- 确认按钮 -->
      <div class="flex justify-center">
        <Button @click="confirmRole">
          确认选择
        </Button>
      </div>
    </div>
  </div>
</template>
