import pandas as pd
import numpy as np

# ============================================================
# SCORE CLÍNICO CONCEITUAL
# ============================================================

def calcular_score_clinico(df):

    df = df.copy()


    def score_fc(valor):

        if pd.isna(valor):
            return 0

        if 60 <= valor <= 100:
            return 0

        elif 50 <= valor < 60 or 100 < valor <= 120:
            return 10

        else:
            return 20


    def score_spo2(valor):

        if pd.isna(valor):
            return 0

        if valor >= 95:
            return 0

        elif valor >= 90:
            return 10

        else:
            return 25


    def score_temperatura(valor):

        if pd.isna(valor):
            return 0

        if 36 <= valor <= 37.5:
            return 0

        elif 35 <= valor < 36 or 37.5 < valor <= 38.5:
            return 10

        else:
            return 20


    def score_lactato(valor):

        if pd.isna(valor):
            return 0

        if valor < 2:
            return 0

        elif valor < 4:
            return 15

        else:
            return 25


    # ========================================================
    # APLICAR SCORE
    # ========================================================

    if "frequencia_cardiaca" in df.columns:

        df["score_fc"] = (
            df["frequencia_cardiaca"]
            .apply(score_fc)
        )

    else:

        df["score_fc"] = 0


    if "saturacao_O2" in df.columns:

        df["score_spo2"] = (
            df["saturacao_O2"]
            .apply(score_spo2)
        )

    else:

        df["score_spo2"] = 0


    if "temperatura" in df.columns:

        df["score_temperatura"] = (
            df["temperatura"]
            .apply(score_temperatura)
        )

    else:

        df["score_temperatura"] = 0


    if "lactato" in df.columns:

        df["score_lactato"] = (
            df["lactato"]
            .apply(score_lactato)
        )

    else:

        df["score_lactato"] = 0


    # ========================================================
    # SCORE TOTAL
    # ========================================================

    df["score_clinico"] = (

        df["score_fc"]

        +

        df["score_spo2"]

        +

        df["score_temperatura"]

        +

        df["score_lactato"]
    )


    return df

# ============================================================
# CLASSIFICAÇÃO CLÍNICA
# ============================================================

def classificar_risco_clinico(df):

    df = df.copy()


    def classificar(score):

        if score < 20:
            return "Baixo"

        elif score < 40:
            return "Moderado"

        elif score < 60:
            return "Alto"

        else:
            return "Crítico"


    df["classificacao_clinica"] = (
        df["score_clinico"]
        .apply(classificar)
    )


    return df


# ============================================================
# ESCALA DE BRADEN
# AVALIAÇÃO CONVENCIONAL COMPLEMENTAR AO SCORE DINÂMICO DE LPP
# ============================================================

def calcular_braden(df):
    """Calcula a pontuação total da Escala de Braden."""

    df = df.copy()

    colunas_braden = [
        "braden_percepcao_sensorial",
        "braden_umidade",
        "braden_atividade",
        "braden_mobilidade",
        "braden_nutricao",
        "braden_friccao_cisalhamento",
    ]

    if not all(coluna in df.columns for coluna in colunas_braden):
        df["braden_total"] = pd.NA
        return df

    for coluna in colunas_braden:
        df[coluna] = pd.to_numeric(
            df[coluna],
            errors="coerce",
        )

    for coluna in [
        "braden_percepcao_sensorial",
        "braden_umidade",
        "braden_atividade",
        "braden_mobilidade",
        "braden_nutricao",
    ]:
        df[coluna] = df[coluna].clip(1, 4)

    df["braden_friccao_cisalhamento"] = (
        df["braden_friccao_cisalhamento"]
        .clip(1, 3)
    )

    df["braden_total"] = (
        df[colunas_braden]
        .sum(axis=1, min_count=len(colunas_braden))
    )

    return df


def classificar_braden(df):
    """Classifica a pontuação total da Braden segundo a estratificação adotada no TCC."""

    df = df.copy()

    def classificar(valor):

        if pd.isna(valor):
            return "Não disponível"

        if valor <= 9:
            return "Severo"

        elif valor <= 12:
            return "Alto"

        elif valor <= 14:
            return "Moderado"

        elif valor <= 18:
            return "Leve"

        else:
            return "Mínimo"

    df["braden_classificacao"] = (
        df["braden_total"]
        .apply(classificar)
    )

    return df

# ============================================================
# SCORE DE RISCO LPP
# MODELO CONCEITUAL PARA DADOS SIMULADOS
# ============================================================

# ============================================================

