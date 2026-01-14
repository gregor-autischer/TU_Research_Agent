import { ref, computed, watch } from 'vue'
import { useAuth } from './useAuth'

// Shared state
const projects = ref([])
const currentProject = ref(null)
const isLoading = ref(false)
const error = ref(null)

export function useProjects() {
    const { getCsrfToken } = useAuth()

    const apiRequest = async (endpoint, options = {}) => {
        const response = await fetch(endpoint, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken(),
                ...options.headers
            },
            credentials: 'include'
        })

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}))
            throw new Error(errorData.error || `Request failed: ${response.status}`)
        }

        return response.json()
    }

    const fetchProjects = async () => {
        isLoading.value = true
        error.value = null
        try {
            const data = await apiRequest('/api/projects/')
            projects.value = data.projects

            // Set initial project if none selected
            if (!currentProject.value && projects.value.length > 0) {
                // Try to recover from local storage
                const savedId = localStorage.getItem('currentProjectId')
                if (savedId) {
                    const found = projects.value.find(p => p.id === parseInt(savedId))
                    if (found) {
                        currentProject.value = found
                        return
                    }
                }
                // Default to first
                currentProject.value = projects.value[0]
            }
        } catch (e) {
            error.value = e.message
            console.error('Failed to fetch projects', e)
        } finally {
            isLoading.value = false
        }
    }

    const createProject = async (name, description = '') => {
        isLoading.value = true
        try {
            const newProject = await apiRequest('/api/projects/', {
                method: 'POST',
                body: JSON.stringify({ name, description })
            })
            projects.value.push(newProject)
            currentProject.value = newProject
            return newProject
        } catch (e) {
            error.value = e.message
            throw e
        } finally {
            isLoading.value = false
        }
    }

    const deleteProject = async (projectId) => {
        try {
            await apiRequest(`/api/projects/${projectId}/`, { method: 'DELETE' })
            projects.value = projects.value.filter(p => p.id !== projectId)

            // Switch if deleted current
            if (currentProject.value && currentProject.value.id === projectId) {
                currentProject.value = projects.value[0] || null
            }
        } catch (e) {
            error.value = e.message
            throw e
        }
    }

    const setCurrentProject = (project) => {
        currentProject.value = project
        localStorage.setItem('currentProjectId', project.id)
    }

    return {
        projects,
        currentProject,
        isLoading,
        error,
        fetchProjects,
        createProject,
        deleteProject,
        setCurrentProject
    }
}
