# pipeline_covid/perfilado.py
from __future__ import annotations
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
OUTPUTS_DIR = ROOT / "outputs"

def asegurar_outputs() -> Path:
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    return OUTPUTS_DIR

def perfilado_basico_df(df: pd.DataFrame) -> pd.DataFrame:
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
        if pd.api.types.is_numeric_dtype(s):
            if not s.dropna().empty:
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

def guardar_perfilado_csv(df: pd.DataFrame, nombre: str = "tabla_perfilado.csv") -> Path:
    outdir = asegurar_outputs()
    tabla = perfilado_basico_df(df)
    destino = outdir / nombre
    tabla.to_csv(destino, index=False)
    return destino
