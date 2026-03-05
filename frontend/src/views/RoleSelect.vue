<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { Button } from '@/components/ui/button'
import {
  Carousel,
  CarouselContent,
  CarouselItem,
} from '@/components/ui/carousel'
import { Card, CardContent } from '@/components/ui/card'

const router = useRouter()
const carouselRef = ref()

const roles = [
  { code: 'admin', name: '社团管理员', description: '管理社团招新、面试安排等' },
  { code: 'interviewer', name: '面试官', description: '参与面试评分、评审工作' },
  { code: 'student', name: '普通学生', description: '申请加入社团、参加面试' },
]

// 当前选中的角色索引
const currentIndex = ref(0)

// 获取当前选中的角色
const currentRole = computed(() => roles[currentIndex.value])

// 监听轮播切换事件
const onSelect = () => {
  if (carouselRef.value?.carouselApi) {
    const api = carouselRef.value.carouselApi
    const index = api.selectedScrollSnap()
    // 确保索引在有效范围内
    if (index >= 0 && index < roles.length) {
      currentIndex.value = index
    }
  }
}

onMounted(() => {
  setTimeout(onSelect, 200)
})

// 向前滚动
const scrollPrev = () => {
  if (carouselRef.value?.scrollPrev) {
    carouselRef.value.scrollPrev()
  }
  // 先更新索引，轮播事件会再次更新
  currentIndex.value = (currentIndex.value - 1 + roles.length) % roles.length
}

// 向后滚动
const scrollNext = () => {
  if (carouselRef.value?.scrollNext) {
    carouselRef.value.scrollNext()
  }
  currentIndex.value = (currentIndex.value + 1) % roles.length
}

const confirmRole = () => {
  const role = currentRole.value
  if (role) {
    router.push({ path: '/init', query: { role: role.code } })
  }
}
</script>

<template>
  <div class="min-h-screen w-full bg-white flex items-center justify-center p-6">
    <div class="w-full max-w-xs flex flex-col gap-6 relative">
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
          @init-api="onSelect"
          @select="onSelect"
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
