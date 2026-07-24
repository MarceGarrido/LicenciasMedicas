"""
Script para crear el usuario administrador inicial.
Uso: python crear_admin.py
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from licencias.models import Usuario, Ciudad, TipoPersonal


def crear_datos_iniciales():
    """Crea ciudades y tipos de personal iniciales."""
    # Ciudades
    ciudades = ['Río Grande', 'Ushuaia', 'Tolhuin']
    for nombre in ciudades:
        ciudad, created = Ciudad.objects.get_or_create(nombre=nombre)
        if created:
            print(f'  ✓ Ciudad creada: {nombre}')
        else:
            print(f'  → Ciudad ya existe: {nombre}')

    # Tipos de personal
    tipos = [
        ('Oficiales', 1),
        ('Suboficiales', 2),
        ('Auxiliares', 3),
    ]
    for nombre, orden in tipos:
        tipo, created = TipoPersonal.objects.get_or_create(
            nombre=nombre,
            defaults={'orden': orden}
        )
        if created:
            print(f'  ✓ Tipo de personal creado: {nombre}')
        else:
            print(f'  → Tipo de personal ya existe: {nombre}')


def crear_admin():
    """Crea el usuario administrador."""
    print('\n' + '═' * 50)
    print('  CREAR USUARIO ADMINISTRADOR')
    print('═' * 50 + '\n')

    # Primero crear datos iniciales
    print('Creando datos iniciales...\n')
    crear_datos_iniciales()

    print('\n' + '─' * 50)
    print('Datos del administrador:\n')

    username = input('  Usuario: ').strip()
    if not username:
        print('  ✗ El usuario no puede estar vacío.')
        return

    if Usuario.objects.filter(username=username).exists():
        print(f'  ✗ El usuario "{username}" ya existe.')
        return

    nombre_completo = input('  Nombre completo: ').strip()
    email = input('  Email: ').strip()
    password = input('  Contraseña: ').strip()

    if not password:
        print('  ✗ La contraseña no puede estar vacía.')
        return

    admin = Usuario.objects.create_user(
        username=username,
        password=password,
        nombre_completo=nombre_completo or username,
        email=email,
        rol='admin',
        is_staff=True,
        is_superuser=True,
    )

    print(f'\n  ✓ Administrador creado exitosamente:')
    print(f'    Usuario: {admin.username}')
    print(f'    Nombre: {admin.nombre_completo}')
    print(f'    Rol: Administrador')
    print(f'\n' + '═' * 50)


if __name__ == '__main__':
    crear_admin()
