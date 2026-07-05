"""Procesamiento de datos de assay geológico, con soporte multi-elemento."""

from collections.abc import Sequence

import pandas as pd


COLUMNAS_BASE = {"hole_id", "from", "to"}


def leer_csv_assay(ruta: str, columnas_ley: Sequence[str]) -> pd.DataFrame:
    """Lee un archivo CSV de assay y devuelve un DataFrame.

    Args:
        ruta: Ruta del archivo CSV.
        columnas_ley: Nombres de las columnas de ley a exigir/procesar
            (ej. ["Cu_pct", "Au_gpt", "Ag_gpt"]).
    """
    df = pd.read_csv(ruta)
    columnas_requeridas = COLUMNAS_BASE | set(columnas_ley)
    columnas_faltantes = columnas_requeridas - set(df.columns)
    if columnas_faltantes:
        raise ValueError(f"Faltan columnas requeridas: {columnas_faltantes}")
    return df


def validar_assay(df: pd.DataFrame, columnas_ley: Sequence[str]) -> None:
    """Valida reglas mínimas de integridad sobre los datos de assay."""
    if df["hole_id"].isna().any():
        raise ValueError("Existen filas con hole_id vacío.")

    if (df["from"] >= df["to"]).any():
        raise ValueError("Existen intervalos donde 'from' >= 'to'.")

    for columna in columnas_ley:
        if (df[columna] < 0).any():
            raise ValueError(f"Existen leyes negativas en la columna '{columna}'.")

    for hole_id, grupo in df.groupby("hole_id"):
        grupo_ordenado = grupo.sort_values("from")
        solapes = (
            grupo_ordenado["from"].iloc[1:].to_numpy()
            < grupo_ordenado["to"].iloc[:-1].to_numpy()
        )
        if solapes.any():
            raise ValueError(f"Intervalos solapados en el sondaje {hole_id}.")


def componer_assay(
    df: pd.DataFrame,
    longitud_composito: float,
    columnas_ley: Sequence[str],
) -> pd.DataFrame:
    """Genera compósitos de longitud fija ponderando cada ley por longitud."""
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
                fila = {"hole_id": hole_id, "from": inicio, "to": fin}

                for columna in columnas_ley:
                    ley_ponderada = (interseccion[columna] * largos).sum() / largos.sum()
                    fila[columna] = round(ley_ponderada, 3)

                resultados.append(fila)

            inicio = fin

    return pd.DataFrame(resultados)


def guardar_csv(
    df: pd.DataFrame,
    ruta: str,
    separador: str = ",",
    codificacion: str = "utf-8-sig",
) -> None:
    """Guarda un DataFrame como archivo CSV.

    Args:
        df: DataFrame a guardar.
        ruta: Ruta destino del archivo CSV.
        separador: Carácter separador de columnas. Usa "," (estándar
            internacional, por defecto) o ";" si el archivo se abrirá
            directamente con doble clic en Excel configurado en español.
        codificacion: Codificación del archivo. "utf-8-sig" (por defecto)
            incluye un BOM que hace que Excel detecte UTF-8 correctamente
            y evita que tildes o "ñ" se vean corruptas.
    """
    df.to_csv(ruta, index=False, sep=separador, encoding=codificacion)