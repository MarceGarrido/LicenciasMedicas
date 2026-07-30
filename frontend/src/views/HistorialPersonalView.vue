<template>
  <div class="historial-personal">
    <div class="page-header">
      <div>
        <button class="btn btn-ghost btn-sm mb-2" @click="$router.back()">← Volver</button>
        <h1 class="page-header__title">Historial de Licencias</h1>
        <p v-if="usuario" class="page-header__subtitle">
          {{ usuario.nombre_completo }} · {{ usuario.jerarquia_nombre }} · {{ usuario.dependencia_nombre }}
        </p>
      </div>
    </div>

    <div v-if="loading" class="loading-overlay"><div class="spinner spinner--lg"></div></div>

    <template v-else>
      <div class="stats-grid mb-6">
        <div class="glass-card stat-card">
          <div class="stat-card__icon" style="background:var(--accent-primary-light)">📁</div>
          <div class="stat-card__value">{{ total }}</div>
          <div class="stat-card__label">Total licencias</div>
        </div>
        <div class="glass-card stat-card">
          <div class="stat-card__icon" style="background:var(--accent-warning-light)">🏥</div>
          <div class="stat-card__value">{{ licencias.filter(l => l.tipo === 'salud').length }}</div>
          <div class="stat-card__label">Razón de Salud</div>
        </div>
        <div class="glass-card stat-card">
          <div class="stat-card__icon" style="background:var(--accent-info-light)">📋</div>
          <div class="stat-card__value">{{ licencias.filter(l => l.tipo === 'atendible').length }}</div>
          <div class="stat-card__label">Razón Atendible</div>
        </div>
      </div>

      <div class="glass-card">
        <h3 class="mb-4">Licencias</h3>
        <div v-if="licencias.length === 0" class="empty-state">
          <div class="empty-state__title">Sin licencias registradas</div>
        </div>
        <table v-else class="data-table">
          <thead>
            <tr>
              <th>Tipo</th>
              <th>Estado</th>
              <th>Inicio</th>
              <th>Fin</th>
              <th>Días</th>
              <th>Cert.</th>
              <th>Fecha solicitud</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="l in licencias" :key="l.id">
              <td><span :class="['badge', l.tipo === 'salud' ? 'badge-warning' : 'badge-info']">{{ l.tipo_display }}</span></td>
              <td><span :class="['badge', estadoBadge(l.estado)]">{{ l.estado_display }}</span></td>
              <td class="text-sm">{{ formatDate(l.fecha_inicio) }}</td>
              <td class="text-sm">{{ formatDate(l.fecha_fin) }}</td>
              <td class="text-sm text-center">{{ l.dias_licencia }}</td>
              <td class="text-center">
                <button v-if="l.tiene_certificado" class="btn btn-ghost btn-sm" @click="descargarCert(l)">📎</button>
                <span v-else class="text-xs text-muted">—</span>
              </td>
              <td class="text-sm text-muted">{{ formatDate(l.fecha_creacion) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>
  </div>
</template>

<script>
import api from '../services/api'

export default {
  name: 'HistorialPersonalView',
  inject: ['showToast'],
  data() {
    return { usuario: null, licencias: [], total: 0, loading: true }
  },
  async mounted() {
    const id = this.$route.params.id
    try {
      const res = await api.get(`/personal/${id}/licencias/`)
      this.usuario = res.data.usuario
      this.licencias = res.data.licencias
      this.total = res.data.total
    } catch (e) {
      console.error(e)
    } finally {
      this.loading = false
    }
  },
  methods: {
    estadoBadge(estado) {
      return { iniciada: 'badge-primary', en_curso: 'badge-warning', finalizada: 'badge-success' }[estado] || 'badge-primary'
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
        a.download = `certificado_${this.usuario?.nombre_completo || 'doc'}.${ext}`
        a.click()
        URL.revokeObjectURL(url)
      } catch (e) {
        this.showToast('Error al descargar.', 'error')
      }
    },
    formatDate(d) {
      if (!d) return ''
      return new Date(d).toLocaleDateString('es-AR', { day: '2-digit', month: '2-digit', year: 'numeric' })
    },
  },
}
</script>
