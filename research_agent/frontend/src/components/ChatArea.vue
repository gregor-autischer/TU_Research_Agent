<script setup>
import { Send, Bot, User, Loader2, FileText, Plus, ChevronDown, ChevronUp, ExternalLink, ShieldCheck, ListFilter, X } from 'lucide-vue-next'
import { ref, nextTick, watch, computed } from 'vue'
import { marked } from 'marked'
import { useVerification } from '../composables/useVerification'
import PaperVerificationDetails from './PaperVerificationDetails.vue'
import VerificationResults from './VerificationResults.vue'

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

// ... imports
// ... props ...

const input = ref('')
const expandedPapers = ref({})
const expandedVerification = ref({})
const textareaRef = ref(null)
const isMultiLine = ref(false)

// Toggles
const autoValidation = ref(true)
const agentMode = ref(false)

// 5-step agent mode state machine
const AGENT_PHASES = {
    IDLE: 'idle',
    CLARIFYING: 'clarifying',
    USER_INPUT: 'user_input',
    RUNNING: 'running',
    SUMMARY: 'summary'
}
const agentPhase = ref(AGENT_PHASES.IDLE)
const agentStepCount = ref(0)
const agentConversationId = ref(null)
const clarificationInput = ref('')
const collapsedMessages = ref({})  // { messageId: true/false }
const MAX_AGENT_STEPS = 5

// Computed for backward compatibility
const isAgentRunning = computed(() => agentPhase.value !== AGENT_PHASES.IDLE)

// Watch agentMode to force autoValidation on
watch(agentMode, (newVal) => {
    if (newVal) {
        autoValidation.value = true
    }
})

// Reset agent state when conversation changes
watch(() => props.conversationId, () => {
    // Don't reset if this IS the agent conversation
    if (agentConversationId.value !== props.conversationId) {
        // We're switching away - don't show agent UI here
    }
})

// Computed to check if agent/loading applies to THIS conversation
const isActiveConversation = computed(() => {
    return !agentConversationId.value || agentConversationId.value === props.conversationId
})

const showAgentRunning = computed(() => {
    return isAgentRunning.value && agentConversationId.value === props.conversationId
})

// Toggle message collapse
const toggleMessageCollapse = (msgId) => {
    collapsedMessages.value[msgId] = !collapsedMessages.value[msgId]
}

const isMessageCollapsed = (msgId) => {
    return collapsedMessages.value[msgId] || false
}

// Computed for input placeholder
const getInputPlaceholder = computed(() => {
    if (showAgentRunning.value) {
        if (agentPhase.value === AGENT_PHASES.CLARIFYING) return 'Preparing questions...'
        if (agentPhase.value === AGENT_PHASES.RUNNING) return `Agent running... Step ${agentStepCount.value}/${MAX_AGENT_STEPS}`
        if (agentPhase.value === AGENT_PHASES.SUMMARY) return 'Generating summary...'
        return 'Agent processing...'
    }
    return 'Ask a research question...'
})


// ... filters ...

const showFilters = ref(false)
const filters = ref({
    yearStart: '',
    yearEnd: '',
    authors: '',
    domain: ''
})

const activeFilterCount = computed(() => {
    let count = 0
    if (filters.value.yearStart) count++
    if (filters.value.yearEnd) count++
    if (filters.value.authors) count++
    if (filters.value.domain) count++
    return count
})

const clearFilters = () => {
    filters.value = {
        yearStart: '',
        yearEnd: '',
        authors: '',
        domain: ''
    }
    showFilters.value = false
}

// Verification
const { verifying, verificationError, verifyMessage, getVerification } = useVerification()
const verifyingMessageId = ref(null)

const handleVerify = async (messageId) => {
    verifyingMessageId.value = messageId
    try {
        const result = await verifyMessage(messageId)
        
        // Collapse this message since next one will arrive
        if (agentPhase.value === AGENT_PHASES.RUNNING) {
            collapsedMessages.value[messageId] = true
        }
        
        // If agent mode is running and we haven't hit max steps, auto-continue
        if (agentPhase.value === AGENT_PHASES.RUNNING && agentStepCount.value < MAX_AGENT_STEPS) {
            agentStepCount.value++
            
            // Get suggestion from verification
            const suggestion = result?.textual_verification?.next_step_suggestion || 'Please continue the research based on the verification results.'
            
            // Auto-send follow-up message
            emit('send-message', suggestion, { ...filters.value })
        } else if (agentPhase.value === AGENT_PHASES.RUNNING) {
            // Max steps reached, transition to SUMMARY phase
            agentPhase.value = AGENT_PHASES.SUMMARY
            
            // Send final summary prompt
            const summaryPrompt = `Based on all our research steps, please provide a comprehensive final summary that includes:
1. All the high-quality papers we found throughout this research session
2. A summary of the key findings and themes
3. Recommendations for the most important papers to read first
4. Any gaps in the research that could be explored further

Present this as a final research report.`
            emit('send-message', summaryPrompt, { ...filters.value })
        }
    } catch (error) {
        console.error('Verification failed:', error)
        // Stop agent on error
        if (agentPhase.value !== AGENT_PHASES.IDLE) {
            resetAgentState()
        }
    } finally {
        verifyingMessageId.value = null
    }
}

