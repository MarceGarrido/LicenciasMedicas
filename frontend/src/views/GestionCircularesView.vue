<template>
  <div class="gestion-circulares">
    <div class="page-header">
      <div>
        <h1 class="page-header__title">Gestionar Circulares</h1>
        <p class="page-header__subtitle">Subir y administrar circulares de Recursos Humanos</p>
      </div>
    </div>

    <!-- Upload Form -->
    <div class="glass-card mb-6">
      <h3 class="mb-4">Subir nueva circular</h3>
      <form @submit.prevent="subirCircular">
        <div class="grid grid-cols-2">
          <div class="form-group">
            <label class="form-label">Título *</label>
            <input type="text" class="form-control" v-model="form.titulo" required placeholder="Título de la circular" />
          </div>
          <div class="form-group">
            <label class="form-label">Archivo (PDF/Word) *</label>
            <input type="file" class="form-control" ref="fileInput" accept=".pdf,.doc,.docx" required @change="onFileSelect" />
          </div>
        </div>
        <div class="form-group">
          <label class="form-label">Descripción (opcional)</label>
          <textarea class="form-control" v-model="form.descripcion" rows="2" placeholder="Breve descripción del contenido"></textarea>
        </div>
        <div class="text-right">
          <button type="submit" class="btn btn-primary" :disabled="uploading">
            {{ uploading ? 'Subiendo...' : '📤 Subir Circular' }}
          </button>
        </div>
      </form>
    </div>

    <!-- List -->
    <div class="glass-card">
      <h3 class="mb-4">Circulares publicadas</h3>
      <div v-if="loading" class="loading-overlay"><div class="spinner"></div></div>
      <div v-else-if="circulares.length === 0" class="empty-state">
        <div class="empty-state__title">No hay circulares</div>
      </div>
      <table v-else class="data-table">
        <thead>
          <tr>
            <th>Título</th>
            <th>Fecha</th>
            <th>Archivo</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="c in circulares" :key="c.id">
            <td>
              <div class="font-semibold">{{ c.titulo }}</div>
              <div v-if="c.descripcion" class="text-xs text-muted truncate" style="max-width:300px">{{ c.descripcion }}</div>
            </td>
            <td class="text-sm text-muted">{{ formatDate(c.fecha_publicacion) }}</td>
            <td><span class="badge badge-info">{{ c.archivo_nombre }}</span></td>
            <td class="text-right">
              <a :href="c.archivo_url" target="_blank" class="btn btn-ghost btn-sm">📥</a>
              <button class="btn btn-ghost btn-sm" @click="eliminar(c)" style="color:var(--accent-danger)">🗑️</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Confirm delete modal -->
    <div v-if="deleteTarget" class="modal-overlay" @click.self="deleteTarget = null">
      <div class="modal">
        <div class="modal__header">
          <h3 class="modal__title">Eliminar circular</h3>
          <button class="btn-ghost btn-icon" @click="deleteTarget = null">✕</button>
        </div>
        <div class="modal__body">
          <p>¿Está seguro de eliminar la circular <strong>"{{ deleteTarget.titulo }}"</strong>?</p>
        </div>
        <div class="modal__footer">
          <button class="btn btn-secondary" @click="deleteTarget = null">Cancelar</button>
          <button class="btn btn-danger" @click="confirmarEliminar">Eliminar</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../services/api'

export default {
  name: 'GestionCircularesView',
  inject: ['showToast'],
  data() {
    return {
      circulares: [],
      loading: true,
      uploading: false,
      form: { titulo: '', descripcion: '' },
      archivo: null,
      deleteTarget: null,
    }
  },
  async mounted() {
    await this.cargar()
  },
  methods: {
    async cargar() {
      this.loading = true
      try {
        const res = await api.get('/circulares/')
        this.circulares = res.data.results || res.data
      } catch (e) {
        console.error(e)
      } finally {
        this.loading = false
      }
    },
    onFileSelect(e) {
      this.archivo = e.target.files[0]
    },
    async subirCircular() {
      if (!this.archivo) return
      this.uploading = true
      try {
        const formData = new FormData()
        formData.append('titulo', this.form.titulo)
        formData.append('descripcion', this.form.descripcion)
        formData.append('archivo', this.archivo)
        await api.post('/circulares/', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
        this.form = { titulo: '', descripcion: '' }
        this.archivo = null
        if (this.$refs.fileInput) this.$refs.fileInput.value = ''
        this.showToast('Circular subida correctamente.', 'success')
        await this.cargar()
      } catch (e) {
        this.showToast(e.response?.data?.error || 'Error al subir circular.', 'error')
      } finally {
        this.uploading = false
      }
    },
    eliminar(c) {
      this.deleteTarget = c
    },
    async confirmarEliminar() {
      try {
        await api.delete(`/circulares/${this.deleteTarget.id}/`)
        this.showToast('Circular eliminada.', 'success')
        this.deleteTarget = null
        await this.cargar()
      } catch (e) {
        this.showToast('Error al eliminar.', 'error')
      }
    },
    formatDate(d) {
      if (!d) return ''
      return new Date(d).toLocaleDateString('es-AR', { day: '2-digit', month: '2-digit', year: 'numeric' })
    },
  },
}
</script>
