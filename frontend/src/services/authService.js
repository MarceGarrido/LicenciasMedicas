import api from './api'

export const authService = {
  async login(username, password) {
    const response = await api.post('/auth/login/', { username, password })
    const { token, usuario } = response.data
    sessionStorage.setItem('auth_token', token)
    sessionStorage.setItem('usuario', JSON.stringify(usuario))
    return usuario
  },

  async logout() {
    try {
      await api.post('/auth/logout/')
    } catch (e) {
      // Ignorar errores de logout
    }
    sessionStorage.removeItem('auth_token')
    sessionStorage.removeItem('usuario')
  },

  async getMe() {
    const response = await api.get('/auth/me/')
    sessionStorage.setItem('usuario', JSON.stringify(response.data))
    return response.data
  },

  async cambiarPassword(passwordActual, passwordNuevo) {
    const response = await api.put('/auth/cambiar-password/', {
      password_actual: passwordActual,
      password_nuevo: passwordNuevo,
    })
    if (response.data.token) {
      sessionStorage.setItem('auth_token', response.data.token)
    }
    return response.data
  },

  getUsuario() {
    const data = sessionStorage.getItem('usuario')
    return data ? JSON.parse(data) : null
  },

  setUsuario(usuario) {
    sessionStorage.setItem('usuario', JSON.stringify(usuario))
  },

  getToken() {
    return sessionStorage.getItem('auth_token')
  },

  isAuthenticated() {
    return !!sessionStorage.getItem('auth_token')
  },

  tieneRol(rol) {
    const usuario = this.getUsuario()
    if (!usuario) return false
    if (Array.isArray(rol)) {
      return rol.includes(usuario.rol)
    }
    return usuario.rol === rol
  },
}

export default authService
