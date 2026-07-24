<template>
  <div class="admin-dependencias">
    <div class="page-header">
      <div>
        <h1 class="page-header__title">Gestión de Dependencias</h1>
        <p class="page-header__subtitle">Administrar dependencias y sus emails</p>
      </div>
      <button class="btn btn-primary" @click="abrirModal()">➕ Nueva Dependencia</button>
    </div>

    <!-- Filter by city -->
    <div class="glass-card mb-4">
      <select class="form-control" v-model="filtroCiudad" @change="cargar" style="max-width:250px">
        <option value="">Todas las ciudades</option>
        <option v-for="c in ciudades" :key="c.id" :value="c.id">{{ c.nombre }}</option>
      </select>
    </div>

    <div v-if="loading" class="loading-overlay"><div class="spinner spinner--lg"></div></div>

    <div v-else class="glass-card">
      <table v-if="dependencias.length" class="data-table">
        <thead>
          <tr><th>Dependencia</th><th>Ciudad</th><th>Email</th><th>Estado</th><th></th></tr>
        </thead>
        <tbody>
          <tr v-for="d in dependencias" :key="d.id">
            <td class="font-semibold text-sm">{{ d.nombre }}</td>
            <td class="text-sm">{{ d.ciudad_nombre }}</td>
            <td class="text-sm">{{ d.email || '—' }}</td>
            <td><span :class="['badge', d.activa ? 'badge-success' : 'badge-danger']">{{ d.activa ? 'Activa' : 'Inactiva' }}</span></td>
            <td class="text-right"><button class="btn btn-ghost btn-sm" @click="abrirModal(d)">✏️</button></td>
          </tr>
        </tbody>
      </table>
      <div v-else class="empty-state"><div class="empty-state__title">No hay dependencias</div></div>
    </div>

    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <div class="modal">
        <div class="modal__header">
          <h3 class="modal__title">{{ editando ? 'Editar' : 'Nueva' }} Dependencia</h3>
          <button class="btn-ghost btn-icon" @click="showModal = false">✕</button>
        </div>
        <form @submit.prevent="guardar" class="modal__body">
          <div class="form-group">
            <label class="form-label">Nombre *</label>
            <input type="text" class="form-control" v-model="form.nombre" required placeholder="Ej: Comisaría 1ª" />
          </div>
          <div class="form-group">
            <label class="form-label">Ciudad *</label>
            <select class="form-control" v-model="form.ciudad" required>
              <option value="">Seleccione...</option>
              <option v-for="c in ciudades" :key="c.id" :value="c.id">{{ c.nombre }}</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Email de la dependencia</label>
            <input type="email" class="form-control" v-model="form.email" placeholder="dependencia@ejemplo.com" />
            <p class="form-hint">Al iniciar una licencia, se notificará a este email.</p>
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
  name: 'AdminDependenciasView',
  inject: ['showToast'],
  data() {
    return { dependencias: [], ciudades: [], loading: true, filtroCiudad: '', showModal: false, editando: false, editId: null, form: { nombre: '', ciudad: '', email: '' }, formError: '', saving: false }
  },
  async mounted() {
    try { const r = await api.get('/admin/ciudades/'); this.ciudades = r.data.results || r.data } catch {}
    await this.cargar()
  },
  methods: {
    async cargar() {
      this.loading = true
      try {
        const params = {}
        if (this.filtroCiudad) params.ciudad = this.filtroCiudad
        const res = await api.get('/admin/dependencias/', { params })
        this.dependencias = res.data.results || res.data
      } catch (e) { console.error(e) } finally { this.loading = false }
    },
    abrirModal(d = null) {
      this.formError = ''
      if (d) { this.editando = true; this.editId = d.id; this.form = { nombre: d.nombre, ciudad: d.ciudad, email: d.email || '' } }
      else { this.editando = false; this.editId = null; this.form = { nombre: '', ciudad: '', email: '' } }
      this.showModal = true
    },
    async guardar() {
      this.formError = ''; this.saving = true
      try {
        if (this.editando) { await api.put(`/admin/dependencias/${this.editId}/`, this.form); this.showToast('Dependencia actualizada.', 'success') }
        else { await api.post('/admin/dependencias/', this.form); this.showToast('Dependencia creada.', 'success') }
        this.showModal = false; await this.cargar()
      } catch (e) {
        this.formError = Object.values(e.response?.data || {}).flat().join(' ') || 'Error al guardar.'
      } finally { this.saving = false }
    },
  },
}
</script>
