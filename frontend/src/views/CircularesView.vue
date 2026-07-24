<template>
  <div class="circulares">
    <div class="page-header">
      <div>
        <h1 class="page-header__title">Circulares</h1>
        <p class="page-header__subtitle">Circulares publicadas por Recursos Humanos</p>
      </div>
    </div>

    <div v-if="loading" class="loading-overlay">
      <div class="spinner spinner--lg"></div>
      <span>Cargando circulares...</span>
    </div>

    <div v-else-if="circulares.length === 0" class="glass-card empty-state">
      <div class="empty-state__icon">📋</div>
      <div class="empty-state__title">No hay circulares</div>
      <div class="empty-state__text">Aún no se han publicado circulares.</div>
    </div>

    <div v-else class="circulares-grid">
      <div v-for="c in circulares" :key="c.id" class="glass-card circular-card">
        <div class="circular-card__header">
          <span class="circular-card__icon">📄</span>
          <div>
            <h3 class="circular-card__title">{{ c.titulo }}</h3>
            <p class="circular-card__meta">
              {{ formatDate(c.fecha_publicacion) }}
              <span v-if="c.publicado_por_nombre"> · {{ c.publicado_por_nombre }}</span>
            </p>
          </div>
        </div>
        <p v-if="c.descripcion" class="circular-card__desc">{{ c.descripcion }}</p>
        <div class="circular-card__footer">
          <span class="badge badge-info">{{ c.archivo_nombre }}</span>
          <a :href="c.archivo_url" target="_blank" class="btn btn-primary btn-sm">
            📥 Descargar
          </a>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../services/api'

export default {
  name: 'CircularesView',
  data() {
    return { loading: true, circulares: [] }
  },
  async mounted() {
    try {
      const res = await api.get('/circulares/')
      this.circulares = res.data.results || res.data
    } catch (e) {
      console.error('Error cargando circulares:', e)
    } finally {
      this.loading = false
    }
  },
  methods: {
    formatDate(d) {
      if (!d) return ''
      return new Date(d).toLocaleDateString('es-AR', { day: '2-digit', month: '2-digit', year: 'numeric' })
    },
  },
}
</script>

<style scoped>
.circulares-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 1rem;
}
.circular-card__header {
  display: flex;
  gap: 0.75rem;
  align-items: flex-start;
  margin-bottom: 0.75rem;
}
.circular-card__icon { font-size: 1.5rem; flex-shrink: 0; }
.circular-card__title { font-size: 1rem; font-weight: 600; line-height: 1.3; }
.circular-card__meta { font-size: 0.75rem; color: var(--text-muted); margin-top: 0.125rem; }
.circular-card__desc { font-size: 0.8125rem; color: var(--text-secondary); margin-bottom: 1rem; line-height: 1.5; }
.circular-card__footer { display: flex; align-items: center; justify-content: space-between; padding-top: 0.75rem; border-top: 1px solid var(--border-color); }
@media (max-width: 768px) {
  .circulares-grid { grid-template-columns: 1fr; }
}
</style>
