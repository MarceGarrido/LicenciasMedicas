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

export default {
  name: 'App',
  components: { AppLayout, Toast },
  provide() {
    return {
      showToast: this.showToast,
    }
  },
  methods: {
    showToast(message, type = 'info') {
      if (this.$refs.toast) {
        this.$refs.toast.show(message, type)
      }
    },
  },
}
</script>
