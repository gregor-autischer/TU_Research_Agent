<script setup>
import SidebarLeft from './components/SidebarLeft.vue'
import ChatArea from './components/ChatArea.vue'
import SidebarRight from './components/SidebarRight.vue'
import { ref, onUnmounted } from 'vue'
import { ChevronLeft, ChevronRight } from 'lucide-vue-next'

const sources = ref([
  {
    id: 1,
    title: "Attention Is All You Need",
    authors: "Vaswani et al.",
    date: "2017",
    type: "PDF",
    summary: "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks that include an encoder and a decoder. The best performing models also connect the encoder and decoder through an attention mechanism. We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely.",
    inContext: true
  },
  {
    id: 2,
    title: "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding",
    authors: "Devlin et al.",
    date: "2018",
    type: "PDF",
    summary: "We introduce a new language representation model called BERT, which stands for Bidirectional Encoder Representations from Transformers. Unlike recent language representation models, BERT is designed to pre-train deep bidirectional representations from unlabeled text by jointly conditioning on both left and right context in all layers.",
    inContext: false
  }
])

const addSource = (newSource) => {
  sources.value.push({
    id: Date.now(),
    ...newSource,
    inContext: true
  })
}

// Left Sidebar Toggle
const isLeftSidebarOpen = ref(true)
const toggleLeftSidebar = () => {
  isLeftSidebarOpen.value = !isLeftSidebarOpen.value
}

// Right Sidebar Resizing
const rightSidebarWidth = ref(384) // Default 384px (w-96 equivalent)
const isResizing = ref(false)

const startResizing = () => {
  isResizing.value = true
  document.addEventListener('mousemove', handleMouseMove)
  document.addEventListener('mouseup', stopResizing)
  document.body.style.cursor = 'col-resize'
  document.body.style.userSelect = 'none' // Prevent text selection while dragging
}

  const handleMouseMove = (e) => {
  if (!isResizing.value) return
  const newWidth = window.innerWidth - e.clientX
  
  // Snap to close if less than 100px
  if (newWidth < 100) {
    rightSidebarWidth.value = 0
    return
  }

  // Min width 250px, Max width 800px
  if (newWidth >= 250 && newWidth <= 800) {
    rightSidebarWidth.value = newWidth
  }
}

const stopResizing = () => {
  isResizing.value = false
  document.removeEventListener('mousemove', handleMouseMove)
  document.removeEventListener('mouseup', stopResizing)
  document.body.style.cursor = ''
  document.body.style.userSelect = ''
}

onUnmounted(() => {
  document.removeEventListener('mousemove', handleMouseMove)
  document.removeEventListener('mouseup', stopResizing)
})
</script>

<template>
  <div class="flex flex-col h-screen bg-primary text-slate-900 font-sans">
    <!-- Top Bar -->
    <header class="h-14 border-b border-slate-200 flex items-center px-4 bg-white shrink-0 z-10">
      <button 
        @click="toggleLeftSidebar"
        class="p-2 hover:bg-slate-100 rounded-lg mr-3 text-slate-600 transition-colors"
        :title="isLeftSidebarOpen ? 'Close Sidebar' : 'Open Sidebar'"
      >
        <ChevronLeft v-if="isLeftSidebarOpen" class="w-5 h-5" />
        <ChevronRight v-else class="w-5 h-5" />
      </button>
      
      <div class="flex items-center gap-2">
        <div class="w-8 h-8 bg-accent rounded-lg flex items-center justify-center text-white font-bold shadow-sm">RA</div>
        <h1 class="text-lg font-semibold tracking-wide text-slate-800">Research Agent</h1>
      </div>
    </header>

    <!-- Main Content -->
    <main class="flex-1 flex overflow-hidden relative">
      <!-- Left Column: Conversations -->
      <transition name="slide-fade">
        <aside 
          v-show="isLeftSidebarOpen"
          class="w-64 border-r border-slate-200 bg-slate-50 flex flex-col shrink-0"
        >
          <SidebarLeft />
        </aside>
      </transition>

      <!-- Center Column: Chat -->
      <section class="flex-1 flex flex-col min-w-0 bg-white relative z-0">
        <ChatArea @add-source="addSource" />
      </section>

      <!-- Resizer Handle -->
      <div 
        class="w-1 cursor-col-resize transition-colors z-20 flex items-center justify-center group"
        :class="isResizing ? 'bg-accent' : 'bg-slate-200 hover:bg-accent'"
        @mousedown="startResizing"
      >
        <div class="h-8 w-0.5 rounded-full transition-colors" :class="isResizing ? 'bg-white' : 'bg-slate-300 group-hover:bg-white'"></div>
      </div>

      <!-- Right Column: Sources -->
      <aside 
        class="border-l border-slate-200 bg-slate-50 flex flex-col shrink-0 overflow-hidden"
        :style="{ width: rightSidebarWidth + 'px' }"
      >
        <SidebarRight :sources="sources" />
      </aside>
    </main>
  </div>
</template>

<style scoped>
.slide-fade-enter-active,
.slide-fade-leave-active {
  transition: all 0.3s ease;
}

.slide-fade-enter-from,
.slide-fade-leave-to {
  width: 0;
  opacity: 0;
  transform: translateX(-20px);
}
</style>
