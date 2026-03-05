<script setup lang="ts">
import { ref } from 'vue'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Switch } from '@/components/ui/switch'
import { Label } from '@/components/ui/label'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from '@/components/ui/tabs'
import { Bell, Shield, Users, Palette } from 'lucide-vue-next'

// 系统设置数据
const settings = ref({
  // 通知设置
  notifications: {
    email_enabled: true,
    sms_enabled: false,
    application_reminder: true,
    interview_reminder: true,
    result_reminder: true
  },
  // 面试设置
  interview: {
    auto_assign: false,
    max_interviewers_per_student: 3,
    interview_duration: 30,
    allow_self_schedule: false
  },
  // 审核设置
  review: {
    auto_approve_threshold: 85,
    require_interview: true,
    allow_multiple_departments: true,
    max_department_selections: 2
  },
  // 界面设置
  ui: {
    theme: 'light',
    language: 'zh-CN',
    date_format: 'YYYY-MM-DD',
    time_format: '24h'
  }
})

const saving = ref(false)

// 保存设置
const saveSettings = () => {
  saving.value = true
  setTimeout(() => {
    saving.value = false
    // 这里应该调用后端API保存设置
  }, 1000)
}

// 重置设置
const resetSettings = () => {
}
</script>

<template>
  <div class="absolute inset-0 flex flex-col">
    <div class="flex-1 min-h-0 overflow-y-auto p-6">
      <div class="mb-6">
        <h1 class="text-2xl font-bold mb-2">系统设置</h1>
        <p class="text-muted-foreground">配置系统参数和偏好设置</p>
      </div>

      <Tabs default-value="notifications" class="space-y-6">
        <TabsList class="w-full justify-start">
          <TabsTrigger value="notifications" class="gap-2">
            <Bell class="w-4 h-4" />
            通知设置
          </TabsTrigger>
          <TabsTrigger value="interview" class="gap-2">
            <Users class="w-4 h-4" />
            面试设置
          </TabsTrigger>
          <TabsTrigger value="review" class="gap-2">
            <Shield class="w-4 h-4" />
            审核设置
          </TabsTrigger>
          <TabsTrigger value="ui" class="gap-2">
            <Palette class="w-4 h-4" />
            界面设置
          </TabsTrigger>
        </TabsList>

        <!-- 通知设置 -->
        <TabsContent value="notifications">
          <Card>
            <CardHeader>
              <CardTitle>通知配置</CardTitle>
            </CardHeader>
            <CardContent class="space-y-6">
              <!-- 邮件通知 -->
              <div class="flex items-center justify-between">
                <div class="space-y-0.5">
                  <Label for="email-enabled">启用邮件通知</Label>
                  <p class="text-sm text-muted-foreground">通过邮件发送系统通知和提醒</p>
                </div>
                <Switch
                  id="email-enabled"
                  v-model:checked="settings.notifications.email_enabled"
                />
              </div>

              <!-- 短信通知 -->
              <div class="flex items-center justify-between">
                <div class="space-y-0.5">
                  <Label for="sms-enabled">启用短信通知</Label>
                  <p class="text-sm text-muted-foreground">通过短信发送重要提醒（需要配置短信服务）</p>
                </div>
                <Switch
                  id="sms-enabled"
                  v-model:checked="settings.notifications.sms_enabled"
                />
              </div>

              <!-- 分隔线 -->
              <div class="border-t"></div>

              <!-- 报名提醒 -->
              <div class="flex items-center justify-between">
                <div class="space-y-0.5">
                  <Label for="application-reminder">报名提醒</Label>
                  <p class="text-sm text-muted-foreground">新学生报名时发送通知</p>
                </div>
                <Switch
                  id="application-reminder"
                  v-model:checked="settings.notifications.application_reminder"
                />
              </div>

              <!-- 面试提醒 -->
              <div class="flex items-center justify-between">
                <div class="space-y-0.5">
                  <Label for="interview-reminder">面试提醒</Label>
                  <p class="text-sm text-muted-foreground">面试前自动提醒学生和面试官</p>
                </div>
                <Switch
                  id="interview-reminder"
                  v-model:checked="settings.notifications.interview_reminder"
                />
              </div>

              <!-- 结果通知 -->
              <div class="flex items-center justify-between">
                <div class="space-y-0.5">
                  <Label for="result-reminder">结果通知</Label>
                  <p class="text-sm text-muted-foreground">审核/面试结果公布后发送通知</p>
                </div>
                <Switch
                  id="result-reminder"
                  v-model:checked="settings.notifications.result_reminder"
                />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <!-- 面试设置 -->
        <TabsContent value="interview">
          <Card>
            <CardHeader>
              <CardTitle>面试配置</CardTitle>
            </CardHeader>
            <CardContent class="space-y-6">
              <!-- 自动分配 -->
              <div class="flex items-center justify-between">
                <div class="space-y-0.5">
                  <Label for="auto-assign">自动分配面试官</Label>
                  <p class="text-sm text-muted-foreground">系统自动为通过审核的学生分配面试官</p>
                </div>
                <Switch
                  id="auto-assign"
                  v-model:checked="settings.interview.auto_assign"
                />
              </div>

              <!-- 每个学生的最大面试官数 -->
              <div class="space-y-2">
                <Label for="max-interviewers">每个学生的最大面试官数</Label>
                <Input
                  id="max-interviewers"
                  type="number"
                  v-model.number="settings.interview.max_interviewers_per_student"
                  min="1"
                  max="5"
                  class="w-full max-w-xs"
                />
                <p class="text-sm text-muted-foreground">建议值为 2-3 人</p>
              </div>

              <!-- 面试时长 -->
              <div class="space-y-2">
                <Label for="interview-duration">默认面试时长（分钟）</Label>
                <Input
                  id="interview-duration"
                  type="number"
                  v-model.number="settings.interview.interview_duration"
                  min="10"
                  max="120"
                  class="w-full max-w-xs"
                />
              </div>

              <!-- 自主预约 -->
              <div class="flex items-center justify-between">
                <div class="space-y-0.5">
                  <Label for="self-schedule">允许学生自主预约面试时间</Label>
                  <p class="text-sm text-muted-foreground">学生可以在可选时间段中选择面试时间</p>
                </div>
                <Switch
                  id="self-schedule"
                  v-model:checked="settings.interview.allow_self_schedule"
                />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <!-- 审核设置 -->
        <TabsContent value="review">
          <Card>
            <CardHeader>
              <CardTitle>审核配置</CardTitle>
            </CardHeader>
            <CardContent class="space-y-6">
              <!-- 自动通过阈值 -->
              <div class="space-y-2">
                <Label for="auto-approve-threshold">自动通过分数阈值</Label>
                <Input
                  id="auto-approve-threshold"
                  type="number"
                  v-model.number="settings.review.auto_approve_threshold"
                  min="60"
                  max="100"
                  class="w-full max-w-xs"
                />
                <p class="text-sm text-muted-foreground">
                  报名评分高于此值的学生可直接通过审核，无需人工审核
                </p>
              </div>

              <!-- 要求面试 -->
              <div class="flex items-center justify-between">
                <div class="space-y-0.5">
                  <Label for="require-interview">要求面试</Label>
                  <p class="text-sm text-muted-foreground">通过审核的学生必须参加面试才能录取</p>
                </div>
                <Switch
                  id="require-interview"
                  v-model:checked="settings.review.require_interview"
                />
              </div>

              <!-- 允许多部门报名 -->
              <div class="flex items-center justify-between">
                <div class="space-y-0.5">
                  <Label for="multiple-departments">允许报名多个部门</Label>
                  <p class="text-sm text-muted-foreground">学生可以同时报名多个部门</p>
                </div>
                <Switch
                  id="multiple-departments"
                  v-model:checked="settings.review.allow_multiple_departments"
                />
              </div>

              <!-- 最大选择部门数 -->
              <div class="space-y-2">
                <Label for="max-departments">最大可选部门数</Label>
                <Input
                  id="max-departments"
                  type="number"
                  v-model.number="settings.review.max_department_selections"
                  min="1"
                  max="5"
                  :disabled="!settings.review.allow_multiple_departments"
                  class="w-full max-w-xs"
                />
                <p class="text-sm text-muted-foreground">
                  学生最多可以选择的部门数量
                </p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <!-- 界面设置 -->
        <TabsContent value="ui">
          <Card>
            <CardHeader>
              <CardTitle>界面偏好</CardTitle>
            </CardHeader>
            <CardContent class="space-y-6">
              <!-- 主题 -->
              <div class="space-y-2">
                <Label for="theme">主题</Label>
                <Select v-model="settings.ui.theme">
                  <SelectTrigger id="theme" class="w-full max-w-xs">
                    <SelectValue placeholder="选择主题" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="light">浅色</SelectItem>
                    <SelectItem value="dark">深色</SelectItem>
                    <SelectItem value="auto">跟随系统</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <!-- 语言 -->
              <div class="space-y-2">
                <Label for="language">语言</Label>
                <Select v-model="settings.ui.language">
                  <SelectTrigger id="language" class="w-full max-w-xs">
                    <SelectValue placeholder="选择语言" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="zh-CN">简体中文</SelectItem>
                    <SelectItem value="en-US">English</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <!-- 日期格式 -->
              <div class="space-y-2">
                <Label for="date-format">日期格式</Label>
                <Select v-model="settings.ui.date_format">
                  <SelectTrigger id="date-format" class="w-full max-w-xs">
                    <SelectValue placeholder="选择日期格式" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="YYYY-MM-DD">2026-01-06</SelectItem>
                    <SelectItem value="YYYY/MM/DD">2026/01/06</SelectItem>
                    <SelectItem value="DD/MM/YYYY">06/01/2026</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <!-- 时间格式 -->
              <div class="space-y-2">
                <Label for="time-format">时间格式</Label>
                <Select v-model="settings.ui.time_format">
                  <SelectTrigger id="time-format" class="w-full max-w-xs">
                    <SelectValue placeholder="选择时间格式" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="24h">24小时制 (14:30)</SelectItem>
                    <SelectItem value="12h">12小时制 (2:30 PM)</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      <!-- 操作按钮 -->
      <div class="mt-6 flex items-center justify-end gap-3">
        <Button variant="outline" @click="resetSettings">
          重置
        </Button>
        <Button @click="saveSettings" :disabled="saving">
          {{ saving ? '保存中...' : '保存设置' }}
        </Button>
      </div>
    </div>
  </div>
</template>
