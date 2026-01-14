import { ref, readonly, watch } from 'vue'
import { useAuth } from './useAuth'
import { useProjects } from './useProjects'
import { useVerification } from './useVerification'

const conversations = ref([])
const currentConversation = ref(null)
const isLoading = ref(false)
const isSending = ref(false)

export function useConversations() {
    const { getCsrfToken } = useAuth()
    const { currentProject } = useProjects()
    const { setVerification } = useVerification()

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

    const fetchConversations = async () => {
        if (!currentProject.value) return

        isLoading.value = true
        try {
            const data = await apiRequest(`/api/conversations/?project_id=${currentProject.value.id}`)
            conversations.value = data.conversations
        } catch (e) {
            console.error('Failed to fetch conversations:', e)
        } finally {
            isLoading.value = false
        }
    }

    // Watch for project changes
    watch(currentProject, (newP) => {
        if (newP) {
            // Clear current conversation as it belongs to old project
            currentConversation.value = null
            fetchConversations()
        } else {
            conversations.value = []
            currentConversation.value = null
        }
    })

    const createConversation = async (title = 'New Conversation') => {
        if (!currentProject.value) throw new Error('No project selected')

        try {
            const data = await apiRequest(`/api/conversations/?project_id=${currentProject.value.id}`, {
                method: 'POST',
                body: JSON.stringify({ title })
            })
            conversations.value.unshift(data)
            currentConversation.value = data
            return data
        } catch (e) {
            console.error('Failed to create conversation:', e)
            throw e
        }
    }

    const loadConversation = async (id) => {
        isLoading.value = true
        try {
            const data = await apiRequest(`/api/conversations/${id}/`)
            currentConversation.value = data

            // Populate verifications from history
            if (data.messages) {
                data.messages.forEach(msg => {
                    if (msg.verification) {
                        setVerification(msg.id, msg.verification)
                    }
                })
            }

            return data
        } catch (e) {
            console.error('Failed to load conversation:', e)
            throw e
        } finally {
            isLoading.value = false
        }
    }

    const updateConversationTitle = async (id, title) => {
        try {
            const data = await apiRequest(`/api/conversations/${id}/`, {
                method: 'PATCH',
                body: JSON.stringify({ title })
            })
            const idx = conversations.value.findIndex(c => c.id === id)
            if (idx !== -1) {
                conversations.value[idx].title = title
            }
            if (currentConversation.value?.id === id) {
                currentConversation.value.title = title
            }
            return data
        } catch (e) {
            console.error('Failed to update conversation:', e)
            throw e
        }
    }

    const deleteConversation = async (id) => {
        try {
            await apiRequest(`/api/conversations/${id}/`, { method: 'DELETE' })
            conversations.value = conversations.value.filter(c => c.id !== id)
            if (currentConversation.value?.id === id) {
                currentConversation.value = null
            }
        } catch (e) {
            console.error('Failed to delete conversation:', e)
            throw e
        }
    }

    const sendMessage = async (conversationId, message, settings = {}, filters = {}) => {
        // Optimistically add user message immediately
        const tempUserMessage = { id: `temp-${Date.now()}`, role: 'user', content: message }

        // Optimistic Title Update (if new conversation)
        let optimisticTitle = null
        if (currentConversation.value?.title === 'New Conversation') {
            optimisticTitle = message.length > 30 ? message.slice(0, 30) + '...' : message
        }

        if (currentConversation.value?.id === conversationId) {
            // Reassign to trigger reactivity
            const updates = {
                messages: [...currentConversation.value.messages, tempUserMessage]
            }
            if (optimisticTitle) {
                updates.title = optimisticTitle
            }
            currentConversation.value = {
                ...currentConversation.value,
                ...updates
            }
        }

        // Update list immediately for title and preview
        const listIdx = conversations.value.findIndex(c => c.id === conversationId)
        if (listIdx !== -1) {
            const listUpdate = { ...conversations.value[listIdx] }
            if (optimisticTitle) {
                listUpdate.title = optimisticTitle
            }
            // Update preview immediately to user message (will be replaced by AI response later)
            listUpdate.preview = message.length > 50 ? message.slice(0, 50) + '...' : message

            conversations.value.splice(listIdx, 1, listUpdate)
        }

        isSending.value = true
        try {
            const data = await apiRequest(`/api/conversations/${conversationId}/chat/`, {
                method: 'POST',
                body: JSON.stringify({ message, ...settings, filters })
            })
            if (currentConversation.value?.id === conversationId) {
                // Replace temp message with real one and add assistant message
                const newMessages = currentConversation.value.messages.filter(m => m.id !== tempUserMessage.id)
                newMessages.push(data.user_message)
                newMessages.push(data.assistant_message)
                currentConversation.value = {
                    ...currentConversation.value,
                    messages: newMessages,
                    title: data.conversation_title || currentConversation.value.title
                }
            }
            const idx = conversations.value.findIndex(c => c.id === conversationId)
            if (idx !== -1) {
                // Create updated conversation object to ensure reactivity
                const updatedConv = {
                    ...conversations.value[idx],
                    preview: data.assistant_message.content.slice(0, 50),
                    updated_at: new Date().toISOString()
                }
                // Update title if it was generated
                if (data.conversation_title) {
                    updatedConv.title = data.conversation_title
                }
                // Remove from current position and add to front
                conversations.value.splice(idx, 1)
                conversations.value.unshift(updatedConv)
            }
            return data
        } catch (e) {
            // Remove temp message on error
            if (currentConversation.value?.id === conversationId) {
                currentConversation.value = {
                    ...currentConversation.value,
                    messages: currentConversation.value.messages.filter(m => m.id !== tempUserMessage.id)
                }
            }
            throw e
        } finally {
            isSending.value = false
        }
    }

    const clearCurrentConversation = () => {
        currentConversation.value = null
    }

    const clearAll = () => {
        conversations.value = []
        currentConversation.value = null
    }

    return {
        conversations: readonly(conversations),
        currentConversation: readonly(currentConversation),
        isLoading: readonly(isLoading),
        isSending: readonly(isSending),
        fetchConversations,
        createConversation,
        loadConversation,
        updateConversationTitle,
        deleteConversation,
        sendMessage,
        clearCurrentConversation,
        clearAll
    }
}
