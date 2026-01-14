import { ref, readonly } from 'vue'

// Available options
export const MODEL_OPTIONS = [
    { value: 'gpt-5', label: 'GPT-5' },
    { value: 'gpt-5.2', label: 'GPT-5.2' },
]

export const VERBOSITY_OPTIONS = [
    { value: 'minimal', label: 'Minimal' },
    { value: 'normal', label: 'Normal' },
    { value: 'detailed', label: 'Detailed' },
]

export const THINKING_LEVEL_OPTIONS = [
    { value: 'low', label: 'Low' },
    { value: 'medium', label: 'Medium' },
    { value: 'high', label: 'High' },
]

// Shared state
const model = ref('gpt-5.2')
const verbosity = ref('normal')
const thinkingLevel = ref('medium')
const userRole = ref('')
const userKnowledge = ref('')

export function useSettings() {
    const setModel = (value) => {
        model.value = value
    }

    const setVerbosity = (value) => {
        verbosity.value = value
    }

    const setThinkingLevel = (value) => {
        thinkingLevel.value = value
    }

    const setUserRole = (value) => {
        userRole.value = value
    }

    const setUserKnowledge = (value) => {
        userKnowledge.value = value
    }

    const getSettings = () => ({
        model: model.value,
        verbosity: verbosity.value,
        thinking_level: thinkingLevel.value,
        user_role: userRole.value,
        user_knowledge: userKnowledge.value,
        web_search: true, // Always on
    })

    return {
        model: readonly(model),
        verbosity: readonly(verbosity),
        thinkingLevel: readonly(thinkingLevel),
        userRole: readonly(userRole),
        userKnowledge: readonly(userKnowledge),
        setModel,
        setVerbosity,
        setThinkingLevel,
        setUserRole,
        setUserKnowledge,
        getSettings,
        MODEL_OPTIONS,
        VERBOSITY_OPTIONS,
        THINKING_LEVEL_OPTIONS,
    }
}
