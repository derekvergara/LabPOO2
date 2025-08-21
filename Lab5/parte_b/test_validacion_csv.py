# parte_b/test_validacion_csv.py

import csv
import pytest

CSV_PATH = "parte_b/productos.csv"

def leer_csv():
    with open(CSV_PATH, newline='', encoding='utf-8') as archivo:
        return list(csv.DictReader(archivo))

def test_columnas_obligatorias():
    filas = leer_csv()
    columnas = filas[0].keys()
    assert "id" in columnas
    assert "nombre" in columnas
    assert "precio" in columnas
    assert "stock" in columnas

def test_tipos_de_datos():
    filas = leer_csv()
    for fila in filas:
        assert fila["id"].isdigit()
        assert isinstance(fila["nombre"], str)
        assert fila["precio"].lstrip('-').replace('.', '', 1).isdigit()
        assert fila["stock"].isdigit()

def test_valores_no_negativos():
    filas = leer_csv()
    for fila in filas:
        precio = float(fila["precio"])
        stock = int(fila["stock"])
        assert stock >= 0
        assert precio >= 0, f"Precio negativo detectado: {precio}"

def test_ids_unicos():
    filas = leer_csv()
    ids = [fila["id"] for fila in filas]
    assert len(ids) == len(set(ids)), "Hay IDs duplicados"
