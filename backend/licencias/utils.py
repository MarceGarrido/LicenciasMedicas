import io
from django.core.files.uploadedfile import InMemoryUploadedFile
from rest_framework.exceptions import ValidationError
from PIL import Image

def validar_y_convertir_a_pdf(archivo):
    if not archivo:
        return None

    extension = archivo.name.split('.')[-1].lower()
    extensiones_permitidas = ('pdf', 'jpg', 'jpeg', 'png')
    
    if extension not in extensiones_permitidas:
        raise ValidationError('Formato no permitido. Use PDF, JPG o PNG.')

    mime_permitidos = ('application/pdf', 'image/jpeg', 'image/png')
    if archivo.content_type not in mime_permitidos:
        raise ValidationError('El tipo de archivo no coincide con la extensión. Verifique el archivo.')

    # Si ya es PDF, no hacemos nada
    if extension == 'pdf' and archivo.content_type == 'application/pdf':
        return archivo

    # Si es imagen, convertir a PDF
    try:
        img = Image.open(archivo)
        if img.mode != 'RGB':
            img = img.convert('RGB')

        pdf_buffer = io.BytesIO()
        img.save(pdf_buffer, format='PDF', resolution=100.0)
        pdf_buffer.seek(0)
        
        nombre_base = archivo.name.rsplit('.', 1)[0]
        nuevo_nombre = f"{nombre_base}.pdf"
        
        return InMemoryUploadedFile(
            pdf_buffer,
            None,
            nuevo_nombre,
            'application/pdf',
            pdf_buffer.getbuffer().nbytes,
            None
        )
    except Exception as e:
        raise ValidationError(f'Error al convertir la imagen a PDF: {str(e)}')
