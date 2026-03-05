<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import {
  searchUsers,
  inviteInterviewer,
  getClubInterviewers,
  type SearchedUser,
  type ClubInterviewer,
} from '@/api/modules/invitation'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Search, UserPlus, Phone, User, Check, Shield, Mail } from 'lucide-vue-next'

const userStore = useUserStore()

// 搜索
const searchPhone = ref('')
const searchLoading = ref(false)
const searchError = ref('')
const searchedUsers = ref<SearchedUser[]>([])

// 邀请弹窗
const showInviteDialog = ref(false)
const selectedUser = ref<SearchedUser | null>(null)
const inviteLoading = ref(false)
const inviteSuccess = ref('')

// 面试官列表
const interviewers = ref<ClubInterviewer[]>([])
const interviewersLoading = ref(false)
const interviewersError = ref('')

// 获取社团 ID
const getClubId = () => {
  return userStore.userInfo?.roles.find((r) => r.code === 'CLUB_ADMIN')?.club_id
}

// 获取面试官列表
const fetchInterviewers = async () => {
  const clubId = getClubId()
  if (!clubId) {
    interviewersError.value = '未找到社团信息'
    return
  }

  try {
    interviewersLoading.value = true
    interviewersError.value = ''
    interviewers.value = await getClubInterviewers(clubId)
  } catch (err: any) {
    interviewersError.value = err.message || '获取面试官列表失败'
  } finally {
    interviewersLoading.value = false
  }
}

// 搜索用户
const handleSearch = async () => {
  if (!searchPhone.value.trim()) {
    searchError.value = '请输入手机号'
    return
  }

  if (searchPhone.value.trim().length < 11) {
    searchError.value = '请输入完整的手机号'
    return
  }

  try {
    searchLoading.value = true
    searchError.value = ''
    searchedUsers.value = await searchUsers({ phone: searchPhone.value.trim() })
    if (searchedUsers.value.length === 0) {
      searchError.value = '未找到该手机号的用户'
    }
  } catch (err: any) {
    searchError.value = err.message || '搜索失败'
  } finally {
    searchLoading.value = false
  }
}

// 打开发送邀请弹窗
const openInviteDialog = (user: SearchedUser) => {
  selectedUser.value = user
  inviteSuccess.value = ''
  showInviteDialog.value = true
}

// 发送邀请
const handleInvite = async () => {
  if (!selectedUser.value) return

  const clubId = getClubId()
  if (!clubId) {
    searchError.value = '未找到社团信息'
    return
  }

  try {
    inviteLoading.value = true
    await inviteInterviewer(clubId, { user_id: selectedUser.value.id })
    inviteSuccess.value = `已向 ${selectedUser.value.name || selectedUser.value.phone} 发送邀请`
    setTimeout(() => {
      showInviteDialog.value = false
      searchedUsers.value = []
      searchPhone.value = ''
      // 刷新面试官列表
      fetchInterviewers()
    }, 1500)
  } catch (err: any) {
    searchError.value = err.message || '发送邀请失败'
  } finally {
    inviteLoading.value = false
  }
}

// 格式化手机号
const formatPhone = (phone: string) => {
  return phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2')
}

// 格式化日期
const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

onMounted(() => {
  fetchInterviewers()
})
</script>

