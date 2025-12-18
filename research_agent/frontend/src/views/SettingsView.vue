<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../composables/useAuth'
import { ArrowLeft, Key, Save, Trash2, Eye, EyeOff, Check } from 'lucide-vue-next'

const router = useRouter()
const { user, saveApiKey, deleteApiKey, error } = useAuth()

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
</script>

<template>
    <div class="min-h-screen bg-slate-50">
        <!-- Header -->
        <header class="h-14 border-b border-slate-200 flex items-center px-4 bg-white">
            <button @click="router.push('/')"
                class="p-2 hover:bg-slate-100 rounded-lg mr-3 text-slate-600 transition-colors">
                <ArrowLeft class="w-5 h-5" />
            </button>
            <h1 class="text-lg font-semibold text-slate-800">Settings</h1>
        </header>

        <!-- Content -->
        <div class="max-w-2xl mx-auto p-6">
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
                    <p class="text-sm" :class="user?.has_api_key ? 'text-green-700' : 'text-amber-700'">
                        <Check v-if="user?.has_api_key" class="w-4 h-4 inline mr-1" />
                        {{ user?.has_api_key ? 'API key is configured' : 'No API key configured' }}
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
        </div>
    </div>
</template>
