# main.py

from modulo_a import ejecutar, descuento10, descuento25
from modulo_b import parsear_enteros, calcular_total, CantidadInvalida
from modulo_c import calcular_descuento, escala

# --- Módulo A ---
print("=== Módulo A ===")
print(ejecutar("saludar", "Ana"))
print(ejecutar("aplaudir", "Carlos"))
# print(ejecutar("bailar", "Luis"))  # Descomenta para ver error

print("Descuento 10% de 100:", descuento10(100))
print("Descuento 25% de 80:", descuento25(80))

# --- Módulo B ---
print("\n=== Módulo B ===")
entradas = ["10", "x", "5"]
valores, errores = parsear_enteros(entradas)
print("Valores válidos:", valores)
print("Errores:", errores)

try:
    print("Total compra:", calcular_total(10, 3))
    # print(calcular_total(10, 0))  # Descomenta para probar error personalizado
except CantidadInvalida as e:
    print("CantidadInvalida:", e)
except ValueError as e:
    print("ValueError:", e)

# --- Módulo C ---
print("\n=== Módulo C ===")
try:
    print("Calcular descuento:", calcular_descuento(100, 0.2))
    print("Escala:", escala(5, 3))
    # print(calcular_descuento(-1, 0.2))  # Descomenta para ver error por argumento negativo
except ValueError as e:
    print("Error en decorador:", e)
