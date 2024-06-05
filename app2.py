import streamlit as st
import pandas as pd
import plotly.express as px
from io import StringIO

st.set_page_config(page_title="Painel de Consultas Processuais", layout="wide") # configuração da página
st.title("Consulta Processos") # título da página

# Inicializar o estado da sessão para armazenar o número do processo e o arquivo
if 'process_number' not in st.session_state:
    st.session_state.process_number = None
if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None

# Crear un botão para inserir um número de processo
number = st.number_input("Digite um número de processo", value=st.session_state.process_number or 0, placeholder="Nº Processo...")
if number:
    st.session_state.process_number = number
st.write("Faremos a consulta utilizando o número do processo: ", st.session_state.process_number)

# Cargar archivo
uploaded_file = st.file_uploader("Carregue um arquivo Excel", type=["xlsx", "xls"])
if uploaded_file is not None:
    st.session_state.uploaded_file = uploaded_file

if st.session_state.uploaded_file is not None:
    # Para ler o arquivo como bytes:
    bytes_data = st.session_state.uploaded_file.getvalue()
    st.write(bytes_data)

    # Para converter para um objeto de IO baseado em string:
    stringio = StringIO(st.session_state.uploaded_file.getvalue().decode("utf-8"))
    st.write(stringio)

    # Para ler o arquivo como string:
    string_data = stringio.read()
    st.write(string_data)

    # Pode ser usado onde um objeto "file-like" é aceito:
    df = pd.read_excel(st.session_state.uploaded_file)
    st.write(df)