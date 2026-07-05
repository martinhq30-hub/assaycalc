"""Tests para assaycalc.core"""

import pandas as pd
import pytest

from assaycalc.core import (
    leer_csv_assay,
    validar_assay,
    componer_assay,
    guardar_csv,
)


# ---------- Fixtures ----------

@pytest.fixture
def df_valido():
    return pd.DataFrame({
        "hole_id": ["DDH-01", "DDH-01", "DDH-01"],
        "from": [0.0, 2.0, 4.0],
        "to": [2.0, 4.0, 6.0],
        "Cu_pct": [0.5, 1.0, 0.3],
    })


# ---------- Tests: leer_csv_assay ----------

def test_leer_csv_assay_lee_correctamente(tmp_path, df_valido):
    ruta = tmp_path / "assay.csv"
    df_valido.to_csv(ruta, index=False)

    resultado = leer_csv_assay(str(ruta), columnas_ley=["Cu_pct"])

    assert list(resultado.columns) == list(df_valido.columns)
    assert len(resultado) == 3


def test_leer_csv_assay_falla_si_faltan_columnas(tmp_path):
    df_incompleto = pd.DataFrame({"hole_id": ["DDH-01"], "from": [0.0]})
    ruta = tmp_path / "assay_incompleto.csv"
    df_incompleto.to_csv(ruta, index=False)

    with pytest.raises(ValueError, match="Faltan columnas requeridas"):
        leer_csv_assay(str(ruta), columnas_ley=["Cu_pct"])


# ---------- Tests: validar_assay ----------

def test_validar_assay_pasa_con_datos_correctos(df_valido):
    # No debe lanzar ninguna excepción
    validar_assay(df_valido, columnas_ley=["Cu_pct"])


def test_validar_assay_falla_con_hole_id_vacio(df_valido):
    df_valido.loc[0, "hole_id"] = None

    with pytest.raises(ValueError, match="hole_id vacío"):
        validar_assay(df_valido, columnas_ley=["Cu_pct"])


def test_validar_assay_falla_con_from_mayor_igual_to(df_valido):
    df_valido.loc[0, "from"] = 5.0
    df_valido.loc[0, "to"] = 2.0

    with pytest.raises(ValueError, match="'from' >= 'to'"):
        validar_assay(df_valido, columnas_ley=["Cu_pct"])


def test_validar_assay_falla_con_ley_negativa(df_valido):
    df_valido.loc[0, "Cu_pct"] = -0.1

    with pytest.raises(ValueError, match="Cu_pct negativas"):
        validar_assay(df_valido, columnas_ley=["Cu_pct"])


def test_validar_assay_falla_con_intervalos_solapados():
    df_solapado = pd.DataFrame({
        "hole_id": ["DDH-01", "DDH-01"],
        "from": [0.0, 1.0],
        "to": [2.0, 3.0],
        "Cu_pct": [0.5, 0.8],
    })

    with pytest.raises(ValueError, match="solapados"):
        validar_assay(df_solapado, columnas_ley=["Cu_pct"])


# ---------- Tests: componer_assay ----------

def test_componer_assay_genera_compositos_correctos(df_valido):
    resultado = componer_assay(df_valido, longitud_composito=2.0, columnas_ley=["Cu_pct"])

    assert len(resultado) == 3
    assert list(resultado["from"]) == [0.0, 2.0, 4.0]
    assert list(resultado["to"]) == [2.0, 4.0, 6.0]
    # El primer intervalo coincide exactamente con un compósito de 2m
    assert resultado.loc[0, "Cu_pct"] == 0.5


def test_componer_assay_pondera_correctamente_intervalo_parcial():
    # Un intervalo de 0 a 3m con ley 1.0, compositado cada 2m
    df = pd.DataFrame({
        "hole_id": ["DDH-01"],
        "from": [0.0],
        "to": [3.0],
        "Cu_pct": [1.0],
    })

    resultado = componer_assay(df, longitud_composito=2.0, columnas_ley=["Cu_pct"])

    # Ambos compósitos (0-2 y 2-4) deben tener ley 1.0,
    # ya que todo el intervalo original tiene la misma ley
    assert resultado["Cu_pct"].tolist() == [1.0, 1.0]


def test_componer_assay_devuelve_dataframe_vacio_si_no_hay_datos():
    df_vacio = pd.DataFrame(columns=["hole_id", "from", "to", "Cu_pct"])

    resultado = componer_assay(df_vacio, longitud_composito=2.0, columnas_ley=["Cu_pct"])

    assert resultado.empty


# ---------- Tests: guardar_csv ----------

def test_guardar_csv_crea_archivo_correctamente(tmp_path, df_valido):
    ruta = tmp_path / "salida.csv"

    guardar_csv(df_valido, str(ruta))

    assert ruta.exists()
    df_leido = pd.read_csv(ruta)
    assert len(df_leido) == len(df_valido)