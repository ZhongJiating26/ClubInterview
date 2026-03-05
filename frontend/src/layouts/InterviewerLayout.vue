<script setup lang="ts">
import { RouterView, useRoute } from 'vue-router'
import {
  Command,
  Building2,
  History,
  Calendar,
  List,
  ClipboardList,
  Filter,
} from 'lucide-vue-next'
import { useUserStore } from '@/stores/user'
import AppSidebar from '@/components/AppSidebar.vue'
import NavUser from '@/components/NavUser.vue'
import NavGroup from '@/components/NavGroup.vue'
import {
  SidebarInset,
  SidebarProvider,
} from '@/components/ui/sidebar'

const userStore = useUserStore()
const route = useRoute()

const data = {
  user: {
    name: userStore.userInfo?.name || '用户',
    email: userStore.userInfo?.phone || '',
    avatar: '',
  },
  navMain: [
    {
      title: '加入社团',
      url: '/interviewer/join',
      icon: Building2,
    },
  ],
  navApplications: [
    {
      title: '报名场次',
      url: '/interviewer/applications/sessions',
      icon: Calendar,
    },
    {
      title: '历史报名记录',
      url: '/interviewer/applications/history',
      icon: History,
    },
  ],
  navInterviews: [
    {
      title: '面试场次',
      url: '/interviewer/interviews/list',
      icon: List,
    },
    {
      title: '面试记录',
      url: '/interviewer/interviews/records',
      icon: ClipboardList,
    },
    {
      title: '面试筛选',
      url: '/interviewer/interviews/filter',
      icon: Filter,
    },
  ],
}
</script>

<template>
  <SidebarProvider class="h-screen">
    <AppSidebar variant="inset">
      <template #header>
        <div class="flex items-center gap-2 px-2">
          <div class="flex aspect-square size-8 items-center justify-center rounded-lg bg-sidebar-primary text-sidebar-primary-foreground">
            <Command class="size-4" />
          </div>
          <div class="grid flex-1 text-left text-sm leading-tight">
            <span class="truncate font-medium">社团面试系统</span>
            <span class="truncate text-xs">面试官端</span>
          </div>
        </div>
      </template>
      <template #content>
        <NavGroup :items="data.navMain" />
        <NavGroup title="报名管理" :items="data.navApplications" />
        <NavGroup title="面试管理" :items="data.navInterviews" />
      </template>
      <template #footer>
        <NavUser :user="data.user" />
      </template>
    </AppSidebar>

    <SidebarInset>
      <!-- 主内容区 -->
      <RouterView :key="route.fullPath" />
    </SidebarInset>
  </SidebarProvider>
</template>
