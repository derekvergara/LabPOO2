from dagster import Definitions, load_assets_from_modules
from . import assets  # todos tus assets y checks están en pipeline_covid/assets.py

defs = Definitions(
    assets=load_assets_from_modules([assets]),
    asset_checks=[assets.chequeos_entrada],  # solo el check que SÍ existe
)
