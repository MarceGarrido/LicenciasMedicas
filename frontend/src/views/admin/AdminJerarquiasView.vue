<template>
  <div class="admin-jerarquias">
    <div class="page-header">
      <div>
        <h1 class="page-header__title">Gestión de Jerarquías</h1>
        <p class="page-header__subtitle">Administrar tipos de personal y jerarquías</p>
      </div>
    </div>

    <div v-if="loading" class="loading-overlay"><div class="spinner spinner--lg"></div></div>

    <template v-else>
      <!-- Tipos de Personal -->
      <div class="glass-card mb-6">
        <div class="flex items-center justify-between mb-4">
          <h3>Tipos de Personal</h3>
          <button class="btn btn-secondary btn-sm" @click="abrirModalTipo()">➕ Nuevo Tipo</button>
        </div>
        <table v-if="tipos.length" class="data-table">
          <thead>
            <tr><th>Nombre</th><th>Orden</th><th>Jerarquías</th><th></th></tr>
          </thead>
          <tbody>
            <tr v-for="t in tipos" :key="t.id">
              <td class="font-semibold">{{ t.nombre }}</td>
              <td class="text-sm">{{ t.orden }}</td>
              <td class="text-sm">{{ t.jerarquias?.length || 0 }}</td>
              <td class="text-right"><button class="btn btn-ghost btn-sm" @click="abrirModalTipo(t)">✏️</button></td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Jerarquías -->
      <div class="glass-card">
        <div class="flex items-center justify-between mb-4">
          <h3>Jerarquías</h3>
          <button class="btn btn-primary btn-sm" @click="abrirModalJerarquia()">➕ Nueva Jerarquía</button>
        </div>
        <div class="mb-4">
          <select class="form-control" v-model="filtroTipo" @change="cargarJerarquias" style="max-width:250px">
            <option value="">Todos los tipos</option>
            <option v-for="t in tipos" :key="t.id" :value="t.id">{{ t.nombre }}</option>
          </select>
        </div>
        <table v-if="jerarquias.length" class="data-table">
          <thead>
            <tr><th>Nombre</th><th>Tipo</th><th>Orden</th><th>Estado</th><th></th></tr>
          </thead>
          <tbody>
            <tr v-for="j in jerarquias" :key="j.id">
              <td class="font-semibold text-sm">{{ j.nombre }}</td>
              <td class="text-sm">{{ j.tipo_personal_nombre }}</td>
              <td class="text-sm">{{ j.orden }}</td>
              <td><span :class="['badge', j.activa ? 'badge-success' : 'badge-danger']">{{ j.activa ? 'Activa' : 'Inactiva' }}</span></td>
              <td class="text-right"><button class="btn btn-ghost btn-sm" @click="abrirModalJerarquia(j)">✏️</button></td>
            </tr>
          </tbody>
        </table>
        <div v-else class="empty-state"><div class="empty-state__title">No hay jerarquías</div></div>
      </div>
    </template>

    <!-- Modal Tipo -->
    <div v-if="showModalTipo" class="modal-overlay" @click.self="showModalTipo = false">
      <div class="modal">
        <div class="modal__header">
          <h3 class="modal__title">{{ editandoTipo ? 'Editar' : 'Nuevo' }} Tipo de Personal</h3>
          <button class="btn-ghost btn-icon" @click="showModalTipo = false">✕</button>
        </div>
        <form @submit.prevent="guardarTipo" class="modal__body">
          <div class="form-group">
            <label class="form-label">Nombre *</label>
            <input type="text" class="form-control" v-model="formTipo.nombre" required />
          </div>
          <div class="form-group">
            <label class="form-label">Orden</label>
            <input type="number" class="form-control" v-model.number="formTipo.orden" />
          </div>
          <p v-if="formError" class="form-error">{{ formError }}</p>
        </form>
        <div class="modal__footer">
          <button class="btn btn-secondary" @click="showModalTipo = false">Cancelar</button>
          <button class="btn btn-primary" @click="guardarTipo" :disabled="saving">Guardar</button>
        </div>
      </div>
    </div>

    <!-- Modal Jerarquía -->
    <div v-if="showModalJerarquia" class="modal-overlay" @click.self="showModalJerarquia = false">
      <div class="modal">
        <div class="modal__header">
          <h3 class="modal__title">{{ editandoJ ? 'Editar' : 'Nueva' }} Jerarquía</h3>
          <button class="btn-ghost btn-icon" @click="showModalJerarquia = false">✕</button>
        </div>
        <form @submit.prevent="guardarJerarquia" class="modal__body">
          <div class="form-group">
            <label class="form-label">Nombre *</label>
            <input type="text" class="form-control" v-model="formJ.nombre" required placeholder="Ej: Comisario General" />
          </div>
          <div class="grid grid-cols-2">
            <div class="form-group">
              <label class="form-label">Tipo de personal *</label>
              <select class="form-control" v-model="formJ.tipo_personal" required>
                <option value="">Seleccione...</option>
                <option v-for="t in tipos" :key="t.id" :value="t.id">{{ t.nombre }}</option>
              </select>
            </div>
            <div class="form-group">
              <label class="form-label">Orden jerárquico</label>
              <input type="number" class="form-control" v-model.number="formJ.orden" />
              <p class="form-hint">Mayor número = mayor rango</p>
            </div>
          </div>
          <p v-if="formError" class="form-error">{{ formError }}</p>
        </form>
        <div class="modal__footer">
          <button class="btn btn-secondary" @click="showModalJerarquia = false">Cancelar</button>
          <button class="btn btn-primary" @click="guardarJerarquia" :disabled="saving">Guardar</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../../services/api'

