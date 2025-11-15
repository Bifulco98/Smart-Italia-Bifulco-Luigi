
SmartFarm Italia è un progetto Python che simula dati agricoli e li visualizza tramite una dashboard interattiva. Il simulatore genera informazioni ambientali (temperatura, umidità, precipitazioni), agronomiche (stadio crescita, nutrienti, resa) ed economiche (costi, ricavi, margine) per più appezzamenti.

La dashboard, sviluppata con Dash e Plotly, offre tre sezioni principali:

Panoramica (resa media, margine totale, precipitazioni).

Focus Economico (ricavi, costi, margine cumulato).

Focus Ambientale (temperatura, umidità, precipitazioni e tabella dati).

Il progetto include test automatici tramite PyTest:

test unitari del simulatore,

test di integrazione sull’intera pipeline dati,

test sui KPI (resa, costi, ricavi, margine, variabili ambientali).

La dashboard si avvia con:
python src/dashboard.py

I test si eseguono con:
python -m pytest -v