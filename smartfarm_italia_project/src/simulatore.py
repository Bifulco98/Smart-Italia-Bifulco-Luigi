"""
Modulo per la generazione dei dati simulati di SmartFarm Italia.

Questo modulo implementa le funzioni di simulazione descritte nel Project Work:
- dati ambientali (temperatura, umidità del suolo, precipitazioni, nutrienti)
- dati produttivi (resa per ettaro, stadio di crescita delle colture)
- dati economici (costi, ricavi, margini)

L'obiettivo non è riprodurre un modello agronomico perfetto, ma ottenere
dati coerenti, realistici e sufficientemente variabili per alimentare
la dashboard di analisi.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


import numpy as np
import pandas as pd

from datetime import datetime

from .config import OUTPUT_DIR


# ---------------------------------------------------------------------------
# Configurazione di base degli appezzamenti e delle colture
# ---------------------------------------------------------------------------

@dataclass
class Appezzamento:
    """
    Rappresenta un appezzamento di terreno di SmartFarm Italia.

    Attributes:
        id_appezzamento: identificativo univoco (es. "A1", "A2"...)
        coltura: tipo di coltura (es. "Grano", "Mais", "Ortaggi")
        superficie_ha: superficie in ettari
        zona_climatica: etichetta indicativa per eventuali differenze climatiche
    """
    id_appezzamento: str
    coltura: str
    superficie_ha: float
    zona_climatica: str = "pianura"


def get_appezzamenti_default() -> List[Appezzamento]:
    """
    Restituisce una configurazione di default per gli appezzamenti di SmartFarm Italia.
    """
    return [
        Appezzamento("A1", "Grano", 12.5, "pianura"),
        Appezzamento("A2", "Mais", 8.0, "collina"),
        Appezzamento("A3", "Ortaggi", 5.2, "pianura"),
    ]


# ---------------------------------------------------------------------------
# Funzione principale di simulazione
# ---------------------------------------------------------------------------

def genera_dati(
    data_inizio: str | datetime,
    data_fine: str | datetime,
    appezzamenti: Optional[List[Appezzamento]] = None,
    freq: str = "D",
    random_state: Optional[int] = None,
    salva_csv: bool = False,
    nome_file: Optional[str] = None,
) -> pd.DataFrame:
    """
    Genera un dataset simulato per SmartFarm Italia.

    Parametri
    ---------
    data_inizio : str | datetime
        Data di inizio della simulazione (es. "2024-01-01").
    data_fine : str | datetime
        Data di fine della simulazione (inclusa) (es. "2024-12-31").
    appezzamenti : list[Appezzamento], opzionale
        Lista di appezzamenti da simulare. Se None, viene usata una configurazione di default.
    freq : str, default "D"
        Frequenza dei dati (es. "D" = giornaliera).
    random_state : int, opzionale
        Seed per la generazione casuale, per rendere la simulazione ripetibile.
    salva_csv : bool, default False
        Se True, salva il DataFrame generato in formato CSV in data/output.
    nome_file : str, opzionale
        Nome del file CSV da salvare (se salva_csv=True). Se non specificato,
        viene generato automaticamente.

    Restituisce
    -----------
    df : pandas.DataFrame
        DataFrame con una riga per (data, appezzamento) e colonne:
        - data
        - id_appezzamento
        - coltura
        - superficie_ha
        - temperatura_c
        - umidita_suolo_pct
        - precipitazioni_mm
        - nutrienti_n
        - nutrienti_p
        - nutrienti_k
        - stadio_crescita
        - resa_kg_ha
        - resa_totale_kg
        - costo_totale_eur
        - ricavi_totali_eur
        - margine_eur
    """
    rng = np.random.default_rng(random_state)

    data_inizio = pd.to_datetime(data_inizio)
    data_fine = pd.to_datetime(data_fine)
    date_index = pd.date_range(start=data_inizio, end=data_fine, freq=freq)

    if appezzamenti is None:
        appezzamenti = get_appezzamenti_default()

    records = []

    giorni_totali = (date_index[-1] - date_index[0]).days + 1

    for appez in appezzamenti:
        for i, data in enumerate(date_index):
            progress = i / max(giorni_totali - 1, 1)

            # ---------------------------
            # 1) SIMULAZIONE AMBIENTALE
            # ---------------------------

            day_of_year = data.timetuple().tm_yday
            temp_media = 17.5 + 12.5 * np.sin(2 * np.pi * (day_of_year - 80) / 365)
            temperatura_c = temp_media + rng.normal(0, 2.0)

            if rng.random() < 0.3:
                precipitazioni_mm = float(max(0, rng.normal(10, 8)))
            else:
                precipitazioni_mm = 0.0

            if i == 0:
                umidita_suolo_pct = rng.uniform(30, 60)
                nutrienti_n = rng.uniform(40, 80)
                nutrienti_p = rng.uniform(20, 50)
                nutrienti_k = rng.uniform(30, 70)
            else:
                prev = records[-1]["umidita_suolo_pct"]
                delta = -rng.uniform(0.1, 0.8)
                if precipitazioni_mm > 0:
                    delta += min(20, precipitazioni_mm * rng.uniform(0.3, 0.6))
                umidita_suolo_pct = np.clip(prev + delta, 10, 90)

                nutrienti_n = max(5, records[-1]["nutrienti_n"] - rng.uniform(0.05, 0.3))
                nutrienti_p = max(5, records[-1]["nutrienti_p"] - rng.uniform(0.02, 0.15))
                nutrienti_k = max(5, records[-1]["nutrienti_k"] - rng.uniform(0.05, 0.25))

                if rng.random() < 0.03:
                    nutrienti_n += rng.uniform(10, 25)
                    nutrienti_p += rng.uniform(5, 15)
                    nutrienti_k += rng.uniform(8, 20)

            # ---------------------------
            # 2) STADIO DI CRESCITA & RESA
            # ---------------------------

            if appez.coltura.lower() in {"grano", "mais"}:
                stadio_base = np.clip(np.sin(np.pi * progress), 0, 1)
            else:
                stadio_base = np.clip(0.3 + 0.7 * progress, 0, 1)

            stadio_crescita = float(np.clip(stadio_base + rng.normal(0, 0.05), 0, 1))

            resa_potenziale = stadio_crescita * 80  # kg/ha max teorico giornaliero

            penalita_umidita = 0.0
            if umidita_suolo_pct < 25 or umidita_suolo_pct > 80:
                penalita_umidita = 0.3
            elif umidita_suolo_pct < 35 or umidita_suolo_pct > 70:
                penalita_umidita = 0.15

            media_nutrients = (nutrienti_n + nutrienti_p + nutrienti_k) / 3
            penalita_nutrienti = 0.0
            if media_nutrients < 20:
                penalita_nutrienti = 0.4
            elif media_nutrients < 35:
                penalita_nutrienti = 0.2

            fattore_penalizzante = 1.0 - (penalita_umidita + penalita_nutrienti)
            fattore_penalizzante = max(0.1, fattore_penalizzante)

            resa_kg_ha = max(
                0.0,
                resa_potenziale * fattore_penalizzante + rng.normal(0, 3.0),
            )

            resa_totale_kg = resa_kg_ha * appez.superficie_ha

            # ---------------------------
            # 3) COSTI, RICAVI, MARGINE
            # ---------------------------

            costo_manodopera = 25 + rng.normal(0, 3)
            costo_input = 10 + rng.normal(0, 2)
            costo_totale_eur = max(0, costo_manodopera + costo_input)

            if appez.coltura.lower() == "grano":
                prezzo_kg = 0.25
            elif appez.coltura.lower() == "mais":
                prezzo_kg = 0.22
            else:
                prezzo_kg = 0.8

            ricavi_totali_eur = max(0, resa_totale_kg * prezzo_kg)
            margine_eur = ricavi_totali_eur - costo_totale_eur

            record = {
                "data": data,
                "id_appezzamento": appez.id_appezzamento,
                "coltura": appez.coltura,
                "superficie_ha": appez.superficie_ha,
                "temperatura_c": float(temperatura_c),
                "umidita_suolo_pct": float(umidita_suolo_pct),
                "precipitazioni_mm": float(precipitazioni_mm),
                "nutrienti_n": float(nutrienti_n),
                "nutrienti_p": float(nutrienti_p),
                "nutrienti_k": float(nutrienti_k),
                "stadio_crescita": float(stadio_crescita),
                "resa_kg_ha": float(resa_kg_ha),
                "resa_totale_kg": float(resa_totale_kg),
                "costo_totale_eur": float(costo_totale_eur),
                "ricavi_totali_eur": float(ricavi_totali_eur),
                "margine_eur": float(margine_eur),
            }
            records.append(record)

    df = pd.DataFrame.from_records(records)
    df.sort_values(["data", "id_appezzamento"], inplace=True)
    df.reset_index(drop=True, inplace=True)

    # Arrotondamento a 3 decimali per tutti i valori numerici
    for col in df.select_dtypes(include=["float", "int"]).columns:
        df[col] = df[col].round(3)

    if salva_csv:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        if nome_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_file = f"smartfarm_dati_{timestamp}.csv"
        percorso = OUTPUT_DIR / nome_file
        df.to_csv(percorso, index=False, sep=";")
        print(f"Dati simulati salvati in: {percorso}")

    return df


if __name__ == "__main__":
    dati = genera_dati("2024-01-01", "2024-03-31", random_state=42, salva_csv=True)
    print(dati.head())
    print(f"Righe generate: {len(dati)}")
