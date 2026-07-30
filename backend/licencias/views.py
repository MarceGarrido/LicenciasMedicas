"""
API Views del Sistema de Licencias Médicas.
"""
import logging
from django.contrib.auth import authenticate
from django.db.models import Count, Q
from rest_framework import status, generics, viewsets
from rest_framework.decorators import api_view, permission_classes, action, throttle_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.throttling import ScopedRateThrottle

from .models import (
    Ciudad, Dependencia, TipoPersonal, Jerarquia,
    Usuario, Licencia, Circular
)
from .serializers import (
    CiudadSerializer, DependenciaSerializer,
    TipoPersonalSerializer, JerarquiaSerializer,
    UsuarioListSerializer, UsuarioDetailSerializer,
    UsuarioCreateSerializer, UsuarioUpdateSerializer,
    CambiarPasswordSerializer,
    LicenciaSerializer, LicenciaCreateSerializer, LicenciaEstadoSerializer,
    CircularSerializer,
)
from .permissions import (
    EsAdmin, EsRRHH, EsBienestar, EsAdminOBienestar, EsAdminORRHH,
    PuedeCrearLicencia, PuedeVerCertificado, EsDuenoOBienestar,
)
from .email_service import enviar_email_nueva_licencia, enviar_email_certificado

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════
# AUTENTICACIÓN
# ═══════════════════════════════════════════

