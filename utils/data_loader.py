import os
import pandas as pd
import streamlit as st

DATA_PATH = os.path.join("data", "uti_simulada.csv")

@st.cache_data
def load_data(file_path: str = DATA_PATH) -> pd.DataFrame:
    """
    Carrega e valida o dataset da UTI Simulada ignorando linhas mal formatadas
    e testando diferentes separadores (;, ,) e encodings.
    """
    if not os.path.exists(file_path):
        st.error(f"⚠️ Arquivo não encontrado no caminho: `{file_path}`. Verifique se o CSV foi enviado para a pasta 'data/'.")
        return pd.DataFrame()
    
    separators = [";", ",", "\t"]
    encodings = ["utf-8", "latin1", "iso-8859-1", "cp1252"]

    for sep in separators:
        for enc in encodings:
            try:
                # on_bad_lines='skip' ignora linhas corrompidas com número incorreto de colunas
                df = pd.read_csv(file_path, sep=sep, encoding=enc, on_bad_lines="skip")
                
                # Se carregou mais de 1 coluna, identificamos o separador correto
                if len(df.columns) > 1:
                    # Tenta converter colunas de data
                    date_columns = [col for col in df.columns if 'data' in str(col).lower() or 'date' in str(col).lower()]
                    for col in date_columns:
                        df[col] = pd.to_datetime(df[col], errors='coerce')
                    return df
            except Exception:
                continue

    # Tentativa de fallback com engine Python flexível
    try:
        df = pd.read_csv(file_path, sep=None, engine="python", on_bad_lines="skip")
        return df
    except Exception as e:
        st.error(f"❌ Erro ao ler o arquivo CSV: {e}")
        return pd.DataFrame()