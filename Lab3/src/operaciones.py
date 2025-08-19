# src/operaciones.py

from typing import Optional

def sumar(a: int, b: int) -> int:
    return a + b

def dividir(a: float, b: float) -> Optional[float]:
    if b == 0:
        return None
    return a / b
