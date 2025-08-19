# cadenas_util.py

def normalizar(texto):
    """Convierte el texto a minúsculas y elimina espacios alrededor"""
    return texto.strip().lower()

def es_email_valido(email):
    """Valida si un correo contiene '@' y un punto '.' después del '@'"""
    if '@' in email and '.' in email[email.index('@'):]:
        return True
    return False

def formatear_nombre(nombre):
    """Convierte el nombre a formato capitalizado tipo 'Juan Pérez'"""
    return ' '.join(palabra.capitalize() for palabra in nombre.strip().split())

def obtener_iniciales(nombre):
    """Devuelve las iniciales del nombre"""
    partes = nombre.strip().split()
    if not partes:
        raise ValueError("Nombre vacío o inválido")
    return ''.join(p[0].upper() for p in partes)