export default {
  name: 'AdminJerarquiasView',
  inject: ['showToast'],
  data() {
    return {
      tipos: [], jerarquias: [], loading: true, filtroTipo: '',
      showModalTipo: false, editandoTipo: false, editIdTipo: null,
      formTipo: { nombre: '', orden: 0 },
      showModalJerarquia: false, editandoJ: false, editIdJ: null,
      formJ: { nombre: '', tipo_personal: '', orden: 0 },
      formError: '', saving: false,
    }
  },
  async mounted() { await this.cargarTodo() },
  methods: {
    async cargarTodo() {
      this.loading = true
      try { await Promise.all([this.cargarTipos(), this.cargarJerarquias()]) }
      finally { this.loading = false }
    },
    async cargarTipos() {
      const r = await api.get('/admin/tipos-personal/')
      this.tipos = r.data.results || r.data
    },
    async cargarJerarquias() {
      const params = {}
      if (this.filtroTipo) params.tipo_personal = this.filtroTipo
      const r = await api.get('/admin/jerarquias/', { params })
      this.jerarquias = r.data.results || r.data
    },
    abrirModalTipo(t = null) {
      this.formError = ''
      if (t) { this.editandoTipo = true; this.editIdTipo = t.id; this.formTipo = { nombre: t.nombre, orden: t.orden } }
      else { this.editandoTipo = false; this.editIdTipo = null; this.formTipo = { nombre: '', orden: 0 } }
      this.showModalTipo = true
    },
    async guardarTipo() {
      this.formError = ''; this.saving = true
      try {
        if (this.editandoTipo) await api.put(`/admin/tipos-personal/${this.editIdTipo}/`, this.formTipo)
        else await api.post('/admin/tipos-personal/', this.formTipo)
        this.showToast('Guardado.', 'success'); this.showModalTipo = false; await this.cargarTipos()
      } catch (e) { this.formError = Object.values(e.response?.data || {}).flat().join(' ') || 'Error.' }
      finally { this.saving = false }
    },
    abrirModalJerarquia(j = null) {
      this.formError = ''
      if (j) { this.editandoJ = true; this.editIdJ = j.id; this.formJ = { nombre: j.nombre, tipo_personal: j.tipo_personal, orden: j.orden } }
      else { this.editandoJ = false; this.editIdJ = null; this.formJ = { nombre: '', tipo_personal: '', orden: 0 } }
      this.showModalJerarquia = true
    },
    async guardarJerarquia() {
      this.formError = ''; this.saving = true
      try {
        if (this.editandoJ) await api.put(`/admin/jerarquias/${this.editIdJ}/`, this.formJ)
        else await api.post('/admin/jerarquias/', this.formJ)
        this.showToast('Guardado.', 'success'); this.showModalJerarquia = false; await this.cargarJerarquias()
      } catch (e) { this.formError = Object.values(e.response?.data || {}).flat().join(' ') || 'Error.' }
      finally { this.saving = false }
    },
  },
}
</script>
