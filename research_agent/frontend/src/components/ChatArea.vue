<script setup>
import { Send, Bot, User, Loader2, FileText, Plus, ChevronDown, ChevronUp, ExternalLink } from 'lucide-vue-next'
import { ref, nextTick } from 'vue'
import { marked } from 'marked'

// Configure marked for safe rendering
marked.setOptions({
    breaks: true,
    gfm: true
})

const renderMarkdown = (text) => {
    if (!text) return ''
    return marked.parse(text)
}

const props = defineProps({
    messages: { type: Array, default: () => [] },
    conversationId: { type: Number, default: null },
    isLoading: { type: Boolean, default: false }
})

const emit = defineEmits(['send-message', 'add-source'])

const input = ref('')
const expandedPapers = ref({})
const textareaRef = ref(null)
const isMultiLine = ref(false)

const adjustTextareaHeight = () => {
    const textarea = textareaRef.value
    if (!textarea) return

    // Reset height to auto to get the correct scrollHeight
    textarea.style.height = 'auto'

    // Calculate line height (approx 24px per line)
    const lineHeight = 24
    const maxLines = 7
    const maxHeight = lineHeight * maxLines
    const minHeight = 52

    // Set new height, capped at max
    const newHeight = Math.min(Math.max(textarea.scrollHeight, minHeight), maxHeight)
    textarea.style.height = newHeight + 'px'

    // Track if content exceeds single line
    isMultiLine.value = newHeight > minHeight
}

const sendMessage = () => {
    if (!input.value.trim() || props.isLoading) return
    emit('send-message', input.value.trim())
    input.value = ''
    isMultiLine.value = false
    nextTick(() => {
        if (textareaRef.value) {
            textareaRef.value.style.height = '52px'
        }
    })
}

const addPaperToSources = (paper) => {
    emit('add-source', {
        title: paper.title,
        authors: paper.authors,
        date: paper.date,
        type: paper.type || 'PDF',
        link: paper.link || '',
        summary: paper.summary
    })
}

const parseResponse = (content) => {
    // If content is already an object, return it
    if (typeof content === 'object' && content !== null) {
        return content
    }
    // If content is a JSON string, parse it
    if (typeof content === 'string') {
        try {
            return JSON.parse(content)
        } catch {
            return null
        }
    }
    return null
}

const getTextContent = (content) => {
    const parsed = parseResponse(content)
    return parsed?.text || null
}

const getPapers = (content) => {
    const parsed = parseResponse(content)
    return parsed?.papers || []
}

const hasStructuredContent = (content) => {
    const parsed = parseResponse(content)
    return parsed !== null && (parsed.text || (parsed.papers && parsed.papers.length > 0))
}

const togglePaper = (msgId, paperIndex) => {
    const key = `${msgId}-${paperIndex}`
    expandedPapers.value[key] = !expandedPapers.value[key]
}

const isPaperExpanded = (msgId, paperIndex) => {
    return expandedPapers.value[`${msgId}-${paperIndex}`] || false
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

          <!-- Structured Response (text + papers) -->
          <template v-if="hasStructuredContent(msg.content)">
            <!-- Text Content -->
            <div v-if="getTextContent(msg.content)" class="prose prose-slate max-w-none" v-html="renderMarkdown(getTextContent(msg.content))">
            </div>

            <!-- Papers Grid -->
            <div v-if="getPapers(msg.content).length > 0" class="space-y-3">
              <div
                v-for="(paper, pIndex) in getPapers(msg.content)"
                :key="pIndex"
                class="bg-white border border-slate-200 rounded-lg shadow-sm hover:shadow-md transition-shadow"
              >
                <!-- Paper Header -->
                <div class="p-4">
                  <div class="flex items-start gap-3">
                    <div class="mt-0.5 text-slate-400 shrink-0">
                      <FileText class="w-5 h-5" />
                    </div>
                    <div class="flex-1 min-w-0">
                      <h4 class="font-medium text-slate-800 text-sm leading-tight">
                        {{ paper.title }}
                      </h4>
                      <div class="flex items-center gap-2 mt-1.5 text-xs text-slate-500">
                        <span>{{ paper.authors }}</span>
                        <span class="text-slate-300">•</span>
                        <span>{{ paper.date }}</span>
                      </div>
                    </div>
                    <div class="flex items-center gap-2 shrink-0">
                      <a
                        v-if="paper.link"
                        :href="paper.link"
                        target="_blank"
                        rel="noopener noreferrer"
                        class="flex items-center gap-1 px-2 py-1.5 text-slate-500 hover:text-accent text-xs font-medium transition-colors"
                        title="Open paper"
                      >
                        <ExternalLink class="w-3.5 h-3.5" />
                      </a>
                      <button
                        @click="addPaperToSources(paper)"
                        class="flex items-center gap-1.5 px-3 py-1.5 bg-accent hover:bg-blue-700 text-white text-xs font-medium rounded-lg transition-colors"
                      >
                        <Plus class="w-3.5 h-3.5" />
                        Add
                      </button>
                    </div>
                  </div>

                  <!-- Summary Toggle -->
                  <button
                    @click="togglePaper(msg.id, pIndex)"
                    class="flex items-center gap-1 mt-3 text-xs font-medium text-slate-500 hover:text-slate-700 transition-colors"
                  >
                    <span>Summary</span>
                    <ChevronUp v-if="isPaperExpanded(msg.id, pIndex)" class="w-3.5 h-3.5" />
                    <ChevronDown v-else class="w-3.5 h-3.5" />
                  </button>
                </div>

                <!-- Expanded Summary -->
                <div
                  v-if="isPaperExpanded(msg.id, pIndex)"
                  class="px-4 pb-4"
                >
                  <div class="text-xs text-slate-600 leading-relaxed bg-slate-50 p-3 rounded border border-slate-100">
                    {{ paper.summary }}
                  </div>
                </div>
              </div>
            </div>
          </template>

          <!-- Plain text fallback -->
          <div v-else class="prose prose-slate max-w-none" v-html="renderMarkdown(msg.content)"></div>
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
    <div class="max-w-3xl mx-auto relative flex items-start">
      <textarea
        ref="textareaRef"
        v-model="input"
        @input="adjustTextareaHeight"
        @keydown.enter.exact.prevent="sendMessage"
        placeholder="Ask a research question..."
        class="flex-1 bg-slate-50 text-slate-800 border border-slate-200 rounded-xl pl-4 pr-12 py-3 focus:outline-none focus:border-accent focus:ring-1 focus:ring-accent resize-none overflow-y-auto scrollbar-hide placeholder:text-slate-400"
        style="min-height: 52px; max-height: 168px;"
        rows="1"
        :disabled="isLoading"
      ></textarea>
      <button
        @click="sendMessage"
        :disabled="isLoading || !input.trim()"
        class="absolute right-2 p-1.5 bg-accent hover:bg-blue-700 text-white rounded-lg transition-all shadow-sm disabled:opacity-50 disabled:cursor-not-allowed"
        :style="isMultiLine ? 'top: 8px' : 'top: 50%; transform: translateY(-50%)'"
      >
        <Send class="w-4 h-4" />
      </button>
    </div>
    <div class="text-center text-xs text-slate-400 mt-2">
      AI can make mistakes. Please verify important information.
    </div>
  </div>
</template>
