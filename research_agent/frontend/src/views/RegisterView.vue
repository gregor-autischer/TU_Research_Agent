<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../composables/useAuth'
import { UserPlus, Eye, EyeOff } from 'lucide-vue-next'

const router = useRouter()
const { register, error } = useAuth()

const username = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const showPassword = ref(false)
const isSubmitting = ref(false)
const localError = ref('')

const handleSubmit = async () => {
    localError.value = ''

    if (!username.value || !password.value) {
        localError.value = 'Username and password are required'
        return
    }

    if (password.value !== confirmPassword.value) {
        localError.value = 'Passwords do not match'
        return
    }

    if (password.value.length < 8) {
        localError.value = 'Password must be at least 8 characters'
        return
    }

    isSubmitting.value = true
    const success = await register(username.value, email.value, password.value)
    isSubmitting.value = false

    if (success) {
        router.push('/')
    }
}
</script>

<template>
    <div class="min-h-screen bg-slate-50 flex items-center justify-center p-4">
        <div class="w-full max-w-md">
            <!-- Logo -->
            <div class="text-center mb-8">
                <div
                    class="w-16 h-16 bg-accent rounded-xl flex items-center justify-center text-white text-2xl font-bold mx-auto shadow-lg">
                    RA
                </div>
                <h1 class="text-2xl font-bold text-slate-800 mt-4">Register</h1>
                <p class="text-slate-500 mt-2">Create your Research Agent account</p>
            </div>

            <!-- Register Form -->
            <div class="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
                <form @submit.prevent="handleSubmit" class="space-y-4">
                    <!-- Error Message -->
                    <div v-if="error || localError" class="bg-red-50 text-red-600 p-3 rounded-lg text-sm">
                        {{ error || localError }}
                    </div>

                    <!-- Username -->
                    <div>
                        <label class="block text-sm font-medium text-slate-700 mb-1">Username</label>
                        <input v-model="username" type="text" required
                            class="w-full px-4 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent text-slate-800 placeholder:text-slate-400"
                            placeholder="Choose a username" />
                    </div>

                    <!-- Email (optional) -->
                    <div>
                        <label class="block text-sm font-medium text-slate-700 mb-1">
                            Email <span class="text-slate-400">(optional)</span>
                        </label>
                        <input v-model="email" type="email"
                            class="w-full px-4 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent text-slate-800 placeholder:text-slate-400"
                            placeholder="your@email.com" />
                    </div>

                    <!-- Password -->
                    <div>
                        <label class="block text-sm font-medium text-slate-700 mb-1">Password</label>
                        <div class="relative">
                            <input v-model="password" :type="showPassword ? 'text' : 'password'" required
                                class="w-full px-4 py-2 pr-10 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent text-slate-800 placeholder:text-slate-400"
                                placeholder="At least 8 characters" />
                            <button type="button" @click="showPassword = !showPassword"
                                class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600">
                                <EyeOff v-if="showPassword" class="w-5 h-5" />
                                <Eye v-else class="w-5 h-5" />
                            </button>
                        </div>
                    </div>

                    <!-- Confirm Password -->
                    <div>
                        <label class="block text-sm font-medium text-slate-700 mb-1">Confirm Password</label>
                        <input v-model="confirmPassword" :type="showPassword ? 'text' : 'password'" required
                            class="w-full px-4 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent text-slate-800 placeholder:text-slate-400"
                            placeholder="Re-enter your password" />
                    </div>

                    <!-- Submit Button -->
                    <button type="submit" :disabled="isSubmitting"
                        class="w-full bg-accent hover:bg-blue-700 text-white font-medium py-2.5 rounded-lg transition-colors flex items-center justify-center gap-2 disabled:opacity-50">
                        <UserPlus class="w-5 h-5" />
                        {{ isSubmitting ? 'Creating account...' : 'Create Account' }}
                    </button>
                </form>

                <!-- Login Link -->
                <p class="text-center text-slate-500 text-sm mt-6">
                    Already have an account?
                    <router-link to="/login" class="text-accent hover:underline font-medium">
                        Sign In
                    </router-link>
                </p>
            </div>
        </div>
    </div>
</template>
