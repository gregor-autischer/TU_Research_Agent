<script setup>
import { ref } from 'vue'
import { MessageSquarePlus, MessageSquare, Pencil, Trash2, Check, X } from 'lucide-vue-next'

const props = defineProps({
    conversations: { type: Array, default: () => [] },
    currentConversationId: { type: Number, default: null }
})

const emit = defineEmits(['select-conversation', 'new-conversation', 'rename-conversation', 'delete-conversation'])

const editingId = ref(null)
const editingTitle = ref('')

const startEditing = (conv, event) => {
    event.stopPropagation()
    editingId.value = conv.id
    editingTitle.value = conv.title
}

const saveEdit = (event) => {
    event.stopPropagation()
    if (editingTitle.value.trim()) {
        emit('rename-conversation', editingId.value, editingTitle.value.trim())
    }
    editingId.value = null
}

const cancelEdit = (event) => {
    event.stopPropagation()
    editingId.value = null
}

const handleDelete = (id, event) => {
    event.stopPropagation()
    if (confirm('Delete this conversation?')) {
        emit('delete-conversation', id)
    }
}

const formatRelativeTime = (dateString) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffMs = now - date
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMs / 3600000)
    const diffDays = Math.floor(diffMs / 86400000)

    if (diffMins < 1) return 'now'
    if (diffMins < 60) return `${diffMins}m`
    if (diffHours < 24) return `${diffHours}h`
    return `${diffDays}d`
}
</script>

<template>
  <div class="flex flex-col h-full">
    <div class="p-4">
      <button
        @click="emit('new-conversation')"
        class="w-full flex items-center gap-2 bg-accent hover:bg-blue-700 text-white px-4 py-2 rounded-md transition-colors shadow-sm mb-2"
      >
        <MessageSquarePlus class="w-4 h-4" />
        <span>New Research Direction</span>
      </button>
    </div>
    <div class="flex-1 overflow-y-auto bg-white">
      <div class="px-4 py-2 text-[10px] font-bold text-slate-400 uppercase tracking-wider bg-slate-50 border-b border-slate-100">Recent</div>

      <!-- Empty State -->
      <div v-if="conversations.length === 0" class="p-4 text-center text-slate-400 text-sm">
        No conversations yet
      </div>

      <!-- Conversation List -->
      <div
        v-for="conv in conversations"
        :key="conv.id"
        @click="emit('select-conversation', conv.id)"
        class="group flex items-start gap-3 p-3 border-b border-slate-100 hover:bg-slate-50 cursor-pointer transition-colors"
        :class="{ 'bg-blue-50 border-l-2 border-l-accent': conv.id === currentConversationId }"
      >
        <MessageSquare class="w-4 h-4 text-slate-400 mt-0.5 group-hover:text-accent transition-colors" :class="{ 'text-accent': conv.id === currentConversationId }" />
        <div class="flex-1 min-w-0">
          <div class="flex items-center justify-between mb-0.5">
            <!-- Editing Mode -->
            <template v-if="editingId === conv.id">
              <input
                v-model="editingTitle"
                @click.stop
                @keydown.enter="saveEdit"
                @keydown.escape="cancelEdit"
                class="flex-1 text-sm font-medium text-slate-700 bg-white border border-slate-300 rounded px-1 py-0.5 focus:outline-none focus:border-accent"
                autofocus
              />
              <div class="flex items-center gap-1 ml-2">
                <button @click="saveEdit" class="p-0.5 text-green-600 hover:bg-green-100 rounded">
                  <Check class="w-3 h-3" />
                </button>
                <button @click="cancelEdit" class="p-0.5 text-slate-400 hover:bg-slate-100 rounded">
                  <X class="w-3 h-3" />
                </button>
              </div>
            </template>
            <!-- Display Mode -->
            <template v-else>
              <div class="text-sm font-medium text-slate-700 truncate pr-2">{{ conv.title }}</div>
              <div class="flex items-center gap-1">
                <span class="text-[10px] text-slate-400 whitespace-nowrap">{{ formatRelativeTime(conv.updated_at) }}</span>
                <button
                  @click="startEditing(conv, $event)"
                  class="p-0.5 text-slate-400 hover:text-accent hover:bg-slate-100 rounded opacity-0 group-hover:opacity-100 transition-opacity"
                >
                  <Pencil class="w-3 h-3" />
                </button>
                <button
                  @click="handleDelete(conv.id, $event)"
                  class="p-0.5 text-slate-400 hover:text-red-500 hover:bg-red-50 rounded opacity-0 group-hover:opacity-100 transition-opacity"
                >
                  <Trash2 class="w-3 h-3" />
                </button>
              </div>
            </template>
          </div>
          <div v-if="editingId !== conv.id" class="text-xs text-slate-500 truncate">{{ conv.preview || 'No messages yet' }}</div>
        </div>
      </div>
    </div>
  </div>
</template>
