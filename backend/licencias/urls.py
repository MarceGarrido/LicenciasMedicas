"""
URLs del Sistema de Licencias Médicas.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import reports

# Router para ViewSets de administración
router = DefaultRouter()
router.register(r'admin/usuarios', views.AdminUsuarioViewSet, basename='admin-usuarios')
router.register(r'admin/ciudades', views.AdminCiudadViewSet, basename='admin-ciudades')
router.register(r'admin/dependencias', views.AdminDependenciaViewSet, basename='admin-dependencias')
router.register(r'admin/tipos-personal', views.AdminTipoPersonalViewSet, basename='admin-tipos-personal')
router.register(r'admin/jerarquias', views.AdminJerarquiaViewSet, basename='admin-jerarquias')

urlpatterns = [
    # Autenticación
    path('auth/login/', views.login_view, name='login'),
    path('auth/logout/', views.logout_view, name='logout'),
    path('auth/me/', views.me_view, name='me'),
    path('auth/cambiar-password/', views.cambiar_password_view, name='cambiar-password'),
    path('auth/actualizar-perfil/', views.actualizar_perfil_view, name='actualizar-perfil'),

    # Gestión masiva (Admin)
    path('admin/usuarios/carga-masiva/', views.carga_masiva_usuarios_view, name='carga-masiva'),
    path('admin/usuarios/ascenso-lote/', views.ascenso_lote_view, name='ascenso-lote'),

    # Circulares
    path('circulares/', views.CircularListCreateView.as_view(), name='circulares-list'),
    path('circulares/<int:pk>/', views.CircularDeleteView.as_view(), name='circulares-delete'),

    # Licencias
    path('licencias/', views.LicenciaListCreateView.as_view(), name='licencias-list'),
    path('licencias/<int:pk>/', views.LicenciaDetailView.as_view(), name='licencias-detail'),
    path('licencias/<int:pk>/certificado/', views.subir_certificado_view, name='licencias-certificado-upload'),
    path('licencias/<int:pk>/certificado/descargar/', views.descargar_certificado_view, name='licencias-certificado-download'),

    # Personal y reportes (Bienestar)
    path('personal/', views.personal_list_view, name='personal-list'),
    path('personal/<int:pk>/licencias/', views.personal_licencias_view, name='personal-licencias'),
    path('reportes/resumen/', views.reportes_resumen_view, name='reportes-resumen'),
    path('reportes/exportar/excel/', reports.exportar_excel, name='reportes-excel'),
    path('reportes/exportar/pdf/', reports.exportar_pdf, name='reportes-pdf'),

    # Datos auxiliares (para formularios)
    path('ciudades/', views.ciudades_list_view, name='ciudades-list'),
    path('dependencias/', views.dependencias_list_view, name='dependencias-list'),
    path('jerarquias/', views.jerarquias_list_view, name='jerarquias-list'),

    # Admin ViewSets
    path('', include(router.urls)),
]
