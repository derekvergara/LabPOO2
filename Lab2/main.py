# main.py

import cadenas_util

print("=== Pruebas de cadenas_util ===")

# Normalización
texto = "  Hola Mundo  "
print("Normalizado:", cadenas_util.normalizar(texto))  # hola mundo

# Validación de email
print("Email válido:", cadenas_util.es_email_valido("usuario@dominio.com"))
print("Email inválido:", cadenas_util.es_email_valido("malformado@dominio"))

# Formatear nombre
print("Nombre formateado:", cadenas_util.formatear_nombre("maria lopez"))

# Iniciales
try:
    print("Iniciales:", cadenas_util.obtener_iniciales("Juan Carlos Pérez"))
    print("Iniciales vacías:", cadenas_util.obtener_iniciales(" "))  # Caso límite
except ValueError as e:
    print("Error:", e)
