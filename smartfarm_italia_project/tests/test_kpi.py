import sys
import os
from datetime import date
import pandas as pd

# aggiunge root al PYTHONPATH
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(ROOT)

from src.simulatore import genera_dati, get_appezzamenti_default
from src.dashboard import filtra_dati


# ---------------------------------------------------------
# FIXTURE CENTRALIZZATA
# ---------------------------------------------------------

def get_filtered():
    """Dataset filtrato esattamente come farebbe la dashboard."""
    df = genera_dati(
        data_inizio="2024-04-01",
        data_fine="2024-04-10",
        appezzamenti=get_appezzamenti_default(),
        random_state=42,
        salva_csv=False
    )
    df["data"] = pd.to_datetime(df["data"])

    # filtro come la dashboard (ALL appezzamenti)
    return filtra_dati(
        appezzamento="ALL",
        start_date=date(2024, 4, 3),
        end_date=date(2024, 4, 7)
    )


# ---------------------------------------------------------
# TEST KPI — PANORAMICA
# ---------------------------------------------------------

def test_kpi_resa_media():
    df = get_filtered()
    resa_media = df["resa_kg_ha"].mean()
    assert resa_media >= 0
    assert not pd.isna(resa_media)


def test_kpi_margine_totale():
    df = get_filtered()
    margine_tot = df["margine_eur"].sum()
    assert not pd.isna(margine_tot)


def test_kpi_precipitazioni_totali():
    df = get_filtered()
    prec = df["precipitazioni_mm"].sum()
    assert not pd.isna(prec)
    assert prec >= 0


# ---------------------------------------------------------
# TEST KPI — ECONOMICI
# ---------------------------------------------------------

def test_kpi_ricavi_totali():
    df = get_filtered()
    ricavi = df["ricavi_totali_eur"].sum()
    assert ricavi >= 0
    assert not pd.isna(ricavi)


def test_kpi_costi_totali():
    df = get_filtered()
    costi = df["costo_totale_eur"].sum()
    assert costi >= 0
    assert not pd.isna(costi)


def test_kpi_margine_medio():
    df = get_filtered()
    margine_medio = df["margine_eur"].mean()
    assert not pd.isna(margine_medio)


# ---------------------------------------------------------
# TEST KPI — AMBIENTALI
# ---------------------------------------------------------

def test_kpi_temperatura_media():
    df = get_filtered()
    temp = df["temperatura_c"].mean()
    assert -20 <= temp <= 50
    assert not pd.isna(temp)


def test_kpi_umidita_media():
    df = get_filtered()
    umid = df["umidita_suolo_pct"].mean()
    assert 0 <= umid <= 100
    assert not pd.isna(umid)


def test_kpi_precipitazioni_ambientali():
    df = get_filtered()
    prec = df["precipitazioni_mm"].sum()
    assert prec >= 0
    assert not pd.isna(prec)


# ---------------------------------------------------------
# COERENZA KPI ECONOMICI
# ---------------------------------------------------------

def test_kpi_margine_coerente():
    df = get_filtered()

    ricavi = df["ricavi_totali_eur"].sum()
    costi = df["costo_totale_eur"].sum()
    margine_kpi = df["margine_eur"].sum()

    # tolleranza: rumore statistico del simulatore
    assert abs(margine_kpi - (ricavi - costi)) < 0.01 * len(df)


# ---------------------------------------------------------
# KPI GLOBALI — END TO END
# ---------------------------------------------------------

def test_kpi_end_to_end_consistency():
    df = get_filtered()

    # KPI
    resa = df["resa_kg_ha"].mean()
    temp = df["temperatura_c"].mean()
    prec = df["precipitazioni_mm"].sum()
    margine = df["margine_eur"].sum()

    assert resa >= 0
    assert -20 <= temp <= 50
    assert prec >= 0
    assert not pd.isna(margine)
