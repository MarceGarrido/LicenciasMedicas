import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from licencias.models import Usuario, Ciudad, TipoPersonal

def crear_datos_iniciales():
    ciudades = ['Río Grande', 'Ushuaia', 'Tolhuin']
    for nombre in ciudades:
        Ciudad.objects.get_or_create(nombre=nombre)

    tipos = [
        ('Oficiales', 1),
        ('Suboficiales', 2),
        ('Auxiliares', 3),
    ]
    for nombre, orden in tipos:
        TipoPersonal.objects.get_or_create(nombre=nombre, defaults={'orden': orden})

def crear_admin_default():
    crear_datos_iniciales()
    username = 'admin'
    password = 'adminpassword'
    
    if not Usuario.objects.filter(username=username).exists():
        admin = Usuario.objects.create_user(
            username=username,
            password=password,
            nombre_completo='Administrador Sistema',
            email='admin@ejemplo.com',
            rol='admin',
            is_staff=True,
            is_superuser=True,
        )
        print(f"Admin creado. Usuario: {username}, Contraseña: {password}")
    else:
        print("El usuario admin ya existe.")

if __name__ == '__main__':
    crear_admin_default()
