<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../composables/useAuth'
import { useSettings, MODEL_OPTIONS, VERBOSITY_OPTIONS, THINKING_LEVEL_OPTIONS } from '../composables/useSettings'
import { ArrowLeft, Key, Save, Trash2, Eye, EyeOff, Check, Cpu, MessageSquare, Brain, UserCircle } from 'lucide-vue-next'

const router = useRouter()
const { user, saveApiKey, deleteApiKey, error } = useAuth()
const {
    model,
    verbosity,
    thinkingLevel,
    userRole,
    userKnowledge,
    setModel,
    setVerbosity,
    setThinkingLevel,
    setUserRole,
    setUserKnowledge,
} = useSettings()

const apiKey = ref('')
const showApiKey = ref(false)
const isSubmitting = ref(false)
const successMessage = ref('')

const handleSave = async () => {
    if (!apiKey.value.trim()) return

    isSubmitting.value = true
    successMessage.value = ''

    const success = await saveApiKey(apiKey.value.trim())

    isSubmitting.value = false

    if (success) {
        successMessage.value = 'API key saved successfully!'
        apiKey.value = ''
        setTimeout(() => {
            successMessage.value = ''
        }, 3000)
    }
}

const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete your API key?')) return

    isSubmitting.value = true
    await deleteApiKey()
    isSubmitting.value = false
}

const formatApiKeyPreview = (key) => {
    if (!key || key.length < 6) return key
    return key.substring(0, 6) + '...'
}
</script>