// Helper to reset agent state
const resetAgentState = () => {
    agentPhase.value = AGENT_PHASES.IDLE
    agentStepCount.value = 0
    agentConversationId.value = null
    clarificationInput.value = ''
}

// Watch for loading completion to trigger verification
watch(() => props.isLoading, (newLoading, oldLoading) => {
    if (oldLoading && !newLoading) {
        // Just finished loading
        const lastMessage = props.messages[props.messages.length - 1]
        
        // Handle agent phase transitions
        if (agentPhase.value === AGENT_PHASES.CLARIFYING && lastMessage?.role === 'assistant') {
            // LLM has asked clarification questions, transition to USER_INPUT
            agentPhase.value = AGENT_PHASES.USER_INPUT
            return // Don't verify clarification questions
        }
        
        if (agentPhase.value === AGENT_PHASES.SUMMARY && lastMessage?.role === 'assistant') {
            // Summary is complete, end agent
            resetAgentState()
            return
        }
        
        // If it's an assistant message with structured content (papers)
        if (lastMessage && lastMessage.role === 'assistant' && hasStructuredContent(lastMessage.content)) {
            // Trigger auto-verification only if enabled
            if (autoValidation.value) {
                handleVerify(lastMessage.id)
            }
        }
    }
})

// Helper to get verification status for a specific paper
const getPaperVerificationStatus = (msgId, paperIndex) => {
    // If currently verifying this message, return 'verifying'
    if (verifyingMessageId.value === msgId) return 'verifying'
    
    const verification = getVerification(msgId)
    if (!verification || !verification.paper_verifications) return 'unverified'
    
    // Find verification for this specific paper index
    const paperVer = verification.paper_verifications.find(pv => pv.paper_index === paperIndex)
    if (!paperVer) return 'unverified'
    
    // Check if it's a "bad" paper
    // Criteria: content mismatch OR low credibility OR low overall quality
    const matches = paperVer.content_verification?.matches ?? true
    const credibility = paperVer.credibility_score ?? 10
    const quality = paperVer.overall_quality ?? 10
    
    if (!matches || credibility < 5.0 || quality < 5.0) {
        return 'bad'
    }
    
    return 'good'
}

const getPaperVerificationData = (msgId, paperIndex) => {
    const verification = getVerification(msgId)
    if (!verification || !verification.paper_verifications) return null
    return verification.paper_verifications.find(pv => pv.paper_index === paperIndex)
}

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
    if (!input.value.trim() || props.isLoading || showAgentRunning.value) return
    
    const messageContent = input.value.trim()
    
    // Start agent mode if enabled - begin with CLARIFYING phase
    if (agentMode.value && agentPhase.value === AGENT_PHASES.IDLE) {
        agentPhase.value = AGENT_PHASES.CLARIFYING
        agentConversationId.value = props.conversationId
        
        // Send clarification prompt
        const clarificationPrompt = `The user wants to research: "${messageContent}"

Before I start the deep research process, I need to understand their needs better. Please ask 2-3 clarifying questions about:
1. What specific aspects of this topic are most important to them?
2. What is their background knowledge level?
3. Are there any specific applications, time periods, or sub-fields they want to focus on?
4. What is the purpose of this research (paper, project, learning, etc.)?

Ask these questions conversationally and wait for their response.`
        
        emit('send-message', clarificationPrompt, { ...filters.value })
    } else {
        emit('send-message', messageContent, { ...filters.value })
    }
    
    input.value = ''
    isMultiLine.value = false
    nextTick(() => {
        if (textareaRef.value) {
            textareaRef.value.style.height = '52px'
        }
    })
}

