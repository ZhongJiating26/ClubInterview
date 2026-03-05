<script setup lang="ts">
import type { SidebarProps } from '@/components/ui/sidebar'

import { Command } from "lucide-vue-next"

import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from '@/components/ui/sidebar'

const props = withDefaults(defineProps<SidebarProps>(), {
  variant: "inset",
})
</script>

<template>
  <Sidebar v-bind="props">
    <SidebarHeader>
      <slot name="header">
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton size="lg" as-child>
              <a href="#">
                <div class="flex aspect-square size-8 items-center justify-center rounded-lg bg-sidebar-primary text-sidebar-primary-foreground">
                  <Command class="size-4" />
                </div>
                <div class="grid flex-1 text-left text-sm leading-tight">
                  <span class="truncate font-medium">Acme Inc</span>
                  <span class="truncate text-xs">Enterprise</span>
                </div>
              </a>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </slot>
    </SidebarHeader>

    <SidebarContent>
      <slot name="content">
        <!-- 默认内容：可以被覆盖 -->
      </slot>
    </SidebarContent>

    <SidebarFooter>
      <slot name="footer">
        <!-- 默认内容：可以被覆盖 -->
      </slot>
    </SidebarFooter>
  </Sidebar>
</template>
