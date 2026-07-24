<template>
  <div class="toast-container">
    <transition-group name="toast">
      <div
        v-for="toast in toasts"
        :key="toast.id"
        :class="['toast', `toast--${toast.type}`]"
      >
        <span class="toast__icon">{{ iconMap[toast.type] }}</span>
        <span class="toast__message">{{ toast.message }}</span>
        <button class="toast__close" @click="remove(toast.id)">✕</button>
      </div>
    </transition-group>
  </div>
</template>

<script>
export default {
  name: 'Toast',
  data() {
    return {
      toasts: [],
      nextId: 0,
      iconMap: {
        success: '✓',
        error: '✗',
        warning: '⚠',
        info: 'ℹ',
      },
    }
  },
  methods: {
    show(message, type = 'info', duration = 4000) {
      const id = this.nextId++
      this.toasts.push({ id, message, type })
      setTimeout(() => this.remove(id), duration)
    },
    remove(id) {
      this.toasts = this.toasts.filter((t) => t.id !== id)
    },
  },
}
</script>

<style scoped>
.toast-enter-active {
  animation: slideInRight 0.3s ease;
}
.toast-leave-active {
  animation: slideInRight 0.3s ease reverse;
}
</style>
