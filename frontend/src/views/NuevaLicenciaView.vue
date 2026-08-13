<template>
  <div class="nueva-licencia">
    <div class="page-header">
      <div>
        <h1 class="page-header__title">Nueva Licencia</h1>
        <p class="page-header__subtitle">Iniciar una solicitud de licencia médica</p>
      </div>
    </div>

    <div v-if="!success" class="glass-card" style="max-width: 640px;">
      <form @submit.prevent="crearLicencia">
        <div class="form-group">
          <label class="form-label">Tipo de licencia *</label>
          <select class="form-control" v-model="form.tipo" required>
            <option value="">Seleccione el tipo...</option>
            <option value="salud">Razón de Salud</option>
            <option value="atendible">Razón Atendible</option>
          </select>
        </div>
        <div class="grid grid-cols-2">
          <div class="form-group">
            <label class="form-label">DNI *</label>
            <input type="text" class="form-control" v-model="form.dni" required placeholder="Sin puntos" />
          </div>
          <div class="form-group">
            <label class="form-label">Legajo *</label>
            <input type="text" class="form-control" v-model="form.legajo" required />
          </div>
        </div>

        <div class="grid grid-cols-2">
          <div class="form-group">
            <label class="form-label">Domicilio durante la licencia *</label>
            <input type="text" class="form-control" v-model="form.domicilio" required placeholder="Calle y Número" />
          </div>
          <div class="form-group">
            <label class="form-label">Email de contacto *</label>
            <input type="email" class="form-control" v-model="form.email_contacto" required />
          </div>
        </div>
        
        <div class="flex gap-4 mb-4" style="flex-wrap: wrap;">
          <label style="display:flex; align-items:center; gap:0.5rem; cursor:pointer;">
            <input type="checkbox" v-model="form.es_internacion" />
            <span style="font-weight: 500;">Es caso de internación</span>
          </label>
          <label style="display:flex; align-items:center; gap:0.5rem; cursor:pointer;">
            <input type="checkbox" v-model="form.cursando_licencia_anual" />
            <span style="font-weight: 500;">Me encuentro cursando Licencia Anual</span>
          </label>
        </div>

        <div class="grid grid-cols-2">
          <div class="form-group">
            <label class="form-label">Fecha de inicio *</label>
            <input type="date" class="form-control" v-model="form.fecha_inicio" required />
          </div>
          <div class="form-group">
            <label class="form-label">Cantidad de días *</label>
            <input type="number" class="form-control" v-model="form.dias" min="1" required placeholder="Ej: 1, 2, 7, 15..." />
          </div>
        </div>

        <div class="flex gap-2 mb-4">
          <button type="button" class="badge badge-secondary" style="cursor:pointer;" @click="form.dias = 1">24 hs (1 día)</button>
          <button type="button" class="badge badge-secondary" style="cursor:pointer;" @click="form.dias = 2">48 hs (2 días)</button>
          <button type="button" class="badge badge-secondary" style="cursor:pointer;" @click="form.dias = 3">72 hs (3 días)</button>
          <button type="button" class="badge badge-secondary" style="cursor:pointer;" @click="form.dias = 4">96 hs (4 días)</button>
        </div>

        <div v-if="fechaFinCalculada" class="mb-4">
          <span class="badge badge-primary">Finaliza el: {{ fechaFinCalculada }}</span>
        </div>

        <div class="form-group">
          <label class="form-label">Observaciones (opcional)</label>
          <textarea class="form-control" v-model="form.observaciones" rows="3" placeholder="Alguna observación adicional..."></textarea>
        </div>

        <div class="form-group">
          <label class="form-label">Certificado médico <span v-if="!form.es_internacion">*</span><span v-else>(opcional por internación)</span></label>
          <div class="file-upload" @click="$refs.cert.click()" @dragover.prevent="dragActive = true" @dragleave="dragActive = false" @drop.prevent="onDrop" :class="{ 'file-upload--active': dragActive }">
            <div v-if="certificado">
              <div class="file-upload__icon">📎</div>
              <div class="file-upload__text">{{ certificado.name }}</div>
              <button type="button" class="btn btn-ghost btn-sm mt-2" @click.stop="certificado = null">Quitar archivo</button>
            </div>
            <div v-else>
              <div class="file-upload__icon">📁</div>
              <div class="file-upload__text">Arrastre un archivo o haga click para seleccionar</div>
              <div class="file-upload__hint">PDF, JPG, PNG (máx. 10MB). Las imágenes se convertirán a PDF automáticamente.</div>
            </div>
          </div>
          <input type="file" ref="cert" style="display:none" accept=".pdf,.jpg,.jpeg,.png" @change="onCertSelect" />
          <p class="form-hint">Solo Bienestar podrá ver el certificado. Se enviará por email automáticamente.</p>
        </div>

        <p v-if="error" class="form-error mb-4">{{ error }}</p>

        <div class="flex gap-3 justify-between">
          <button type="button" class="btn btn-secondary" @click="$router.back()">Cancelar</button>
          <button type="submit" class="btn btn-primary btn-lg" :disabled="submitting">
            {{ submitting ? 'Enviando...' : '📤 Iniciar Licencia' }}
          </button>
        </div>
      </form>
    </div>

    <!-- Pantalla de éxito -->
    <div v-if="success" class="glass-card" style="max-width: 640px; text-align: center; padding: 3rem 1.5rem;">
      <div style="font-size: 4rem; margin-bottom: 1rem;">✅</div>
      <h2 style="margin-bottom: 1rem; color: var(--accent-success)">¡Licencia solicitada con éxito!</h2>
      <p style="color: var(--text-secondary); margin-bottom: 2rem;">
        Tu solicitud ha sido registrada correctamente y se ha notificado a Bienestar y a tu jefe directo.
      </p>
      <div class="flex gap-3 justify-center">
        <router-link to="/" class="btn btn-secondary">Ir al Inicio</router-link>
        <router-link :to="`/personal/${usuarioId}/historial`" class="btn btn-primary">Ver mis licencias</router-link>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../services/api'

