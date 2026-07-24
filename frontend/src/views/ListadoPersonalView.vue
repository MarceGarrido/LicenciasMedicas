<template>
  <div class="listado-personal">
    <div class="page-header">
      <div>
        <h1 class="page-header__title">Listado de Personal</h1>
        <p class="page-header__subtitle">Personal activo del sistema</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="glass-card mb-4">
      <div class="filters">
        <input type="text" class="form-control" v-model="busqueda" placeholder="Buscar por nombre..." @input="cargar" style="max-width:300px" />
        <select class="form-control" v-model="filtroCiudad" @change="cargar" style="max-width:200px">
          <option value="">Todas las ciudades</option>
          <option v-for="c in ciudades" :key="c.id" :value="c.id">{{ c.nombre }}</option>
        </select>
      </div>
    </div>

    <div v-if="loading" class="loading-overlay"><div class="spinner spinner--lg"></div></div>

    <div v-else class="glass-card">
      <div v-if="personal.length === 0" class="empty-state">
        <div class="empty-state__title">No se encontró personal</div>
      </div>
      <div v-else style="overflow-x:auto">
        <table class="data-table">
          <thead>
            <tr>
              <th>Nombre</th>
              <th>Jerarquía</th>
              <th>Dependencia</th>
              <th>Ciudad</th>
              <th>Licencias</th>
              <th v-if="esBienestar"></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="p in personal" :key="p.id">
              <td class="font-semibold text-sm">{{ p.nombre_completo }}</td>
              <td class="text-sm">{{ p.jerarquia_nombre || '—' }}</td>
              <td class="text-sm">{{ p.dependencia_nombre || '—' }}</td>
              <td class="text-sm">{{ p.ciudad_nombre || '—' }}</td>
              <td class="text-sm text-center">
                <span class="badge badge-primary">{{ p.total_licencias }}</span>
              </td>
              <td v-if="esBienestar">
                <router-link :to="`/personal/${p.id}/historial`" class="btn btn-ghost btn-sm">
                  Ver historial →
                </router-link>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../services/api'
import authService from '../services/authService'

export default {
  name: 'ListadoPersonalView',
  data() {
    return { personal: [], ciudades: [], loading: true, busqueda: '', filtroCiudad: '' }
  },
  computed: {
    esBienestar() {
      const u = authService.getUsuario()
      return u && (u.rol === 'bienestar' || u.rol === 'admin')
    },
  },
  async mounted() {
    try {
      const citiesRes = await api.get('/ciudades/')
      this.ciudades = citiesRes.data
    } catch (e) { /* ignore */ }
    await this.cargar()
  },
  methods: {
    async cargar() {
      this.loading = true
      try {
        const params = {}
        if (this.busqueda) params.busqueda = this.busqueda
        if (this.filtroCiudad) params.ciudad = this.filtroCiudad
        const res = await api.get('/personal/', { params })
        this.personal = res.data.results || res.data
      } catch (e) {
        console.error(e)
      } finally {
        this.loading = false
      }
    },
  },
}
</script>

<style scoped>
.filters { display: flex; gap: 0.75rem; flex-wrap: wrap; }
</style>
