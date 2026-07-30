<template>
  <nav :class="['sidebar', { 'sidebar--collapsed': collapsed, 'sidebar--mobile-open': mobileOpen }]">
    <div class="sidebar__header">
      <div class="sidebar__logo" @click="$router.push('/')">
        <span class="sidebar__logo-icon">🏥</span>
        <span v-if="!collapsed" class="sidebar__logo-text">Licencias Médicas</span>
      </div>
      <button v-if="!isMobile" class="sidebar__toggle btn-ghost btn-icon" @click="$emit('toggle')">
        {{ collapsed ? '▸' : '◂' }}
      </button>
    </div>

    <div class="sidebar__nav">
      <!-- General -->
      <div class="sidebar__section">
        <span v-if="!collapsed" class="sidebar__section-title">General</span>
        <router-link to="/" class="sidebar__link" active-class="sidebar__link--active" exact>
          <span class="sidebar__link-icon">📊</span>
          <span v-if="!collapsed" class="sidebar__link-text">Inicio</span>
        </router-link>
        <router-link to="/circulares" class="sidebar__link" active-class="sidebar__link--active">
          <span class="sidebar__link-icon">📋</span>
          <span v-if="!collapsed" class="sidebar__link-text">Circulares</span>
        </router-link>
      </div>

      <!-- Personal -->
      <div v-if="tieneRol(['personal'])" class="sidebar__section">
        <span v-if="!collapsed" class="sidebar__section-title">Licencias</span>
        <router-link to="/licencias/nueva" class="sidebar__link" active-class="sidebar__link--active">
          <span class="sidebar__link-icon">➕</span>
          <span v-if="!collapsed" class="sidebar__link-text">Nueva Licencia</span>
        </router-link>
        <router-link to="/licencias/mis-licencias" class="sidebar__link" active-class="sidebar__link--active">
          <span class="sidebar__link-icon">📁</span>
          <span v-if="!collapsed" class="sidebar__link-text">Mis Licencias</span>
        </router-link>
      </div>

      <!-- RRHH -->
      <div v-if="tieneRol(['rrhh'])" class="sidebar__section">
        <span v-if="!collapsed" class="sidebar__section-title">Recursos Humanos</span>
        <router-link to="/circulares/gestionar" class="sidebar__link" active-class="sidebar__link--active">
          <span class="sidebar__link-icon">📤</span>
          <span v-if="!collapsed" class="sidebar__link-text">Gestionar Circulares</span>
        </router-link>
        <router-link to="/personal" class="sidebar__link" active-class="sidebar__link--active">
          <span class="sidebar__link-icon">👥</span>
          <span v-if="!collapsed" class="sidebar__link-text">Listado Personal</span>
        </router-link>
      </div>

      <!-- Bienestar / Gestión -->
      <div v-if="tieneRol(['bienestar'])" class="sidebar__section">
        <span v-if="!collapsed" class="sidebar__section-title">
          {{ isSoloAdmin ? 'Gestión' : 'Bienestar' }}
        </span>
        <router-link to="/licencias/gestion" class="sidebar__link" active-class="sidebar__link--active">
          <span class="sidebar__link-icon">📑</span>
          <span v-if="!collapsed" class="sidebar__link-text">Gestión Licencias</span>
        </router-link>
        <router-link to="/personal" class="sidebar__link" active-class="sidebar__link--active">
          <span class="sidebar__link-icon">👥</span>
          <span v-if="!collapsed" class="sidebar__link-text">Personal</span>
        </router-link>
        <router-link to="/reportes" class="sidebar__link" active-class="sidebar__link--active">
          <span class="sidebar__link-icon">📈</span>
          <span v-if="!collapsed" class="sidebar__link-text">Reportes</span>
        </router-link>
      </div>

      <!-- Admin -->
      <div v-if="tieneRol(['admin'])" class="sidebar__section">
        <span v-if="!collapsed" class="sidebar__section-title">Administración</span>
        <router-link to="/admin/usuarios" class="sidebar__link" active-class="sidebar__link--active">
          <span class="sidebar__link-icon">👤</span>
          <span v-if="!collapsed" class="sidebar__link-text">Usuarios</span>
        </router-link>
        <router-link to="/admin/ciudades" class="sidebar__link" active-class="sidebar__link--active">
          <span class="sidebar__link-icon">🏙️</span>
          <span v-if="!collapsed" class="sidebar__link-text">Ciudades</span>
        </router-link>
        <router-link to="/admin/dependencias" class="sidebar__link" active-class="sidebar__link--active">
          <span class="sidebar__link-icon">🏢</span>
          <span v-if="!collapsed" class="sidebar__link-text">Dependencias</span>
        </router-link>
        <router-link to="/admin/jerarquias" class="sidebar__link" active-class="sidebar__link--active">
          <span class="sidebar__link-icon">⭐</span>
          <span v-if="!collapsed" class="sidebar__link-text">Jerarquías</span>
        </router-link>
      </div>
    </div>
  </nav>

  <!-- Mobile overlay -->
  <div v-if="mobileOpen" class="sidebar__mobile-overlay" @click="$emit('close-mobile')"></div>

  <!-- Mobile bottom nav -->
  <nav v-if="isMobile" class="bottom-nav">
    <router-link to="/" class="bottom-nav__item" active-class="bottom-nav__item--active" exact>
      <span class="bottom-nav__icon">📊</span>
      <span class="bottom-nav__label">Inicio</span>
    </router-link>
    <router-link to="/circulares" class="bottom-nav__item" active-class="bottom-nav__item--active">
      <span class="bottom-nav__icon">📋</span>
      <span class="bottom-nav__label">Circulares</span>
    </router-link>
    <router-link v-if="tieneRol(['personal'])" to="/licencias/nueva" class="bottom-nav__item bottom-nav__item--primary">
      <span class="bottom-nav__icon">➕</span>
      <span class="bottom-nav__label">Licencia</span>
    </router-link>
    <router-link v-if="tieneRol(['personal'])" to="/licencias/mis-licencias" class="bottom-nav__item" active-class="bottom-nav__item--active">
      <span class="bottom-nav__icon">📁</span>
      <span class="bottom-nav__label">Mis Lic.</span>
    </router-link>
    <router-link v-if="tieneRol(['bienestar'])" to="/licencias/gestion" class="bottom-nav__item" active-class="bottom-nav__item--active">
      <span class="bottom-nav__icon">📑</span>
      <span class="bottom-nav__label">Licencias</span>
    </router-link>
    <router-link v-if="tieneRol(['bienestar'])" to="/reportes" class="bottom-nav__item" active-class="bottom-nav__item--active">
      <span class="bottom-nav__icon">📈</span>
      <span class="bottom-nav__label">Reportes</span>
    </router-link>
    <router-link v-if="tieneRol(['rrhh'])" to="/circulares/gestionar" class="bottom-nav__item" active-class="bottom-nav__item--active">
      <span class="bottom-nav__icon">📤</span>
      <span class="bottom-nav__label">Subir</span>
    </router-link>
    <router-link v-if="tieneRol(['admin'])" to="/admin/usuarios" class="bottom-nav__item" active-class="bottom-nav__item--active">
      <span class="bottom-nav__icon">⚙️</span>
      <span class="bottom-nav__label">Admin</span>
    </router-link>
  </nav>
