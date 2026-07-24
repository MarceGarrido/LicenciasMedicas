<template>
  <div class="admin-usuarios">
    <div class="page-header">
      <div>
        <h1 class="page-header__title">Gestión de Usuarios</h1>
        <p class="page-header__subtitle">Crear y administrar cuentas de usuario</p>
      </div>
      <button class="btn btn-primary" @click="abrirModal()">➕ Nuevo Usuario</button>
    </div>

    <div v-if="loading" class="loading-overlay"><div class="spinner spinner--lg"></div></div>

    <div v-else class="glass-card">
      <div v-if="usuarios.length === 0" class="empty-state">
        <div class="empty-state__title">No hay usuarios</div>
      </div>
      <div v-else style="overflow-x:auto">
        <table class="data-table">
          <thead>
            <tr>
              <th>Usuario</th>
              <th>Nombre</th>
              <th>Rol</th>
              <th>Jerarquía</th>
              <th>Dependencia</th>
              <th>Estado</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="u in usuarios" :key="u.id">
              <td class="text-sm font-semibold">{{ u.username }}</td>
              <td class="text-sm">{{ u.nombre_completo }}</td>
              <td><span :class="['badge', rolBadge(u.rol)]">{{ rolLabel(u.rol) }}</span></td>
              <td class="text-sm">{{ u.jerarquia_nombre || '—' }}</td>
              <td class="text-sm">{{ u.dependencia_nombre || '—' }}</td>
              <td>
                <span :class="['badge', u.is_active ? 'badge-success' : 'badge-danger']">
                  {{ u.is_active ? 'Activo' : 'Inactivo' }}
                </span>
              </td>
              <td class="text-right">
                <button class="btn btn-ghost btn-sm" @click="abrirModal(u)">✏️</button>
                <button v-if="u.is_active" class="btn btn-ghost btn-sm" @click="desactivar(u)" style="color:var(--accent-danger)">🚫</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Modal -->
    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <div class="modal" style="max-width:600px">
        <div class="modal__header">
          <h3 class="modal__title">{{ editando ? 'Editar Usuario' : 'Nuevo Usuario' }}</h3>
          <button class="btn-ghost btn-icon" @click="showModal = false">✕</button>
        </div>
        <form @submit.prevent="guardar" class="modal__body">
          <div class="grid grid-cols-2">
            <div class="form-group">
              <label class="form-label">Usuario *</label>
              <input type="text" class="form-control" v-model="form.username" required :disabled="editando" />
            </div>
            <div class="form-group">
              <label class="form-label">{{ editando ? 'Nueva contraseña (dejar vacío para no cambiar)' : 'Contraseña *' }}</label>
              <input type="password" class="form-control" v-model="form.password" :required="!editando" minlength="8" />
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">Nombre completo *</label>
            <input type="text" class="form-control" v-model="form.nombre_completo" required />
          </div>
          <div class="grid grid-cols-2">
            <div class="form-group">
              <label class="form-label">Rol *</label>
              <select class="form-control" v-model="form.rol" required>
                <option value="personal">Personal</option>
                <option value="rrhh">Recursos Humanos</option>
                <option value="bienestar">Bienestar</option>
                <option value="admin">Administrador</option>
              </select>
            </div>
            <div class="form-group">
              <label class="form-label">Email</label>
              <input type="email" class="form-control" v-model="form.email" />
            </div>
          </div>
          <div class="grid grid-cols-2">
            <div class="form-group">
              <label class="form-label">Dependencia</label>
              <select class="form-control" v-model="form.dependencia">
                <option :value="null">— Sin asignar —</option>
                <option v-for="d in dependencias" :key="d.id" :value="d.id">{{ d.nombre }} ({{ d.ciudad_nombre }})</option>
              </select>
            </div>
            <div class="form-group">
              <label class="form-label">Jerarquía</label>
              <select class="form-control" v-model="form.jerarquia">
                <option :value="null">— Sin asignar —</option>
                <optgroup v-for="t in tiposPersonal" :key="t.id" :label="t.nombre">
                  <option v-for="j in t.jerarquias" :key="j.id" :value="j.id">{{ j.nombre }}</option>
                </optgroup>
              </select>
            </div>
          </div>
          <p v-if="formError" class="form-error">{{ formError }}</p>
        </form>
        <div class="modal__footer">
          <button class="btn btn-secondary" @click="showModal = false">Cancelar</button>
          <button class="btn btn-primary" @click="guardar" :disabled="saving">
            {{ saving ? 'Guardando...' : 'Guardar' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../../services/api'

const rolLabels = { admin: 'Administrador', personal: 'Personal', rrhh: 'RRHH', bienestar: 'Bienestar' }
const rolBadges = { admin: 'badge-danger', personal: 'badge-primary', rrhh: 'badge-info', bienestar: 'badge-success' }

export default {
  name: 'AdminUsuariosView',
  inject: ['showToast'],
  data() {
    return {
      usuarios: [],
      dependencias: [],
      tiposPersonal: [],
      loading: true,
      showModal: false,
      editando: false,
      editId: null,
      form: this.formVacio(),
      formError: '',
      saving: false,
    }
  },
  async mounted() {
    await Promise.all([this.cargar(), this.cargarAux()])
  },
  methods: {
    formVacio() {
      return { username: '', password: '', nombre_completo: '', rol: 'personal', email: '', dependencia: null, jerarquia: null }
    },
    async cargar() {
      this.loading = true
      try {
        const res = await api.get('/admin/usuarios/')
        this.usuarios = res.data.results || res.data
      } catch (e) { console.error(e) }
      finally { this.loading = false }
    },
    async cargarAux() {
      try {
        const [depRes, tipRes] = await Promise.all([
          api.get('/dependencias/'),
          api.get('/jerarquias/'),
        ])
        this.dependencias = depRes.data.results || depRes.data
        this.tiposPersonal = tipRes.data.results || tipRes.data
      } catch (e) { console.error(e) }
    },
    abrirModal(u = null) {
      this.formError = ''
      if (u) {
        this.editando = true
        this.editId = u.id
        this.form = {
          username: u.username,
          password: '',
          nombre_completo: u.nombre_completo,
          rol: u.rol,
          email: u.email || '',
          dependencia: u.dependencia,
          jerarquia: u.jerarquia,
        }
      } else {
        this.editando = false
        this.editId = null
        this.form = this.formVacio()
      }
      this.showModal = true
    },
    async guardar() {
      this.formError = ''
      this.saving = true
      try {
        const data = { ...this.form }
        if (!data.password) delete data.password
        if (this.editando) {
          await api.put(`/admin/usuarios/${this.editId}/`, data)
          this.showToast('Usuario actualizado.', 'success')
        } else {
          await api.post('/admin/usuarios/', data)
          this.showToast('Usuario creado.', 'success')
        }
        this.showModal = false
        await this.cargar()
      } catch (e) {
        const data = e.response?.data
        if (data) {
          this.formError = Object.values(data).flat().join(' ')
        } else {
          this.formError = 'Error al guardar.'
        }
      } finally {
        this.saving = false
      }
    },
    async desactivar(u) {
      if (!confirm(`¿Desactivar al usuario "${u.nombre_completo}"?`)) return
      try {
        await api.delete(`/admin/usuarios/${u.id}/`)
        this.showToast('Usuario desactivado.', 'success')
        await this.cargar()
      } catch (e) {
        this.showToast(e.response?.data?.error || 'Error.', 'error')
      }
    },
    rolLabel(r) { return rolLabels[r] || r },
    rolBadge(r) { return rolBadges[r] || 'badge-primary' },
  },
}
</script>
