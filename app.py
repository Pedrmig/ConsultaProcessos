import streamlit as st
import pandas as pd
import requests
import json
from io import StringIO, BytesIO
import cons_api

st.set_page_config(page_title="Painel de Consultas Processuais", layout="wide")  # configuração da página
st.title("Consulta Processos")  # título da página



# Inicializar o estado da sessão para armazenar o número do processo e o arquivo
if 'process_number' not in st.session_state:
    st.session_state.process_number = None
if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None

# Criar um campo para inserir um número de processo
number = st.number_input("Digite um número de processo", value=st.session_state.process_number or 0, placeholder="Nº Processo...")
if number:
    st.session_state.process_number = number
st.write("Faremos a consulta utilizando o número do processo: ", st.session_state.process_number)

# Carregar arquivo
uploaded_file = st.file_uploader("Carregue um arquivo Excel", type=["xlsx", "xls"])
if uploaded_file is not None:
    st.session_state.uploaded_file = uploaded_file

# Função para processar um número de processo
def processa_numero_processo(numero_processo):
    tribunal, data = consulta_tribunal(numero_processo)
    if data:
        return pd.json_normalize(data['hits']['hits'])
    else:
        st.write(f"Processo {numero_processo} não encontrado.")
        return pd.DataFrame()

# Processar arquivo ou número de processo
result_df = pd.DataFrame()
if st.session_state.uploaded_file is not None:
    df = pd.read_excel(st.session_state.uploaded_file)
    numeros_processos = df['NumeroProcesso'].tolist()  # Ajuste conforme o nome da coluna
    dataframes = [processa_numero_processo(num) for num in numeros_processos]
    result_df = pd.concat(dataframes, ignore_index=True)
elif st.session_state.process_number:
    result_df = processa_numero_processo(st.session_state.process_number)

if not result_df.empty:
    st.write(result_df)

    # Botão para download
    @st.cache_data
    def convert_df(df):
        # IMPORTANT: Cache the conversion to prevent computation on every rerun
        return df.to_csv(index=False).encode('utf-8')

    csv = convert_df(result_df)

    st.download_button(
        label="Download CSV",
        data=csv,
        file_name='consulta_processos.csv',
        mime='text/csv',
    )

    
