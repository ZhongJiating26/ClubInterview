<script setup lang="ts">
import type { LucideIcon } from "lucide-vue-next"
import { RouterLink } from 'vue-router'
import {
  SidebarGroup,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from '@/components/ui/sidebar'

defineProps<{
  title?: string
  items: {
    title: string
    url: string
    icon?: LucideIcon
  }[]
}>()
</script>

<template>
  <SidebarGroup>
    <SidebarGroupLabel v-if="title">{{ title }}</SidebarGroupLabel>
    <SidebarMenu>
      <SidebarMenuItem v-for="item in items" :key="item.title">
        <SidebarMenuButton as-child>
          <RouterLink :to="item.url" class="flex items-center gap-2">
            <component v-if="item.icon" :is="item.icon" class="size-4" />
            <span>{{ item.title }}</span>
          </RouterLink>
        </SidebarMenuButton>
      </SidebarMenuItem>
    </SidebarMenu>
  </SidebarGroup>
</template>
