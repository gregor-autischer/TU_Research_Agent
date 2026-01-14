<script setup>
import { 
    CheckCircle, 
    AlertTriangle, 
    XCircle, 
    ChevronDown, 
    ChevronUp,
    Shield,
    Link as LinkIcon,
    FileText,
    AlertCircle,
    BookOpen,
    ExternalLink
} from 'lucide-vue-next'
import { ref, computed } from 'vue'

const props = defineProps({
    verification: { type: Object, required: true }
})

const expanded = ref(false)

// Access textual_verification data
const textualVerification = computed(() => props.verification.textual_verification || {})
const paperVerifications = computed(() => props.verification.paper_verifications || [])

const confidenceColor = computed(() => {
    const score = props.verification.confidence_score
    if (score >= 80) return 'text-green-600'
    if (score >= 60) return 'text-yellow-600'
    return 'text-red-600'
})

const confidenceBgColor = computed(() => {
    const score = props.verification.confidence_score
    if (score >= 80) return 'bg-green-50 border-green-200'
    if (score >= 60) return 'bg-yellow-50 border-yellow-200'
    return 'bg-red-50 border-red-200'
})

const hasIssues = computed(() => {
    const warnings = textualVerification.value.hallucination_warnings?.length > 0
    const lowQualityPapers = paperVerifications.value.some(pv => pv.overall_quality < 4)
    const contentMismatches = paperVerifications.value.some(pv => !pv.content_verification?.matches)
    return warnings || lowQualityPapers || contentMismatches
})

const hallucinationCount = computed(() => {
    return textualVerification.value.hallucination_warnings?.length || 0
})

const paperIssuesCount = computed(() => {
    return paperVerifications.value.filter(pv => 
        !pv.content_verification?.matches || pv.overall_quality < 4
    ).length || 0
})

const severityColor = (severity) => {
    switch (severity) {
        case 'high': return 'text-red-600 bg-red-50'
        case 'medium': return 'text-yellow-600 bg-yellow-50'
        case 'low': return 'text-blue-600 bg-blue-50'
        default: return 'text-gray-600 bg-gray-50'
    }
}
</script>

<template>
    <div :class="['mt-4 rounded-lg border-2 overflow-hidden', confidenceBgColor]">
        <!-- Header - Always Visible -->
        <div class="p-4">
            <div class="flex items-start justify-between gap-4">
                <div class="flex items-start gap-3 flex-1">
                    <Shield :class="['w-5 h-5 mt-0.5 shrink-0', confidenceColor]" />
                    <div class="flex-1 min-w-0">
                        <div class="flex items-center gap-2 mb-1">
                            <h4 class="font-semibold text-slate-800">Verification Report</h4>
                            <span :class="['text-sm font-bold px-2 py-0.5 rounded', confidenceColor]">
                                {{ Math.round(verification.confidence_score) }}%
                            </span>
                        </div>
                        <p class="text-sm text-slate-700 leading-relaxed">{{ verification.summary }}</p>
                        
                        <!-- Quick Issues Summary -->
                        <div v-if="hasIssues" class="flex flex-wrap gap-2 mt-2">
                            <span v-if="hallucinationCount > 0" class="text-xs px-2 py-1 bg-red-100 text-red-700 rounded-full flex items-center gap-1">
                                <AlertCircle class="w-3 h-3" />
                                {{ hallucinationCount }} Warning{{ hallucinationCount !== 1 ? 's' : '' }}
                            </span>
                            <span v-if="paperIssuesCount > 0" class="text-xs px-2 py-1 bg-orange-100 text-orange-700 rounded-full flex items-center gap-1">
                                <FileText class="w-3 h-3" />
                                {{ paperIssuesCount }} Paper Issue{{ paperIssuesCount !== 1 ? 's' : '' }}
                            </span>
                        </div>
                    </div>
                </div>
                
                <button
                    @click="expanded = !expanded"
                    class="flex items-center gap-1 px-3 py-1.5 text-xs font-medium text-slate-600 hover:text-slate-800 hover:bg-white/50 rounded transition-colors shrink-0"
                >
                    <span>{{ expanded ? 'Less' : 'Details' }}</span>
                    <ChevronUp v-if="expanded" class="w-4 h-4" />
                    <ChevronDown v-else class="w-4 h-4" />
                </button>
            </div>
        </div>

        <div v-if="expanded" class="border-t border-slate-200 bg-white/50 p-4 space-y-4">

            <!-- Hallucination Warnings (Only if present) -->
            <div v-if="textualVerification.hallucination_warnings?.length > 0">
                <h5 class="text-xs font-semibold uppercase text-red-600 mb-2 flex items-center gap-2">
                    <AlertTriangle class="w-3.5 h-3.5" />
                    Critical Warnings
                </h5>
                <div class="space-y-2">
                    <div
                        v-for="(warning, idx) in textualVerification.hallucination_warnings"
                        :key="idx"
                        class="p-2.5 rounded bg-red-50 border border-red-100 text-sm"
                    >
                        <div class="font-medium text-red-800">{{ warning.description }}</div>
                        <div class="text-xs text-red-600 mt-0.5">{{ warning.explanation }}</div>
                    </div>
                </div>
            </div>

            <!-- Analysis & Scores -->
            <div>
                <h5 class="text-xs font-semibold uppercase text-slate-500 mb-3 flex items-center gap-2">
                    <Shield class="w-3.5 h-3.5" />
                    Quality Analysis
                </h5>

                <div class="grid grid-cols-2 gap-4 mb-3">
                    <!-- Response Score -->
                    <div class="bg-slate-50 p-2 rounded border border-slate-100">
                        <div class="text-xs text-slate-500 mb-1">Response Quality</div>
                        <div class="font-semibold text-slate-700">
                            {{ textualVerification.response_quality?.score || '-' }}/10
                        </div>
                    </div>
                    <!-- Accuracy Score -->
                    <div class="bg-slate-50 p-2 rounded border border-slate-100">
                        <div class="text-xs text-slate-500 mb-1">Accuracy Score</div>
                        <div class="font-semibold text-slate-700">
                            {{ textualVerification.accuracy_assessment?.score || '-' }}/10
                        </div>
                    </div>
                </div>

                <!-- Notes -->
                <div class="text-sm text-slate-600 space-y-2">
                    <p v-if="textualVerification.response_quality?.notes">
                        <span class="font-medium text-slate-700">Quality:</span> 
                        {{ textualVerification.response_quality.notes }}
                    </p>
                    <p v-if="textualVerification.accuracy_assessment?.notes">
                        <span class="font-medium text-slate-700">Accuracy:</span>
                        {{ textualVerification.accuracy_assessment.notes }}
                    </p>
                </div>

                <!-- Factual Errors -->
                <div v-if="textualVerification.accuracy_assessment?.factual_errors?.length > 0" class="mt-3">
                    <div class="text-xs font-semibold text-red-600 mb-1">Detected Issues:</div>
                    <ul class="list-disc list-inside text-xs text-red-600 space-y-0.5">
                        <li v-for="(error, idx) in textualVerification.accuracy_assessment.factual_errors" :key="idx">
                            {{ error }}
                        </li>
                    </ul>
                </div>
            </div>

        </div>
    </div>
</template>
