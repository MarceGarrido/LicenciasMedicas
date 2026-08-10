<template>
  <header class="app-header">
    <div class="header__left">
      <button class="btn-ghost header__menu-toggle" @click="$emit('toggle-sidebar')">
        <span class="menu-icon">☰</span>
      </button>
      <div class="header__breadcrumb">
        <span class="header__page-title">{{ pageTitle }}</span>
      </div>
    </div>
    <div class="header__right">
      <button class="btn-ghost btn-icon theme-toggle" @click="toggleTheme" title="Alternar tema">
        {{ isDark ? '☀️' : '🌙' }}
      </button>
      <div class="header__user" @click="showMenu = !showMenu">
        <div class="header__avatar">{{ initials }}</div>
        <div class="header__user-info">
          <span class="header__user-name">{{ usuario?.nombre_completo }}</span>
          <span class="header__user-role">{{ rolLabel }}</span>
        </div>
        <span class="header__chevron">▾</span>
      </div>
      <div v-if="showMenu" class="header__dropdown" @click.stop>
        <button class="header__dropdown-item" @click="abrirActualizarDatos">
          📋 Actualizar datos
        </button>
        <button class="header__dropdown-item" @click="cambiarPassword">
          🔒 Cambiar contraseña
        </button>
        <hr class="header__dropdown-divider" />
        <button class="header__dropdown-item header__dropdown-item--danger" @click="cerrarSesion">
          🚪 Cerrar sesión
        </button>
      </div>
    </div>
    <div v-if="showMenu" class="header__overlay" @click="showMenu = false"></div>
  </header>

  <!-- Modal cambiar contraseña -->
  <div v-if="showPasswordModal" class="modal-overlay" @click.self="showPasswordModal = false">
    <div class="modal">
      <div class="modal__header">
        <h3 class="modal__title">Cambiar contraseña</h3>
        <button class="btn-ghost btn-icon" @click="showPasswordModal = false">✕</button>
      </div>
      <form @submit.prevent="submitPassword" class="modal__body">
        <div class="form-group">
          <label class="form-label">Contraseña actual</label>
          <input type="password" class="form-control" v-model="passwordForm.actual" required />
        </div>
        <div class="form-group">
          <label class="form-label">Nueva contraseña</label>
          <input type="password" class="form-control" v-model="passwordForm.nueva" required minlength="8" />
        </div>
        <div class="form-group">
          <label class="form-label">Confirmar nueva contraseña</label>
          <input type="password" class="form-control" v-model="passwordForm.confirmar" required />
        </div>
        <p v-if="passwordError" class="form-error">{{ passwordError }}</p>
      </form>
      <div class="modal__footer">
        <button class="btn btn-secondary" @click="showPasswordModal = false">Cancelar</button>
        <button class="btn btn-primary" @click="submitPassword" :disabled="passwordLoading">
          {{ passwordLoading ? 'Guardando...' : 'Guardar' }}
        </button>
      </div>
    </div>
  </div>

  <!-- Modal actualizar datos -->
  <div v-if="showDatosModal" class="modal-overlay" @click.self="showDatosModal = false">
    <div class="modal" style="max-width:500px">
      <div class="modal__header">
        <h3 class="modal__title">📋 Actualizar mis datos</h3>
        <button class="btn-ghost btn-icon" @click="showDatosModal = false">✕</button>
      </div>
      <div class="modal__body">
        <div class="perfil-actual">
          <div class="perfil-actual__item">
            <span class="perfil-actual__label">Jerarquía actual:</span>
            <span class="perfil-actual__value">{{ usuario?.jerarquia_nombre || 'Sin asignar' }}</span>
          </div>
          <div class="perfil-actual__item">
            <span class="perfil-actual__label">Dependencia actual:</span>
            <span class="perfil-actual__value">{{ usuario?.dependencia_nombre || 'Sin asignar' }}</span>
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">Jerarquía</label>
          <select class="form-control" v-model="datosForm.jerarquia">
            <option :value="null">— Sin asignar —</option>
            <optgroup v-for="t in tiposPersonal" :key="t.id" :label="t.nombre">
              <option v-for="j in t.jerarquias" :key="j.id" :value="j.id">{{ j.nombre }}</option>
            </optgroup>
          </select>
        </div>
        <div class="form-group">
          <label class="form-label">Dependencia (lugar donde brinda servicio)</label>
          <select class="form-control" v-model="datosForm.dependencia">
            <option :value="null">— Sin asignar —</option>
            <option v-for="d in dependencias" :key="d.id" :value="d.id">{{ d.nombre }} ({{ d.ciudad_nombre }})</option>
          </select>
        </div>
        <p v-if="datosError" class="form-error">{{ datosError }}</p>
      </div>
      <div class="modal__footer">
        <button class="btn btn-secondary" @click="showDatosModal = false">Cancelar</button>
        <button class="btn btn-primary" @click="submitDatos" :disabled="datosLoading">
          {{ datosLoading ? 'Guardando...' : 'Guardar cambios' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../../services/api'
import authService from '../../services/authService'

const rolLabels = {
  admin: 'Administrador',
  personal: 'Personal',
  rrhh: 'Recursos Humanos',
  bienestar: 'Bienestar',
}

export default {
  name: 'AppHeader',
  emits: ['toggle-sidebar'],
  data() {
    return {
      showMenu: false,
      showPasswordModal: false,
      showDatosModal: false,
      passwordForm: { actual: '', nueva: '', confirmar: '' },
      passwordError: '',
      passwordLoading: false,
      datosForm: { jerarquia: null, dependencia: null },
      datosError: '',
      datosLoading: false,
      tiposPersonal: [],
      dependencias: [],
      isDark: (localStorage.getItem('theme') || 'dark') === 'dark',
    }
  },
  mounted() {
    document.documentElement.setAttribute('data-theme', this.isDark ? 'dark' : 'light')
  },
  computed: {
    usuario() {
      return authService.getUsuario()
    },
    initials() {
      if (!this.usuario?.nombre_completo) return '?'
      return this.usuario.nombre_completo
        .split(' ')
        .map((w) => w[0])
        .slice(0, 2)
        .join('')
        .toUpperCase()
    },
    rolLabel() {
      return rolLabels[this.usuario?.rol] || this.usuario?.rol
    },
    pageTitle() {
      return this.$route.name || 'Sistema de Licencias'
    },
  },
  methods: {
    toggleTheme() {
      const next = this.isDark ? 'light' : 'dark'
      document.documentElement.setAttribute('data-theme', next)
      localStorage.setItem('theme', next)
      this.isDark = next === 'dark'
    },
    cambiarPassword() {
      this.showMenu = false
      this.showPasswordModal = true
      this.passwordForm = { actual: '', nueva: '', confirmar: '' }
      this.passwordError = ''
    },
    async submitPassword() {
      this.passwordError = ''
      if (this.passwordForm.nueva !== this.passwordForm.confirmar) {
        this.passwordError = 'Las contraseñas no coinciden.'
        return
      }
      if (this.passwordForm.nueva.length < 8) {
        this.passwordError = 'La contraseña debe tener al menos 8 caracteres.'
        return
      }
      this.passwordLoading = true
      try {
        await authService.cambiarPassword(this.passwordForm.actual, this.passwordForm.nueva)
        this.showPasswordModal = false
        this.$root.showToast?.('Contraseña actualizada correctamente.', 'success')
      } catch (e) {
        this.passwordError = e.response?.data?.password_actual?.[0] || e.response?.data?.error || 'Error al cambiar contraseña.'
      } finally {
        this.passwordLoading = false
      }
    },
    async abrirActualizarDatos() {
      this.showMenu = false
      this.datosError = ''
      this.datosForm = {
        jerarquia: this.usuario?.jerarquia || null,
        dependencia: this.usuario?.dependencia || null,
      }
      this.showDatosModal = true

      // Cargar opciones
      try {
        const [tipRes, depRes] = await Promise.all([
          api.get('/jerarquias/'),
          api.get('/dependencias/'),
        ])
        this.tiposPersonal = tipRes.data.results || tipRes.data
        this.dependencias = depRes.data.results || depRes.data
      } catch (e) {
        console.error(e)
      }
    },
    async submitDatos() {
      this.datosError = ''
      this.datosLoading = true
      try {
        const res = await api.put('/auth/actualizar-perfil/', {
          jerarquia: this.datosForm.jerarquia,
          dependencia: this.datosForm.dependencia,
        })
        // Actualizar datos en localStorage
        authService.setUsuario(res.data.usuario)
        this.showDatosModal = false
        this.$root.showToast?.('Datos actualizados correctamente.', 'success')
      } catch (e) {
        this.datosError = e.response?.data?.error || 'Error al actualizar los datos.'
      } finally {
        this.datosLoading = false
      }
    },
    async cerrarSesion() {
      this.showMenu = false
      await authService.logout()
      this.$router.push('/login')
    },
  },
}
</script>

<style scoped>
.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: var(--header-height);
  padding: 0 1.5rem;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header__left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.header__menu-toggle {
  display: none;
  font-size: 1.25rem;
  padding: 0.5rem;
}

.header__page-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
}

.header__right {
  position: relative;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.theme-toggle {
  font-size: 1.125rem;
}

.header__user {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  cursor: pointer;
  padding: 0.375rem 0.5rem;
  border-radius: var(--border-radius-sm);
  transition: background var(--transition-fast);
}

.header__user:hover {
  background: var(--bg-glass);
}

.header__avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8125rem;
  font-weight: 600;
  color: white;
  flex-shrink: 0;
}

.header__user-info {
  display: flex;
  flex-direction: column;
}

.header__user-name {
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--text-primary);
  line-height: 1.3;
}

