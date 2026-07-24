"""
Configuración del panel de administración de Django.
"""
from django.contrib import admin
from .models import Ciudad, Dependencia, TipoPersonal, Jerarquia, Usuario, Licencia, Circular


@admin.register(Ciudad)
class CiudadAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'email_bienestar', 'activa', 'fecha_creacion']
    list_filter = ['activa']
    search_fields = ['nombre']


@admin.register(Dependencia)
class DependenciaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'ciudad', 'email', 'activa', 'fecha_creacion']
    list_filter = ['ciudad', 'activa']
    search_fields = ['nombre']


@admin.register(TipoPersonal)
class TipoPersonalAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'orden', 'activo', 'fecha_creacion']
    list_filter = ['activo']


@admin.register(Jerarquia)
class JerarquiaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'tipo_personal', 'orden', 'activa', 'fecha_creacion']
    list_filter = ['tipo_personal', 'activa']
    search_fields = ['nombre']


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ['username', 'nombre_completo', 'rol', 'jerarquia', 'dependencia', 'is_active']
    list_filter = ['rol', 'is_active', 'dependencia__ciudad']
    search_fields = ['username', 'nombre_completo']


@admin.register(Licencia)
class LicenciaAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'tipo', 'estado', 'fecha_inicio', 'fecha_fin', 'fecha_creacion']
    list_filter = ['tipo', 'estado', 'fecha_creacion']
    search_fields = ['usuario__nombre_completo']
    date_hierarchy = 'fecha_creacion'


@admin.register(Circular)
class CircularAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'publicado_por', 'fecha_publicacion']
    search_fields = ['titulo']
    date_hierarchy = 'fecha_publicacion'
