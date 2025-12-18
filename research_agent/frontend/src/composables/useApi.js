import { useAuth } from './useAuth'

export function useApi() {
    const { getCsrfToken } = useAuth()

    const chat = async (message) => {
        const response = await fetch('/api/chat/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            credentials: 'include',
            body: JSON.stringify({ message })
        })

        const data = await response.json()

        if (!response.ok) {
            throw new Error(data.error || 'Chat request failed')
        }

        return data
    }

    return { chat }
}
