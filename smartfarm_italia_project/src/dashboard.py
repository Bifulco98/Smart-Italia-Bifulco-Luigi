"""
Dashboard SmartFarm Italia: vista panoramica, focus economico e focus ambientale.
"""

from __future__ import annotations

from datetime import date

import pandas as pd
from dash import Dash, dcc, html, Input, Output, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px

from .simulatore import genera_dati, get_appezzamenti_default


# ---------------------------------------------------------------------------
# Dati
# ---------------------------------------------------------------------------

df = genera_dati(
    data_inizio="2024-01-01",
    data_fine="2024-12-31",
    appezzamenti=get_appezzamenti_default(),
    random_state=42,
    salva_csv=False,
)

df["data"] = pd.to_datetime(df["data"])

appezzamenti_options = [{"label": "Tutti gli appezzamenti", "value": "ALL"}]
for appez_id in df["id_appezzamento"].unique():
    appezzamenti_options.append(
        {"label": f"Appezzamento {appez_id}", "value": appez_id}
    )

data_min = df["data"].min().date()
data_max = df["data"].max().date()


# ---------------------------------------------------------------------------
# Stili Tabs
# ---------------------------------------------------------------------------

TAB_LABEL_STYLE = {
    "fontWeight": "500",
    "color": "#495057",  # grigio scuro leggibile
}

TAB_LABEL_ACTIVE_STYLE = {
    "fontWeight": "700",
    "color": "#0d6efd",  # blu bootstrap
}


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.LUX],
    title="SmartFarm Italia - Dashboard",
    suppress_callback_exceptions=True,
)

server = app.server


def kpi_card(title: str, value: str, subtitle: str = "") -> dbc.Card:
    return dbc.Card(
        [
            dbc.CardBody(
                [
                    html.H6(title, className="card-title text-muted mb-1"),
                    html.H3(value, className="card-text fw-bold mb-1"),
                    html.Small(subtitle, className="text-muted"),
                ]
            )
        ],
        className="shadow-sm h-100",
    )


def fig_nessun_dato(titolo: str = "Nessun dato disponibile per i filtri selezionati"):
    fig = px.scatter(title=titolo)
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return fig


app.layout = dbc.Container(
    fluid=True,
    children=[
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H2(
                            "SmartFarm Italia – Dashboard agricola",
                            className="fw-bold mb-1",
                        ),
                        html.P(
                            "Monitoraggio di dati ambientali, produttivi ed economici.",
                            className="text-muted mb-0",
                        ),
                    ],
                    md=8,
                ),
            ],
            className="my-3",
        ),

        html.Hr(),

        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Label("Seleziona appezzamento", className="fw-semibold mb-1"),
                        dcc.Dropdown(
                            id="filtro-appezzamento",
                            options=appezzamenti_options,
                            value="ALL",
                            clearable=False,
                        ),
                    ],
                    md=4,
                ),
                dbc.Col(
                    [
                        html.Label("Intervallo temporale", className="fw-semibold mb-1"),
                        dcc.DatePickerRange(
                            id="filtro-date",
                            min_date_allowed=data_min,
                            max_date_allowed=data_max,
                            start_date=data_min,
                            end_date=data_max,
                            display_format="DD/MM/YYYY",
                        ),
                    ],
                    md=6,
                ),
                dbc.Col(
                    [
                        html.Label(" ", className="mb-1"),
                        dbc.Button(
                            "Reset filtri",
                            id="btn-reset-filtri",
                            color="primary",
                            className="w-100",
                            size="sm",
                        ),
                    ],
                    md=2,
                    className="d-flex flex-column justify-content-end",
                ),
            ],
            className="my-3",
        ),

        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader(
                                dbc.Tabs(
                                    id="tabs",
                                    active_tab="tab-panoramica",
                                    className="nav-pills nav-fill",
                                    children=[
                                        dbc.Tab(
                                            label="Panoramica",
                                            tab_id="tab-panoramica",
                                            label_style=TAB_LABEL_STYLE,
                                            active_label_style=TAB_LABEL_ACTIVE_STYLE,
                                        ),
                                        dbc.Tab(
                                            label="Focus economico",
                                            tab_id="tab-economico",
                                            label_style=TAB_LABEL_STYLE,
                                            active_label_style=TAB_LABEL_ACTIVE_STYLE,
                                        ),
                                        dbc.Tab(
                                            label="Focus ambientale",
                                            tab_id="tab-ambientale",
                                            label_style=TAB_LABEL_STYLE,
                                            active_label_style=TAB_LABEL_ACTIVE_STYLE,
                                        ),
                                    ],
                                )
                            ),
                            dbc.CardBody(
                                id="tabs-content",
                                className="bg-light",
                            ),
                        ],
                        className="shadow-sm",
                    ),
                    md=12,
                )
            ],
            className="mb-4",
        ),
    ],
)