</template>

<script>
import authService from '../../services/authService'

export default {
  name: 'AppSidebar',
  props: {
    collapsed: Boolean,
    mobileOpen: Boolean,
  },
  emits: ['toggle', 'close-mobile'],
  data() {
    return {
      isMobile: window.innerWidth <= 768,
    }
  },
  computed: {
    isSoloAdmin() {
      const usuario = authService.getUsuario()
      return usuario && usuario.rol === 'admin'
    }
  },
  mounted() {
    window.addEventListener('resize', this.handleResize)
  },
  beforeUnmount() {
    window.removeEventListener('resize', this.handleResize)
  },
  methods: {
    handleResize() {
      this.isMobile = window.innerWidth <= 768
    },
    tieneRol(roles) {
      const usuario = authService.getUsuario()
      if (!usuario) return false
      // Admin puede ver todo
      if (usuario.rol === 'admin') return true
      return roles.includes(usuario.rol)
    },
  },
}
</script>

<style scoped>
.sidebar {
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  width: var(--sidebar-width);
  background: var(--bg-secondary);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  z-index: 200;
  transition: width var(--transition-base), transform var(--transition-base);
  overflow-y: auto;
  overflow-x: hidden;
}

.sidebar--collapsed {
  width: var(--sidebar-collapsed);
}

