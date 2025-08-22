from dagster import Definitions, load_assets_from_modules

from pipeline_covid import assets

all_assets = load_assets_from_modules([assets])

from .leer_datos import (
    leer_datos,
    datos_procesados,
    metrica_incidencia_7d,
    metrica_factor_crec_7d,
    reporte_excel_covid
)

defs = Definitions(
    assets=[
        leer_datos,
        datos_procesados,
        metrica_incidencia_7d,
        metrica_factor_crec_7d,
        reporte_excel_covid
    ]
)