# ---------------------------------------------------------------------------
# Utilità dati
# ---------------------------------------------------------------------------

def filtra_dati(appezzamento: str, start_date: date, end_date: date) -> pd.DataFrame:
    df_filtrato = df.copy()

    if appezzamento and appezzamento != "ALL":
        df_filtrato = df_filtrato[df_filtrato["id_appezzamento"] == appezzamento]

    if start_date is not None:
        df_filtrato = df_filtrato[df_filtrato["data"] >= pd.to_datetime(start_date)]
    if end_date is not None:
        df_filtrato = df_filtrato[df_filtrato["data"] <= pd.to_datetime(end_date)]

    return df_filtrato


# ---------------------------------------------------------------------------
# Callback reset filtri
# ---------------------------------------------------------------------------

@app.callback(
    Output("filtro-appezzamento", "value"),
    Output("filtro-date", "start_date"),
    Output("filtro-date", "end_date"),
    Input("btn-reset-filtri", "n_clicks"),
    prevent_initial_call=True,
)
def reset_filtri(n_clicks):
    return "ALL", data_min, data_max


# ---------------------------------------------------------------------------
# Callback contenuto tabs
# ---------------------------------------------------------------------------

@app.callback(
    Output("tabs-content", "children"),
    Input("tabs", "active_tab"),
)
def render_tab_content(active_tab):
    if active_tab == "tab-panoramica":
        return [
            dbc.Row(
                [
                    dbc.Col(id="kpi-resa-media", md=4),
                    dbc.Col(id="kpi-margine-totale", md=4),
                    dbc.Col(id="kpi-precipitazioni-totali", md=4),
                ],
                className="my-3",
            ),
            dbc.Row(
                [
                    dbc.Col(dcc.Graph(id="grafico-resa-tempo"), md=6),
                    dbc.Col(dcc.Graph(id="grafico-margine-tempo"), md=6),
                ],
                className="my-3",
            ),
        ]

    if active_tab == "tab-economico":
        return [
            dbc.Row(
                [
                    dbc.Col(id="kpi-ricavi-totali", md=4),
                    dbc.Col(id="kpi-costi-totali", md=4),
                    dbc.Col(id="kpi-margine-medio", md=4),
                ],
                className="my-3",
            ),
            dbc.Row(
                [
                    dbc.Col(dcc.Graph(id="grafico-ricavi-tempo"), md=6),
                    dbc.Col(dcc.Graph(id="grafico-costi-tempo"), md=6),
                ],
                className="my-3",
            ),
            dbc.Row(
                [
                    dbc.Col(dcc.Graph(id="grafico-margine-accumulato"), md=12),
                ],
                className="my-3",
            ),
        ]

    if active_tab == "tab-ambientale":
        return [
            dbc.Row(
                [
                    dbc.Col(id="kpi-temp-media", md=4),
                    dbc.Col(id="kpi-umidita-media", md=4),
                    dbc.Col(id="kpi-precipitazioni-totali-amb", md=4),
                ],
                className="my-3",
            ),
            dbc.Row(
                [
                    dbc.Col(dcc.Graph(id="grafico-temp-tempo"), md=6),
                    dbc.Col(dcc.Graph(id="grafico-umidita-tempo"), md=6),
                ],
                className="my-3",
            ),
            dbc.Row(
                [
                    dbc.Col(dcc.Graph(id="grafico-precipitazioni-tempo"), md=6),
                    dbc.Col(
                        [
                            html.H5("Dati grezzi (riepilogo)", className="mb-2"),
                            dash_table.DataTable(
                                id="tabella-dati",
                                page_size=10,
                                style_table={"height": "400px", "overflowY": "auto"},
                                style_header={"fontWeight": "bold"},
                                style_cell={
                                    "fontSize": 12,
                                    "padding": "4px",
                                    "whiteSpace": "nowrap",
                                    "textOverflow": "ellipsis",
                                },
                            ),
                        ],
                        md=6,
                    ),
                ],
                className="my-3",
            ),
        ]

    return html.Div("Tab non riconosciuta.")