.sidebar__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem;
  min-height: var(--header-height);
  border-bottom: 1px solid var(--border-color);
}

.sidebar__logo {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  cursor: pointer;
  overflow: hidden;
}

.sidebar__logo-icon {
  font-size: 1.5rem;
  flex-shrink: 0;
}

.sidebar__logo-text {
  font-size: 0.9375rem;
  font-weight: 700;
  color: var(--text-primary);
  white-space: nowrap;
  background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.sidebar__toggle {
  flex-shrink: 0;
  color: var(--text-muted);
  font-size: 0.875rem;
}

.sidebar__nav {
  flex: 1;
  padding: 0.5rem;
}

.sidebar__section {
  margin-bottom: 0.5rem;
}

.sidebar__section-title {
  display: block;
  padding: 0.5rem 0.75rem;
  font-size: 0.6875rem;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.sidebar__link {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.625rem 0.75rem;
  border-radius: var(--border-radius-sm);
  color: var(--text-secondary);
  font-size: 0.875rem;
  font-weight: 450;
  transition: all var(--transition-fast);
  text-decoration: none;
  white-space: nowrap;
  overflow: hidden;
}

.sidebar__link:hover {
  background: var(--bg-glass);
  color: var(--text-primary);
}

.sidebar__link--active {
  background: var(--accent-primary-light);
  color: var(--accent-primary);
  font-weight: 500;
}

.sidebar__link-icon {
  font-size: 1.125rem;
  flex-shrink: 0;
  width: 24px;
  text-align: center;
}

.sidebar__link-text {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Mobile */
.sidebar__mobile-overlay {
  display: none;
}

@media (max-width: 768px) {
  .sidebar {
    transform: translateX(-100%);
    width: var(--sidebar-width);
    z-index: 300;
  }

  .sidebar--mobile-open {
    transform: translateX(0);
  }

  .sidebar--collapsed {
    width: var(--sidebar-width);
  }

  .sidebar__mobile-overlay {
    display: block;
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.5);
    z-index: 250;
  }
}

/* Bottom Nav */
.bottom-nav {
  display: none;
}

@media (max-width: 768px) {
  .bottom-nav {
    display: flex;
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    height: 60px;
    background: var(--bg-secondary);
    border-top: 1px solid var(--border-color);
    z-index: 100;
    justify-content: space-around;
    align-items: center;
    padding: 0 0.25rem;
    padding-bottom: env(safe-area-inset-bottom, 0);
  }

  .bottom-nav__item {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.125rem;
    padding: 0.375rem 0.5rem;
    color: var(--text-muted);
    text-decoration: none;
    font-size: 0.625rem;
    border-radius: var(--border-radius-sm);
    transition: color var(--transition-fast);
    min-width: 48px;
  }

  .bottom-nav__item--active {
    color: var(--accent-primary);
  }

  .bottom-nav__item--primary {
    background: var(--accent-primary);
    color: white;
    border-radius: 50%;
    width: 44px;
    height: 44px;
    min-width: 44px;
    padding: 0;
    justify-content: center;
    margin-top: -12px;
    box-shadow: 0 2px 8px rgba(59, 130, 246, 0.4);
  }

  .bottom-nav__item--primary .bottom-nav__label {
    display: none;
  }

  .bottom-nav__icon {
    font-size: 1.25rem;
  }

  .bottom-nav__label {
    font-weight: 500;
  }
}
</style>
