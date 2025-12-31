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
    AlertCircle
} from 'lucide-vue-next'
import { ref, computed } from 'vue'

const props = defineProps({
    verification: { type: Object, required: true }
})

const expanded = ref(false)

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
    return props.verification.hallucination_warnings?.length > 0 ||
           props.verification.link_verification?.some(lv => !lv.result.valid) ||
           props.verification.bibtex_verification?.some(bv => !bv.result.valid)
})

const linkIssuesCount = computed(() => {
    return props.verification.link_verification?.filter(lv => !lv.result.valid).length || 0
})

const bibtexIssuesCount = computed(() => {
    return props.verification.bibtex_verification?.filter(bv => !bv.result.valid).length || 0
})

const hallucinationCount = computed(() => {
    return props.verification.hallucination_warnings?.length || 0
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
                            <span v-if="linkIssuesCount > 0" class="text-xs px-2 py-1 bg-orange-100 text-orange-700 rounded-full flex items-center gap-1">
                                <LinkIcon class="w-3 h-3" />
                                {{ linkIssuesCount }} Link Issue{{ linkIssuesCount !== 1 ? 's' : '' }}
                            </span>
                            <span v-if="bibtexIssuesCount > 0" class="text-xs px-2 py-1 bg-yellow-100 text-yellow-700 rounded-full flex items-center gap-1">
                                <FileText class="w-3 h-3" />
                                {{ bibtexIssuesCount }} BibTeX Issue{{ bibtexIssuesCount !== 1 ? 's' : '' }}
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

        <!-- Detailed Report - Expandable -->
        <div v-if="expanded" class="border-t border-slate-200 bg-white/50 p-4 space-y-4">
            
            <!-- Hallucination Warnings -->
            <div v-if="verification.hallucination_warnings?.length > 0">
                <h5 class="text-sm font-semibold text-slate-800 mb-2 flex items-center gap-2">
                    <AlertCircle class="w-4 h-4 text-red-600" />
                    Hallucination Warnings
                </h5>
                <div class="space-y-2">
                    <div
                        v-for="(warning, idx) in verification.hallucination_warnings"
                        :key="idx"
                        :class="['p-3 rounded border', severityColor(warning.severity)]"
                    >
                        <div class="flex items-start gap-2">
                            <AlertTriangle class="w-4 h-4 shrink-0 mt-0.5" />
                            <div class="flex-1 min-w-0">
                                <div class="flex items-center gap-2 mb-1">
                                    <span class="text-xs font-semibold uppercase">{{ warning.type?.replace('_', ' ') }}</span>
                                    <span class="text-xs px-1.5 py-0.5 bg-white/50 rounded">{{ warning.severity }}</span>
                                </div>
                                <p class="text-sm font-medium">{{ warning.description }}</p>
                                <p class="text-xs mt-1 opacity-90">{{ warning.explanation }}</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Paper Ratings -->
            <div v-if="verification.paper_ratings?.length > 0">
                <h5 class="text-sm font-semibold text-slate-800 mb-2 flex items-center gap-2">
                    <FileText class="w-4 h-4 text-blue-600" />
                    Paper Quality Assessment
                </h5>
                <div class="space-y-2">
                    <div
                        v-for="(rating, idx) in verification.paper_ratings"
                        :key="idx"
                        class="p-3 bg-slate-50 rounded border border-slate-200"
                    >
                        <div class="font-medium text-sm text-slate-800 mb-2">{{ rating.title }}</div>
                        <div class="grid grid-cols-2 gap-3 text-xs">
                            <div>
                                <span class="text-slate-600">Credibility:</span>
                                <span class="ml-1 font-semibold">{{ rating.credibility_score }}/10</span>
                                <p class="text-slate-600 mt-1">{{ rating.credibility_notes }}</p>
                            </div>
                            <div>
                                <span class="text-slate-600">Quality:</span>
                                <span class="ml-1 font-semibold">{{ rating.quality_score }}/10</span>
                                <p class="text-slate-600 mt-1">{{ rating.quality_notes }}</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Link Verification -->
            <div v-if="verification.link_verification?.length > 0">
                <h5 class="text-sm font-semibold text-slate-800 mb-2 flex items-center gap-2">
                    <LinkIcon class="w-4 h-4 text-purple-600" />
                    Link Verification
                </h5>
                <div class="space-y-2">
                    <div
                        v-for="(linkCheck, idx) in verification.link_verification"
                        :key="idx"
                        class="p-3 bg-slate-50 rounded border border-slate-200"
                    >
                        <div class="flex items-start gap-2">
                            <CheckCircle v-if="linkCheck.result.valid" class="w-4 h-4 text-green-600 shrink-0 mt-0.5" />
                            <XCircle v-else class="w-4 h-4 text-red-600 shrink-0 mt-0.5" />
                            <div class="flex-1 min-w-0">
                                <div class="text-sm font-medium text-slate-800 truncate">{{ linkCheck.title }}</div>
                                <div class="text-xs text-slate-600 mt-1 break-all">{{ linkCheck.link || 'No link provided' }}</div>
                                <div v-if="!linkCheck.result.valid" class="text-xs text-red-600 mt-1">
                                    {{ linkCheck.result.reason }}
                                </div>
                                <div v-else class="text-xs text-green-600 mt-1">
                                    ✓ Accessible (HTTP {{ linkCheck.result.status_code }})
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- BibTeX Verification -->
            <div v-if="verification.bibtex_verification?.length > 0">
                <h5 class="text-sm font-semibold text-slate-800 mb-2 flex items-center gap-2">
                    <FileText class="w-4 h-4 text-indigo-600" />
                    BibTeX Verification
                </h5>
                <div class="space-y-2">
                    <div
                        v-for="(bibtexCheck, idx) in verification.bibtex_verification"
                        :key="idx"
                        class="p-3 bg-slate-50 rounded border border-slate-200"
                    >
                        <div class="flex items-start gap-2">
                            <CheckCircle v-if="bibtexCheck.result.valid" class="w-4 h-4 text-green-600 shrink-0 mt-0.5" />
                            <XCircle v-else class="w-4 h-4 text-red-600 shrink-0 mt-0.5" />
                            <div class="flex-1 min-w-0">
                                <div class="text-sm font-medium text-slate-800">{{ bibtexCheck.title }}</div>
                                <div v-if="!bibtexCheck.result.valid" class="mt-1">
                                    <div class="text-xs text-red-600 font-medium mb-1">Issues found:</div>
                                    <ul class="text-xs text-red-600 list-disc list-inside space-y-0.5">
                                        <li v-for="(issue, issueIdx) in bibtexCheck.result.issues" :key="issueIdx">
                                            {{ issue }}
                                        </li>
                                    </ul>
                                </div>
                                <div v-else class="text-xs text-green-600 mt-1">
                                    ✓ Valid BibTeX format
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

        </div>
    </div>
</template>
