<script setup>
import SourceItem from './SourceItem.vue'
import { Library } from 'lucide-vue-next'

defineProps({
  sources: {
    type: Array,
    required: true
  }
})
</script>

<template>
  <div class="flex flex-col h-full">
    <div class="p-4 border-b border-slate-200 flex items-center gap-2 bg-slate-50">
      <Library class="w-5 h-5 text-accent" />
      <h2 class="font-semibold text-slate-700">Sources Database</h2>
      <span class="ml-auto text-xs bg-white border border-slate-200 text-slate-500 px-2 py-0.5 rounded-full shadow-sm">{{ sources.length }}</span>
    </div>

    <div class="flex-1 overflow-y-auto p-4 space-y-4">
      <SourceItem 
        v-for="source in sources" 
        :key="source.id" 
        :source="source" 
      />
    </div>
  </div>
</template>
