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

    <!-- Filtros de fecha -->
    <div class="glass-card mb-4">
      <div class="filters">
        <div class="form-group" style="margin:0">
          <label class="form-label">Desde</label>
          <input type="date" class="form-control" v-model="filtro.fecha_desde" @change="cargar" />
        </div>
        <div class="form-group" style="margin:0">
          <label class="form-label">Hasta</label>
          <input type="date" class="form-control" v-model="filtro.fecha_hasta" @change="cargar" />
        </div>
        <div style="display:flex;align-items:flex-end">
          <button class="btn btn-ghost btn-sm" @click="resetFiltros">Limpiar filtros</button>
        </div>
      </div>
    </div>

    <div v-if="loading" class="loading-overlay"><div class="spinner spinner--lg"></div></div>

    <template v-else>
      <!-- Stats -->
      <div class="stats-grid mb-6">
        <div class="glass-card stat-card">
          <div class="stat-card__icon" style="background:var(--accent-primary-light)">📊</div>
          <div class="stat-card__value">{{ datos.total }}</div>
          <div class="stat-card__label">Total Licencias</div>
        </div>
        <div class="glass-card stat-card" v-for="t in datos.por_tipo" :key="t.tipo">
          <div class="stat-card__icon" :style="{ background: t.tipo === 'salud' ? 'var(--accent-warning-light)' : 'var(--accent-info-light)' }">
            {{ t.tipo === 'salud' ? '🏥' : '📋' }}
          </div>
          <div class="stat-card__value">{{ t.total }}</div>
          <div class="stat-card__label">{{ t.tipo === 'salud' ? 'Razón de Salud' : 'Razón Atendible' }}</div>
        </div>
      </div>

      <!-- Charts -->
      <div class="grid grid-cols-2 mb-6">
        <div class="glass-card">
          <h3 class="mb-4">Licencias por mes</h3>
          <canvas ref="chartMes"></canvas>
        </div>
        <div class="glass-card">
          <h3 class="mb-4">Por estado</h3>
          <canvas ref="chartEstado"></canvas>
        </div>
      </div>

      <div class="grid grid-cols-2">
        <div class="glass-card">
          <h3 class="mb-4">Top dependencias</h3>
          <canvas ref="chartDep"></canvas>
        </div>
        <div class="glass-card">
          <h3 class="mb-4">Por ciudad</h3>
          <canvas ref="chartCiudad"></canvas>
        </div>
      </div>
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
      datos: { total: 0, por_tipo: [], por_estado: [], por_mes: [], por_dependencia: [], por_ciudad: [] },
      loading: true,
      filtro: { fecha_desde: '', fecha_hasta: '' },
      charts: [],
    }
  },
  async mounted() {
    await this.cargar()
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

      // Per month bar chart
      if (this.$refs.chartMes) {
        this.charts.push(new Chart(this.$refs.chartMes, {
          type: 'bar',
          data: {
            labels: this.datos.por_mes.map(m => m.mes),
            datasets: [{
              label: 'Licencias',
              data: this.datos.por_mes.map(m => m.total),
              backgroundColor: 'rgba(59, 130, 246, 0.6)',
              borderColor: '#3b82f6',
              borderWidth: 1,
              borderRadius: 6,
            }],
          },
          options: chartOpts,
        }))
      }

      // Status pie chart
      if (this.$refs.chartEstado) {
        const estadoColors = { iniciada: '#3b82f6', en_curso: '#f59e0b', finalizada: '#10b981' }
        const estadoLabels = { iniciada: 'Iniciada', en_curso: 'En Curso', finalizada: 'Finalizada' }
        this.charts.push(new Chart(this.$refs.chartEstado, {
          type: 'doughnut',
          data: {
            labels: this.datos.por_estado.map(e => estadoLabels[e.estado] || e.estado),
            datasets: [{
              data: this.datos.por_estado.map(e => e.total),
              backgroundColor: this.datos.por_estado.map(e => estadoColors[e.estado] || '#6b7280'),
              borderWidth: 0,
            }],
          },
          options: { responsive: true, plugins: { legend: { labels: { color: '#9ca3af' } } } },
        }))
      }

      // Top dependencias horizontal bar
      if (this.$refs.chartDep) {
        this.charts.push(new Chart(this.$refs.chartDep, {
          type: 'bar',
          data: {
            labels: this.datos.por_dependencia.map(d => d.dependencia),
            datasets: [{
              label: 'Licencias',
              data: this.datos.por_dependencia.map(d => d.total),
              backgroundColor: 'rgba(139, 92, 246, 0.6)',
              borderColor: '#8b5cf6',
              borderWidth: 1,
              borderRadius: 6,
            }],
          },
          options: { ...chartOpts, indexAxis: 'y' },
        }))
      }

      // Per city
      if (this.$refs.chartCiudad) {
        const cityColors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444']
        this.charts.push(new Chart(this.$refs.chartCiudad, {
          type: 'doughnut',
          data: {
            labels: this.datos.por_ciudad.map(c => c.ciudad),
            datasets: [{
              data: this.datos.por_ciudad.map(c => c.total),
              backgroundColor: cityColors,
              borderWidth: 0,
            }],
          },
          options: { responsive: true, plugins: { legend: { labels: { color: '#9ca3af' } } } },
        }))
      }
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
</style>
