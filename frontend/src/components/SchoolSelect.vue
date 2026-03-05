<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { searchSchools, type School } from '@/api/modules/school'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Search, X, School as SchoolIcon } from 'lucide-vue-next'

const props = defineProps<{
  modelValue: number | null
  modelCode?: string | null
  label?: string
  placeholder?: string
  required?: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: number | null]
  'update:modelCode': [value: string | null]
}>()

const query = ref('')
const schools = ref<School[]>([])
const loading = ref(false)
const showDropdown = ref(false)
const selectedIndex = ref(-1)
const inputRef = ref<HTMLInputElement | null>(null)
const dropdownRef = ref<HTMLDivElement | null>(null)

let debounceTimer: ReturnType<typeof setTimeout> | null = null

// 搜索学校
const search = async () => {
  if (!query.value.trim()) {
    schools.value = []
    showDropdown.value = false
    return
  }

  loading.value = true
  try {
    const res = await searchSchools(query.value)
    schools.value = res.items
    selectedIndex.value = -1
    showDropdown.value = true
  } catch (err) {
    schools.value = []
  } finally {
    loading.value = false
  }
}

// 防抖搜索
const debouncedSearch = () => {
  if (debounceTimer) {
    clearTimeout(debounceTimer)
  }
  debounceTimer = setTimeout(() => {
    search()
  }, 300)
}

// 选择学校
const selectSchool = (school: School) => {
  query.value = school.name
  emit('update:modelValue', school.id)
  emit('update:modelCode', school.code)
  showDropdown.value = false
  schools.value = []
}

// 清除选择
const clear = () => {
  query.value = ''
  emit('update:modelValue', null)
  emit('update:modelCode', null)
  schools.value = []
  showDropdown.value = false
  inputRef.value?.focus()
}

// 键盘导航
const handleKeydown = (e: KeyboardEvent) => {
  if (!showDropdown.value) {
    if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
      e.preventDefault()
      search()
    }
    return
  }

  switch (e.key) {
    case 'ArrowDown':
      e.preventDefault()
      selectedIndex.value = Math.min(selectedIndex.value + 1, schools.value.length - 1)
      scrollToSelected()
      break
    case 'ArrowUp':
      e.preventDefault()
      selectedIndex.value = Math.max(selectedIndex.value - 1, -1)
      scrollToSelected()
      break
    case 'Enter':
      e.preventDefault()
      if (selectedIndex.value >= 0 && schools.value[selectedIndex.value]) {
        selectSchool(schools.value[selectedIndex.value])
      }
      break
    case 'Escape':
      showDropdown.value = false
      break
  }
}

// 滚动到选中项
const scrollToSelected = () => {
  const dropdown = dropdownRef.value
  if (!dropdown) return

  const items = dropdown.querySelectorAll('[data-school-item]')
  const selected = items[selectedIndex.value] as HTMLElement
  if (selected) {
    selected.scrollIntoView({ block: 'nearest' })
  }
}

// 点击外部关闭
const handleClickOutside = (e: MouseEvent) => {
  const target = e.target as HTMLElement
  if (!target.closest('.school-select-container')) {
    showDropdown.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

// 监听输入
watch(query, () => {
  debouncedSearch()
})
</script>

<template>
  <div class="school-select-container relative grid gap-2">
    <Label v-if="label" :for="label">{{ label }}</Label>

    <div class="relative">
      <Input
        ref="inputRef"
        :id="label"
        v-model="query"
        type="text"
        :placeholder="placeholder || '输入学校名称搜索'"
        :required="required"
        autocomplete="off"
        @input="debouncedSearch"
        @keydown="handleKeydown"
        @focus="search"
        class="pr-10"
      />

      <!-- 清除按钮 -->
      <button
        v-if="modelValue"
        type="button"
        class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
        @click="clear"
      >
        <X class="w-4 h-4" />
      </button>

      <!-- 搜索图标 -->
      <Search v-else class="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
    </div>

    <!-- 下拉列表 -->
    <div
      v-if="showDropdown && schools.length > 0"
      ref="dropdownRef"
      class="absolute z-50 w-full mt-1 bg-white border rounded-md shadow-lg max-h-60 overflow-y-auto"
      style="top: 100%;"
    >
      <button
        v-for="(school, index) in schools"
        :key="school.id"
        type="button"
        data-school-item
        class="w-full px-3 py-2 text-left hover:bg-gray-100 flex items-center gap-2"
        :class="{ 'bg-primary/10 text-primary': index === selectedIndex }"
        @click="selectSchool(school)"
        @mouseenter="selectedIndex = index"
      >
        <SchoolIcon class="w-4 h-4 text-gray-400" />
        <span class="flex-1 truncate">{{ school.name }}</span>
      </button>
    </div>

    <!-- 无结果 -->
    <div
      v-if="showDropdown && query && schools.length === 0 && !loading"
      class="absolute z-50 w-full mt-1 px-3 py-2 bg-white border rounded-md shadow-lg text-sm text-gray-500"
      style="top: 100%;"
    >
      未找到匹配的学校
    </div>

    <!-- 加载中 -->
    <div
      v-if="loading"
      class="absolute z-50 w-full mt-1 px-3 py-2 bg-white border rounded-md shadow-lg text-sm text-gray-500"
      style="top: 100%;"
    >
      搜索中...
    </div>
  </div>
</template>
