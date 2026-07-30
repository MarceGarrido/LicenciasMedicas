"""
Serializers del Sistema de Licencias Médicas.
"""
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import (
    Ciudad, Dependencia, TipoPersonal, Jerarquia,
    Usuario, Licencia, Circular
)


# ─── Geografía ───

class CiudadSerializer(serializers.ModelSerializer):
    cantidad_dependencias = serializers.SerializerMethodField()

    class Meta:
        model = Ciudad
        fields = ['id', 'nombre', 'email_bienestar', 'activa', 'cantidad_dependencias', 'fecha_creacion']
        read_only_fields = ['fecha_creacion']

    def get_cantidad_dependencias(self, obj):
        return obj.dependencias.filter(activa=True).count()


class DependenciaSerializer(serializers.ModelSerializer):
    ciudad_nombre = serializers.CharField(source='ciudad.nombre', read_only=True)

    class Meta:
        model = Dependencia
        fields = ['id', 'nombre', 'email', 'ciudad', 'ciudad_nombre', 'activa', 'fecha_creacion']
        read_only_fields = ['fecha_creacion']


# ─── Jerarquías ───

class JerarquiaSerializer(serializers.ModelSerializer):
    tipo_personal_nombre = serializers.CharField(source='tipo_personal.nombre', read_only=True)

    class Meta:
        model = Jerarquia
        fields = ['id', 'nombre', 'tipo_personal', 'tipo_personal_nombre', 'orden', 'activa', 'fecha_creacion']
        read_only_fields = ['fecha_creacion']


class TipoPersonalSerializer(serializers.ModelSerializer):
    jerarquias = JerarquiaSerializer(many=True, read_only=True)

    class Meta:
        model = TipoPersonal
        fields = ['id', 'nombre', 'orden', 'activo', 'jerarquias', 'fecha_creacion']
        read_only_fields = ['fecha_creacion']


# ─── Usuarios ───

class UsuarioListSerializer(serializers.ModelSerializer):
    """Serializer para listado de usuarios (sin datos sensibles)."""
    jerarquia_nombre = serializers.CharField(source='jerarquia.nombre', read_only=True, default=None)
    dependencia_nombre = serializers.CharField(source='dependencia.nombre', read_only=True, default=None)
    ciudad_nombre = serializers.SerializerMethodField()
    tipo_personal_nombre = serializers.SerializerMethodField()
    total_licencias = serializers.SerializerMethodField()

    class Meta:
        model = Usuario
        fields = [
            'id', 'username', 'nombre_completo', 'rol',
            'jerarquia', 'jerarquia_nombre',
            'dependencia', 'dependencia_nombre',
            'ciudad_nombre', 'tipo_personal_nombre',
            'total_licencias', 'is_active',
        ]

    def get_ciudad_nombre(self, obj):
        if obj.dependencia and obj.dependencia.ciudad:
            return obj.dependencia.ciudad.nombre
        return None

    def get_tipo_personal_nombre(self, obj):
        if obj.jerarquia and obj.jerarquia.tipo_personal:
            return obj.jerarquia.tipo_personal.nombre
        return None

    def get_total_licencias(self, obj):
        # Usar el valor anotado si existe (evita N+1 queries)
        return getattr(obj, 'total_licencias', obj.licencias.count())


class UsuarioDetailSerializer(serializers.ModelSerializer):
    """Serializer para detalle de usuario (incluye datos del perfil)."""
    jerarquia_nombre = serializers.CharField(source='jerarquia.nombre', read_only=True, default=None)
    dependencia_nombre = serializers.CharField(source='dependencia.nombre', read_only=True, default=None)
    ciudad_nombre = serializers.SerializerMethodField()
    tipo_personal_nombre = serializers.SerializerMethodField()

    class Meta:
        model = Usuario
        fields = [
            'id', 'username', 'nombre_completo', 'rol', 'email',
            'jerarquia', 'jerarquia_nombre',
            'dependencia', 'dependencia_nombre',
            'ciudad_nombre', 'tipo_personal_nombre',
            'is_active', 'date_joined',
        ]
        read_only_fields = ['date_joined']

    def get_ciudad_nombre(self, obj):
        if obj.dependencia and obj.dependencia.ciudad:
            return obj.dependencia.ciudad.nombre
        return None

    def get_tipo_personal_nombre(self, obj):
        if obj.jerarquia and obj.jerarquia.tipo_personal:
            return obj.jerarquia.tipo_personal.nombre
        return None


class UsuarioCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear usuarios (Admin)."""
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = Usuario
        fields = [
            'id', 'username', 'password', 'nombre_completo',
            'rol', 'email', 'jerarquia', 'dependencia', 'is_active',
        ]

    def create(self, validated_data):
        password = validated_data.pop('password')
        usuario = Usuario(**validated_data)
        usuario.set_password(password)
        usuario.save()
        return usuario


class UsuarioUpdateSerializer(serializers.ModelSerializer):
    """Serializer para actualizar usuarios (Admin)."""
    password = serializers.CharField(write_only=True, required=False, validators=[validate_password])

    class Meta:
        model = Usuario
        fields = [
            'id', 'username', 'password', 'nombre_completo',
            'rol', 'email', 'jerarquia', 'dependencia', 'is_active',
        ]

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class CambiarPasswordSerializer(serializers.Serializer):
    """Serializer para cambio de contraseña propia."""
    password_actual = serializers.CharField()
    password_nuevo = serializers.CharField(validators=[validate_password])

    def validate_password_actual(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('La contraseña actual es incorrecta.')
        return value


# ─── Licencias ───

class LicenciaSerializer(serializers.ModelSerializer):
    """Serializer para licencias."""
    usuario_nombre = serializers.CharField(source='usuario.nombre_completo', read_only=True)
    usuario_jerarquia = serializers.CharField(source='usuario.jerarquia.nombre', read_only=True, default=None)
    usuario_dependencia = serializers.CharField(source='usuario.dependencia.nombre', read_only=True, default=None)
    usuario_ciudad = serializers.SerializerMethodField()
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    dias_licencia = serializers.IntegerField(read_only=True)
    tiene_certificado = serializers.SerializerMethodField()

    class Meta:
        model = Licencia
        fields = [
            'id', 'usuario', 'usuario_nombre', 'usuario_jerarquia',
            'usuario_dependencia', 'usuario_ciudad',
            'tipo', 'tipo_display', 'estado', 'estado_display',
            'fecha_inicio', 'fecha_fin', 'dias_licencia',
            'observaciones', 'tiene_certificado',
            'fecha_creacion', 'fecha_actualizacion',
        ]
        read_only_fields = ['usuario', 'fecha_creacion', 'fecha_actualizacion']

    def get_usuario_ciudad(self, obj):
        if obj.usuario.dependencia and obj.usuario.dependencia.ciudad:
            return obj.usuario.dependencia.ciudad.nombre
        return None

    def get_tiene_certificado(self, obj):
        return bool(obj.certificado_medico)


class LicenciaCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear licencias (Personal)."""
    class Meta:
        model = Licencia
        fields = ['id', 'tipo', 'fecha_inicio', 'fecha_fin', 'observaciones', 'certificado_medico']

    def validate(self, data):
        if data.get('fecha_fin') and data.get('fecha_inicio') and data['fecha_fin'] < data['fecha_inicio']:
            raise serializers.ValidationError(
                {'fecha_fin': 'La fecha de fin no puede ser anterior a la fecha de inicio.'}
            )
        return data

    def validate_certificado_medico(self, value):
        from .utils import validar_y_convertir_a_pdf
        return validar_y_convertir_a_pdf(value)

    def create(self, validated_data):
        validated_data['usuario'] = self.context['request'].user
        return super().create(validated_data)


class LicenciaEstadoSerializer(serializers.ModelSerializer):
    """Serializer para actualizar el estado de una licencia (Bienestar)."""
    class Meta:
        model = Licencia
        fields = ['estado']


# ─── Circulares ───

class CircularSerializer(serializers.ModelSerializer):
    """Serializer para circulares."""
    publicado_por_nombre = serializers.CharField(
        source='publicado_por.nombre_completo', read_only=True, default=None
    )
    archivo_nombre = serializers.SerializerMethodField()
    archivo_url = serializers.SerializerMethodField()

    class Meta:
        model = Circular
        fields = [
            'id', 'titulo', 'descripcion', 'archivo', 'archivo_nombre',
            'archivo_url', 'fecha_publicacion', 'publicado_por', 'publicado_por_nombre',
        ]
        read_only_fields = ['fecha_publicacion', 'publicado_por']

    def get_archivo_nombre(self, obj):
        if obj.archivo:
            return obj.archivo.name.split('/')[-1]
        return None

    def get_archivo_url(self, obj):
        if obj.archivo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.archivo.url)
        return None

    def create(self, validated_data):
        validated_data['publicado_por'] = self.context['request'].user
        return super().create(validated_data)