<template>
  <div class="absolute inset-0 flex flex-col">
    <!-- 头部 -->
    <div class="flex-shrink-0 px-6 pt-6 pb-4">
      <h1 class="text-2xl font-bold mb-2">社团人员管理</h1>
      <p class="text-muted-foreground">管理社团成员和面试官</p>
    </div>

    <!-- 内容区域 -->
    <div class="flex-1 min-h-0 overflow-y-auto px-6 pb-6">
      <Tabs default-value="interviewers" class="space-y-6">
        <TabsList>
          <TabsTrigger value="interviewers">面试官管理</TabsTrigger>
          <TabsTrigger value="invite">邀请面试官</TabsTrigger>
        </TabsList>

        <!-- 面试官列表 -->
        <TabsContent value="interviewers" class="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle class="flex items-center gap-2">
                <Shield class="w-5 h-5" />
                面试官列表
              </CardTitle>
              <CardDescription>当前社团的所有面试官</CardDescription>
            </CardHeader>
            <CardContent>
              <!-- 错误提示 -->
              <div v-if="interviewersError" class="mb-4 p-3 text-sm text-red-600 bg-red-50 rounded-md">
                {{ interviewersError }}
              </div>

              <!-- 加载状态 -->
              <div v-if="interviewersLoading" class="text-center py-12">
                <p class="text-muted-foreground">加载中...</p>
              </div>

              <!-- 数据列表 -->
              <Table v-else-if="interviewers.length > 0">
                <TableHeader>
                  <TableRow>
                    <TableHead>姓名</TableHead>
                    <TableHead>手机号</TableHead>
                    <TableHead>邮箱</TableHead>
                    <TableHead>加入时间</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  <TableRow v-for="interviewer in interviewers" :key="interviewer.id">
                    <TableCell class="font-medium">{{ interviewer.name }}</TableCell>
                    <TableCell>
                      <div class="flex items-center gap-2">
                        <Phone class="w-4 h-4 text-muted-foreground" />
                        {{ formatPhone(interviewer.phone) }}
                      </div>
                    </TableCell>
                    <TableCell>
                      <div class="flex items-center gap-2">
                        <Mail class="w-4 h-4 text-muted-foreground" />
                        {{ interviewer.email || '-' }}
                      </div>
                    </TableCell>
                    <TableCell>{{ formatDate(interviewer.joined_at) }}</TableCell>
                  </TableRow>
                </TableBody>
              </Table>

              <!-- 空状态 -->
              <div v-else class="text-center py-8 text-muted-foreground">
                暂无面试官，前往"邀请面试官"标签页添加
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <!-- 邀请面试官 -->
        <TabsContent value="invite" class="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>搜索并邀请</CardTitle>
              <CardDescription>输入手机号搜索用户并发送面试官邀请</CardDescription>
            </CardHeader>
            <CardContent class="space-y-4">
              <div class="flex gap-4">
                <div class="flex-1">
                  <Label for="phone">手机号</Label>
                  <div class="flex gap-2 mt-1.5">
                    <Input
                      id="phone"
                      v-model="searchPhone"
                      placeholder="请输入手机号"
                      @keyup.enter="handleSearch"
                    />
                    <Button @click="handleSearch" :disabled="searchLoading">
                      <Search class="w-4 h-4 mr-2" />
                      {{ searchLoading ? '搜索中...' : '搜索' }}
                    </Button>
                  </div>
                </div>
              </div>

              <!-- 错误提示 -->
              <div v-if="searchError" class="p-3 text-sm text-red-600 bg-red-50 rounded-md">
                {{ searchError }}
              </div>
            </CardContent>
          </Card>

          <!-- 搜索结果 -->
          <Card v-if="searchedUsers.length > 0">
            <CardHeader>
              <CardTitle class="text-lg">搜索结果</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>用户ID</TableHead>
                    <TableHead>姓名</TableHead>
                    <TableHead>手机号</TableHead>
                    <TableHead class="text-right">操作</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  <TableRow v-for="user in searchedUsers" :key="user.id">
                    <TableCell class="font-medium">{{ user.id }}</TableCell>
                    <TableCell>
                      <div class="flex items-center gap-2">
                        <User class="w-4 h-4 text-muted-foreground" />
                        {{ user.name || '未设置姓名' }}
                      </div>
                    </TableCell>
                    <TableCell>
                      <div class="flex items-center gap-2">
                        <Phone class="w-4 h-4 text-muted-foreground" />
                        {{ formatPhone(user.phone) }}
                      </div>
                    </TableCell>
                    <TableCell class="text-right">
                      <Button
                        size="sm"
                        @click="openInviteDialog(user)"
                      >
                        <UserPlus class="w-4 h-4 mr-1" />
                        发送邀请
                      </Button>
                    </TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </CardContent>
          </Card>

          <!-- 无结果 -->
          <Card v-if="searchedUsers.length === 0 && !searchLoading && searchPhone && !searchError">
            <CardContent class="flex flex-col items-center justify-center py-12">
              <User class="w-12 h-12 text-muted-foreground mb-4" />
              <p class="text-muted-foreground">未找到该手机号的用户</p>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  </div>

  <!-- 发送邀请确认弹窗 -->
  <Dialog :open="showInviteDialog" @update:open="showInviteDialog = $event">
    <DialogContent class="max-w-md">
      <DialogHeader>
        <DialogTitle>发送面试官邀请</DialogTitle>
        <DialogDescription>
          确认邀请「{{ selectedUser?.name || selectedUser?.phone }}」成为社团面试官吗？
        </DialogDescription>
      </DialogHeader>

      <!-- 成功提示 -->
      <div v-if="inviteSuccess" class="py-4">
        <div class="flex items-center gap-2 text-green-600">
          <Check class="w-5 h-5" />
          <span>{{ inviteSuccess }}</span>
        </div>
      </div>

      <!-- 确认内容 -->
      <div v-else class="py-4">
        <div class="bg-muted rounded-md p-4 space-y-2">
          <div class="flex justify-between text-sm">
            <span class="text-muted-foreground">姓名</span>
            <span class="font-medium">{{ selectedUser?.name || '未设置姓名' }}</span>
          </div>
          <div class="flex justify-between text-sm">
            <span class="text-muted-foreground">手机号</span>
            <span class="font-medium">{{ selectedUser?.phone }}</span>
          </div>
        </div>
        <p class="text-sm text-muted-foreground mt-4">
          对方接受邀请后将成为社团的面试官，可以参与面试评分等工作。
        </p>
      </div>

      <DialogFooter v-if="!inviteSuccess">
        <Button variant="outline" @click="showInviteDialog = false">取消</Button>
        <Button @click="handleInvite" :disabled="inviteLoading">
          {{ inviteLoading ? '发送中...' : '确认发送' }}
        </Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>
