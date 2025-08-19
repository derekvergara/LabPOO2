# modulo_c.py

# C.1 – Decorador de validación
def requiere_positivos(func):
    def wrapper(*args, **kwargs):
        for arg in args:
            if isinstance(arg, (int, float)) and arg <= 0:
                raise ValueError(f"Todos los argumentos deben ser positivos. Argumento inválido: {arg}")
        return func(*args, **kwargs)
    return wrapper

@requiere_positivos
def calcular_descuento(precio, porcentaje):
    return precio * (1 - porcentaje)

@requiere_positivos
def escala(valor, factor):
    return valor * factor
