# modulo_b.py

# B.1 – Validación de entrada
def parsear_enteros(entradas):
    valores = []
    errores = []
    for e in entradas:
        try:
            valores.append(int(e))
        except ValueError:
            errores.append(f"'{e}' no es un número válido")
    return valores, errores

# B.2 – Excepciones personalizadas
class CantidadInvalida(Exception):
    pass

def calcular_total(precio_unitario, cantidad):
    if cantidad <= 0:
        raise CantidadInvalida("La cantidad debe ser mayor a cero.")
    if precio_unitario < 0:
        raise ValueError("El precio unitario no puede ser negativo.")
    return precio_unitario * cantidad