@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([ScopedRateThrottle])
def login_view(request):
    """Login con username y password, devuelve token."""
    request.throttle_scope = 'login'
    username = request.data.get('username', '').strip()
    password = request.data.get('password', '')

    if not username or not password:
        return Response(
            {'error': 'Se requieren usuario y contraseña.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = authenticate(username=username, password=password)

    if user is None:
        return Response(
            {'error': 'Credenciales inválidas.'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    if not user.is_active:
        return Response(
            {'error': 'Usuario desactivado. Contacte al administrador.'},
            status=status.HTTP_403_FORBIDDEN
        )

    token, _ = Token.objects.get_or_create(user=user)

    serializer = UsuarioDetailSerializer(user)
    return Response({
        'token': token.key,
        'usuario': serializer.data,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """Elimina el token del usuario."""
    try:
        request.user.auth_token.delete()
    except Exception:
        pass
    return Response({'message': 'Sesión cerrada correctamente.'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me_view(request):
    """Devuelve datos del usuario autenticado."""
    serializer = UsuarioDetailSerializer(request.user)
    return Response(serializer.data)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def cambiar_password_view(request):
    """Cambiar contraseña propia."""
    serializer = CambiarPasswordSerializer(data=request.data, context={'request': request})
    serializer.is_valid(raise_exception=True)
    request.user.set_password(serializer.validated_data['password_nuevo'])
    request.user.save()

    # Regenerar token
    try:
        request.user.auth_token.delete()
    except Exception:
        pass
    token = Token.objects.create(user=request.user)

    return Response({
        'message': 'Contraseña actualizada correctamente.',
        'token': token.key,
    })


# ═══════════════════════════════════════════
# ADMINISTRACIÓN (Solo Admin)
# ═══════════════════════════════════════════

class AdminUsuarioViewSet(viewsets.ModelViewSet):
    """CRUD de usuarios (solo Admin)."""
    permission_classes = [IsAuthenticated, EsAdmin]
    queryset = Usuario.objects.select_related('jerarquia', 'jerarquia__tipo_personal', 'dependencia', 'dependencia__ciudad').all()

    def get_serializer_class(self):
        if self.action == 'create':
            return UsuarioCreateSerializer
        if self.action in ('update', 'partial_update'):
            return UsuarioUpdateSerializer
        if self.action == 'retrieve':
            return UsuarioDetailSerializer
        return UsuarioListSerializer

    def destroy(self, request, *args, **kwargs):
        """En lugar de eliminar, desactivar el usuario."""
        usuario = self.get_object()
        if usuario == request.user:
            return Response(
                {'error': 'No puede desactivar su propio usuario.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        usuario.is_active = False
        usuario.save()
        return Response({'message': 'Usuario desactivado correctamente.'})


class AdminCiudadViewSet(viewsets.ModelViewSet):
    """CRUD de ciudades (solo Admin)."""
    permission_classes = [IsAuthenticated, EsAdmin]
    queryset = Ciudad.objects.prefetch_related('dependencias').all()
    serializer_class = CiudadSerializer


class AdminDependenciaViewSet(viewsets.ModelViewSet):
    """CRUD de dependencias (solo Admin)."""
    permission_classes = [IsAuthenticated, EsAdmin]
    queryset = Dependencia.objects.select_related('ciudad').all()
    serializer_class = DependenciaSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        ciudad_id = self.request.query_params.get('ciudad')
        if ciudad_id:
            qs = qs.filter(ciudad_id=ciudad_id)
        return qs


class AdminTipoPersonalViewSet(viewsets.ModelViewSet):
    """CRUD de tipos de personal (solo Admin)."""
    permission_classes = [IsAuthenticated, EsAdmin]
    queryset = TipoPersonal.objects.prefetch_related('jerarquias').all()
    serializer_class = TipoPersonalSerializer


class AdminJerarquiaViewSet(viewsets.ModelViewSet):
    """CRUD de jerarquías (solo Admin)."""
    permission_classes = [IsAuthenticated, EsAdmin]
    queryset = Jerarquia.objects.select_related('tipo_personal').all()
    serializer_class = JerarquiaSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        tipo_id = self.request.query_params.get('tipo_personal')
        if tipo_id:
            qs = qs.filter(tipo_personal_id=tipo_id)
        return qs


# ═══════════════════════════════════════════
# CIRCULARES
# ═══════════════════════════════════════════

class CircularListCreateView(generics.ListCreateAPIView):
    """
    GET: Todos los usuarios pueden ver circulares.
    POST: Solo RRHH puede crear circulares.
    """
    queryset = Circular.objects.select_related('publicado_por').all()
    serializer_class = CircularSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), EsAdminORRHH()]
        return [IsAuthenticated()]


class CircularDeleteView(generics.DestroyAPIView):
    """Solo RRHH o Admin puede eliminar circulares."""
    queryset = Circular.objects.all()
    serializer_class = CircularSerializer
    permission_classes = [IsAuthenticated, EsAdminORRHH]


# ═══════════════════════════════════════════
# LICENCIAS
# ═══════════════════════════════════════════

class LicenciaListCreateView(generics.ListCreateAPIView):
    """
    GET: Personal ve sus licencias, Bienestar ve todas.
    POST: Personal crea nuevas licencias.
    """
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        user = self.request.user
        qs = Licencia.objects.select_related(
            'usuario', 'usuario__jerarquia', 'usuario__dependencia',
            'usuario__dependencia__ciudad'
        )

        if user.rol in ('bienestar', 'admin'):
            # Bienestar y Admin ven todas
            pass
        else:
            # Personal y RRHH ven solo las propias
            qs = qs.filter(usuario=user)

        # Filtros opcionales
        tipo = self.request.query_params.get('tipo')
        estado = self.request.query_params.get('estado')
        usuario_id = self.request.query_params.get('usuario')
        fecha_desde = self.request.query_params.get('fecha_desde')
        fecha_hasta = self.request.query_params.get('fecha_hasta')

        if tipo:
            qs = qs.filter(tipo=tipo)
        if estado:
            qs = qs.filter(estado=estado)
        if usuario_id and user.rol in ('bienestar', 'admin'):
            qs = qs.filter(usuario_id=usuario_id)
        if fecha_desde:
            qs = qs.filter(fecha_inicio__gte=fecha_desde)
        if fecha_hasta:
            qs = qs.filter(fecha_inicio__lte=fecha_hasta)

        return qs

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return LicenciaCreateSerializer
        return LicenciaSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), PuedeCrearLicencia()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        licencia = serializer.save()
        # Enviar emails automáticos
        try:
            enviar_email_nueva_licencia(licencia)
            if licencia.certificado_medico:
                enviar_email_certificado(licencia)
        except Exception as e:
            logger.error(f'Error al enviar email de nueva licencia: {e}')

class LicenciaDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Dueño o Bienestar pueden ver detalle.
    PATCH: Solo Bienestar puede actualizar estado.
    DELETE: Solo Admin puede borrar licencias.
    """
    queryset = Licencia.objects.select_related(
        'usuario', 'usuario__jerarquia', 'usuario__dependencia',
        'usuario__dependencia__ciudad'
    )
    permission_classes = [IsAuthenticated, EsDuenoOBienestar]

    def get_serializer_class(self):
        if self.request.method in ('PATCH', 'PUT'):
            return LicenciaEstadoSerializer
        return LicenciaSerializer

    def get_permissions(self):
        if self.request.method in ('PATCH', 'PUT'):
            return [IsAuthenticated(), EsAdminOBienestar()]
        if self.request.method == 'DELETE':
            return [IsAuthenticated(), EsAdmin()]
        return [IsAuthenticated(), EsDuenoOBienestar()]


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def subir_certificado_view(request, pk):
    """Subir certificado médico a una licencia existente."""
    try:
        licencia = Licencia.objects.get(pk=pk)
    except Licencia.DoesNotExist:
        return Response(
            {'error': 'Licencia no encontrada.'},
            status=status.HTTP_404_NOT_FOUND
        )

    # Solo el dueño puede subir certificado
    if licencia.usuario != request.user and request.user.rol != 'admin':
        return Response(
            {'error': 'No tiene permiso para subir certificado a esta licencia.'},
            status=status.HTTP_403_FORBIDDEN
        )

    archivo = request.FILES.get('certificado')
    if not archivo:
        return Response(
            {'error': 'Debe adjuntar un archivo.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Validar extensión
    extension = archivo.name.split('.')[-1].lower()
    extensiones_permitidas = ('pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx')
    if extension not in extensiones_permitidas:
        return Response(
            {'error': 'Formato no permitido. Use PDF, JPG, PNG, DOC o DOCX.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Validar tipo MIME del contenido real
    mime_permitidos = (
        'application/pdf',
        'image/jpeg', 'image/png',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    )
    if archivo.content_type not in mime_permitidos:
        return Response(
            {'error': 'El tipo de archivo no coincide con la extensión. Verifique el archivo.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    licencia.certificado_medico = archivo
    licencia.save()

    # Enviar email con certificado solo a Bienestar
    try:
        enviar_email_certificado(licencia)
    except Exception as e:
        logger.error(f'Error al enviar email de certificado: {e}')

    return Response({'message': 'Certificado subido correctamente.'})


@api_view(['GET'])
@permission_classes([IsAuthenticated, PuedeVerCertificado])
def descargar_certificado_view(request, pk):
    """Descargar certificado médico (solo Bienestar/Admin)."""
    try:
        licencia = Licencia.objects.get(pk=pk)
    except Licencia.DoesNotExist:
        return Response(
            {'error': 'Licencia no encontrada.'},
            status=status.HTTP_404_NOT_FOUND
        )

    if not licencia.certificado_medico:
        return Response(
            {'error': 'Esta licencia no tiene certificado médico.'},
            status=status.HTTP_404_NOT_FOUND
        )

    from django.http import FileResponse
    return FileResponse(
        licencia.certificado_medico.open('rb'),
        as_attachment=True,
        filename=licencia.certificado_medico.name.split('/')[-1]
    )


# ═══════════════════════════════════════════
# PERSONAL Y REPORTES (Bienestar)
# ═══════════════════════════════════════════

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def personal_list_view(request):
    """Listar personal con resumen de licencias (RRHH y Bienestar)."""
    if request.user.rol not in ('bienestar', 'rrhh', 'admin'):
        return Response(
            {'error': 'No tiene permiso para ver esta información.'},
            status=status.HTTP_403_FORBIDDEN
        )

    usuarios = Usuario.objects.filter(
        rol='personal', is_active=True
    ).select_related(
        'jerarquia', 'jerarquia__tipo_personal',
        'dependencia', 'dependencia__ciudad'
    ).annotate(
        total_licencias=Count('licencias'),
        licencias_activas=Count('licencias', filter=Q(licencias__estado__in=['iniciada', 'en_curso'])),
    )

    # Filtros
    ciudad = request.query_params.get('ciudad')
    dependencia = request.query_params.get('dependencia')
    busqueda = request.query_params.get('busqueda')

    if ciudad:
        usuarios = usuarios.filter(dependencia__ciudad_id=ciudad)
    if dependencia:
        usuarios = usuarios.filter(dependencia_id=dependencia)
    if busqueda:
        usuarios = usuarios.filter(nombre_completo__icontains=busqueda)

    serializer = UsuarioListSerializer(usuarios, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated, EsAdminOBienestar])
def personal_licencias_view(request, pk):
    """Historial de licencias de un usuario específico (Bienestar)."""
    try:
        usuario = Usuario.objects.select_related(
            'jerarquia', 'dependencia', 'dependencia__ciudad'
        ).get(pk=pk)
    except Usuario.DoesNotExist:
        return Response(
            {'error': 'Usuario no encontrado.'},
            status=status.HTTP_404_NOT_FOUND
        )

    licencias = Licencia.objects.filter(
        usuario=usuario
    ).select_related(
        'usuario', 'usuario__jerarquia', 'usuario__dependencia',
        'usuario__dependencia__ciudad'
    ).order_by('-fecha_creacion')

    usuario_data = UsuarioDetailSerializer(usuario).data
    licencias_data = LicenciaSerializer(licencias, many=True).data

    return Response({
        'usuario': usuario_data,
        'licencias': licencias_data,
        'total': licencias.count(),
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated, EsAdminOBienestar])
def reportes_resumen_view(request):
    """Estadísticas generales para el dashboard de Bienestar."""
    from django.utils import timezone
    from django.db.models.functions import TruncMonth
    from datetime import timedelta

    # Filtros de fecha
    fecha_desde = request.query_params.get('fecha_desde')
    fecha_hasta = request.query_params.get('fecha_hasta')

    licencias = Licencia.objects.all()

    if fecha_desde:
        licencias = licencias.filter(fecha_inicio__gte=fecha_desde)
    if fecha_hasta:
        licencias = licencias.filter(fecha_inicio__lte=fecha_hasta)

    # Totales generales
    total = licencias.count()
    por_tipo = licencias.values('tipo').annotate(total=Count('id'))
    por_estado = licencias.values('estado').annotate(total=Count('id'))

    # Por mes (últimos 12 meses)
    hace_12_meses = timezone.now() - timedelta(days=365)
    por_mes = licencias.filter(
        fecha_creacion__gte=hace_12_meses
    ).annotate(
        mes=TruncMonth('fecha_creacion')
    ).values('mes').annotate(
        total=Count('id')
    ).order_by('mes')

    # Por dependencia (top 10)
    por_dependencia = licencias.values(
        'usuario__dependencia__nombre'
    ).annotate(
        total=Count('id')
    ).order_by('-total')[:10]

    # Por ciudad
    por_ciudad = licencias.values(
        'usuario__dependencia__ciudad__nombre'
    ).annotate(
        total=Count('id')
    ).order_by('-total')

    return Response({
        'total': total,
        'por_tipo': list(por_tipo),
        'por_estado': list(por_estado),
        'por_mes': [
            {'mes': item['mes'].strftime('%Y-%m'), 'total': item['total']}
            for item in por_mes
        ],
        'por_dependencia': [
            {'dependencia': item['usuario__dependencia__nombre'] or 'Sin dependencia', 'total': item['total']}
            for item in por_dependencia
        ],
        'por_ciudad': [
            {'ciudad': item['usuario__dependencia__ciudad__nombre'] or 'Sin ciudad', 'total': item['total']}
            for item in por_ciudad
        ],
    })


# ═══════════════════════════════════════════
# DATOS AUXILIARES (para formularios)
# ═══════════════════════════════════════════

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ciudades_list_view(request):
    """Listar ciudades activas."""
    ciudades = Ciudad.objects.filter(activa=True)
    serializer = CiudadSerializer(ciudades, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dependencias_list_view(request):
    """Listar dependencias activas, filtrable por ciudad."""
    dependencias = Dependencia.objects.filter(activa=True).select_related('ciudad')
    ciudad_id = request.query_params.get('ciudad')
    if ciudad_id:
        dependencias = dependencias.filter(ciudad_id=ciudad_id)
    serializer = DependenciaSerializer(dependencias, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def jerarquias_list_view(request):
    """Listar jerarquías agrupadas por tipo de personal."""
    tipos = TipoPersonal.objects.filter(activo=True).prefetch_related(
        'jerarquias'
    )
    serializer = TipoPersonalSerializer(tipos, many=True)
    return Response(serializer.data)