# ---------------------------------------------------------------------------
# KPI panoramica
# ---------------------------------------------------------------------------

@app.callback(
    Output("kpi-resa-media", "children"),
    Output("kpi-margine-totale", "children"),
    Output("kpi-precipitazioni-totali", "children"),
    Input("filtro-appezzamento", "value"),
    Input("filtro-date", "start_date"),
    Input("filtro-date", "end_date"),
)
def aggiorna_kpi_panoramica(appezzamento, start_date, end_date):
    df_filtrato = filtra_dati(appezzamento, start_date, end_date)

    if df_filtrato.empty:
        return (
            kpi_card("Resa media (kg/ha)", "-", "Nessun dato nel periodo selezionato"),
            kpi_card("Margine totale (€)", "-", "Nessun dato nel periodo selezionato"),
            kpi_card(
                "Precipitazioni totali (mm)",
                "-",
                "Nessun dato nel periodo selezionato",
            ),
        )

    resa_media = df_filtrato["resa_kg_ha"].mean()
    margine_totale = df_filtrato["margine_eur"].sum()
    precipitazioni_totali = df_filtrato["precipitazioni_mm"].sum()

    return (
        kpi_card(
            "Resa media (kg/ha)",
            f"{resa_media:,.3f}",
            "Media su periodo e appezzamenti selezionati",
        ),
        kpi_card(
            "Margine totale (€)",
            f"{margine_totale:,.3f}",
            "Somma dei margini giornalieri",
        ),
        kpi_card(
            "Precipitazioni totali (mm)",
            f"{precipitazioni_totali:,.3f}",
            "Accumulo totale nel periodo",
        ),
    )


# ---------------------------------------------------------------------------
# KPI economici
# ---------------------------------------------------------------------------

@app.callback(
    Output("kpi-ricavi-totali", "children"),
    Output("kpi-costi-totali", "children"),
    Output("kpi-margine-medio", "children"),
    Input("filtro-appezzamento", "value"),
    Input("filtro-date", "start_date"),
    Input("filtro-date", "end_date"),
)
def aggiorna_kpi_economici(appezzamento, start_date, end_date):
    df_filtrato = filtra_dati(appezzamento, start_date, end_date)

    if df_filtrato.empty:
        return (
            kpi_card("Ricavi totali (€)", "-", "Nessun dato nel periodo selezionato"),
            kpi_card("Costi totali (€)", "-", "Nessun dato nel periodo selezionato"),
            kpi_card("Margine medio (€)", "-", "Nessun dato nel periodo selezionato"),
        )

    ricavi_totali = df_filtrato["ricavi_totali_eur"].sum()
    costi_totali = df_filtrato["costo_totale_eur"].sum()
    margine_medio = df_filtrato["margine_eur"].mean()

    return (
        kpi_card(
            "Ricavi totali (€)",
            f"{ricavi_totali:,.3f}",
            "Somma ricavi nel periodo selezionato",
        ),
        kpi_card(
            "Costi totali (€)",
            f"{costi_totali:,.3f}",
            "Somma costi nel periodo selezionato",
        ),
        kpi_card(
            "Margine medio (€)",
            f"{margine_medio:,.3f}",
            "Media del margine giornaliero",
        ),
    )


