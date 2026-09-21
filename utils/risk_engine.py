import pandas as pd
import numpy as np


# ============================================================
# ESCALA DE BRADEN
# ============================================================

def calcular_braden(df):
    df = df.copy()
    colunas = [
        "braden_percepcao_sensorial",
        "braden_umidade",
        "braden_atividade",
        "braden_mobilidade",
        "braden_nutricao",
        "braden_friccao_cisalhamento",
    ]

    if not all(c in df.columns for c in colunas):
        df["braden_total"] = pd.NA
        return df

    for c in colunas:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    for c in colunas[:-1]:
        df[c] = df[c].clip(1, 4)
    df["braden_friccao_cisalhamento"] = df["braden_friccao_cisalhamento"].clip(1, 3)

    df["braden_total"] = df[colunas].sum(axis=1, min_count=len(colunas))
    return df


def classificar_braden(df):
    df = df.copy()

    def classificar(v):
        if pd.isna(v):
            return "Não disponível"
        if v <= 9:
            return "Severo"
        if v <= 12:
            return "Alto"
        if v <= 14:
            return "Moderado"
        if v <= 18:
            return "Leve"
        return "Mínimo"

    df["braden_classificacao"] = df["braden_total"].apply(classificar)
    return df


# ============================================================
# MODELO INTEGRADO DE RISCO DE LPP — TCC, SEÇÃO 5.4
# ============================================================

def _componente_braden(s):
    return np.select([s >= 19, s.between(13, 18), s <= 12], [0.0, 0.5, 1.0], default=np.nan)


def _componente_internacao(s):
    return np.select([s < 3, s.between(3, 6), s >= 7], [0.0, 0.5, 1.0], default=np.nan)


def _componente_vasoativo(s):
    texto = s.astype(str).str.strip().str.lower()
    sim = texto.isin(["sim", "1", "true", "yes"])
    nao = texto.isin(["não", "nao", "0", "false", "no"])
    return np.select([nao, sim], [0.0, 1.0], default=np.nan)


def _componente_mobilidade(s):
    return np.select([s == 4, s.isin([2, 3]), s == 1], [0.0, 0.5, 1.0], default=np.nan)


def _componente_posicao(s):
    return np.select([s < 60, s.between(60, 120), s > 120], [0.0, 0.5, 1.0], default=np.nan)


def _componente_reposicionamento(s):
    return np.select([s >= 12, s.between(6, 11), s < 6], [0.0, 0.5, 1.0], default=np.nan)


def _componente_equipe(s):
    return np.select([s <= 2, (s > 2) & (s < 4), s >= 4], [0.0, 0.5, 1.0], default=np.nan)


def _componente_ocupacao(s):
    return np.select([s < 80, s.between(80, 90), s > 90], [0.0, 0.5, 1.0], default=np.nan)


def calcular_score_lpp(df):
    df = df.copy()

    requisitos = {
        "comp_lpp_braden": ("braden_total", _componente_braden),
        "comp_lpp_internacao": ("dia_internacao", _componente_internacao),
        "comp_lpp_vasoativo": ("uso_drogas_vasoativas", _componente_vasoativo),
        "comp_lpp_mobilidade": ("braden_mobilidade", _componente_mobilidade),
        "comp_lpp_posicao": ("tempo_posicao_atual_min", _componente_posicao),
        "comp_lpp_reposicionamento": ("mudancas_posicao_24h", _componente_reposicionamento),
        "comp_lpp_equipe": ("pacientes_por_enfermeiro", _componente_equipe),
        "comp_lpp_ocupacao": ("taxa_ocupacao_pct", _componente_ocupacao),
    }

    componentes = []
    for destino, (origem, funcao) in requisitos.items():
        if origem not in df.columns:
            df[destino] = np.nan
        else:
            serie = df[origem]
            if origem != "uso_drogas_vasoativas":
                serie = pd.to_numeric(serie, errors="coerce")
            df[destino] = funcao(serie)
        componentes.append(destino)

    # O score só é calculado quando os oito componentes estão disponíveis.
    completos = df[componentes].notna().all(axis=1)
    df["score_lpp"] = np.nan
    df.loc[completos, "score_lpp"] = (
        10 * df.loc[completos, componentes].mean(axis=1)
    ).round(2)

    return df


def classificar_risco_lpp(df):
    df = df.copy()

    def classificar(score):
        if pd.isna(score):
            return "Não disponível"
        if score < 4:
            return "Baixo"
        if score < 7:
            return "Médio"
        return "Alto"

    df["classificacao_lpp_score"] = df["score_lpp"].apply(classificar)
    df["classificacao_lpp"] = df["classificacao_lpp_score"]

    # Regra automática definida no modelo:
    # Braden <= 12 + posição > 120 min + uso de vasoativo => Alto.
    vaso = (
        df.get("uso_drogas_vasoativas", pd.Series("", index=df.index))
        .astype(str).str.strip().str.lower().isin(["sim", "1", "true", "yes"])
    )
    override = (
        (pd.to_numeric(df.get("braden_total"), errors="coerce") <= 12)
        & (pd.to_numeric(df.get("tempo_posicao_atual_min"), errors="coerce") > 120)
        & vaso
    )
    df["regra_alto_risco_lpp"] = override
    df.loc[override, "classificacao_lpp"] = "Alto"
    return df


# ============================================================
# ALERTAS — TCC, SEÇÃO 5.3
# ============================================================

def calcular_alertas(df):
    df = df.copy()

    fc = pd.to_numeric(df.get("frequencia_cardiaca"), errors="coerce")
    pas = pd.to_numeric(df.get("pressao_sistolica"), errors="coerce")
    spo2 = pd.to_numeric(df.get("saturacao_O2"), errors="coerce")

    df["alerta_fc_motor"] = (fc <= 40) | (fc >= 131)
    df["alerta_pas_motor"] = (pas <= 90) | (pas >= 220)
    df["alerta_spo2_motor"] = spo2 <= 91
    df["alerta_lpp_motor"] = df["classificacao_lpp"].eq("Alto")

    colunas = [
        "alerta_fc_motor",
        "alerta_pas_motor",
        "alerta_spo2_motor",
        "alerta_lpp_motor",
    ]
    df["quantidade_alertas_motor"] = df[colunas].sum(axis=1).astype(int)

    # Alias oficial para as páginas novas. Mantém o nome simples sem
    # reaproveitar os alertas antigos já existentes no CSV.
    df["quantidade_alertas"] = df["quantidade_alertas_motor"]

    def motivos(row):
        itens = []
        if row["alerta_fc_motor"]:
            itens.append("FC")
        if row["alerta_pas_motor"]:
            itens.append("PAS")
        if row["alerta_spo2_motor"]:
            itens.append("SpO₂")
        if row["alerta_lpp_motor"]:
            itens.append("LPP")
        return ", ".join(itens) if itens else "Sem alerta"

    df["motivos_alerta"] = df.apply(motivos, axis=1)
    return df


def processar_riscos(df):
    """Pipeline único do motor analítico descrito até a Seção 5.5."""
    df = calcular_braden(df)
    df = classificar_braden(df)
    df = calcular_score_lpp(df)
    df = classificar_risco_lpp(df)
    df = calcular_alertas(df)
    return df