// Handle clarification submission
const handleClarificationSubmit = () => {
    if (!clarificationInput.value.trim() || props.isLoading) return
    
    // Collapse the clarification question (last message)
    const lastMessage = props.messages[props.messages.length - 1]
    if (lastMessage && lastMessage.role === 'assistant') {
        collapsedMessages.value[lastMessage.id] = true
    }

    // Transition to RUNNING phase
    agentPhase.value = AGENT_PHASES.RUNNING
    agentStepCount.value = 1
    
    // Send user's clarification answers with instruction to begin research
    const researchPrompt = `Here are my answers to your questions: ${clarificationInput.value.trim()}

Now please begin the deep research process. Find relevant high-quality papers and provide detailed analysis.`
    
    emit('send-message', researchPrompt, { ...filters.value })
    clarificationInput.value = ''
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
    // Clean close verification if opening summary
    expandedVerification.value[key] = false
    expandedPapers.value[key] = !expandedPapers.value[key]
}

const isPaperExpanded = (msgId, paperIndex) => {
    return expandedPapers.value[`${msgId}-${paperIndex}`] || false
}

const toggleVerification = (msgId, paperIndex) => {
    const key = `${msgId}-${paperIndex}`
    // Clean close summary if opening verification
    expandedPapers.value[key] = false
    expandedVerification.value[key] = !expandedVerification.value[key]
}

const isVerificationExpanded = (msgId, paperIndex) => {
    return expandedVerification.value[`${msgId}-${paperIndex}`] || false
}
</script>

