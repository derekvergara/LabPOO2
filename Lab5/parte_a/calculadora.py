# parte_a/calculadora.py

def suma(a: float, b: float) -> float:
    return a + b

def dividir(a: float, b: float) -> float:
    if b == 0:
        raise ValueError("No se puede dividir por cero")
    return a / b

def es_par(numero: int) -> bool:
    return numero % 2 == 0
