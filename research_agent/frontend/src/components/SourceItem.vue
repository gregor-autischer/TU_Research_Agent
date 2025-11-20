<script setup>
import { ref } from 'vue'
import { FileText, ChevronDown, ChevronUp, Download, Globe } from 'lucide-vue-next'

const props = defineProps({
  source: {
    type: Object,
    required: true
  }
})

const isOpen = ref(false)
const inContext = ref(props.source.inContext)

const toggleContext = () => {
  inContext.value = !inContext.value
  // In a real app, emit event to update parent state
}
</script>

<template>
  <div class="bg-white border border-slate-200 rounded-lg overflow-hidden hover:border-accent/50 hover:shadow-md transition-all duration-200">
    <!-- Header -->
    <div class="p-3">
      <div class="flex items-start justify-between gap-2 mb-2">
        <div class="flex items-center gap-2 text-xs font-medium text-accent bg-blue-50 px-2 py-0.5 rounded border border-blue-100">
          <FileText v-if="source.type === 'PDF'" class="w-3 h-3" />
          <Globe v-else class="w-3 h-3" />
          {{ source.type }}
        </div>
        <div class="text-xs text-slate-400">{{ source.date }}</div>
      </div>
      
      <h3 class="font-medium text-slate-800 text-sm leading-snug mb-1">{{ source.title }}</h3>
      <p class="text-xs text-slate-500 mb-3">{{ source.authors }}</p>

      <!-- Actions -->
      <div class="flex items-center justify-between mt-2">
        <button class="p-1.5 text-slate-400 hover:text-accent hover:bg-blue-50 rounded transition-colors" title="Download">
          <Download class="w-4 h-4" />
        </button>
        
        <!-- Context Toggle -->
        <button 
          @click="toggleContext"
          class="flex items-center gap-2 px-2 py-1 rounded-full text-xs font-medium transition-colors border"
          :class="inContext ? 'bg-green-50 text-green-600 border-green-200' : 'bg-slate-50 text-slate-400 border-slate-200'"
        >
          <div class="w-2 h-2 rounded-full" :class="inContext ? 'bg-green-500' : 'bg-slate-300'"></div>
          Context
        </button>
      </div>
    </div>

    <!-- Summary Toggle -->
    <button 
      @click="isOpen = !isOpen"
      class="w-full flex items-center justify-between px-3 py-2 bg-slate-50 hover:bg-slate-100 text-xs text-slate-500 border-t border-slate-100 transition-colors"
    >
      <span>Summary</span>
      <ChevronUp v-if="isOpen" class="w-3 h-3" />
      <ChevronDown v-else class="w-3 h-3" />
    </button>

    <!-- Summary Content -->
    <div v-if="isOpen" class="p-3 bg-slate-50/50 text-xs text-slate-600 leading-relaxed border-t border-slate-100">
      {{ source.summary }}
    </div>
  </div>
</template>
