<template>
  <div class="login-page">
    <div class="login-bg"></div>
    <div class="login-container">
      <div class="login-card glass-card">
        <div class="login-header">
          <span class="login-icon">🏥</span>
          <h1 class="login-title">Aviso de Licencias Policiales</h1>
          <p class="login-subtitle">Sistema de Gestión</p>
        </div>

        <form @submit.prevent="handleLogin" class="login-form">
          <div class="form-group">
            <label class="form-label" for="username">Usuario</label>
            <input
              id="username"
              type="text"
              class="form-control"
              v-model="username"
              placeholder="Ingrese su usuario"
              autocomplete="username"
              required
              :disabled="loading"
            />
          </div>

          <div class="form-group">
            <label class="form-label" for="password">Contraseña</label>
            <div class="password-wrapper">
              <input
                id="password"
                :type="showPassword ? 'text' : 'password'"
                class="form-control"
                v-model="password"
                placeholder="Ingrese su contraseña"
                autocomplete="current-password"
                required
                :disabled="loading"
              />
              <button
                type="button"
                class="password-toggle"
                @click="showPassword = !showPassword"
                tabindex="-1"
              >
                {{ showPassword ? '🙈' : '👁️' }}
              </button>
            </div>
          </div>

          <p v-if="error" class="login-error">{{ error }}</p>

          <button type="submit" class="btn btn-primary btn-lg w-full" :disabled="loading">
            <span v-if="loading" class="spinner" style="width:18px;height:18px;border-width:2px;"></span>
            {{ loading ? 'Ingresando...' : 'Ingresar' }}
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import authService from '../services/authService'

export default {
  name: 'LoginView',
  data() {
    return {
      username: '',
      password: '',
      showPassword: false,
      loading: false,
      error: '',
    }
  },
  methods: {
    async handleLogin() {
      this.error = ''
      this.loading = true

      try {
        await authService.login(this.username, this.password)
        this.$router.push('/')
      } catch (e) {
        this.error = e.response?.data?.error || 'Error al iniciar sesión. Intente nuevamente.'
      } finally {
        this.loading = false
      }
    },
  },
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  position: relative;
}

.login-bg {
  position: fixed;
  inset: 0;
  background:
    radial-gradient(ellipse at 30% 20%, rgba(59, 130, 246, 0.15) 0%, transparent 50%),
    radial-gradient(ellipse at 70% 80%, rgba(139, 92, 246, 0.1) 0%, transparent 50%),
    var(--bg-primary);
  z-index: 0;
}

.login-container {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 420px;
}

.login-card {
  padding: 2.5rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: var(--shadow-xl), 0 0 40px rgba(59, 130, 246, 0.1);
}

.login-header {
  text-align: center;
  margin-bottom: 2rem;
}

.login-icon {
  font-size: 3rem;
  display: block;
  margin-bottom: 0.75rem;
  filter: drop-shadow(0 0 10px rgba(59, 130, 246, 0.3));
}

.login-title {
  font-size: 1.625rem;
  font-weight: 700;
  background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 0.25rem;
}

.login-subtitle {
  font-size: 0.875rem;
  color: var(--text-muted);
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.password-wrapper {
  position: relative;
}

.password-wrapper .form-control {
  padding-right: 2.5rem;
}

.password-toggle {
  position: absolute;
  right: 0.5rem;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1rem;
  padding: 0.25rem;
  opacity: 0.7;
}

.password-toggle:hover {
  opacity: 1;
}

.login-error {
  color: var(--accent-danger);
  font-size: 0.8125rem;
  text-align: center;
  padding: 0.5rem;
  background: var(--accent-danger-light);
  border-radius: var(--border-radius-sm);
}

@media (max-width: 480px) {
  .login-card {
    padding: 1.5rem;
  }
}
</style>
