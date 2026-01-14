<script setup>
import { ref, computed, nextTick, onMounted, onUnmounted } from 'vue'
import { FileText, ChevronDown, ChevronUp, Trash2, Globe, ExternalLink, Copy, Check, Loader2, Plus } from 'lucide-vue-next'
import { useProjects } from '../composables/useProjects'
import { usePapers } from '../composables/usePapers'

const props = defineProps({
  source: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['toggle-context', 'delete'])

const { projects, currentProject } = useProjects()
const { copyPaperToProject } = usePapers()

const isOpen = ref(false)
const copied = ref(false)
const showCopyMenu = ref(false)
const isCopying = ref(false)
const copyMenuRef = ref(null)

const inContext = computed(() => props.source.inContext)

// Filter out current project
const otherProjects = computed(() => {
  return projects.value.filter(p => !currentProject.value || p.id !== currentProject.value.id)
})

const toggleContext = () => {
  emit('toggle-context', props.source.id)
}

const handleDelete = () => {
  emit('delete', props.source.id)
}

const copyBibtex = async () => {
  if (!props.source.bibtex) return
  try {
    await navigator.clipboard.writeText(props.source.bibtex)
    copied.value = true
    setTimeout(() => {
      copied.value = false
    }, 2000)
  } catch (err) {
    console.error('Failed to copy:', err)
  }
}

const handleCopy = async (targetProjectId) => {
  isCopying.value = true
  try {
    await copyPaperToProject(props.source.id, targetProjectId)
    showCopyMenu.value = false
    // Optional: Show success toast?
  } catch (e) {
    console.error("Failed to copy paper:", e)
  } finally {
    isCopying.value = false
  }
}

// Close menu on outside click
const handleClickOutside = (e) => {
  if (showCopyMenu.value && copyMenuRef.value && !copyMenuRef.value.contains(e.target)) {
    showCopyMenu.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
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

            <div v-if="source.bibtexLoading" class="text-slate-400" title="Generating BibTeX...">
              <Loader2 class="w-3.5 h-3.5 animate-spin" />
            </div>
            <button
              v-else-if="source.bibtex"
              @click="copyBibtex"
              class="text-slate-400 hover:text-accent transition-colors"
              :title="copied ? 'Copied!' : 'Copy BibTeX'"
            >
              <Check v-if="copied" class="w-3.5 h-3.5 text-green-500" />
              <Copy v-else class="w-3.5 h-3.5" />
            </button>

            <!-- Copy to Project -->
            <div class="relative" ref="copyMenuRef">
                <button
                    @click.stop="showCopyMenu = !showCopyMenu"
                    class="text-slate-400 hover:text-indigo-600 transition-colors"
                    title="Add to another project"
                    :disabled="isCopying"
                >
                    <Loader2 v-if="isCopying" class="w-3.5 h-3.5 animate-spin" />
                    <Plus v-else class="w-3.5 h-3.5" />
                </button>
                
                <div v-if="showCopyMenu" class="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 border border-slate-200 z-50">
                    <div class="px-3 py-1 text-xs font-semibold text-slate-500 border-b border-slate-100">Add to Project</div>
                    <div v-if="otherProjects.length === 0" class="px-3 py-2 text-xs text-slate-400 italic">No other projects</div>
                    <button
                        v-for="project in otherProjects"
                        :key="project.id"
                        @click="handleCopy(project.id)"
                        class="w-full text-left px-4 py-2 text-sm text-slate-700 hover:bg-slate-50 text-truncate"
                    >
                        {{ project.name }}
                    </button>
                </div>
            </div>

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
