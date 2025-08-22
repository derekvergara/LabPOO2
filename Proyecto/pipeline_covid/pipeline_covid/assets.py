from dagster import asset, AssetCheckResult
import pandas as pd


@asset
def leer_datos():
    df = pd.read_csv("../data/covid.csv", parse_dates=["fecha"])
    return df


@asset
def datos_procesados(leer_datos: pd.DataFrame):
    df = leer_datos.copy()
    df = df.dropna()
    return df


@asset
def metrica_incidencia_7d(datos_procesados: pd.DataFrame):
    incidencia = datos_procesados.groupby("provincia")["nuevos_casos"].rolling(window=7).sum().reset_index()
    incidencia.rename(columns={"nuevos_casos": "incidencia_7d"}, inplace=True)
    return incidencia


@asset
def metrica_factor_crec_7d(metrica_incidencia_7d: pd.DataFrame):
    metrica = metrica_incidencia_7d.copy()
    metrica["factor_crecimiento"] = metrica.groupby("provincia")["incidencia_7d"].pct_change()
    return metrica


@asset
def reporte_excel_covid(datos_procesados: pd.DataFrame):
    ruta = "data/reporte_covid.xlsx"
    datos_procesados.to_excel(ruta, index=False)
    return ruta


# ----------------------------- CHECKS ----------------------------- #

@asset
def check_columnas_clave(leer_datos: pd.DataFrame):
    columnas_esperadas = {"fecha", "provincia", "nuevos_casos"}
    columnas_presentes = set(leer_datos.columns)
    return AssetCheckResult(
        passed=columnas_esperadas.issubset(columnas_presentes),
        metadata={"columnas_presentes": list(columnas_presentes)},
    )


@asset
def check_fecha_no_futura(leer_datos: pd.DataFrame):
    fecha_max = leer_datos["fecha"].max()
    return AssetCheckResult(
        passed=pd.to_datetime(fecha_max) <= pd.Timestamp.today(),
        metadata={"fecha_max": fecha_max.strftime("%Y-%m-%d")},
    )


@asset
def check_unicidad(leer_datos: pd.DataFrame):
    duplicados = leer_datos.duplicated(subset=["fecha", "provincia"]).sum()
    return AssetCheckResult(
        passed=duplicados == 0,
        metadata={"duplicados": duplicados},
    )
