# pipeline_covid/assets.py
from __future__ import annotations

from pathlib import Path
import os
import io
import requests
import pandas as pd
from dagster import (
    asset,
    asset_check,
    AssetCheckResult,
    MetadataValue,
)

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
OUTPUTS_DIR = ROOT / "outputs"
CANONICAL_URL = "https://catalog.ourworldindata.org/garden/covid/latest/compact/compact.csv"

# ---------------------------
# Utilidades
# ---------------------------
def _asegurar_outputs() -> Path:
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    return OUTPUTS_DIR

def _perfilado_basico_df(df: pd.DataFrame) -> pd.DataFrame:
    filas = []
    total = len(df)
    for col in df.columns:
        s = df[col]
        n_nulos = int(s.isna().sum())
        pct_nulos = round((n_nulos / total) * 100, 2) if total else 0.0
        n_unicos = int(s.nunique(dropna=True))
        ejemplo = None if s.dropna().empty else s.dropna().iloc[0]
        fila = {
            "columna": col,
            "tipo": str(s.dtype),
            "n_nulos": n_nulos,
            "pct_nulos": pct_nulos,
            "n_unicos": n_unicos,
            "ejemplo": ejemplo,
            "min": None, "max": None, "media": None, "mediana": None, "std": None,
            "top_valor": None, "top_freq": None,
        }
        if pd.api.types.is_numeric_dtype(s) and not s.dropna().empty:
            fila.update({
                "min": float(s.min()),
                "max": float(s.max()),
                "media": float(s.mean()),
                "mediana": float(s.median()),
                "std": float(s.std()),
            })
        else:
            vc = s.value_counts(dropna=True)
            if not vc.empty:
                fila.update({"top_valor": vc.index[0], "top_freq": int(vc.iloc[0])})
        filas.append(fila)
    return pd.DataFrame(filas)

# ===========================
# ASSET 1: LECTURA DE DATOS
# ===========================
@asset
def leer_datos() -> pd.DataFrame:
    """
    Intenta descargar el CSV canónico; si falla, usa data/compact.csv local.
    Normaliza columnas (country->location, code->iso_code).
    NO transforma datos: solo lectura + normalización de nombres.
    """
    df: pd.DataFrame
    try:
        resp = requests.get(CANONICAL_URL, timeout=60)
        resp.raise_for_status()
        df = pd.read_csv(io.BytesIO(resp.content), low_memory=False)
        print("CSV descargado desde URL canónica.")
    except Exception as e:
        ruta_local = DATA_DIR / "compact.csv"
        print(f"No se pudo descargar. Usando local: {ruta_local} | Motivo: {e}")
        df = pd.read_csv(ruta_local, low_memory=False)

    # Normalizar nombres segun tu fuente
    rename_map = {}
    if "country" in df.columns and "location" not in df.columns:
        rename_map["country"] = "location"
    if "code" in df.columns and "iso_code" not in df.columns:
        rename_map["code"] = "iso_code"
    if rename_map:
        df = df.rename(columns=rename_map)

    print("Columnas disponibles (normalizadas):", df.columns.tolist())

    # Deja todo lo demás intacto (sin filtros/limpiezas aqui)
    return df


# ======================================
# ASSET CHECK: Chequeos de entrada (UI)
# ======================================
@asset_check(asset=leer_datos)
def chequeos_entrada(context, leer_datos: pd.DataFrame) -> AssetCheckResult:
    """
    Valida esquema y fechas. Permite new_cases negativos (los reporta).
    Muestra resumen en la UI de Dagster.
    """
    df = leer_datos
    hoy = pd.Timestamp.utcnow().normalize()

    reglas = []

    # max(date) ≤ hoy
    fechas_ok = True
    if "date" in df.columns:
        try:
            max_date = pd.to_datetime(df["date"]).max()
            fechas_ok = (max_date <= hoy)
        except Exception:
            fechas_ok = False
    reglas.append(("max(date) ≤ hoy", fechas_ok))

    # columnas clave presentes
    claves_ok = all(c in df.columns for c in ["location", "date", "population"])
    reglas.append(("columnas clave presentes (location,date,population)", claves_ok))

    # población > 0
    pop_ok = "population" in df.columns and (pd.to_numeric(df["population"], errors="coerce").fillna(0) > 0).all()
    reglas.append(("population > 0", pop_ok))

    # unicidad (location,date)
    duplicados = 0
    unicidad_ok = True
    if all(c in df.columns for c in ["location", "date"]):
        duplicados = int(df.duplicated(subset=["location", "date"]).sum())
        unicidad_ok = (duplicados == 0)
    reglas.append((f"unicidad (location,date) [duplicados={duplicados}]", unicidad_ok))

    # new_cases: permitir negativos, pero contarlos
    neg_count = None
    new_cases_ok = True
    if "new_cases" in df.columns:
        series_nc = pd.to_numeric(df["new_cases"], errors="coerce")
        neg_count = int((series_nc.fillna(0) < 0).sum())
        new_cases_ok = True  # permitidos (documentado por la consigna)
    reglas.append((f"new_cases (negativos permitidos, count={neg_count})", new_cases_ok))

    tabla = pd.DataFrame(reglas, columns=["nombre_regla", "estado"])
    passed = bool(tabla["estado"].all())

    return AssetCheckResult(
        passed=passed,
        metadata={
            "resumen": MetadataValue.md(tabla.to_markdown(index=False)),
            "total_filas": len(df),
        },
    )


