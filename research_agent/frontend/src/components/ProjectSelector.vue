<script setup>
import { ref, onMounted, nextTick, onUnmounted } from 'vue'
import { useProjects } from '../composables/useProjects'
import { FolderGit2, Plus, Check, ChevronsUpDown, Loader2 } from 'lucide-vue-next'

const { projects, currentProject, fetchProjects, createProject, setCurrentProject, isLoading } = useProjects()

const isOpen = ref(false)
const isCreating = ref(false)
const newProjectName = ref('')
const selectorRef = ref(null)
const inputRef = ref(null)

const handleClickOutside = (e) => {
    if (selectorRef.value && !selectorRef.value.contains(e.target)) {
        isOpen.value = false
        isCreating.value = false
    }
}

onMounted(() => {
    fetchProjects()
    document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
    document.removeEventListener('click', handleClickOutside)
})

const toggleDropdown = () => {
    isOpen.value = !isOpen.value
    if (!isOpen.value) isCreating.value = false
}

const handleSelect = (project) => {
    setCurrentProject(project)
    isOpen.value = false
}

const handleCreate = async () => {
    if (!newProjectName.value.trim()) return
    
    try {
        await createProject(newProjectName.value)
        newProjectName.value = ''
        isCreating.value = false
        isOpen.value = false
    } catch (e) {
        console.error(e)
    }
}

const startCreating = async () => {
    isCreating.value = true
    await nextTick()
    inputRef.value?.focus()
}
</script>

<template>
    <div class="relative z-20" ref="selectorRef">
        <button 
            @click.stop="toggleDropdown"
            class="flex items-center gap-2 w-full p-2 rounded-lg hover:bg-slate-200 transition-colors text-left"
            :disabled="isLoading"
        >
            <div class="p-1.5 bg-indigo-100 rounded text-indigo-600">
                <FolderGit2 v-if="!isLoading" class="w-4 h-4" />
                <Loader2 v-else class="w-4 h-4 animate-spin" />
            </div>
            
            <div class="flex-1 min-w-0">
                <div class="text-sm font-semibold text-slate-700 truncate">
                    {{ currentProject?.name || 'Select Project' }}
                </div>
                <div class="text-xs text-slate-500 truncate">
                    {{ isLoading ? 'Loading...' : `${projects.length} Projects` }}
                </div>
            </div>
            
            <ChevronsUpDown class="w-4 h-4 text-slate-400" />
        </button>

        <transition
            enter-active-class="transition duration-100 ease-out"
            enter-from-class="transform scale-95 opacity-0"
            enter-to-class="transform scale-100 opacity-100"
            leave-active-class="transition duration-75 ease-in"
            leave-from-class="transform scale-100 opacity-100"
            leave-to-class="transform scale-95 opacity-0"
        >
            <div v-if="isOpen" class="absolute top-full left-0 w-full mt-1 bg-white border border-slate-200 rounded-lg shadow-lg overflow-hidden py-1">
                
                <div class="max-h-64 overflow-y-auto">
                    <button 
                        v-for="project in projects" 
                        :key="project.id"
                        @click="handleSelect(project)"
                        class="w-full text-left px-3 py-2 text-sm flex items-center justify-between hover:bg-slate-50 transition-colors"
                        :class="currentProject?.id === project.id ? 'bg-indigo-50 text-indigo-700 font-medium' : 'text-slate-700'"
                    >
                        <span class="truncate">{{ project.name }}</span>
                        <Check v-if="currentProject?.id === project.id" class="w-4 h-4" />
                    </button>
                </div>
                
                <div class="border-t border-slate-100 mt-1 pt-1 px-2 pb-2">
                    <div v-if="isCreating" class="flex items-center gap-1 mt-1">
                        <input 
                            ref="inputRef"
                            v-model="newProjectName"
                            @keyup.enter="handleCreate"
                            @keyup.esc="isCreating = false"
                            placeholder="Project Name"
                            class="flex-1 text-sm border border-slate-300 rounded px-2 py-1 outline-none focus:border-indigo-500"
                            @click.stop
                        />
                        <button 
                            @click.stop="handleCreate"
                            class="p-1 bg-indigo-600 text-white rounded hover:bg-indigo-700 disabled:opacity-50"
                            :disabled="!newProjectName.trim() || isLoading"
                        >
                            <Check class="w-4 h-4" />
                        </button>
                    </div>
                    <button 
                        v-else
                        @click.stop.prevent="startCreating"
                        class="w-full flex items-center gap-2 px-2 py-1.5 text-sm text-slate-600 hover:bg-slate-100 rounded transition-colors mt-1"
                    >
                        <Plus class="w-4 h-4" />
                        <span>Create Project</span>
                    </button>
                </div>
            </div>
        </transition>
    </div>
</template>
