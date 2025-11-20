<script setup>
import { MessageSquarePlus, MessageSquare } from 'lucide-vue-next'
</script>

<template>
  <div class="flex flex-col h-full">
    <div class="p-4">
      <button class="w-full flex items-center gap-2 bg-accent hover:bg-blue-700 text-white px-4 py-2 rounded-md transition-colors shadow-sm mb-2">
        <MessageSquarePlus class="w-4 h-4" />
        <span>New Research Direction</span>
      </button>
    </div>
    <div class="flex-1 overflow-y-auto bg-white">
      <div class="px-4 py-2 text-[10px] font-bold text-slate-400 uppercase tracking-wider bg-slate-50 border-b border-slate-100">Recent</div>
      
      <!-- Boilerplate Conversation -->
      <div class="group flex items-start gap-3 p-3 border-b border-slate-100 hover:bg-slate-50 cursor-pointer transition-colors">
        <MessageSquare class="w-4 h-4 text-slate-400 mt-0.5 group-hover:text-accent transition-colors" />
        <div class="flex-1 min-w-0">
          <div class="flex items-center justify-between mb-0.5">
            <div class="text-sm font-medium text-slate-700 truncate pr-2">Transformer Architecture Research</div>
            <span class="text-[10px] text-slate-400 whitespace-nowrap">2h</span>
          </div>
          <div class="text-xs text-slate-500 truncate">Discussion about attention mechanisms...</div>
        </div>
      </div>

      <div class="group flex items-start gap-3 p-3 border-b border-slate-100 hover:bg-slate-50 cursor-pointer transition-colors">
        <MessageSquare class="w-4 h-4 text-slate-400 mt-0.5 group-hover:text-accent transition-colors" />
        <div class="flex-1 min-w-0">
          <div class="flex items-center justify-between mb-0.5">
            <div class="text-sm font-medium text-slate-700 truncate pr-2">LLM Evaluation Metrics</div>
            <span class="text-[10px] text-slate-400 whitespace-nowrap">1d</span>
          </div>
          <div class="text-xs text-slate-500 truncate">Comparing BLEU vs ROUGE scores...</div>
        </div>
      </div>
    </div>
  </div>
</template>