def calcular_score_lpp(df):

    df = df.copy()


    score_total = pd.Series(
        0,
        index=df.index,
        dtype=float
    )


    # ========================================================
    # TEMPO NA POSIÇÃO
    # ========================================================

    if "tempo_posicao_atual_min" in df.columns:

        tempo = df["tempo_posicao_atual_min"]

        score_tempo = np.select(

            [
                tempo < 60,
                (tempo >= 60) & (tempo < 120),
                (tempo >= 120) & (tempo < 180),
                tempo >= 180
            ],

            [
                0,
                10,
                20,
                30
            ],

            default=0
        )

        df["score_lpp_tempo"] = score_tempo
        score_total += score_tempo


    # ========================================================
    # PRESSÃO DO COLCHÃO
    # ========================================================

    if "pressao_media_colchao" in df.columns:

        pressao = df["pressao_media_colchao"]

        score_pressao = np.select(

            [
                pressao < 30,
                (pressao >= 30) & (pressao < 50),
                pressao >= 50
            ],

            [
                0,
                15,
                25
            ],

            default=0
        )

        df["score_lpp_pressao"] = score_pressao
        score_total += score_pressao


    # ========================================================
    # MUDANÇAS DE POSIÇÃO
    # ========================================================

    if "mudancas_posicao_24h" in df.columns:

        mudancas = df["mudancas_posicao_24h"]

        score_mudancas = np.select(

            [
                mudancas >= 8,
                (mudancas >= 4) & (mudancas < 8),
                mudancas < 4
            ],

            [
                0,
                10,
                20
            ],

            default=0
        )

        df["score_lpp_mudancas"] = score_mudancas
        score_total += score_mudancas


    # ========================================================
    # ÍNDICE DE MOVIMENTO
    # ========================================================

    if "indice_movimento" in df.columns:

        movimento = pd.to_numeric(
            df["indice_movimento"],
            errors="coerce",
        ).fillna(0) * 100

        score_movimento = np.select(

            [
                movimento >= 70,
                (movimento >= 40) & (movimento < 70),
                movimento < 40
            ],

            [
                0,
                10,
                20
            ],

            default=0
        )

        df["score_lpp_movimento"] = score_movimento
        score_total += score_movimento


    # ========================================================
    # RISCO DE IMOBILIDADE
    # ========================================================

    if "risco_imobilidade" in df.columns:

        risco = df["risco_imobilidade"]

        # Funciona se o risco já estiver entre 0 e 10
        # ou em escala percentual

        risco = pd.to_numeric(
            risco,
            errors="coerce"
        )

        risco = risco.fillna(0)


        if risco.max() <= 10:

            score_imobilidade = risco * 2

        else:

            score_imobilidade = risco * 0.2


        df["score_lpp_imobilidade"] = score_imobilidade.round(1)
        score_total += score_imobilidade


    # ========================================================
    # GARANTIR COMPONENTES DO MOTOR
    # ========================================================

    for coluna_componente in [
        "score_lpp_tempo",
        "score_lpp_pressao",
        "score_lpp_mudancas",
        "score_lpp_movimento",
        "score_lpp_imobilidade",
    ]:
        if coluna_componente not in df.columns:
            df[coluna_componente] = 0.0

    # ========================================================
    # LIMITAR ENTRE 0 E 100
    # ========================================================

    df["score_lpp"] = (
        score_total
        .clip(0, 100)
        .round(1)
    )


    return df

# ============================================================
# CLASSIFICAÇÃO DO RISCO LPP
# ============================================================

def classificar_risco_lpp(df):

    df = df.copy()


    def classificar(score):

        if score < 30:
            return "Baixo"

        elif score < 60:
            return "Moderado"

        elif score < 80:
            return "Alto"

        else:
            return "Crítico"


    df["classificacao_lpp"] = (
        df["score_lpp"]
        .apply(classificar)
    )


    return df

# ============================================================
# CONTADOR DE ALERTAS
# ============================================================

def calcular_alertas(df):

    df = df.copy()

    alertas = pd.Series(
        0,
        index=df.index
    )


    # SpO2 crítica

    if "saturacao_O2" in df.columns:

        alertas += (
            df["saturacao_O2"] < 90
        ).astype(int)


    # Frequência cardíaca crítica

    if "frequencia_cardiaca" in df.columns:

        alertas += (

            (
                df["frequencia_cardiaca"] < 50
            )

            |

            (
                df["frequencia_cardiaca"] > 120
            )

        ).astype(int)


    # Temperatura crítica

    if "temperatura" in df.columns:

        alertas += (

            (
                df["temperatura"] < 35
            )

            |

            (
                df["temperatura"] > 38.5
            )

        ).astype(int)


    # Lactato elevado

    if "lactato" in df.columns:

        alertas += (
            df["lactato"] >= 4
        ).astype(int)


    # LPP crítico

    if "score_lpp" in df.columns:

        alertas += (
            df["score_lpp"] >= 80
        ).astype(int)


    df["quantidade_alertas"] = alertas


    return df

# ============================================================
# ÍNDICE DE PRIORIDADE
# ============================================================

def calcular_indice_prioridade(df):

    df = df.copy()


    # ========================================================
    # NORMALIZAR ALERTAS
    # ========================================================

    if "quantidade_alertas" in df.columns:

        max_alertas = 5

        score_alertas = (

            df["quantidade_alertas"]

            / max_alertas

            * 100

        ).clip(0, 100)

    else:

        score_alertas = 0


    # ========================================================
    # ÍNDICE FINAL
    # ========================================================

    df["indice_prioridade"] = (

        df["score_clinico"] * 0.40

        +

        df["score_lpp"] * 0.40

        +

        score_alertas * 0.20

    ).round(1)


    return df

# ============================================================
# CLASSIFICAÇÃO DA PRIORIDADE
# ============================================================

def classificar_prioridade(df):

    df = df.copy()


    def classificar(valor):

        if valor < 30:
            return "Baixa"

        elif valor < 60:
            return "Moderada"

        elif valor < 80:
            return "Alta"

        else:
            return "Crítica"


    df["classificacao_prioridade"] = (
        df["indice_prioridade"]
        .apply(classificar)
    )


    return df

# ============================================================
# PIPELINE COMPLETO DO MOTOR DE RISCO
# ============================================================

def processar_riscos(df):

    df = calcular_score_clinico(df)

    df = classificar_risco_clinico(df)

    df = calcular_braden(df)

    df = classificar_braden(df)

    df = calcular_score_lpp(df)

    df = classificar_risco_lpp(df)

    df = calcular_alertas(df)

    df = calcular_indice_prioridade(df)

    df = classificar_prioridade(df)

    return df