.header__user-role {
  font-size: 0.6875rem;
  color: var(--text-muted);
  line-height: 1.3;
}

.header__chevron {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.header__dropdown {
  position: absolute;
  top: calc(100% + 0.5rem);
  right: 0;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-sm);
  box-shadow: var(--shadow-xl);
  min-width: 200px;
  padding: 0.25rem;
  z-index: 200;
  animation: scaleIn 0.15s ease;
}

.header__dropdown-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  width: 100%;
  padding: 0.625rem 0.75rem;
  font-size: 0.8125rem;
  color: var(--text-secondary);
  background: none;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all var(--transition-fast);
  font-family: var(--font-family);
  text-align: left;
}

.header__dropdown-item:hover {
  background: var(--bg-glass);
  color: var(--text-primary);
}

.header__dropdown-item--danger:hover {
  color: var(--accent-danger);
}

.header__dropdown-divider {
  border: none;
  border-top: 1px solid var(--border-color);
  margin: 0.25rem 0;
}

.header__overlay {
  position: fixed;
  inset: 0;
  z-index: 99;
}

.menu-icon {
  font-size: 1.125rem;
}

/* Perfil actual info */
.perfil-actual {
  background: var(--bg-glass);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-md);
  padding: 0.75rem 1rem;
  margin-bottom: 1rem;
}

.perfil-actual__item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.25rem 0;
}

.perfil-actual__label {
  font-size: 0.8125rem;
  color: var(--text-muted);
}

.perfil-actual__value {
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--text-primary);
}

@media (max-width: 768px) {
  .app-header {
    padding: 0 1rem;
  }

  .header__menu-toggle {
    display: flex;
  }

  .header__user-info {
    display: none;
  }

  .header__chevron {
    display: none;
  }
}
</style>
