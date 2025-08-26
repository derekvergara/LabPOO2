import csv

# Ruta relativa al archivo CSV
CSV_PATH = 'parte_b/productos.csv'

# Validación simple: precio > 0 y stock >= 0
def validar_producto(producto):
    try:
        precio = float(producto['precio'])
        stock = int(producto['stock'])
        return precio > 0 and stock >= 0
    except ValueError:
        return False

def cargar_productos(path):
    productos_validos = []
    with open(path, newline='', encoding='utf-8') as csvfile:
        lector = csv.DictReader(csvfile)
        for fila in lector:
            if validar_producto(fila):
                productos_validos.append(fila)
    return productos_validos

if __name__ == '__main__':
    productos = cargar_productos(CSV_PATH)
    print("📦 Productos con stock válido:")
    for p in productos:
        print(f"- {p['nombre']}: ${p['precio']} ({p['stock']} unidades)")
