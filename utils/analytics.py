import pandas as pd
import numpy as np


def preparar_dados(df):
    """Prepara a base clínica simulada para o motor analítico."""
    df = df.copy()

    if "timestamp" in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df["timestamp"]):
            df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        else:
            serie = df["timestamp"].astype(str).str.strip()
            convertido = pd.to_datetime(
                serie, format="%d/%m/%Y %H:%M", errors="coerce"
            )
            mascara = convertido.isna()
            if mascara.any():
                convertido.loc[mascara] = pd.to_datetime(
                    serie.loc[mascara],
                    format="%d/%m/%Y %H:%M:%S",
                    errors="coerce",
                )
            mascara = convertido.isna()
            if mascara.any():
                convertido.loc[mascara] = pd.to_datetime(
                    serie.loc[mascara], dayfirst=True, errors="coerce"
                )
            df["timestamp"] = convertido

    ordem = [c for c in ["id_paciente", "timestamp"] if c in df.columns]
    if ordem:
        df = df.sort_values(ordem).reset_index(drop=True)

    numericas = [
        "idade", "dia_internacao", "tempo_internacao_horas",
        "frequencia_cardiaca", "pressao_sistolica", "pressao_diastolica",
        "pressao_media", "saturacao_O2", "temperatura", "lactato",
        "leucocitos", "creatinina", "angulacao_dorso",
        "mudancas_posicao_24h", "tempo_posicao_atual_min",
        "pressao_media_colchao", "indice_movimento",
        "risco_imobilidade", "risco_pressao",
        "pacientes_por_enfermeiro", "taxa_ocupacao_pct",
        "braden_percepcao_sensorial", "braden_umidade",
        "braden_atividade", "braden_mobilidade",
        "braden_nutricao", "braden_friccao_cisalhamento",
    ]
    for coluna in numericas:
        if coluna in df.columns:
            df[coluna] = pd.to_numeric(df[coluna], errors="coerce")

    if (
        "pressao_media" not in df.columns
        and "pressao_sistolica" in df.columns
        and "pressao_diastolica" in df.columns
    ):
        df["pressao_media"] = (
            df["pressao_sistolica"] + 2 * df["pressao_diastolica"]
        ) / 3

    return df


def calcular_medias_moveis(df):
    """Média móvel dos três registros mais recentes: FC, PAS e SpO2."""
    df = df.copy()
    variaveis = ["frequencia_cardiaca", "pressao_sistolica", "saturacao_O2"]

    for variavel in variaveis:
        if variavel in df.columns and "id_paciente" in df.columns:
            df[f"{variavel}_media_3"] = (
                df.groupby("id_paciente")[variavel]
                .transform(lambda x: x.rolling(window=3, min_periods=1).mean())
            )
    return df


def calcular_tendencias(df):
    """Classifica a direção entre registros consecutivos."""
    df = df.copy()
    variaveis = ["frequencia_cardiaca", "pressao_sistolica", "saturacao_O2"]

    for variavel in variaveis:
        if variavel in df.columns and "id_paciente" in df.columns:
            diferenca = df.groupby("id_paciente")[variavel].diff()
            df[f"{variavel}_variacao"] = diferenca
            df[f"{variavel}_tendencia"] = np.select(
                [diferenca > 0, diferenca < 0],
                ["subindo", "descendo"],
                default="estavel",
            )
    return df


def processar_dados(df):
    df = preparar_dados(df)
    df = calcular_medias_moveis(df)
    df = calcular_tendencias(df)
    return df
