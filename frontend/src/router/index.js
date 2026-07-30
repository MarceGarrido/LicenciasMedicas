import { createRouter, createWebHistory } from 'vue-router'
import authService from '../services/authService'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/LoginView.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/',
    name: 'Inicio',
    component: () => import('../views/DashboardView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/circulares',
    name: 'Circulares',
    component: () => import('../views/CircularesView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/circulares/gestionar',
    name: 'GestionCirculares',
    component: () => import('../views/GestionCircularesView.vue'),
    meta: { requiresAuth: true, roles: ['rrhh', 'admin'] },
  },
  {
    path: '/licencias/nueva',
    name: 'NuevaLicencia',
    component: () => import('../views/NuevaLicenciaView.vue'),
    meta: { requiresAuth: true, roles: ['personal', 'admin'] },
  },
  {
    path: '/licencias/mis-licencias',
    name: 'MisLicencias',
    component: () => import('../views/MisLicenciasView.vue'),
    meta: { requiresAuth: true, roles: ['personal', 'admin'] },
  },
  {
    path: '/licencias/gestion',
    name: 'GestionLicencias',
    component: () => import('../views/GestionLicenciasView.vue'),
    meta: { requiresAuth: true, roles: ['bienestar', 'admin'] },
  },
  {
    path: '/personal',
    name: 'ListadoPersonal',
    component: () => import('../views/ListadoPersonalView.vue'),
    meta: { requiresAuth: true, roles: ['rrhh', 'bienestar', 'admin'] },
  },
  {
    path: '/personal/:id/historial',
    name: 'HistorialPersonal',
    component: () => import('../views/HistorialPersonalView.vue'),
    meta: { requiresAuth: true, roles: ['bienestar', 'admin'] },
  },
  {
    path: '/reportes',
    name: 'Reportes',
    component: () => import('../views/ReportesView.vue'),
    meta: { requiresAuth: true, roles: ['bienestar', 'admin'] },
  },
  {
    path: '/admin/usuarios',
    name: 'AdminUsuarios',
    component: () => import('../views/admin/AdminUsuariosView.vue'),
    meta: { requiresAuth: true, roles: ['admin'] },
  },
  {
    path: '/admin/dependencias',
    name: 'AdminDependencias',
    component: () => import('../views/admin/AdminDependenciasView.vue'),
    meta: { requiresAuth: true, roles: ['admin'] },
  },
  {
    path: '/admin/ciudades',
    name: 'AdminCiudades',
    component: () => import('../views/admin/AdminCiudadesView.vue'),
    meta: { requiresAuth: true, roles: ['admin'] },
  },
  {
    path: '/admin/jerarquias',
    name: 'AdminJerarquias',
    component: () => import('../views/admin/AdminJerarquiasView.vue'),
    meta: { requiresAuth: true, roles: ['admin'] },
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/',
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Guard de navegación
router.beforeEach((to, from, next) => {
  const requiresAuth = to.meta.requiresAuth !== false
  const isAuthenticated = authService.isAuthenticated()

  if (requiresAuth && !isAuthenticated) {
    next('/login')
    return
  }

  if (to.path === '/login' && isAuthenticated) {
    next('/')
    return
  }

  // Verificar roles
  if (to.meta.roles) {
    const usuario = authService.getUsuario()
    if (usuario && usuario.rol !== 'admin' && !to.meta.roles.includes(usuario.rol)) {
      next('/')
      return
    }
  }

  next()
})

export default router
