<script setup>
import { Send, Bot, User, Loader2 } from 'lucide-vue-next'
import { ref } from 'vue'

const props = defineProps({
    messages: { type: Array, default: () => [] },
    conversationId: { type: Number, default: null },
    isLoading: { type: Boolean, default: false }
})

const emit = defineEmits(['send-message', 'add-source'])

const input = ref('')

const sendMessage = () => {
    if (!input.value.trim() || props.isLoading) return
    emit('send-message', input.value.trim())
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

    <!-- Empty State -->
    <div v-if="messages.length === 0" class="flex items-center justify-center h-full">
      <div class="text-center text-slate-400">
        <Bot class="w-12 h-12 mx-auto mb-4 opacity-50" />
        <p>Ask a research question to get started</p>
      </div>
    </div>

    <!-- Messages -->
    <template v-for="(msg, index) in messages" :key="msg.id || index">
      <!-- User Message -->
      <div v-if="msg.role === 'user'" class="flex gap-4 max-w-3xl mx-auto">
        <div class="w-8 h-8 rounded-full bg-slate-200 flex items-center justify-center shrink-0">
          <User class="w-5 h-5 text-slate-600" />
        </div>
        <div class="flex-1 space-y-2">
          <div class="font-medium text-slate-700">You</div>
          <div class="text-slate-800 leading-relaxed">{{ msg.content }}</div>
        </div>
      </div>

      <!-- AI Response -->
      <div v-else class="flex gap-4 max-w-3xl mx-auto">
        <div class="w-8 h-8 rounded-full bg-accent flex items-center justify-center shrink-0 shadow-sm">
          <Bot class="w-5 h-5 text-white" />
        </div>
        <div class="flex-1 space-y-4">
          <div class="font-medium text-accent">Research Agent</div>
          <div class="text-slate-800 leading-relaxed whitespace-pre-wrap">{{ msg.content }}</div>
        </div>
      </div>
    </template>

    <!-- Loading Indicator -->
    <div v-if="isLoading" class="flex gap-4 max-w-3xl mx-auto">
      <div class="w-8 h-8 rounded-full bg-accent flex items-center justify-center shrink-0 shadow-sm">
        <Loader2 class="w-5 h-5 text-white animate-spin" />
      </div>
      <div class="flex-1 space-y-4">
        <div class="font-medium text-accent">Research Agent</div>
        <div class="text-slate-400">Thinking...</div>
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
        :disabled="isLoading"
      ></textarea>
      <button
        @click="sendMessage"
        :disabled="isLoading || !input.trim()"
        class="absolute right-2 top-2 p-1.5 bg-accent hover:bg-blue-700 text-white rounded-lg transition-colors shadow-sm disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <Send class="w-4 h-4" />
      </button>
    </div>
    <div class="text-center text-xs text-slate-400 mt-2">
      AI can make mistakes. Please verify important information.
    </div>
  </div>
</template>
