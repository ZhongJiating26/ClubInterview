<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { getClubsBySchool, type ClubHomeInfo } from '@/api/modules/clubs'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

// 社团列表
const clubs = ref<ClubHomeInfo[]>([])
const loading = ref(false)
const error = ref('')

// 获取学校编码
const schoolCode = computed(() => userStore.userInfo?.school_code)

// 获取社团列表
const fetchClubs = async () => {
  if (!schoolCode.value) {
    error.value = '未找到学校信息'
    return
  }

  try {
    loading.value = true
    error.value = ''

    // 获取学校的社团列表
    const result = await getClubsBySchool({
      school_code: schoolCode.value
    })

    // 排序：先按是否招新排序（招新中在前），再按名称拼音排序
    clubs.value = result.sort((a, b) => {
      // 招新状态排序：招新中在前
      const aRecruiting = a.recruiting_status === 'RECRUITING' ? 0 : 1
      const bRecruiting = b.recruiting_status === 'RECRUITING' ? 0 : 1

      if (aRecruiting !== bRecruiting) {
        return aRecruiting - bRecruiting
      }

      // 名称拼音排序
      return a.name.localeCompare(b.name, 'zh-CN')
    })
  } catch (err: any) {
    error.value = err.message || '获取社团列表失败'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchClubs()
})

// 监听路由变化，返回首页时重新加载数据
watch(() => route.path, (newPath) => {
  if (newPath === '/student/home') {
    fetchClubs()
  }
})

// 点击社团卡片，跳转到详情页
const handleClubClick = (clubId: number) => {
  router.push(`/student/club/${clubId}`)
}
</script>

<template>
  <div class="pb-4">
    <!-- 错误提示 -->
    <div v-if="error" class="mb-4 p-3 text-sm text-red-600 bg-red-50 rounded-md">
      {{ error }}
    </div>

    <!-- 加载状态 -->
    <div v-if="loading && clubs.length === 0" class="text-center text-gray-400 py-12">
      加载中...
    </div>

    <!-- 空状态 -->
    <div v-else-if="!loading && clubs.length === 0" class="text-center text-gray-400 py-12">
      <p>暂无社团信息</p>
    </div>

    <!-- 社团列表 -->
    <div v-else class="grid grid-cols-1 gap-4">
      <Card
        v-for="club in clubs"
        :key="club.id"
        class="overflow-hidden !py-0 cursor-pointer shadow-none"
        @click="handleClubClick(club.id)"
      >
        <CardContent class="p-3">
          <div class="flex gap-3">
            <!-- 左边：社团信息 -->
            <div class="flex-1 min-w-0 pl-1">
              <h3 class="font-semibold text-base mb-1">{{ club.name }}</h3>
              <p v-if="club.description" class="text-sm text-gray-600 line-clamp-1">
                {{ club.description }}
              </p>
              <p v-else class="text-sm text-gray-400 italic">
                暂无简介
              </p>
            </div>

            <!-- 右边：Logo 和招新状态 -->
            <div class="flex flex-col items-center gap-2 flex-shrink-0">
              <!-- 社团 Logo -->
              <img
                :src="club.logo_url || '/placeholder-logo.png'"
                :alt="club.name"
                class="w-16 h-16 rounded-lg object-cover bg-gray-100"
                @error="(e) => { (e.target as HTMLImageElement).src = '/placeholder-logo.png' }"
              />

              <!-- 招新状态 -->
              <Badge
                :variant="club.recruiting_status === 'RECRUITING' ? 'default' : 'secondary'"
                :class="club.recruiting_status === 'RECRUITING' ? 'bg-green-500 hover:bg-green-600 text-white text-xs' : 'bg-gray-200 text-gray-600 text-xs'"
              >
                {{ club.recruiting_status === 'RECRUITING' ? '招新中' : '暂无招新' }}
              </Badge>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  </div>
</template>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
