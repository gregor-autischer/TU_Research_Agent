<script setup>
import SourceItem from './SourceItem.vue'
import { Library, Download } from 'lucide-vue-next'
import { computed } from 'vue'

const props = defineProps({
  sources: {
    type: Array,
    required: true
  }
})

const emit = defineEmits(['toggle-context', 'delete-paper'])

const handleToggleContext = (id) => {
  emit('toggle-context', id)
}

const handleDelete = (id) => {
  emit('delete-paper', id)
}

const hasAnyBibtex = computed(() => {
  return props.sources.some(s => s.bibtex)
})

const downloadAllBibtex = () => {
  const bibtexEntries = props.sources
    .filter(s => s.bibtex)
    .map(s => s.bibtex)
    .join('\n\n')

  if (!bibtexEntries) return

  const blob = new Blob([bibtexEntries], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'references.bib'
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}
</script>

<template>
  <div class="flex flex-col h-full">
    <div class="p-4 border-b border-slate-200 flex items-center gap-2 bg-slate-50">
      <Library class="w-5 h-5 text-accent" />
      <h2 class="font-semibold text-slate-700">Sources Database</h2>
      <span class="ml-auto text-xs bg-white border border-slate-200 text-slate-500 px-2 py-0.5 rounded-full shadow-sm">{{ sources.length }}</span>
    </div>

    <div class="flex-1 overflow-y-auto bg-white">
      <SourceItem
        v-for="source in sources"
        :key="source.id"
        :source="source"
        @toggle-context="handleToggleContext"
        @delete="handleDelete"
      />
    </div>

    <div v-if="hasAnyBibtex" class="p-3 border-t border-slate-200 bg-slate-50">
      <button
        @click="downloadAllBibtex"
        class="w-full flex items-center justify-center gap-2 px-3 py-2 bg-accent text-white rounded-lg hover:bg-accent/90 transition-colors text-sm font-medium"
      >
        <Download class="w-4 h-4" />
        Download All BibTeX
      </button>
    </div>
  </div>
</template>
