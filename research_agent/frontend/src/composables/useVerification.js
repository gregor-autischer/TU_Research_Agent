import { ref } from 'vue'
import { useAuth } from './useAuth'
import { useSettings } from './useSettings'

// Shared state
const verifying = ref(false)
const verificationError = ref(null)
const verificationResults = ref({})

export function useVerification() {
    const { getCsrfToken } = useAuth()
    const { getSettings } = useSettings()

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

    const verifyMessage = async (messageId) => {
        verifying.value = true
        verificationError.value = null

        try {
            const settings = getSettings()
            const data = await apiRequest(`/api/messages/${messageId}/verify/`, {
                method: 'POST',
                body: JSON.stringify({ model: settings.model })
            })
            verificationResults.value[messageId] = data
            return data
        } catch (error) {
            console.error('[Verification] Error:', error)
            verificationError.value = error.message || 'Verification failed'
            throw error
        } finally {
            verifying.value = false
        }
    }

    const setVerification = (messageId, data) => {
        verificationResults.value[messageId] = data
    }

    const getVerification = (messageId) => {
        return verificationResults.value[messageId] || null
    }

    const clearVerification = (messageId) => {
        delete verificationResults.value[messageId]
    }

    const clearAllVerifications = () => {
        verificationResults.value = {}
    }

    return {
        verifying,
        verificationError,
        verificationResults,
        verifyMessage,
        setVerification,
        getVerification,
        clearVerification,
        clearAllVerifications
    }
}
