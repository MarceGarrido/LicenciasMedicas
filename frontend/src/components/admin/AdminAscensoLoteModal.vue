<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal" style="max-width:900px">
      <div class="modal__header">
        <h3 class="modal__title">⬆️ Ascensos en Lote</h3>
        <button class="btn-ghost btn-icon" @click="$emit('close')">✕</button>
      </div>

      <div class="modal__body">
        <!-- Filtros -->
        <div class="filtros-row">
          <div class="form-group" style="flex:1">
            <label class="form-label">Tipo de personal</label>
            <select class="form-control" v-model="filtroTipo" @change="filtroJerarquia = null">
              <option :value="null">— Todos —</option>
              <option v-for="t in tiposPersonal" :key="t.id" :value="t.id">{{ t.nombre }}</option>
            </select>
          </div>
          <div class="form-group" style="flex:1">
            <label class="form-label">Jerarquía actual</label>
            <select class="form-control" v-model="filtroJerarquia">
              <option :value="null">— Todas —</option>
              <option v-for="j in jerarquiasFiltradas" :key="j.id" :value="j.id">{{ j.nombre }}</option>
            </select>
          </div>
          <div class="form-group" style="flex:1">
            <label class="form-label">Dependencia</label>
            <select class="form-control" v-model="filtroDependencia">
              <option :value="null">— Todas —</option>
              <option v-for="d in dependencias" :key="d.id" :value="d.id">{{ d.nombre }} ({{ d.ciudad_nombre }})</option>
            </select>
          </div>
        </div>

        <!-- Tabla de usuarios -->
        <div v-if="loading" style="text-align:center;padding:2rem">
          <div class="spinner spinner--lg"></div>
        </div>

        <div v-else-if="usuariosFiltrados.length === 0" class="empty-state" style="padding:1.5rem">
          <div class="empty-state__title">No hay usuarios con los filtros seleccionados</div>
        </div>

        <div v-else>
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.5rem">
            <label class="form-label" style="margin:0">
              <input type="checkbox" @change="toggleAll" :checked="todosSeleccionados" />
              Seleccionar todos ({{ usuariosFiltrados.length }})
            </label>
            <span class="badge badge-primary">{{ seleccionados.length }} seleccionados</span>
          </div>

          <div style="overflow-x:auto;max-height:300px;overflow-y:auto">
            <table class="data-table">
              <thead>
                <tr>
                  <th style="width:40px"></th>
                  <th>Nombre</th>
                  <th>Jerarquía actual</th>
                  <th>Dependencia</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="u in usuariosFiltrados" :key="u.id" :class="{ 'row-selected': seleccionados.includes(u.id) }">
                  <td>
                    <input type="checkbox" :value="u.id" v-model="seleccionados" />
                  </td>
                  <td class="text-sm">{{ u.nombre_completo }}</td>
                  <td class="text-sm">{{ u.jerarquia_nombre || '—' }}</td>
                  <td class="text-sm">{{ u.dependencia_nombre || '—' }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Selector de nueva jerarquía -->
        <div v-if="seleccionados.length > 0" class="ascenso-destino">
          <div class="form-group" style="flex:1;margin:0">
            <label class="form-label">Ascender a la jerarquía:</label>
            <select class="form-control" v-model="nuevaJerarquiaId">
              <option :value="null">— Seleccione la nueva jerarquía —</option>
              <optgroup v-for="t in tiposPersonal" :key="t.id" :label="t.nombre">
                <option v-for="j in t.jerarquias" :key="j.id" :value="j.id">{{ j.nombre }}</option>
              </optgroup>
            </select>
          </div>
        </div>

        <p v-if="formError" class="form-error" style="margin-top:0.5rem">{{ formError }}</p>
      </div>

      <div class="modal__footer">
        <button class="btn btn-secondary" @click="$emit('close')">Cancelar</button>
        <button
          class="btn btn-primary"
          @click="confirmarAscenso"
          :disabled="seleccionados.length === 0 || !nuevaJerarquiaId || procesando"
        >
          {{ procesando ? 'Procesando...' : `⬆️ Ascender ${seleccionados.length} usuario(s)` }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../../services/api'

export default {
  name: 'AdminAscensoLoteModal',
  inject: ['showToast'],
  emits: ['close', 'done'],
  props: {
    usuarios: { type: Array, default: () => [] },
    dependencias: { type: Array, default: () => [] },
    tiposPersonal: { type: Array, default: () => [] },
  },
  data() {
    return {
      loading: false,
      filtroTipo: null,
      filtroJerarquia: null,
      filtroDependencia: null,
      seleccionados: [],
      nuevaJerarquiaId: null,
      procesando: false,
      formError: '',
    }
  },
  computed: {
    jerarquiasFiltradas() {
      if (!this.filtroTipo) {
        return this.tiposPersonal.flatMap(t => t.jerarquias || [])
      }
      const tipo = this.tiposPersonal.find(t => t.id === this.filtroTipo)
      return tipo ? (tipo.jerarquias || []) : []
    },
    usuariosFiltrados() {
      let lista = this.usuarios.filter(u => u.rol === 'personal' && u.is_active)
      if (this.filtroTipo) {
        lista = lista.filter(u => {
          const tipo = this.tiposPersonal.find(t =>
            (t.jerarquias || []).some(j => j.id === u.jerarquia)
          )
          return tipo && tipo.id === this.filtroTipo
        })
      }
      if (this.filtroJerarquia) {
        lista = lista.filter(u => u.jerarquia === this.filtroJerarquia)
      }
      if (this.filtroDependencia) {
        lista = lista.filter(u => u.dependencia === this.filtroDependencia)
      }
      return lista
    },
    todosSeleccionados() {
      return this.usuariosFiltrados.length > 0 &&
        this.usuariosFiltrados.every(u => this.seleccionados.includes(u.id))
    },
  },
  methods: {
    toggleAll(e) {
      if (e.target.checked) {
        const ids = this.usuariosFiltrados.map(u => u.id)
        this.seleccionados = [...new Set([...this.seleccionados, ...ids])]
      } else {
        const idsToRemove = new Set(this.usuariosFiltrados.map(u => u.id))
        this.seleccionados = this.seleccionados.filter(id => !idsToRemove.has(id))
      }
    },
    async confirmarAscenso() {
      this.formError = ''
      const jerarquiaNombre = this.tiposPersonal
        .flatMap(t => t.jerarquias || [])
        .find(j => j.id === this.nuevaJerarquiaId)?.nombre || 'la jerarquía seleccionada'

      if (!confirm(`¿Está seguro de ascender a ${this.seleccionados.length} usuario(s) a "${jerarquiaNombre}"?`)) {
        return
      }

      this.procesando = true
      try {
        const res = await api.post('/admin/usuarios/ascenso-lote/', {
          usuario_ids: this.seleccionados,
          nueva_jerarquia_id: this.nuevaJerarquiaId,
        })
        this.showToast(`${res.data.ascendidos} usuario(s) ascendidos a ${res.data.nueva_jerarquia}.`, 'success')
        this.$emit('done')
        this.$emit('close')
      } catch (e) {
        this.formError = e.response?.data?.error || 'Error al procesar los ascensos.'
        this.showToast(this.formError, 'error')
      } finally {
        this.procesando = false
      }
    },
  },
}
</script>

<style scoped>
.filtros-row {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

@media (max-width: 768px) {
  .filtros-row {
    flex-direction: column;
  }
}

.row-selected {
  background: var(--accent-primary-light) !important;
}

.ascenso-destino {
  display: flex;
  align-items: flex-end;
  gap: 1rem;
  margin-top: 1rem;
  padding: 1rem;
  background: var(--bg-glass);
  border-radius: var(--border-radius-md);
  border: 1px solid var(--border-color);
}
</style>