# ---------------------------------------------------------------------------
# KPI ambientali
# ---------------------------------------------------------------------------

@app.callback(
    Output("kpi-temp-media", "children"),
    Output("kpi-umidita-media", "children"),
    Output("kpi-precipitazioni-totali-amb", "children"),
    Input("filtro-appezzamento", "value"),
    Input("filtro-date", "start_date"),
    Input("filtro-date", "end_date"),
)
def aggiorna_kpi_ambientali(appezzamento, start_date, end_date):
    df_filtrato = filtra_dati(appezzamento, start_date, end_date)

    if df_filtrato.empty:
        return (
            kpi_card("Temperatura media (°C)", "-", "Nessun dato nel periodo selezionato"),
            kpi_card("Umidità media suolo (%)", "-", "Nessun dato nel periodo selezionato"),
            kpi_card(
                "Precipitazioni totali (mm)",
                "-",
                "Nessun dato nel periodo selezionato",
            ),
        )

    temp_media = df_filtrato["temperatura_c"].mean()
    umidita_media = df_filtrato["umidita_suolo_pct"].mean()
    precipitazioni_totali = df_filtrato["precipitazioni_mm"].sum()

    return (
        kpi_card(
            "Temperatura media (°C)",
            f"{temp_media:,.3f}",
            "Media nel periodo selezionato",
        ),
        kpi_card(
            "Umidità media suolo (%)",
            f"{umidita_media:,.3f}",
            "Media nel periodo selezionato",
        ),
        kpi_card(
            "Precipitazioni totali (mm)",
            f"{precipitazioni_totali:,.3f}",
            "Accumulo totale nel periodo",
        ),
    )


# ---------------------------------------------------------------------------
# Grafici panoramica
# ---------------------------------------------------------------------------

@app.callback(
    Output("grafico-resa-tempo", "figure"),
    Output("grafico-margine-tempo", "figure"),
    Input("filtro-appezzamento", "value"),
    Input("filtro-date", "start_date"),
    Input("filtro-date", "end_date"),
)
def aggiorna_grafici_panoramica(appezzamento, start_date, end_date):
    df_filtrato = filtra_dati(appezzamento, start_date, end_date)

    if df_filtrato.empty:
        fig_vuota = fig_nessun_dato()
        return fig_vuota, fig_vuota

    fig_resa = px.line(
        df_filtrato,
        x="data",
        y="resa_kg_ha",
        color="id_appezzamento",
        title="Andamento della resa (kg/ha)",
        labels={
            "data": "Data",
            "resa_kg_ha": "Resa (kg/ha)",
            "id_appezzamento": "Appezzamento",
        },
        template="plotly_white",
    )

    fig_margine = px.line(
        df_filtrato,
        x="data",
        y="margine_eur",
        color="id_appezzamento",
        title="Margine giornaliero (€)",
        labels={
            "data": "Data",
            "margine_eur": "Margine (€)",
            "id_appezzamento": "Appezzamento",
        },
        template="plotly_white",
    )

    return fig_resa, fig_margine


# ---------------------------------------------------------------------------
# Grafici economici
# ---------------------------------------------------------------------------

