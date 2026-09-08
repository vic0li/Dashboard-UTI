import pandas as pd
import numpy as np


# ============================================================
# PREPARAÇÃO GERAL DOS DADOS
# ============================================================

def preparar_dados(df):

    # Criar uma cópia para não alterar o dataframe original
    df = df.copy()


    # ========================================================
    # TIMESTAMP
    # ========================================================

    if "timestamp" in df.columns:

        df["timestamp"] = pd.to_datetime(
            df["timestamp"],
            errors="coerce"
        )


    # ========================================================
    # ORDENAR DADOS
    # ========================================================

    colunas_ordenacao = []

    if "id_paciente" in df.columns:
        colunas_ordenacao.append("id_paciente")

    if "timestamp" in df.columns:
        colunas_ordenacao.append("timestamp")


    if colunas_ordenacao:

        df = df.sort_values(
            by=colunas_ordenacao
        ).reset_index(drop=True)


    # ========================================================
    # CONVERTER VARIÁVEIS NUMÉRICAS
    # ========================================================

    colunas_numericas = [

        # CLÍNICAS
        "idade",
        "frequencia_cardiaca",
        "pressao_sistolica",
        "pressao_diastolica",
        "pressao_media",
        "saturacao_O2",
        "temperatura",

        # LABORATORIAIS
        "lactato",
        "leucocitos",
        "creatinina",

        # LPP
        "angulacao_dorso",
        "mudancas_posicao_24h",
        "tempo_posicao_atual_min",
        "pressao_media_colchao",
        "indice_movimento",
        "risco_imobilidade",
        "risco_pressao"
    ]


    for coluna in colunas_numericas:

        if coluna in df.columns:

            df[coluna] = pd.to_numeric(
                df[coluna],
                errors="coerce"
            )


    # ========================================================
    # CALCULAR PRESSÃO MÉDIA
    # ========================================================

    if (
        "pressao_media" not in df.columns
        and
        "pressao_sistolica" in df.columns
        and
        "pressao_diastolica" in df.columns
    ):

        df["pressao_media"] = (
            df["pressao_sistolica"]
            +
            (2 * df["pressao_diastolica"])
        ) / 3


    return df


# ============================================================
# MÉDIA MÓVEL
# ============================================================

def calcular_medias_moveis(df):

    df = df.copy()


    variaveis = [

        "frequencia_cardiaca",
        "saturacao_O2",
        "temperatura",
        "lactato"
    ]


    for variavel in variaveis:

        if (
            variavel in df.columns
            and
            "id_paciente" in df.columns
        ):

            nome_coluna = f"{variavel}_media_3"

            df[nome_coluna] = (
                df
                .groupby("id_paciente")[variavel]
                .transform(
                    lambda x: x.rolling(
                        window=3,
                        min_periods=1
                    ).mean()
                )
            )


    return df


# ============================================================
# CÁLCULO DE TENDÊNCIAS
# ============================================================

def calcular_tendencias(df):

    df = df.copy()


    variaveis = [

        "frequencia_cardiaca",
        "saturacao_O2",
        "temperatura",
        "lactato"
    ]


    for variavel in variaveis:

        if (
            variavel in df.columns
            and
            "id_paciente" in df.columns
        ):

            diferenca = (
                df
                .groupby("id_paciente")[variavel]
                .diff()
            )


            nome_tendencia = f"{variavel}_tendencia"


            df[nome_tendencia] = np.select(

                [
                    diferenca > 0,
                    diferenca < 0
                ],

                [
                    "subindo",
                    "descendo"
                ],

                default="estavel"
            )


    return df


# ============================================================
# PIPELINE COMPLETO
# ============================================================

def processar_dados(df):

    df = preparar_dados(df)

    df = calcular_medias_moveis(df)

    df = calcular_tendencias(df)

    return df