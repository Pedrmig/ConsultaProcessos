import streamlit as st
import pandas as pd
import requests
import json
from io import StringIO, BytesIO
import cons_api
import tkinter as tk
from tkinter import filedialog

st.set_page_config(page_title="Painel de Consultas Processuais", layout="wide")  # configuração da página
st.title("Consulta Processos")  # título da página



# Inicializar o estado da sessão para armazenar o número do processo e o arquivo
if 'process_number' not in st.session_state:
    st.session_state.process_number = None
if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None

# Criar um campo para inserir um número de processo
number = st.text_input("Digite um número de processo", placeholder="Nº Processo...")
if number:
    if number.isdigit() and len(number) == 20:  # Verifica se a entrada é um número
        st.session_state.process_number = int(number)  # Converte a entrada em um inteiro
        st.write("Faremos a consulta utilizando o número do processo: ", st.session_state.process_number)
    else:
        st.write("Por favor, insira um número válido.")

# Função para processar um número de processo
def processa_numero_processo(numero_processo):
    data = cons_api.consulta_tribunal(numero_processo)
    if data:
        df = cons_api.json_to_dataframe(data)
        root = tk.Tk()
        root.withdraw()  # Oculta a janela Tkinter
        pasta_salvar = filedialog.asksaveasfilename(defaultextension='.xlsx')  # Abre a janela 'Salvar como'
        if pasta_salvar:  # Se um caminho de arquivo foi selecionado
            df.to_excel(pasta_salvar, index=False)
    else:
        st.write(f"Processo {numero_processo} não encontrado.")
        return pd.DataFrame()

# Carregar arquivo
uploaded_file = st.file_uploader("Carregue um arquivo Excel", type=["xlsx", "xls"])
if uploaded_file is not None:
    st.session_state.uploaded_file = uploaded_file



    
