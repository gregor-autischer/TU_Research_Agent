import { ref, readonly } from 'vue'

const user = ref(null)
const isLoading = ref(true)
const error = ref(null)

function getCsrfToken() {
    const name = 'csrftoken'
    const cookies = document.cookie.split(';')
    for (let cookie of cookies) {
        const [cookieName, cookieValue] = cookie.trim().split('=')
        if (cookieName === name) {
            return cookieValue
        }
    }
    return null
}

async function apiRequest(url, options = {}) {
    const csrfToken = getCsrfToken()

    const response = await fetch(url, {
        ...options,
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
            ...options.headers
        },
        credentials: 'include'
    })

    const data = await response.json()

    if (!response.ok) {
        throw new Error(data.error || 'Request failed')
    }

    return data
}

export function useAuth() {
    const checkAuth = async () => {
        isLoading.value = true
        error.value = null
        try {
            await fetch('/api/auth/csrf/', { credentials: 'include' })
            const data = await apiRequest('/api/auth/user/')
            user.value = data.user
        } catch (e) {
            user.value = null
        } finally {
            isLoading.value = false
        }
    }

    const login = async (username, password) => {
        error.value = null
        try {
            const data = await apiRequest('/api/auth/login/', {
                method: 'POST',
                body: JSON.stringify({ username, password })
            })
            user.value = data.user
            return true
        } catch (e) {
            error.value = e.message
            return false
        }
    }

    const register = async (username, email, password) => {
        error.value = null
        try {
            const data = await apiRequest('/api/auth/register/', {
                method: 'POST',
                body: JSON.stringify({ username, email, password })
            })
            user.value = data.user
            return true
        } catch (e) {
            error.value = e.message
            return false
        }
    }

    const logout = async () => {
        try {
            await apiRequest('/api/auth/logout/', { method: 'POST' })
            user.value = null
            return true
        } catch (e) {
            error.value = e.message
            return false
        }
    }

    const saveApiKey = async (apiKey) => {
        error.value = null
        try {
            const data = await apiRequest('/api/auth/api-key/', {
                method: 'POST',
                body: JSON.stringify({ api_key: apiKey })
            })
            if (user.value) {
                user.value.has_api_key = true
                user.value.api_key_preview = data.api_key_preview
            }
            return true
        } catch (e) {
            error.value = e.message
            return false
        }
    }

    const deleteApiKey = async () => {
        error.value = null
        try {
            await apiRequest('/api/auth/api-key/delete/', { method: 'DELETE' })
            if (user.value) {
                user.value.has_api_key = false
                user.value.api_key_preview = null
            }
            return true
        } catch (e) {
            error.value = e.message
            return false
        }
    }

    return {
        user: readonly(user),
        isLoading: readonly(isLoading),
        error: readonly(error),
        checkAuth,
        login,
        register,
        logout,
        saveApiKey,
        deleteApiKey,
        getCsrfToken
    }
}
