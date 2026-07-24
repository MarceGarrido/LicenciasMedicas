<template>
  <div class="admin-ciudades">
    <div class="page-header">
      <div>
        <h1 class="page-header__title">Gestión de Ciudades</h1>
        <p class="page-header__subtitle">Administrar ciudades y emails de Bienestar</p>
      </div>
      <button class="btn btn-primary" @click="abrirModal()">➕ Nueva Ciudad</button>
    </div>

    <div v-if="loading" class="loading-overlay"><div class="spinner spinner--lg"></div></div>

    <div v-else class="glass-card">
      <table v-if="ciudades.length" class="data-table">
        <thead>
          <tr><th>Ciudad</th><th>Email Bienestar</th><th>Dependencias</th><th>Estado</th><th></th></tr>
        </thead>
        <tbody>
          <tr v-for="c in ciudades" :key="c.id">
            <td class="font-semibold">{{ c.nombre }}</td>
            <td class="text-sm">{{ c.email_bienestar || '—' }}</td>
            <td class="text-center"><span class="badge badge-primary">{{ c.cantidad_dependencias }}</span></td>
            <td><span :class="['badge', c.activa ? 'badge-success' : 'badge-danger']">{{ c.activa ? 'Activa' : 'Inactiva' }}</span></td>
            <td class="text-right"><button class="btn btn-ghost btn-sm" @click="abrirModal(c)">✏️</button></td>
          </tr>
        </tbody>
      </table>
      <div v-else class="empty-state"><div class="empty-state__title">No hay ciudades</div></div>
    </div>

    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <div class="modal">
        <div class="modal__header">
          <h3 class="modal__title">{{ editando ? 'Editar Ciudad' : 'Nueva Ciudad' }}</h3>
          <button class="btn-ghost btn-icon" @click="showModal = false">✕</button>
        </div>
        <form @submit.prevent="guardar" class="modal__body">
          <div class="form-group">
            <label class="form-label">Nombre *</label>
            <input type="text" class="form-control" v-model="form.nombre" required />
          </div>
          <div class="form-group">
            <label class="form-label">Email de Bienestar</label>
            <input type="email" class="form-control" v-model="form.email_bienestar" placeholder="bienestar@ejemplo.com" />
            <p class="form-hint">Email donde se enviarán los certificados médicos de esta ciudad.</p>
          </div>
          <p v-if="formError" class="form-error">{{ formError }}</p>
        </form>
        <div class="modal__footer">
          <button class="btn btn-secondary" @click="showModal = false">Cancelar</button>
          <button class="btn btn-primary" @click="guardar" :disabled="saving">{{ saving ? 'Guardando...' : 'Guardar' }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../../services/api'

export default {
  name: 'AdminCiudadesView',
  inject: ['showToast'],
  data() {
    return { ciudades: [], loading: true, showModal: false, editando: false, editId: null, form: { nombre: '', email_bienestar: '' }, formError: '', saving: false }
  },
  async mounted() { await this.cargar() },
  methods: {
    async cargar() {
      this.loading = true
      try { const res = await api.get('/admin/ciudades/'); this.ciudades = res.data.results || res.data } catch (e) { console.error(e) } finally { this.loading = false }
    },
    abrirModal(c = null) {
      this.formError = ''
      if (c) { this.editando = true; this.editId = c.id; this.form = { nombre: c.nombre, email_bienestar: c.email_bienestar || '' } }
      else { this.editando = false; this.editId = null; this.form = { nombre: '', email_bienestar: '' } }
      this.showModal = true
    },
    async guardar() {
      this.formError = ''; this.saving = true
      try {
        if (this.editando) { await api.put(`/admin/ciudades/${this.editId}/`, this.form); this.showToast('Ciudad actualizada.', 'success') }
        else { await api.post('/admin/ciudades/', this.form); this.showToast('Ciudad creada.', 'success') }
        this.showModal = false; await this.cargar()
      } catch (e) {
        this.formError = Object.values(e.response?.data || {}).flat().join(' ') || 'Error al guardar.'
      } finally { this.saving = false }
    },
  },
}
</script>
