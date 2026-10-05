from __future__ import annotations

import csv
import html
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
import plotly.express as px
import streamlit as st


RANKING_FILE = Path(__file__).with_name("ranking_publico.csv")
EXPECTED_COLUMNS = {
    "Posição",
    "Pessoa",
    "Celular final 4",
    "Votos HELP",
    "BMG (não conta)",
    "Sem comprovante",
    "Revisar",
    "Atualizado em",
}
COUNT_COLUMNS = ("Posição", "Votos HELP", "BMG (não conta)", "Sem comprovante", "Revisar")


def load_ranking(path: Path) -> tuple[list[dict[str, Any]], str]:
    with path.open("r", encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source, delimiter=";")
        if not reader.fieldnames or not EXPECTED_COLUMNS.issubset(reader.fieldnames):
            raise ValueError("O CSV não tem as colunas esperadas para o ranking.")

        rows: list[dict[str, Any]] = []
        for line_number, source_row in enumerate(reader, start=2):
            if not (source_row.get("Pessoa") or "").strip():
                continue
            row: dict[str, Any] = dict(source_row)
            try:
                for column in COUNT_COLUMNS:
                    row[column] = int(row[column] or 0)
            except (TypeError, ValueError) as error:
                raise ValueError(
                    f"Valor numérico inválido na linha {line_number} do CSV."
                ) from error
            rows.append(row)

    rows.sort(key=lambda row: (row["Posição"], row["Pessoa"].casefold()))
    updated_at = max((row.get("Atualizado em", "").strip() for row in rows), default="")
    return rows, updated_at


def add_motivation(rows: list[dict[str, Any]]) -> None:
    for index, row in enumerate(rows):
        if index == 0:
            if len(rows) == 1:
                row["Próximo passo"] = "Líder do ranking"
                continue
            lead = row["Votos HELP"] - rows[1]["Votos HELP"]
            row["Próximo passo"] = (
                f"Lidera por {lead} voto(s)" if lead > 0 else "Empate na liderança"
            )
            continue

        votes_to_pass = max(1, rows[index - 1]["Votos HELP"] - row["Votos HELP"] + 1)
        row["Próximo passo"] = f"Faltam {votes_to_pass} voto(s) para subir"


st.set_page_config(
    page_title="Ranking HELP | Prêmio Reclame Aqui",
    page_icon="🏆",
    layout="wide",
)

st.markdown(
    """
    <style>
    .block-container {max-width: 1220px; padding-top: 2rem; padding-bottom: 3rem;}
    div[data-testid="stMetric"] {
        background: #ffffff; border: 1px solid #e8edf2; border-radius: 14px;
        padding: 16px 18px; box-shadow: 0 3px 12px rgba(15, 23, 42, .05);
    }
    .last-update {
        display: flex; align-items: center; gap: 14px; margin: 10px 0 22px;
        padding: 16px 20px; border: 1px solid #fed7aa; border-left: 6px solid #f97316;
        border-radius: 14px; background: linear-gradient(100deg, #fff7ed, #ffffff);
    }
    .last-update-icon {font-size: 1.8rem;}
    .last-update-label {color: #9a3412; font-size: .78rem; font-weight: 800;
        letter-spacing: .08em; text-transform: uppercase;}
    .last-update-value {color: #431407; font-size: 1.15rem; font-weight: 700;
        margin-top: 2px;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🏆 Ranking HELP")
st.caption("Campanha Prêmio Reclame Aqui")

try:
    ranking, updated_at = load_ranking(RANKING_FILE)
except FileNotFoundError:
    st.error("Ainda não há um ranking publicado.")
    st.stop()
except (OSError, ValueError, csv.Error) as error:
    st.error(f"Não foi possível ler o ranking: {error}")
    st.stop()

if not ranking:
    st.info("O ranking está vazio.")
    st.stop()

add_motivation(ranking)

try:
    parsed_update = datetime.fromisoformat(updated_at)
    display_update = parsed_update.strftime("%d/%m/%Y às %H:%M")
except ValueError:
    display_update = updated_at or "não informada"

safe_update = html.escape(f"{display_update} · Horário de Brasília")
st.markdown(
    f'<div class="last-update"><div class="last-update-icon">🕒</div>'
    f'<div><div class="last-update-label">Última atualização</div>'
    f'<div class="last-update-value">{safe_update}</div></div></div>',
    unsafe_allow_html=True,
)

total_help = sum(row["Votos HELP"] for row in ranking)
first_place = ranking[0]

left, middle, right = st.columns(3)
left.metric("Votos para HELP", f"{total_help:,}".replace(",", "."))
middle.metric("Pessoas no ranking", len(ranking))
right.metric("Líder atual", first_place["Pessoa"])

st.divider()
st.subheader("🔥 Disputa do Top 7")
top7 = ranking[:7]
chart_data = pd.DataFrame(
    {
        "Pessoa": [
            f"{row['Pessoa']} · {row['Celular final 4']}"
            if row["Celular final 4"]
            else row["Pessoa"]
            for row in top7
        ],
        "Votos HELP": [row["Votos HELP"] for row in top7],
    }
)
figure = px.bar(
    chart_data,
    x="Votos HELP",
    y="Pessoa",
    orientation="h",
    text="Votos HELP",
    labels={"Pessoa": "", "Votos HELP": "Votos para HELP"},
    color_discrete_sequence=["#ec5b3f"],
)
figure.update_traces(
    textposition="outside",
    textfont_size=13,
    cliponaxis=False,
    hovertemplate="<b>%{y}</b><br>Votos HELP: %{x}<extra></extra>",
)
figure.update_layout(
    height=max(340, 54 * len(top7) + 70),
    margin={"l": 8, "r": 36, "t": 12, "b": 12},
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    showlegend=False,
    font={"family": "Arial, sans-serif", "color": "#334155"},
    xaxis={"showgrid": True, "gridcolor": "#e9eef3", "zeroline": False},
    yaxis={
        "title": None,
        "categoryorder": "array",
        "categoryarray": list(reversed(chart_data["Pessoa"].tolist())),
        "automargin": True,
    },
)
st.plotly_chart(figure, use_container_width=True, config={"displayModeBar": False})

st.divider()
st.subheader("📣 Sua posição no ranking")
st.caption(
    "Veja seus votos e quantos faltam para ultrapassar a pessoa logo acima. "
    "A liderança mostra a vantagem sobre o segundo lugar."
)

table_data = pd.DataFrame(
    [
        {
            "Posição": row["Posição"],
            "Pessoa": row["Pessoa"],
            "Final do celular": row["Celular final 4"] or "—",
            "Votos HELP": row["Votos HELP"],
            "Próximo passo": row["Próximo passo"],
        }
        for row in ranking
    ]
)
st.dataframe(
    table_data,
    hide_index=True,
    use_container_width=True,
    column_config={
        "Posição": st.column_config.NumberColumn("Pos.", format="%d"),
        "Pessoa": st.column_config.TextColumn("Pessoa"),
        "Final do celular": st.column_config.TextColumn("Final 4"),
        "Votos HELP": st.column_config.NumberColumn("Votos HELP", format="%d"),
        "Próximo passo": st.column_config.TextColumn(
            "Próximo passo",
            help="Votos necessários para ultrapassar a pessoa logo acima.",
        ),
    },
)
