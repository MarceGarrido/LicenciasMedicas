<template>
  <div id="app-root">
    <Toast ref="toast" />
    <router-view v-if="$route.path === '/login'" />
    <AppLayout v-else>
      <router-view />
    </AppLayout>
  </div>
</template>

<script>
import AppLayout from './components/layout/AppLayout.vue'
import Toast from './components/ui/Toast.vue'
import authService from './services/authService'

export default {
  name: 'App',
  components: { AppLayout, Toast },
  provide() {
    return {
      showToast: this.showToast,
    }
  },
  data() {
    return {
      inactivityTimer: null,
      INACTIVITY_LIMIT: 30 * 60 * 1000, // 30 minutos
    }
  },
  mounted() {
    this.setupInactivityListener()
  },
  beforeUnmount() {
    this.cleanupInactivityListener()
  },
  methods: {
    showToast(message, type = 'info') {
      if (this.$refs.toast) {
        this.$refs.toast.show(message, type)
      }
    },
    setupInactivityListener() {
      const events = ['mousemove', 'keydown', 'click', 'scroll', 'touchstart']
      events.forEach((event) => window.addEventListener(event, this.resetInactivityTimer))
      this.resetInactivityTimer()
    },
    cleanupInactivityListener() {
      const events = ['mousemove', 'keydown', 'click', 'scroll', 'touchstart']
      events.forEach((event) => window.removeEventListener(event, this.resetInactivityTimer))
      if (this.inactivityTimer) clearTimeout(this.inactivityTimer)
    },
    resetInactivityTimer() {
      if (!authService.isAuthenticated()) return // No hacer nada si no está logueado
      
      if (this.inactivityTimer) clearTimeout(this.inactivityTimer)
      this.inactivityTimer = setTimeout(() => {
        this.logoutPorInactividad()
      }, this.INACTIVITY_LIMIT)
    },
    async logoutPorInactividad() {
      await authService.logout()
      if (this.$route.path !== '/login') {
        this.$router.push('/login')
        setTimeout(() => {
          this.showToast('Sesión cerrada por inactividad (30 min).', 'warning')
        }, 500)
      }
    },
  },
}
</script>
