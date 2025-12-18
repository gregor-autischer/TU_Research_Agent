<script setup>
import SidebarLeft from '../components/SidebarLeft.vue'
import ChatArea from '../components/ChatArea.vue'
import SidebarRight from '../components/SidebarRight.vue'
import UserMenu from '../components/UserMenu.vue'
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ChevronLeft, ChevronRight } from 'lucide-vue-next'
import { useConversations } from '../composables/useConversations'
import { usePapers } from '../composables/usePapers'
import { useSettings } from '../composables/useSettings'

const {
    conversations,
    currentConversation,
    isSending,
    fetchConversations,
    createConversation,
    loadConversation,
    updateConversationTitle,
    deleteConversation,
    sendMessage
} = useConversations()

const {
    papers,
    fetchPapers,
    addPaper,
    toggleContext,
    deletePaper
} = usePapers()

const { getSettings } = useSettings()

const messages = computed(() => currentConversation.value?.messages || [])
const conversationId = computed(() => currentConversation.value?.id || null)

onMounted(() => {
    fetchConversations()
    fetchPapers()
})

const handleNewConversation = async () => {
    await createConversation()
}

const handleSelectConversation = async (id) => {
    await loadConversation(id)
}

const handleRenameConversation = async (id, title) => {
    await updateConversationTitle(id, title)
}

const handleDeleteConversation = async (id) => {
    await deleteConversation(id)
}

const handleSendMessage = async (message) => {
    let convId = conversationId.value
    if (!convId) {
        const conv = await createConversation()
        convId = conv.id
    }
    await sendMessage(convId, message, getSettings())
}

const handleAddSource = async (newSource) => {
    await addPaper(newSource)
}

const handleToggleContext = async (id) => {
    await toggleContext(id)
}

const handleDeletePaper = async (id) => {
    await deletePaper(id)
}

// Left Sidebar Toggle
const isLeftSidebarOpen = ref(true)
const toggleLeftSidebar = () => {
    isLeftSidebarOpen.value = !isLeftSidebarOpen.value
}

// Right Sidebar Resizing
const rightSidebarWidth = ref(384)
const isResizing = ref(false)

const startResizing = () => {
    isResizing.value = true
    document.addEventListener('mousemove', handleMouseMove)
    document.addEventListener('mouseup', stopResizing)
    document.body.style.cursor = 'col-resize'
    document.body.style.userSelect = 'none'
}

const handleMouseMove = (e) => {
    if (!isResizing.value) return
    const newWidth = window.innerWidth - e.clientX

    if (newWidth < 100) {
        rightSidebarWidth.value = 0
        return
    }

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
        <header class="h-14 border-b border-slate-200 flex items-center justify-between px-4 bg-white shrink-0 z-10">
            <div class="flex items-center">
                <button @click="toggleLeftSidebar"
                    class="p-2 hover:bg-slate-100 rounded-lg mr-3 text-slate-600 transition-colors"
                    :title="isLeftSidebarOpen ? 'Close Sidebar' : 'Open Sidebar'">
                    <ChevronLeft v-if="isLeftSidebarOpen" class="w-5 h-5" />
                    <ChevronRight v-else class="w-5 h-5" />
                </button>

                <div class="flex items-center gap-2">
                    <div
                        class="w-8 h-8 bg-accent rounded-lg flex items-center justify-center text-white font-bold shadow-sm">
                        RA</div>
                    <h1 class="text-lg font-semibold tracking-wide text-slate-800">Research Agent</h1>
                </div>
            </div>

            <!-- User Menu -->
            <UserMenu />
        </header>

        <!-- Main Content -->
        <main class="flex-1 flex overflow-hidden relative">
            <!-- Left Column: Conversations -->
            <transition name="slide-fade">
                <aside v-show="isLeftSidebarOpen" class="w-64 border-r border-slate-200 bg-slate-50 flex flex-col shrink-0">
                    <SidebarLeft
                        :conversations="conversations"
                        :current-conversation-id="conversationId"
                        @select-conversation="handleSelectConversation"
                        @new-conversation="handleNewConversation"
                        @rename-conversation="handleRenameConversation"
                        @delete-conversation="handleDeleteConversation"
                    />
                </aside>
            </transition>

            <!-- Center Column: Chat -->
            <section class="flex-1 flex flex-col min-w-0 bg-white relative z-0">
                <ChatArea
                    :messages="messages"
                    :conversation-id="conversationId"
                    :is-loading="isSending"
                    @send-message="handleSendMessage"
                    @add-source="handleAddSource"
                />
            </section>

            <!-- Resizer Handle -->
            <div class="w-1 cursor-col-resize transition-colors z-20 flex items-center justify-center group"
                :class="isResizing ? 'bg-accent' : 'bg-slate-200 hover:bg-accent'" @mousedown="startResizing">
                <div class="h-8 w-0.5 rounded-full transition-colors"
                    :class="isResizing ? 'bg-white' : 'bg-slate-300 group-hover:bg-white'"></div>
            </div>

            <!-- Right Column: Sources -->
            <aside class="border-l border-slate-200 bg-slate-50 flex flex-col shrink-0 overflow-hidden"
                :style="{ width: rightSidebarWidth + 'px' }">
                <SidebarRight
                    :sources="papers"
                    @toggle-context="handleToggleContext"
                    @delete-paper="handleDeletePaper"
                />
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
