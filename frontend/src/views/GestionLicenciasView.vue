<template>
  <div class="gestion-licencias">
    <div class="page-header">
      <div>
        <h1 class="page-header__title">Gestión de Licencias</h1>
        <p class="page-header__subtitle">Todas las licencias del personal</p>
      </div>
      <div class="page-header__actions">
        <button class="btn btn-sm" :class="vistaAgrupada ? 'btn-primary' : 'btn-secondary'" @click="vistaAgrupada = !vistaAgrupada">
          🏢 {{ vistaAgrupada ? 'Vista agrupada' : 'Agrupar por dependencia' }}
        </button>
        <button class="btn btn-secondary btn-sm" @click="exportarExcel">📊 Excel</button>
        <button class="btn btn-secondary btn-sm" @click="exportarPDF">📄 PDF</button>
      </div>
    </div>

    <!-- Filters -->
    <div class="glass-card mb-4">
      <div class="filters">
        <div class="form-group" style="margin:0">
          <select class="form-control" v-model="filtro.ciudad" @change="onCiudadChange">
            <option value="">Todas las ciudades</option>
            <option v-for="c in ciudades" :key="c.id" :value="c.id">{{ c.nombre }}</option>
          </select>
        </div>
        <div class="form-group" style="margin:0">
          <select class="form-control" v-model="filtro.dependencia" @change="cargar">
            <option value="">Todas las dependencias</option>
            <option v-for="d in dependenciasFiltradas" :key="d.id" :value="d.id">{{ d.nombre }}</option>
          </select>
        </div>
        <div class="form-group" style="margin:0">
          <select class="form-control" v-model="filtro.tipo" @change="cargar">
            <option value="">Todos los tipos</option>
            <option value="salud">Razón de Salud</option>
            <option value="atendible">Razón Atendible</option>
          </select>
        </div>
        <div class="form-group" style="margin:0">
          <select class="form-control" v-model="filtro.estado" @change="cargar">
            <option value="">Todos los estados</option>
            <option value="iniciada">Iniciada</option>
            <option value="en_curso">En Curso</option>
            <option value="finalizada">Finalizada</option>
          </select>
        </div>
        <div class="form-group" style="margin:0">
          <input type="date" class="form-control" v-model="filtro.fecha_desde" @change="cargar" placeholder="Desde" />
        </div>
        <div class="form-group" style="margin:0">
          <input type="date" class="form-control" v-model="filtro.fecha_hasta" @change="cargar" placeholder="Hasta" />
        </div>
      </div>
    </div>

    <div v-if="loading" class="loading-overlay"><div class="spinner spinner--lg"></div></div>

    <!-- Vista agrupada por dependencia -->
    <div v-else-if="vistaAgrupada">
      <div v-if="Object.keys(licenciasPorDependencia).length === 0" class="glass-card empty-state">
        <div class="empty-state__icon">📑</div>
        <div class="empty-state__title">No hay licencias con los filtros seleccionados</div>
      </div>
      <div v-for="(grupo, dep) in licenciasPorDependencia" :key="dep" class="glass-card mb-4">
        <div class="grupo-header" @click="grupo.abierto = !grupo.abierto">
          <div class="grupo-header__info">
            <span class="grupo-header__icon">🏢</span>
            <span class="grupo-header__nombre">{{ dep }}</span>
            <span class="badge badge-primary">{{ grupo.licencias.length }}</span>
          </div>
          <span class="grupo-header__toggle">{{ grupo.abierto ? '▲' : '▼' }}</span>
        </div>
        <div v-if="grupo.abierto" style="overflow-x:auto">
          <table class="data-table">
            <thead>
              <tr>
                <th>Personal</th>
                <th>Tipo</th>
                <th>Estado</th>
                <th>Inicio</th>
                <th>Fin</th>
                <th>Días</th>
                <th>Cert.</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="l in grupo.licencias" :key="l.id">
                <td>
                  <div class="font-semibold text-sm">{{ l.usuario_nombre }}</div>
                  <div class="text-xs text-muted">{{ l.usuario_jerarquia }}</div>
                </td>
                <td><span :class="['badge', l.tipo === 'salud' ? 'badge-warning' : 'badge-info']">{{ l.tipo_display }}</span></td>
                <td>
                  <span class="badge" :class="{'badge-primary': l.estado === 'iniciada', 'badge-warning': l.estado === 'en_curso', 'badge-success': l.estado === 'finalizada'}">{{ l.estado_display }}</span>
                </td>
                <td class="text-sm">{{ formatDate(l.fecha_inicio) }}</td>
                <td class="text-sm">{{ formatDate(l.fecha_fin) }}</td>
                <td class="text-sm text-center">{{ l.dias_licencia }}</td>
                <td class="text-center">
                  <button v-if="l.tiene_certificado" class="btn btn-ghost btn-sm" @click="descargarCert(l)" title="Descargar certificado">📎</button>
                  <span v-else class="text-muted text-xs">—</span>
                </td>
                <td>
                  <router-link :to="`/personal/${l.usuario}/historial`" class="btn btn-ghost btn-sm" title="Ver historial">👤</router-link>
                  <button v-if="tieneRol(['admin'])" class="btn btn-ghost btn-sm text-danger" @click="confirmarEliminar(l)" title="Eliminar licencia">🗑️</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Vista plana (original) -->
    <div v-else class="glass-card">
      <div v-if="licencias.length === 0" class="empty-state">
        <div class="empty-state__icon">📑</div>
        <div class="empty-state__title">No hay licencias</div>
      </div>
      <div v-else style="overflow-x:auto">
        <table class="data-table hidden-mobile">
          <thead>
            <tr>
              <th>Personal</th>
              <th>Dependencia</th>
              <th>Tipo</th>
              <th>Estado</th>
              <th>Inicio</th>
              <th>Fin</th>
              <th>Días</th>
              <th>Cert.</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="l in licenciasFiltradas" :key="l.id">
              <td>
                <div class="font-semibold text-sm">{{ l.usuario_nombre }}</div>
                <div class="text-xs text-muted">{{ l.usuario_jerarquia }}</div>
              </td>
              <td class="text-sm">{{ l.usuario_dependencia }}<br><span class="text-xs text-muted">{{ l.usuario_ciudad }}</span></td>
              <td><span :class="['badge', l.tipo === 'salud' ? 'badge-warning' : 'badge-info']">{{ l.tipo_display }}</span></td>
              <td>
                <span class="badge" :class="{'badge-primary': l.estado === 'iniciada', 'badge-warning': l.estado === 'en_curso', 'badge-success': l.estado === 'finalizada'}">{{ l.estado_display }}</span>
              </td>
              <td class="text-sm">{{ formatDate(l.fecha_inicio) }}</td>
              <td class="text-sm">{{ formatDate(l.fecha_fin) }}</td>
              <td class="text-sm text-center">{{ l.dias_licencia }}</td>
              <td class="text-center">
                <button v-if="l.tiene_certificado" class="btn btn-ghost btn-sm" @click="descargarCert(l)" title="Descargar certificado">📎</button>
                <span v-else class="text-muted text-xs">—</span>
              </td>
              <td>
                <router-link :to="`/personal/${l.usuario}/historial`" class="btn btn-ghost btn-sm" title="Ver historial">👤</router-link>
                <button v-if="tieneRol(['admin'])" class="btn btn-ghost btn-sm text-danger" @click="confirmarEliminar(l)" title="Eliminar licencia">🗑️</button>
              </td>
            </tr>
          </tbody>
        </table>

        <!-- Mobile cards view -->
        <div class="mobile-cards show-mobile">
          <div v-for="l in licenciasFiltradas" :key="`mob-${l.id}`" class="licencia-mob-card">
            <div class="flex justify-between items-start mb-2">
              <div>
                <div class="font-semibold">{{ l.usuario_nombre }}</div>
                <div class="text-xs text-muted">{{ l.usuario_jerarquia }} - {{ l.usuario_dependencia }}</div>
              </div>
              <span :class="['badge', l.tipo === 'salud' ? 'badge-warning' : 'badge-info']">{{ l.tipo_display }}</span>
            </div>
            
            <div class="flex justify-between items-center mb-3">
              <div class="text-sm">
                {{ formatDate(l.fecha_inicio) }} <span class="text-muted mx-1">→</span> {{ formatDate(l.fecha_fin) }}
                <div class="text-xs text-muted mt-1">{{ l.dias_licencia }} días</div>
              </div>
              <div>
                <button v-if="l.tiene_certificado" class="btn btn-ghost btn-sm" @click="descargarCert(l)" title="Descargar certificado">📎 Cert.</button>
              </div>
            </div>

            <div class="flex gap-2 items-center">
              <div class="flex-1">
                <span class="badge" :class="{'badge-primary': l.estado === 'iniciada', 'badge-warning': l.estado === 'en_curso', 'badge-success': l.estado === 'finalizada'}">{{ l.estado_display }}</span>
              </div>
              <router-link :to="`/personal/${l.usuario}/historial`" class="btn btn-secondary btn-icon" title="Ver historial">👤</router-link>
              <button v-if="tieneRol(['admin'])" class="btn btn-secondary btn-icon text-danger" @click="confirmarEliminar(l)" title="Eliminar licencia">🗑️</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal confirmación de eliminación -->
    <div v-if="licenciaToDelete" class="modal-overlay" @click.self="licenciaToDelete = null">
      <div class="modal">
        <div class="modal__header">
          <h3 class="modal__title text-danger">Eliminar Licencia</h3>
          <button class="btn-ghost btn-icon" @click="licenciaToDelete = null">✕</button>
        </div>
        <div class="modal__body">
          <p>¿Estás seguro de que deseas eliminar la licencia de <strong>{{ licenciaToDelete.usuario_nombre }}</strong>?</p>
          <p class="text-sm text-muted mt-2">Esta acción no se puede deshacer.</p>
        </div>
        <div class="modal__footer">
          <button class="btn btn-secondary" @click="licenciaToDelete = null">Cancelar</button>
          <button class="btn btn-danger" @click="eliminarLicencia">Sí, eliminar</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../services/api'
