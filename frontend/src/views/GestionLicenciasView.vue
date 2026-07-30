<template>
  <div class="gestion-licencias">
    <div class="page-header">
      <div>
        <h1 class="page-header__title">Gestión de Licencias</h1>
        <p class="page-header__subtitle">Todas las licencias del personal</p>
      </div>
      <div class="page-header__actions">
        <button class="btn btn-secondary btn-sm" @click="exportarExcel">📊 Excel</button>
        <button class="btn btn-secondary btn-sm" @click="exportarPDF">📄 PDF</button>
      </div>
    </div>

    <!-- Filters -->
    <div class="glass-card mb-4">
      <div class="filters">
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
            <tr v-for="l in licencias" :key="l.id">
              <td>
                <div class="font-semibold text-sm">{{ l.usuario_nombre }}</div>
                <div class="text-xs text-muted">{{ l.usuario_jerarquia }}</div>
              </td>
              <td class="text-sm">{{ l.usuario_dependencia }}<br><span class="text-xs text-muted">{{ l.usuario_ciudad }}</span></td>
              <td><span :class="['badge', l.tipo === 'salud' ? 'badge-warning' : 'badge-info']">{{ l.tipo_display }}</span></td>
              <td>
                <div class="flex items-center gap-1">
                  <span class="badge" :class="{'badge-primary': l.estado === 'iniciada', 'badge-warning': l.estado === 'en_curso', 'badge-success': l.estado === 'finalizada', 'badge-danger': l.estado === 'rechazada'}">{{ l.estado_display }}</span>
                  <button v-if="l.estado !== 'rechazada' && tieneRol(['bienestar', 'admin'])" class="btn btn-ghost btn-sm text-danger" style="padding:0;width:24px;height:24px" title="Rechazar licencia" @click="cambiarEstado(l, 'rechazada')">✖</button>
                </div>
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
          <div v-for="l in licencias" :key="`mob-${l.id}`" class="licencia-mob-card">
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
                <span class="badge" :class="{'badge-primary': l.estado === 'iniciada', 'badge-warning': l.estado === 'en_curso', 'badge-success': l.estado === 'finalizada', 'badge-danger': l.estado === 'rechazada'}">{{ l.estado_display }}</span>
              </div>
              <button v-if="l.estado !== 'rechazada' && tieneRol(['bienestar', 'admin'])" class="btn btn-secondary btn-icon text-danger" title="Rechazar" @click="cambiarEstado(l, 'rechazada')">✖</button>
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
      loading: true,
      filtro: { tipo: '', estado: '', fecha_desde: '', fecha_hasta: '' },
      licenciaToDelete: null,
    }
  },
  async mounted() {
    await this.cargar()
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
        console.error(e)
      } finally {
        this.loading = false
      }
    },
    async cambiarEstado(l, nuevoEstado) {
      if (nuevoEstado === 'rechazada' && !confirm('¿Estás seguro de que deseas rechazar esta licencia? Esta acción no cambiará los estados automáticos si te equivocas.')) {
        return
      }
      try {
        await api.patch(`/licencias/${l.id}/`, { estado: nuevoEstado })
        this.showToast('Estado actualizado.', 'success')
        await this.cargar()
      } catch (e) {
        this.showToast('Error al actualizar estado.', 'error')
      }
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

@media (max-width: 768px) {
  .filters { flex-direction: column; }
  .filters .form-group { min-width: auto; }
  
  .show-mobile { display: block; }
  .hidden-mobile { display: none; }
}
</style>
