<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal" style="max-width:800px">
      <div class="modal__header">
        <h3 class="modal__title">📥 Carga Masiva de Usuarios</h3>
        <button class="btn-ghost btn-icon" @click="$emit('close')">✕</button>
      </div>

      <!-- Paso 1: Subir archivo -->
      <div v-if="paso === 1" class="modal__body">
        <p class="text-sm" style="margin-bottom:1rem;color:var(--text-secondary)">
          Suba un archivo Excel (.xlsx) con las columnas: <strong>nombre_completo</strong>, <strong>dependencia</strong>, <strong>jerarquia</strong>, <strong>email</strong> (opcional).
          El sistema generará automáticamente el nombre de usuario y la contraseña para cada persona.
        </p>

        <button class="btn btn-secondary btn-sm" @click="descargarPlantilla" style="margin-bottom:1rem">
          📄 Descargar plantilla Excel
        </button>

        <div
          class="upload-zone"
          :class="{ 'upload-zone--hover': dragging }"
          @dragover.prevent="dragging = true"
          @dragleave.prevent="dragging = false"
          @drop.prevent="onDrop"
          @click="$refs.fileInput.click()"
        >
          <input ref="fileInput" type="file" accept=".xlsx" style="display:none" @change="onFileSelect" />
          <div v-if="!archivo" class="upload-zone__content">
            <span class="upload-zone__icon">📂</span>
            <span class="upload-zone__text">Arrastre un archivo .xlsx aquí o haga clic para seleccionar</span>
          </div>
          <div v-else class="upload-zone__content">
            <span class="upload-zone__icon">✅</span>
            <span class="upload-zone__text">{{ archivo.name }}</span>
            <button class="btn btn-ghost btn-sm" @click.stop="archivo = null" style="color:var(--accent-danger)">Quitar</button>
          </div>
        </div>

        <p v-if="errorArchivo" class="form-error" style="margin-top:0.5rem">{{ errorArchivo }}</p>
      </div>

      <!-- Paso 2: Procesando -->
      <div v-if="paso === 2" class="modal__body" style="text-align:center;padding:2rem">
        <div class="spinner spinner--lg"></div>
        <p style="margin-top:1rem;color:var(--text-secondary)">Procesando archivo...</p>
      </div>

      <!-- Paso 3: Resultados -->
      <div v-if="paso === 3" class="modal__body">
        <div class="resultado-header">
          <div class="resultado-stat resultado-stat--success">
            <span class="resultado-stat__number">{{ resultado.creados }}</span>
            <span class="resultado-stat__label">Creados</span>
          </div>
          <div v-if="resultado.errores.length" class="resultado-stat resultado-stat--error">
            <span class="resultado-stat__number">{{ resultado.errores.length }}</span>
            <span class="resultado-stat__label">Errores</span>
          </div>
        </div>

        <!-- Errores -->
        <div v-if="resultado.errores.length" class="resultado-errores">
          <h4 style="color:var(--accent-danger);margin-bottom:0.5rem">⚠️ Errores encontrados:</h4>
          <div v-for="e in resultado.errores" :key="e.fila" class="resultado-error-item">
            <strong>Fila {{ e.fila }}:</strong> {{ e.nombre }} — {{ e.error }}
          </div>
        </div>

        <!-- Usuarios creados -->
        <div v-if="resultado.usuarios.length" style="margin-top:1rem">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.5rem">
            <h4 style="color:var(--accent-success)">✅ Usuarios creados:</h4>
            <button class="btn btn-secondary btn-sm" @click="copiarCredenciales">📋 Copiar todo</button>
          </div>
          <div style="overflow-x:auto;max-height:300px;overflow-y:auto">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Nombre</th>
                  <th>Usuario</th>
                  <th>Contraseña</th>
                  <th>Dependencia</th>
                  <th>Jerarquía</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="u in resultado.usuarios" :key="u.username">
                  <td class="text-sm">{{ u.nombre_completo }}</td>
                  <td class="text-sm font-semibold">{{ u.username }}</td>
                  <td class="text-sm" style="font-family:monospace">{{ u.password }}</td>
                  <td class="text-sm">{{ u.dependencia }}</td>
                  <td class="text-sm">{{ u.jerarquia }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <div class="modal__footer">
        <button class="btn btn-secondary" @click="$emit('close')">{{ paso === 3 ? 'Cerrar' : 'Cancelar' }}</button>
        <button v-if="paso === 1" class="btn btn-primary" @click="subir" :disabled="!archivo">
          🚀 Procesar archivo
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../../services/api'

export default {
  name: 'AdminCargaMasivaModal',
  inject: ['showToast'],
  emits: ['close', 'done'],
  data() {
    return {
      paso: 1,
      archivo: null,
      dragging: false,
      errorArchivo: '',
      resultado: { creados: 0, errores: [], usuarios: [] },
    }
  },
  methods: {
    onFileSelect(e) {
      const file = e.target.files[0]
      if (file) this.setArchivo(file)
    },
    onDrop(e) {
      this.dragging = false
      const file = e.dataTransfer.files[0]
      if (file) this.setArchivo(file)
    },
    setArchivo(file) {
      this.errorArchivo = ''
      if (!file.name.endsWith('.xlsx')) {
        this.errorArchivo = 'Solo se aceptan archivos Excel (.xlsx)'
        return
      }
      this.archivo = file
    },
    async subir() {
      this.paso = 2
      this.errorArchivo = ''
      try {
        const formData = new FormData()
        formData.append('archivo', this.archivo)
        const res = await api.post('/admin/usuarios/carga-masiva/', formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        })
        this.resultado = res.data
        this.paso = 3
        if (res.data.creados > 0) {
          this.showToast(`${res.data.creados} usuarios creados exitosamente.`, 'success')
          this.$emit('done')
        }
      } catch (e) {
        this.paso = 1
        this.errorArchivo = e.response?.data?.error || 'Error al procesar el archivo.'
        this.showToast(this.errorArchivo, 'error')
      }
    },
    copiarCredenciales() {
      const texto = this.resultado.usuarios.map(u =>
        `${u.nombre_completo}\tUsuario: ${u.username}\tContraseña: ${u.password}`
      ).join('\n')
      navigator.clipboard.writeText(texto)
      this.showToast('Credenciales copiadas al portapapeles.', 'success')
    },
    descargarPlantilla() {
      // Crear un CSV simple como plantilla
      const headers = 'nombre_completo,dependencia,jerarquia,email'
      const ejemplo = 'Juan Carlos Pérez,Comisaría 1ra,Cabo,'
      const contenido = `${headers}\n${ejemplo}\n`
      const blob = new Blob(['\ufeff' + contenido], { type: 'text/csv;charset=utf-8;' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = 'plantilla_usuarios.csv'
      a.click()
      URL.revokeObjectURL(url)
      this.showToast('Plantilla descargada. Puede abrirla con Excel, completarla y guardarla como .xlsx antes de subirla.', 'success')
    },
  },
}
</script>

<style scoped>
.upload-zone {
  border: 2px dashed var(--border-color);
  border-radius: var(--border-radius-md);
  padding: 2rem;
  text-align: center;
  cursor: pointer;
  transition: all var(--transition-fast);
  background: var(--bg-glass);
}

.upload-zone:hover,
.upload-zone--hover {
  border-color: var(--accent-primary);
  background: var(--accent-primary-light);
}

.upload-zone__content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.upload-zone__icon {
  font-size: 2rem;
}

.upload-zone__text {
  color: var(--text-secondary);
  font-size: 0.875rem;
}

.resultado-header {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

.resultado-stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1rem 1.5rem;
  border-radius: var(--border-radius-md);
  flex: 1;
}

.resultado-stat--success {
  background: rgba(16, 185, 129, 0.1);
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.resultado-stat--error {
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.resultado-stat__number {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-primary);
}

.resultado-stat__label {
  font-size: 0.75rem;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.resultado-errores {
  background: rgba(239, 68, 68, 0.05);
  border: 1px solid rgba(239, 68, 68, 0.2);
  border-radius: var(--border-radius-md);
  padding: 1rem;
  max-height: 150px;
  overflow-y: auto;
}

.resultado-error-item {
  font-size: 0.8125rem;
  color: var(--text-secondary);
  padding: 0.25rem 0;
  border-bottom: 1px solid var(--border-color);
}

.resultado-error-item:last-child {
  border-bottom: none;
}
</style>
