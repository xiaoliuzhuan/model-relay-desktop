<script setup lang="ts">
defineProps<{
  testTooltip: string;
}>();

const emit = defineEmits<{
  test: [];
  add: [];
  edit: [];
  delete: [];
  "move-up": [];
  "move-down": [];
}>();
</script>

<template>
  <div class="mtga-panel-card">
    <div class="flex items-start justify-between gap-3">
      <div>
        <p class="text-sm font-medium text-slate-900">快捷操作</p>
        <p class="mt-1 text-xs text-slate-600">新增、维护顺序或对当前组做编辑与测活</p>
      </div>
      <button
        class="btn btn-xs btn-outline shrink-0 rounded-lg border-slate-200 px-3 text-slate-600 hover:border-indigo-400 hover:bg-indigo-50 hover:text-indigo-700 tooltip mtga-tooltip"
        :data-tip="testTooltip"
        style="--mtga-tooltip-max: 250px"
        @click="emit('test')"
      >
        测活
      </button>
    </div>

    <div class="mt-4 grid gap-2 sm:grid-cols-2">
      <button class="mtga-btn-primary" @click="emit('add')">新增配置组</button>
      <button class="mtga-btn-outline" @click="emit('edit')">修改当前组</button>
      <button class="mtga-btn-error" @click="emit('delete')">删除当前组</button>
      <button class="mtga-btn-outline" @click="emit('move-up')">上移当前组</button>
      <button class="mtga-btn-outline sm:col-span-2" @click="emit('move-down')">下移当前组</button>
    </div>

    <p class="mt-3 text-xs text-slate-500">
      删除、修改、排序都会基于当前选中的配置组执行；删除时仍会至少保留一个配置组。
    </p>
  </div>
</template>