# =====================================
# ASSET: Perfilado inicial (CSV ligero)
# =====================================
@asset
def perfilado_inicial(leer_datos: pd.DataFrame) -> str:
    """
    Genera outputs/tabla_perfilado.csv con perfilado básico.
    """
    _asegurar_outputs()
    tabla = _perfilado_basico_df(leer_datos)
    destino = OUTPUTS_DIR / "tabla_perfilado.csv"
    tabla.to_csv(destino, index=False)
    print(f" Perfilado guardado en: {destino}")
    return str(destino)


# ===========================
# ASSET 2: DATOS PROCESADOS
# ===========================
@asset
def datos_procesados(leer_datos: pd.DataFrame) -> pd.DataFrame:
    df = leer_datos.copy()

    # Tipos
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")

    for c in ["new_cases", "people_vaccinated", "population"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    # Eliminar nulos en columnas clave de métricas (como pide la rúbrica)
    cols_req = [c for c in ["new_cases", "people_vaccinated"] if c in df.columns]
    if cols_req:
        df = df.dropna(subset=cols_req)

    # Eliminar duplicados (location,date)
    if all(c in df.columns for c in ["location", "date"]):
        df = df.drop_duplicates(subset=["location", "date"])

    # Filtrar Ecuador + país comparativo
    paises = ["Ecuador", "Peru"]  # cambia Peru si quieres
    if "location" in df.columns:
        df = df[df["location"].isin(paises)]

    # Devolver columnas esenciales si existen
    columnas = [c for c in ['location', 'date', 'new_cases', 'people_vaccinated', 'population'] if c in df.columns]
    return df[columnas].copy()


# ==========================================
# ASSET 3: MÉTRICA INCIDENCIA 7D por 100k
# ==========================================
@asset
def metrica_incidencia_7d(datos_procesados: pd.DataFrame) -> pd.DataFrame:
    df = datos_procesados.copy().sort_values(by=["location", "date"])
    df["incidencia_diaria"] = (df["new_cases"] / df["population"]) * 100_000
    df["incidencia_7d"] = df.groupby("location")["incidencia_diaria"].transform(
        lambda x: x.rolling(7, min_periods=1).mean()
    )
    return df[["date", "location", "incidencia_7d"]]


# ==========================================
# ASSET 4: MÉTRICA FACTOR CRECIMIENTO 7D
# ==========================================
@asset
def metrica_factor_crec_7d(datos_procesados: pd.DataFrame) -> pd.DataFrame:
    df = datos_procesados.copy().sort_values(by=["location", "date"])
    # semana fin usando periodo semanal (fin de semana)
    df["semana_fin"] = df["date"].dt.to_period("W").apply(lambda r: r.end_time)

    resumen = df.groupby(["location", "semana_fin"], as_index=False).agg({"new_cases": "sum"})
    resumen["casos_prev"] = resumen.groupby("location")["new_cases"].shift(1)
    resumen["factor_crec_7d"] = resumen["new_cases"] / resumen["casos_prev"].replace(0, pd.NA)

    return resumen.rename(columns={"location": "location", "new_cases": "casos_semana"})[
        ["semana_fin", "location", "casos_semana", "factor_crec_7d"]
    ]


# ======================================
# ASSET 5: REPORTE FINAL EN EXCEL
# ======================================
@asset
def reporte_excel_covid(
    metrica_incidencia_7d: pd.DataFrame,
    metrica_factor_crec_7d: pd.DataFrame,
    datos_procesados: pd.DataFrame,
) -> None:
    _asegurar_outputs()
    ruta_excel = OUTPUTS_DIR / "reporte_covid_final.xlsx"
    with pd.ExcelWriter(ruta_excel) as writer:
        datos_procesados.to_excel(writer, index=False, sheet_name="Datos Procesados")
        metrica_incidencia_7d.to_excel(writer, index=False, sheet_name="Incidencia 7d")
        metrica_factor_crec_7d.to_excel(writer, index=False, sheet_name="Factor Crec 7d")
    print(f" Reporte generado en: {ruta_excel}")