@app.callback(
    Output("grafico-ricavi-tempo", "figure"),
    Output("grafico-costi-tempo", "figure"),
    Output("grafico-margine-accumulato", "figure"),
    Input("filtro-appezzamento", "value"),
    Input("filtro-date", "start_date"),
    Input("filtro-date", "end_date"),
)
def aggiorna_grafici_economici(appezzamento, start_date, end_date):
    df_filtrato = filtra_dati(appezzamento, start_date, end_date)

    if df_filtrato.empty:
        fig_vuota = fig_nessun_dato()
        return fig_vuota, fig_vuota, fig_vuota

    fig_ricavi = px.line(
        df_filtrato,
        x="data",
        y="ricavi_totali_eur",
        color="id_appezzamento",
        title="Ricavi giornalieri (€)",
        labels={
            "data": "Data",
            "ricavi_totali_eur": "Ricavi (€)",
            "id_appezzamento": "Appezzamento",
        },
        template="plotly_white",
    )

    fig_costi = px.line(
        df_filtrato,
        x="data",
        y="costo_totale_eur",
        color="id_appezzamento",
        title="Costi giornalieri (€)",
        labels={
            "data": "Data",
            "costo_totale_eur": "Costi (€)",
            "id_appezzamento": "Appezzamento",
        },
        template="plotly_white",
    )

    df_acc = df_filtrato.sort_values("data").copy()
    df_acc["margine_accumulato"] = df_acc.groupby("id_appezzamento")[
        "margine_eur"
    ].cumsum()

    fig_margine_acc = px.line(
        df_acc,
        x="data",
        y="margine_accumulato",
        color="id_appezzamento",
        title="Margine cumulato (€)",
        labels={
            "data": "Data",
            "margine_accumulato": "Margine cumulato (€)",
            "id_appezzamento": "Appezzamento",
        },
        template="plotly_white",
    )

    return fig_ricavi, fig_costi, fig_margine_acc


# ---------------------------------------------------------------------------
# Grafici ambientali + tabella
# ---------------------------------------------------------------------------

@app.callback(
    Output("grafico-temp-tempo", "figure"),
    Output("grafico-umidita-tempo", "figure"),
    Output("grafico-precipitazioni-tempo", "figure"),
    Output("tabella-dati", "data"),
    Output("tabella-dati", "columns"),
    Input("filtro-appezzamento", "value"),
    Input("filtro-date", "start_date"),
    Input("filtro-date", "end_date"),
)
def aggiorna_grafici_ambientali_e_tabella(appezzamento, start_date, end_date):
    df_filtrato = filtra_dati(appezzamento, start_date, end_date)

    if df_filtrato.empty:
        fig_vuota = fig_nessun_dato("Nessun dato da mostrare")
        return fig_vuota, fig_vuota, fig_vuota, [], []

    fig_temp = px.line(
        df_filtrato,
        x="data",
        y="temperatura_c",
        color="id_appezzamento",
        title="Temperatura (°C)",
        labels={
            "data": "Data",
            "temperatura_c": "Temperatura (°C)",
            "id_appezzamento": "Appezzamento",
        },
        template="plotly_white",
    )

    fig_umidita = px.line(
        df_filtrato,
        x="data",
        y="umidita_suolo_pct",
        color="id_appezzamento",
        title="Umidità del suolo (%)",
        labels={
            "data": "Data",
            "umidita_suolo_pct": "Umidità suolo (%)",
            "id_appezzamento": "Appezzamento",
        },
        template="plotly_white",
    )

    fig_prec = px.bar(
        df_filtrato,
        x="data",
        y="precipitazioni_mm",
        color="id_appezzamento",
        title="Precipitazioni giornaliere (mm)",
        labels={
            "data": "Data",
            "precipitazioni_mm": "Precipitazioni (mm)",
            "id_appezzamento": "Appezzamento",
        },
        template="plotly_white",
    )

    colonne_tabella = [
        "data",
        "id_appezzamento",
        "coltura",
        "temperatura_c",
        "umidita_suolo_pct",
        "precipitazioni_mm",
        "resa_kg_ha",
        "margine_eur",
    ]
    df_tab = df_filtrato[colonne_tabella].copy()
    df_tab["data"] = df_tab["data"].dt.strftime("%Y-%m-%d")

    columns = [{"name": c, "id": c} for c in df_tab.columns]
    data = df_tab.to_dict("records")

    return fig_temp, fig_umidita, fig_prec, data, columns


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)
