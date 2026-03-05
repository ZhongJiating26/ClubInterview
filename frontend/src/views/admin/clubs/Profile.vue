<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { getClub, updateClub, type ClubInfo } from '@/api/modules/clubs'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

const userStore = useUserStore()

// 原始数据（从服务器获取）
const originalData = ref<ClubInfo | null>(null)

// 表单数据（编辑用）
const formData = ref({
  name: '',
  category: '',
  description: '',
  logo_url: '',  // 存储完整 URL
  cert_file_url: '',  // 认证证书 URL
})

// 选择的文件
const logoFile = ref<File | null>(null)
const certFile = ref<File | null>(null)

// 视图模式: 'view' | 'edit'
const viewMode = ref<'view' | 'edit'>('view')
const loading = ref(false)
const error = ref('')
const success = ref('')

// 社团分类选项
const categoryOptions = [
  '学术科技类',
  '文化艺术类',
  '体育健身类',
  '公益服务类',
  '创新创业类',
  '其他类'
]

// 获取社团信息
const fetchClub = async () => {
  const clubId = userStore.userInfo?.roles.find(r => r.code === 'CLUB_ADMIN')?.club_id
  if (!clubId) {
    error.value = '未找到社团信息'
    return
  }

  try {
    const res = await getClub(clubId)
    originalData.value = res
    // 初始化表单数据
    formData.value = {
      name: res.name,
      category: res.category,
      description: res.description,
      logo_url: res.logo_url,
      cert_file_url: res.cert_file_url || ''
    }
  } catch (err: any) {
    error.value = err.message || '获取社团信息失败'
  }
}

// 进入编辑模式
const handleEdit = () => {
  if (!originalData.value) return
  formData.value = {
    name: originalData.value.name,
    category: originalData.value.category,
    description: originalData.value.description,
    logo_url: originalData.value.logo_url,
    cert_file_url: originalData.value.cert_file_url || ''
  }
  logoFile.value = null
  certFile.value = null
  viewMode.value = 'edit'
  error.value = ''
  success.value = ''
}

// 取消编辑
const handleCancel = () => {
  if (!originalData.value) return
  formData.value = {
    name: originalData.value.name,
    category: originalData.value.category,
    description: originalData.value.description,
    logo_url: originalData.value.logo_url,
    cert_file_url: originalData.value.cert_file_url || ''
  }
  logoFile.value = null
  certFile.value = null
  viewMode.value = 'view'
  error.value = ''
}

// 选择 logo 图片
const handleLogoChange = (event: Event) => {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return

  // 验证文件类型
  if (!file.type.startsWith('image/')) {
    error.value = '请选择图片文件'
    return
  }

  // 验证文件大小 (2MB)
  if (file.size > 2 * 1024 * 1024) {
    error.value = '图片大小不能超过 2MB'
    return
  }

  logoFile.value = file
  error.value = ''
}

// 选择证书文件
const handleCertChange = (event: Event) => {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return

  // 验证文件类型 (PDF 或 图片)
  const allowedTypes = ['image/jpeg', 'image/png', 'image/jpg', 'application/pdf']
  if (!allowedTypes.includes(file.type)) {
    error.value = '请选择 PDF 或图片文件'
    return
  }

  // 验证文件大小 (5MB)
  if (file.size > 5 * 1024 * 1024) {
    error.value = '文件大小不能超过 5MB'
    return
  }

  certFile.value = file
  error.value = ''
}

// 获取证书显示名称
const getCertFileName = () => {
  if (certFile.value) {
    return certFile.value.name
  }
  if (formData.value.cert_file_url) {
    // 从 URL 中提取文件名
    const urlParts = formData.value.cert_file_url.split('/')
    return urlParts[urlParts.length - 1] || '认证证书'
  }
  return ''
}

// 确认修改
const handleConfirm = async () => {
  if (!originalData.value) return
  error.value = ''
  success.value = ''
  loading.value = true

  try {
    // 调用更新接口，传入文件和基本信息
    const res = await updateClub(originalData.value.id, {
      name: formData.value.name,
      category: formData.value.category,
      description: formData.value.description,
      logo: logoFile.value,
      cert_file: certFile.value
    })

    success.value = '保存成功'
    // 重新获取数据
    await fetchClub()
    viewMode.value = 'view'
  } catch (err: any) {
    error.value = err.message || '保存失败'
  } finally {
    loading.value = false
  }
}

// 获取 Logo 显示 URL（优先本地预览，否则原始 URL）
const getLogoUrl = () => {
  if (logoFile.value) {
    return URL.createObjectURL(logoFile.value)
  }
  return formData.value.logo_url || ''
}

// 状态文本映射
const statusText: Record<string, string> = {
  REVIEW: '审核中',
  APPROVED: '已通过',
  REJECTED: '已拒绝'
}

onMounted(() => {
  fetchClub()
})
</script>