export default {
  name: 'NuevaLicenciaView',
  inject: ['showToast'],
  data() {
    return {
      form: { 
        tipo: '', fecha_inicio: '', dias: 1, observaciones: '',
        dni: '', legajo: '', domicilio: '', email_contacto: '',
        es_internacion: false, cursando_licencia_anual: false,
        tipo_atencion: 'presencial', doctor_nombre: ''
      },
      doctoresTelemedicina: [
        'DR. TELEMEDICINA 1', 'DR. TELEMEDICINA 2', 'DR. TELEMEDICINA 3',
        'DR. TELEMEDICINA 4', 'DR. TELEMEDICINA 5', 'DR. TELEMEDICINA 6',
        'DR. TELEMEDICINA 7', 'DR. TELEMEDICINA 8', 'DR. TELEMEDICINA 9',
        'DR. TELEMEDICINA 10', 'DR. TELEMEDICINA 11', 'DR. TELEMEDICINA 12',
        'DR. TELEMEDICINA 13', 'DR. TELEMEDICINA 14', 'DR. TELEMEDICINA 15'
      ],
      certificado: null,
      dragActive: false,
      submitting: false,
      error: '',
      success: false,
      usuarioId: null,
    }
  },
  computed: {
    fechaFinCalculada() {
      if (!this.form.fecha_inicio || !this.form.dias || this.form.dias < 1) return ''
      const d1 = new Date(this.form.fecha_inicio)
      // Ajustar fecha fin sumando (dias - 1) dias calendario
      d1.setDate(d1.getDate() + parseInt(this.form.dias) - 1)
      
      // Formatear a yyyy-mm-dd
      const year = d1.getUTCFullYear()
      const month = String(d1.getUTCMonth() + 1).padStart(2, '0')
      const day = String(d1.getUTCDate()).padStart(2, '0')
      return `${day}/${month}/${year}`
    },
    fechaFinFormatoBackend() {
      if (!this.form.fecha_inicio || !this.form.dias || this.form.dias < 1) return ''
      const d1 = new Date(this.form.fecha_inicio)
      d1.setDate(d1.getDate() + parseInt(this.form.dias) - 1)
      const year = d1.getUTCFullYear()
      const month = String(d1.getUTCMonth() + 1).padStart(2, '0')
      const day = String(d1.getUTCDate()).padStart(2, '0')
      return `${year}-${month}-${day}`
    },
  },
  methods: {
    onCertSelect(e) {
      this.certificado = e.target.files[0]
    },
    onDrop(e) {
      this.dragActive = false
      const file = e.dataTransfer.files[0]
      if (file) this.certificado = file
    },
    formatearDoctor() {
      if (this.form.doctor_nombre) {
        let val = this.form.doctor_nombre.normalize('NFD').replace(/[\u0300-\u036f]/g, '')
        this.form.doctor_nombre = val.toUpperCase()
      }
    },
    async cargarUsuario() {
      // Necesitamos el ID del usuario para el botón "Ver mis licencias"
      try {
        const authService = (await import('../services/authService')).default
        const usr = authService.getUsuario()
        if (usr) this.usuarioId = usr.id
      } catch (e) {
        console.error(e)
      }
    },
    async crearLicencia() {
      this.error = ''
      if (!this.form.fecha_inicio || !this.form.dias || this.form.dias < 1) {
        this.error = 'Debe ingresar una cantidad de días válida.'
        return
      }

      if (!this.form.es_internacion && !this.certificado) {
        this.error = 'Debe adjuntar el certificado médico salvo caso de internación.'
        return
      }

      this.submitting = true
      try {
        const formData = new FormData()
        formData.append('tipo', this.form.tipo)
        formData.append('fecha_inicio', this.form.fecha_inicio)
        formData.append('fecha_fin', this.fechaFinFormatoBackend)
        formData.append('dni', this.form.dni)
        formData.append('legajo', this.form.legajo)
        formData.append('domicilio', this.form.domicilio)
        formData.append('email_contacto', this.form.email_contacto)
        formData.append('es_internacion', this.form.es_internacion ? 'True' : 'False')
        formData.append('cursando_licencia_anual', this.form.cursando_licencia_anual ? 'True' : 'False')
        formData.append('tipo_atencion', this.form.tipo_atencion)
        formData.append('doctor_nombre', this.form.doctor_nombre)
        
        if (this.form.observaciones) formData.append('observaciones', this.form.observaciones)
        if (this.certificado) formData.append('certificado_medico', this.certificado)

        await api.post('/licencias/', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
        await this.cargarUsuario()
        this.success = true
        this.showToast('Licencia iniciada correctamente.', 'success')
      } catch (e) {
        const data = e.response?.data
        if (data) {
          const msgs = Object.values(data).flat()
          this.error = msgs.join(' ')
        } else {
          this.error = 'Error al crear la licencia.'
        }
      } finally {
        this.submitting = false
      }
    },
  },
}
</script>
