<script setup>
import { ref, computed } from 'vue'
import { FileText, ChevronDown, ChevronUp, Trash2, Globe, ExternalLink } from 'lucide-vue-next'

const props = defineProps({
  source: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['toggle-context', 'delete'])

const isOpen = ref(false)

const inContext = computed(() => props.source.inContext)

const toggleContext = () => {
  emit('toggle-context', props.source.id)
}

const handleDelete = () => {
  emit('delete', props.source.id)
}
</script>

<template>
  <div class="group border-b border-slate-100 hover:bg-slate-50 transition-colors">
    <!-- Main Row -->
    <div class="py-4 px-3 flex items-start gap-3">
      <!-- Icon -->
      <div class="mt-0.5 text-slate-400">
        <FileText v-if="source.type === 'PDF'" class="w-4 h-4" />
        <Globe v-else class="w-4 h-4" />
      </div>

      <!-- Content -->
      <div class="flex-1 min-w-0">
        <div class="flex items-start justify-between gap-2">
          <h3 class="font-medium text-slate-800 text-sm leading-tight truncate pr-2" :title="source.title">
            {{ source.title }}
          </h3>
          <span class="text-[10px] text-slate-400 whitespace-nowrap shrink-0">{{ source.date }}</span>
        </div>

        <div class="flex items-center justify-between mt-2">
          <p class="text-xs text-slate-500 truncate max-w-[120px]" :title="source.authors">{{ source.authors }}</p>

          <div class="flex items-center gap-3">
            <a
              v-if="source.link"
              :href="source.link"
              target="_blank"
              rel="noopener noreferrer"
              class="text-slate-400 hover:text-accent transition-colors"
              title="Open paper"
            >
              <ExternalLink class="w-3.5 h-3.5" />
            </a>

            <button
              @click="handleDelete"
              class="text-slate-400 hover:text-red-500 transition-colors"
              title="Delete"
            >
              <Trash2 class="w-3.5 h-3.5" />
            </button>

            <button
              @click="toggleContext"
              class="flex items-center gap-1.5 text-xs font-medium transition-colors"
              :class="inContext ? 'text-green-600' : 'text-slate-400 hover:text-slate-600'"
              title="Toggle Context"
            >
              <div class="w-2 h-2 rounded-full" :class="inContext ? 'bg-green-500' : 'bg-slate-300'"></div>
              Context
            </button>

            <button
              @click="isOpen = !isOpen"
              class="flex items-center gap-1 text-xs font-medium text-slate-400 hover:text-slate-600 transition-colors"
            >
              <span>Summary</span>
              <ChevronUp v-if="isOpen" class="w-3.5 h-3.5" />
              <ChevronDown v-else class="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Summary Row -->
    <div v-if="isOpen" class="px-3 pb-3 pl-10">
      <div class="text-xs text-slate-600 leading-relaxed bg-slate-50 p-2 rounded border border-slate-100">
        {{ source.summary }}
      </div>
    </div>
  </div>
</template>
