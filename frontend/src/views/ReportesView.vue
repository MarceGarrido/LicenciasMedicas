<template>
  <div class="reportes">
    <div class="page-header">
      <div>
        <h1 class="page-header__title">Reportes y Estadísticas</h1>
        <p class="page-header__subtitle">Análisis de licencias del personal</p>
      </div>
      <div class="page-header__actions">
        <button class="btn btn-secondary btn-sm" @click="exportar('excel')">📊 Excel</button>
        <button class="btn btn-secondary btn-sm" @click="exportar('pdf')">📄 PDF</button>
      </div>
    </div>



    <div v-if="loading" class="loading-overlay"><div class="spinner spinner--lg"></div></div>

    <template v-else>
      <!-- Nueva sección: Licencias activas por dependencia (Estilo Excel) -->
      <div class="glass-card mb-6">
        <div class="flex items-center justify-between mb-4">
          <h3 style="margin:0">Licencias Activas Hoy por Dependencia</h3>
          <div class="form-group" style="margin:0; min-width:200px">
            <select class="form-control" v-model="filtroCiudadActivas">
              <option value="">Todas las ciudades</option>
              <option v-for="c in ciudades" :key="c.id" :value="c.id">{{ c.nombre }}</option>
            </select>
          </div>
        </div>
        
        <div v-if="!datos.dependencias_activas || dependenciasActivasFiltradas.length === 0" class="empty-state">
          <div class="empty-state__icon">🏢</div>
          <div class="empty-state__title">No hay licencias activas en el día de hoy para esta ciudad</div>
        </div>
        <div v-else style="overflow-x:auto">
          <table class="data-table">
            <thead>
              <tr>
                <th>Dependencia</th>
                <th>Ciudad</th>
                <th class="text-center">Personal Faltante (Licencias Activas)</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="dep in dependenciasActivasFiltradas" :key="dep.usuario__dependencia__id">
                <td class="font-semibold">{{ dep.usuario__dependencia__nombre || 'Sin Dependencia' }}</td>
                <td class="text-sm text-muted">{{ dep.usuario__dependencia__ciudad__nombre || '—' }}</td>
                <td class="text-center">
                  <span class="badge badge-warning" style="font-size:1rem; padding:0.25rem 0.75rem;">
                    {{ dep.total_activas }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Stats -->
      <div class="stats-grid mb-6">
        <div class="glass-card stat-card">
          <div class="stat-card__icon" style="background:var(--accent-primary-light)">📊</div>
          <div class="stat-card__value">{{ datos.total }}</div>
          <div class="stat-card__label">Total Licencias Histórico</div>
        </div>
        <div class="glass-card stat-card" v-for="t in datos.por_tipo" :key="t.tipo">
          <div class="stat-card__icon" :style="{ background: t.tipo === 'salud' ? 'var(--accent-warning-light)' : 'var(--accent-info-light)' }">
            {{ t.tipo === 'salud' ? '🏥' : '📋' }}
          </div>
          <div class="stat-card__value">{{ t.total }}</div>
          <div class="stat-card__label">{{ t.tipo === 'salud' ? 'Razón de Salud' : 'Razón Atendible' }}</div>
        </div>
      </div>

      <!-- Charts removidos temporalmente -->
    </template>
  </div>
</template>

<script>
import { Chart, registerables } from 'chart.js'
import api from '../services/api'

Chart.register(...registerables)

export default {
  name: 'ReportesView',
  inject: ['showToast'],
  data() {
    return {
      datos: { total: 0, por_tipo: [], por_estado: [], por_mes: [], por_dependencia: [], por_ciudad: [], dependencias_activas: [] },
      ciudades: [],
      loading: true,
      filtro: { fecha_desde: '', fecha_hasta: '' },
      filtroCiudadActivas: '',
      charts: [],
    }
  },
  computed: {
    dependenciasActivasFiltradas() {
      let lista = this.datos.dependencias_activas || []
      if (this.filtroCiudadActivas) {
        lista = lista.filter(d => d.usuario__dependencia__ciudad__id == this.filtroCiudadActivas)
      }
      return lista
    }
  },
  async mounted() {
    await Promise.all([this.cargar(), this.cargarAux()])
  },
  beforeUnmount() {
    this.charts.forEach(c => c.destroy())
  },
  methods: {
    async cargar() {
      this.loading = true
      try {
        const params = {}
        if (this.filtro.fecha_desde) params.fecha_desde = this.filtro.fecha_desde
        if (this.filtro.fecha_hasta) params.fecha_hasta = this.filtro.fecha_hasta
        const res = await api.get('/reportes/resumen/', { params })
        this.datos = res.data
        this.$nextTick(() => this.renderCharts())
      } catch (e) {
        console.error(e)
      } finally {
        this.loading = false
      }
    },
    async cargarAux() {
      try {
        const res = await api.get('/ciudades/')
        this.ciudades = res.data.results || res.data
      } catch (e) { console.error(e) }
    },
    resetFiltros() {
      this.filtro = { fecha_desde: '', fecha_hasta: '' }
      this.cargar()
    },
    renderCharts() {
      this.charts.forEach(c => c.destroy())
      this.charts = []

      const chartOpts = {
        responsive: true,
        maintainAspectRatio: true,
        plugins: { legend: { labels: { color: '#9ca3af' } } },
        scales: {
          x: { ticks: { color: '#6b7280' }, grid: { color: 'rgba(255,255,255,0.05)' } },
          y: { ticks: { color: '#6b7280' }, grid: { color: 'rgba(255,255,255,0.05)' }, beginAtZero: true },
        },
      }

      // Gráficos desactivados temporalmente a petición del usuario.
    },
    async exportar(formato) {
      try {
        const params = { ...this.filtro }
        const res = await api.get(`/reportes/exportar/${formato}/`, { params, responseType: 'blob' })
        const ext = formato === 'excel' ? 'xlsx' : 'pdf'
        const url = URL.createObjectURL(res.data)
        const a = document.createElement('a')
        a.href = url
        a.download = `reporte_licencias.${ext}`
        a.click()
        URL.revokeObjectURL(url)
      } catch (e) {
        this.showToast(`Error al exportar ${formato}.`, 'error')
      }
    },
  },
}
</script>

<style scoped>
.filters { display: flex; gap: 0.75rem; align-items: flex-end; flex-wrap: wrap; }
.flex { display: flex; }
.items-center { align-items: center; }
.justify-between { justify-content: space-between; }
</style>
