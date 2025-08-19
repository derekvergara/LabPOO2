# main.py

from src.operaciones import sumar, dividir

print("Suma:", sumar(5, 7))
print("División válida:", dividir(10.0, 2.0))
print("División por cero:", dividir(5.0, 0.0))  # Debe retornar None (caso mal diseñado)
