import pandas as pd

# 1. Lectura
df = pd.read_csv("data/productos.csv")
print("\n--- Exploración ---")
print(df.head())
print(df.info())
print("Nulos por columna:\n", df.isna().sum())

# 2. Limpieza y columnas derivadas
df["fecha"] = pd.to_datetime(df["fecha"])  # convertir a datetime
df["valor_total"] = df["precio"] * df["stock"]  # nueva columna
df["categoria"] = df["categoria"].str.capitalize()  # normaliza texto
df["stock"] = df["stock"].fillna(0)  # imputar nulos con 0

# 3. Agrupación y filtro
df_filtrado = df[df["precio"] > 100]
agrupado = df_filtrado.groupby("categoria").agg({
    "precio": "mean",
    "stock": "sum",
    "valor_total": "sum"
}).reset_index()

print("\n--- Resumen por categoría (pandas) ---")
print(agrupado)

# 4. Exportar
agrupado.to_csv("resumen/pandas_resumen.csv", index=False)
