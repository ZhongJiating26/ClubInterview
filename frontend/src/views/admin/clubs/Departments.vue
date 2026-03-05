<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import {
  getDepartments,
  createDepartment,
  updateDepartment,
  deleteDepartment,
  type Department,
} from '@/api/modules/clubs'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog'
import { Plus, Pencil, Trash2 } from 'lucide-vue-next'

const userStore = useUserStore()

// 部门列表
const departments = ref<Department[]>([])
const loading = ref(false)
const error = ref('')
const success = ref('')

// 对话框状态
const showDialog = ref(false)
const dialogMode = ref<'create' | 'edit'>('create')
const deleteDialog = ref(false)
const departmentToDelete = ref<Department | null>(null)
const editingDeptId = ref<number | null>(null)  // 保存编辑中的部门 ID

// 表单数据
const formData = ref({
  name: '',
  description: '',
})

const categoryOptions = [
  '学术科技类',
  '文化艺术类',
  '体育健身类',
  '公益服务类',
  '创新创业类',
  '其他类',
]

// 获取社团 ID
const getClubId = () => {
  return userStore.userInfo?.roles.find((r) => r.code === 'CLUB_ADMIN')?.club_id
}

// 获取部门列表
const fetchDepartments = async () => {
  const clubId = getClubId()
  if (!clubId) {
    error.value = '未找到社团信息'
    return
  }

  try {
    loading.value = true
    const res = await getDepartments(clubId)
    departments.value = res
  } catch (err: any) {
    error.value = err.message || '获取部门列表失败'
  } finally {
    loading.value = false
  }
}

// 打开创建对话框
const openCreateDialog = () => {
  formData.value = { name: '', description: '' }
  editingDeptId.value = null  // 重置编辑 ID
  dialogMode.value = 'create'
  showDialog.value = true
}

// 打开编辑对话框
const openEditDialog = (dept: Department) => {
  formData.value = { name: dept.name, description: dept.description || '' }
  editingDeptId.value = dept.id  // 保存部门 ID
  dialogMode.value = 'edit'
  showDialog.value = true
}

// 确认创建/编辑
const handleConfirm = async () => {
  const clubId = getClubId()
  if (!clubId) {
    error.value = '未找到社团信息'
    return
  }

  if (!formData.value.name.trim()) {
    error.value = '请输入部门名称'
    return
  }

  try {
    loading.value = true
    error.value = ''
    success.value = ''

    if (dialogMode.value === 'create') {
      await createDepartment(clubId, {
        name: formData.value.name,
        description: formData.value.description,
      })
      success.value = '创建成功'
    } else if (editingDeptId.value) {
      // 编辑模式，使用保存的部门 ID
      await updateDepartment(clubId, editingDeptId.value, {
        name: formData.value.name,
        description: formData.value.description,
      })
      success.value = '更新成功'
    }

    showDialog.value = false
    await fetchDepartments()
  } catch (err: any) {
    error.value = err.message || (dialogMode.value === 'create' ? '创建失败' : '更新失败')
  } finally {
    loading.value = false
  }
}

// 打开删除确认对话框
const openDeleteDialog = (dept: Department) => {
  departmentToDelete.value = dept
  deleteDialog.value = true
}

// 确认删除
const handleDelete = async () => {
  const clubId = getClubId()
  const dept = departmentToDelete.value
  if (!clubId || !dept) return

  try {
    loading.value = true
    error.value = ''
    success.value = ''

    await deleteDepartment(clubId, dept.id)
    success.value = '删除成功'
    deleteDialog.value = false
    departmentToDelete.value = null
    await fetchDepartments()
  } catch (err: any) {
    error.value = err.message || '删除失败'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchDepartments()
})
</script>

<template>
  <div class="flex flex-col flex-1 overflow-hidden">
    <div class="flex-1 min-h-0 overflow-y-auto p-6">
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold">部门管理</h1>
      <Button @click="openCreateDialog">
        <Plus class="w-4 h-4 mr-2" />
        新建部门
      </Button>
    </div>

    <!-- 错误提示 -->
    <div v-if="error" class="mb-4 p-3 text-sm text-red-600 bg-red-50 rounded-md">
      {{ error }}
    </div>

    <!-- 成功提示 -->
    <div v-if="success" class="mb-4 p-3 text-sm text-green-600 bg-green-50 rounded-md">
      {{ success }}
    </div>

    <!-- 部门列表 -->
    <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      <Card v-for="dept in departments" :key="dept.id" class="border-0 h-full flex flex-col">
        <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle class="text-lg">{{ dept.name }}</CardTitle>
          <div class="flex items-center gap-1">
            <Button variant="ghost" size="icon" @click="openEditDialog(dept)">
              <Pencil class="w-4 h-4" />
            </Button>
            <Button variant="ghost" size="icon" @click="openDeleteDialog(dept)">
              <Trash2 class="w-4 h-4 text-red-500" />
            </Button>
          </div>
        </CardHeader>
        <CardContent class="flex-1 flex flex-col">
          <p class="text-sm text-muted-foreground break-words line-clamp-3">
            {{ dept.description || '暂无描述' }}
          </p>
          <p class="text-xs text-muted-foreground mt-auto pt-2">
            创建时间: {{ new Date(dept.created_at).toLocaleDateString() }}
          </p>
        </CardContent>
      </Card>

      <!-- 空状态 -->
      <div v-if="departments.length === 0 && !loading" class="col-span-full">
        <Card class="border-0">
          <CardContent class="flex flex-col items-center justify-center py-12">
            <p class="text-muted-foreground mb-4">暂无部门，点击下方按钮创建</p>
            <Button @click="openCreateDialog">
              <Plus class="w-4 h-4 mr-2" />
              新建部门
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>

    <!-- 创建/编辑对话框 -->
    <Dialog :open="showDialog" @update:open="showDialog = $event">
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{{ dialogMode === 'create' ? '新建部门' : '编辑部门' }}</DialogTitle>
        </DialogHeader>
        <div class="space-y-4 py-4">
          <div class="space-y-2">
            <Label for="dept-name">部门名称</Label>
            <Input
              id="dept-name"
              v-model="formData.name"
              placeholder="请输入部门名称"
            />
          </div>
          <div class="space-y-2">
            <Label for="dept-desc">部门描述</Label>
            <Textarea
              id="dept-desc"
              v-model="formData.description"
              placeholder="请输入部门描述（选填）"
              rows="3"
            />
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" @click="showDialog = false">取消</Button>
          <Button @click="handleConfirm" :disabled="loading">
            {{ loading ? '保存中...' : '确认' }}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>

    <!-- 删除确认对话框 -->
    <Dialog :open="deleteDialog" @update:open="deleteDialog = $event">
      <DialogContent>
        <DialogHeader>
          <DialogTitle>确认删除</DialogTitle>
          <DialogDescription>
            确定要删除部门 "{{ departmentToDelete?.name }}" 吗？删除后无法恢复。
          </DialogDescription>
        </DialogHeader>
        <DialogFooter>
          <Button variant="outline" @click="deleteDialog = false">取消</Button>
          <Button variant="destructive" @click="handleDelete" :disabled="loading">
            {{ loading ? '删除中...' : '确认删除' }}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
    </div>
  </div>
</template>
