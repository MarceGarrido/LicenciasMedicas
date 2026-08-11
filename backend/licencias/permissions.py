"""
Permisos personalizados por rol.
"""
from rest_framework.permissions import BasePermission


class EsAdmin(BasePermission):
    """Solo usuarios con rol Administrador."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol == 'admin'


class EsRRHH(BasePermission):
    """Solo usuarios con rol Recursos Humanos."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol == 'rrhh'


class EsBienestar(BasePermission):
    """Solo usuarios con rol Bienestar."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol == 'bienestar'


class EsPersonal(BasePermission):
    """Solo usuarios con rol Personal."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol == 'personal'


class EsAdminOBienestar(BasePermission):
    """Administrador o Bienestar."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol in ('admin', 'bienestar')


class EsAdminORRHH(BasePermission):
    """Administrador o Recursos Humanos."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol in ('admin', 'rrhh')


class PuedeCrearLicencia(BasePermission):
    """Personal puede crear licencias."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol in ('personal', 'admin')


class PuedeVerCertificado(BasePermission):
    """Solo Bienestar puede ver certificados médicos."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol == 'bienestar'


class EsDuenoOBienestar(BasePermission):
    """El dueño de la licencia o Bienestar/Admin."""
    def has_object_permission(self, request, view, obj):
        if request.user.rol in ('bienestar', 'admin'):
            return True
        return obj.usuario == request.user