<template>
  <!-- Messages Area -->
  <div class="flex-1 overflow-y-auto p-6 space-y-8">

    <!-- Controls Header (scrolls with content) -->
    <div class="flex items-center justify-end gap-6 max-w-3xl mx-auto pb-4 border-b border-slate-100">
        <!-- Auto Validation -->
        <label class="flex items-center gap-2 cursor-pointer select-none">
            <div class="relative">
               <input type="checkbox" v-model="autoValidation" class="sr-only peer">
               <div class="w-9 h-5 bg-slate-200 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-indigo-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-indigo-600"></div>
            </div>
            <span class="text-sm font-medium text-slate-600">Auto Validation</span>
        </label>

        <!-- Agent Mode -->
        <label class="flex items-center gap-2 cursor-pointer select-none">
            <div class="relative">
               <input type="checkbox" v-model="agentMode" class="sr-only peer">
               <div class="w-9 h-5 bg-slate-200 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-indigo-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-indigo-600"></div>
            </div>
            <span class="text-sm font-medium text-slate-600">Five-step Agent Mode</span>
        </label>
    </div>

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
          <div class="flex items-center justify-between">
            <div class="font-medium text-accent">Research Agent</div>
            <!-- Collapse Toggle Button -->
            <button 
              @click="toggleMessageCollapse(msg.id)"
              class="text-slate-400 hover:text-slate-600 transition-colors p-1 rounded"
              :title="isMessageCollapsed(msg.id) ? 'Expand' : 'Collapse'"
            >
              <ChevronUp v-if="!isMessageCollapsed(msg.id)" class="w-4 h-4" />
              <ChevronDown v-else class="w-4 h-4" />
            </button>
          </div>

          <!-- Collapsible Content -->
          <div v-show="!isMessageCollapsed(msg.id)">
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
                class="bg-white border rounded-lg shadow-sm hover:shadow-md transition-all duration-300"
                :class="{
                    'opacity-60 grayscale': getPaperVerificationStatus(msg.id, pIndex) === 'verifying',
                    'border-slate-200': getPaperVerificationStatus(msg.id, pIndex) === 'unverified',
                    'border-green-200 bg-green-50/30': getPaperVerificationStatus(msg.id, pIndex) === 'good',
                    'border-red-200 bg-red-50': getPaperVerificationStatus(msg.id, pIndex) === 'bad'
                }"
              >
                <!-- Paper Header -->
                <div class="p-4">
                  <div class="flex items-start gap-3">
                    <div class="mt-0.5 shrink-0" :class="{
                        'text-slate-400': getPaperVerificationStatus(msg.id, pIndex) === 'unverified' || getPaperVerificationStatus(msg.id, pIndex) === 'verifying',
                        'text-green-500': getPaperVerificationStatus(msg.id, pIndex) === 'good',
                        'text-red-500': getPaperVerificationStatus(msg.id, pIndex) === 'bad'
                    }">
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
                        
                        <!-- Status Badge -->
                        <span v-if="getPaperVerificationStatus(msg.id, pIndex) === 'verifying'" class="flex items-center gap-1 text-slate-400">
                            <Loader2 class="w-3 h-3 animate-spin" /> Verifying
                        </span>
                        <span v-else-if="getPaperVerificationStatus(msg.id, pIndex) === 'bad'" class="text-red-500 font-medium">
                            Low Credibility / Issues
                        </span>
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

                  <!-- Item Actions (Summary & Verification) -->
                  <div class="flex items-center gap-3 mt-3">
                      <!-- Summary Toggle -->
                      <button
                        @click="togglePaper(msg.id, pIndex)"
                        class="flex items-center gap-1 text-xs font-medium transition-colors"
                        :class="isPaperExpanded(msg.id, pIndex) ? 'text-accent' : 'text-slate-500 hover:text-slate-700'"
                      >
                        <span>Summary</span>
                        <ChevronUp v-if="isPaperExpanded(msg.id, pIndex)" class="w-3.5 h-3.5" />
                        <ChevronDown v-else class="w-3.5 h-3.5" />
                      </button>

                      <!-- Verification Toggle (Only if verified) -->
                      <button
                        v-if="getPaperVerificationData(msg.id, pIndex)"
                        @click="toggleVerification(msg.id, pIndex)"
                        class="flex items-center gap-1 text-xs font-medium transition-colors"
                        :class="isVerificationExpanded(msg.id, pIndex) ? 'text-accent' : 'text-slate-500 hover:text-slate-700'"
                      >
                        <span>Verification</span>
                        <ChevronUp v-if="isVerificationExpanded(msg.id, pIndex)" class="w-3.5 h-3.5" />
                        <ChevronDown v-else class="w-3.5 h-3.5" />
                      </button>
                  </div>
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

                <!-- Expanded Verification Details -->
                <div v-if="isVerificationExpanded(msg.id, pIndex)">
                    <PaperVerificationDetails 
                        :verification="getPaperVerificationData(msg.id, pIndex)"
                    />
                </div>
              </div>
            </div>
          </template>

          <!-- Plain text fallback -->
          <div v-else class="prose prose-slate max-w-none" v-html="renderMarkdown(msg.content)"></div>

          <!-- Message Footer Verification Status -->
          <div class="flex items-center gap-2 mt-2" v-if="verifyingMessageId === msg.id">
            <Loader2 class="w-4 h-4 text-accent animate-spin" />
            <span class="text-xs text-slate-500 font-medium">Verifying sources and content authenticity...</span>
          </div>

          <!-- Verification Results (General) -->
          <VerificationResults
            v-if="getVerification(msg.id)"
            :verification="getVerification(msg.id)"
          />

          <!-- Manual Verify Button -->
          <div v-else-if="msg.role === 'assistant' && !verifyingMessageId && hasStructuredContent(msg.content) && !autoValidation" class="mt-4">
            <button 
                @click="handleVerify(msg.id)"
                class="flex items-center gap-2 px-4 py-2 bg-indigo-50 text-indigo-700 rounded-lg hover:bg-indigo-100 transition-colors text-sm font-medium"
            >
                <ShieldCheck class="w-4 h-4" />
                Verify Response
            </button>
          </div>
          </div>  <!-- Close collapsible content -->
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
  <div class="p-4 border-t border-slate-200 bg-white/95 backdrop-blur relative">
    <!-- Filter Popover -->
    <div v-if="showFilters" class="absolute bottom-full left-4 mb-2 w-80 bg-white rounded-xl shadow-lg border border-slate-200 p-4 z-20">
        <div class="flex items-center justify-between mb-3">
            <h3 class="font-semibold text-slate-700 text-sm">Search Filters</h3>
            <button @click="showFilters = false" class="text-slate-400 hover:text-slate-600">
                <X class="w-4 h-4" />
            </button>
        </div>
        
        <div class="space-y-3">
            <!-- Year Range -->
            <div>
                <label class="block text-xs font-medium text-slate-500 mb-1">Year Range</label>
                <div class="flex gap-2">
                    <input v-model="filters.yearStart" type="number" placeholder="Start" class="w-full px-3 py-1.5 text-sm border border-slate-200 rounded-lg focus:outline-none focus:border-accent" />
                    <input v-model="filters.yearEnd" type="number" placeholder="End" class="w-full px-3 py-1.5 text-sm border border-slate-200 rounded-lg focus:outline-none focus:border-accent" />
                </div>
            </div>
            
            <!-- Authors -->
            <div>
                <label class="block text-xs font-medium text-slate-500 mb-1">Authors/Venue</label>
                <input v-model="filters.authors" type="text" placeholder="e.g. Smith, Nature..." class="w-full px-3 py-1.5 text-sm border border-slate-200 rounded-lg focus:outline-none focus:border-accent" />
            </div>

             <!-- Domain/Topic -->
            <div>
                <label class="block text-xs font-medium text-slate-500 mb-1">Specific Domain</label>
                <input v-model="filters.domain" type="text" placeholder="e.g. Machine Learning..." class="w-full px-3 py-1.5 text-sm border border-slate-200 rounded-lg focus:outline-none focus:border-accent" />
            </div>

            <!-- Clear -->
             <div class="pt-2 flex justify-end">
                <button @click="clearFilters" class="text-xs text-slate-500 hover:text-red-500 transition-colors">
                    Clear Filters
                </button>
             </div>
        </div>
    </div>

    <div class="max-w-3xl mx-auto relative flex items-start gap-2">
      <!-- Filter Button (only show when not in agent phases) -->
      <button 
        v-if="agentPhase === AGENT_PHASES.IDLE"
        @click="showFilters = !showFilters"
        class="mt-3 p-2 rounded-lg transition-colors relative"
        :class="activeFilterCount > 0 ? 'bg-accent/10 text-accent' : 'text-slate-400 hover:text-slate-600 hover:bg-slate-100'"
        title="Search Filters"
      >
        <ListFilter class="w-5 h-5" />
        <span v-if="activeFilterCount > 0" class="absolute -top-1 -right-1 w-4 h-4 bg-accent text-white text-[10px] font-bold rounded-full flex items-center justify-center border-2 border-white">
            {{ activeFilterCount }}
        </span>
      </button>

      <!-- Clarification Input (USER_INPUT phase) -->
      <template v-if="agentPhase === AGENT_PHASES.USER_INPUT && agentConversationId === props.conversationId">
        <textarea
          v-model="clarificationInput"
          @keydown.enter.exact.prevent="handleClarificationSubmit"
          placeholder="Answer the questions above to guide your research..."
          class="flex-1 bg-indigo-50 text-slate-800 border-2 border-indigo-300 rounded-xl pl-4 pr-4 py-3 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 resize-none overflow-y-auto scrollbar-hide placeholder:text-slate-400"
          style="min-height: 72px; max-height: 168px;"
          rows="2"
          :disabled="isLoading"
        ></textarea>
        <button
          @click="handleClarificationSubmit"
          :disabled="isLoading || !clarificationInput.trim()"
          class="px-4 py-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl font-medium transition-all shadow-sm disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
        >
          <Send class="w-4 h-4" />
          Start Research
        </button>
      </template>

      <!-- Normal Input (IDLE or not this conversation) -->
      <template v-else>
        <textarea
          ref="textareaRef"
          v-model="input"
          @input="adjustTextareaHeight"
          @keydown.enter.exact.prevent="sendMessage"
          :placeholder="getInputPlaceholder"
          class="flex-1 bg-slate-50 text-slate-800 border border-slate-200 rounded-xl pl-4 pr-12 py-3 focus:outline-none focus:border-accent focus:ring-1 focus:ring-accent resize-none overflow-y-auto scrollbar-hide placeholder:text-slate-400"
          style="min-height: 52px; max-height: 168px;"
          rows="1"
          :disabled="isLoading || showAgentRunning"
        ></textarea>
        
        <button
          @click="sendMessage"
          :disabled="isLoading || showAgentRunning || !input.trim()"
          class="absolute right-2 p-1.5 bg-accent hover:bg-blue-700 text-white rounded-lg transition-all shadow-sm disabled:opacity-50 disabled:cursor-not-allowed"
          :style="isMultiLine ? 'top: 8px' : 'top: 50%; transform: translateY(-50%)'"
        >
          <Send class="w-4 h-4" />
        </button>
      </template>
    </div>
    
    <!-- Agent Mode Indicator -->
    <div v-if="showAgentRunning" class="text-center text-sm text-indigo-600 font-medium mt-2 flex items-center justify-center gap-2">
      <Loader2 class="w-4 h-4 animate-spin" />
      <span v-if="agentPhase === AGENT_PHASES.CLARIFYING">Agent preparing clarification questions...</span>
      <span v-else-if="agentPhase === AGENT_PHASES.RUNNING">Five-step Agent: Step {{ agentStepCount }} of {{ MAX_AGENT_STEPS }}</span>
      <span v-else-if="agentPhase === AGENT_PHASES.SUMMARY">Generating final research summary...</span>
      <span v-else>Agent processing...</span>
    </div>
    <div v-else-if="agentPhase === AGENT_PHASES.USER_INPUT && agentConversationId === props.conversationId" class="text-center text-sm text-indigo-600 font-medium mt-2">
      Please answer the questions above and click "Start Research"
    </div>
    <div v-else class="text-center text-xs text-slate-400 mt-2">
      AI can make mistakes. Please verify important information.
    </div>
  </div>
</template>


