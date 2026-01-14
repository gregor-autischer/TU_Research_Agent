import { ref, readonly, watch } from 'vue'
import { useAuth } from './useAuth'
import { useProjects } from './useProjects'

const papers = ref([])
const isLoading = ref(false)

export function usePapers() {
    const { getCsrfToken } = useAuth()
    const { currentProject } = useProjects()

    async function apiRequest(url, options = {}) {
        const response = await fetch(url, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken(),
                ...options.headers
            },
            credentials: 'include'
        })

        if (response.status === 204) {
            return null
        }

        const data = await response.json()
        if (!response.ok) {
            throw new Error(data.error || 'Request failed')
        }
        return data
    }

    const fetchPapers = async () => {
        if (!currentProject.value) return

        isLoading.value = true
        try {
            const data = await apiRequest(`/api/papers/?project_id=${currentProject.value.id}`)
            papers.value = data.papers
        } catch (e) {
            console.error('Failed to fetch papers:', e)
        } finally {
            isLoading.value = false
        }
    }

    // Watch for project changes
    watch(currentProject, (newP) => {
        if (newP) {
            fetchPapers()
        } else {
            papers.value = []
        }
    })

    const addPaper = async (paper) => {
        if (!currentProject.value) throw new Error('No project selected')

        try {
            const data = await apiRequest(`/api/papers/?project_id=${currentProject.value.id}`, {
                method: 'POST',
                body: JSON.stringify(paper)
            })
            // Add paper immediately with loading state for bibtex
            data.bibtexLoading = true
            papers.value.unshift(data)

            // Generate BibTeX asynchronously
            generateBibtex(data.id)

            return data
        } catch (e) {
            console.error('Failed to add paper:', e)
            throw e
        }
    }

    const generateBibtex = async (id) => {
        try {
            const data = await apiRequest(`/api/papers/${id}/generate-bibtex/`, {
                method: 'POST'
            })
            // Update paper with generated bibtex
            const idx = papers.value.findIndex(p => p.id === id)
            if (idx !== -1) {
                papers.value[idx].bibtex = data.bibtex
                papers.value[idx].bibtexLoading = false
            }
            return data
        } catch (e) {
            console.error('Failed to generate bibtex:', e)
            // Clear loading state on error
            const idx = papers.value.findIndex(p => p.id === id)
            if (idx !== -1) {
                papers.value[idx].bibtexLoading = false
            }
        }
    }

    const updatePaper = async (id, updates) => {
        try {
            const data = await apiRequest(`/api/papers/${id}/`, {
                method: 'PATCH',
                body: JSON.stringify(updates)
            })
            const idx = papers.value.findIndex(p => p.id === id)
            if (idx !== -1) {
                papers.value[idx] = data
            }
            return data
        } catch (e) {
            console.error('Failed to update paper:', e)
            throw e
        }
    }

    const deletePaper = async (id) => {
        try {
            await apiRequest(`/api/papers/${id}/`, { method: 'DELETE' })
            papers.value = papers.value.filter(p => p.id !== id)
        } catch (e) {
            console.error('Failed to delete paper:', e)
            throw e
        }
    }

    const toggleContext = async (id) => {
        const paper = papers.value.find(p => p.id === id)
        if (paper) {
            await updatePaper(id, { inContext: !paper.inContext })
        }
    }

    const clearPapers = () => {
        papers.value = []
    }

    const copyPaperToProject = async (paperId, targetProjectId) => {
        try {
            const data = await apiRequest(`/api/papers/${paperId}/copy/`, {
                method: 'POST',
                body: JSON.stringify({ target_project_id: targetProjectId })
            })
            return data
        } catch (e) {
            console.error('Failed to copy paper:', e)
            throw e
        }
    }

    return {
        papers: readonly(papers),
        isLoading: readonly(isLoading),
        fetchPapers,
        addPaper,
        updatePaper,
        deletePaper,
        toggleContext,
        clearPapers,
        copyPaperToProject
    }
}