<template>
  <div class="flex flex-col flex-1 overflow-hidden">
    <div class="flex-1 min-h-0 overflow-y-auto p-6">
    <div class="max-w-2xl mx-auto">
    <h1 class="text-2xl font-bold mb-6">社团资料</h1>

    <!-- 错误提示 -->
    <div v-if="error" class="mb-4 p-3 text-sm text-red-600 bg-red-50 rounded-md">
      {{ error }}
    </div>

    <!-- 成功提示 -->
    <div v-if="success" class="mb-4 p-3 text-sm text-green-600 bg-green-50 rounded-md">
      {{ success }}
    </div>

    <!-- 查看模式 -->
    <div v-if="viewMode === 'view'">
      <Card class="border-0">
        <CardHeader class="flex flex-row items-center gap-4">
          <img
            v-if="formData.logo_url"
            :src="formData.logo_url"
            alt="社团 Logo"
            class="w-20 h-20 rounded-lg object-cover"
          />
          <div v-else class="w-20 h-20 rounded-lg bg-gray-200 flex items-center justify-center">
            <span class="text-gray-400 text-sm">暂无 Logo</span>
          </div>
          <div class="flex-1">
            <CardTitle class="text-xl">{{ formData.name }}</CardTitle>
            <p class="text-sm text-muted-foreground mt-1">{{ formData.category }}</p>
            <p class="text-xs text-muted-foreground mt-0.5">{{ originalData?.school_name }}</p>
          </div>
          <Badge variant="secondary">{{ statusText[originalData?.status || ''] || originalData?.status }}</Badge>
        </CardHeader>
        <CardContent class="space-y-4">
          <div>
            <Label class="text-sm text-muted-foreground">社团简介</Label>
            <p class="mt-1">{{ formData.description || '暂无简介' }}</p>
          </div>
          <div>
            <Label class="text-sm text-muted-foreground">认证证书</Label>
            <div v-if="formData.cert_file_url" class="mt-1">
              <a
                :href="formData.cert_file_url"
                target="_blank"
                class="text-blue-600 hover:underline flex items-center gap-1"
              >
                查看证书
              </a>
            </div>
            <p v-else class="mt-1 text-muted-foreground">暂无证书</p>
          </div>
          <div class="pt-4 border-t">
            <Button @click="handleEdit">修改资料</Button>
          </div>
        </CardContent>
      </Card>
    </div>

    <!-- 编辑模式 -->
    <form v-else @submit.prevent="handleConfirm">
      <Card class="border-0">
        <CardHeader>
          <CardTitle>编辑社团资料</CardTitle>
        </CardHeader>
        <CardContent class="space-y-4">
          <!-- Logo -->
          <div class="space-y-2">
            <Label>社团 Logo</Label>
            <div class="flex items-center gap-4">
              <img
                :src="getLogoUrl()"
                alt="Logo 预览"
                class="w-20 h-20 rounded-lg object-cover"
              />
              <div>
                <input
                  type="file"
                  accept="image/*"
                  class="hidden"
                  id="logo-upload"
                  @change="handleLogoChange"
                />
                <Label
                  for="logo-upload"
                  class="cursor-pointer inline-flex items-center justify-center rounded-md text-sm font-medium border border-gray-300 bg-white hover:bg-gray-50 px-4 py-2"
                >
                  {{ logoFile ? '重新选择' : '选择图片' }}
                </Label>
                <p class="text-xs text-muted-foreground mt-1">支持 jpg、png，最大 2MB</p>
              </div>
            </div>
          </div>

          <!-- 社团名称 -->
          <div class="space-y-2">
            <Label for="name">社团名称</Label>
            <Input id="name" v-model="formData.name" required />
          </div>

          <!-- 社团分类 -->
          <div class="space-y-2">
            <Label for="category">社团分类</Label>
            <Select v-model="formData.category" required>
              <SelectTrigger>
                <SelectValue placeholder="请选择分类" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem v-for="cat in categoryOptions" :key="cat" :value="cat">
                  {{ cat }}
                </SelectItem>
              </SelectContent>
            </Select>
          </div>

          <!-- 社团简介 -->
          <div class="space-y-2">
            <Label for="description">社团简介</Label>
            <Textarea
              id="description"
              v-model="formData.description"
              placeholder="请输入社团简介"
              rows="4"
            />
          </div>

          <!-- 认证证书 -->
          <div class="space-y-2">
            <Label>认证证书</Label>
            <div class="flex items-center gap-4">
              <div class="flex-1">
                <div v-if="formData.cert_file_url || certFile" class="flex items-center gap-2">
                  <span class="text-sm text-green-600">✓ 已上传</span>
                  <span class="text-sm text-muted-foreground">{{ getCertFileName() }}</span>
                </div>
                <p v-else class="text-sm text-muted-foreground">暂未上传证书</p>
              </div>
              <div>
                <input
                  type="file"
                  accept=".pdf,.jpg,.jpeg,.png"
                  class="hidden"
                  id="cert-upload"
                  @change="handleCertChange"
                />
                <Label
                  for="cert-upload"
                  class="cursor-pointer inline-flex items-center justify-center rounded-md text-sm font-medium border border-gray-300 bg-white hover:bg-gray-50 px-4 py-2"
                >
                  {{ certFile ? '重新上传' : '上传证书' }}
                </Label>
                <p class="text-xs text-muted-foreground mt-1">支持 PDF、jpg、png，最大 5MB</p>
              </div>
            </div>
          </div>

          <!-- 按钮组 -->
          <div class="flex gap-4 pt-4 border-t">
            <Button type="button" variant="outline" @click="handleCancel" :disabled="loading">
              取消
            </Button>
            <Button type="submit" :disabled="loading">
              {{ loading ? '保存中...' : '确认修改' }}
            </Button>
          </div>
        </CardContent>
      </Card>
    </form>
    </div>
    </div>
  </div>
</template>
