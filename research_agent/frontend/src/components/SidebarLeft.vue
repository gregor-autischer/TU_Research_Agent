<script setup>
import { MessageSquarePlus, MessageSquare } from 'lucide-vue-next'
</script>

<template>
  <div class="p-4">
    <button class="w-full flex items-center gap-2 bg-accent hover:bg-blue-700 text-white px-4 py-2 rounded-md transition-colors mb-6 shadow-sm">
      <MessageSquarePlus class="w-4 h-4" />
      <span>New Chat</span>
    </button>

    <div class="space-y-2">
      <div class="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3">Recent</div>
      
      <!-- Boilerplate Conversation -->
      <div class="group flex items-center gap-3 p-3 rounded-lg bg-white border border-slate-200 hover:border-accent/50 hover:shadow-sm cursor-pointer transition-all">
        <MessageSquare class="w-4 h-4 text-slate-400 group-hover:text-accent transition-colors" />
        <div class="flex-1 overflow-hidden">
          <div class="text-sm font-medium text-slate-700 truncate">Transformer Architecture Research</div>
          <div class="text-xs text-slate-500 truncate">2 hours ago</div>
        </div>
      </div>

      <div class="group flex items-center gap-3 p-3 rounded-lg hover:bg-white hover:shadow-sm cursor-pointer transition-all">
        <MessageSquare class="w-4 h-4 text-slate-400 group-hover:text-accent transition-colors" />
        <div class="flex-1 overflow-hidden">
          <div class="text-sm font-medium text-slate-600 truncate">LLM Evaluation Metrics</div>
          <div class="text-xs text-slate-500 truncate">Yesterday</div>
        </div>
      </div>
    </div>
  </div>
</template>
