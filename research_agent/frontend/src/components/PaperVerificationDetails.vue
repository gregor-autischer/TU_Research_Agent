<script setup>
import { Check, X, AlertTriangle, Shield, BookOpen, Award } from 'lucide-vue-next'

const props = defineProps({
  verification: {
    type: Object,
    required: true
  }
})

const getScoreColor = (score) => {
  if (score >= 8) return 'text-green-600'
  if (score >= 5) return 'text-yellow-600'
  return 'text-red-600'
}

const getScoreBg = (score) => {
  if (score >= 8) return 'bg-green-100'
  if (score >= 5) return 'bg-yellow-100'
  return 'bg-red-100'
}
</script>

<template>
  <div class="px-4 pb-4 space-y-4">
    <div class="bg-slate-50 p-4 rounded-lg border border-slate-200 text-sm space-y-4">
      
      <!-- Section 1: Content Authenticity -->
      <div>
        <h5 class="font-medium text-slate-800 mb-2 flex items-center gap-2">
            <Shield class="w-4 h-4 text-slate-500" />
            Content Authenticity
        </h5>
        
        <div class="grid gap-3">
             <!-- Match Status -->
            <div class="flex items-start gap-3 bg-white p-2.5 rounded border border-slate-100">
                <div class="mt-0.5">
                    <Check v-if="verification.content_verification?.matches" class="w-4 h-4 text-green-500" />
                    <X v-else class="w-4 h-4 text-red-500" />
                </div>
                <div>
                    <div class="font-medium text-slate-700">
                        {{ verification.content_verification?.matches ? 'Content Verified' : 'Content Mismatch' }}
                    </div>
                    <p class="text-xs text-slate-500 mt-0.5">
                        {{ verification.content_verification?.explanation || 'No explanation provided.' }}
                    </p>
                    <ul v-if="verification.content_verification?.issues?.length" class="mt-2 text-xs text-red-600 list-disc list-inside">
                        <li v-for="(issue, i) in verification.content_verification.issues" :key="i">{{ issue }}</li>
                    </ul>
                </div>
            </div>
        </div>
      </div>

      <!-- Section 2: Quality & Credibility -->
      <div>
        <h5 class="font-medium text-slate-800 mb-2 flex items-center gap-2">
            <Award class="w-4 h-4 text-slate-500" />
            Quality & Citations
        </h5>
        
        <div class="grid grid-cols-2 gap-3">
             <!-- Credibility Score -->
            <div class="bg-white p-2.5 rounded border border-slate-100">
                <div class="text-xs text-slate-500 mb-1">Credibility Score</div>
                <div class="flex items-end gap-2">
                    <span class="text-xl font-bold" :class="getScoreColor(verification.credibility_score)">
                        {{ verification.credibility_score?.toFixed(1) || 'N/A' }}
                    </span>
                    <span class="text-xs text-slate-400 mb-1">/ 10</span>
                </div>
                <p class="text-xs text-slate-500 mt-1 line-clamp-2" :title="verification.credibility_notes">
                    {{ verification.credibility_notes }}
                </p>
            </div>

            <!-- Quality Score -->
            <div class="bg-white p-2.5 rounded border border-slate-100">
                <div class="text-xs text-slate-500 mb-1">Impact Score</div>
                <div class="flex items-end gap-2">
                    <span class="text-xl font-bold" :class="getScoreColor(verification.overall_quality)">
                        {{ verification.overall_quality?.toFixed(1) || 'N/A' }}
                    </span>
                     <span class="text-xs text-slate-400 mb-1">/ 10</span>
                </div>
                 <p class="text-xs text-slate-500 mt-1">Based on venue & citations</p>
            </div>
        </div>
      </div>

       <!-- Section 3: Summary Accuracy -->
       <div>
        <h5 class="font-medium text-slate-800 mb-2 flex items-center gap-2">
            <BookOpen class="w-4 h-4 text-slate-500" />
            AI Summary Accuracy
        </h5>
         <div class="bg-white p-2.5 rounded border border-slate-100">
             <div class="flex items-center gap-2 mb-1">
                 <span class="text-sm font-medium" :class="verification.summary_evaluation?.accurate ? 'text-green-600' : 'text-red-600'">
                     {{ verification.summary_evaluation?.accurate ? 'Accurate Summary' : 'Inaccurate Summary' }}
                 </span>
             </div>
             <p class="text-xs text-slate-500">
                 {{ verification.summary_evaluation?.notes || 'No notes available.' }}
             </p>
         </div>
       </div>

    </div>
  </div>
</template>
