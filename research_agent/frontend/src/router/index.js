import { createRouter, createWebHistory } from 'vue-router'
import { useAuth } from '../composables/useAuth'

const routes = [
    {
        path: '/login',
        name: 'Login',
        component: () => import('../views/LoginView.vue'),
        meta: { requiresGuest: true }
    },
    {
        path: '/register',
        name: 'Register',
        component: () => import('../views/RegisterView.vue'),
        meta: { requiresGuest: true }
    },
    {
        path: '/',
        name: 'Home',
        component: () => import('../views/HomeView.vue'),
        meta: { requiresAuth: true }
    },
    {
        path: '/settings',
        name: 'Settings',
        component: () => import('../views/SettingsView.vue'),
        meta: { requiresAuth: true }
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

let authChecked = false

router.beforeEach(async (to, from, next) => {
    const { user, checkAuth, isLoading } = useAuth()

    if (!authChecked) {
        await checkAuth()
        authChecked = true
    }

    if (to.meta.requiresAuth && !user.value) {
        next('/login')
    } else if (to.meta.requiresGuest && user.value) {
        next('/')
    } else {
        next()
    }
})

export default router
