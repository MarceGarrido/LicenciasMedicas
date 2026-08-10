import api from './api'

export const authService = {
  async login(username, password) {
    const response = await api.post('/auth/login/', { username, password })
    const { token, usuario } = response.data
    localStorage.setItem('auth_token', token)
    localStorage.setItem('usuario', JSON.stringify(usuario))
    return usuario
  },

  async logout() {
    try {
      await api.post('/auth/logout/')
    } catch (e) {
      // Ignorar errores de logout
    }
    localStorage.removeItem('auth_token')
    localStorage.removeItem('usuario')
  },

  async getMe() {
    const response = await api.get('/auth/me/')
    localStorage.setItem('usuario', JSON.stringify(response.data))
    return response.data
  },

  async cambiarPassword(passwordActual, passwordNuevo) {
    const response = await api.put('/auth/cambiar-password/', {
      password_actual: passwordActual,
      password_nuevo: passwordNuevo,
    })
    if (response.data.token) {
      localStorage.setItem('auth_token', response.data.token)
    }
    return response.data
  },

  getUsuario() {
    const data = localStorage.getItem('usuario')
    return data ? JSON.parse(data) : null
  },

  setUsuario(usuario) {
    localStorage.setItem('usuario', JSON.stringify(usuario))
  },

  getToken() {
    return localStorage.getItem('auth_token')
  },

  isAuthenticated() {
    return !!localStorage.getItem('auth_token')
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
