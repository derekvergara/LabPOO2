import duckdb

# 1. Consulta directa sobre el CSV (sin pandas)
print("\n--- Conteo desde DuckDB ---")
result = duckdb.sql("""
    SELECT categoria, COUNT(*) as total_productos
    FROM 'data/productos.csv'
    WHERE precio > 100
    GROUP BY categoria
""")
print(result)

# 2. Análisis similar al de pandas
query = """
  SELECT 
    categoria,
    AVG(precio) AS precio_promedio,
    SUM(COALESCE(stock, 0)) AS stock_total,
    SUM(precio * COALESCE(stock, 0)) AS valor_total
FROM 'data/productos.csv'
WHERE precio > 100
GROUP BY categoria
"""

# 3. Exportar a CSV
duckdb.sql(f"""
    COPY ({query}) TO 'resumen/duckdb_resumen.csv' (HEADER, DELIMITER ',')
""")

print("\n--- Exportación DuckDB completa ---")
