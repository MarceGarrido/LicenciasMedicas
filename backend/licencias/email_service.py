"""
Servicio de envío de emails automáticos.
"""
import logging
from django.core.mail import EmailMessage
from django.conf import settings

logger = logging.getLogger(__name__)


def enviar_email_nueva_licencia(licencia):
    """
    Envía email al crear una nueva licencia:
    - Al email de la dependencia del usuario
    - Al email de Bienestar de la ciudad correspondiente
    """
    usuario = licencia.usuario
    tipo_display = licencia.get_tipo_display()

    asunto = f'Nueva Licencia: {usuario.nombre_completo} - Legajo {usuario.legajo or "Sin Legajo"}'

    cuerpo = f"""
Se ha iniciado una nueva licencia en el sistema.

DATOS DE LA LICENCIA:
─────────────────────
Personal: {usuario.nombre_completo}
DNI: {usuario.dni or 'No registrado'}
Legajo: {usuario.legajo or 'No registrado'}
Jerarquía: {usuario.jerarquia.nombre if usuario.jerarquia else 'No asignada'}
Dependencia: {usuario.dependencia.nombre if usuario.dependencia else 'No asignada'}

Domicilio durante licencia: {licencia.domicilio or 'No registrado'}
Email de contacto: {licencia.email_contacto or 'No registrado'}
¿Es caso de internación?: {'Sí' if licencia.es_internacion else 'No'}
¿Cursa licencia anual?: {'Sí' if licencia.cursando_licencia_anual else 'No'}

Tipo de Licencia: {tipo_display}
Fecha de Inicio: {licencia.fecha_inicio.strftime('%d/%m/%Y')}
Fecha de Fin: {licencia.fecha_fin.strftime('%d/%m/%Y')}
Días: {licencia.dias_licencia}
Observaciones: {licencia.observaciones or 'Sin observaciones'}

Estado: {licencia.get_estado_display()}
Fecha de solicitud: {licencia.fecha_creacion.strftime('%d/%m/%Y %H:%M')}

─────────────────────
Este es un mensaje automático del Sistema de Licencias Médicas.
"""

    destinatarios = []

    # Email de la dependencia
    if usuario.dependencia and usuario.dependencia.email:
        destinatarios.append(usuario.dependencia.email)

    # Email de Bienestar de la ciudad
    if usuario.dependencia and usuario.dependencia.ciudad and usuario.dependencia.ciudad.email_bienestar:
        destinatarios.append(usuario.dependencia.ciudad.email_bienestar)

    if not destinatarios:
        logger.warning(
            f'No hay destinatarios para la licencia {licencia.id} '
            f'del usuario {usuario.nombre_completo}. '
            f'Verificar emails de dependencia y bienestar.'
        )
        return False

    try:
        email = EmailMessage(
            subject=asunto,
            body=cuerpo,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=destinatarios,
        )
        email.send(fail_silently=False)
        logger.info(
            f'Email de nueva licencia enviado a: {", ".join(destinatarios)}'
        )
        return True
    except Exception as e:
        logger.error(f'Error al enviar email de licencia: {e}')
        return False


def enviar_email_certificado(licencia):
    """
    Envía email con certificado médico adjunto SOLO a Bienestar de la ciudad.
    """
    usuario = licencia.usuario

    if not licencia.certificado_medico:
        logger.warning(f'Licencia {licencia.id} no tiene certificado médico adjunto.')
        return False

    # Solo al email de Bienestar de la ciudad
    email_bienestar = None
    if usuario.dependencia and usuario.dependencia.ciudad:
        email_bienestar = usuario.dependencia.ciudad.email_bienestar

    if not email_bienestar:
        logger.warning(
            f'No hay email de Bienestar configurado para la ciudad del usuario '
            f'{usuario.nombre_completo}.'
        )
        return False

    tipo_display = licencia.get_tipo_display()
    asunto = f'Certificado Médico: {usuario.nombre_completo} - Legajo {usuario.legajo or "Sin Legajo"}'

    cuerpo = f"""
Se ha cargado un certificado médico en el sistema.

DATOS:
─────────────────────
Personal: {usuario.nombre_completo}
DNI: {usuario.dni or 'No registrado'}
Legajo: {usuario.legajo or 'No registrado'}
Jerarquía: {usuario.jerarquia.nombre if usuario.jerarquia else 'No asignada'}
Dependencia: {usuario.dependencia.nombre if usuario.dependencia else 'No asignada'}
Tipo de Licencia: {tipo_display}
Fecha de Inicio: {licencia.fecha_inicio.strftime('%d/%m/%Y')}
Fecha de Fin: {licencia.fecha_fin.strftime('%d/%m/%Y')}
Días: {licencia.dias_licencia}

Se adjunta el certificado médico.

─────────────────────
Este es un mensaje automático del Sistema de Licencias Médicas.
"""

    try:
        email = EmailMessage(
            subject=asunto,
            body=cuerpo,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email_bienestar],
        )
        # Adjuntar el certificado
        licencia.certificado_medico.open()
        file_name = licencia.certificado_medico.name.split('/')[-1]
        file_content = licencia.certificado_medico.read()
        licencia.certificado_medico.close()
        
        email.attach(file_name, file_content)
        email.send(fail_silently=False)
        logger.info(f'Email con certificado enviado a Bienestar: {email_bienestar}')
        return True
    except Exception as e:
        logger.error(f'Error al enviar email de certificado: {e}')
        return False
