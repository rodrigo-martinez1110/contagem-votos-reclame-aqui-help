from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path

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


def load_ranking(path: Path) -> tuple[list[dict[str, str]], str]:
    with path.open("r", encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source, delimiter=";")
        if not reader.fieldnames or not EXPECTED_COLUMNS.issubset(reader.fieldnames):
            raise ValueError("O CSV não tem as colunas esperadas para o ranking.")
        rows = [row for row in reader if row.get("Pessoa", "").strip()]

    rows.sort(key=lambda row: (int(row["Posição"]), row["Pessoa"].casefold()))
    updated_values = [row.get("Atualizado em", "").strip() for row in rows]
    updated_at = max(updated_values, default="")
    return rows, updated_at


st.set_page_config(
    page_title="Ranking HELP | Prêmio Reclame Aqui",
    page_icon="🏆",
    layout="wide",
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

try:
    parsed_update = datetime.fromisoformat(updated_at)
    display_update = parsed_update.strftime("%d/%m/%Y às %H:%M")
except ValueError:
    display_update = updated_at or "não informada"

total_help = sum(int(row["Votos HELP"]) for row in ranking)
first_place = ranking[0]

left, middle, right = st.columns(3)
left.metric("Votos para HELP", f"{total_help:,}".replace(",", "."))
middle.metric("Pessoas no ranking", len(ranking))
right.metric("Líder atual", first_place["Pessoa"])
st.caption(f"Última atualização: {display_update}")

display_columns = [
    "Posição",
    "Pessoa",
    "Celular final 4",
    "Votos HELP",
    "BMG (não conta)",
    "Sem comprovante",
    "Revisar",
]
st.table([{column: row[column] for column in display_columns} for row in ranking])
