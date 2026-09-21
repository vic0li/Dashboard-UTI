from pathlib import Path
import streamlit as st
import pandas as pd


@st.cache_data
def load_data():
    """Carrega a base clínica e incorpora os indicadores operacionais necessários ao modelo LPP."""
    raiz = Path(__file__).resolve().parents[1]
    clinico_path = raiz / "data" / "uti_simulada.csv"
    operacional_path = raiz / "data" / "UTI_operacional.csv"

    df = pd.read_csv(clinico_path, sep=";", dtype={"timestamp": "string"})
    df.columns = df.columns.astype(str).str.strip()

    if not operacional_path.exists():
        return df

    op = pd.read_csv(operacional_path, sep=";")
    op.columns = op.columns.astype(str).str.strip()

    clin_ts = pd.to_datetime(
        df["timestamp"].astype(str).str.strip(),
        format="%d/%m/%Y %H:%M",
        errors="coerce",
    )
    op_ts = pd.to_datetime(op["timestamp"], errors="coerce")

    clin = df.copy()
    clin["_timestamp_merge"] = clin_ts
    op = op.copy()
    op["_timestamp_merge"] = op_ts

    colunas_op = [
        "_timestamp_merge",
        "taxa_ocupacao_pct",
        "pacientes_por_enfermeiro",
    ]
    op = op[[c for c in colunas_op if c in op.columns]].dropna(subset=["_timestamp_merge"])
    op = op.sort_values("_timestamp_merge")
    clin = clin.sort_values("_timestamp_merge")

    # Cada registro clínico recebe a condição operacional vigente mais recente.
    combinado = pd.merge_asof(
        clin,
        op,
        on="_timestamp_merge",
        direction="backward",
    )

    # Para registros anteriores ao primeiro turno operacional, usa o primeiro
    # valor disponível, evitando criar uma regra clínica a partir de dado ausente.
    for c in ["taxa_ocupacao_pct", "pacientes_por_enfermeiro"]:
        if c in combinado.columns:
            combinado[c] = combinado[c].bfill().ffill()

    combinado = combinado.drop(columns=["_timestamp_merge"])
    return combinado.reset_index(drop=True)