<template>
    <div class="h-screen flex flex-col bg-slate-50 overflow-hidden">
        <!-- Header -->
        <header class="h-14 border-b border-slate-200 flex items-center px-4 bg-white shrink-0 z-10">
            <button @click="router.push('/')"
                class="p-2 hover:bg-slate-100 rounded-lg mr-3 text-slate-600 transition-colors">
                <ArrowLeft class="w-5 h-5" />
            </button>
            <h1 class="text-lg font-semibold text-slate-800">Settings</h1>
        </header>

        <!-- Content -->
        <div class="flex-1 overflow-y-auto">
            <div class="max-w-2xl mx-auto p-6 space-y-6">
                <!-- API Key Section -->
                <div class="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
                    <div class="flex items-center gap-3 mb-4">
                        <div class="w-10 h-10 bg-amber-100 rounded-lg flex items-center justify-center">
                            <Key class="w-5 h-5 text-amber-600" />
                        </div>
                        <div>
                            <h2 class="text-lg font-semibold text-slate-800">OpenAI API Key</h2>
                            <p class="text-sm text-slate-500">Required for chat functionality</p>
                        </div>
                    </div>

                    <!-- Current Status -->
                    <div class="mb-4 p-3 rounded-lg" :class="user?.has_api_key ? 'bg-green-50' : 'bg-amber-50'">
                        <p class="text-sm flex items-center" :class="user?.has_api_key ? 'text-green-700' : 'text-amber-700'">
                            <Check v-if="user?.has_api_key" class="w-4 h-4 mr-1" />
                            <template v-if="user?.has_api_key">
                                API key configured: <span class="font-mono ml-1">{{ formatApiKeyPreview(user?.api_key_preview) }}</span>
                            </template>
                            <template v-else>
                                No API key configured
                            </template>
                        </p>
                    </div>

                    <!-- Success Message -->
                    <div v-if="successMessage" class="mb-4 p-3 bg-green-50 text-green-700 rounded-lg text-sm">
                        {{ successMessage }}
                    </div>

                    <!-- Error Message -->
                    <div v-if="error" class="mb-4 p-3 bg-red-50 text-red-600 rounded-lg text-sm">
                        {{ error }}
                    </div>

                    <!-- API Key Input -->
                    <div class="space-y-4">
                        <div>
                            <label class="block text-sm font-medium text-slate-700 mb-1">
                                {{ user?.has_api_key ? 'Update API Key' : 'Enter API Key' }}
                            </label>
                            <div class="relative">
                                <input v-model="apiKey" :type="showApiKey ? 'text' : 'password'"
                                    class="w-full px-4 py-2 pr-10 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent font-mono text-sm text-slate-800 placeholder:text-slate-400"
                                    placeholder="sk-..." />
                                <button type="button" @click="showApiKey = !showApiKey"
                                    class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600">
                                    <EyeOff v-if="showApiKey" class="w-5 h-5" />
                                    <Eye v-else class="w-5 h-5" />
                                </button>
                            </div>
                            <p class="text-xs text-slate-400 mt-1">
                                Your API key is stored securely and never shared
                            </p>
                        </div>

                        <div class="flex gap-3">
                            <button @click="handleSave" :disabled="!apiKey.trim() || isSubmitting"
                                class="flex-1 bg-accent hover:bg-blue-700 text-white font-medium py-2 rounded-lg transition-colors flex items-center justify-center gap-2 disabled:opacity-50">
                                <Save class="w-4 h-4" />
                                Save API Key
                            </button>

                            <button v-if="user?.has_api_key" @click="handleDelete" :disabled="isSubmitting"
                                class="px-4 py-2 border border-red-200 text-red-600 hover:bg-red-50 rounded-lg transition-colors flex items-center gap-2">
                                <Trash2 class="w-4 h-4" />
                                Delete
                            </button>
                        </div>
                    </div>
                </div>

                <!-- Model Settings Section -->
                <div class="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
                    <div class="flex items-center gap-3 mb-6">
                        <div class="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                            <Cpu class="w-5 h-5 text-blue-600" />
                        </div>
                        <div>
                            <h2 class="text-lg font-semibold text-slate-800">Chat Settings</h2>
                            <p class="text-sm text-slate-500">Configure model and response preferences</p>
                        </div>
                    </div>

                    <div class="space-y-6">
                        <!-- Model Selection -->
                        <div>
                            <label class="block text-sm font-medium text-slate-700 mb-2">
                                Model
                            </label>
                            <div class="grid grid-cols-2 gap-2">
                                <button
                                    v-for="option in MODEL_OPTIONS"
                                    :key="option.value"
                                    @click="setModel(option.value)"
                                    class="px-4 py-2.5 text-sm font-medium rounded-lg border transition-colors"
                                    :class="model === option.value
                                        ? 'bg-accent text-white border-accent'
                                        : 'bg-white text-slate-700 border-slate-200 hover:border-slate-300 hover:bg-slate-50'"
                                >
                                    {{ option.label }}
                                </button>
                            </div>
                        </div>

                        <!-- Verbosity Selection -->
                        <div>
                            <div class="flex items-center gap-2 mb-2">
                                <MessageSquare class="w-4 h-4 text-slate-500" />
                                <label class="block text-sm font-medium text-slate-700">
                                    Verbosity
                                </label>
                            </div>
                            <p class="text-xs text-slate-500 mb-3">Controls how detailed the responses are</p>
                            <div class="flex gap-2">
                                <button
                                    v-for="option in VERBOSITY_OPTIONS"
                                    :key="option.value"
                                    @click="setVerbosity(option.value)"
                                    class="flex-1 px-4 py-2 text-sm font-medium rounded-lg border transition-colors"
                                    :class="verbosity === option.value
                                        ? 'bg-accent text-white border-accent'
                                        : 'bg-white text-slate-700 border-slate-200 hover:border-slate-300 hover:bg-slate-50'"
                                >
                                    {{ option.label }}
                                </button>
                            </div>
                        </div>

                        <!-- Thinking Level Selection -->
                        <div>
                            <div class="flex items-center gap-2 mb-2">
                                <Brain class="w-4 h-4 text-slate-500" />
                                <label class="block text-sm font-medium text-slate-700">
                                    Thinking Level
                                </label>
                            </div>
                            <p class="text-xs text-slate-500 mb-3">Higher levels include more foundational papers and interdisciplinary connections</p>
                            <div class="flex gap-2">
                                <button
                                    v-for="option in THINKING_LEVEL_OPTIONS"
                                    :key="option.value"
                                    @click="setThinkingLevel(option.value)"
                                    class="flex-1 px-4 py-2 text-sm font-medium rounded-lg border transition-colors"
                                    :class="thinkingLevel === option.value
                                        ? 'bg-accent text-white border-accent'
                                        : 'bg-white text-slate-700 border-slate-200 hover:border-slate-300 hover:bg-slate-50'"
                                >
                                    {{ option.label }}
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- User Persona Section -->
                <div class="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
                    <div class="flex items-center gap-3 mb-6">
                        <div class="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                            <UserCircle class="w-5 h-5 text-purple-600" />
                        </div>
                        <div>
                            <h2 class="text-lg font-semibold text-slate-800">User Persona</h2>
                            <p class="text-sm text-slate-500">Help the AI customize answers for you</p>
                        </div>
                    </div>

                    <div class="space-y-4">
                        <!-- User Role -->
                        <div>
                            <label class="block text-sm font-medium text-slate-700 mb-1">
                                Who are you?
                            </label>
                            <input
                                :value="userRole"
                                @input="e => setUserRole(e.target.value)"
                                type="text"
                                class="w-full px-4 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent text-sm text-slate-800 placeholder:text-slate-400"
                                placeholder="e.g. PhD Student, Curious High Schooler, Software Engineer..."
                            />
                            <p class="text-xs text-slate-400 mt-1">
                                Defines the perspective the AI should take.
                            </p>
                        </div>

                        <!-- Knowledge Level -->
                        <div>
                            <label class="block text-sm font-medium text-slate-700 mb-1">
                                Knowledge Level & Domain
                            </label>
                            <input
                                :value="userKnowledge"
                                @input="e => setUserKnowledge(e.target.value)"
                                type="text"
                                class="w-full px-4 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent text-sm text-slate-800 placeholder:text-slate-400"
                                placeholder="e.g. Expert in ML, Beginner in biology..."
                            />
                            <p class="text-xs text-slate-400 mt-1">
                                Helps the AI adjust technical depth and explanations.
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
