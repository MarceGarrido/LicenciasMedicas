<template>
  <div class="dashboard">
    <div class="page-header">
      <div>
        <h1 class="page-header__title">Bienvenido, {{ usuario?.nombre_completo }}</h1>
        <p class="page-header__subtitle">{{ rolLabel }} · {{ fechaHoy }}</p>
      </div>
    </div>

    <!-- Stats Cards -->
    <div v-if="!loading" class="stats-grid mb-6">
      <div class="glass-card stat-card" v-for="stat in stats" :key="stat.label">
        <div class="stat-card__icon" :style="{ background: stat.bg }">{{ stat.icon }}</div>
        <div class="stat-card__value">{{ stat.value }}</div>
        <div class="stat-card__label">{{ stat.label }}</div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="glass-card mb-6">
      <h3 class="mb-4">Acciones rápidas</h3>
      <div class="quick-actions">
        <router-link v-if="tieneRol(['personal', 'admin'])" to="/licencias/nueva" class="quick-action">
          <span class="quick-action__icon">➕</span>
          <span class="quick-action__text">Nueva Licencia</span>
        </router-link>
        <router-link to="/circulares" class="quick-action">
          <span class="quick-action__icon">📋</span>
          <span class="quick-action__text">Ver Circulares</span>
        </router-link>
        <router-link v-if="tieneRol(['rrhh', 'admin'])" to="/circulares/gestionar" class="quick-action">
          <span class="quick-action__icon">📤</span>
          <span class="quick-action__text">Subir Circular</span>
        </router-link>
        <router-link v-if="tieneRol(['bienestar', 'admin'])" to="/licencias/gestion" class="quick-action">
          <span class="quick-action__icon">📑</span>
          <span class="quick-action__text">Ver Licencias</span>
        </router-link>
        <router-link v-if="tieneRol(['bienestar', 'admin'])" to="/reportes" class="quick-action">
          <span class="quick-action__icon">📈</span>
          <span class="quick-action__text">Reportes</span>
        </router-link>
        <router-link v-if="tieneRol(['admin'])" to="/admin/usuarios" class="quick-action">
          <span class="quick-action__icon">👤</span>
          <span class="quick-action__text">Gestionar Usuarios</span>
        </router-link>
      </div>
    </div>

    <!-- Recent circulars -->
    <div class="glass-card">
      <div class="flex items-center justify-between mb-4">
        <h3>Últimas Circulares</h3>
        <router-link to="/circulares" class="btn btn-ghost btn-sm">Ver todas →</router-link>
      </div>
      <div v-if="circulares.length === 0" class="text-center p-4 text-muted border border-dashed rounded-lg" style="border-color: var(--border-color)">
        <div style="font-size: 2rem; margin-bottom: 0.5rem; opacity: 0.5">📋</div>
        <div>No hay circulares recientes publicadas.</div>
      </div>
      <div v-else class="circulares-list">
        <div v-for="c in circulares" :key="c.id" class="circular-item">
          <div class="circular-item__icon">📄</div>
          <div class="circular-item__info">
            <span class="circular-item__title">{{ c.titulo }}</span>
            <span class="circular-item__date">{{ formatDate(c.fecha_publicacion) }}</span>
          </div>
          <a :href="c.archivo_url" target="_blank" class="btn btn-ghost btn-sm">Ver</a>
        </div>
      </div>
    </div>

    <div v-if="loading" class="loading-overlay">
      <div class="spinner spinner--lg"></div>
      <span>Cargando dashboard...</span>
    </div>
  </div>
</template>

<script>
import api from '../services/api'
import authService from '../services/authService'

const rolLabels = {
  admin: 'Administrador',
  personal: 'Personal',
  rrhh: 'Recursos Humanos',
  bienestar: 'Bienestar',
}

