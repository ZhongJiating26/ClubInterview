<script setup lang="ts">
import { h } from 'vue'
import { cn } from '@/lib/utils'

interface Step {
  title: string
  description: string
}

const props = defineProps<{
  modelValue: number
  steps: Step[]
  class?: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: number]
}>()

const updateStep = (index: number) => {
  emit('update:modelValue', index)
}

// Check icon SVG
const CheckIcon = () => {
  return h('svg', {
    xmlns: 'http://www.w3.org/2000/svg',
    width: '16',
    height: '16',
    viewBox: '0 0 24 24',
    fill: 'none',
    stroke: 'currentColor',
    'stroke-width': '2',
    'stroke-linecap': 'round',
    'stroke-linejoin': 'round'
  }, [
    h('polyline', { points: '20 6 9 17 4 12' })
  ])
}
</script>

<template>
  <div :class="cn('flex items-center justify-between', props.class)">
    <div
      v-for="(step, index) in steps"
      :key="index"
      class="flex items-center flex-1"
    >
      <!-- 步骤项 -->
      <button
        type="button"
        class="flex items-center gap-3 p-1 group"
        :class="{ 'cursor-pointer': index <= modelValue }"
        :disabled="index > modelValue"
        @click="updateStep(index)"
      >
        <!-- 步骤指示器 -->
        <div
          :class="cn(
            'inline-flex items-center justify-center rounded-full w-8 h-8 text-sm font-medium transition-colors',
            index < modelValue ? 'bg-primary text-primary-foreground' :
            index === modelValue ? 'bg-primary text-primary-foreground' :
            'bg-muted text-muted-foreground'
          )"
        >
          <CheckIcon v-if="index < modelValue" />
          <span v-else>{{ index + 1 }}</span>
        </div>

        <!-- 标题和描述 -->
        <div class="flex flex-col items-start text-left">
          <span
            :class="cn(
              'text-sm font-medium',
              index <= modelValue ? 'text-foreground' : 'text-muted-foreground'
            )"
          >
            {{ step.title }}
          </span>
          <span class="text-xs text-muted-foreground">
            {{ step.description }}
          </span>
        </div>
      </button>

      <!-- 分隔线 -->
      <div
        v-if="index < steps.length - 1"
        :class="cn(
          'flex-1 h-px mx-4 transition-colors',
          index < modelValue ? 'bg-primary' : 'bg-muted'
        )"
      />
    </div>
  </div>
</template>
