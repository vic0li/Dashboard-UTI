# ============================================================
# DATA LOADER
# UTI INTELLIGENT CARE
#
# Responsável pelo carregamento da base de dados simulada.
# ============================================================


import streamlit as st
import pandas as pd


# ============================================================
# CARREGAMENTO DA BASE
# ============================================================

@st.cache_data
def load_data():

    # ========================================================
    # CAMINHO DA BASE
    # ========================================================

    caminho = "data/uti_simulada.csv"


    # ========================================================
    # LEITURA DO CSV
    # ========================================================

    # O timestamp é carregado inicialmente como texto.
    #
    # Isso evita que o pandas interprete automaticamente
    # datas no formato americano MM/DD/YYYY.
    #
    # A conversão para datetime será realizada de forma
    # explícita posteriormente.

    df = pd.read_csv(

        caminho,

        sep=";",

        dtype={

            "timestamp": "string"

        }

    )


    # ========================================================
    # LIMPEZA DOS NOMES DAS COLUNAS
    # ========================================================

    df.columns = (

        df.columns

        .astype(str)

        .str.strip()

    )


    # ========================================================
    # RETORNO
    # ========================================================

    return df