export default {
  name: 'DashboardView',
  data() {
    return {
      loading: true,
      circulares: [],
      licenciasCount: 0,
      licenciasActivas: 0,
      personalCount: 0,
    }
  },
  computed: {
    usuario() {
      return authService.getUsuario()
    },
    rolLabel() {
      return rolLabels[this.usuario?.rol] || ''
    },
    fechaHoy() {
      return new Date().toLocaleDateString('es-AR', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      })
    },
    stats() {
      const s = []
      const rol = this.usuario?.rol

      if (rol === 'personal') {
        s.push(
          { icon: '📁', label: 'Mis Licencias', value: this.licenciasCount, bg: 'var(--accent-primary-light)' },
          { icon: '🔔', label: 'Activas', value: this.licenciasActivas, bg: 'var(--accent-warning-light)' },
          { icon: '📋', label: 'Circulares', value: this.circulares.length, bg: 'var(--accent-info-light)' },
        )
      } else if (rol === 'bienestar') {
        s.push(
          { icon: '📑', label: 'Total Licencias', value: this.licenciasCount, bg: 'var(--accent-primary-light)' },
          { icon: '🔔', label: 'Licencias Activas', value: this.licenciasActivas, bg: 'var(--accent-warning-light)' },
          { icon: '👥', label: 'Personal', value: this.personalCount, bg: 'var(--accent-success-light)' },
          { icon: '📋', label: 'Circulares', value: this.circulares.length, bg: 'var(--accent-info-light)' },
        )
      } else if (rol === 'rrhh') {
        s.push(
          { icon: '📋', label: 'Circulares', value: this.circulares.length, bg: 'var(--accent-primary-light)' },
          { icon: '👥', label: 'Personal', value: this.personalCount, bg: 'var(--accent-success-light)' },
        )
      } else {
        // admin
        s.push(
          { icon: '📑', label: 'Total Licencias', value: this.licenciasCount, bg: 'var(--accent-primary-light)' },
          { icon: '🔔', label: 'Activas', value: this.licenciasActivas, bg: 'var(--accent-warning-light)' },
          { icon: '👥', label: 'Personal', value: this.personalCount, bg: 'var(--accent-success-light)' },
          { icon: '📋', label: 'Circulares', value: this.circulares.length, bg: 'var(--accent-info-light)' },
        )
      }
      return s
    },
  },
  async mounted() {
    await this.cargarDatos()
  },
  methods: {
    async cargarDatos() {
      this.loading = true
      try {
        const fetchPersonal = this.tieneRol(['bienestar', 'rrhh', 'admin'])
        const requests = [
          api.get('/circulares/', { params: { page_size: 5 } }),
          api.get('/licencias/'),
        ]
        if (fetchPersonal) {
          requests.push(api.get('/personal/').catch(() => ({ data: [] })))
        }

        const responses = await Promise.all(requests)
        
        const circularesRes = responses[0]
        const licenciasRes = responses[1]
        
        this.circulares = (circularesRes.data.results || circularesRes.data).slice(0, 5)
        const licencias = licenciasRes.data.results || licenciasRes.data
        this.licenciasCount = licenciasRes.data.count || licencias.length
        this.licenciasActivas = licencias.filter(l => ['iniciada', 'en_curso'].includes(l.estado)).length

        if (fetchPersonal && responses[2]) {
          const personal = responses[2].data.results || responses[2].data
          this.personalCount = Array.isArray(personal) ? personal.length : 0
        }
      } catch (e) {
        console.error('Error cargando dashboard:', e)
      } finally {
        this.loading = false
      }
    },
    tieneRol(roles) {
      const usuario = authService.getUsuario()
      if (!usuario) return false
      if (usuario.rol === 'admin') return true
      return roles.includes(usuario.rol)
    },
    formatDate(dateStr) {
      if (!dateStr) return ''
      return new Date(dateStr).toLocaleDateString('es-AR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
      })
    },
  },
}
</script>

<style scoped>
.quick-actions {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 0.75rem;
}

.quick-action {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 1.25rem 1rem;
  background: var(--bg-glass);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  text-decoration: none;
  color: var(--text-secondary);
  transition: all var(--transition-base);
  cursor: pointer;
}

.quick-action:hover {
  background: var(--bg-glass-hover);
  border-color: var(--accent-primary);
  color: var(--text-primary);
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.quick-action__icon {
  font-size: 1.5rem;
}

.quick-action__text {
  font-size: 0.8125rem;
  font-weight: 500;
  text-align: center;
}

.circulares-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.circular-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  border-radius: var(--border-radius-sm);
  transition: background var(--transition-fast);
}

.circular-item:hover {
  background: var(--bg-glass);
}

.circular-item__icon {
  font-size: 1.25rem;
  flex-shrink: 0;
}

.circular-item__info {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.circular-item__title {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.circular-item__date {
  font-size: 0.75rem;
  color: var(--text-muted);
}

@media (max-width: 480px) {
  .quick-actions {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
