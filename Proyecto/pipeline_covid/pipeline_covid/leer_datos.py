import pandas as pd
from dagster import asset
from pathlib import Path
import os

### ASSET 1: LECTURA DE DATOS

@asset
def leer_datos() -> pd.DataFrame:
    ruta_archivo = Path(__file__).resolve().parents[1] / "data" / "compact.csv"
    df = pd.read_csv(ruta_archivo)
    print("Columnas disponibles en el CSV:", df.columns.tolist())

    # Renombrar 'country' a 'location' para que el resto del pipeline funcione
    df = df.rename(columns={"country": "location"})

    columnas = ['location', 'date', 'new_cases', 'people_vaccinated', 'population']
    df = df[columnas]
    df['date'] = pd.to_datetime(df['date'])
    return df

### ASSET 2: DATOS PROCESADOS
@asset
def datos_procesados(leer_datos: pd.DataFrame) -> pd.DataFrame:
    df = leer_datos.copy()

    # Eliminar nulos
    df = df.dropna(subset=["new_cases", "people_vaccinated"])

    # Eliminar duplicados
    df = df.drop_duplicates(subset=["location", "date"])

    # Filtrar solo Ecuador y otro país
    paises = ["Ecuador", "Peru"]  # Puedes cambiar Peru por otro
    df = df[df["location"].isin(paises)]

    # Devolver solo columnas esenciales
    columnas = ['location', 'date', 'new_cases', 'people_vaccinated', 'population']
    return df[columnas]


### ASSET 3: MÉTRICA INCIDENCIA 7D
@asset
def metrica_incidencia_7d(datos_procesados: pd.DataFrame) -> pd.DataFrame:
    df = datos_procesados.copy()
    df = df.sort_values(by=["location", "date"])

    df["incidencia_diaria"] = (df["new_cases"] / df["population"]) * 100000
    df["incidencia_7d"] = df.groupby("location")["incidencia_diaria"].transform(lambda x: x.rolling(7, min_periods=1).mean())

    return df[["date", "location", "incidencia_7d"]]


### ASSET 4: MÉTRICA FACTOR CRECIMIENTO 7D
@asset
def metrica_factor_crec_7d(datos_procesados: pd.DataFrame) -> pd.DataFrame:
    df = datos_procesados.copy()
    df = df.sort_values(by=["location", "date"])

    df["semana"] = df["date"].dt.to_period("W").apply(lambda r: r.end_time)

    resumen = df.groupby(["location", "semana"]).agg({"new_cases": "sum"}).reset_index()
    resumen["casos_prev"] = resumen.groupby("location")["new_cases"].shift(1)
    resumen["factor_crec_7d"] = resumen["new_cases"] / resumen["casos_prev"]

    return resumen.rename(columns={"semana": "semana_fin", "new_cases": "casos_semana"})[["semana_fin", "location", "casos_semana", "factor_crec_7d"]]


### ASSET 5: REPORTE FINAL EN EXCEL
@asset
def reporte_excel_covid(metrica_incidencia_7d: pd.DataFrame, metrica_factor_crec_7d: pd.DataFrame, datos_procesados: pd.DataFrame) -> None:
    output_dir = Path(__file__).resolve().parents[1] / "outputs"
    os.makedirs(output_dir, exist_ok=True)  # ⬅️ Crear la carpeta si no existe
    ruta_excel = output_dir / "reporte_covid_final.xlsx"

    with pd.ExcelWriter(ruta_excel) as writer:
        datos_procesados.to_excel(writer, index=False, sheet_name="Datos Procesados")
        metrica_incidencia_7d.to_excel(writer, index=False, sheet_name="Incidencia 7d")
        metrica_factor_crec_7d.to_excel(writer, index=False, sheet_name="Factor Crec 7d")

    print(f"Reporte generado en: {ruta_excel}")