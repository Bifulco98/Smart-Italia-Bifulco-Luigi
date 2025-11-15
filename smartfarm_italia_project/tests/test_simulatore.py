import sys
import os
import pandas as pd
from datetime import date

# Rende visibile la cartella root
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(ROOT)

from src.simulatore import genera_dati, get_appezzamenti_default
from src.dashboard import filtra_dati


# ---------------------------------------------------------
# FIXTURE CENTRALIZZATA
# ---------------------------------------------------------

def get_full_dataset():
    """Generazione dati reali per un mese (scenario completo)."""
    df = genera_dati(
        data_inizio="2024-03-01",
        data_fine="2024-03-10",
        appezzamenti=get_appezzamenti_default(),
        random_state=42,
        salva_csv=False,
    )
    df["data"] = pd.to_datetime(df["data"])
    return df


# ---------------------------------------------------------
# TEST 1 — Integrazione simulatore + filtro
# ---------------------------------------------------------

def test_filtra_dati_integrazione():
    df = get_full_dataset()

    # scegliamo un appezzamento esistente
    appez = df["id_appezzamento"].iloc[0]

    df_filtrato = filtra_dati(
        appezzamento=appez,
        start_date=date(2024, 3, 5),
        end_date=date(2024, 3, 7),
    )

    # Tutte le righe devono appartenere a quell’appezzamento
    assert df_filtrato["id_appezzamento"].nunique() == 1
    assert (df_filtrato["id_appezzamento"] == appez).all()

    # Intervallo date corretto
    assert df_filtrato["data"].min().date() >= date(2024, 3, 5)
    assert df_filtrato["data"].max().date() <= date(2024, 3, 7)


# ---------------------------------------------------------
# TEST 2 — KPI di integrazione
# ---------------------------------------------------------

def test_kpi_integrazione():
    df = get_full_dataset()

    # Filtriamo un range
    df_range = filtra_dati(
        appezzamento="ALL",
        start_date=date(2024, 3, 2),
        end_date=date(2024, 3, 5),
    )

    # KPI da testare
    resa_media = df_range["resa_kg_ha"].mean()
    margine_totale = df_range["margine_eur"].sum()
    temp_media = df_range["temperatura_c"].mean()

    # Non devono essere valori "strani" o non calcolati
    assert resa_media > 0
    assert not pd.isna(resa_media)

    assert not pd.isna(margine_totale)

    assert -20 <= temp_media <= 50, "Temperatura media fuori range"


# ---------------------------------------------------------
# TEST 3 — Coerenza pipeline completa
# simulatore → filtra_dati → KPI → coerenza
# ---------------------------------------------------------

def test_pipeline_end_to_end():
    df = get_full_dataset()

    # Step 1: filtro
    df_f = filtra_dati("ALL", date(2024, 3, 3), date(2024, 3, 4))

    # Step 2: KPI calcolati manualmente
    resa = df_f["resa_kg_ha"].mean()
    costi = df_f["costo_totale_eur"].sum()
    ricavi = df_f["ricavi_totali_eur"].sum()
    margine = df_f["margine_eur"].sum()

    # Step 3: Controlli di integrazione
    assert resa >= 0
    assert costi >= 0
    assert ricavi >= 0

    # Il margine totale deve essere approssimativamente ricavi - costi
    assert abs(margine - (ricavi - costi)) < 0.01 * len(df_f), \
        "Margine totale incoerente con ricavi e costi"

    # Controllo sulla presenza di dati ragionevoli
    assert df_f["temperatura_c"].between(-20, 50).all()
    assert df_f["umidita_suolo_pct"].between(0, 100).all()
    assert (df_f["precipitazioni_mm"] >= 0).all()


# ---------------------------------------------------------
# TEST 4 — End to end per appezzamento singolo
# ---------------------------------------------------------

def test_pipeline_singolo_appezzamento():
    df = get_full_dataset()

    appez = df["id_appezzamento"].unique()[0]

    df_f = filtra_dati(
        appezzamento=appez,
        start_date=date(2024, 3, 1),
        end_date=date(2024, 3, 10),
    )

    # Verifico che la pipeline funzioni correttamente
    assert df_f["id_appezzamento"].nunique() == 1
    assert (df_f["id_appezzamento"] == appez).all()

    # Verifico che ci siano dati
    assert not df_f.empty

    # KPI integrati
    assert df_f["resa_kg_ha"].mean() >= 0
    assert df_f["margine_eur"].sum() is not None
