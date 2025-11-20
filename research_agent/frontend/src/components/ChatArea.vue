<script setup>
import { Send, Plus, Bot, User } from 'lucide-vue-next'
import { ref } from 'vue'

const emit = defineEmits(['add-source'])

const input = ref('')

const sendMessage = () => {
  if (!input.value.trim()) return
  // Mock send
  input.value = ''
}

const addSampleSource = () => {
  emit('add-source', {
    title: "GPT-3: Language Models are Few-Shot Learners",
    authors: "Brown et al.",
    date: "2020",
    type: "PDF",
    summary: "Recent work has demonstrated substantial gains on many NLP tasks and benchmarks by pre-training on a large corpus of text followed by fine-tuning on a specific task. We demonstrate that scaling up language models greatly improves task-agnostic, few-shot performance, sometimes even reaching competitiveness with prior state-of-the-art fine-tuning approaches."
  })
}
</script>

<template>
  <!-- Messages Area -->
  <div class="flex-1 overflow-y-auto p-6 space-y-8">
    
    <!-- User Message -->
    <div class="flex gap-4 max-w-3xl mx-auto">
      <div class="w-8 h-8 rounded-full bg-slate-200 flex items-center justify-center shrink-0">
        <User class="w-5 h-5 text-slate-600" />
      </div>
      <div class="flex-1 space-y-2">
        <div class="font-medium text-slate-700">User</div>
        <div class="text-slate-800 leading-relaxed">
          Can you find some key papers on Transformer architectures and their evolution?
        </div>
      </div>
    </div>

    <!-- AI Response -->
    <div class="flex gap-4 max-w-3xl mx-auto">
      <div class="w-8 h-8 rounded-full bg-accent flex items-center justify-center shrink-0 shadow-sm">
        <Bot class="w-5 h-5 text-white" />
      </div>
      <div class="flex-1 space-y-4">
        <div class="font-medium text-accent">Research Agent</div>
        <div class="text-slate-800 leading-relaxed">
          <p class="mb-4">Here are some foundational papers regarding Transformer architectures:</p>
          
          <!-- Source Recommendation Card -->
          <div class="bg-white border border-slate-200 rounded-lg p-4 hover:border-accent/50 hover:shadow-sm transition-all">
            <div class="flex justify-between items-start gap-4">
              <div>
                <h3 class="font-semibold text-accent mb-1">GPT-3: Language Models are Few-Shot Learners</h3>
                <p class="text-sm text-slate-500 mb-2">Brown et al. • 2020</p>
                <p class="text-sm text-slate-600 line-clamp-2">
                  Demonstrates that scaling up language models greatly improves task-agnostic, few-shot performance.
                </p>
              </div>
              <button 
                @click="addSampleSource"
                class="shrink-0 flex items-center gap-1 text-xs font-medium bg-blue-50 text-accent hover:bg-blue-100 px-3 py-1.5 rounded-full transition-colors"
              >
                <Plus class="w-3 h-3" />
                Add Source
              </button>
            </div>
          </div>

        </div>
      </div>
    </div>

  </div>

  <!-- Input Area -->
  <div class="p-4 border-t border-slate-200 bg-white/95 backdrop-blur">
    <div class="max-w-3xl mx-auto relative">
      <textarea
        v-model="input"
        @keydown.enter.prevent="sendMessage"
        placeholder="Ask a research question..."
        class="w-full bg-slate-50 text-slate-800 border border-slate-200 rounded-xl pl-4 pr-12 py-3 focus:outline-none focus:border-accent focus:ring-1 focus:ring-accent resize-none h-[52px] max-h-32 scrollbar-hide placeholder:text-slate-400"
      ></textarea>
      <button 
        @click="sendMessage"
        class="absolute right-2 top-2 p-1.5 bg-accent hover:bg-blue-700 text-white rounded-lg transition-colors shadow-sm"
      >
        <Send class="w-4 h-4" />
      </button>
    </div>
    <div class="text-center text-xs text-slate-400 mt-2">
      AI can make mistakes. Please verify important information.
    </div>
  </div>
</template>