import authService from '../services/authService'

export default {
  name: 'GestionLicenciasView',
  inject: ['showToast'],
  data() {
    return {
      licencias: [],
      ciudades: [],
      dependencias: [],
      loading: true,
      vistaAgrupada: false,
      filtro: { tipo: '', estado: '', fecha_desde: '', fecha_hasta: '', ciudad: '', dependencia: '' },
      licenciaToDelete: null,
    }
  },
  computed: {
    dependenciasFiltradas() {
      if (!this.filtro.ciudad) return this.dependencias
      return this.dependencias.filter(d => d.ciudad == this.filtro.ciudad)
    },
    licenciasFiltradas() {
      let lista = this.licencias
      if (this.filtro.dependencia) {
        const depNombre = this.dependencias.find(d => d.id == this.filtro.dependencia)?.nombre
        if (depNombre) lista = lista.filter(l => l.usuario_dependencia === depNombre)
      }
      if (this.filtro.ciudad) {
        const ciudadNombre = this.ciudades.find(c => c.id == this.filtro.ciudad)?.nombre
        if (ciudadNombre) lista = lista.filter(l => l.usuario_ciudad === ciudadNombre)
      }
      return lista
    },
    licenciasPorDependencia() {
      const grupos = {}
      for (const l of this.licenciasFiltradas) {
        const dep = l.usuario_dependencia || 'Sin dependencia'
        if (!grupos[dep]) {
          grupos[dep] = { licencias: [], abierto: true }
        }
        grupos[dep].licencias.push(l)
      }
      const sorted = {}
      for (const key of Object.keys(grupos).sort()) {
        sorted[key] = grupos[key]
      }
      return sorted
    },
  },
  async mounted() {
    await Promise.all([this.cargar(), this.cargarAux()])
  },
  methods: {
    async cargar() {
      this.loading = true
      try {
        const params = {}
        if (this.filtro.tipo) params.tipo = this.filtro.tipo
        if (this.filtro.estado) params.estado = this.filtro.estado
        if (this.filtro.fecha_desde) params.fecha_desde = this.filtro.fecha_desde
        if (this.filtro.fecha_hasta) params.fecha_hasta = this.filtro.fecha_hasta
        const res = await api.get('/licencias/', { params })
        this.licencias = res.data.results || res.data
      } catch (e) {
        this.error = 'Error al cargar los datos.'
      } finally {
        this.loading = false
      }
    },
    async cargarAux() {
      try {
        const [ciuRes, depRes] = await Promise.all([
          api.get('/ciudades/'),
          api.get('/dependencias/'),
        ])
        this.ciudades = ciuRes.data.results || ciuRes.data
        this.dependencias = depRes.data.results || depRes.data
      } catch (e) { console.error(e) }
    },
    onCiudadChange() {
      this.filtro.dependencia = ''
      this.cargar()
    },
    async descargarCert(l) {
      try {
        const res = await api.get(`/licencias/${l.id}/certificado/descargar/`, { responseType: 'blob' })
        const type = res.data.type || ''
        let ext = 'pdf'
        if (type.includes('jpeg') || type.includes('jpg')) ext = 'jpg'
        else if (type.includes('png')) ext = 'png'
        else if (type.includes('msword') || type.includes('doc')) ext = 'docx'

        const url = URL.createObjectURL(res.data)
        const a = document.createElement('a')
        a.href = url
        a.download = `certificado_${l.usuario_nombre}.${ext}`
        a.click()
        URL.revokeObjectURL(url)
      } catch (e) {
        this.showToast('Error al descargar certificado.', 'error')
      }
    },
    confirmarEliminar(l) {
      this.licenciaToDelete = l
    },
    async eliminarLicencia() {
      if (!this.licenciaToDelete) return
      try {
        await api.delete(`/licencias/${this.licenciaToDelete.id}/`)
        this.showToast('Licencia eliminada.', 'success')
        this.licenciaToDelete = null
        await this.cargar()
      } catch (e) {
        this.showToast('Error al eliminar licencia.', 'error')
      }
    },
    exportarExcel() {
      this.exportar('excel')
    },
    exportarPDF() {
      this.exportar('pdf')
    },
    async exportar(formato) {
      try {
        const params = { ...this.filtro }
        const res = await api.get(`/reportes/exportar/${formato}/`, { params, responseType: 'blob' })
        const ext = formato === 'excel' ? 'xlsx' : 'pdf'
        const url = URL.createObjectURL(res.data)
        const a = document.createElement('a')
        a.href = url
        a.download = `licencias.${ext}`
        a.click()
        URL.revokeObjectURL(url)
      } catch (e) {
        this.showToast(`Error al exportar ${formato}.`, 'error')
      }
    },
    formatDate(d) {
      if (!d) return ''
      return new Date(d).toLocaleDateString('es-AR', { day: '2-digit', month: '2-digit', year: 'numeric' })
    },
    tieneRol(roles) {
      const usuario = authService.getUsuario()
      if (!usuario) return false
      if (usuario.rol === 'admin') return true
      return roles.includes(usuario.rol)
    },
  },
}
</script>

<style scoped>
.filters {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}
.filters .form-group {
  flex: 1;
  min-width: 150px;
}
.show-mobile { display: none; }
.hidden-mobile { display: table; }

.licencia-mob-card {
  padding: 1rem;
  border-bottom: 1px solid var(--border-color);
}
.licencia-mob-card:last-child {
  border-bottom: none;
}
.mx-1 { margin: 0 0.25rem; }

/* Grupo por dependencia */
.grupo-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  cursor: pointer;
  user-select: none;
  transition: background var(--transition-fast);
  border-radius: var(--border-radius-md);
}

.grupo-header:hover {
  background: var(--bg-glass);
}

.grupo-header__info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.grupo-header__icon {
  font-size: 1.25rem;
}

.grupo-header__nombre {
  font-weight: 600;
  font-size: 0.9375rem;
  color: var(--text-primary);
}

.grupo-header__toggle {
  color: var(--text-muted);
  font-size: 0.75rem;
}

.mb-4 {
  margin-bottom: 1rem;
}

@media (max-width: 768px) {
  .filters { flex-direction: column; }
  .filters .form-group { min-width: auto; }
  
  .show-mobile { display: block; }
  .hidden-mobile { display: none; }
}
</style>
