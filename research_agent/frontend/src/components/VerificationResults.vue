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

        <!-- Detailed Report - Expandable -->
        <div v-if="expanded" class="border-t border-slate-200 bg-white/50 p-4 space-y-4">

            <!-- Hallucination Warnings -->
            <div>
                <h5 class="text-sm font-semibold text-slate-800 mb-2 flex items-center gap-2">
                    <AlertCircle class="w-4 h-4 text-red-600" />
                    Hallucination Warnings
                </h5>
                <div v-if="!textualVerification.hallucination_warnings || textualVerification.hallucination_warnings.length === 0" class="text-xs text-slate-500 italic">
                    No hallucination warnings detected
                </div>
                <div v-else class="space-y-2">
                    <div
                        v-for="(warning, idx) in textualVerification.hallucination_warnings"
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

            <!-- Response Quality Assessment -->
            <div>
                <h5 class="text-sm font-semibold text-slate-800 mb-2 flex items-center gap-2">
                    <CheckCircle class="w-4 h-4 text-blue-600" />
                    Response Quality
                </h5>
                <div v-if="!textualVerification.response_quality" class="text-xs text-slate-500 italic">
                    Response quality assessment not available
                </div>
                <div v-else class="p-3 bg-slate-50 rounded border border-slate-200">
                    <div class="grid grid-cols-2 gap-3 text-xs mb-2">
                        <div>
                            <span class="text-slate-600">Addresses Question:</span>
                            <span class="ml-1 font-semibold">{{ textualVerification.response_quality.addresses_question ? '✓ Yes' : '✗ No' }}</span>
                        </div>
                        <div>
                            <span class="text-slate-600">Clear & Helpful:</span>
                            <span class="ml-1 font-semibold">{{ textualVerification.response_quality.clear_and_helpful ? '✓ Yes' : '✗ No' }}</span>
                        </div>
                        <div>
                            <span class="text-slate-600">Follows Instructions:</span>
                            <span class="ml-1 font-semibold">{{ textualVerification.response_quality.follows_instructions ? '✓ Yes' : '✗ No' }}</span>
                        </div>
                        <div>
                            <span class="text-slate-600">Score:</span>
                            <span class="ml-1 font-semibold">{{ textualVerification.response_quality.score }}/10</span>
                        </div>
                    </div>
                    <p class="text-xs text-slate-600">{{ textualVerification.response_quality.notes }}</p>
                </div>
            </div>

            <!-- Accuracy Assessment -->
            <div>
                <h5 class="text-sm font-semibold text-slate-800 mb-2 flex items-center gap-2">
                    <Shield class="w-4 h-4 text-green-600" />
                    Accuracy Assessment
                </h5>
                <div v-if="!textualVerification.accuracy_assessment" class="text-xs text-slate-500 italic">
                    Accuracy assessment not available
                </div>
                <div v-else class="p-3 bg-slate-50 rounded border border-slate-200">
                    <div class="grid grid-cols-2 gap-3 text-xs mb-2">
                        <div>
                            <span class="text-slate-600">Claims Supported:</span>
                            <span class="ml-1 font-semibold">{{ textualVerification.accuracy_assessment.claims_supported ? '✓ Yes' : '✗ No' }}</span>
                        </div>
                        <div>
                            <span class="text-slate-600">Summaries Accurate:</span>
                            <span class="ml-1 font-semibold">{{ textualVerification.accuracy_assessment.summaries_accurate ? '✓ Yes' : '✗ No' }}</span>
                        </div>
                        <div>
                            <span class="text-slate-600">Papers Cited Correctly:</span>
                            <span class="ml-1 font-semibold">{{ textualVerification.accuracy_assessment.papers_cited_correctly ? '✓ Yes' : '✗ No' }}</span>
                        </div>
                        <div>
                            <span class="text-slate-600">Score:</span>
                            <span class="ml-1 font-semibold">{{ textualVerification.accuracy_assessment.score }}/10</span>
                        </div>
                    </div>
                    <p class="text-xs text-slate-600 mb-1">{{ textualVerification.accuracy_assessment.notes }}</p>
                    <div v-if="textualVerification.accuracy_assessment.factual_errors?.length > 0" class="mt-2">
                        <div class="text-xs text-red-600 font-medium mb-1">Factual Errors:</div>
                        <ul class="text-xs text-red-600 list-disc list-inside space-y-0.5">
                            <li v-for="(error, idx) in textualVerification.accuracy_assessment.factual_errors" :key="idx">
                                {{ error }}
                            </li>
                        </ul>
                    </div>
                </div>
            </div>

            <!-- Paper Verifications -->
            <div>
                <h5 class="text-sm font-semibold text-slate-800 mb-2 flex items-center gap-2">
                    <BookOpen class="w-4 h-4 text-purple-600" />
                    Paper Verifications ({{ paperVerifications.length }})
                </h5>
                <div v-if="paperVerifications.length === 0" class="text-xs text-slate-500 italic">
                    No paper verifications available
                </div>
                <div v-else class="space-y-3">
                    <div
                        v-for="(paper, idx) in paperVerifications"
                        :key="idx"
                        class="p-3 bg-slate-50 rounded border border-slate-200"
                    >
                        <!-- Paper Title and Link -->
                        <div class="flex items-start justify-between gap-2 mb-2">
                            <div class="flex-1 min-w-0">
                                <div class="font-medium text-sm text-slate-800 mb-1">{{ paper.title }}</div>
                                <div class="text-xs text-slate-600">
                                    {{ paper.claimed_authors }} ({{ paper.claimed_date }})
                                </div>
                            </div>
                            <a 
                                v-if="paper.link" 
                                :href="paper.link" 
                                target="_blank" 
                                class="shrink-0 text-blue-600 hover:text-blue-800"
                            >
                                <ExternalLink class="w-4 h-4" />
                            </a>
                        </div>

                        <!-- Content Match Status -->
                        <div v-if="paper.content_verification" class="mb-2">
                            <div class="flex items-center gap-2 text-xs">
                                <CheckCircle v-if="paper.content_verification.matches" class="w-3 h-3 text-green-600" />
                                <XCircle v-else class="w-3 h-3 text-red-600" />
                                <span :class="paper.content_verification.matches ? 'text-green-700' : 'text-red-700'" class="font-medium">
                                    Content {{ paper.content_verification.matches ? 'Verified' : 'Mismatch' }}
                                    ({{ paper.content_verification.confidence }}% confidence)
                                </span>
                            </div>
                            <p class="text-xs text-slate-600 mt-1 ml-5">{{ paper.content_verification.explanation }}</p>
                            <div v-if="paper.content_verification.issues?.length > 0" class="ml-5 mt-1">
                                <ul class="text-xs text-orange-600 list-disc list-inside">
                                    <li v-for="(issue, issueIdx) in paper.content_verification.issues" :key="issueIdx">
                                        {{ issue }}
                                    </li>
                                </ul>
                            </div>
                        </div>

                        <!-- Quality Scores -->
                        <div class="grid grid-cols-2 gap-3 mb-2">
                            <div class="text-xs">
                                <span class="text-slate-600">Credibility:</span>
                                <span class="ml-1 font-semibold">{{ paper.credibility_score }}/10</span>
                                <p class="text-slate-600 mt-0.5">{{ paper.credibility_notes }}</p>
                            </div>
                            <div class="text-xs">
                                <span class="text-slate-600">Quality:</span>
                                <span class="ml-1 font-semibold">{{ paper.overall_quality }}/10</span>
                            </div>
                        </div>

                        <!-- Paper Quality Details -->
                        <div v-if="paper.paper_quality" class="text-xs text-slate-600 mb-2">
                            <p>{{ paper.paper_quality.quality_notes }}</p>
                        </div>

                        <!-- Summary Evaluation -->
                        <div v-if="paper.summary_evaluation" class="mt-2 pt-2 border-t border-slate-200">
                            <div class="flex items-center gap-2 text-xs mb-1">
                                <CheckCircle v-if="paper.summary_evaluation.accurate" class="w-3 h-3 text-green-600" />
                                <AlertTriangle v-else class="w-3 h-3 text-orange-600" />
                                <span class="font-medium">
                                    Summary {{ paper.summary_evaluation.accurate ? 'Accurate' : 'Has Issues' }}
                                    ({{ paper.summary_evaluation.score }}/10)
                                </span>
                            </div>
                            <p class="text-xs text-slate-600 ml-5">{{ paper.summary_evaluation.notes }}</p>
                            <div v-if="paper.summary_evaluation.issues?.length > 0" class="ml-5 mt-1">
                                <ul class="text-xs text-orange-600 list-disc list-inside">
                                    <li v-for="(issue, issueIdx) in paper.summary_evaluation.issues" :key="issueIdx">
                                        {{ issue }}
                                    </li>
                                </ul>
                            </div>
                        </div>

                        <!-- Overall Assessment -->
                        <div v-if="paper.overall_assessment" class="mt-2 pt-2 border-t border-slate-200 text-xs text-slate-700 italic">
                            {{ paper.overall_assessment }}
                        </div>

                        <!-- OpenAlex Data -->
                        <div v-if="paper.openalex_metadata?.success" class="mt-2 pt-2 border-t border-slate-200">
                            <div class="text-xs text-slate-500">
                                <span class="font-medium">OpenAlex:</span>
                                {{ paper.openalex_metadata.cited_by_count }} citations,
                                {{ paper.openalex_metadata.publication_year }},
                                {{ paper.openalex_metadata.authors?.length || 0 }} authors
                                <span v-if="paper.openalex_metadata.venue?.name">
                                    · {{ paper.openalex_metadata.venue.name }}
                                </span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

        </div>
    </div>
</template>
