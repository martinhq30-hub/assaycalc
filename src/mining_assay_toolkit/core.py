"""Procesamiento básico de datos de assay geológico (v0)."""

import pandas as pd


REQUIRED_COLUMNS = {"hole_id", "from", "to", "Cu_pct"}


def leer_csv_assay(ruta: str) -> pd.DataFrame:
    """Lee un archivo CSV de assay y devuelve un DataFrame."""
    df = pd.read_csv(
        ruta,
        sep=None,
        engine="python",
        encoding="utf-8-sig"
    )

    columnas_faltantes = REQUIRED_COLUMNS - set(df.columns)

    if columnas_faltantes:
        raise ValueError(f"Faltan columnas requeridas: {columnas_faltantes}")

    return df


def validar_assay(df: pd.DataFrame) -> None:
    """Valida reglas mínimas de integridad sobre los datos de assay."""
    if df["hole_id"].isna().any():
        raise ValueError("Existen filas con hole_id vacío.")

    if (df["from"] >= df["to"]).any():
        raise ValueError("Existen intervalos donde 'from' >= 'to'.")

    if (df["Cu_pct"] < 0).any():
        raise ValueError("Existen leyes de Cu_pct negativas.")

    for hole_id, grupo in df.groupby("hole_id"):
        grupo_ordenado = grupo.sort_values("from")
        solapes = (
            grupo_ordenado["from"].iloc[1:].to_numpy()
            < grupo_ordenado["to"].iloc[:-1].to_numpy()
        )
        if solapes.any():
            raise ValueError(f"Intervalos solapados en el sondaje {hole_id}.")


def componer_assay(df: pd.DataFrame, longitud_composito: float) -> pd.DataFrame:
    """Genera compósitos de longitud fija ponderando la ley por longitud del intervalo."""
    resultados = []

    for hole_id, grupo in df.groupby("hole_id"):
        grupo = grupo.sort_values("from").reset_index(drop=True)
        profundidad_max = grupo["to"].max()
        inicio = 0.0

        while inicio < profundidad_max:
            fin = inicio + longitud_composito
            interseccion = grupo[(grupo["from"] < fin) & (grupo["to"] > inicio)]

            if not interseccion.empty:
                largos = (
                    interseccion["to"].clip(upper=fin)
                    - interseccion["from"].clip(lower=inicio)
                )
                ley_ponderada = (interseccion["Cu_pct"] * largos).sum() / largos.sum()

                resultados.append({
                    "hole_id": hole_id,
                    "from": inicio,
                    "to": fin,
                    "Cu_pct": round(ley_ponderada, 3),
                })

            inicio = fin

    return pd.DataFrame(resultados)


def guardar_csv(df: pd.DataFrame, ruta: str) -> None:
    """Guarda un DataFrame como archivo CSV."""
    df.to_csv(ruta, index=False)