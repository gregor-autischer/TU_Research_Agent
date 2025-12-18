import { ref, readonly } from 'vue'
import { useAuth } from './useAuth'

const conversations = ref([])
const currentConversation = ref(null)
const isLoading = ref(false)
const isSending = ref(false)

export function useConversations() {
    const { getCsrfToken } = useAuth()

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
        isLoading.value = true
        try {
            const data = await apiRequest('/api/conversations/')
            conversations.value = data.conversations
        } catch (e) {
            console.error('Failed to fetch conversations:', e)
        } finally {
            isLoading.value = false
        }
    }

    const createConversation = async (title = 'New Conversation') => {
        try {
            const data = await apiRequest('/api/conversations/', {
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

    const sendMessage = async (conversationId, message) => {
        // Optimistically add user message immediately
        const tempUserMessage = { id: `temp-${Date.now()}`, role: 'user', content: message }
        if (currentConversation.value?.id === conversationId) {
            // Reassign to trigger reactivity
            currentConversation.value = {
                ...currentConversation.value,
                messages: [...currentConversation.value.messages, tempUserMessage]
            }
        }

        isSending.value = true
        try {
            const data = await apiRequest(`/api/conversations/${conversationId}/chat/`, {
                method: 'POST',
                body: JSON.stringify({ message })
            })
            if (currentConversation.value?.id === conversationId) {
                // Replace temp message with real one and add assistant message
                const newMessages = currentConversation.value.messages.filter(m => m.id !== tempUserMessage.id)
                newMessages.push(data.user_message)
                newMessages.push(data.assistant_message)
                currentConversation.value = {
                    ...currentConversation.value,
                    messages: newMessages
                }
            }
            const idx = conversations.value.findIndex(c => c.id === conversationId)
            if (idx !== -1) {
                conversations.value[idx].preview = data.assistant_message.content.slice(0, 50)
                conversations.value[idx].updated_at = new Date().toISOString()
                const [conv] = conversations.value.splice(idx, 1)
                conversations.value.unshift(conv)
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
        clearCurrentConversation
    }
}
