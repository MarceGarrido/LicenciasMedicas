"""
Modelos del Sistema de Licencias Médicas.
"""
import os
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator


def certificado_upload_path(instance, filename):
    """Genera ruta segura para certificados médicos."""
    ext = os.path.splitext(filename)[1]
    return f'certificados/usuario_{instance.usuario.id}/{instance.id or "temp"}_{filename}'


def circular_upload_path(instance, filename):
    """Genera ruta para archivos de circulares."""
    return f'circulares/{filename}'


# ─── Geografía / Estructura organizacional ───

class Ciudad(models.Model):
    """Ciudades de la provincia (Río Grande, Ushuaia, Tolhuin)."""
    nombre = models.CharField(max_length=100, unique=True)
    email_bienestar = models.EmailField(
        blank=True,
        default='',
        help_text='Email de Bienestar correspondiente a esta ciudad'
    )
    activa = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Ciudad'
        verbose_name_plural = 'Ciudades'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Dependencia(models.Model):
    """Dependencias policiales (Comisarías, Direcciones, etc.)."""
    nombre = models.CharField(max_length=200)
    email = models.EmailField(
        blank=True,
        default='',
        help_text='Email de contacto de la dependencia'
    )
    ciudad = models.ForeignKey(
        Ciudad,
        on_delete=models.PROTECT,
        related_name='dependencias'
    )
    activa = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Dependencia'
        verbose_name_plural = 'Dependencias'
        ordering = ['ciudad__nombre', 'nombre']
        unique_together = ['nombre', 'ciudad']

    def __str__(self):
        return f'{self.nombre} - {self.ciudad.nombre}'


# ─── Jerarquías ───

class TipoPersonal(models.Model):
    """Tipos de personal: Oficiales, Suboficiales, Auxiliares."""
    nombre = models.CharField(max_length=100, unique=True)
    orden = models.IntegerField(
        default=0,
        help_text='Orden de visualización (menor = primero)'
    )
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Tipo de Personal'
        verbose_name_plural = 'Tipos de Personal'
        ordering = ['orden', 'nombre']

    def __str__(self):
        return self.nombre


class Jerarquia(models.Model):
    """Jerarquías dentro de cada tipo de personal."""
    nombre = models.CharField(max_length=100)
    tipo_personal = models.ForeignKey(
        TipoPersonal,
        on_delete=models.PROTECT,
        related_name='jerarquias'
    )
    orden = models.IntegerField(
        default=0,
        help_text='Orden jerárquico (mayor = más alto rango)'
    )
    activa = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Jerarquía'
        verbose_name_plural = 'Jerarquías'
        ordering = ['tipo_personal__orden', '-orden']
        unique_together = ['nombre', 'tipo_personal']

    def __str__(self):
        return f'{self.nombre} ({self.tipo_personal.nombre})'


# ─── Usuarios ───

class Usuario(AbstractUser):
    """Usuario del sistema con rol y datos institucionales."""
    ROL_CHOICES = [
        ('admin', 'Administrador'),
        ('supervisor', 'Supervisor'),
        ('personal', 'Personal'),
        ('rrhh', 'Recursos Humanos'),
        ('bienestar', 'Bienestar'),
    ]

    rol = models.CharField(
        max_length=20,
        choices=ROL_CHOICES,
        default='personal'
    )
    dni = models.CharField(max_length=20, blank=True, default='')
    legajo = models.CharField(max_length=20, blank=True, default='')
    nombre_completo = models.CharField(max_length=200)
    jerarquia = models.ForeignKey(
        Jerarquia,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='usuarios'
    )
    dependencia = models.ForeignKey(
        Dependencia,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='usuarios'
    )

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['nombre_completo']

    def __str__(self):
        return self.nombre_completo or self.username

    @property
    def ciudad(self):
        """Ciudad del usuario a través de su dependencia."""
        if self.dependencia:
            return self.dependencia.ciudad
        return None

    @property
    def es_admin(self):
        return self.rol == 'admin'

    @property
    def es_personal(self):
        return self.rol == 'personal'

    @property
    def es_rrhh(self):
        return self.rol == 'rrhh'

    @property
    def es_bienestar(self):
        return self.rol == 'bienestar'

    @property
    def es_supervisor(self):
        return self.rol == 'supervisor'


# ─── Licencias ───

class Licencia(models.Model):
    """Licencia médica del personal."""
    TIPO_CHOICES = [
        ('salud', 'Razón de Salud'),
        ('atendible', 'Razón Atendible'),
    ]
    ESTADO_CHOICES = [
        ('iniciada', 'Iniciada'),
        ('en_curso', 'En Curso'),
        ('finalizada', 'Finalizada'),
    ]

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='licencias'
    )
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='iniciada',
        help_text='Estado real en base de datos (obsoleto, se calcula en estado_actual)'
    )
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    domicilio = models.CharField(max_length=255, blank=True, default='', help_text='Domicilio real durante la licencia')
    email_contacto = models.EmailField(blank=True, default='', help_text='Email de contacto')
    cursando_licencia_anual = models.BooleanField(default=False)
    es_internacion = models.BooleanField(default=False)
    observaciones = models.TextField(blank=True, default='')
    certificado_medico = models.FileField(
        upload_to='certificados/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(
            allowed_extensions=['pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx']
        )],
        help_text='Certificado médico (solo visible para Bienestar)'
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Licencia'
        verbose_name_plural = 'Licencias'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f'{self.usuario.nombre_completo} - {self.get_tipo_display()} ({self.get_estado_actual_display()})'

    @property
    def estado_actual(self):
        """Calcula el estado de forma dinámica basado en la fecha."""
        from django.utils import timezone
        hoy = timezone.localdate()
        
        if hoy < self.fecha_inicio:
            return 'iniciada'
        elif self.fecha_inicio <= hoy <= self.fecha_fin:
            return 'en_curso'
        else:
            return 'finalizada'

    def get_estado_actual_display(self):
        estados = dict(self.ESTADO_CHOICES)
        return estados.get(self.estado_actual, self.estado_actual)

    @property
    def dias_licencia(self):
        """Calcula los días de licencia."""
        if self.fecha_inicio and self.fecha_fin:
            delta = self.fecha_fin - self.fecha_inicio
            return delta.days + 1  # Incluye ambos días
        return 0


# ─── Circulares ───

class Circular(models.Model):
    """Circulares publicadas por Recursos Humanos."""
    titulo = models.CharField(max_length=300)
    descripcion = models.TextField(blank=True, default='')
    archivo = models.FileField(
        upload_to='circulares/',
        validators=[FileExtensionValidator(
            allowed_extensions=['pdf', 'doc', 'docx']
        )],
        help_text='Archivo PDF o Word de la circular'
    )
    fecha_publicacion = models.DateTimeField(auto_now_add=True)
    publicado_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        related_name='circulares_publicadas'
    )

    class Meta:
        verbose_name = 'Circular'
        verbose_name_plural = 'Circulares'
        ordering = ['-fecha_publicacion']

    def __str__(self):
        return self.titulo
