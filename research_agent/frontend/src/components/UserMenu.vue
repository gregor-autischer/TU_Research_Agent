<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../composables/useAuth'
import { User, Settings, LogOut, ChevronDown, Shield } from 'lucide-vue-next'

const router = useRouter()
const { user, logout } = useAuth()

const isOpen = ref(false)

const handleLogout = async () => {
    await logout()
    router.push('/login')
}
</script>

<template>
    <div class="relative">
        <button @click="isOpen = !isOpen"
            class="flex items-center gap-2 px-3 py-1.5 hover:bg-slate-100 rounded-lg transition-colors">
            <div class="w-8 h-8 bg-slate-200 rounded-full flex items-center justify-center">
                <User class="w-4 h-4 text-slate-600" />
            </div>
            <span class="text-sm font-medium text-slate-700">{{ user?.username }}</span>
            <ChevronDown class="w-4 h-4 text-slate-400" />
        </button>

        <!-- Dropdown -->
        <div v-if="isOpen"
            class="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-slate-200 py-1 z-50">
            <router-link to="/settings" @click="isOpen = false"
                class="flex items-center gap-2 px-4 py-2 text-sm text-slate-700 hover:bg-slate-50">
                <Settings class="w-4 h-4" />
                Settings
            </router-link>
            <a v-if="user?.is_staff" href="/admin/" target="_blank" @click="isOpen = false"
                class="flex items-center gap-2 px-4 py-2 text-sm text-slate-700 hover:bg-slate-50">
                <Shield class="w-4 h-4" />
                Admin
            </a>
            <button @click="handleLogout"
                class="flex items-center gap-2 px-4 py-2 text-sm text-red-600 hover:bg-red-50 w-full text-left">
                <LogOut class="w-4 h-4" />
                Sign Out
            </button>
        </div>
    </div>

    <!-- Click outside to close -->
    <div v-if="isOpen" @click="isOpen = false" class="fixed inset-0 z-40"></div>
</template>
