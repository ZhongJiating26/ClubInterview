<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useUserStore } from '@/stores/user'
import {
  getPositions,
  getDepartments,
  createPosition,
  updatePosition,
  deletePosition,
  type Position,
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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
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

// 岗位列表和部门列表
const positions = ref<Position[]>([])
const departments = ref<Department[]>([])
const loading = ref(false)
const error = ref('')
const success = ref('')

// 对话框状态
const showDialog = ref(false)
const dialogMode = ref<'create' | 'edit'>('create')
const deleteDialog = ref(false)
const positionToDelete = ref<Position | null>(null)
const editingPosId = ref<number | null>(null)  // 保存编辑中的岗位 ID

// 表单数据
const formData = ref({
  name: '',
  description: '',
  requirement: '',
  department_id: '' as string,
})

// 获取社团 ID
const getClubId = () => {
  return userStore.userInfo?.roles.find((r) => r.code === 'CLUB_ADMIN')?.club_id
}

// 获取部门列表
const fetchDepartments = async () => {
  const clubId = getClubId()
  if (!clubId) return

  try {
    const res = await getDepartments(clubId)
    departments.value = res
  } catch (err) {
  }
}

// 获取岗位列表
const fetchPositions = async () => {
  const clubId = getClubId()
  if (!clubId) {
    error.value = '未找到社团信息'
    return
  }

  try {
    loading.value = true
    const res = await getPositions(clubId)
    positions.value = res
  } catch (err: any) {
    error.value = err.message || '获取岗位列表失败'
  } finally {
    loading.value = false
  }
}

// 根据部门 ID 获取部门名称
const getDepartmentName = (deptId: number | null) => {
  if (!deptId) return '未分配部门'
  const dept = departments.value.find((d) => d.id === deptId)
  return dept?.name || '未知部门'
}

// 打开创建对话框
const openCreateDialog = () => {
  formData.value = {
    name: '',
    description: '',
    requirement: '',
    department_id: '',
  }
  editingPosId.value = null  // 重置编辑 ID
  dialogMode.value = 'create'
  showDialog.value = true
}

// 打开编辑对话框
const openEditDialog = (pos: Position) => {
  formData.value = {
    name: pos.name,
    description: pos.description || '',
    requirement: pos.requirement || '',
    department_id: pos.department_id?.toString() || '',
  }
  editingPosId.value = pos.id  // 保存岗位 ID
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
    error.value = '请输入岗位名称'
    return
  }

  try {
    loading.value = true
    error.value = ''
    success.value = ''

    const data = {
      name: formData.value.name,
      description: formData.value.description,
      requirement: formData.value.requirement,
      department_id: formData.value.department_id && formData.value.department_id !== '-1' ? Number(formData.value.department_id) : undefined,
    }

    if (dialogMode.value === 'create') {
      await createPosition(clubId, data)
      success.value = '创建成功'
    } else if (editingPosId.value) {
      // 编辑模式，使用保存的岗位 ID
      await updatePosition(clubId, editingPosId.value, data)
      success.value = '更新成功'
    }

    showDialog.value = false
    await fetchPositions()
  } catch (err: any) {
    error.value = err.message || (dialogMode.value === 'create' ? '创建失败' : '更新失败')
  } finally {
    loading.value = false
  }
}

// 打开删除确认对话框
const openDeleteDialog = (pos: Position) => {
  positionToDelete.value = pos
  deleteDialog.value = true
}

// 确认删除
const handleDelete = async () => {
  const clubId = getClubId()
  const pos = positionToDelete.value
  if (!clubId || !pos) return

  try {
    loading.value = true
    error.value = ''
    success.value = ''

    await deletePosition(clubId, pos.id)
    success.value = '删除成功'
    deleteDialog.value = false
    positionToDelete.value = null
    await fetchPositions()
  } catch (err: any) {
    error.value = err.message || '删除失败'
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await Promise.all([fetchDepartments(), fetchPositions()])
})
</script>

<template>
  <div class="flex flex-col flex-1 overflow-hidden">
    <div class="flex-1 min-h-0 overflow-y-auto p-6">
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold">岗位管理</h1>
      <Button @click="openCreateDialog">
        <Plus class="w-4 h-4 mr-2" />
        新建岗位
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

    <!-- 岗位列表 -->
    <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      <Card v-for="pos in positions" :key="pos.id" class="border-0 h-full flex flex-col">
        <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle class="text-lg">{{ pos.name }}</CardTitle>
        </CardHeader>
        <CardContent class="flex-1 flex flex-col">
          <p class="text-sm text-muted-foreground">
            部门: {{ getDepartmentName(pos.department_id) }}
          </p>
          <p v-if="pos.description" class="text-sm break-words line-clamp-2 mt-2">
            {{ pos.description }}
          </p>
          <p v-if="pos.requirement" class="text-xs text-muted-foreground break-words line-clamp-2 mt-2">
            要求: {{ pos.requirement }}
          </p>
          <div class="flex items-center gap-1 pt-2 mt-auto">
            <Button variant="ghost" size="icon" @click="openEditDialog(pos)">
              <Pencil class="w-4 h-4" />
            </Button>
            <Button variant="ghost" size="icon" @click="openDeleteDialog(pos)">
              <Trash2 class="w-4 h-4 text-red-500" />
            </Button>
          </div>
        </CardContent>
      </Card>

      <!-- 空状态 -->
      <div v-if="positions.length === 0 && !loading" class="col-span-full">
        <Card class="border-0">
          <CardContent class="flex flex-col items-center justify-center py-12">
            <p class="text-muted-foreground mb-4">暂无岗位，点击下方按钮创建</p>
            <Button @click="openCreateDialog">
              <Plus class="w-4 h-4 mr-2" />
              新建岗位
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>

    <!-- 创建/编辑对话框 -->
    <Dialog :open="showDialog" @update:open="showDialog = $event">
      <DialogContent class="max-w-lg">
        <DialogHeader>
          <DialogTitle>{{ dialogMode === 'create' ? '新建岗位' : '编辑岗位' }}</DialogTitle>
          <DialogDescription>填写岗位信息后点击确认保存</DialogDescription>
        </DialogHeader>
        <div class="space-y-4 py-4">
          <div class="space-y-2">
            <Label for="pos-name">岗位名称</Label>
            <Input
              id="pos-name"
              v-model="formData.name"
              placeholder="请输入岗位名称"
            />
          </div>

          <div class="space-y-2">
            <Label for="pos-dept">所属部门</Label>
            <Select v-model="formData.department_id">
              <SelectTrigger>
                <SelectValue placeholder="请选择部门（选填）" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="-1">未分配部门</SelectItem>
                <SelectItem v-for="dept in departments" :key="dept.id" :value="dept.id.toString()">
                  {{ dept.name }}
                </SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div class="space-y-2">
            <Label for="pos-desc">岗位描述</Label>
            <Textarea
              id="pos-desc"
              v-model="formData.description"
              placeholder="请输入岗位描述（选填）"
              rows="2"
            />
          </div>

          <div class="space-y-2">
            <Label for="pos-req">任职要求</Label>
            <Textarea
              id="pos-req"
              v-model="formData.requirement"
              placeholder="请输入任职要求（选填）"
              rows="2"
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
            确定要删除岗位 "{{ positionToDelete?.name }}" 吗？删除后无法恢复。
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
