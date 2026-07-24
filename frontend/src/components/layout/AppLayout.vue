<template>
  <div class="app-layout">
    <AppSidebar
      :collapsed="sidebarCollapsed"
      :mobile-open="mobileMenuOpen"
      @toggle="sidebarCollapsed = !sidebarCollapsed"
      @close-mobile="mobileMenuOpen = false"
    />
    <div :class="['app-layout__main', { 'app-layout__main--sidebar-collapsed': sidebarCollapsed }]">
      <AppHeader @toggle-sidebar="mobileMenuOpen = !mobileMenuOpen" />
      <main class="app-layout__content">
        <slot />
      </main>
    </div>
  </div>
</template>

<script>
import AppHeader from './AppHeader.vue'
import AppSidebar from './AppSidebar.vue'

export default {
  name: 'AppLayout',
  components: { AppHeader, AppSidebar },
  data() {
    return {
      sidebarCollapsed: false,
      mobileMenuOpen: false,
    }
  },
  watch: {
    '$route'() {
      this.mobileMenuOpen = false
    },
  },
}
</script>

<style scoped>
.app-layout {
  min-height: 100vh;
}

.app-layout__main {
  margin-left: var(--sidebar-width);
  min-height: 100vh;
  transition: margin-left var(--transition-base);
}

.app-layout__main--sidebar-collapsed {
  margin-left: var(--sidebar-collapsed);
}

.app-layout__content {
  padding: 1.5rem;
  max-width: 1400px;
}

@media (max-width: 768px) {
  .app-layout__main {
    margin-left: 0;
  }

  .app-layout__main--sidebar-collapsed {
    margin-left: 0;
  }

  .app-layout__content {
    padding: 1rem;
    padding-bottom: calc(60px + 1rem + env(safe-area-inset-bottom, 0));
  }
}
</style>
