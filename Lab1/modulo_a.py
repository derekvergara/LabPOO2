# modulo_a.py

# A.1 – Funciones como valores
def saludar(nombre):
    return f"Hola, {nombre}"

def despedir(nombre):
    return f"Adiós, {nombre}"

def aplaudir(nombre):
    return f"Bien hecho, {nombre}!"

acciones = {
    "saludar": saludar,
    "despedir": despedir,
    "aplaudir": aplaudir
}

def ejecutar(accion, *args, **kwargs):
    if accion in acciones:
        return acciones[accion](*args, **kwargs)
    else:
        raise ValueError(f"Acción no reconocida: '{accion}'")

# A.2 – Funciones internas y closures
def crear_descuento(porcentaje):
    def aplicar_descuento(precio):
        return precio * (1 - porcentaje)
    return aplicar_descuento

descuento10 = crear_descuento(0.10)
descuento25 = crear_descuento(0.25)
