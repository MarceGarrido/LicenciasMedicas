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
        <table class="data-table">
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
                <select class="form-control" style="padding:0.25rem 0.5rem;font-size:0.8125rem;min-width:110px" :value="l.estado" @change="cambiarEstado(l, $event.target.value)">
                  <option value="iniciada">Iniciada</option>
                  <option value="en_curso">En Curso</option>
                  <option value="finalizada">Finalizada</option>
                </select>
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
                <button v-if="tieneRol(['admin'])" class="btn btn-ghost btn-sm text-danger" @click="eliminarLicencia(l.id)" title="Eliminar licencia">🗑️</button>
              </td>
            </tr>
          </tbody>
        </table>
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
      try {
        await api.patch(`/licencias/${l.id}/`, { estado: nuevoEstado })
        l.estado = nuevoEstado
        this.showToast('Estado actualizado.', 'success')
      } catch (e) {
        this.showToast('Error al actualizar estado.', 'error')
        await this.cargar()
      }
    },
    async descargarCert(l) {
      try {
        const res = await api.get(`/licencias/${l.id}/certificado/descargar/`, { responseType: 'blob' })
        const url = URL.createObjectURL(res.data)
        const a = document.createElement('a')
        a.href = url
        a.download = `certificado_${l.usuario_nombre}.pdf`
        a.click()
        URL.revokeObjectURL(url)
      } catch (e) {
        this.showToast('Error al descargar certificado.', 'error')
      }
    },
    async eliminarLicencia(id) {
      if (!confirm('¿Estás seguro de que deseas eliminar esta licencia? Esta acción no se puede deshacer.')) return
      try {
        await api.delete(`/licencias/${id}/`)
        this.showToast('Licencia eliminada.', 'success')
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
@media (max-width: 768px) {
  .filters { flex-direction: column; }
  .filters .form-group { min-width: auto; }
}
</style>
