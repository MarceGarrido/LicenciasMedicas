<template>
  <div class="mis-licencias">
    <div class="page-header">
      <div>
        <h1 class="page-header__title">Mis Licencias</h1>
        <p class="page-header__subtitle">Historial de tus licencias médicas</p>
      </div>
      <router-link to="/licencias/nueva" class="btn btn-primary">➕ Nueva Licencia</router-link>
    </div>

    <div v-if="loading" class="loading-overlay"><div class="spinner spinner--lg"></div></div>

    <div v-else-if="licencias.length === 0" class="glass-card empty-state">
      <div class="empty-state__icon">📁</div>
      <div class="empty-state__title">No tienes licencias</div>
      <div class="empty-state__text">Aún no has iniciado ninguna licencia.</div>
      <router-link to="/licencias/nueva" class="btn btn-primary mt-4">Iniciar licencia</router-link>
    </div>

    <div v-else class="licencias-list">
      <div v-for="l in licencias" :key="l.id" class="glass-card licencia-card">
        <div class="licencia-card__header">
          <div>
            <span :class="['badge', badgeClass(l.tipo)]">{{ l.tipo_display }}</span>
            <span :class="['badge', estadoBadge(l.estado)]" style="margin-left:0.25rem">{{ l.estado_display }}</span>
          </div>
          <span class="text-xs text-muted">{{ formatDate(l.fecha_creacion) }}</span>
        </div>
        <div class="licencia-card__body">
          <div class="licencia-card__dates">
            <div>
              <span class="text-xs text-muted">Desde</span>
              <span class="font-semibold">{{ formatDate(l.fecha_inicio) }}</span>
            </div>
            <span class="licencia-card__arrow">→</span>
            <div>
              <span class="text-xs text-muted">Hasta</span>
              <span class="font-semibold">{{ formatDate(l.fecha_fin) }}</span>
            </div>
            <div>
              <span class="text-xs text-muted">Días</span>
              <span class="font-semibold">{{ l.dias_licencia }}</span>
            </div>
          </div>
          <p v-if="l.observaciones" class="text-sm text-muted mt-2">{{ l.observaciones }}</p>
        </div>
        <div class="licencia-card__footer">
          <div class="flex items-center gap-2">
            <span v-if="l.tiene_certificado" class="badge badge-success">📎 Certificado adjunto</span>
            <span v-else class="text-xs text-muted">Sin certificado</span>
          </div>
          <button v-if="!l.tiene_certificado" class="btn btn-secondary btn-sm" @click="openUpload(l)">
            📤 Subir certificado
          </button>
        </div>
      </div>
    </div>

    <!-- Upload certificate modal -->
    <div v-if="uploadTarget" class="modal-overlay" @click.self="uploadTarget = null">
      <div class="modal">
        <div class="modal__header">
          <h3 class="modal__title">Subir certificado médico</h3>
          <button class="btn-ghost btn-icon" @click="uploadTarget = null">✕</button>
        </div>
        <div class="modal__body">
          <p class="text-sm text-muted mb-4">El certificado será enviado por email solo a Bienestar.</p>
          <input type="file" class="form-control" ref="certInput" accept=".pdf,.jpg,.jpeg,.png,.doc,.docx" />
        </div>
        <div class="modal__footer">
          <button class="btn btn-secondary" @click="uploadTarget = null">Cancelar</button>
          <button class="btn btn-primary" @click="subirCertificado" :disabled="uploadingCert">
            {{ uploadingCert ? 'Subiendo...' : 'Subir' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../services/api'

export default {
  name: 'MisLicenciasView',
  inject: ['showToast'],
  data() {
    return { licencias: [], loading: true, uploadTarget: null, uploadingCert: false }
  },
  async mounted() {
    await this.cargar()
  },
  methods: {
    async cargar() {
      this.loading = true
      try {
        const res = await api.get('/licencias/')
        this.licencias = res.data.results || res.data
      } catch (e) {
        console.error(e)
      } finally {
        this.loading = false
      }
    },
    openUpload(l) {
      this.uploadTarget = l
    },
    async subirCertificado() {
      const file = this.$refs.certInput?.files?.[0]
      if (!file) return this.showToast('Seleccione un archivo.', 'warning')
      this.uploadingCert = true
      try {
        const fd = new FormData()
        fd.append('certificado', file)
        await api.post(`/licencias/${this.uploadTarget.id}/certificado/`, fd, { headers: { 'Content-Type': 'multipart/form-data' } })
        this.showToast('Certificado subido y enviado a Bienestar.', 'success')
        this.uploadTarget = null
        await this.cargar()
      } catch (e) {
        this.showToast(e.response?.data?.error || 'Error al subir certificado.', 'error')
      } finally {
        this.uploadingCert = false
      }
    },
    badgeClass(tipo) {
      return tipo === 'salud' ? 'badge-warning' : 'badge-info'
    },
    estadoBadge(estado) {
      const map = { iniciada: 'badge-primary', en_curso: 'badge-warning', finalizada: 'badge-success' }
      return map[estado] || 'badge-primary'
    },
    formatDate(d) {
      if (!d) return ''
      return new Date(d).toLocaleDateString('es-AR', { day: '2-digit', month: '2-digit', year: 'numeric' })
    },
  },
}
</script>

<style scoped>
.licencias-list { display: flex; flex-direction: column; gap: 1rem; }
.licencia-card__header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem; }
.licencia-card__dates { display: flex; gap: 1.5rem; align-items: center; }
.licencia-card__dates > div { display: flex; flex-direction: column; }
.licencia-card__arrow { color: var(--text-muted); font-size: 1.25rem; }
.licencia-card__footer { display: flex; justify-content: space-between; align-items: center; padding-top: 0.75rem; border-top: 1px solid var(--border-color); margin-top: 0.75rem; }
@media (max-width: 480px) { .licencia-card__dates { gap: 0.75rem; flex-wrap: wrap; } }
</style>
